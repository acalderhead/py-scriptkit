# py-scriptkit

A standard-library-only toolkit that gives a single-file Python script a spine:
dataclass-driven config wired to both a CLI and environment variables, structured
logging, and a few utilities that are tedious to rewrite for the twentieth time.

Nothing installs it. A script names a released tag in its PEP 723 header, and `uv`
fetches that exact tag on first run. This is the one decision the rest of the
project bends around. A script written in March keeps running against the
scriptkit it was written against, no matter what the library did in the nine
months since, and it keeps doing that without anyone maintaining it. The price is
that a published tag can never change, which is why the release process below
looks stricter than a personal library seems to warrant.

The repo is `py-scriptkit` and the import name is `scriptkit`. Current release is
**v1.0.0**.

| Section | What is in it |
| --- | --- |
| [Writing a script](#writing-a-script) | The pinned header, the settings dataclass, the API, the logger, and `scriptkit new`. This is why you are usually here. |
| [Cutting a release](#cutting-a-release) | The eight-step checklist, and the three constraints that decide what the library is allowed to become. |
| [Working on scriptkit](#working-on-scriptkit) | Dev venv setup, the lint and type and test gates, and where everything lives. |

Every command block here is Windows PowerShell, and the syntax assumes it:
statements chain with `;`, not `&&`; paths are written `.\name`; and interpreters
are called as `python.exe`. Run them in a PowerShell terminal. VS Code's
integrated terminal is PowerShell by default on Windows, so the blocks paste in
unchanged; if its default profile has been switched to Git Bash or cmd, pick a
PowerShell profile from the terminal dropdown first, or the `.\`, `;`, and `.exe`
forms will not behave the same. The uv installer is the exception: it invokes
`powershell` itself, so it runs from any shell.


## Writing a script

The pin goes in the header. Everything else is an ordinary frozen dataclass:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v1.0.0",
# ]
# ///
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from scriptkit import ScriptSettings, get_logger, parse_settings

logger = get_logger(__file__)

@dataclass(frozen=True)
class Settings(ScriptSettings):
    name: str = "World"           # -> --name / APP_NAME, default "World"
    retries: int = 3              # scalars, bool, Path, Decimal, UUID, ...
    mode: Literal["fast", "slow"] = "fast"   # Enum / Literal -> choices
    tags: list[str] = field(default_factory=list)  # --tags a b c / APP_TAGS=a,b,c
    since: datetime | None = None            # Optional[...] + ISO date/datetime
```

Every settable field turns into a `--flag` and also reads an `APP_*` environment
variable. The annotation does the work from there. `Enum` and `Literal` become
`choices`, so a bad value dies at the parser instead of somewhere in the middle
of the run. `list[X]` becomes `nargs`, and the env form takes the same values
comma-separated. `datetime` and `date` go through `fromisoformat`. `Optional[...]`
gets unwrapped to the type inside it before any of that happens. Precedence runs
CLI, then env, then the default in the dataclass.

That is the entire configuration story. What else a script gets:

| API | Purpose |
| --- | --- |
| `ScriptSettings` | frozen-dataclass config base; `dir_output` == `dir_base` (created on run), `dir_data` = `dir_base/data` |
| `parse_settings(cls)` | builds the CLI and env wiring off the dataclass; precedence is CLI > env > default |
| `get_logger` / `set_log_level` | RichLogger console output, or a stdlib fallback with the same semantic methods |
| `timestamp(granularity)` | compact UTC stamps, year down to second |
| `scriptkit.azure.get_credential` | lazy `DefaultAzureCredential` |

The logger takes a vocabulary aimed at what a script is actually doing rather than
at severity: `stage`, `step`, `substep`, `config`, `metric`, `result`, `read`,
`write`, `metadata`, `alert`, and `check`. The stdlib four are still there, so
`info`, `warning`, `error`, and `debug` work as usual.

Add the `[rich]` extra to the pin for decorated console output:

```
"scriptkit[rich] @ git+https://github.com/acalderhead/py-scriptkit.git@<tag>",
```

Leave the extra off and the identical calls print plain `[TAG]`-prefixed lines
through a shim. This matters because it means adding or dropping `rich` never
touches a line of script code.

### Starting from a template

`scriptkit new` writes a fresh copy of the bundled module template into the
current directory. A module carries no pin, since it imports scriptkit rather than
fetching it.

```powershell
.\.venv313\Scripts\scriptkit.exe new my_module
```

From git with nothing installed locally, substituting the current release from
the top of this file:

```powershell
uvx --from "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@<tag>" scriptkit new my_module
```

The full form is `scriptkit new NAME [--dir DIR] [--force]`. The name gets
normalized into a snake_case filename, and `--dir` defaults to wherever you are.

Single-file scripts are not scaffolded from here. Each script repo has its own
`new-script.ps1`, which is what stamps the pinned PEP 723 header.


## Cutting a release

Plain [semver](https://semver.org). PATCH for fixes, MINOR for features that break
nobody, MAJOR for anything that breaks a caller.

The rule that matters more than the numbering: a published tag is a promise.
Scripts resolve tags at runtime, on machines you are not sitting at, so moving a
tag rewrites code that nobody is looking at and nobody will suspect. Add tags.
Never move one.

1. Make the change under `src/scriptkit/`, with tests in `tests/`.

2. Bump `__version__` in [`src/scriptkit/__init__.py`](src/scriptkit/__init__.py).

   Do not go looking for a version in `pyproject.toml`. There isn't one. The
   field is declared `dynamic` and hatch reads `__version__` out of the package
   at build time, which is set up under `[tool.hatch.version]`. One number, one
   file, no chance of the two disagreeing.

3. Leave `pyproject.toml` alone unless you added or changed a dependency or an
   extra, in `[project.dependencies]` or `[project.optional-dependencies]`.
   Nothing else in there is per-release.

4. Write the `CHANGELOG.md` entry. Open a `## [vX.Y.Z]` heading, move the
   relevant lines down out of `## [Unreleased]`, and group them under `Added`,
   `Changed`, and `Fixed`.

5. Go green:

   ```powershell
   .\.venv313\Scripts\python.exe -m ruff check .
   .\.venv313\Scripts\python.exe -m pyright
   .\.venv313\Scripts\python.exe -m pytest -q
   ```

   The `ruff check` and `pytest (all versions)` VS Code tasks do the same with
   fewer keystrokes.

6. Commit, tag, push:

   ```powershell
   git commit -am "Release vX.Y.Z: <summary>"
   git tag vX.Y.Z
   git push origin main --tags
   ```

7. Move the defaults onto the new tag. Three places hold one:
   `src/scriptkit/templates/script_template.py`, each script repo's
   `new-script.ps1` and the `-Tag` default in its `setup-venvs.ps1`, and the
   READMEs, this one included.

   Scripts already out there keep their old pin, which is the entire point.
   Bump a script's header when you want its new behavior and not before.

8. Confirm CI is green, and that one `uv run` against a real script resolves the
   new tag from a cold cache. A tag that GitHub has but `uv` cannot resolve is a
   failure you want to find now.

### What the library is allowed to become

Three constraints, and they are the reason step 1 is short.

Standard library only. Anything heavier hides behind an optional extra the way
`[rich]` and `[azure]` do, and never lands in the base install. A script that
pulls a dependency tree to print a timestamp is worse than no library.

Every public API has a test, and CI is green before a tag exists. Consumers pin
tags, so a broken tag is permanent.

Anything printed stays ASCII-safe. A legacy Windows console will render the rest
as garbage, and it will do it in the log file you are reading six months later to
work out what went wrong.


## Working on scriptkit

You only need any of this to edit the library itself. Consuming scripts need
`uv run` and nothing else.

Install [uv](https://docs.astral.sh/uv/):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Then build the dev virtualenvs. There is one per supported Python minor version,
each an editable `.[dev]` install, so ruff, pyright, and pytest come with them:

```powershell
.\setup-venvs.ps1            # builds .venv311 / .venv312 / .venv313
.\setup-venvs.ps1 -Force     # delete and recreate them
```

VS Code points at `.venv313` for IntelliSense, linting, and debugging. Switch
with *Python: Select Interpreter*, or use the versioned debug configs. Every
command below also exists as a task under **Terminal > Run Task**.

### Lint and format

Ruff is configured in [`pyproject.toml`](pyproject.toml) under `[tool.ruff]`:
line length, a pinned rule set, and `src/scriptkit/templates/` excluded, because
the templates are not this project's code and should not be held to its lint
config. Lint results do not depend on which interpreter runs them, so `.venv313`
is enough.

The plain check lives in the release checklist. The two variants worth having to
hand:

```powershell
.\.venv313\Scripts\python.exe -m ruff check --fix .    # apply the safe auto-fixes
.\.venv313\Scripts\python.exe -m ruff format .         # reformat in place
```

Tasks are `ruff check` and `ruff format`. Format-on-save is already on for Python
files, set in [.vscode/settings.json](.vscode/settings.json), so the format
command is mostly for files you touched outside the editor.

### Types

Pyright is in the `dev` extra and configured under `[tool.pyright]`. It checks
`src` against the 3.11 baseline and skips the bundled templates. The package
ships a `py.typed` marker, which means this gate guards the types your consumers
see in their editors, not only the ones you see in yours. That makes a type
regression a visible, breaking change rather than a private annoyance.

The command is in the release checklist.

### Tests

The suite is in `tests/`, one file per module, with `testpaths` set in
`pyproject.toml`. Single-version runs are in the release checklist. This is the
local stand-in for the CI matrix, and every public API passes on all three:

```powershell
.\.venv311\Scripts\python.exe -m pytest -q; .\.venv312\Scripts\python.exe -m pytest -q; .\.venv313\Scripts\python.exe -m pytest -q
```

CI runs `{ubuntu,windows}` against `{3.11,3.12,3.13}`, so the local matrix catches
version problems but not platform ones. Tasks: `pytest (3.13)` is the default test
task, with `pytest (3.11/3.12)` and `pytest (all versions)` alongside it. The VS
Code Testing beaker works too.

### Scaffolding for local work

`new-module.ps1` copies `module_template.py` and `new-test.ps1` copies
`test_template.py`. Both have `.bat` launchers for double-clicking. These do the
same job as `scriptkit new` without needing the console entry point on PATH.

### Layout

```
py-scriptkit/
├── src/scriptkit/          the package (import name = scriptkit)
│   ├── __init__.py         public API + __version__ (single source of truth)
│   ├── settings.py         ScriptSettings, build_parser_from_settings, parse_settings
│   ├── logging.py          get_logger / set_log_level (RichLogger or stdlib shim)
│   ├── times.py            timestamp()
│   ├── azure.py            lazy DefaultAzureCredential helper
│   ├── cli.py              `scriptkit new`, scaffolds a module (console entry point)
│   ├── py.typed            PEP 561 marker, ships inline types to consumers
│   └── templates/          the source of truth all repos scaffold from
│       ├── script_template.py   single-file script (PEP 723 header, pinned)
│       ├── module_template.py   importable module (no pin, it imports scriptkit)
│       └── test_template.py     pytest file for a module
├── tests/                  pytest suite, one file per module
├── .github/workflows/      ruff + pyright + pytest on {ubuntu,windows} × {3.11,3.12,3.13}
├── .vscode/                run / debug / test config
├── new-module.ps1 / .bat   local dev scaffolder, copies module_template.py
├── new-test.ps1 / .bat     local dev scaffolder, copies test_template.py
├── setup-venvs.ps1 / .bat  builds the per-version dev venvs
├── pyproject.toml          package metadata (version is dynamic, read from __init__)
├── CHANGELOG.md            per-release notes, keyed by git tag
├── ROADMAP.md              phased action plan across the three repos
├── IDEAS.md                post-v1.0.0 brainstorm, not committed work
└── CLAUDE.md               session handoff for Claude Code
```

`src/scriptkit/` is the ordinary src layout. The `src/` directory keeps the
package off the repo root, so an import cannot accidentally resolve against the
working tree and the tests are forced to exercise the installed copy, which is
what a consumer gets. The `scriptkit/` directory inside it is the package, and its
name is the import name.
