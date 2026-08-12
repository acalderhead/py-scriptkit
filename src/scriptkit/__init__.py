"""
Purpose
───────
    A stdlib-first toolkit for single-file Python scripts. Provides the common
    infrastructure that used to be inlined at the top of every script.

Public API
──────────
    ScriptSettings             : frozen-dataclass config base with a path cascade
    build_parser_from_settings : build an ArgumentParser from a settings class
    parse_settings             : parse args into a populated settings instance
                                 (precedence: CLI > env var > default)
    get_logger / set_log_level : RichLogger when available, stdlib shim otherwise
    timestamp                  : compact UTC timestamps at a chosen granularity
    ENV_PREFIX                 : env-var prefix used by the settings wiring

Notes
─────
    Scripts pin a specific version of this package in their PEP 723 header, so a
    script written today keeps running against the scriptkit it was born with
    even after the library moves on.
"""

from .logging import get_logger, set_log_level
from .settings import (
    ENV_PREFIX,
    ScriptSettings,
    build_parser_from_settings,
    parse_settings,
)
from .times import timestamp

__version__ = "0.5.4"

__all__ = [
    "ENV_PREFIX",
    "ScriptSettings",
    "build_parser_from_settings",
    "parse_settings",
    "get_logger",
    "set_log_level",
    "timestamp",
    "__version__",
]
