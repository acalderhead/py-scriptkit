"""
Purpose
───────
    The ``scriptkit`` console entry point. Currently provides ``scriptkit new``,
    a cross-platform scaffolder that writes a fresh copy of the bundled module
    template into a target directory.

Public API
──────────
    build_parser : Construct the ``scriptkit`` argument parser
    main         : Entry point for the ``scriptkit`` console script

Usage
─────
    uvx --from "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v1.0.0" \
        scriptkit new my_module

Notes
─────
    The module template ships inside the package (``scriptkit/templates``), so
    this works from a dev ``.venv`` or straight from a git checkout via ``uvx``.
"""

from __future__ import annotations

import argparse
import re
import sys
from importlib.resources import files
from pathlib import Path

from . import __version__

__all__ = [
    "build_parser",
    "main",
]


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Construct the ``scriptkit`` argument parser."""
    parser = argparse.ArgumentParser(
        prog = "scriptkit",
        description = "scriptkit developer commands.",
    )
    parser.add_argument(
        "--version", action = "version", version = f"%(prog)s {__version__}"
    )
    sub = parser.add_subparsers(dest = "command", required = True)

    new = sub.add_parser("new", help = "scaffold a new module from the template")
    new.add_argument(
        "name", help = "name for the new module (normalized to snake_case)"
    )
    new.add_argument(
        "--dir",
        default = ".",
        help    = "directory to create the module in (default: current dir)",
    )
    new.add_argument(
        "--force", action = "store_true", help = "overwrite an existing file"
    )
    new.set_defaults(func = _cmd_new)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``scriptkit`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}", file = sys.stderr)
        return 2


# ──────────────────────────────────────────────────────────────────────────────
# Internal Helpers
# ──────────────────────────────────────────────────────────────────────────────

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
    """Return the bundled module template's text (UTF-8)."""
    resource = files("scriptkit") / "templates" / "module_template.py"
    return resource.read_text(encoding = "utf-8")


def _cmd_new(args: argparse.Namespace) -> int:
    """Scaffold a new module from the bundled template; return a process exit code."""
    stem = _slugify(args.name)

    dest_dir = Path(args.dir)
    dest_dir.mkdir(parents = True, exist_ok = True)

    dest = dest_dir / f"{stem}.py"

    if dest.exists() and not args.force:
        print(
            f"Refusing to overwrite {dest} (pass --force to replace it).",
            file = sys.stderr,
        )
        return 1

    # newline="\n": keep modules LF on every OS, regardless of the host default.
    dest.write_text(_read_template(), encoding = "utf-8", newline = "\n")

    print(f"Created {dest}")
    print(f"Next:  edit {dest} and fill in the module.")
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    raise SystemExit(main())
