# py-scriptkit

Stdlib-first toolkit for single-file Python scripts — dataclass config with CLI+env wiring, semantic logging with a rich fallback, and small utilities. Consumed via versioned git tags.

> **Repo `py-scriptkit`, import name `scriptkit`.** The repository is
> `py-scriptkit`; the installable/importable package is `scriptkit`
> (`import scriptkit`). Repo-name ≠ import-name is normal and intentional.

---

## The bigger picture

This is one of three repos that make up a personal Python system:

| Repo | Role | Owner |
| --- | --- | --- |
| **py-scriptkit** (this one) | the **library + template** — the source of truth | personal · public |
| [py-scripts](https://github.com/acalderhead/py-scripts) | personal utility scripts | personal |
| [py-cenvar-scripts](https://github.com/acalderhead/py-cenvar-scripts) | Cenvar / work utility scripts | Cenvar / work |

The script repos never copy this code — each script **pins a released tag** of
`scriptkit` in its PEP 723 header and fetches it via `uv`. That keeps one source
of truth here while letting every script stay reproducible against the exact
version it was written for.

## Why this exists

Every utility script needs the same plumbing: argument parsing, environment
overrides, sensible paths, structured logging, a clean failure path. Re-inlining
that at the top of every file (the old `py_template_v2.py` approach) meant fixing
the same bug in a dozen places. `scriptkit` extracts it once, versions it, and
lets scripts inherit it.

## Layout

```
py-scriptkit/
├─ src/scriptkit/            the library (importable, SemVer-tagged)
│  ├─ __init__.py            public API + __version__ (single source of truth)
│  ├─ settings.py            ScriptSettings + auto CLI/env parser (CLI > env > default)
│  ├─ logging.py             get_logger: RichLogger, or a semantic-aware stdlib fallback
│  ├─ times.py               timestamp()
│  └─ azure.py               lazy DefaultAzureCredential seam
├─ templates/
│  └─ script_template.py     the canonical thin template (PEP 723 header)
├─ tests/                    pytest suite for scriptkit
├─ .vscode/                  shared run/debug/test config
├─ pyproject.toml            hatchling build; [rich] / [azure] / [dev] extras
├─ CHANGELOG.md              one section per released version (drives the tags)
└─ .github/workflows/ci.yml  ruff + pytest on 3.11 / 3.12
```

### Why `src/scriptkit/` and not just `src/`

Two separate ideas are stacked here, and both are deliberate:

- **`src/` (the "src layout").** Keeping the package one level down from the repo
  root means tests run against the *installed* package, not the raw files in the
  working directory. This catches "works on my machine but the packaging is
  broken" bugs. It's the modern recommended layout for a distributable package.
- **`scriptkit/` (the package folder).** This directory name *is* the import
  name — `import scriptkit` maps to `src/scriptkit/`. It can't be flattened away;
  a package needs a folder to live in.

So `src/scriptkit/` = "the source root contains one package named scriptkit." Not
redundant — each part carries meaning. (The **script** repos have no `src/`
because they aren't packages; they're collections of standalone files.)

## Public API

```python
from scriptkit import (
    ScriptSettings,             # dataclass config base (subclass it)
    parse_settings,             # build a CLI + env wiring and return a Settings
    build_parser_from_settings, # the parser builder (if you need it directly)
    get_logger, set_log_level,  # RichLogger or stdlib fallback
    timestamp,                  # compact UTC stamps
)
```

`scriptkit.azure.get_credential()` is a lazy `DefaultAzureCredential` helper
(needs the `[azure]` extra).

---

## Developing the library

One-time setup (uses [uv](https://docs.astral.sh/uv/)):

```powershell
uv venv
uv pip install -e ".[dev]"      # installs scriptkit editable + pytest + ruff
```

Then:

```powershell
.\.venv\Scripts\python.exe -m pytest -q      # or: VS Code Testing beaker
.\.venv\Scripts\python.exe -m ruff check .
```

VS Code: open the folder, pick `.venv` as the interpreter (already the default in
`.vscode/settings.json`), and use the built-in **pytest** / **ruff check** tasks.

## Versioning & releasing — the important part

`scriptkit` uses [Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH`.

- **PATCH** (`0.1.0 → 0.1.1`): bug fixes, no behavior change for callers.
- **MINOR** (`0.1.0 → 0.2.0`): new capability, backward-compatible.
- **MAJOR** (`0.x → 1.0`, `1.x → 2.0`): a breaking change — a removed/renamed
  function, a changed signature, different default behavior.

**Why it matters:** scripts pin a tag. A script that says `@v0.1.0` keeps getting
exactly v0.1.0 forever, even after you release v2.0. That's the whole guarantee —
so honor SemVer, because a script author trusts that bumping a *minor* version is
safe and bumping a *major* version is a deliberate migration.

### Cutting a release

1. Make your changes under `src/scriptkit/` (and add/adjust tests).
2. Confirm green: `pytest -q` and `ruff check .`.
3. Bump `__version__` in **`src/scriptkit/__init__.py`** — this is the single
   source of truth; `pyproject.toml` reads it dynamically via hatchling.
4. Move the `CHANGELOG.md` `[Unreleased]` notes into a new dated version section.
5. Commit, tag, push:

   ```powershell
   git commit -am "Release v0.2.0: <summary>"
   git tag v0.2.0
   git push origin main --tags
   ```

That's it — the new tag is immediately usable as
`scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v0.2.0`.

### Upgrading a script to a new version

Scripts don't auto-upgrade (by design). To move a script forward, edit the tag in
its PEP 723 header (or re-scaffold with `new-script.ps1 -Tag vX.Y.Z`). Old scripts
you don't touch keep running on their original pin.

## Maintenance guidance

- **Keep it stdlib-first.** The value here is near-zero mandatory dependencies.
  New heavy dependencies belong behind an optional extra (like `[rich]` /
  `[azure]`), never in the base `dependencies`.
- **Everything public gets a test.** The suite is the contract scripts rely on.
- **Anything printed must be Windows-console safe** (avoid em-dashes and other
  non-cp1252 characters in log/`print` strings; box-drawing characters are fine
  in comments/docstrings since they're never emitted).
- **Update `CHANGELOG.md` in the same commit as the change**, not at release time
  — future-you will thank present-you.
- **CI (`.github/workflows/ci.yml`) must stay green** on 3.11 and 3.12 before you
  tag.
