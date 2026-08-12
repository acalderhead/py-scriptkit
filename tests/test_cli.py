"""
Purpose
───────
    Tests for scriptkit.cli: name slugifying, module scaffolding from the
    bundled template, overwrite behavior, and --version.
"""

from __future__ import annotations

import pytest

from scriptkit import __version__
from scriptkit.cli import _slugify, main

# ──────────────────────────────────────────────────────────────────────────────
# Slugify
# ──────────────────────────────────────────────────────────────────────────────

def test_slugify_normalizes_to_snake_case():
    assert _slugify("Reconcile Invoices") == "reconcile_invoices"
    assert _slugify("backup-photos.py") == "backup_photos"
    assert _slugify("  weird__Name!! ") == "weird_name"


def test_slugify_rejects_empty():
    with pytest.raises(ValueError):
        _slugify("!!!")


# ──────────────────────────────────────────────────────────────────────────────
# scriptkit new
# ──────────────────────────────────────────────────────────────────────────────

def test_new_creates_module(tmp_path):
    rc = main(["new", "my_module", "--dir", str(tmp_path)])
    assert rc == 0
    created = tmp_path / "my_module.py"
    assert created.exists()
    text = created.read_text(encoding = "utf-8")
    # The bundled module template body carried over.
    assert "__all__" in text
    assert "def placeholder_func" in text


def test_new_writes_lf_line_endings(tmp_path):
    main(["new", "demo", "--dir", str(tmp_path)])
    raw = (tmp_path / "demo.py").read_bytes()
    assert b"\r\n" not in raw


def test_new_refuses_overwrite_without_force(tmp_path, capsys):
    main(["new", "dup", "--dir", str(tmp_path)])
    rc = main(["new", "dup", "--dir", str(tmp_path)])
    assert rc == 1
    assert "Refusing to overwrite" in capsys.readouterr().err


def test_new_force_overwrites(tmp_path):
    main(["new", "dup", "--dir", str(tmp_path)])
    rc = main(["new", "dup", "--dir", str(tmp_path), "--force"])
    assert rc == 0


def test_new_creates_target_dir(tmp_path):
    target = tmp_path / "nested" / "pkg"
    rc = main(["new", "deep", "--dir", str(target)])
    assert rc == 0
    assert (target / "deep.py").exists()


# ──────────────────────────────────────────────────────────────────────────────
# Version
# ──────────────────────────────────────────────────────────────────────────────

def test_version_flag_reports_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out
