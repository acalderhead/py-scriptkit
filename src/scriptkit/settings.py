"""
scriptkit.settings — dataclass-driven configuration with CLI + env wiring.

Subclass ``ScriptSettings`` in a script and add only that script's fields. Each
settable field automatically becomes a CLI flag and reads a matching
environment variable (see ENV_PREFIX). Resolution precedence is

    CLI argument  >  environment variable  >  dataclass default

Supported field types are wired automatically: scalars (str, int, float, Path,
and anything else constructible from a string, e.g. Decimal / UUID), ``bool``
(as a ``--flag`` / ``--no-flag`` pair), ``datetime`` / ``date`` (ISO 8601 via
``fromisoformat``), ``Enum`` and ``Literal[...]`` (constrained choices),
``list[X]`` (repeatable on the CLI, comma-separated in the env), and
``Optional[...]`` wrapping any of the above. Derived (init=False) fields and
types that can't map to a single CLI argument (dict, tuple, non-Optional
unions) are skipped by the auto-parser and left to bespoke handling.
"""

from __future__ import annotations

import argparse
import enum
import logging
import os
from collections.abc import Callable
from dataclasses import MISSING, dataclass, field, fields
from datetime import date, datetime
from pathlib import Path
from types import UnionType
from typing import Any, Literal, NamedTuple, Union, get_args, get_origin, get_type_hints

_log = logging.getLogger(__name__)

# Prefix for environment-variable overrides, e.g. field `temp_val` -> APP_TEMP_VAL
ENV_PREFIX = "APP_"


def _bool_from_str(value: str) -> bool:
    """Parse a boolean from a string using common truthy spellings."""
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _scalar_caster(arg_type: type) -> Callable[[str], Any]:
    """
    Return a ``str -> value`` callable for a plain scalar field type.

    Most types (int, float, Path, Decimal, UUID, ...) construct straight from a
    string, so the type itself is the caster. ``bool`` and the date/time types
    are the exceptions: bool needs truthy parsing, and date/datetime need
    ``fromisoformat`` because their constructors take numeric components, not a
    string.
    """
    if arg_type is bool:
        return _bool_from_str
    if arg_type is datetime:
        return datetime.fromisoformat
    if arg_type is date:
        return date.fromisoformat
    return arg_type


def _enum_caster(enum_cls: type[enum.Enum]) -> tuple[Callable[[str], enum.Enum], str]:
    """
    Build a name->member parser for an Enum field, plus a display metavar.

    Members are matched by *name* (e.g. ``--color RED``), not value, on both the
    CLI and the env path. Returns ``(parse, metavar)``; ``parse`` raises
    ArgumentTypeError (whose message argparse prints verbatim) on an unknown
    name so the user sees the valid options.
    """
    names = [member.name for member in enum_cls]

    def parse(raw: str) -> enum.Enum:
        try:
            return enum_cls[raw]
        except KeyError:
            raise argparse.ArgumentTypeError(
                f"invalid choice: {raw!r} (choose from {', '.join(names)})"
            ) from None

    parse.__name__ = enum_cls.__name__
    return parse, "{" + ",".join(names) + "}"


class _ArgSpec(NamedTuple):
    """
    How one dataclass field maps onto argparse.

    kind    : "bool" | "scalar" | "list" | "unsupported". Drives which
              add_argument shape is used (and whether the field is skipped).
    caster  : str -> value callable. For "list" it casts a single element;
              unused (a harmless placeholder) when kind is "unsupported".
    choices : Allowed values, or None. Set for Literal fields.
    metavar : Help/usage placeholder, or None. Set for Enum fields.
    """

    kind: str
    caster: Callable[[str], Any]
    choices: list[Any] | None
    metavar: str | None


def _optional_inner(arg_type: Any) -> Any | None:
    """
    If ``arg_type`` is ``Optional[X]`` — a Union / ``X | None`` with exactly one
    non-None member — return ``X``; otherwise return None.

    Broader unions (``int | str``, with or without None) can't reduce to a
    single argparse type, so they return None and are treated as unsupported.
    """
    if get_origin(arg_type) in (Union, UnionType):
        members = get_args(arg_type)
        non_none = [a for a in members if a is not type(None)]
        if len(non_none) == 1 and len(non_none) != len(members):
            return non_none[0]
    return None


def _value_spec(arg_type: Any) -> tuple[Callable[[str], Any], list[Any] | None, str | None]:
    """
    Resolve one scalar / Enum / Literal value into ``(caster, choices, metavar)``.

    Enum yields a name-lookup caster plus a metavar; Literal yields choices and a
    caster typed from the first literal; plain scalars yield just a caster.
    """
    if get_origin(arg_type) is Literal:
        choices = list(get_args(arg_type))
        element_type = type(choices[0]) if choices else str
        return _scalar_caster(element_type), choices, None
    if isinstance(arg_type, type) and issubclass(arg_type, enum.Enum):
        caster, metavar = _enum_caster(arg_type)
        return caster, None, metavar
    return _scalar_caster(arg_type), None, None


def _resolve_argspec(arg_type: Any) -> _ArgSpec:
    """
    Map a field's declared type to an _ArgSpec describing how to add it to the
    parser and how to cast its env-var string.

    ``Optional[...]`` is unwrapped first, then re-dispatched, so wrappers like
    ``Optional[list[X]]`` and ``Optional[Enum]`` compose for free. Types that
    can't map to a single CLI argument return kind "unsupported".
    """
    inner = _optional_inner(arg_type)
    if inner is not None:
        arg_type = inner

    origin = get_origin(arg_type)

    if origin is list:
        args = get_args(arg_type)
        element = args[0] if args else str
        # Nested generics (list[list[...]], list[Optional[...]]) aren't supported.
        if get_origin(element) is not None and get_origin(element) is not Literal:
            return _ArgSpec("unsupported", str, None, None)
        caster, _, _ = _value_spec(element)
        return _ArgSpec("list", caster, None, None)

    if arg_type is bool:
        return _ArgSpec("bool", _bool_from_str, None, None)

    # Any remaining generic (dict, tuple, set, non-Optional Union) can't map to a
    # single argparse type. Literal is the exception; _value_spec handles it.
    if origin is not None and origin is not Literal:
        return _ArgSpec("unsupported", str, None, None)

    caster, choices, metavar = _value_spec(arg_type)
    return _ArgSpec("scalar", caster, choices, metavar)


def _cast_env(value: str, spec: _ArgSpec) -> Any:
    """
    Cast a raw environment-variable string per the field's resolved _ArgSpec.

    Booleans use truthy spellings; lists split on commas (each item trimmed and
    cast with the element caster); everything else goes through the single-value
    caster. Kept in lockstep with the CLI so an env value and a ``--flag`` value
    resolve identically.
    """
    if spec.kind == "bool":
        return _bool_from_str(value)
    if spec.kind == "list":
        return [spec.caster(item.strip()) for item in value.split(",") if item.strip()]
    return spec.caster(value)


@dataclass(frozen=True)
class ScriptSettings:
    """
    Base configuration for scripts built on scriptkit.

    Subclass this and add your own fields (each needs a default so it can act as
    a CLI default). ``dir_base`` is the single settable root; ``dir_data`` and
    ``dir_output`` cascade from it in ``__post_init__``, so overriding the root
    relocates everything.

    ``dir_base`` defaults to the current working directory. For script-relative
    paths instead, override it in your subclass::

        dir_base: Path = field(default_factory=lambda: Path(__file__).resolve().parent)

    or set ``--dir-base`` / ``APP_DIR_BASE`` at runtime.
    """

    # Paths ────────────────────────────
    dir_base: Path = field(default_factory=Path.cwd)

    dir_data: Path = field(init=False, default=Path())
    dir_output: Path = field(init=False, default=Path())

    # Logging ──────────────────────────
    log_level: str = "INFO"

    def __post_init__(self):
        """Derive dependent paths and ensure required infrastructure exists."""
        # object.__setattr__ is required because the dataclass is frozen.
        object.__setattr__(self, "dir_data", self.dir_base / "data")
        object.__setattr__(self, "dir_output", self.dir_base / "output")
        self.dir_output.mkdir(parents=True, exist_ok=True)


class _ScriptHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    """
    Combined help formatter used for every script's --help.

    RawDescriptionHelpFormatter keeps the module docstring's line breaks and
    section layout intact (argparse's default reflows it into one paragraph);
    ArgumentDefaultsHelpFormatter still appends "(default: ...)" to each option.
    """


def build_parser_from_settings(
    cls: type,
    description: str | None = None,
    version: str | None = None,
) -> argparse.ArgumentParser:
    """
    Construct an ArgumentParser dynamically from a ScriptSettings subclass.

    cls         : Dataclass type whose fields define the CLI arguments.
    description : Optional help text shown at the top of --help output.
    version     : Optional version string; when given, adds a --version flag.
                  (Pass the *script's* __version__, not scriptkit's.)

    Returns a configured ArgumentParser. Resolution precedence is
    CLI > env var > dataclass default. Derived (init=False) fields and fields
    whose type can't map to a single CLI argument are skipped and left to
    bespoke handling (see the module docstring for the supported types).
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=_ScriptHelpFormatter,
    )
    if version is not None:
        parser.add_argument(
            "--version", action="version", version=f"%(prog)s {version}"
        )

    type_hints = get_type_hints(cls)

    for f in fields(cls):
        # Derived fields (dir_data, etc.) are computed, not user-supplied.
        if not f.init:
            continue

        arg_name = f"--{f.name.replace('_', '-')}"
        spec = _resolve_argspec(type_hints[f.name])

        # Types that don't map to a single CLI argument are left to bespoke code.
        if spec.kind == "unsupported":
            _log.debug("Skipping CLI arg for unsupported-typed field: %s", f.name)
            continue

        env_name = f"{ENV_PREFIX}{f.name.upper()}"
        env_value = os.environ.get(env_name)

        # Precedence: an env value supplies the default (CLI still overrides it);
        # otherwise fall back to the dataclass default, resolving default_factory
        # fields (e.g. dir_base) which report MISSING for `f.default`.
        if env_value is not None:
            default = _cast_env(env_value, spec)
            is_required = False
        elif f.default is not MISSING:
            default = f.default
            is_required = False
        elif f.default_factory is not MISSING:  # type: ignore[misc]
            default = f.default_factory()
            is_required = False
        else:
            default = None
            is_required = True

        if spec.kind == "bool":
            # BooleanOptionalAction gives a clean --flag / --no-flag pair and
            # makes a required boolean expressible (unlike a bare store_true).
            parser.add_argument(
                arg_name,
                action=argparse.BooleanOptionalAction,
                default=None if is_required else default,
                required=is_required,
                help=f"(env: {env_name})",
            )
        elif spec.kind == "list":
            # nargs="*" collects space-separated CLI tokens; the env form is
            # comma-separated (see _cast_env). Each element is cast individually.
            parser.add_argument(
                arg_name,
                nargs="*",
                type=spec.caster,
                default=None if is_required else default,
                required=is_required,
                help=f"(env: {env_name}, comma-separated)",
            )
        else:
            kwargs: dict[str, Any] = {
                "type": spec.caster,
                "default": None if is_required else default,
                "required": is_required,
                "help": f"(env: {env_name})",
            }
            # choices (Literal) and metavar (Enum) are only set when relevant.
            if spec.choices is not None:
                kwargs["choices"] = spec.choices
            if spec.metavar is not None:
                kwargs["metavar"] = spec.metavar
            parser.add_argument(arg_name, **kwargs)

    return parser


def parse_settings(
    cls: type,
    description: str | None = None,
    version: str | None = None,
):
    """
    Parse command-line arguments and return a populated settings instance.

    cls         : The ScriptSettings subclass to build and populate.
    description : Optional --help description (commonly the script's __doc__).
    version     : Optional script version string for the --version flag.

    Returns an instance of ``cls`` populated from CLI arguments, environment
    variables, or field defaults (in that order of precedence).
    """
    parser = build_parser_from_settings(cls, description=description, version=version)
    args = parser.parse_args()
    return cls(**vars(args))
