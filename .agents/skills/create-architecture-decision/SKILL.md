---
name: create-architecture-decision
description: >-
  Record an architecture decision (ADR) with context, alternatives and consequences in a project with an architecture overview, or supersede an earlier one.
---

# Skill: Create Architecture Decision

Record a choice between real alternatives in the architecture overview. The template and the rules are in [spec-system](../spec-system/SKILL.md), sections Item Templates and Architecture Overview. Only in a project whose `AGENTS.md` names the architecture overview.

## Reads

- The requirements that motivate the choice and the stakeholder input they cite
- The Solution Strategy and the existing decisions (titles and status)
- Where the choice is already implemented: the code that shows it

## Files Modified

- `specification/architecture/09-decisions/ADR-<n>-<slug>.adoc` (new)
- `specification/architecture/09-decisions/index.adoc` (`include::` line)
- The superseded decision and the Solution Strategy, if the decision replaces one

## Execution Steps

1. **Is it a Decision**: There must be at least one real alternative that was considered or that a reader would ask about. A rule without alternative is a concept; a detail of one requirement belongs to its technical specification.
2. **ID**: The next free number (`grep -rho '\[\[ADR-[0-9]*' specification/architecture`). Never reuse a number, also not of a superseded decision.
3. **Draft**: Fill the template: `Status::` (`Proposed` until the user accepts it, then `Accepted (<version>)`), `Motivated by::` with the requirements, the context with the forces at the time (a stakeholder's proposal belongs here, not in a requirement), the decision, every alternative with the reason against it, and the consequences, the negative ones included. Verify every claim about the code in the code.
4. **Supersede**: A decision that replaces an earlier one says so in its context; the earlier one gets the status "Superseded by `<<ADR-n>>`" and keeps its text. Update the solution principle in the Solution Strategy.
5. **Impact**: List the technical specifications that follow the earlier decision or are affected by the new one for the user, each with what has to change.
6. **Verify**: Run the `validate-specs` task (see [toolchain](../toolchain/SKILL.md)).
