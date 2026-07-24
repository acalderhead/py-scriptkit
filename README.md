# py-scriptkit

A small, standard-library-only toolkit that gives single-file Python scripts a consistent spine: dataclass-driven config (CLI + environment variables), structured logging, and a few utilities. Scripts depend on it by pinning a released version.

> Repository: `py-scriptkit` · import name: `scriptkit` (`import scriptkit`).

## Use it in a script

Pin a released tag in the script's PEP 723 header and run with [uv](https://docs.astral.sh/uv/):

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v0.2.1",
# ]
# ///
from dataclasses import dataclass
from scriptkit import ScriptSettings, get_logger, parse_settings

logger = get_logger(__file__)

@dataclass(frozen=True)
class Settings(ScriptSettings):
    name: str = "World"      # -> --name / APP_NAME, default "World"
```

Add `[rich]` for decorated console logging: `scriptkit[rich] @ git+...@v0.2.1`.

## What you get

| API | Purpose |
| --- | --- |
| `ScriptSettings` | frozen-dataclass config base; `dir_base` → `data/` / `output/` path cascade |
| `parse_settings(cls)` | build a CLI + env wiring from the dataclass (precedence: **CLI > env > default**) |
| `get_logger` / `set_log_level` | rich console logging, or a stdlib fallback with the same semantic methods |
| `timestamp(granularity)` | compact UTC stamps (year → second) |
| `scriptkit.azure.get_credential` | lazy `DefaultAzureCredential` |

## Layout

```
src/scriptkit/       the package (settings, logging, times, azure)
templates/           script_template.py — the canonical starting point
tests/               pytest suite
.github/workflows/   ruff + pytest on 3.11 / 3.12
```

`src/scriptkit/` is the standard "src layout": `src/` keeps the package off the
repo root so tests run against the installed copy, and `scriptkit/` is the
package folder (its name is the import name).

## Versioning

[Semantic Versioning](https://semver.org): **PATCH** = fixes, **MINOR** = new
backward-compatible features, **MAJOR** = breaking changes. Scripts pin a tag, so
a published tag is a promise — never move one after release; only add new ones.

## Cutting a release

```powershell
uv pip install -e ".[dev]"              # once, in a local .venv
# 1. make the change under src/scriptkit/ (+ tests)
# 2. bump __version__ in src/scriptkit/__init__.py
# 3. add a CHANGELOG.md entry
uv run --no-project python -m ruff check .
uv run --no-project python -m pytest -q
git commit -am "Release vX.Y.Z: <summary>"
git tag vX.Y.Z
git push origin main --tags
```

## Maintenance rules

- Stay standard-library-only; heavy dependencies go behind an optional extra
  (like `[rich]` / `[azure]`), never in the base install.
- Every public API has a test; CI must be green before tagging.
- Anything printed stays ASCII-safe in logs (avoid characters a legacy Windows
  console can't render).
