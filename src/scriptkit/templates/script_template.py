#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   # Pin the scriptkit version this script was written against. Bump the tag
#   # only when you WANT its improvements; old scripts keep running unchanged.
#   # For decorated console logging, use: "scriptkit[rich] @ git+..."
#   "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v0.5.1",
# ]
# ///

"""
Purpose
───────
    One-two sentences describing what the script is designed to do.

Context
───────
    Optional background on why this script exists or the scenario/problem it
    addresses.

Inputs / Parameters
───────────────────
    Fields on Settings become CLI flags automatically. Each also reads an
    environment variable (APP_<FIELD>). Precedence: CLI > env var > default.

    temp_val  : Description of the first parameter.
    temp_bool : Description of the second parameter.

Outputs
───────
    Processed data, results, or console/log output.

Usage
─────
    uv run script_name.py [options]
    uv run script_name.py --help       # lists every flag + its env var

Notes
─────
    Anything future-you (or a teammate) should be aware of.
"""

import sys
import traceback
from dataclasses import dataclass

from scriptkit import ScriptSettings, get_logger, parse_settings, set_log_level, timestamp

__author__ = "Aidan Calderhead"
__version__ = "1.0.0"

# TODO:  Example Text
# NOTE:  Example Text
# FIXME: Example Text

logger = get_logger(__file__)


# ──────────────────────────────────────────────────────────────────────────────
# Settings
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen = True)
class Settings(ScriptSettings):
    # Inherits dir_base / dir_data / dir_output cascade and log_level.
    # Add only THIS script's fields below (each needs a default).
    temp_val: int = 42
    temp_bool: bool = False


# ──────────────────────────────────────────────────────────────────────────────
# Grouped Functions
# ──────────────────────────────────────────────────────────────────────────────

def placeholder_func(data, flag: bool = True):
    """
    Perform a placeholder processing step on input data.

    data : Input object to be processed.
    flag : Example optional parameter controlling behavior.

    Returns processed output. Replace with actual logic.
    """
    return data


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def main(settings: Settings) -> int:
    """
    Primary execution logic for the script.

    settings : Validated Settings instance containing configuration and paths.

    Returns an integer exit code (0 for success, non-zero for failure).
    """
    logger.stage(f"Run {timestamp()} - base={settings.dir_base}")

    data = placeholder_func(settings.dir_data)
    result = placeholder_func(data)
    placeholder_func(result, settings.dir_output)

    logger.info("Processing complete")
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Config errors (bad args, un-writable output dir) surface loudly before the
    # handler below; they are startup faults, not pipeline failures.
    settings = parse_settings(Settings, description = __doc__, version = __version__)
    set_log_level(logger, settings.log_level)

    try:
        sys.exit(main(settings))
    except Exception:
        # Records the full stack on failure. Uses .error(str) for
        # logger-agnostic behavior (works under RichLogger and the shim alike).
        logger.error(f"Pipeline failed:\n{traceback.format_exc()}")
        sys.exit(1)
