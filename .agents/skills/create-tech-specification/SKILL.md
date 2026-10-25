---
name: create-tech-specification
description: >-
  Break down a requirement into technical specifications (architecture, data models, component interactions, interface definitions) in modular item files in specification/tech-specification/<chapter>/.
---

# Skill: Create Technical Specification

Map functional and non-functional requirements to the design of their part, within the architecture, in modular item files. Layout, anchors, levels and traceability are defined in [spec-system](../spec-system/SKILL.md).

## Reads

- The requirement items to implement and their acceptance scenarios (BDT)
- With an architecture overview: the function and building block the requirements are allocated to, the principles of the Solution Strategy and the decisions and concepts they name; not the whole overview
- The code of the building block, and the existing technical specifications of the target chapter

## Files Modified

- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc` (one new file per specification)
- `specification/tech-specification/<NN-chapter>/index.adoc` (`include::` line for the new item)
- The technical specification master (see [spec-system](../spec-system/SKILL.md), Layout), if a new chapter needs `include::` registration

## Execution Steps

1. **Target Chapter**: Locate the existing chapter folder in `specification/tech-specification/` or create a new one (e.g. `specification/tech-specification/02-combat/`) with an `index.adoc` holding the `==` heading.
2. **Include Registration**: Create the item file `<ID>-<slug>.adoc` (e.g. `TS-2.1-attack-planner.adoc`) and add `include::<ID>-<slug>.adoc[]` to the chapter `index.adoc`. For a new chapter, add `include::specification/tech-specification/<NN-chapter>/index.adoc[]` to the technical specification master.
3. **Requirement Mapping**: Reference originating requirement anchor (e.g., `<<FR-2.1>>`).
4. **Architecture**: If `AGENTS.md` names the architecture overview, the requirements must have passed [update-architecture](../update-architecture/SKILL.md). Name the function and building block the item realises and follow the principles, decisions and concepts that apply. A design that needs a new building block, pattern or choice goes back to [update-architecture](../update-architecture/SKILL.md) first.
5. **Specification Breakdown**:
   - Component breakdown within the building block
   - State and data schemas
   - Interface definitions and contracts
   - Component interactions / sequence
   - Settings: the configuration keys the design uses, never their values (Levels and Allocation)
   - Tests: where no acceptance scenario checks a requirement, the tests that do, with their reference material
6. **Draft Section**: Write the specification section into the item file with unique anchor (e.g. `[[TS-2.1]]`), after the template of [spec-system](../spec-system/SKILL.md).
7. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
