"""
Purpose
───────
    Tests for <module under test>: <the behaviors these tests cover>.

Notes
─────
    Test functions are named so the name states the behavior; a docstring is
    optional. Group related tests under a section header, and keep shared setup
    in the Fixtures & Helpers section. Run a subset with, e.g.,
    ``pytest tests/test_module.py -k enum``.
"""

from __future__ import annotations

import pytest

from scriptkit.module_name import thing_under_test


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures & Helpers
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def example_fixture():
    """Reusable setup shared by several tests. Replace or delete."""
    return thing_under_test


def _make_example(value = 0):
    """Private helper (leading underscore) shared by tests; not collected."""
    return value


# ──────────────────────────────────────────────────────────────────────────────
# <Behavior group — e.g. happy path / a feature name>
# ──────────────────────────────────────────────────────────────────────────────

def test_does_the_expected_thing(example_fixture):
    """State the behavior under test (optional; the name should already say it)."""
    assert example_fixture is thing_under_test


# ──────────────────────────────────────────────────────────────────────────────
# <Another group — e.g. edge cases / errors>
# ──────────────────────────────────────────────────────────────────────────────

def test_raises_on_bad_input():
    with pytest.raises(ValueError):
        _make_example("replace with the failing call")
