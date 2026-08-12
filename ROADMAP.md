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

ONCE 6 COMPLETE, we can start adding scripts in a major release for
v1.0.0+

(Phase 7 — editor run-button synced to `uv run` — is complete: each script
repo's `.vscode` runs the open file through `uv run --exact` via the default
build task / F5, plus a status-bar button from the VSCode Task Buttons
extension.)
