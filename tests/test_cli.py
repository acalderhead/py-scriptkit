"""Tests for scriptkit.cli: the `scriptkit new` scaffolder."""

import pytest

from scriptkit import __version__
from scriptkit.cli import _slugify, main


def test_slugify_normalizes_to_snake_case():
    assert _slugify("Reconcile Invoices") == "reconcile_invoices"
    assert _slugify("backup-photos.py") == "backup_photos"
    assert _slugify("  weird__Name!! ") == "weird_name"


def test_slugify_rejects_empty():
    with pytest.raises(ValueError):
        _slugify("!!!")


def test_new_creates_pinned_script(tmp_path):
    rc = main(["new", "my_tool", "--dir", str(tmp_path), "--tag", "v9.9.9"])
    assert rc == 0
    created = tmp_path / "my_tool.py"
    assert created.exists()
    text = created.read_text(encoding="utf-8")
    # The pin was repointed to the requested tag...
    assert "py-scriptkit.git@v9.9.9" in text
    # ...and no stale pin from the template survives.
    assert "@v0." not in text
    # It's a real, runnable skeleton (template body carried over).
    assert "class Settings(ScriptSettings)" in text


def test_new_default_tag_is_this_version(tmp_path):
    rc = main(["new", "demo", "--dir", str(tmp_path)])
    assert rc == 0
    text = (tmp_path / "demo.py").read_text(encoding="utf-8")
    assert f"py-scriptkit.git@v{__version__}" in text


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
    target = tmp_path / "nested" / "scripts"
    rc = main(["new", "deep", "--dir", str(target)])
    assert rc == 0
    assert (target / "deep.py").exists()


def test_version_flag_reports_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out
