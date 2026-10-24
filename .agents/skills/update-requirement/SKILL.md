---
name: update-requirement
description: >-
  Update an existing requirement in its specification/requirements/ item file and perform an impact check on tech-specification and backlog items.
---

# Skill: Update Requirement

Modify existing requirements and cascade impacts to downstream technical specifications and stories, following [spec-system](../spec-system/SKILL.md).

## Files Modified

- `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc`
- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc` (impact check)
- `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc` (impact check)

## Execution Steps

1. **Locate**: Open the requirement's item file, found by ID (e.g. `ls specification/requirements/*/FR-1.0-*`).
2. **Update**: Modify description, title, or acceptance criteria while ensuring SMART criteria compliance.
3. **Impact Check**: Search `specification/tech-specification/` and `specification/backlog/` (e.g. `grep -rl '<<FR-1.0' specification`) for references to the changed requirement anchor.
4. **Impact Report**: List the affected technical specifications and user stories for the user, each with what has to change.
5. **Cascade**: Update affected technical specs and story acceptance and test criteria, or flag dependencies for the user.
6. **Validate**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
