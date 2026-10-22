---
name: update-feature
description: >-
  Perform impact analysis on a feature change and update modular specification item files across specification/ while preserving reference traceability.
---

# Skill: Update Feature

Update existing feature artifacts through end-to-end impact analysis across modular item files, following [spec-system](../spec-system/SKILL.md).

## Files Modified

- `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc`
- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc`
- `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc`

## Execution Steps

1. **Targeted Reading**: Read only the affected item files (e.g. `specification/requirements/01-core-shell/FR-1.2-*.adoc` and the TS/US items referencing it) rather than whole chapters or the whole suite; list a chapter folder to see its items.
2. **Requirement Updates**: Apply [update-requirement](../update-requirement/SKILL.md) to modify requirements in their item files.
3. **Tech Spec Updates**: Update architecture, data models, or interface definitions in the affected tech-specification item files.
4. **Backlog Updates**: Update user stories, acceptance criteria, and test pyramid criteria in the affected backlog item files using [update-user-story](../update-user-story/SKILL.md).
5. **Traceability & Validation**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)) to verify cross-references.
