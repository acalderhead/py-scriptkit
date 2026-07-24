"""
scriptkit.times — small time helpers.

``timestamp`` returns a compact UTC stamp at a chosen granularity, handy for
naming output files and run directories.
"""

from __future__ import annotations

from datetime import datetime, timezone

# Granularity presets for timestamp(); each trims the compact UTC stamp to a
# coarser unit. Ordered coarse -> fine for readability.
_TIMESTAMP_FORMATS = {
    "year": "%Y",
    "month": "%Y%m",
    "day": "%Y%m%d",
    "hour": "%Y%m%d%H",
    "minute": "%Y%m%d%H%M",
    "second": "%Y%m%d%H%M%S",
}


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
    return datetime.now(timezone.utc).strftime(fmt)
