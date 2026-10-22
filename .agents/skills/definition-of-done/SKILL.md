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
4. **Release Notes**: The file of the next version, `specification/release-notes/<version>.adoc` with the heading `== <version> (unreleased)`, names the change under Features, Fixes or Breaking Changes with its traced items (see [spec-system](../spec-system/SKILL.md)); create it if the last release closed the previous one.
5. **Project Additions**: Any further criterion listed under `Definition of Done` in `AGENTS.md`.

If a check cannot pass, the task is not done: report what fails instead of committing.
