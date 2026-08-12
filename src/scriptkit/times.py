"""
Purpose
───────
    Small time helpers. ``timestamp`` returns a compact UTC stamp at a chosen
    granularity, handy for naming output files and run directories.

Public API
──────────
    timestamp : Compact UTC timestamp string at a chosen granularity

Usage
─────
    from scriptkit.times import timestamp
"""

from __future__ import annotations

from datetime import UTC, datetime

__all__ = ["timestamp"]


# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

# Granularity presets for timestamp()
_TIMESTAMP_FORMATS = {
    "year":   "%Y",
    "month":  "%Y%m",
    "day":    "%Y%m%d",
    "hour":   "%Y%m%d%H",
    "minute": "%Y%m%d%H%M",
    "second": "%Y%m%d%H%M%S",
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def timestamp(granularity: str = "minute") -> str:
    """
    Generate a compact UTC timestamp string at the requested granularity.

    granularity : One of year, month, day, hour, minute (default), second.
                  Default "minute" yields YYYYMMDDHHMM.

    Returns the current UTC time formatted to the chosen granularity. Raises
    ValueError on an unknown granularity.
    """
    try:
        fmt = _TIMESTAMP_FORMATS[granularity]
    except KeyError:
        valid = ", ".join(_TIMESTAMP_FORMATS)
        raise ValueError(
            f"Unknown granularity {granularity!r}; choose from: {valid}"
        ) from None
    return datetime.now(UTC).strftime(fmt)
