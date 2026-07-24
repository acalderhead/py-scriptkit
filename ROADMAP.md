# Roadmap / Action Plan

Working plan for the three-repo Python system
(`py-scriptkit` = library + template; `py-scripts` = personal;
`py-cenvar-scripts` = work). This file is the pick-up point between work
sessions — update it as phases complete.

## Baseline

- **Current release:** `scriptkit v0.2.1` (committed + tagged locally; push pending).
- **Consumers pin:** `scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@vX.Y.Z`.
- **Toolchain:** Python 3.11+; uv; ruff; pytest.
- **CI today:** GitHub Actions, **Ubuntu only, Python 3.11 + 3.12** (two jobs). This
  is why only "CI / 3.11" and "CI / 3.12" show up. 3.13/3.14 and Windows are added
  in Phase 2 — they are NOT tested yet.

## Guardrails (avoid scope drift)

1. **One theme per release.** Each phase maps to at most one version bump.
2. **Green before tag:** `ruff check .` + `pytest -q` pass on all CI targets.
3. **SemVer, and tags are immutable** — never move a published tag; only add new ones.
4. **Library changes → version bump + CHANGELOG entry.** Docs/CI-only changes don't bump.
5. **Blocked items wait for their listed input** rather than being guessed.

---

## Phase 0 — Confirm the baseline · Owner: YOU · no release

Covers **(item 1) VS Code compatibility**.

Push `v0.2.1` first:
```powershell
cd C:\Users\a.calderhead_stegose\repos\py-scriptkit; git push origin main --tags
cd ..\py-scripts;        git push origin main
cd ..\py-cenvar-scripts; git push origin main
```

Then run the VS Code checklist in `py-scripts`:

| Check | How | Pass |
| --- | --- | --- |
| Interpreter | Cmd Palette → *Python: Select Interpreter* → `.venv` | no red squiggle on `from scriptkit import ...` |
| Run | open `scripts/example_hello.py` → **Ctrl+Shift+B** | greets in terminal |
| Run w/ args | Run Task → "uv run: current file (with args)" → `--name Aidan --times 2` | greets twice |
| Debug | breakpoint in `main()` → **F5** | stops at breakpoint |
| Tests | Testing beaker → run | `test_example_hello` passes (2) |
| Lint/format | edit + save a script | Ruff formats on save; Problems clean |

Run tasks use `uv run` (need `v0.2.1` pushed + repo public); Debug/Tests use the
local `.venv` (offline OK). **Report failures before Phase 1.**

---

## Phase 1 — Standardize + expand READMEs · Owner: ME · no release

Covers **(item 2)**, **(item 4 → RichLogger install docs)**, and the run-methods note.

Shared section template for all three repos:

1. **Description** — what the repo is (2–3 lines).
2. **One-Time Setup** — install uv; create/select the dev `.venv`.
3. **File Architecture** — directory tree with one-line annotations.
4. **Running files** *(script repos)* — how to execute, **both ways**:
   - **PowerShell:** `uv run scripts/<name>.py [args]`
   - **VS Code:** Ctrl+Shift+B ("uv run: current file"); the "(with args)" task; F5 to debug.
   - Note which uses the pinned scriptkit (`uv run`) vs the local `.venv` (debug/tests).
5. **Maintenance Instructions** — a concrete **checklist** (see below). Assume the
   reader is new to versioning: spell out every detail, including when to touch
   `pyproject.toml`.

**RichLogger install note (in Setup/Running of the script repos):** to get decorated
logs, change the script's pin to add the `[rich]` extra —
`scriptkit[rich] @ git+https://github.com/acalderhead/py-scriptkit.git@vX.Y.Z` — then
`uv run` pulls RichLogger automatically; without it, scripts use the stdlib fallback.
*(Depends on `acalderhead/rich-logger` being public at its pinned tag — verified in Phase 4.)*

**`py-scriptkit` Maintenance = release checklist:**
1. Make the change under `src/scriptkit/` (+ tests).
2. Bump `__version__` in `src/scriptkit/__init__.py`. **Do NOT edit the version in
   `pyproject.toml`** — it reads `__version__` automatically (`dynamic = ["version"]`).
3. Only edit `pyproject.toml` if you **add/change dependencies or extras**
   (`[project.dependencies]` / `[project.optional-dependencies]`).
4. Add a `CHANGELOG.md` entry under a new `## [vX.Y.Z]` heading.
5. `ruff check .` and `pytest -q` green.
6. `git commit -am "Release vX.Y.Z: ..."` → `git tag vX.Y.Z` → `git push origin main --tags`.
7. To move scripts onto the new version, bump the pins (template, `new-script.ps1`
   default `-Tag`, READMEs, example). Existing scripts keep their old pin on purpose.
8. Confirm CI is green and one `uv run` works.

**Script-repo Maintenance:** the daily loop (`new-script.ps1` → edit → run → commit);
"shared logic goes into `scriptkit`, not copied here."

Test (YOU): skim each README; confirm the sections read cleanly and the release
checklist is followable start-to-finish.

---

## Phase 2 — Catch bugs before release (CI hardening) · Owner: ME · → v0.2.2

Covers **(3a) Windows runner**, **(3b) type check**, **(item 5) Python 3.13/3.14**.

- **Matrix:** add `windows-latest`; expand Python to **3.11, 3.12, 3.13, 3.14**
  (all released/stable; minimum supported stays 3.11). Result: 8 CI jobs.
- **Type checking:** add `pyright` to dev deps + a CI step; ship a `py.typed` marker
  in `src/scriptkit/` so consumer scripts get type info.
- Fix whatever the Windows/type-check jobs surface.

Why v0.2.2: `py.typed` changes the shipped package → warrants a bump.

Test (YOU): after push, confirm all 8 CI jobs green; re-run the Phase 0 checklist.

---

## Phase 3 — Richer auto-CLI types · Owner: ME · → v0.3.0

Covers **(3c)**. Extend `build_parser_from_settings` to handle `Optional[...]`,
`list[...]` (nargs), and `Enum` (choices) — currently skipped.

Test (YOU): scaffold a script with a `list[str]` and an `Enum` field; confirm
`--flag a b c`, choice validation, and `--help` choices all work.

---

## Phase 4 — RichLogger end-to-end · Owner: ME · NEEDS INPUT · → v0.3.x

Covers the rest of **(item 6) integrate RichLogger; update commands**.

Phase 1 documents *how to pull* rich. This phase makes sure it actually works:
- Verify `acalderhead/rich-logger` is **public** and the `[rich]` extra's pinned
  tag resolves via `uv`.
- Install a script with `scriptkit[rich]` and confirm decorated output; confirm the
  stdlib fallback matches RichLogger method-for-method.

**INPUT NEEDED:** (a) confirm what "integrate" should mean — keep `[rich]` opt-in
(current), or make it the default for scripts; (b) point me at RichLogger's current
tag + method list so the fallback shim stays in sync ("update commands").

Test (YOU): run a `[rich]`-pinned script; confirm colored/structured output.

---

## Phase 5 — Cross-platform scaffolder · Owner: ME · → v0.4.0

Covers **(item 7)**. Replace per-repo `new-script.ps1` (Windows-only, duplicated)
with a `scriptkit new <name>` **console entry point** in the package.

- Add `[project.scripts]`; implement `scriptkit new NAME [--tag] [--dir]`.
- Invoke via `uvx --from "scriptkit @ git+...@vX.Y.Z" scriptkit new my_tool`, or from
  the dev `.venv`. Keep `new-script.ps1` one release as a shim, then remove.

Test (YOU): `scriptkit new demo` in a script repo → lands in `scripts/demo.py`,
pinned, clean, runs.

---

## Phase 6 — Port existing utility scripts · Owner: YOU · (can start after Phase 0)

Covers **(item 5, new)**. Bring your current Python utilities into the system.

Triage each utility:
- **Standalone tool** → scaffold a script into `py-scripts` or `py-cenvar-scripts`
  (`new-script.ps1 <name>`), paste logic into `main()`, expose inputs as `Settings`
  fields, add its own PEP 723 deps.
- **Shared logic** (used by 2+ scripts, generic) → flag it for `scriptkit`; ME to
  integrate as a versioned release (own phase/bump). Don't copy shared code across scripts.

This runs on YOUR track in parallel; ping me when something should become a
`scriptkit` feature.

---

## Phase 7 — Custom formatting rules · Owner: ME · BLOCKED · deferred to LAST

Covers **(item 4)**. Moved to the end per your call (time-costly; the rules doc is
on another device).

Context/limits: `ruff check` (lint) is highly configurable; `ruff format` is
Black-style with only minor knobs and **can't** express arbitrary custom layout
(aligned assignments, custom banners). Scope depends entirely on your rules.

**INPUT NEEDED (when you're ready):** the custom-formatting doc. Then I'll map each
rule to ruff (lint/format) vs "not enforceable," wire a shared config + a
"format before release" step (and optionally a pre-commit hook), and document it.

---

## Recommended order

**Phase 0 (you)** → **1** (READMEs) → **2** (v0.2.2 CI) → **3** (v0.3.0 CLI) →
**4** (RichLogger, once its Qs are answered) → **5** (v0.4.0 scaffolder) →
**7** (formatting, last). **Phase 6 (your script porting)** runs in parallel any
time after Phase 0.

## Open questions (blockers)

- **Phase 4:** keep `[rich]` opt-in or make it default? RichLogger's current tag +
  method list. Is `acalderhead/rich-logger` public?
- **Phase 7:** your custom-formatting doc (from the other device).
