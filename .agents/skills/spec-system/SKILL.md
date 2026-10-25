---
name: spec-system
description: >-
  The modular AsciiDoc specification system: file layout, item files, anchors, traceability, SMART criteria and test pyramid levels. Read before creating, updating or researching requirements, technical specifications, user stories or release notes.
---

# Skill: Specification System

The shared rules for all specification artifacts. The `create-*` and `update-*` skills apply them; this skill only describes them.

## Documentation Format

- Specifications, backlog and release notes are AsciiDoc (`.adoc`); asciidoctor-diagram syntax is available for diagrams.
- Stakeholder input is Markdown.

## Layout

To keep the context small, every item lives in its own file.

| Kind | Master (project root) | Item files | Anchors |
|---|---|---|---|
| Requirements | `specification-web.adoc` | `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc` | `FR-x.y`, `NFR-x` |
| Technical specifications | `tech-specification-web.adoc` | `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc` | `TS-x.y` |
| User stories | `backlog-web.adoc` | `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc` | `US-x.y` |
| Release notes | `release-notes.adoc` | `specification/release-notes/<version>.adoc` | – |
| Stakeholder input | `SPEC.md` (index only) | `specification/stakeholder/<NN>-<topic>.md` | `SPEC.md §n` = file `<NN>` |
| Acceptance scenarios (BDT only) | – (rendered in the test report) | `specification/acceptance/<NN-chapter>/<slug>.feature` | `@AT-x.y` |

- The master names above are the default layout of the validator; a project that names them differently configures them in `.spec-validator.json` (see Validator). The other skills say "the master" of a kind and mean these files.
- A master includes each chapter as `include::specification/<folder>/<NN-chapter>/index.adoc[]`.
- A chapter `index.adoc` holds the `==` heading, the chapter intro and one `include::<ID>-<slug>.adoc[]` per item (paths relative to the index).
- An item file starts with its anchor `[[FR-2.1]]` followed by its `===` heading. Never the shorthand `[#FR-2.1]`: Asciidoctor reads the dot as a role and gives FR-2.1 and FR-2.2 the same id `FR-2`.
- A new item gets its own file plus an include line in the chapter index; a new chapter gets a folder, an `index.adoc` and an include in the master.

## Reading

- Find an item by ID: `ls specification/*/*/<ID>-*`. Load only that file.
- Load a chapter `index.adoc` only for the chapter intro.
- Find references to an item: `grep -rl '<<FR-2.1' specification`.

## SMART Criteria

Every requirement and user story is:

- **Specific**: clearly and unambiguously stated.
- **Measurable**: acceptance criteria are testable and verifiable.
- **Achievable**: implementable within the project's stack.
- **Relevant**: traceable to a stakeholder need or a parent requirement.
- **Time-bound**: includes an effort estimate (`Effort::`).

## Item Templates

Requirement (`Stakeholder need::` is a constraint instead where there is no need behind it):

```asciidoc
[[FR-2.1]]
=== FR-2.1 Attack order

The system shall <one statement>.

.Acceptance criteria
. <verifiable condition>

Stakeholder need:: SPEC.md §2.1 +
Effort:: 2 h
```

Technical specification:

```asciidoc
[[TS-2.1]]
=== TS-2.1 Attack planner

Implements <<FR-2.1>> and <<NFR-3>>.

<architecture, data model, interface definitions, interactions>
```

User story (a test level that does not apply says why, e.g. `* Blackbox test: none, no user journey`):

```asciidoc
[[US-2.1]]
=== US-2.1 Plan the attack order

Effort:: 4 h +
Traces to:: <<TS-2.1>>, <<FR-2.1>>

As a <role>, I want <goal>, so that <benefit>.

.Acceptance criteria
. <testable condition>

.Technical tasks
. <implementation step>

.Test criteria
* Unit test: <functions, validators, services and what they must show>
* Component test: <rendered or isolated modules, interactions>
* Integration test: <persistence, service chains>
* Blackbox test: <critical user journey>
```

## Traceability

- Requirements reference stakeholder needs or constraints (`SPEC.md §n`).
- Technical specifications reference requirements (`<<FR-x.y>>`).
- User stories reference technical specifications and requirements (`<<TS-x.y>>`, `<<FR-x.y>>`).
- Every change to an artifact needs an impact analysis on the artifacts upstream and downstream.
- The `validate-specs` task (see [toolchain](../toolchain/SKILL.md)) checks includes, unique anchors, references and traceability.

## Validator

- The `validate-specs` task runs [spec-validator](https://github.com/thst71/spec-validator) through the launcher `bin/validate-specs` (`bin/validate-specs.ps1` on Windows), from the project root. The project pins the release in `.agents/spec-validator.lock` (version and archive checksums, checked in). The launcher runs an installed `spec-validator` whose `-version` is exactly the pinned version; otherwise it downloads the release once into the user cache and verifies it against the lock.
- `bin/validate-specs --update [v<version>]` pins a release (default: the latest release; tags without a release are skipped): it refuses a tag that is not signed by an allowed signer of `~/.agents/allowed_signers`, writes the lock from the release's checksums and stages it. Commit it as `chore: spec-validator <version>`. Update the pin only when the user asks for it; a stricter validator then shows up in that commit, not in an unrelated one.
- Exit code 0: valid; 1: problems, one per line; 2: usage or configuration error.
- A project with a different layout (masters, folders, anchor kinds, traceability rules) describes it in `.spec-validator.json` in its root; see the validator's README.
- `SPEC_VALIDATOR=<path>` runs another binary, e.g. a development build.

## Test Pyramid

User stories name the levels that apply. The tooling per level is in the component's toolchain profile; project-specific limits (e.g. manual runs on real hardware) are in `AGENTS.md`.

| Level | Scope | Usage |
|---|---|---|
| **Unit** | single functions, pure logic | always, for pure logic and utilities |
| **Component** | one module in isolation, collaborators mocked or faked | every non-trivial module |
| **Integration** | several modules together, incl. files, databases, services | persistence and multi-module flows |
| **Blackbox** | the product as a separate process (CLI, API, UI) | critical user journeys |

## Requirements-Based Blackbox Testing (BDT)

A project decides whether its blackbox level is requirements-based. `AGENTS.md` says so under "Testing"; without that line, everything in this section is off and the blackbox level tests critical user journeys as the toolchain profile describes. The [bdt-adopt](../bdt-adopt/SKILL.md) skill turns it on.

- **Scenarios**: acceptance scenarios are Gherkin feature files (English) in `specification/acceptance/<NN-chapter>/<slug>.feature`, one feature per file, chapters as in the requirements.
- **IDs**: every `Scenario` or `Scenario Outline` carries exactly one tag `@AT-x.y`, unique across all feature files; `x` is the chapter, `y` counts within it. Never put an ID on `Feature`, `Rule` or `Examples`.
- **Traces**: bottom-up only, from a scenario to the requirements it accepts: tags `@FR-x.y`, `@NFR-x` on the scenario, or on its `Feature` or `Rule` for all of its scenarios. Scenarios do not trace to user stories or technical specifications; stories may reference scenarios (`<<AT-x.y>>`) in their test criteria.
- **Validation**: `.spec-validator.json` lists the test kind (`"tests": [{"kind": "AT", "folder": "specification/acceptance", "format": "gherkin", "traces": ["FR", "NFR"]}]`); the `validate-specs` task then checks IDs, uniqueness and traces with the rest of the specification. It needs spec-validator 0.2.1 or later.
- **Runs**: the `bdt` task (see [toolchain](../toolchain/SKILL.md)) runs the scenarios against the built product and writes Cucumber JSON to `build/bdt/cucumber.json`. Not on every commit: in the Definition of Done, on pull requests and on releases.
- **Reports**: `validate-specs -test-report build/bdt/cucumber.json` writes `test-report.adoc` (every scenario with its steps and result), `validate-specs -trace-report -results build/bdt/cucumber.json` writes `traceability-report.adoc` (requirements to scenarios, scenarios to requirements, orphaned scenarios, uncovered requirements). Both are generated, never committed; pull requests attach them as a job artifact, releases render them with the other masters. See [traceability-report](../traceability-report/SKILL.md).
- **Later test kinds**: the validator configuration lists test kinds, so that manual test specifications (e.g. `MT`, with a report template) and a completeness rule for requirements can be added without changing this layout.

## Release Notes

`specification/release-notes/<version>.adoc` lists Features, Fixes and Breaking Changes, each with its traced items (`<<US-x.y>>`, `<<FR-x.y>>`). A new version gets its own file and an include in `release-notes.adoc`, newest first.

- The heading of a version is `== Release v<version> (<date>)`: until the release `== Release v<version> (unreleased)`, then the [release](../release/SKILL.md) skill sets `YYYY-MM-DD`. The release pipeline refuses any other heading.
- Directly below the heading: `Built with agent-skills v<version>.`, the content of `.agents/skills/VERSION` at the release. The pipeline compares both.
- The master `release-notes.adoc` has no `:sectnums:`: a number in front of the version ("2. 0.1.0") is easily misread.
- The first change after a release creates the file of the next version.

## Rendering

Every release attaches each master as one HTML file (images and diagrams embedded) plus a zip of all of them. References to items of another master become links between these files. Asciidoctor fails the release on any warning or unresolved reference, so:

- Write literal references in running text as passthrough: `` `+<<ID>>+` ``. Inside plain backticks, `<<ID>>` is still a reference.
- Diagrams use asciidoctor-diagram (PlantUML, Graphviz, …); they render in the pipeline without extra setup.
