---
name: update-feature
description: >-
  Perform impact analysis on a feature change and update modular specification chapters across docs/ while preserving reference traceability.
---

# Skill: Update Feature

Update existing feature artifacts through end-to-end impact analysis across modular chapter files.

## Files Modified

- `docs/specifications/<chapter>.adoc`
- `docs/tech-specifications/<chapter>.adoc`
- `docs/backlog/<chapter>.adoc`

## Execution Steps

1. **Targeted Reading**: Read only the relevant feature chapter files (e.g. `docs/specifications/01-core-shell.adoc`, `docs/tech-specifications/01-core-shell.adoc`, `docs/backlog/01-core-shell.adoc`) rather than the whole suite.
2. **Requirement Updates**: Apply [update-requirement](../update-requirement/SKILL.md) to modify requirements in the specification chapter file.
3. **Tech Spec Updates**: Update architecture, data models, or interface definitions in the tech-specification chapter file.
4. **Backlog Updates**: Update user stories, acceptance criteria, and test pyramid criteria in the backlog chapter file using [update-user-story](../update-user-story/SKILL.md).
5. **Traceability & Validation**: Run `npm run validate:specs` to verify cross-references.
