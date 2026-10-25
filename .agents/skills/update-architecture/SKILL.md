---
name: update-architecture
description: >-
  Check new or changed requirements against the architecture overview before their technical specification is written: map them to the logical functions, keep the allocation complete, and change functions, principles, building blocks or decisions first where they do not fit.
---

# Skill: Update Architecture

The architecture check between the requirements and the technical specification, after [spec-system](../spec-system/SKILL.md), section Architecture Overview. Only in a project whose `AGENTS.md` names the architecture overview.

## Reads

- The new or changed requirement items
- The Solution Strategy (functions and principles) and the Building Block View (allocation)
- The titles and status of the decisions; a decision's text only where a principle refers to it

## Files Modified

- `specification/architecture/04-solution-strategy/index.adoc` (functions, principles)
- `specification/architecture/05-building-blocks/index.adoc` (blocks, allocation)
- Other sections where the change reaches them (context, concepts, glossary)

## Execution Steps

1. **Map**: For each new or changed functional requirement, name the logical functions it needs; for each non-functional one, the principles it constrains.
2. **Covered**: If every function exists and its principle fits, the architecture stays as it is. Add the requirement to the functions it is served by, and name function and building block for its technical specification.
3. **Not Covered**: If the requirement needs a new function, a principle that does not fit, or a new building block, propose the change to the user before any technical specification is written: the function, its principle, the decision with [create-architecture-decision](../create-architecture-decision/SKILL.md) where there is a choice, and the change of the allocation.
4. **Coverage**: List every functional requirement that no function serves, every function without a building block and every building block without a function; resolve them with the user.
5. **Concepts**: If technical specifications repeat the same rule, record it as a concept and name it from them.
6. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
