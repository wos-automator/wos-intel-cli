# agent-skills

Shared, project-independent workflows for coding agents (Claude Code, Codex, Gemini, …): specification, implementation, bug fixing, done check and commits, for projects in any language. A project vendors the library unchanged into `.agents/skills/` and keeps everything project-specific in its `AGENTS.md`.

## User's Guide

You talk to the agent in plain language; it picks the skill. What works best: ask for one level at a time, review it, and only then ask for the next.

### Where to Start

1. Adopt the library in the project and write its `AGENTS.md` (see [Adopting the Library](#adopting-the-library)).
2. Write down what is needed as stakeholder input: `SPEC.md` as the index, one file per topic in `specification/stakeholder/`. Stay on the stakeholder's level: what is needed, what must not happen, what you measured or collected (reference material). Mark a technical idea as a proposal unless you would reject any other solution; then it is a constraint.
3. Ask for the requirements of a section, review them, then ask for the next level.

### The Levels

```text
SPEC.md (stakeholder input)
 └─ requirements FR/NFR ─── acceptance scenarios AT (with BDT)
     └─ architecture check (with an architecture overview)
         └─ technical specification TS
             └─ user stories US
                 └─ code, tests, release notes
```

Each level is derived from the one above it and holds only its own kind of content; [spec-system](spec-system/SKILL.md), section Levels and Allocation, says what belongs where. A technical idea in the stakeholder input becomes a proposal for the architecture, not a requirement; a threshold becomes a configuration value, not an acceptance criterion.

### Typical Requests

| You say | The agent | and stops |
|---|---|---|
| "I added §9 to SPEC.md. Create the requirements and let me review them." | [create-requirement](create-requirement/SKILL.md) for each need, with BDT also the scenarios; lists the proposals it found | after the requirements |
| "Requirements approved. Check the architecture and write the technical specification." | [update-architecture](update-architecture/SKILL.md), then [create-tech-specification](create-tech-specification/SKILL.md) | after the technical specification, or earlier with a proposal if the architecture has to change |
| "Cut the stories." | [create-user-story](create-user-story/SKILL.md) | after the stories |
| "Implement US-9.1." | [implement-user-story](implement-user-story/SKILL.md): tests first, done check, release notes, commit | after the commit |
| "New feature: …, down to the backlog, let me review each level." | [create-new-feature](create-new-feature/SKILL.md) with a review gate after each level | after each level |
| "SPEC §3 changed: … Show me the impact first." | [update-feature](update-feature/SKILL.md): impact report | after the report; changes the items after your approval |
| "BUG-0042: …" | [fix-bug](fix-bug/SKILL.md): failing test first, fix, done check, commit | after the commit |
| "Release 0.4.0." | [release](release/SKILL.md): notes, version, checks | before the tag, which you sign and push |

Without "let me review", a request runs through all the levels it names and reports at the end.

### Context per Level

Every level skill names under `Reads` what it loads, and nothing else is needed for that step. That keeps each step's context small, and it is the boundary along which steps can be handed to separate agents.

| Level | Skill | Reads | Writes |
|---|---|---|---|
| Requirements | [create-requirement](create-requirement/SKILL.md) | the stakeholder section, the requirement titles of its chapter | requirement items |
| Scenarios | [create-acceptance-scenarios](create-acceptance-scenarios/SKILL.md) | the requirement, its reference material, the existing step texts | feature files, step definitions |
| Architecture check | [update-architecture](update-architecture/SKILL.md) | the new requirements, the Solution Strategy, the Building Block View, the decision titles | functions, principles, allocation, decisions |
| Technical specification | [create-tech-specification](create-tech-specification/SKILL.md) | the requirements; their function, building block, principles and decisions; the block's code | technical specification items |
| Stories | [create-user-story](create-user-story/SKILL.md) | the technical specification items, their requirements, the scenario IDs, the test limits | story items |
| Implementation | [implement-user-story](implement-user-story/SKILL.md) | the story, its technical specification items, the concepts and decisions they name, the block's code and tests | code, tests, release notes |

## Layers

| Layer | Where | Holds |
|---|---|---|
| Project | `AGENTS.md` of the project | components and their profiles, deviating commands, test limits, commit scopes, extra rules; links to the skills |
| Workflow | `<skill>/SKILL.md` | language-free procedures: specification, implementation, fixes, done check, commit |
| Method | `spec-system/`, `definition-of-done/` | the rules the workflows apply |
| Toolchain | `toolchain/SKILL.md` + `toolchain/<profile>/` | the task contract, one profile per language and build tool |
| Environment | `environment/SKILL.md` + `environment/shells/`; personal: `~/.agents/environment/` | how commands are started on a machine |

Lookup: `AGENTS.md` → workflow skill → method / toolchain → profile, each loaded only when needed. A removed profile folder makes the agent infer the commands from the project's task definitions.

## Task Contract

Workflows never name commands, only tasks: `check`, `test`, `lint`, `format-check`, `typecheck`, `validate-specs`. Each project exposes them through its task runner; see [toolchain](toolchain/SKILL.md).

## Requirements-Based Blackbox Testing

A project may decide that its blackbox level is requirements-based (BDT): acceptance scenarios in Gherkin feature files trace to its requirements, run on pull requests and releases, and every release carries a test report and a traceability report. The [bdt-adopt](bdt-adopt/SKILL.md) skill turns it on; [spec-system](spec-system/SKILL.md) holds the rules, the toolchain profiles the runners (playwright-bdd for node-npm, pytest-bdd for the Python profiles, godog for go-task, Cucumber-JVM on the JUnit Platform for java-maven and java-gradle). Without the decision, nothing of it applies.

## Architecture Overview

A project may also keep an architecture overview in the structure of [arc42](https://arc42.org): context, the solution strategy (logical functions and the principle chosen for each), the building blocks with the allocation of the functions, cross-cutting concepts, decisions (ADR) and a glossary. It explains how the parts fit together and why, and it is checked before a new requirement gets its technical specification. The [architecture-adopt](architecture-adopt/SKILL.md) skill turns it on, [update-architecture](update-architecture/SKILL.md) and [create-architecture-decision](create-architecture-decision/SKILL.md) keep it current; [spec-system](spec-system/SKILL.md) holds the rules. Without the decision, the technical specification carries the structure.

## Releases

Every project releases the same way, offline: the user signs an annotated tag `v<semver>` and pushes it; the pipeline of [release-actions](https://github.com/thst71/release-actions) verifies the signature against the repository's environment secret, runs the gate, builds the artifacts, renders each specification master as one HTML file and publishes the release with the dated release notes. Other tag names stay free for other uses. See the [release](release/SKILL.md) skill for the procedure, the workflow template and the one-time repository setup.

## Versions

The library itself has no release pipeline: a version is a signed, annotated tag `v<semver>` whose message lists the changes since the previous tag. `vendor.sh` writes the vendored version into `.agents/skills/VERSION`; release notes name it ("Built with agent-skills v0.3.0.").

## Precedence

The project's `AGENTS.md` comes first, then this library, then the user's personal instructions and skills (`~/.claude/skills`, `~/.agents/`). Personal files may cover the machine environment and how to communicate, never a project rule. For that reason the library is not linked into `.claude/skills/`: a personal skill of the same name would win there.

## Adopting the Library

Once per machine, trust the maintainer's signing key: `~/.agents/allowed_signers` holds the line `<maintainer email> namespaces="git" <ssh public key>`, with the key as published among the signing keys of the maintainer's GitHub account (`gh api users/thst71/ssh_signing_keys --jq '.[].key'`).

```sh
# first time: from a checkout of this repository
sh /path/to/agent-skills/vendor.sh v0.8.0
# a project using the spec-system: pin the validator (latest release, or v<version>)
.agents/skills/spec-system/bin/validate-specs --update
git commit -m "chore(agents): vendor agent-skills v0.8.0"
# later updates: the vendored copy updates itself
.agents/skills/vendor.sh v0.8.1
git commit -m "chore(agents): vendor agent-skills v0.8.1"
```

`vendor.sh` clones the tag, refuses it unless its SSH signature is by an allowed signer who is the tagger, replaces `.agents/skills/` with the tag's content (without `.github/` and `tests/`) and stages the result, so that every update is one signed, linear commit. A project that used `git subtree` before switches by running it once.

The validator version is the project's own: `.agents/spec-validator.lock` lives outside `.agents/skills/`, so vendoring never changes it, and a new validator release changes neither the library nor the project until `validate-specs --update` pins it. The same key in `~/.agents/allowed_signers` signs the validator's tags. A project coming from v0.3.0 or older (pin inside the library) runs `--update v<version>` once, in the vendoring commit.

Then write the project's `AGENTS.md`: what the project is, a skill table linking `.agents/skills/<skill>/SKILL.md`, the precedence rule, the components with their toolchain profiles, test limits and commit scopes. Adopt the release workflow as the [release](release/SKILL.md) skill describes.

Do not edit the vendored files for one project; adapt in `AGENTS.md`. A change that is right for every project goes into this repository.

## Platforms

macOS and Linux are the targets. Windows is nice to have:

> "Is Windows a real target or just nice to have?" – Claude
>
> "Windows is nice to have, quote me quoting you in the readme :-)" – Thomas Strauß

## Contributing

- Skills are short, numbered procedures with a `Files Modified` and an `Execution Steps` section, in the style of the existing ones. A skill that works on specification items or code also has a `Reads` section: the context the step needs, and nothing more.
- Skills never name a language, a tool or a command; that belongs in a toolchain profile.
- Links between skills are relative (`../toolchain/SKILL.md`); CI checks that they resolve.
- Commits follow the [commit](commit/SKILL.md) skill; the scope is the skill or profile name.

## License

[LGPL-3.0-only](COPYING.LESSER) (which builds on the [GPL-3.0](COPYING)). Using the library in a project of any license is fine; changes to the library itself stay free.
