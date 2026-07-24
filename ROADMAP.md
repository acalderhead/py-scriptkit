# Roadmap / Action Plan

Working plan for the three-repo Python system
(`py-scriptkit` = library + template; `py-scripts` = personal;
`py-cenvar-scripts` = work). This file is the pick-up point between work
sessions — update it as phases complete.

## Baseline

- **Current release:** `scriptkit v0.2.1` (committed + tagged locally; push pending).
- **Consumers pin:** `scriptkit @ git+https://github.com/acalderhead/py-scriptkit.git@vX.Y.Z`.
- **Toolchain:** Python 3.11+; uv; ruff; pytest. CI on GitHub Actions (Ubuntu).

## Guardrails (avoid scope drift)

1. **One theme per release.** Each phase below maps to at most one version bump.
2. **Green before tag:** `ruff check .` + `pytest -q` pass on all CI targets.
3. **SemVer, and tags are immutable** — never move a published tag; only add new ones.
4. **Library changes → version bump + CHANGELOG entry.** Docs/CI-only changes don't bump.
5. **Blocked items wait for their listed input** rather than being guessed.

---

## Phase 0 — Confirm the baseline  ·  Owner: YOU  ·  no release

Covers action item **(1) Test VS Code compatibility**.

**Do first:** push `v0.2.1`.
```powershell
cd C:\Users\a.calderhead_stegose\repos\py-scriptkit; git push origin main --tags
cd ..\py-scripts;        git push origin main
cd ..\py-cenvar-scripts; git push origin main
```

**Then run the VS Code checklist** (in `py-scripts`):

| Check | How | Pass |
| --- | --- | --- |
| Interpreter | Cmd Palette → *Python: Select Interpreter* → `.venv` | no red squiggle on `from scriptkit import ...` |
| Run | open `scripts/example_hello.py` → **Ctrl+Shift+B** | greets in terminal |
| Run w/ args | Run Task → "uv run: current file (with args)" → `--name Aidan --times 2` | greets twice |
| Debug | breakpoint in `main()` → **F5** | stops at breakpoint |
| Tests | Testing beaker → run | `test_example_hello` passes (2) |
| Lint/format | edit + save a script | Ruff formats on save; Problems clean |

Note: Run tasks use `uv run` (need `v0.2.1` pushed + repo public). Debug/Tests use
the local `.venv` and work offline. **Report any failures before Phase 1.**

---

## Phase 1 — Standardize READMEs  ·  Owner: ME  ·  no release

Covers action item **(2)**. Rewrite all three READMEs to a shared four-section
template. Recommended order (leads with what-it-is, then how):

1. **Description** — what the repo is, in 2–3 lines.
2. **One-Time Setup** — install uv; create/select the dev `.venv`.
3. **File Architecture** — the directory tree with one-line annotations.
4. **Maintenance Instructions** — repo-specific upkeep: for `py-scriptkit`, the
   release playbook + rules; for the script repos, the daily loop + "shared logic
   goes to scriptkit."

Decision: keep this exact section set and order across all three for consistency
(script repos will have short Description/Setup, richer Architecture/Maintenance).

Test (YOU): skim each README top-to-bottom; confirm the four sections read cleanly.

---

## Phase 2 — Catch bugs before release (CI hardening)  ·  Owner: ME  ·  → v0.2.2

Covers **(3a) Windows runner**, **(3b) type check**, and **(5) Python 3.13/3.14**.

- **CI matrix:** add `windows-latest` alongside `ubuntu-latest`, and expand Python
  to **3.11, 3.12, 3.13, 3.14**. *(Answer to item 5: yes — 3.13 and 3.14 are both
  released/stable as of now; minimum supported stays 3.11.)*
- **Type checking:** add `pyright` (fast, no config) to dev deps + a CI step; ship a
  `py.typed` marker in `src/scriptkit/` so consumer scripts get type info.
- Fix whatever the Windows job / type check surfaces (this is the point).

Why v0.2.2: `py.typed` changes the distributed package, so it warrants a bump.
If type checking surfaces many fixes, they still ship together as v0.2.2.

Test (YOU): after I push, confirm all CI jobs (now Win+Ubuntu × 3.11–3.14) are green,
then re-run the Phase 0 VS Code checklist.

Payoff: the two bug classes already hit (Windows path/encoding) get caught in CI, not by you.

---

## Phase 3 — Pre-release formatting  ·  Owner: ME  ·  BLOCKED on your input

Covers **(4) custom formatting rules (non-PEP)**.

Context/limits you should know:
- `ruff check` (lint) is highly configurable — rule selection, isort, many checks.
- `ruff format` (the formatter) is Black-style and only mildly configurable
  (line length, quote style, indent, magic trailing comma, line endings). It
  **cannot** express arbitrary custom layout (e.g. aligned assignments, bespoke
  comment banners).

**INPUT NEEDED (blocker):** share your custom formatting rules — the actual config
file, or a written list. With them I can determine what maps to ruff (lint/format)
vs what needs a different approach, then wire a **pre-release format+check step**
(and optionally a pre-commit hook). Until I see the rules I can't scope this.

Likely outcome: a shared `ruff.toml`/format config in `py-scriptkit`, referenced by
all repos, plus a documented "format before release" step. Release only if it
changes shipped library code; otherwise tooling-only (no bump).

---

## Phase 4 — Richer auto-CLI types  ·  Owner: ME  ·  → v0.3.0

Covers **(3c)**. Extend `build_parser_from_settings` to handle field types it
currently skips: `Optional[...]`, `list[...]` (nargs), and `Enum` (choices).

Why v0.3.0: new backward-compatible capability (minor bump).

Test (YOU): scaffold a script with a `list[str]` and an `Enum` field; confirm
`--flag a b c` and choice validation work, and `--help` shows the choices.

---

## Phase 5 — RichLogger integration  ·  Owner: ME  ·  NEEDS CLARIFICATION  ·  → v0.3.x

Covers **(6) Integrate RichLogger; update commands**.

Current state: `scriptkit.logging.get_logger` already uses `rich_logger.RichLogger`
when the `[rich]` extra is installed, and falls back to a stdlib shim otherwise.

**QUESTIONS to resolve before this phase:**
- What does "integrate" mean here — (a) make `[rich]` the default so scripts get
  decorated logs out of the box, (b) bundle it as a non-optional dependency, or
  (c) just verify/document it works end-to-end?
- "Update commands": does this mean align the semantic method names
  (`stage/step/metric/...`) with RichLogger's **current** API, or update the
  install/usage commands in docs? Please point me at RichLogger's current version
  tag + method list (or the repo) so the shim stays in sync.

Test (YOU, once scoped): install a script with `scriptkit[rich]` and confirm
decorated output; confirm the stdlib fallback still matches method-for-method.

---

## Phase 6 — Cross-platform scaffolder  ·  Owner: ME  ·  → v0.4.0

Covers **(7)**. Replace the per-repo `new-script.ps1` (Windows-only, duplicated)
with a `scriptkit new <name>` **console entry point** shipped in the package, so
scaffolding works on any OS and lives in one place.

- Add `[project.scripts]` entry point; implement `scriptkit new NAME [--tag] [--dir]`.
- Invoke via `uvx --from "scriptkit @ git+...@vX.Y.Z" scriptkit new my_tool`
  (no local install needed), or from the dev `.venv`.
- Keep `new-script.ps1` for one release as a thin shim, then remove.

Why v0.4.0: new user-facing surface (entry point) in the package.

Test (YOU): run `scriptkit new demo` in a script repo; confirm it lands in
`scripts/demo.py`, pinned, clean (no mojibake), and runs.

---

## Recommended order

Phase 0 (you) → 1 → 2 → 4 → 6, with **3** slotting in as soon as you provide the
formatting rules, and **5** once its questions are answered. Phases 2, 4, 6 are the
version-bearing releases (v0.2.2, v0.3.0, v0.4.0).

## Open questions (blockers)

- **Phase 3:** your custom formatting rules (file or list).
- **Phase 5:** meaning of "integrate RichLogger" + which "commands"; RichLogger's
  current tag and method list.
