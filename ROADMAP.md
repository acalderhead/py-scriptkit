# Roadmap / Action Plan

Remaining action items before the major **v1.0.0** release. Phase numbers are
retained from the original plan and are intentionally non-sequential.

---

## PHASE 2: Richer auto-CLI types

- Release: Minor
- Scope:
  - Extend `build_parser_from_settings` to handle `Optional[...]`, `list[...]`
    (nargs), and `Enum` (choices)
  - Determine if other types should be included

---

## PHASE 5: Custom formatting rules

- Release: Minor
- Scope:
  - Get Python formatting rules document
  - Determine Ruff vs personal formatting
  - Configure for Ruff
  - [OPTIONAL] Create an auto-formatter in VS Code

---

## PHASE 6: Update templates

- Release: Minor
- Scope:
  - For py-scriptkit, update the template based on my style
  - For others, add new styled/appropriate templates
  - DO NOT update example files since these will soon be replaced

---

ONCE 2, 5, 6 COMPLETE, we can start adding scripts in a major release for
v1.0.0+
