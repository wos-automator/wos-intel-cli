---
name: create-tech-specification
description: >-
  Break down a requirement into technical specifications (architecture, data models, component interactions, interface definitions) in modular chapter files in docs/tech-specifications/.
---

# Skill: Create Technical Specification

Map functional and non-functional requirements to technical architecture and schemas in modular chapter files.

## Files Modified

- `docs/tech-specifications/<chapter>.adoc`
- `tech-specification-web.adoc` (if new chapter needs `include::` registration)

## Execution Steps

1. **Target Chapter**: Locate existing chapter file in `docs/tech-specifications/` or create a new chapter file (e.g. `docs/tech-specifications/02-combat.adoc`).
2. **Include Registration**: If creating a new chapter file, add `include::docs/tech-specifications/<chapter>.adoc[]` to `tech-specification-web.adoc`.
3. **Requirement Mapping**: Reference originating requirement anchor (e.g., `<<FR-2.1>>`).
4. **Specification Breakdown**:
   - Architecture layer and component breakdown
   - State and data schemas
   - interface definitions and contracts
   - Component interactions / sequence
5. **Draft Section**: Write specification section with unique anchor (e.g. `[#TS-2.1]`).
6. **Verify**: Run `npm run validate:specs`.
