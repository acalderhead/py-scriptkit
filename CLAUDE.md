# CLAUDE.md — py-scriptkit

Session handoff for future Claude Code sessions. Read this first.

## What this is
`py-scriptkit` is a **stdlib-first toolkit** for single-file Python scripts:
dataclass config with CLI + env wiring, semantic logging (RichLogger or a stdlib
shim), and small utilities. Import name is `scriptkit`. **This is the only
versioned repo** of the three; the two script repos (`py-scripts`,
`py-scripts-cenvar`, siblings under `../`) *point* at a released tag, never
carry their own version.

- Current release: **v0.5.4** (git tags `vX.Y.Z`; `__version__` in
  `src/scriptkit/__init__.py` is the single source of truth — `pyproject.toml`
  reads it dynamically, do NOT add a version there).
- GitHub: `github.com/acalderhead/py-scriptkit` (pushes over https work).

## Layout
- `src/scriptkit/` — the package: `settings.py` (ScriptSettings + auto-CLI parser),
  `logging.py` (get_logger/set_log_level), `times.py`, `azure.py`, `cli.py`
  (`scriptkit new` — scaffolds a **module**, not a script), `templates/`
  (script_template.py, module_template.py, test_template.py — the single source
  of truth all repos scaffold from).
- `tests/` — one file per module, pytest.
- `new-module.ps1` / `new-test.ps1` (+ `.bat`) — local dev scaffolders.
- `setup-venvs.ps1` — builds `.venv311/312/313` (uv-managed, editable `.[dev]`).

## Conventions (important — the user is exacting about these)
- **Formatting = Ruff as LINTER only, no autoformatter.** `.gitattributes`,
  `[tool.ruff]` in pyproject. House style: **spaces around keyword/default `=`**
  (`frozen = True`) — that's why `E251` etc. are ignored. Manual vertical column
  alignment is allowed (whitespace lint rules relaxed).
- **Section headers**: 80-wide `# ─` dividers ordered **Constants → Public API →
  Internal Helpers**. Sectioned module docstrings (`Purpose`/`Context`/`Public
  API`/`Usage`/`Notes` with `───` underlines). Function docstrings: purpose,
  then `arg : description`, then Returns/Raises.
- **`.ps1`/`.bat` must be ASCII** (PS 5.1 reads them as cp1252; non-ASCII breaks
  parsing). `.ps1`/`.bat` are `eol=crlf` in `.gitattributes`; source is LF.
- Anything printed stays ASCII-safe (legacy Windows console).

## Toolchain / verify (PowerShell — NOT bash; `;` not `&&`, no `sed`)
```powershell
.\.venv313\Scripts\python.exe -m pytest -q
.\.venv313\Scripts\python.exe -m ruff check src tests
.\.venv313\Scripts\python.exe -m pyright src
```
Run these before any release. The README's **"The release checklist"** section
is the authoritative release process — follow it, don't improvise.

## Release model
Only py-scriptkit is tagged. To cut a release: bump `__version__`, bump the
`templates/script_template.py` PEP 723 pin, move CHANGELOG `[Unreleased]` → a
dated `[vX.Y.Z]`, go green, commit + tag + push. Then bump the "current version"
pointers in the two script repos (their `new-script.ps1`/`new-test.ps1` `-Tag`
defaults and README pins) — but NOT individual scripts' frozen pins.

## State toward v1.0.0
Phases 2, 5, 7 done; script template restored; output defaults outside the repo
(`~/_repo-output/<script-name>`, `dir_output` == `dir_base`). ROADMAP's remaining
gate is Phase 6 (templates in the script repos). See ROADMAP.md and CHANGELOG.md.
