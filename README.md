# py-scriptkit

A small, standard-library-only toolkit that gives single-file Python scripts a
consistent spine: dataclass-driven config (CLI + environment variables),
structured logging, and a few utilities. Scripts depend on it by pinning a
released version, so a script keeps running against the scriptkit it was born
with even after the library moves on.

> Repository: `py-scriptkit` · import name: `scriptkit` (`import scriptkit`).

## File architecture

```
py-scriptkit/
├── src/scriptkit/          the package (import name = scriptkit)
│   ├── __init__.py         public API + __version__ (single source of truth)
│   ├── settings.py         ScriptSettings, build_parser_from_settings, parse_settings
│   ├── logging.py          get_logger / set_log_level (RichLogger or stdlib shim)
│   ├── times.py            timestamp()
│   └── azure.py            lazy DefaultAzureCredential helper
├── templates/
│   └── script_template.py  the canonical starting point for a new script
├── tests/                  pytest suite (one file per module)
├── .github/workflows/      ruff + pytest on 3.11 / 3.12 (see ROADMAP for expansion)
├── .vscode/                run / debug / test config
├── setup-venvs.ps1         builds the per-version dev venvs
├── pyproject.toml          package metadata (version is dynamic — read from __init__)
├── CHANGELOG.md            per-release notes, keyed by git tag
└── ROADMAP.md              phased action plan across the three repos
```

`src/scriptkit/` is the standard "src layout": `src/` keeps the package off the
repo root so tests run against the installed copy, and `scriptkit/` is the
package folder (its name is the import name).

## One-time setup (development)

Only needed to develop scriptkit itself (editing `src/scriptkit/`, running
tests). Consuming scripts don't need this — they just `uv run` (see below).

Install [uv](https://docs.astral.sh/uv/):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Create the per-version dev virtualenvs (one editable `.[dev]` install per
supported Python minor version):

```powershell
.\setup-venvs.ps1            # builds .venv311 / .venv312 / .venv313
.\setup-venvs.ps1 -Force     # delete and recreate them
```

VS Code uses `.venv313` by default for IntelliSense, linting, and debugging
(switch with *Python: Select Interpreter* or the versioned debug configs).

## Execution

### Using scriptkit in a script

Consumers don't install scriptkit — they pin a released tag in the script's
PEP 723 header, and `uv run` fetches it on first run:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v0.2.3",
# ]
# ///
from dataclasses import dataclass
from scriptkit import ScriptSettings, get_logger, parse_settings

logger = get_logger(__file__)

@dataclass(frozen=True)
class Settings(ScriptSettings):
    name: str = "World"      # -> --name / APP_NAME, default "World"
```

What a script inherits from the package:

| API | Purpose |
| --- | --- |
| `ScriptSettings` | frozen-dataclass config base; `dir_base` → `data/` / `output/` path cascade |
| `parse_settings(cls)` | build a CLI + env wiring from the dataclass (precedence: **CLI > env > default**) |
| `get_logger` / `set_log_level` | RichLogger console output, or a stdlib fallback with the same semantic methods |
| `timestamp(granularity)` | compact UTC stamps (year → second) |
| `scriptkit.azure.get_credential` | lazy `DefaultAzureCredential` |

The semantic logging vocabulary (`stage`, `step`, `substep`, `config`, `metric`,
`result`, `read`, `write`, `meta`, `alert`, `check`, plus stdlib `info` /
`warning` / `error` / `debug`) works identically under RichLogger and the
fallback. Add the `[rich]` extra to the pin
(`scriptkit[rich] @ git+...@v0.2.3`) for decorated console output; without it,
the same calls print plain `[TAG]`-prefixed lines.

## Maintenance

All commands below assume the dev venvs from `setup-venvs.ps1` exist (each is an
editable `.[dev]` install, so ruff and pytest are present). Every one also has a
VS Code task — run it from **Terminal → Run Task** instead of typing the path if
you prefer.

### Linting & formatting

Ruff is configured in [`pyproject.toml`](pyproject.toml) under `[tool.ruff]`
(line length, pinned rule set, `templates/` excluded). From the repo root:

```powershell
.\.venv313\Scripts\python.exe -m ruff check .          # report lint issues
.\.venv313\Scripts\python.exe -m ruff check --fix .    # apply the safe auto-fixes
.\.venv313\Scripts\python.exe -m ruff format .         # reformat in place
```

Lint is Python-version-independent, so the default `.venv313` is enough. Tasks:
**`ruff check`**, **`ruff format`**. Format-on-save is already enabled for Python
files ([.vscode/settings.json](.vscode/settings.json)), so day to day you mostly
just save.

### Tests

The suite lives in `tests/` (one file per module; `testpaths` set in
`pyproject.toml`). Run it on the default version:

```powershell
.\.venv313\Scripts\python.exe -m pytest -q
```

Run it on all three supported versions — the local equivalent of the CI matrix,
and every public API must pass on each:

```powershell
.\.venv311\Scripts\python.exe -m pytest -q; .\.venv312\Scripts\python.exe -m pytest -q; .\.venv313\Scripts\python.exe -m pytest -q
```

Tasks: **`pytest (3.13)`** (default test task), **`pytest (3.11/3.12)`**,
**`pytest (all versions)`** — or the VS Code Testing beaker.

### Versioning

[Semantic Versioning](https://semver.org): **PATCH** = fixes, **MINOR** = new
backward-compatible features, **MAJOR** = breaking changes. Scripts pin a tag, so
a published tag is a promise — **never move a tag after release; only add new
ones.**

### The release checklist

Assume nothing about prior versioning knowledge; every step is spelled out.

1. **Make the change** under `src/scriptkit/`, with tests in `tests/`.
2. **Bump `__version__`** in [`src/scriptkit/__init__.py`](src/scriptkit/__init__.py).
   **Do NOT edit a version in `pyproject.toml`** — there isn't one to edit. The
   version is declared `dynamic` and hatch reads it from `__version__`
   automatically (see `[tool.hatch.version]`).
3. **Only touch `pyproject.toml`** if you **add or change dependencies or
   extras** (`[project.dependencies]` / `[project.optional-dependencies]`).
   Nothing else there changes per release.
4. **Add a `CHANGELOG.md` entry** under a new `## [vX.Y.Z]` heading (move items
   out of `## [Unreleased]`), grouped `Added` / `Changed` / `Fixed`.
5. **Go green:**
   ```powershell
   .\.venv313\Scripts\python.exe -m ruff check .
   .\.venv313\Scripts\python.exe -m pytest -q
   ```
   (Or the `ruff check` / `pytest (all versions)` VS Code tasks.)
6. **Commit, tag, push:**
   ```powershell
   git commit -am "Release vX.Y.Z: <summary>"
   git tag vX.Y.Z
   git push origin main --tags
   ```
7. **Move scripts onto the new version** by bumping the pins where the default
   lives: `templates/script_template.py`, each repo's `new-script.ps1` default
   `-Tag`, the READMEs, and any example scripts. **Existing scripts keep their
   old pin on purpose** — bump a script's header only when you want the new
   behavior.
8. **Confirm** CI is green and at least one `uv run <script>` resolves the new
   tag.

### Rules

- Stay standard-library-only; heavy dependencies go behind an optional extra
  (like `[rich]` / `[azure]`), never in the base install.
- Every public API has a test; CI must be green before tagging.
- Anything printed stays ASCII-safe in logs (avoid characters a legacy Windows
  console can't render).
