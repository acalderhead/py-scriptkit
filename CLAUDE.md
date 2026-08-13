# CLAUDE.md: py-scriptkit

Orientation for a new session. Read this first, then the README for any process it
points at.

## The setup in one paragraph
py-scriptkit is a stdlib-first toolkit for single-file Python scripts: dataclass
config wired to a CLI and environment variables, semantic logging (RichLogger or a
stdlib shim), and small utilities. It is one of three sibling repos under `../`.
This one is the library and the only versioned repo. The other two, `py-scripts`
and `py-scripts-cenvar`, are collections of scripts that pin a released tag of this
library and carry no version of their own. Import name is `scriptkit`. Current
release is v1.0.0, the first stable tag.

## The model everything depends on
A script names a scriptkit tag in its PEP 723 header and `uv run` fetches exactly
that tag. A published tag is therefore a promise to code running on machines you
cannot see: add tags, never move one. That single fact is why the release process
is strict, why `__version__` is the only place a version is written in the
package, and why bumping the library never disturbs a script until someone edits
its header.

## Common errors
The ones worth knowing before you touch anything:
- Running `ruff format`. There is no autoformatter, on purpose. The house style
  hand-aligns `=` columns, and every formatter (`ruff format`, Black, YAPF)
  destroys that alignment. Lint with `ruff check`; never format.
- Linting or type-checking `templates/`. The three templates are data, not package
  surface, and are full of intentional placeholders. They are excluded from ruff
  and pyright in `pyproject.toml`; a report of errors inside them means a tool was
  pointed there by hand.
- Editing a version anywhere but `__version__`. Adding one to `pyproject.toml` is
  the classic mistake; the field is declared `dynamic` under
  `[tool.hatch.version]` and there is nothing to edit.
- Forgetting a pin at release time. The tag is written by hand in several places:
  `templates/script_template.py`, the docstrings in `cli.py` and `logging.py`,
  both script repos' `-Tag` defaults, and the READMEs. They drift; right before
  1.0 the tree had four different versions live at once. Release-checklist step 7
  lists them, and all of them move together.
- A change that passes on 3.13 and fails on 3.11. CI is `{ubuntu,windows}` against
  `{3.11,3.12,3.13}`, and 3.11 is the pyright baseline. Run the `pytest (all
  versions)` task before tagging, not just the default.
- Non-ASCII in a `.ps1` or `.bat`. PS 5.1 reads them as cp1252, so a stray Unicode
  character breaks parsing. Source is LF; `.ps1`/`.bat` are `eol=crlf`. Anything
  the package prints stays ASCII-safe for the same reason (the `--help` crash on
  cp1252 was a real bug, fixed in 0.5.3 by forcing UTF-8 stdio).
- Reaching for bash. This is PowerShell: `;` not `&&`, no `sed`. Hand the user
  PowerShell.

## Invariants
- `__version__` in `src/scriptkit/__init__.py` is the single source of truth.
- Base install is standard-library only. Anything heavier hides behind an extra
  (`[rich]`, `[azure]`), never the base.
- Every public API has a test, and CI is green before a tag exists. A consumer
  pins tags, so a broken tag is permanent.

## Verify
```powershell
.\.venv313\Scripts\python.exe -m ruff check .
.\.venv313\Scripts\python.exe -m pyright
.\.venv313\Scripts\python.exe -m pytest -q
```
All three before any release. The README's "Cutting a release" is the
authoritative process; follow it rather than improvising.

## Map
The full tree is in the README. What you edit:
- `src/scriptkit/`: `settings.py` (ScriptSettings and the auto-CLI parser),
  `logging.py`, `times.py`, `azure.py`, `cli.py` (`scriptkit new`, which scaffolds
  a module, not a script).
- `src/scriptkit/templates/`: `script_template.py`, `module_template.py`,
  `test_template.py`, the source of truth all repos scaffold from.
- `tests/`: one file per module.
- `new-module.ps1` and `new-test.ps1` (plus `.bat` launchers) scaffold locally;
  `setup-venvs.ps1` builds `.venv311/312/313`.

## Conventions
- Section headers are 80-wide `# ─` dividers ordered Constants, Public API,
  Internal Helpers. Module docstrings are sectioned (Purpose, Context, Public API,
  Usage, Notes, with `───` underlines). Function docstrings run purpose, then
  `arg : description`, then Returns and Raises.
- Shared logic belongs in the library, promoted into a release, not pasted into a
  script.

## Where things stand
v1.0.0 is the first stable tag. The roadmap that led here is complete:
richer-typed auto-CLI, Ruff as linter, the three templates as source of truth, and
editor run and debug through `uv run`. One loose end worth a glance is whether
py-scripts-cenvar tracks the current release the way py-scripts does. Post-1.0
directions are parked in IDEAS.md; the next tag follows the README's "Cutting a
release" checklist.
