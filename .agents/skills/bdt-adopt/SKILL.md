---
name: bdt-adopt
description: >-
  Turn on requirements-based blackbox testing (BDT) in a project once the user has decided on it: acceptance scenarios in Gherkin feature files, their validation, the bdt task, and test and traceability reports on pull requests and releases.
---

# Skill: Adopt Requirements-Based Blackbox Testing

Run once per project, after the user decided that its blackbox level is requirements-based. The rules are in [spec-system](../spec-system/SKILL.md), section BDT; this skill sets the project up for them.

## Reads

- `AGENTS.md`, the BDT section and the Pull Request and Release Build steps of the component's toolchain profile
- The existing workflows and task definitions of the component
- One requirement for the first scenarios

## Files Modified

- `AGENTS.md` (Testing, the BDT skills)
- `.spec-validator.json` (test kind `AT`)
- `.agents/spec-validator.lock` (spec-validator 0.2.1 or later)
- `specification/acceptance/` (first feature file)
- The task definitions and test setup of the component (the `bdt` task of its toolchain profile)
- `.gitignore` (generated reports and results)
- `.github/workflows/pull-request.yml`, `.github/workflows/release.yml`

## Execution Steps

1. **Decision**: Confirm with the user that the blackbox level becomes requirements-based. Do not adopt BDT on your own.
2. **Validator**: If `.agents/spec-validator.lock` pins a version below 0.2.1 (0.2.0 was never published), ask the user to update it, then run `.agents/skills/spec-system/bin/validate-specs --update v<version>` with the version the user chose, at least `v0.2.1` (see [spec-system](../spec-system/SKILL.md), Validator), and commit the lock on its own.
3. **Configuration**: Write `.spec-validator.json` with the default layout of [spec-system](../spec-system/SKILL.md) (or the project's own) plus the test kind `{"kind": "AT", "folder": "specification/acceptance", "format": "gherkin", "traces": ["FR", "NFR"]}`. Run the `validate-specs` task.
4. **Tooling**: Set up the runner of the component's toolchain profile (section BDT): dependencies, configuration, step definitions folder and the `bdt` task writing `build/bdt/cucumber.json`. A profile without a BDT section: stop and tell the user; do not invent one.
5. **First Scenarios**: Write scenarios for one existing requirement with [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md) and run the `bdt` task until they pass.
6. **Ignore**: Add `build/`, `test-report.adoc` and `traceability-report.adoc` to `.gitignore`, plus the runner's generated files the profile names.
7. **Workflows**: In `.github/workflows/pull-request.yml` ([template](../release/pull-request.yml)) and `.github/workflows/release.yml` ([template](../release/release.yml)), add the `bdt` steps of the profile's Pull Request and Release Build steps. The BDT steps of both templates run only when feature files exist.
8. **AGENTS.md**: Add under "Testing" the line "Testing: requirements-based blackbox tests (BDT)" and the skills [create-acceptance-scenarios](../create-acceptance-scenarios/SKILL.md), [update-acceptance-scenarios](../update-acceptance-scenarios/SKILL.md) and [traceability-report](../traceability-report/SKILL.md) to the skill table.
9. **Verify**: Run the `check` and `bdt` tasks, then [traceability-report](../traceability-report/SKILL.md). Uncovered requirements are expected at first; list them for the user.
10. **Commit**: One commit with [commit](../commit/SKILL.md): `chore: requirements-based blackbox testing`.
