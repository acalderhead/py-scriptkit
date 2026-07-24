"""
scriptkit.cli — the ``scriptkit`` console entry point.

Currently provides ``scriptkit new``, a cross-platform replacement for the
per-repo ``new-script.ps1`` scaffolder: it writes a fresh copy of the bundled
script template into a target directory and pins its scriptkit dependency to a
release tag. The template ships inside the package (``scriptkit/templates``),
so this works from a dev ``.venv`` or straight from a git checkout via ``uvx``::

    uvx --from "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v0.4.0" \
        scriptkit new my_tool
"""

from __future__ import annotations

import argparse
import re
import sys
from importlib.resources import files
from pathlib import Path

from . import __version__

# Matches the scriptkit git pin in the bundled template so `new` can repoint it
# to the requested tag (mirrors the substitution the old new-script.ps1 did).
_PIN_RE = re.compile(r"py-scriptkit\.git@v\d+\.\d+\.\d+")


def _slugify(name: str) -> str:
    """
    Normalize an arbitrary name into a snake_case module stem.

    e.g. "Reconcile Invoices" / "reconcile-invoices.py" -> "reconcile_invoices".
    Raises ValueError if nothing usable remains.
    """
    stem = re.sub(r"[^A-Za-z0-9]+", "_", name.removesuffix(".py")).strip("_").lower()
    if not stem:
        raise ValueError(f"Could not derive a filename from {name!r}.")
    return stem


def _read_template() -> str:
    """Return the bundled script template's text (UTF-8)."""
    resource = files("scriptkit") / "templates" / "script_template.py"
    return resource.read_text(encoding="utf-8")


def _cmd_new(args: argparse.Namespace) -> int:
    """Scaffold a new pinned script; return a process exit code."""
    stem = _slugify(args.name)
    dest_dir = Path(args.dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{stem}.py"
    if dest.exists() and not args.force:
        print(
            f"Refusing to overwrite {dest} (pass --force to replace it).",
            file=sys.stderr,
        )
        return 1

    content = _PIN_RE.sub(f"py-scriptkit.git@{args.tag}", _read_template())
    # newline="\n": keep scripts LF on every OS so the shebang / PEP 723 header
    # parse cleanly under uv, regardless of the host platform's default.
    dest.write_text(content, encoding="utf-8", newline="\n")

    print(f"Created {dest} (pinned scriptkit@{args.tag})")
    print(f"Next:  uv run {dest} --help")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the ``scriptkit`` argument parser."""
    parser = argparse.ArgumentParser(
        prog="scriptkit",
        description="scriptkit developer commands.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new", help="scaffold a new scriptkit-based script")
    new.add_argument(
        "name", help="name for the new script (normalized to snake_case)"
    )
    new.add_argument(
        "--tag",
        default=f"v{__version__}",
        help="scriptkit release tag to pin the new script to "
        "(default: this scriptkit's own version)",
    )
    new.add_argument(
        "--dir",
        default="scripts",
        help="directory to create the script in (default: scripts)",
    )
    new.add_argument(
        "--force", action="store_true", help="overwrite an existing file"
    )
    new.set_defaults(func=_cmd_new)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``scriptkit`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
