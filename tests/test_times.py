"""
Purpose
───────
    Tests for scriptkit.times.timestamp: default granularity, per-granularity
    lengths, and the unknown-granularity error.
"""

from __future__ import annotations

import re

import pytest

from scriptkit import timestamp

# ──────────────────────────────────────────────────────────────────────────────
# Granularity
# ──────────────────────────────────────────────────────────────────────────────

def test_default_is_minute_granularity():
    assert re.fullmatch(r"\d{12}", timestamp())


def test_each_granularity_length():
    expected = {
        "year":    4,
        "month":   6,
        "day":     8,
        "hour":   10,
        "minute": 12,
        "second": 14,
    }
    for granularity, length in expected.items():
        assert len(timestamp(granularity)) == length


# ──────────────────────────────────────────────────────────────────────────────
# Errors
# ──────────────────────────────────────────────────────────────────────────────

def test_unknown_granularity_raises_valueerror():
    with pytest.raises(ValueError):
        timestamp("fortnight")
