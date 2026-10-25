---
name: implement-user-story
description: >-
  Implement a user story from its specification/backlog/ item file following TDD, testing pyramid requirements, type-checking, linting, and Definition of Done.
---

# Skill: Implement User Story

Implement a backlog user story adhering to strict TDD and Definition of Done.

## Reads

- The story item and the technical specification items it traces to
- The concepts and decisions those name (architecture overview), not the whole overview
- The code of the building block and its tests

## Files Modified

- Source code files of the affected components
- Test files, in the layout of the existing tests
- `specification/release-notes/<version>.adoc`

## Execution Steps

1. **Context Gathering**: Read the story's item file `specification/backlog/<NN-chapter>/<US-ID>-<slug>.adoc` and the referenced tech spec item files `specification/tech-specification/<NN-chapter>/<TS-ID>-<slug>.adoc` (saving tokens by loading only the relevant items). A story that needs a design the technical specification does not hold goes back to [create-tech-specification](../create-tech-specification/SKILL.md) first; settings get their value in the configuration, not in the specification.
2. **Baseline Check**: Run the `check` task (see [toolchain](../toolchain/SKILL.md)) to ensure a green starting state.
3. **TDD Approach**: Write failing unit/component/integration tests matching the story's Test Criteria before writing implementation code.
4. **Implementation**: Write the minimal code necessary to pass all tests.
5. **Acceptance Scenarios**: If `AGENTS.md` names requirements-based blackbox testing (BDT), implement the step definitions the story's scenarios still miss and run the `bdt` task (see [toolchain](../toolchain/SKILL.md)) until they pass.
6. **Quality & DoD Verification**: Apply [definition-of-done](../definition-of-done/SKILL.md).
7. **Release Notes Update**: Update the target release version file in `specification/release-notes/<version>.adoc` with the new feature and trace back to requirements via story reference (`<<US-x.y>>`, `<<FR-x.y>>`).
8. **Commit**: Commit the story as one commit using [commit](../commit/SKILL.md) (type `feat`).
