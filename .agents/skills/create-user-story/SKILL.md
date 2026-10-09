---
name: create-user-story
description: >-
  Break down a technical specification into atomic, SMART user stories with Acceptance Criteria and Test Pyramid levels in modular chapter files in docs/backlog/.
---

# Skill: Create User Story

Create implementable, atomic user stories with structured test pyramid criteria in modular chapter files.

## Files Modified

- `docs/backlog/<chapter>.adoc`
- `backlog-web.adoc` (if new chapter needs `include::` registration)

## Execution Steps

1. **Target Chapter**: Locate existing chapter file in `docs/backlog/` or create a new chapter file (e.g. `docs/backlog/02-combat.adoc`).
2. **Include Registration**: If creating a new chapter file, add `include::docs/backlog/<chapter>.adoc[]` to `backlog-web.adoc`.
3. **SMART Story Format**:
   - Story Anchor (e.g., `[#US-2.1]`)
   - Narrative: *As a... I want to... So that...*
   - Traceability Links: Reference Tech Spec (`<<TS-2.1>>`) and Requirement (`<<FR-2.1>>`).
   - Acceptance Criteria (numbered, testable).
4. **Test Criteria Definition**: Explicitly specify applicable test levels:
   - **Unit test** (Vitest): Functions, validators, service methods, pure logic.
   - **Component test** (Vitest + RTL): Isolated React components, mocked hooks.
   - **Integration test** (Vitest + fake-indexeddb): Persistence flows, service chains.
   - **Blackbox test** (Playwright): Critical end-to-end user journeys.
5. **Verify**: Run `npm run validate:specs`.
