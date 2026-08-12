"""
Purpose
───────
    Tests for scriptkit.settings: precedence, path cascade, and the typed CLI
    arguments (scalars, Enum, Literal, list, datetime/date, and Optional).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

import pytest

from scriptkit import ScriptSettings, build_parser_from_settings

# ──────────────────────────────────────────────────────────────────────────────
# Fixtures & Helpers
# ──────────────────────────────────────────────────────────────────────────────

class Color(Enum):
    RED = "r"
    GREEN = "g"
    BLUE = "b"


@dataclass(frozen = True)
class Demo(ScriptSettings):
    temp_val: int = 42
    temp_bool: bool = False


@dataclass(frozen = True)
class Typed(ScriptSettings):
    ratio: float = 1.5
    price: Decimal = Decimal("9.99")
    ident: UUID = UUID("00000000-0000-0000-0000-000000000001")
    color: Color = Color.RED
    mode: Literal["fast", "slow"] = "fast"
    tags: list[str] = field(default_factory = list)
    sizes: list[int] = field(default_factory = list)
    cutoff: datetime = datetime(2020, 1, 1, 0, 0, 0)
    day: date = date(2020, 1, 1)
    # Both spellings are exercised on purpose: Optional[X] resolves to
    # typing.Union while X | None resolves to types.UnionType, and the parser
    # must unwrap both. Keep the Optional[...] form despite UP045.
    maybe: Optional[int] = None  # noqa: UP045
    maybe_color: Color | None = None


# ──────────────────────────────────────────────────────────────────────────────
# Precedence & path cascade
# ──────────────────────────────────────────────────────────────────────────────

def test_path_cascade_and_defaults(tmp_path):
    s = Demo(dir_base = tmp_path)
    assert s.temp_val == 42
    assert s.temp_bool is False
    assert s.dir_data == tmp_path / "data"
    assert s.dir_output == tmp_path / "output"
    # __post_init__ creates the output dir.
    assert s.dir_output.exists()


def test_default_is_dataclass_default(monkeypatch):
    monkeypatch.delenv("APP_TEMP_VAL", raising = False)
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
    monkeypatch.delenv("APP_TEMP_BOOL", raising = False)
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
    monkeypatch.delenv("APP_DIR_BASE", raising = False)
    monkeypatch.chdir(tmp_path)
    parser = build_parser_from_settings(Demo)
    args = parser.parse_args([])
    assert args.dir_base == tmp_path


def test_version_flag_exits(capsys):
    parser = build_parser_from_settings(Demo, version = "1.2.3")
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])
    assert "1.2.3" in capsys.readouterr().out


# ──────────────────────────────────────────────────────────────────────────────
# Scalars (construct straight from a string, no special handling)
# ──────────────────────────────────────────────────────────────────────────────

def test_float_scalar():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--ratio", "2.75"]).ratio == 2.75


def test_decimal_and_uuid_scalars():
    parser = build_parser_from_settings(Typed)
    args = parser.parse_args(
        ["--price", "3.50", "--ident", "12345678-1234-5678-1234-567812345678"]
    )
    assert args.price == Decimal("3.50")
    assert args.ident == UUID("12345678-1234-5678-1234-567812345678")


# ──────────────────────────────────────────────────────────────────────────────
# Enum (matched by name)
# ──────────────────────────────────────────────────────────────────────────────

def test_enum_by_name_cli():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--color", "GREEN"]).color is Color.GREEN


def test_enum_default_used():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args([]).color is Color.RED


def test_enum_env_by_name(monkeypatch):
    monkeypatch.setenv("APP_COLOR", "BLUE")
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args([]).color is Color.BLUE


def test_enum_rejects_value_spelling(capsys):
    # Members are matched by name, so the underlying value ("g") is invalid.
    parser = build_parser_from_settings(Typed)
    with pytest.raises(SystemExit):
        parser.parse_args(["--color", "g"])
    assert "choose from" in capsys.readouterr().err


# ──────────────────────────────────────────────────────────────────────────────
# Literal (choices)
# ──────────────────────────────────────────────────────────────────────────────

def test_literal_choice_accepted():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--mode", "slow"]).mode == "slow"


def test_literal_rejects_unknown(capsys):
    parser = build_parser_from_settings(Typed)
    with pytest.raises(SystemExit):
        parser.parse_args(["--mode", "medium"])
    assert "invalid choice" in capsys.readouterr().err


# ──────────────────────────────────────────────────────────────────────────────
# list[X] (nargs on CLI, comma-separated in env)
# ──────────────────────────────────────────────────────────────────────────────

def test_list_str_cli_nargs():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--tags", "a", "b", "c"]).tags == ["a", "b", "c"]


def test_list_int_casts_elements():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--sizes", "1", "2", "3"]).sizes == [1, 2, 3]


def test_list_default_is_empty():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args([]).tags == []


def test_list_env_comma_separated(monkeypatch):
    monkeypatch.setenv("APP_SIZES", "4, 5 ,6")
    parser = build_parser_from_settings(Typed)
    # Whitespace around each item is trimmed, then cast to int.
    assert parser.parse_args([]).sizes == [4, 5, 6]


# ──────────────────────────────────────────────────────────────────────────────
# datetime / date (ISO 8601 via fromisoformat)
# ──────────────────────────────────────────────────────────────────────────────

def test_datetime_isoformat():
    parser = build_parser_from_settings(Typed)
    args = parser.parse_args(["--cutoff", "2023-06-15T08:30:00"])
    assert args.cutoff == datetime(2023, 6, 15, 8, 30, 0)


def test_date_isoformat():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--day", "2023-06-15"]).day == date(2023, 6, 15)


def test_datetime_env(monkeypatch):
    monkeypatch.setenv("APP_CUTOFF", "2024-12-31T23:59:59")
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args([]).cutoff == datetime(2024, 12, 31, 23, 59, 59)


# ──────────────────────────────────────────────────────────────────────────────
# Optional[...] wrapping other supported types
# ──────────────────────────────────────────────────────────────────────────────

def test_optional_defaults_to_none():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args([]).maybe is None


def test_optional_int_can_be_set():
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--maybe", "5"]).maybe == 5


def test_optional_enum_redispatches_to_enum():
    # Optional[Color] must unwrap and still match Color members by name.
    parser = build_parser_from_settings(Typed)
    assert parser.parse_args(["--maybe-color", "GREEN"]).maybe_color is Color.GREEN


def test_typed_settings_construct_from_defaults(tmp_path):
    # The whole dataclass round-trips: parsed args populate a real instance.
    parser = build_parser_from_settings(Typed)
    args = parser.parse_args(["--dir-base", str(tmp_path)])
    s = Typed(**vars(args))
    assert s.color is Color.RED
    assert s.mode == "fast"
    assert s.tags == []
    assert s.maybe is None
