"""
scriptkit — a stdlib-first toolkit for single-file Python scripts.

Provides the common infrastructure that used to be inlined at the top of every
script:

    - ScriptSettings          : frozen-dataclass config base with a path cascade
    - build_parser_from_settings / parse_settings
                              : auto-generate a CLI + env wiring from a dataclass
                                (precedence: CLI > env var > default)
    - get_logger / set_log_level
                              : RichLogger when available, a semantic-aware
                                stdlib fallback when it is not
    - timestamp               : compact UTC timestamps at a chosen granularity

Scripts pin a specific version of this package in their PEP 723 header, so a
script written today keeps running against the scriptkit it was born with even
after the library moves on.
"""

from .logging import get_logger, set_log_level
from .settings import (
    ENV_PREFIX,
    ScriptSettings,
    build_parser_from_settings,
    parse_settings,
)
from .times import timestamp

__version__ = "0.2.1"

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
