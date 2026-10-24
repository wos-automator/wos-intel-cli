---
name: create-user-story
description: >-
  Break down a technical specification into atomic, SMART user stories with Acceptance Criteria and Test Pyramid levels in modular item files in specification/backlog/<chapter>/.
---

# Skill: Create User Story

Create implementable, atomic user stories with structured test pyramid criteria in modular item files. Layout, anchors, SMART criteria and test pyramid levels are defined in [spec-system](../spec-system/SKILL.md).

## Files Modified

- `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc` (one new file per story)
- `specification/backlog/<NN-chapter>/index.adoc` (`include::` line for the new item)
- The backlog master (see [spec-system](../spec-system/SKILL.md), Layout), if a new chapter needs `include::` registration

## Execution Steps

1. **Target Chapter**: Locate the existing chapter folder in `specification/backlog/` or create a new one (e.g. `specification/backlog/02-combat/`) with an `index.adoc` holding the `==` heading.
2. **Include Registration**: Create the item file `<ID>-<slug>.adoc` (e.g. `US-2.1-attack-order.adoc`) and add `include::<ID>-<slug>.adoc[]` to the chapter `index.adoc`. For a new chapter, add `include::specification/backlog/<NN-chapter>/index.adoc[]` to the backlog master.
3. **SMART Story Format**, after the user story template of [spec-system](../spec-system/SKILL.md):
   - Story Anchor (e.g., `[[US-2.1]]`)
   - Effort estimate (`Effort::`)
   - Traceability Links: Reference Tech Spec (`<<TS-2.1>>`) and Requirement (`<<FR-2.1>>`).
   - Narrative: *As a... I want to... So that...*
   - Acceptance Criteria (numbered, testable).
   - Technical Tasks (numbered implementation steps).
4. **Test Criteria Definition**: Answer for every level of the test pyramid:
   - Unit: which functions, validators and services need tests?
   - Component: which modules or rendered components, and which interactions?
   - Integration: which persistence or cross-module flows?
   - Blackbox: is a critical user journey affected?

   Name what each test must show, specific enough to implement without ambiguity; a level that does not apply says why. Name the tooling from the component's toolchain profile and respect the project's limits in `AGENTS.md`.
5. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
