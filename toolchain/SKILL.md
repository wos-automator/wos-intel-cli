---
name: toolchain
description: >-
  Resolve how to install, build, test, lint and validate a project from its task contract and the language profile of each component; infer the commands when no profile matches.
---

# Skill: Toolchain

Every other skill names **contract tasks** (e.g. "run the `check` task") instead of commands. This skill turns a task name into the command for the component at hand.

## Task Contract

Each project exposes these tasks through its task runner. Spelling may follow the runner's convention (`validateSpecs` in Gradle).

| Task | Required | Does |
|---|---|---|
| `check` | yes | the quality gate: everything below that the project has, in one command; fails on any error or warning |
| `test` | yes | the full test suite |
| `lint` | yes | static analysis |
| `format-check` | if a formatter is used | formatting verification without changing files |
| `typecheck` | if the language has a separate type check | type check or compilation |
| `validate-specs` | if the project uses the [spec-system](../spec-system/SKILL.md) | anchors, includes, traceability |
| `dist` | if the project releases artifacts | builds the release artifacts into `dist/` (see [release](../release/SKILL.md)) |
| `version` | if the version lives in a file | prints the project version, so that a release can compare it with the tag |

Dependency installation and running a single test level are not tasks; the profile names the commands. Each profile also lists its `Release Build`: the workflow steps that set up the toolchain and run `check` and `dist` in the release pipeline.

## Resolution Order

1. **Project facts**: `AGENTS.md` lists the components (path → profile) and any deviating command. Those win.
2. **Profile**: `<profile>/PROFILE.md` next to this file for the component's profile.
3. **Inference**: when the component has no profile, or the profile folder was removed (see below).

Load the [environment](../environment/SKILL.md) skill before running the first command.

## Profiles

| Profile | Marker files |
|---|---|
| [python-uv](python-uv/PROFILE.md) | `pyproject.toml` + `uv.lock` |
| [python-poetry](python-poetry/PROFILE.md) | `pyproject.toml` + `poetry.lock` |
| [go-task](go-task/PROFILE.md) | `go.mod` + `Taskfile.yml` |
| [java-maven](java-maven/PROFILE.md) | `pom.xml` |
| [java-gradle](java-gradle/PROFILE.md) | `build.gradle(.kts)` / `settings.gradle(.kts)` |

A profile holds what is true for every project of its kind: task runner invocation, install command, test tooling per pyramid level and the language's debug leftovers. Project-specific values belong in `AGENTS.md`, never in a profile.

## Inference (no profile)

1. **Detect**: Identify the ecosystem from marker files in the component root (`package.json` + lockfile, `Cargo.toml`, `*.csproj`, `Makefile`, the files above, …).
2. **Read the task definitions**: `[tool.poe.tasks]`, `package.json` `scripts`, `Taskfile.yml`, `Makefile` targets, Gradle tasks, Maven phases.
3. **Map**: Assign each contract task to an existing task or command. Do not invent a task the project lacks; report the gap instead.
4. **Report**: Tell the user the mapping before relying on it, and suggest adding it to `AGENTS.md` or as a new profile.

## Multi-Component Projects

Resolve per component: run a component's tasks from its root with its profile. The project-level `check` passes only when every component's `check` passes.
