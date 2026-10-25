---
name: architecture-adopt
description: >-
  Set up the architecture overview of a project (arc42 sections: context, solution strategy with logical functions, building blocks with their allocation, concepts, decisions, glossary) once the user has decided on it, derived from the requirements and the code.
---

# Skill: Adopt the Architecture Overview

Run once per project, after the user decided to keep an architecture overview. The rules are in [spec-system](../spec-system/SKILL.md), sections Levels and Allocation and Architecture Overview; this skill sets the project up for them.

## Reads

- The requirements (titles and acceptance criteria, chapter by chapter) and the stakeholder input they cite
- The technical specification: chapter intros and the items' first lines
- The code: the modules and what they import

## Files Modified

- `AGENTS.md` (Architecture, the architecture skills)
- `.spec-validator.json` (master, kinds `ADR` and `LF`, rule for `ADR`)
- The architecture master and `specification/architecture/<NN-section>/`
- `specification/release-notes/<version>.adoc`

## Execution Steps

1. **Decision**: Confirm with the user that the project keeps an architecture overview. Do not adopt it on your own.
2. **Configuration**: Add the master, the kinds and the rule of [spec-system](../spec-system/SKILL.md) (Architecture Overview, Validation) to `.spec-validator.json`; write the file with the default layout first if the project has none. Run the `validate-specs` task.
3. **Skeleton**: Create the master with one include per section and a chapter `index.adoc` per section (the usual start of spec-system).
4. **Context and Building Blocks**: Describe the neighbours of the system and the building blocks with their dependencies as the code shows them; verify every dependency in the code, not in the technical specification.
5. **Function Structure**: Derive the logical functions from the functional requirements, solution-free, each naming the requirements it serves. List every functional requirement no function serves and resolve it with the user.
6. **Principles and Decisions**: Name the solution principle of each function. Record the choices with real alternatives that the code and the specification show as decisions with [create-architecture-decision](../create-architecture-decision/SKILL.md).
7. **Allocation**: Write the matrix of functions to building blocks; every function has a block and every block a function.
8. **Concepts and Glossary**: Record what several technical specifications rely on as concepts, and the domain terms of the specification as the glossary.
9. **Allocation Review**: List for the user what the existing items hold on the wrong level (Levels and Allocation): solutions in requirements, a project structure in a requirement or technical specification, values repeated outside the configuration. Do not move them on your own; the user decides, and [update-requirement](../update-requirement/SKILL.md) moves them.
10. **AGENTS.md**: Add under "Architecture" the line "Architecture: architecture overview (`architecture-web.adoc`)" and the skills [update-architecture](../update-architecture/SKILL.md) and [create-architecture-decision](../create-architecture-decision/SKILL.md) to the skill table.
11. **Verify**: Run the `validate-specs` task; render the masters if the project renders them locally. Name the overview in the release notes under Documentation.
12. **Commit**: One commit with [commit](../commit/SKILL.md): `docs: architecture overview`.
