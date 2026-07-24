"""
scriptkit.settings — dataclass-driven configuration with CLI + env wiring.

Subclass ``ScriptSettings`` in a script and add only that script's fields. Each
settable field automatically becomes a CLI flag and reads a matching
environment variable (see ENV_PREFIX). Resolution precedence is

    CLI argument  >  environment variable  >  dataclass default

Derived (init=False) fields and complex/generic-typed fields (list[str],
Optional[...]) are skipped by the auto-parser and left to bespoke handling.
"""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import MISSING, dataclass, field, fields
from pathlib import Path
from typing import Any, get_origin, get_type_hints

_log = logging.getLogger(__name__)

# Prefix for environment-variable overrides, e.g. field `temp_val` -> APP_TEMP_VAL
ENV_PREFIX = "APP_"


def _cast_env(value: str, arg_type: type) -> Any:
    """
    Cast a raw environment-variable string into the field's declared type.

    value    : Raw string pulled from os.environ.
    arg_type : Target type (bool, int, Path, str, ...).

    Returns the value coerced to arg_type. Booleans accept common truthy
    spellings ("1", "true", "yes", "on"); everything else is passed to the
    type's constructor.
    """
    if arg_type is bool:
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return arg_type(value)


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
    CLI > env var > dataclass default. Derived (init=False) and complex/generic
    fields are skipped and left to bespoke handling.
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
        arg_type = type_hints[f.name]

        # Bypass complex types (list[str], Optional[...]) that need custom logic.
        if get_origin(arg_type) is not None:
            _log.debug("Skipping CLI arg for generic-typed field: %s", f.name)
            continue

        env_name = f"{ENV_PREFIX}{f.name.upper()}"
        env_value = os.environ.get(env_name)

        # Precedence: an env value supplies the default (CLI still overrides it);
        # otherwise fall back to the dataclass default, resolving default_factory
        # fields (e.g. dir_base) which report MISSING for `f.default`.
        if env_value is not None:
            default = _cast_env(env_value, arg_type)
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

        if arg_type is bool:
            # BooleanOptionalAction gives a clean --flag / --no-flag pair and
            # makes a required boolean expressible (unlike a bare store_true).
            parser.add_argument(
                arg_name,
                action=argparse.BooleanOptionalAction,
                default=None if is_required else default,
                required=is_required,
                help=f"(env: {env_name})",
            )
        else:
            parser.add_argument(
                arg_name,
                type=arg_type,
                default=None if is_required else default,
                required=is_required,
                help=f"(env: {env_name})",
            )

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
