# Changelog

All notable changes to `scriptkit` are documented here. Versions follow
[Semantic Versioning](https://semver.org). Each released version has a git tag
(`vX.Y.Z`) that scripts pin against.

## [Unreleased]

## [0.5.3] — 2026-08-12

### Fixed
- `parse_settings` now forces UTF-8 stdout/stderr, so `--help` (which echoes the
  script docstring's box-drawing underlines) no longer crashes with
  `UnicodeEncodeError` on a legacy Windows codepage (cp1252). Guarded so pytest's
  captured streams are left untouched.

### Changed
- The script template exposes `dir_base` as a field on `Settings`, defaulting
  **outside the repo** (`~/script-output/<script-name>`) so runs never write into
  version control, with a one-line example to repoint it (e.g. next to the
  script). `dir_data` / `dir_output` still cascade from it.

## [0.5.2] — 2026-08-12

### Added
- Double-click `.bat` launchers next to every `.ps1` (setup-venvs, new-module,
  new-test here; new-script/new-test in the downstream repos). Double-clicking
  the `.bat` in File Explorer runs the scaffolder — it prompts for a name,
  bypasses the execution policy for that one process, and pauses on the result
  — so no terminal or execution-policy setup is needed.

## [0.5.1] — 2026-08-12

### Added
- `new-module.ps1` and `new-test.ps1` — Windows scaffolders that copy the
  bundled `module_template.py` / `test_template.py` (local-dev companions to the
  cross-platform `scriptkit new`).

### Restored
- `templates/script_template.py` — brought back (it was removed in 0.5.0). It is
  the copy `scriptkit new`-style scaffolders and the downstream repos'
  `new-script.ps1` point at; py-scriptkit remains the single source of truth for
  all three templates. The template imports scriptkit (no inlined machinery) and
  pins `@v0.5.1`.

## [0.5.0] — 2026-08-12

### Added
- The auto-CLI parser (`build_parser_from_settings` / `parse_settings`) now
  wires richer field types beyond scalars and `bool`: `Enum` and `Literal[...]`
  (constrained choices), `datetime` / `date` (ISO 8601 via `fromisoformat`),
  `list[X]` (repeatable on the CLI, comma-separated in the env var), and
  `Optional[...]` wrapping any supported type (unwrapped then re-dispatched, so
  `Optional[list[X]]` / `Optional[Enum]` compose). Enum members are matched by
  **name** (`--color RED`) on both the CLI and env paths. Types that can't map
  to a single CLI argument (dict, tuple, non-Optional unions) are still skipped
  and left to bespoke handling.
- Two new bundled templates: `templates/module_template.py` (importable modules)
  and `templates/test_template.py` (pytest files), each carrying the project's
  section-header + docstring style.

### Changed
- **`scriptkit new` now scaffolds a module** from `module_template.py` instead
  of a script. The PEP 723 pin-rewrite step and the `--tag` flag are gone
  (modules carry no dependency pin); `--dir` now defaults to the current
  directory.
- Formatting is enforced by Ruff-as-linter only (no autoformatter); the whole
  package and its tests were restyled to a consistent house style — sectioned
  module docstrings, `# ───` section headers ordered Constants → Public API →
  Internal Helpers, and spaces around keyword/default `=`.

### Removed
- `templates/script_template.py` — py-scriptkit is now a module-first library;
  script templates live in the downstream script repos.

## [0.4.0] — 2026-07-24

### Added
- `scriptkit new NAME [--tag] [--dir] [--force]` — a cross-platform console
  entry point (`[project.scripts]`) that scaffolds a new pinned script from the
  bundled template. Replaces the per-repo, Windows-only `new-script.ps1`.
  Invoke from a dev `.venv` or via
  `uvx --from "scriptkit @ git+...@v0.4.0" scriptkit new my_tool`.
- The script template now ships inside the package
  (`scriptkit/templates/script_template.py`) so the scaffolder works without a
  local checkout of this repo.

### Changed
- The canonical template moved from `templates/` to
  `src/scriptkit/templates/`; ruff and pyright exclude it (it is data, not
  checked package surface).

## [0.3.0] — 2026-07-24

### Added
- Ship a PEP 561 `py.typed` marker so consumer scripts (and their type
  checkers) pick up scriptkit's inline type information.
- Static type checking with `pyright` (added to the `dev` extra and run in CI),
  configured via `[tool.pyright]` against the 3.11 baseline.

### Changed
- CI matrix expanded to **{ubuntu, windows} × {3.11, 3.12, 3.13}** (6 jobs);
  Windows and Python 3.13 are now exercised on every push. Minimum supported
  Python stays 3.11.

## [0.2.4] — 2026-07-24

### Changed
- `[rich]` extra now pins `rich_logger` v1.0.4, whose semantic-log labels match
  the method that triggers them (e.g. `substep` → SUBSTEP, `info` → INFO)
  instead of the old aliases (SUB, STATUS).
- Renamed semantic method `meta` → `metadata` (label METADATA) to match
  rich_logger v1.0.4. The stdlib fallback shim is updated in lockstep, so both
  backends expose the same vocabulary. **Breaking:** any caller using
  `logger.meta(...)` must switch to `logger.metadata(...)` (no in-repo callers
  used it).

## [0.2.3] — 2026-07-24

Development-tooling and documentation release — the shipped `scriptkit` package
is unchanged from 0.2.1 (identical public API and behavior).

### Changed
- Development environment now builds one uv-managed venv per supported Python
  version (`.venv311` / `.venv312` / `.venv313`) via `setup-venvs.ps1`, with
  matching VS Code run / debug / test tasks, so the suite can be exercised on
  every version the package claims to support.
- README reorganized around a step-by-step Maintenance guide (linting, tests,
  release checklist).

### Fixed
- `setup-venvs.ps1` no longer aborts on re-run when the interpreters are already
  present (Windows PowerShell was treating uv's stderr progress as fatal).

Note: `0.2.2` was tagged on a docs-only commit with no version bump or changelog
entry; `0.2.3` supersedes it and is the first properly cut release since 0.2.1.

## [0.2.1] — 2026-07-24

### Changed
- `--help` now preserves the script docstring's layout (section headings and
  line breaks) instead of reflowing it into a single paragraph, while still
  showing each option's default. (New `_ScriptHelpFormatter`.)

### Fixed
- `get_logger` derives the logger name correctly on any OS when given a
  Windows-style path (previously only split on the host OS's separator).

## [0.2.0] — 2026-07-24

First published release: the common single-file-script infrastructure as an
installable, versioned package.

### Added
- `ScriptSettings` — frozen-dataclass config base with a `dir_base` → `data/` /
  `output/` path cascade.
- `build_parser_from_settings` / `parse_settings` — auto-generate a CLI and
  environment-variable wiring from a dataclass (precedence: CLI > env > default),
  now resolving `default_factory` fields such as `dir_base`.
- `get_logger` / `set_log_level` — RichLogger when installed, otherwise a stdlib
  fallback that still answers the semantic vocabulary (`stage`, `metric`, …) via
  `[TAG]` prefixes.
- `timestamp` — compact UTC stamps at year → second granularity.
- `scriptkit.azure.get_credential` — lazy `DefaultAzureCredential` helper.
- Thin `templates/script_template.py` with a PEP 723 header for `uv run`.
