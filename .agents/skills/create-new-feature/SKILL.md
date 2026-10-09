---
name: create-new-feature
description: >-
  Break down a new feature into requirements, technical specifications, and backlog user stories satisfying SMART criteria and reference traceability using modular chapter files.
---

# Skill: Create New Feature

Decompose a feature request into specification artifacts across modular chapter files.

## Files Modified

- `docs/specifications/<feature-chapter>.adoc` & `specification-web.adoc`
- `docs/tech-specifications/<feature-chapter>.adoc` & `tech-specification-web.adoc`
- `docs/backlog/<feature-chapter>.adoc` & `backlog-web.adoc`

## Execution Steps

1. **Chapter Identification**: Determine or create the feature chapter filename (e.g. `docs/specifications/02-dungeon-generator.adoc`).
2. **Requirements Definition**: Split the feature into atomic requirements using [create-requirement](../create-requirement/SKILL.md) in the feature's specification chapter file. Ensure the chapter is included in `specification-web.adoc`.
3. **Technical Architecture**: Map requirements to technical specifications (architecture, data models, interfaces) using [create-tech-specification](../create-tech-specification/SKILL.md) in `docs/tech-specifications/<feature-chapter>.adoc`. Ensure the chapter is included in `tech-specification-web.adoc`.
4. **Backlog Stories**: Break down the technical specification into implementable user stories with test criteria using [create-user-story](../create-user-story/SKILL.md) in `docs/backlog/<feature-chapter>.adoc`. Ensure the chapter is included in `backlog-web.adoc`.
5. **Traceability Verification**: Run `npm run validate:specs` to verify all anchors (`FR-x.y`, `TS-x.y`, `US-x.y`) and `include::` directives are valid.
