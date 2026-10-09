---
name: create-requirement
description: >-
  Break down a feature description into SMART requirements with measurable acceptance criteria and write them to modular chapter files in docs/specifications/.
---

# Skill: Create Requirement

Break down a feature into formal requirements meeting quality and traceability standards in modular chapter files.

## Files Modified

- `docs/specifications/<chapter>.adoc`
- `specification-web.adoc` (if new chapter needs `include::` registration)

## Execution Steps

1. **Target Chapter**: Identify existing chapter file in `docs/specifications/` or create a new chapter file (e.g. `docs/specifications/02-combat.adoc`).
2. **Include Registration**: If a new chapter file is created, add `include::docs/specifications/<chapter>.adoc[]` to `specification-web.adoc`.
3. **SMART Criteria Check**:
   - **S**pecific: Unambiguously stated.
   - **M**easurable: Verifiable acceptance criteria.
   - **A**chievable: Implementable with current stack.
   - **R**elevant: Traceable to stakeholder need or constraint.
   - **T**ime-bound: Effort estimate included.
4. **Draft Section**: In the chapter file, add the requirement section:
   - Unique anchor (e.g., `[#FR-2.1]`)
   - Title
   - Description
   - Acceptance criteria (numbered with verifiable conditions)
   - Stakeholder need / constraint link
5. **Verify**: Run `npm run validate:specs`.
