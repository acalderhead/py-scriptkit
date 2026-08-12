"""
Purpose
───────
    RichLogger when available, a semantic-aware stdlib fallback when it is not.
    ``get_logger`` returns a RichLogger (decorated console output) if the
    optional ``rich_logger`` package is installed, otherwise a plain stdlib
    logger that still answers RichLogger's custom vocabulary
    (stage/step/metric/alert/...).

Context
───────
    Each custom method maps to a standard level and prepends a [TAG], so the
    semantic distinction survives even in a plain, aggregator-parseable log used
    by CI runners or Azure Monitor / Log Analytics.

Public API
──────────
    get_logger    : Logger for a name or __file__ path (Rich, else stdlib shim)
    set_log_level : Apply a textual log level to an existing logger

Usage
─────
    from scriptkit.logging import get_logger, set_log_level

Notes
─────
    Semantic vocabulary answered by the stdlib fallback:

    | Purpose                        | Methods                            |
    | ------------------------------ | ---------------------------------- |
    | I/O and metadata management    | `read`, `write`, `metadata`        |
    | Execution flow and structure   | `stage`, `step`, `substep`, `info` |
    | Experiment config and results  | `config`, `metric`, `result`       |
    | Warnings and alerts            | `warning`, `alert`                 |
    | Errors and failures            | `error`                            |
    | Developer checks and traceback | `check`, `debug`                   |

    Install the rich variant with:

        pip install "scriptkit[rich] @ git+https://github.com/acalderhead/py-scriptkit.git@v0.2.4"
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

__all__ = [
    "get_logger",
    "set_log_level",
]


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

# method  :     (       level,    tag       )
_SEMANTIC_METHODS = {
    "stage":    (logging.INFO,    "STAGE"   ),
    "step":     (logging.INFO,    "STEP"    ),
    "substep":  (logging.INFO,    "SUBSTEP" ),
    "config":   (logging.INFO,    "CONFIG"  ),
    "metric":   (logging.INFO,    "METRIC"  ),
    "result":   (logging.INFO,    "RESULT"  ),
    "read":     (logging.INFO,    "READ"    ),
    "write":    (logging.INFO,    "WRITE"   ),
    "metadata": (logging.INFO,    "METADATA"),
    "alert":    (logging.WARNING, "ALERT"   ),
    "check":    (logging.DEBUG,   "CHECK"   ),
}

# Fixed width for the logger-name column. Names are padded up to this width and
# hard-truncated beyond it, so the message column stays aligned regardless of
# name length (a plain "%(name)-20s" would pad but never truncate).
_NAME_WIDTH = 20


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_logger(name_or_path: Any = None):
    """
    Return a logger for the given name or ``__file__`` path.

    name_or_path : A logger name, or a path/``__file__`` whose stem is used.

    Prefers ``rich_logger.RichLogger`` for decorated console output; falls back
    to a stdlib logger that still exposes the semantic vocabulary via a [TAG]
    prefix (see module docstring) when rich_logger is unavailable.
    """
    name = _name_from(name_or_path)
    try:
        # rich_logger is optional (github/acalderhead/rich-logger); only present
        # when the [rich] extra is installed, hence the missing-import ignore.
        from rich_logger import RichLogger  # pyright: ignore[reportMissingImports]
        return RichLogger(name)
    except ImportError:
        _configure_stdlib()
        return logging.getLogger(name)


def set_log_level(logger, level_name: str) -> None:
    """
    Apply a textual log level (e.g. "DEBUG") to an existing logger.

    logger     : The logger returned by ``get_logger``.
    level_name : Level name; unknown values fall back to INFO.
    """
    level = getattr(logging, str(level_name).upper(), logging.INFO)
    try:
        logger.setLevel(level)
    except Exception:
        # Custom loggers may not expose setLevel; ignore rather than fail startup.
        pass


# ──────────────────────────────────────────────────────────────────────────────
# Internal Helpers
# ──────────────────────────────────────────────────────────────────────────────

class _StdlibShimLogger(logging.Logger):
    """
    stdlib Logger that also answers RichLogger's custom method names.

    Standard methods behave normally. Each extra semantic method logs at its
    mapped level with a [TAG] prefix and accepts any positional/keyword
    arguments, so call sites written for RichLogger never break under the
    fallback (an unknown payload is stringified, never format-interpolated).
    """

    def _emit_semantic(self, level: int, tag: str, *args: Any, **kwargs: Any) -> None:
        if not self.isEnabledFor(level):
            return

        parts = [str(a) for a in args]
        parts += [f"{k} = {v}" for k, v in kwargs.items()]

        # The %-args are controlled here (tag, text); the caller's payload only
        # ever lands in `parts`, so it can never trigger a %-format error.
        self.log(level, "[%s] %s", tag, " ".join(parts))


def _install_semantic_methods(cls: type) -> None:
    """Attach the semantic vocabulary to cls, skipping names it already owns."""
    for name, (level, tag) in _SEMANTIC_METHODS.items():
        if hasattr(cls, name):
            continue

        def _make(_level: int, _tag: str):
            def _method(self, *args: Any, **kwargs: Any) -> None:
                self._emit_semantic(_level, _tag, *args, **kwargs)

            return _method

        setattr(cls, name, _make(level, tag))


_install_semantic_methods(_StdlibShimLogger)


class _AlignedFormatter(logging.Formatter):
    """Formatter that truncates/pads the logger name to a fixed column width."""

    def format(self, record: logging.LogRecord) -> str:
        record.name_fixed = f"{record.name[:_NAME_WIDTH]:<{_NAME_WIDTH}}"
        return super().format(record)


_configured = False


def _configure_stdlib() -> None:
    """Install the aligned stdlib handler + shim logger class once."""
    global _configured
    if _configured:
        return

    # Non-TTY sinks (CI, Azure Monitor / Log Analytics) get a plain, ANSI-free,
    # aggregator-parseable format. Fields are separated by " | " and level/name
    # are fixed-width, so the message column stays aligned across records.
    handler = logging.StreamHandler()
    handler.setFormatter(
        _AlignedFormatter(
            fmt = "%(asctime)s | %(levelname)-8s | %(name_fixed)s | %(message)s",
            datefmt = "%Y-%m-%dT%H:%M:%S%z",
        )
    )

    logging.basicConfig(level = logging.INFO, handlers = [handler])
    logging.setLoggerClass(_StdlibShimLogger)

    _configured = True


def _name_from(name_or_path: Any) -> str:
    """
    Derive a logger name; a path-like value is reduced to its file stem.

    Normalize Windows separators to '/' first so the stem is derived correctly
    on any OS: a script's __file__ uses native separators, but a value carrying
    '\\' must not be treated as one long filename on POSIX (where '\\' is a
    legal filename character, not a separator).
    """
    if name_or_path is None:
        return "script"
    text = str(name_or_path).replace("\\", "/")
    if text.endswith(".py") or "/" in text:
        return Path(text).stem
    return text
