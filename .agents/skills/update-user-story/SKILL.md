---
name: update-user-story
description: >-
  Update or extend an existing user story in docs/backlog/ chapter files with updated acceptance criteria and test pyramid criteria.
---

# Skill: Update User Story

Modify an existing user story, technical tasks, and associated test pyramid criteria in modular chapter files.

## Files Modified

- `docs/backlog/<chapter>.adoc`
- `docs/tech-specifications/<chapter>.adoc` (impact check)

## Execution Steps

1. **Locate**: Find the user story section anchor (e.g. `[#US-1.0]`) in the chapter file under `docs/backlog/`.
2. **Update**: Update story narrative, acceptance criteria, technical tasks, or test criteria.
3. **Test Criteria Alignment**: Ensure test pyramid sections reflect any added or changed acceptance criteria.
4. **Impact Check**: Check for gaps in `docs/tech-specifications/` or requirement invalidations, and update or flag accordingly.
5. **Validate**: Run `npm run validate:specs`.
