---
name: create-requirement
description: >-
  Break down a feature description into SMART requirements with measurable acceptance criteria and write them to modular item files in specification/requirements/<chapter>/.
---

# Skill: Create Requirement

Break down a feature into formal requirements meeting quality and traceability standards in modular item files. Layout, anchors and SMART criteria are defined in [spec-system](../spec-system/SKILL.md).

## Files Modified

- `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc` (one new file per requirement)
- `specification/requirements/<NN-chapter>/index.adoc` (`include::` line for the new item)
- `specification-web.adoc` (if a new chapter needs `include::` registration)

## Execution Steps

1. **Target Chapter**: Identify the existing chapter folder in `specification/requirements/` or create a new one (e.g. `specification/requirements/02-combat/`) with an `index.adoc` holding the `==` heading.
2. **Include Registration**: Create the item file `<ID>-<slug>.adoc` (e.g. `FR-2.1-attack-order.adoc`) and add `include::<ID>-<slug>.adoc[]` to the chapter `index.adoc`. For a new chapter, add `include::specification/requirements/<NN-chapter>/index.adoc[]` to `specification-web.adoc`.
3. **SMART Criteria Check**: Check each requirement against the SMART criteria.
4. **Draft Section**: In the item file, add the requirement section:
   - Unique anchor (e.g., `[[FR-2.1]]`)
   - Title
   - Description
   - Acceptance criteria (numbered with verifiable conditions)
   - Stakeholder need / constraint link
5. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
