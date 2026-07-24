"""Tests for scriptkit.times.timestamp."""

import re

import pytest

from scriptkit import timestamp


def test_default_is_minute_granularity():
    assert re.fullmatch(r"\d{12}", timestamp())


def test_each_granularity_length():
    expected = {
        "year": 4,
        "month": 6,
        "day": 8,
        "hour": 10,
        "minute": 12,
        "second": 14,
    }
    for granularity, length in expected.items():
        assert len(timestamp(granularity)) == length


def test_unknown_granularity_raises_valueerror():
    with pytest.raises(ValueError):
        timestamp("fortnight")
