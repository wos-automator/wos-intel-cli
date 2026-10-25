---
name: update-requirement
description: >-
  Update an existing requirement in its specification/requirements/ item file and perform an impact check on tech-specification and backlog items.
---

# Skill: Update Requirement

Modify existing requirements and cascade impacts to downstream technical specifications and stories, following [spec-system](../spec-system/SKILL.md).

## Reads

- The requirement item and the stakeholder input it cites
- For the impact check: only the items that reference it

## Files Modified

- `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc`
- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc` (impact check)
- `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc` (impact check)

## Execution Steps

1. **Locate**: Open the requirement's item file, found by ID (e.g. `ls specification/requirements/*/FR-1.0-*`).
2. **Update**: Modify description, title, or acceptance criteria while ensuring SMART criteria compliance and the level of a requirement (Levels and Allocation of [spec-system](../spec-system/SKILL.md)): content that belongs to another level moves there instead of staying.
3. **Impact Check**: Search `specification/tech-specification/` and `specification/backlog/` (e.g. `grep -rl '<<FR-1.0' specification`) for references to the changed requirement anchor; If `AGENTS.md` names requirements-based blackbox testing (BDT), also `specification/acceptance/` for its trace tag (`grep -rn '@FR-1.0' specification/acceptance`); if it names the architecture overview, also `specification/architecture/` (the functions that serve it, the decisions it motivates).
4. **Impact Report**: List the affected technical specifications and user stories for the user, each with what has to change.
5. **Cascade**: If the user asked to see the impact first, stop after the report and wait for approval. Then update affected technical specs and story acceptance and test criteria, or flag dependencies for the user; affected scenarios with [update-acceptance-scenarios](../update-acceptance-scenarios/SKILL.md); the architecture with [update-architecture](../update-architecture/SKILL.md).
6. **Validate**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
