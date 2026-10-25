---
name: create-requirement
description: >-
  Break down a feature description into SMART requirements with measurable acceptance criteria and write them to modular item files in specification/requirements/<chapter>/.
---

# Skill: Create Requirement

Break down a feature into formal requirements meeting quality and traceability standards in modular item files. Layout, anchors, levels and SMART criteria are defined in [spec-system](../spec-system/SKILL.md).

## Reads

- The stakeholder input the requirement comes from (its `SPEC.md` section)
- The requirements of the target chapter (titles), to avoid overlaps
- Not the architecture, the technical specification or the code: a requirement does not depend on the solution

## Files Modified

- `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc` (one new file per requirement)
- `specification/requirements/<NN-chapter>/index.adoc` (`include::` line for the new item)
- The requirements master (see [spec-system](../spec-system/SKILL.md), Layout), if a new chapter needs `include::` registration

## Execution Steps

1. **Target Chapter**: Identify the existing chapter folder in `specification/requirements/` or create a new one (e.g. `specification/requirements/02-combat/`) with an `index.adoc` holding the `==` heading.
2. **Include Registration**: Create the item file `<ID>-<slug>.adoc` (e.g. `FR-2.1-attack-order.adoc`) and add `include::<ID>-<slug>.adoc[]` to the chapter `index.adoc`. For a new chapter, add `include::specification/requirements/<NN-chapter>/index.adoc[]` to the requirements master.
3. **SMART Criteria Check**: Check each requirement against the SMART criteria.
4. **Level Check**: Check each requirement against Levels and Allocation of [spec-system](../spec-system/SKILL.md): it holds behaviour seen from outside; no modules, files, commands, algorithms or tuning values. Decide for each technical statement of the stakeholder whether it is a constraint (a non-functional requirement) or a proposal, and for each number whether it stays in the requirement. Report the proposals to the user; they go to the architecture or the technical specification, not into the requirement.
5. **Draft Section**: In the item file, add the requirement section after the requirement template of [spec-system](../spec-system/SKILL.md):
   - Unique anchor (e.g., `[[FR-2.1]]`)
   - Title
   - Description
   - Acceptance criteria (numbered with verifiable conditions)
   - Stakeholder need / constraint link
   - Effort estimate
6. **Acceptance Scenarios**: If `AGENTS.md` names requirements-based blackbox testing (BDT), write the requirement's scenarios with [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md).
7. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
