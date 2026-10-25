---
name: update-acceptance-scenarios
description: >-
  Change, retrace or retire acceptance scenarios after a requirement changed, in a project with requirements-based blackbox testing (BDT); keeps AT IDs stable.
---

# Skill: Update Acceptance Scenarios

Keep the acceptance scenarios in line with changed requirements. Only in a project whose `AGENTS.md` names requirements-based blackbox testing; rules in [spec-system](../spec-system/SKILL.md), section BDT.

## Reads

- The changed requirement items
- The scenarios that trace to them and the existing step texts

## Files Modified

- `specification/acceptance/<NN-chapter>/<slug>.feature`
- The step definitions of the component, where steps change

## Execution Steps

1. **Locate**: Find the scenarios of the changed requirement: `grep -rn '@FR-x.y' specification/acceptance` (also on `Feature` and `Rule` lines).
2. **Impact Report**: List for the user each scenario with what changes: steps, examples, traces, or retirement.
3. **Update**: Change steps and examples to the new acceptance criteria. A scenario keeps its ID while it accepts the same behaviour; a new behaviour gets a new scenario with [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md).
4. **Retrace**: When a scenario accepts another requirement now, change its trace tags; it must keep at least one.
5. **Retire**: A scenario whose behaviour is gone is deleted; its ID is not reused. Mention it in the release notes under Breaking Changes when users relied on the behaviour.
6. **Verify**: Run the `validate-specs` and `bdt` tasks, then [traceability-report](../traceability-report/SKILL.md) to check that no requirement became uncovered.
