"""Tests for scriptkit.logging: the stdlib fallback shim behaves under no rich."""

import sys

from scriptkit import get_logger, set_log_level


def _force_stdlib(monkeypatch):
    # Setting the module to None makes `import rich_logger` raise ImportError,
    # forcing get_logger down the stdlib fallback path deterministically.
    monkeypatch.setitem(sys.modules, "rich_logger", None)


def test_fallback_exposes_semantic_methods(monkeypatch):
    _force_stdlib(monkeypatch)
    log = get_logger("test-shim-methods")
    for name in ("stage", "step", "substep", "config", "metric",
                 "result", "read", "write", "metadata", "alert", "check"):
        assert hasattr(log, name), f"missing semantic method: {name}"


def test_semantic_methods_do_not_raise(monkeypatch):
    _force_stdlib(monkeypatch)
    log = get_logger("test-shim-callable")
    # Positional + keyword payloads must both be accepted, never format-crash.
    log.stage("beginning", run=1)
    log.metric("throughput", 42, unit="rps")
    log.alert("watch out")
    log.check("debug detail")


def test_get_logger_derives_name_from_path(monkeypatch):
    _force_stdlib(monkeypatch)
    log = get_logger(r"C:\some\dir\my_script.py")
    assert log.name == "my_script"


def test_set_log_level(monkeypatch):
    import logging

    _force_stdlib(monkeypatch)
    log = get_logger("test-shim-level")
    set_log_level(log, "DEBUG")
    assert log.level == logging.DEBUG
    # Unknown level falls back to INFO rather than raising.
    set_log_level(log, "NONSENSE")
    assert log.level == logging.INFO
