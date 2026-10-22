---
name: update-user-story
description: >-
  Update or extend an existing user story in its specification/backlog/ item file with updated acceptance criteria and test pyramid criteria.
---

# Skill: Update User Story

Modify an existing user story, technical tasks, and associated test pyramid criteria in its item file, following [spec-system](../spec-system/SKILL.md).

## Files Modified

- `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc`
- `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc` (impact check)

## Execution Steps

1. **Locate**: Open the story's item file, found by ID (e.g. `ls specification/backlog/*/US-1.0-*`).
2. **Update**: Update story narrative, acceptance criteria, technical tasks, or test criteria.
3. **Test Criteria Alignment**: Ensure test pyramid sections reflect any added or changed acceptance criteria.
4. **Impact Check**: Check for gaps in the referenced `specification/tech-specification/` items or requirement invalidations, and update or flag accordingly.
5. **Validate**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
