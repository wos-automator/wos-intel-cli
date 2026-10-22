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

- A master includes each chapter as `include::specification/<folder>/<NN-chapter>/index.adoc[]`.
- A chapter `index.adoc` holds the `==` heading, the chapter intro and one `include::<ID>-<slug>.adoc[]` per item (paths relative to the index).
- An item file starts with its anchor (`[#FR-2.1]`) followed by its `===` heading.
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
- **Time-bound**: includes an effort estimate.

## Traceability

- Requirements reference stakeholder needs or constraints (`SPEC.md §n`).
- Technical specifications reference requirements (`<<FR-x.y>>`).
- User stories reference technical specifications and requirements (`<<TS-x.y>>`, `<<FR-x.y>>`).
- Every change to an artifact needs an impact analysis on the artifacts upstream and downstream.
- The `validate-specs` task (see [toolchain](../toolchain/SKILL.md)) checks includes, unique anchors, references and traceability.

## Test Pyramid

User stories name the levels that apply. The tooling per level is in the component's toolchain profile; project-specific limits (e.g. manual runs on real hardware) are in `AGENTS.md`.

| Level | Scope | Usage |
|---|---|---|
| **Unit** | single functions, pure logic | always, for pure logic and utilities |
| **Component** | one module in isolation, collaborators mocked or faked | every non-trivial module |
| **Integration** | several modules together, incl. files, databases, services | persistence and multi-module flows |
| **Blackbox** | the product as a separate process (CLI, API, UI) | critical user journeys |

## Release Notes

`specification/release-notes/<version>.adoc` lists Features, Fixes and Breaking Changes, each with its traced items (`<<US-x.y>>`, `<<FR-x.y>>`). A new version gets its own file and an include in `release-notes.adoc`, newest first.
