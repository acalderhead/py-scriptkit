# Roadmap / Action Plan

Remaining action items before the major **v1.0.0** release. Phase numbers are
retained from the original plan and are intentionally non-sequential.

---

## PHASE 6: Update templates

- Release: Minor
- Scope:
  - py-scriptkit templates are complete (module + test templates).
  - Only py-scripts and py-scripts-cenvar still need their templates updated to
    match the new style.
  - DO NOT update example files since these will soon be replaced

---

## PHASE 7: Editor run-button -> uv run

- Release: Minor
- Scope:
  - Wire the editor's run/execute button (the terminal ▶) to `uv run` so a
    script runs with its PEP 723 pins (installing scriptkit) instead of the
    plain interpreter, which fails with ModuleNotFoundError.
  - Likely a per-repo `.vscode` task / launch config (and/or a terminal
    profile) that routes the run button through `uv run`.

---

ONCE 6, 7 COMPLETE, we can start adding scripts in a major release for
v1.0.0+
