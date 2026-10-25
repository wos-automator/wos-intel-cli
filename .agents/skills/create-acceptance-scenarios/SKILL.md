---
name: create-acceptance-scenarios
description: >-
  Write the Gherkin acceptance scenarios that accept a requirement, with AT IDs and trace tags, in a project with requirements-based blackbox testing (BDT).
---

# Skill: Create Acceptance Scenarios

Turn the acceptance criteria of a requirement into acceptance scenarios that run as blackbox tests. Only in a project whose `AGENTS.md` names requirements-based blackbox testing; layout, IDs and traces are defined in [spec-system](../spec-system/SKILL.md), section BDT.

## Reads

- The requirement item and the reference material its criteria name
- The feature file of its chapter and the existing step texts
- Not the technical specification: scenarios check the requirement from outside

## Files Modified

- `specification/acceptance/<NN-chapter>/<slug>.feature` (new or extended)
- The step definitions of the component, where a step is new

## Execution Steps

1. **Requirement**: Read the requirement's item file. Each acceptance criterion that is observable from outside the product needs at least one scenario; a criterion that is not (e.g. an internal limit) stays with the lower test levels and is named in the user story instead.
2. **Feature File**: Use the feature file of the requirement's chapter (`specification/acceptance/<NN-chapter>/`) or create one; one feature per file, tagged with the requirements all of its scenarios accept.
3. **IDs**: Give every new `Scenario` or `Scenario Outline` the next free ID of the chapter, `@AT-<chapter>.<n>` (find the highest with `grep -rho '@AT-<chapter>\.[0-9]*' specification/acceptance`). Never reuse an ID, also not of a deleted scenario.
4. **Traces**: Tag the scenario with each requirement it accepts (`@FR-x.y`, `@NFR-x`) unless the feature or rule already carries the tag. No tags of user stories or technical specifications.
5. **Steps**: Write the steps in the language of the user, without implementation details (no selectors, no function names). Reuse existing step texts; a scenario outline covers several values of one behaviour.
6. **Step Definitions**: Implement new steps as the component's toolchain profile (section BDT) describes, against the built product only.
7. **Verify**: Run the `validate-specs` and `bdt` tasks (see [toolchain](../toolchain/SKILL.md)). A scenario for a requirement that is not implemented yet fails; say so instead of weakening it.
