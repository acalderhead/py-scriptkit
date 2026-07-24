# py-scriptkit

Stdlib-first toolkit for single-file Python scripts — dataclass config with CLI+env wiring, semantic logging with a rich fallback, and small utilities. Consumed via versioned git tags.

> **Repo `py-scriptkit`, package `scriptkit`.** The repository is named
> `py-scriptkit`; the importable package is `scriptkit` (`import scriptkit`).
> This is the **source of truth** — the library and the script template. Actual
> scripts live in [`py-scripts`](https://github.com/acalderhead/py-scripts)
> (personal) and [`py-cenvar-scripts`](https://github.com/acalderhead/py-cenvar-scripts) (work).

## What's here

```
py-scriptkit/
├─ src/scriptkit/       the library (importable, SemVer-tagged)
│  ├─ settings.py       ScriptSettings + auto CLI/env parser (CLI > env > default)
│  ├─ logging.py        RichLogger, with a semantic-aware stdlib fallback
│  ├─ times.py          timestamp()
│  └─ azure.py          lazy DefaultAzureCredential seam
├─ templates/
│  └─ script_template.py   the canonical thin template (PEP 723 header)
├─ tests/               pytest suite for scriptkit
└─ .github/workflows/   ruff + pytest on 3.11 / 3.12
```

## Using it from a script

Scripts don't clone this repo — they pin a released tag in their PEP 723 header
and run with [uv](https://docs.astral.sh/uv/):

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@v0.1.0",
# ]
# ///
from scriptkit import ScriptSettings, get_logger, parse_settings
```

For decorated console logging, use the `rich` extra:

```
scriptkit[rich] @ git+https://github.com/acalderhead/py-scriptkit.git@v0.1.0
```

Because each script names its own tag, a script written today keeps running
unchanged after the library moves on. Bump a script's pin only when you *want*
its improvements.

## Developing the library

```powershell
uv venv
uv pip install -e ".[dev]"
ruff check .
pytest -q
```

## Releasing a new version

1. Edit `src/scriptkit/`.
2. Bump `__version__` in `src/scriptkit/__init__.py`.
3. Add a `CHANGELOG.md` entry.
4. Tag and push:

   ```powershell
   git tag v0.2.0
   git push origin main --tags
   ```

Scripts keep pointing at whatever tag they named until you bump them.
