---
name: traceability-report
description: >-
  Generate and read the test report and the traceability report of a project with requirements-based blackbox testing (BDT): which requirements the acceptance scenarios cover, which scenarios are orphaned, what failed.
---

# Skill: Traceability Report

Create the two generated reports locally and act on them. The release pipeline creates the same reports for every release, pull requests attach them as an artifact. Rules in [spec-system](../spec-system/SKILL.md), section BDT.

## Reads

- The results of the last `bdt` run and the two generated reports
- For each finding, only the requirement or scenario it names

## Files Modified

- `test-report.adoc`, `traceability-report.adoc` in the project root (generated, ignored by git)

## Execution Steps

1. **Run**: Run the `bdt` task (see [toolchain](../toolchain/SKILL.md)); it writes `build/bdt/cucumber.json`.
2. **Test Report**: `.agents/skills/spec-system/bin/validate-specs -test-report build/bdt/cucumber.json`.
3. **Traceability Report**: `.agents/skills/spec-system/bin/validate-specs -trace-report -results build/bdt/cucumber.json`, after the test report, so that scenario IDs become links.
4. **Read**: From `traceability-report.adoc`, report to the user:
   - failed, undefined or not run scenarios, with their requirements;
   - orphaned scenarios (should be none): fix their trace tags with [update-acceptance-scenarios](../update-acceptance-scenarios/SKILL.md);
   - uncovered requirements: propose scenarios with [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md), or state why a requirement is not testable from outside (later: a manual test specification).
5. **Do Not Commit** the reports; they are rebuilt from the results.
