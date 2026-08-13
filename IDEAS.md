# Ideas

Nothing here is committed. It is a parking lot for directions worth considering
after v1.0.0, so the ROADMAP can stay a list of actual plans. An entry graduates
to ROADMAP.md when it turns into one; until then it stays a line or two.

## Pin hygiene

The same scriptkit version is written by hand in a dozen places and they drift.
Right before 1.0, the tree had `v0.5.0`, `v0.5.3`, `v0.4.0`, and `v0.2.4` all live
while `__version__` said `0.5.4`.

- A pytest that greps the tree and fails when any hand-written `@vX.Y.Z` pin
  disagrees with `__version__`. Cheapest possible fix, would have caught every
  one of those. Nothing blocking it.
- A one-command pin bump that rewrites every reference (the template, the two
  docstrings that carry a pin, both script repos' `-Tag` defaults, the READMEs)
  from `__version__`. Wants the grep test first, so it has something to check its
  own work against.
- Stop shipping a literal pin in `script_template.py` at all. Put a
  `@__SCRIPTKIT_TAG__` placeholder in the header and have whatever writes the
  file substitute `v{__version__}`. That deletes the largest drift surface
  instead of policing it, but every scaffolder has to do the substitution, so it
  wants the CLI to own script scaffolding first.
- A CI job on tag push that fails when the tag does not equal `__version__`.
  Catches the one mistake that cannot be undone, since the tag is already public
  by the time anyone notices.

## Cross-platform scaffolding

Scaffolding is split. `scriptkit new` (module) is cross-platform, but scripts and
tests are scaffolded only by Windows `.ps1`/`.bat`, so a macOS or Linux user
cannot scaffold either.

- Fold scripts and tests into the CLI (`scriptkit new --kind script|module|test`).
  The templates already ship in the package, so no checkout or raw-fetch is
  needed. This also retires the `.ps1` duplication and most of the pin-drift
  surface. Blocked only by wanting the CLI stable first.
- If that is too big, ship `.sh` companions to the `.ps1` scaffolders.
- `setup-venvs.ps1` is the other Windows-only file, and it hardcodes
  `Scripts\python.exe`. A dev on Linux cannot build the venvs the README tells
  them to build. Smaller than the scaffolder problem and independent of it.
- The interactive flow in `new-test.ps1` (list the source files, pick a number,
  re-prompt on collision) is the nicest thing in the repo and the CLI has no
  equivalent. Whatever replaces the `.ps1` files should keep it, or the
  cross-platform version is a downgrade for the person who actually uses it.

## Settings sources and types

- A config-file layer in the precedence chain (CLI > env > file > default) for
  scripts with many knobs. Nobody has needed it yet, which is the only reason it
  is here and not in the roadmap.
- Mark a field secret so its value is masked in `--help` and in `config` log
  lines. Small, pairs with the secrets guidance already in `azure.py`.
- `dict` and `tuple` fields, and nested generics like `list[list[X]]`, are
  skipped by the parser today. Add them when a real script needs one, not before.
- `ENV_PREFIX` is a module constant, so every scriptkit script on a machine reads
  the same `APP_*` namespace. `APP_DIR_BASE` set for one script silently
  relocates all of them. Let a subclass declare its own prefix
  (`env_prefix = "RECON_"`) and fall back to `APP_` when it does not.
- `parse_settings` calls `parser.parse_args()` with no argv, so it can only be
  driven by `sys.argv`. `cli.main` already takes `argv` and is testable because
  of it. Adding the same parameter costs one line and gives every consuming
  script a way to test its own settings.
- `--print-config`: resolve everything, print each field with the value and where
  it came from (CLI, env, or default), exit 0. The precedence is the part people
  get wrong, and today the only way to see it is to read the source.
- Constructing a `Settings` creates a directory. `__post_init__` calls
  `dir_output.mkdir`, so building one in a test, or in a `--print-config` path,
  writes to disk as a side effect. Either move it to an explicit
  `settings.ensure_dirs()` that `main` calls, or accept it and say so in the
  docstring. The current behavior is a surprise either way.
- A `validate()` hook called at the end of `__post_init__`, so a bad combination
  of otherwise-valid flags dies at startup with one line instead of a traceback
  from the middle of the run.
- Short flags and other per-field knobs through the `metadata` dict that already
  carries `help`: `field(metadata = {"help": ..., "short": "-n"})`. The metadata
  channel exists and `help` is the only key using it.

## Logging

- Optional file sink beside the output dir, off by default.
- A JSON formatter for the stdlib fallback. It already targets CI and Azure
  Monitor; JSON parses cleaner there than the ` | ` columns.
- A test that both backends expose the same semantic method set. The shim
  re-implements RichLogger's vocabulary by hand, so it will drift when
  rich_logger changes.
- `_configure_stdlib` calls `logging.basicConfig`, which is a no-op when the root
  logger already has handlers. A script (or a library it imported) that
  configured logging first gets none of the aligned format, silently. `force =
  True` fixes it and steals the root handler from whoever set it; doing nothing
  is defensible. What is not defensible is that neither behavior is written down.
- Timed stages: `with logger.stage("Load"):` that logs entry, exit, and duration.
  The vocabulary already names what a script is doing, and duration is the thing
  every run gets asked about afterward.
- `settings.log_config(logger)`, one call that emits every field at CONFIG level
  with secrets masked. Pairs with `--print-config` and the secret-field marker;
  all three want the same field walk.

## Script boilerplate

Every script carries the same twenty lines of main-guard: parse, set level, try,
catch, format the traceback, exit non-zero. It is in `script_template.py`, so it
is correct, and it is also copied into every script that will ever exist.

- `scriptkit.run(main, Settings)`: parse settings, apply the log level, log the
  resolved config, time the run, catch and log the traceback, return the exit
  code. Collapses the template's whole entry-point block to one line. The cost is
  that the flow stops being visible in the script, which for a single-file script
  someone else has to debug is a real cost, not a stylistic one. Worth prototyping
  against a real script before deciding.
- Record what actually ran. A script's `--version` prints the script's version;
  it does not say which scriptkit tag `uv` resolved. Append it (`1.0.0 (scriptkit
  0.5.4)`), and log the same line at startup. Scripts run on machines you cannot
  see, and "which version were you running" currently has two answers and no way
  to get either.
- The template's `dir_base` defaults to `~/_repo-output/<script-name>`;
  `ScriptSettings` defaults to `Path.cwd()`. Both are deliberate and the
  divergence is not written down anywhere the reader of one will find the other.

## Testing

- An autouse fixture in `tests/conftest.py` that clears the whole `APP_*`
  namespace. Every settings test currently calls `monkeypatch.delenv` per
  variable, and the failure mode of forgetting one is a test that passes on your
  machine and fails on someone whose shell has that variable set.
- A `scriptkit.testing` module for consumers: build a settings instance without
  touching `sys.argv` or the filesystem, and assert on semantic log calls. Nobody
  writing a script today has a way to test it that does not involve subprocess.
- Parse the fenced Python blocks out of README.md and `ast.parse` them in a test.
  The settings example in the README is the first thing anyone copies, and
  nothing checks that it still matches the parser.

## CI and release

- Lint and pyright run in all six matrix cells. The README already says lint
  results do not depend on the interpreter, and pyright is pinned to the 3.11
  baseline regardless of which Python runs it. Split them into one `lint` job and
  leave the matrix to pytest: five fewer redundant runs and a failure you can
  read at a glance.
- Nothing in CI ever installs `[rich]`, so the RichLogger path is untested on
  every platform and version. One extra cell installing `.[rich,dev]` covers it,
  and it is the same walk as the backend-parity test above.
- `astral-sh/setup-uv` runs without cache configuration. Turning caching on is a
  one-line change to six jobs that each resolve the same dependency set.
- Release-checklist step 8 (confirm one `uv run` resolves the new tag from a cold
  cache) is a job, not a manual step. Run it on tag push, in a container with no
  uv cache, against the actual published tag.
- Generate the GitHub release body from the matching CHANGELOG section on tag
  push. The text is already written by then.
- Protect the tag namespace on GitHub so a tag cannot be force-moved. The entire
  design rests on tags being immutable and nothing currently enforces it except
  the release checklist and good intentions.

## Distribution

Everything resolves over `git+https://…@tag`, scriptkit and rich_logger alike, so
every run, dev venv, and CI job needs git access to GitHub. Publishing to a
private index or attaching wheels to releases would let `uvx scriptkit` and
locked-down CI resolve without git. It is the largest item here and the least
urgent while everything runs on machines that have git.

- The cheap half of it: attach a built wheel to each GitHub release and point
  locked-down consumers at it with `--find-links`. No index to host, no
  credentials to distribute, and it removes the git requirement for the machines
  that actually have the problem. Does not help `uvx`, which still wants a
  resolvable name.

## Docs and house style

- The README's "Lint and format" section documents `ruff format .` as a command
  worth having to hand, and says format-on-save is on for Python files.
  `.vscode/settings.json` sets `editor.formatOnSave: false`, and CLAUDE.md and
  `pyproject.toml` both say never to run the formatter because it destroys the
  hand-aligned `=` columns. The docs currently recommend the one command the
  project forbids. Settle it and delete the loser.
- There is a `ruff format` task in `.vscode/tasks.json`, one keystroke from the
  `ruff check` task next to it, that will silently reformat the whole tree.
  Deleting it costs nothing.
- `.vscode/tasks.json` also carries an auto-detected `npm: build` task pointing
  into `.venv311/Lib/site-packages/pyright/dist`. It is noise from VS Code
  finding a `package.json` inside a venv, and it ships to everyone who clones.
- The house style (80-wide `# ─` dividers, ordered Constants / Public API /
  Internal Helpers, sectioned module docstrings) is enforced by attention alone.
  A pytest that checks the section headers exist and are in order would make it
  mechanical. So would a `.code-snippets` file, and that one also makes the style
  faster to follow instead of only harder to break.
- CLAUDE.md, the README, and this file each carry a copy of the current release
  number in prose. Three places, one fact, and the release checklist does not
  list two of them.

## Ergonomics

A `scriptkit doctor` that diagnoses the stale-cache and stale-venv problem the
READMEs spend so many words on, and prints the exact `--exact` or `-Force` to run.

- What it should check, once it exists: uv is installed and recent enough; git
  can reach GitHub; the three venvs exist and match the current `[dev]` pins; the
  pin in the file you point it at resolves, and whether it is behind
  `__version__`.
- `scriptkit pin <file>` to rewrite a script's PEP 723 header to a given tag, or
  to the latest release. Bumping a script by hand means editing a comment block
  correctly, and the failure is a script that resolves the wrong version quietly.
- `scriptkit check <file>` to validate a header before you commit it: the pin is
  a real tag, `requires-python` matches, the extras spelled in it exist.
