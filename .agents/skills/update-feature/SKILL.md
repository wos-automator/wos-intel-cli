---
name: update-feature
description: >-
  Perform impact analysis on a feature change and update modular specification item files across specification/ while preserving reference traceability.
---

# Skill: Update Feature

Update existing feature artifacts through end-to-end impact analysis across modular item files, following [spec-system](../spec-system/SKILL.md).

## Reads

- The changed stakeholder input
- The affected items only, level by level (see Targeted Reading)

## Files Modified

- `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc`
- The architecture overview (only with one, and only where the change reaches it)
- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc`
- `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc`
- New item files and chapter indexes, if the change adds scope

## Execution Steps

1. **Targeted Reading**: Read only the affected item files (e.g. `specification/requirements/01-core-shell/FR-1.2-*.adoc` and the TS/US items referencing it) rather than whole chapters or the whole suite; list a chapter folder to see its items.
2. **Requirement Updates**: Apply [update-requirement](../update-requirement/SKILL.md) to modify requirements in their item files. Report the impact (requirements, scenarios, architecture, technical specifications, stories) to the user; if the user asked to see it first, stop here and continue only after approval.
3. **Architecture Check**: If `AGENTS.md` names the architecture overview, check the changed requirements with [update-architecture](../update-architecture/SKILL.md) before the technical specifications change.
4. **Tech Spec Updates**: Update architecture, data models, or interface definitions in the affected tech-specification item files.
5. **Backlog Updates**: Update user stories, acceptance criteria, and test pyramid criteria in the affected backlog item files using [update-user-story](../update-user-story/SKILL.md).
6. **New Scope**: If the change adds scope that no existing item covers, create the new items with [create-requirement](../create-requirement/SKILL.md), [create-tech-specification](../create-tech-specification/SKILL.md) and [create-user-story](../create-user-story/SKILL.md) instead of stretching an existing item.
7. **Acceptance Scenarios**: If `AGENTS.md` names requirements-based blackbox testing (BDT), update the scenarios of the changed requirements with [update-acceptance-scenarios](../update-acceptance-scenarios/SKILL.md) and write those of new requirements with [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md).
8. **Traceability & Validation**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)) to verify cross-references.
