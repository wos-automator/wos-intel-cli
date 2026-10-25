---
name: create-new-feature
description: >-
  Break down a new feature into requirements, technical specifications, and backlog user stories satisfying SMART criteria and reference traceability using modular item files, level by level with a review by the user between the levels.
---

# Skill: Create New Feature

Decompose a feature request into specification artifacts across modular item files, following [spec-system](../spec-system/SKILL.md) (masters and folders under Layout, the levels under Levels and Allocation).

## Reads

- The stakeholder input of the feature (its `SPEC.md` section)
- Per level, only what that level's skill names under Reads

## Files Modified

- `specification/requirements/<NN-feature>/` (`index.adoc` + item files) & the requirements master
- `specification/acceptance/<NN-feature>/` (feature files; BDT only)
- The architecture overview (only with one, and only where the feature does not fit it)
- `specification/tech-specification/<NN-feature>/` (`index.adoc` + item files) & the technical specification master
- `specification/backlog/<NN-feature>/` (`index.adoc` + item files) & the backlog master

## Review Gates

After each level, report the new items to the user: IDs, titles, open questions, and what the stakeholder input proposes rather than requires. Stop there if the user asked for that level only (e.g. "create the requirements and let me review them") or asked to review each level; continue with the next level only after the user approved. Without such a request, go through all levels and report once at the end.

## Execution Steps

1. **Chapter Identification**: Determine or create the feature chapter folder name (e.g. `05-dungeon-generator`), used under all kinds.
2. **Requirements**: Split the feature into atomic requirements using [create-requirement](../create-requirement/SKILL.md) in `specification/requirements/<NN-feature>/`. Ensure the chapter index is included in the requirements master.
3. **Acceptance Scenarios**: If `AGENTS.md` names requirements-based blackbox testing (BDT), write the scenarios of the new requirements with [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md) in `specification/acceptance/<NN-feature>/`. *Review gate: requirements and scenarios.*
4. **Architecture Check**: If `AGENTS.md` names the architecture overview, map the new requirements to the logical functions with [update-architecture](../update-architecture/SKILL.md); a feature that needs a new function, principle or building block changes the architecture first. *Review gate, if the architecture changed.*
5. **Technical Specification**: Map requirements to technical specifications using [create-tech-specification](../create-tech-specification/SKILL.md) in `specification/tech-specification/<NN-feature>/`. Ensure the chapter index is included in the technical specification master. *Review gate.*
6. **Backlog Stories**: Break down the technical specification into implementable user stories with test criteria using [create-user-story](../create-user-story/SKILL.md) in `specification/backlog/<NN-feature>/`; their blackbox test criteria name the scenarios. Ensure the chapter index is included in the backlog master. *Review gate.*
7. **Traceability Verification**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)) to verify all anchors (`FR-x.y`, `TS-x.y`, `US-x.y`) and `include::` directives are valid.
