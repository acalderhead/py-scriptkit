"""Tests for scriptkit.settings: precedence, path cascade, and bool flags."""

from dataclasses import dataclass

import pytest

from scriptkit import ScriptSettings, build_parser_from_settings


@dataclass(frozen=True)
class Demo(ScriptSettings):
    temp_val: int = 42
    temp_bool: bool = False


def test_path_cascade_and_defaults(tmp_path):
    s = Demo(dir_base=tmp_path)
    assert s.temp_val == 42
    assert s.temp_bool is False
    assert s.dir_data == tmp_path / "data"
    assert s.dir_output == tmp_path / "output"
    # __post_init__ creates the output dir.
    assert s.dir_output.exists()


def test_default_is_dataclass_default(monkeypatch):
    monkeypatch.delenv("APP_TEMP_VAL", raising=False)
    parser = build_parser_from_settings(Demo)
    args = parser.parse_args([])
    assert args.temp_val == 42


def test_env_supplies_default(monkeypatch):
    monkeypatch.setenv("APP_TEMP_VAL", "99")
    parser = build_parser_from_settings(Demo)
    args = parser.parse_args([])
    assert args.temp_val == 99


def test_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("APP_TEMP_VAL", "99")
    parser = build_parser_from_settings(Demo)
    args = parser.parse_args(["--temp-val", "7"])
    assert args.temp_val == 7


def test_bool_optional_action(monkeypatch):
    monkeypatch.delenv("APP_TEMP_BOOL", raising=False)
    parser = build_parser_from_settings(Demo)
    assert parser.parse_args(["--temp-bool"]).temp_bool is True
    assert parser.parse_args(["--no-temp-bool"]).temp_bool is False


def test_env_bool_truthy(monkeypatch):
    monkeypatch.setenv("APP_TEMP_BOOL", "yes")
    parser = build_parser_from_settings(Demo)
    assert parser.parse_args([]).temp_bool is True


def test_dir_base_default_factory_resolves(monkeypatch, tmp_path):
    # dir_base uses default_factory; the parser must resolve it, not mark it
    # required. With no env/CLI override it should fall back to cwd.
    monkeypatch.delenv("APP_DIR_BASE", raising=False)
    monkeypatch.chdir(tmp_path)
    parser = build_parser_from_settings(Demo)
    args = parser.parse_args([])
    assert args.dir_base == tmp_path


def test_version_flag_exits(capsys):
    parser = build_parser_from_settings(Demo, version="1.2.3")
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])
    assert "1.2.3" in capsys.readouterr().out
