---
name: implement-user-story
description: >-
  Implement a user story from its specification/backlog/ item file following TDD, testing pyramid requirements, type-checking, linting, and Definition of Done.
---

# Skill: Implement User Story

Implement a backlog user story adhering to strict TDD and Definition of Done.

## Files Modified

- Source code files (`src/**`)
- Test files (`src/**/*.test.ts`, `src/**/*.test.tsx`, `e2e/**/*.spec.ts`)
- `specification/release-notes/<version>.adoc`

## Execution Steps

1. **Context Gathering**: Read the story's item file `specification/backlog/<NN-chapter>/<US-ID>-<slug>.adoc` and the referenced tech spec item files `specification/tech-specification/<NN-chapter>/<TS-ID>-<slug>.adoc` (saving tokens by loading only the relevant items).
2. **Baseline Check**: Run existing test suite (`npm run check` or `npm run test`) to ensure a green starting state.
3. **TDD Approach**: Write failing unit/component/integration tests matching the story's Test Criteria before writing implementation code.
4. **Implementation**: Write the minimal code necessary to pass all tests.
5. **Quality & DoD Verification**:
   - Run `npm run check` (`tsc`, `eslint`, `vitest`, `validate:specs`).
   - Zero `console.log` or debug leftovers.
6. **Release Notes Update**: Update the target release version file in `specification/release-notes/<version>.adoc` with the new feature and trace back to requirements via story reference (`<<US-x.y>>`, `<<FR-x.y>>`).
7. **Commit**: Commit the story as one commit using [commit](../commit/SKILL.md) (type `feat`).
