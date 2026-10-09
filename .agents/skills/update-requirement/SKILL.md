---
name: update-requirement
description: >-
  Update an existing requirement in docs/specifications/ chapter files and perform an impact check on tech-specifications and backlog chapters.
---

# Skill: Update Requirement

Modify existing requirements and cascade impacts to downstream technical specifications and stories.

## Files Modified

- `docs/specifications/<chapter>.adoc`
- `docs/tech-specifications/<chapter>.adoc` (impact check)
- `docs/backlog/<chapter>.adoc` (impact check)

## Execution Steps

1. **Locate**: Find the target requirement anchor (e.g., `[#FR-1.0]`) in the appropriate chapter file under `docs/specifications/`.
2. **Update**: Modify description, title, or acceptance criteria while ensuring SMART criteria compliance.
3. **Impact Check**: Search `docs/tech-specifications/` and `docs/backlog/` for references to the changed requirement anchor.
4. **Cascade**: Update affected technical specs and story test criteria, or flag dependencies for the user.
5. **Validate**: Run `npm run validate:specs`.
