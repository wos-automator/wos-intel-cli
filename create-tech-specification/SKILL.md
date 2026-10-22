---
name: create-tech-specification
description: >-
  Break down a requirement into technical specifications (architecture, data models, component interactions, interface definitions) in modular item files in specification/tech-specification/<chapter>/.
---

# Skill: Create Technical Specification

Map functional and non-functional requirements to technical architecture and schemas in modular item files. Layout, anchors and traceability are defined in [spec-system](../spec-system/SKILL.md).

## Files Modified

- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc` (one new file per specification)
- `specification/tech-specification/<NN-chapter>/index.adoc` (`include::` line for the new item)
- `tech-specification-web.adoc` (if a new chapter needs `include::` registration)

## Execution Steps

1. **Target Chapter**: Locate the existing chapter folder in `specification/tech-specification/` or create a new one (e.g. `specification/tech-specification/02-combat/`) with an `index.adoc` holding the `==` heading.
2. **Include Registration**: Create the item file `<ID>-<slug>.adoc` (e.g. `TS-2.1-attack-planner.adoc`) and add `include::<ID>-<slug>.adoc[]` to the chapter `index.adoc`. For a new chapter, add `include::specification/tech-specification/<NN-chapter>/index.adoc[]` to `tech-specification-web.adoc`.
3. **Requirement Mapping**: Reference originating requirement anchor (e.g., `<<FR-2.1>>`).
4. **Specification Breakdown**:
   - Architecture layer and component breakdown
   - State and data schemas
   - interface definitions and contracts
   - Component interactions / sequence
5. **Draft Section**: Write the specification section into the item file with unique anchor (e.g. `[[TS-2.1]]`).
6. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
