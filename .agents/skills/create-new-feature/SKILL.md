---
name: create-new-feature
description: >-
  Break down a new feature into requirements, technical specifications, and backlog user stories satisfying SMART criteria and reference traceability using modular item files.
---

# Skill: Create New Feature

Decompose a feature request into specification artifacts across modular item files, following [spec-system](../spec-system/SKILL.md) (masters and folders under Layout).

## Files Modified

- `specification/requirements/<NN-feature>/` (`index.adoc` + item files) & the requirements master
- `specification/tech-specification/<NN-feature>/` (`index.adoc` + item files) & the technical specification master
- `specification/backlog/<NN-feature>/` (`index.adoc` + item files) & the backlog master

## Execution Steps

1. **Chapter Identification**: Determine or create the feature chapter folder name (e.g. `05-dungeon-generator`), used under all three kinds.
2. **Requirements Definition**: Split the feature into atomic requirements using [create-requirement](../create-requirement/SKILL.md) in `specification/requirements/<NN-feature>/`. Ensure the chapter index is included in the requirements master.
3. **Technical Architecture**: Map requirements to technical specifications (architecture, data models, interfaces) using [create-tech-specification](../create-tech-specification/SKILL.md) in `specification/tech-specification/<NN-feature>/`. Ensure the chapter index is included in the technical specification master.
4. **Backlog Stories**: Break down the technical specification into implementable user stories with test criteria using [create-user-story](../create-user-story/SKILL.md) in `specification/backlog/<NN-feature>/`. Ensure the chapter index is included in the backlog master.
5. **Traceability Verification**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)) to verify all anchors (`FR-x.y`, `TS-x.y`, `US-x.y`) and `include::` directives are valid.
