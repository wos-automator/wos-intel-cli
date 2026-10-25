---
name: definition-of-done
description: >-
  Verify that an implementation task is complete: quality gate green, no debug leftovers, conventions kept, release notes updated. Run before declaring a story or fix done and before committing.
---

# Skill: Definition of Done

An implementation task is complete ONLY when all checks below pass.

## Checks

1. **Quality Gate**: The `check` task passes for every changed component (see [toolchain](../toolchain/SKILL.md)): tests, type check, lint, format check and spec validation, without errors or warnings.
2. **No Leftovers**: No debug output, unused variables or imports, or leftover debug code. The component's profile lists what counts as a debug leftover in its language.
3. **Conventions**: The code follows the existing architectural patterns and style of the surrounding code.
4. **Release Notes**: The file of the next version, `specification/release-notes/<version>.adoc` with the heading `== Release v<version> (unreleased)`, names the change under Features, Fixes or Breaking Changes with its traced items (see [spec-system](../spec-system/SKILL.md)); create it if the last release closed the previous one.
5. **Test Durations**: The test run recorded the execution time of each test (see [toolchain](../toolchain/SKILL.md)); report tests the change made noticeably slower, with the reason.
6. **Architecture**: If `AGENTS.md` names the architecture overview, a change of building blocks, of a concept or of a decision is reflected there ([update-architecture](../update-architecture/SKILL.md), [create-architecture-decision](../create-architecture-decision/SKILL.md)).
7. **Acceptance Scenarios**: If `AGENTS.md` names requirements-based blackbox testing (BDT): the `bdt` task passes for the scenarios of the changed requirements, and [traceability-report](../traceability-report/SKILL.md) shows no orphaned scenario.
8. **Project Additions**: Any further criterion listed under `Definition of Done` in `AGENTS.md`.

If a check cannot pass, the task is not done: report what fails instead of committing.
