---
name: fix-bug
description: >-
  Reproduce and fix a bug with an automated regression test, root cause analysis, and update specification/release-notes/.
---

# Skill: Fix Bug

Reproduce, diagnose, and resolve defects with automated regression coverage.

## Reads

- The defect report and the requirement it violates
- The technical specification of the affected part and its code and tests

## Files Modified

- Source code files causing the defect
- Test files, in the layout of the existing tests
- `specification/release-notes/<version>.adoc`

## Execution Steps

1. **Reproduction**: Write an automated test (unit or integration) reproducing the bug. Ensure the test fails before applying fixes.
2. **Root Cause Analysis**: Inspect source files and diagnose the underlying defect.
3. **Fix**: Implement the minimal fix to turn the test green without introducing regressions.
4. **Verification**: Apply [definition-of-done](../definition-of-done/SKILL.md); the `check` task must pass.
5. **Release Notes**: Update `specification/release-notes/<version>.adoc` under the Fixes section, noting any behavioral changes.
6. **Commit**: Commit the fix as one commit using [commit](../commit/SKILL.md) (type `fix`, `Fixes: BUG-xxxx`).
