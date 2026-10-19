# Workspace Guidelines & Rules

## Terminal Execution Environment

The user relies on `fish` shell and its specific PATH environment variables. Whenever executing a terminal command (e.g. `uv run poe test`, `uv run poe check`, `uv sync`) using the `run_command` tool, you **MUST** wrap and execute the command in a Fish login shell:
`fish -lc "your command here"`

---

## Toolchain

> Machine-readable summary for agent skills (create-requirement, create-tech-specification, create-user-story, create-new-feature, update-requirement, definition-of-done, etc.). Keep this in sync with the sections below if commands ever change.

- Ecosystem: Python 3.11+ / uv (`pyproject.toml`, tasks via `poethepoet`)
- Quality gate command: `uv run poe check` (runs `ruff check`, `ruff format --check`, `mypy`, `pytest`, and validate-specs together)
- Spec validation command: `uv run poe validate-specs` → `python scripts/validate_specs.py`
- Dependency install: `uv sync`
- Test pyramid mapping:
  - Unit: pytest (`uv run pytest -m unit`)
  - Component: pytest + `pytest-mock` / scripted fake game (`uv run pytest -m component`)
  - Integration: pytest + `tmp_path` files (`uv run pytest -m integration`)
  - Blackbox/E2E: pytest running the CLI as a process (`uv run pytest -m blackbox`); runs against the real device are manual
- Shell wrapper for commands: `fish -lc "..."` (see Terminal Execution Environment above)

---

## Quality Guidelines

### Modular Documentation Format
- Primary specification and backlog documentation format is AsciiDoc (`.adoc`).
- Asciidoctor-diagram syntax is supported for architectural diagrams.
- **Item-Level Modularization:** To optimize token usage and context clarity:
  - Master entry points reside at the root: `specification-web.adoc`, `tech-specification-web.adoc`, `backlog-web.adoc`, `release-notes.adoc`.
  - All split files reside in `specification/`, one subdirectory per master; each chapter is a folder:
    - Requirements: `specification/requirements/<NN-chapter>/<ID>-<slug>.adoc` (e.g. `FR-3.4-starting-mission.adoc`, `NFR-2-quality-gate.adoc`)
    - Technical Specifications: `specification/tech-specification/<NN-chapter>/<ID>-<slug>.adoc`
    - Backlog User Stories: `specification/backlog/<NN-chapter>/<ID>-<slug>.adoc`
    - Release Notes: `specification/release-notes/<version>.adoc`
    - Stakeholder input (`SPEC.md` sections): `specification/stakeholder/<NN>-<topic>.md`; `SPEC.md` is only an index, `SPEC.md §n` refers to file `<NN>`.
  - Master files include chapter indexes via `include::specification/<folder>/<NN-chapter>/index.adoc[]`; the chapter `index.adoc` holds the `==` heading, the chapter intro and one `include::<ID>-<slug>.adoc[]` per item (paths relative to the index).
  - Each item file starts with its anchor (`[#FR-x.y]`) and its `===` heading. A new item gets its own file plus an include line in the chapter index; a new chapter gets a folder, an `index.adoc` and an include in the master.
  - When researching or updating a specific item, load only its item file (find it by ID with `ls specification/*/*/<ID>-*`); load the chapter `index.adoc` only for the chapter intro.

### SMART Criteria
Every requirement and user story must be:
- **Specific**: Clearly and unambiguously stated.
- **Measurable**: Acceptance criteria are testable and verifiable.
- **Achievable**: Implementable within the project tech stack.
- **Relevant**: Traceable to stakeholder needs or parent requirements.
- **Time-bound**: Includes an effort estimate.

### Test Pyramid
| Level | Scope | Tooling | Usage |
|---|---|---|---|
| **Unit test** | Single functions, pure logic, detection on reference screenshots | pytest | Always, for pure logic/utilities |
| **Component test** | A single module in isolation, collaborators mocked or faked | pytest + `pytest-mock` | For every non-trivial module (flow, ADB wrapper) |
| **Integration test** | Configuration and state files, CLI in-process | pytest + `tmp_path` | For persistence / multi-module flows |
| **Blackbox test** | The CLI as a separate process | pytest + `subprocess` | `detect`, usage errors; device runs are manual |

### Reference Traceability
- Requirements reference stakeholder needs / constraints (`FR-x.y`, `NFR-x`).
- Technical specifications reference requirements (`FR-x.y`).
- User stories reference technical specifications and requirements (`TS-x.y`, `FR-x.y`).
- Any artifact change requires an impact analysis on downstream/upstream artifacts.
- Validate cross-references and includes with `uv run poe validate-specs`.

---

## Definition of Done (DoD)

An implementation task is complete ONLY when:
1. `uv run poe check` passes completely:
   - Full test suite passes (`uv run poe test`).
   - Type-checking passes without errors (`uv run poe typecheck`).
   - Lint and formatting pass without errors or warnings (`uv run poe lint`, `uv run poe format-check`).
   - Specification cross-references and includes validate cleanly (`uv run poe validate-specs`).
2. No `print()` debug statements, unused variables/imports, or leftover debug code remain.
3. Code adheres to existing architectural patterns and styling conventions.
4. `specification/release-notes/<version>.adoc` is updated with relevant Features, Fixes, or Breaking Changes and requirement traceability links.

---

## Commit Messages

Commits follow Conventional Commits (`feat(flow): …`, `fix(detect): …`) with `Refs:` footers to
the traced items. The format and the steps are in the [commit](.agents/skills/commit/SKILL.md)
skill; use it for every commit.

---

## Self-Correction & Debugging Protocol

- **Do Not Guess**: Read stack traces and error messages carefully before editing code.
- **Isolate**: Reproduce defects with a minimal automated test before modifying code.
- **Limit Loops**: If a test or build fails more than 3 times for the same reason, stop and ask the user for guidance.
- **Zero Unapproved Dependencies**: Do not add new dependencies (`uv add`) unless specified in the technical specification or requested by the user.

---

## Model-Specific Directives

- **Reasoning Models (Gemini Thinking, OpenAI o-series)**: Do not over-refactor outside requested scope. Omit conversational fluff and manual planning chatter in final responses; output direct technical results.
- **Claude Models**: Zero laziness policy (no placeholders). Match whitespace precisely when editing code.
- **GPT-4o Models**: Strictly adhere to tool schemas and verify file contents before editing.

---

## Toolchain Template (reference — copy into a new project's AGENTS.md)

Blank version of the block above, for the next project (Java, Python, Go, or otherwise). The shared skill library reads the `## Toolchain` heading generically, so any project that fills this in works with the same skills unchanged.

```
## Toolchain
- Ecosystem: <language / package manager, e.g. Java 21 / Maven, Python 3.12 / Poetry, Go 1.23>
- Quality gate command: <single command that runs tests + type-check/compile + lint>
- Spec validation command: <command that validates FR/TS/US anchors and include:: directives, if this project uses the modular AsciiDoc spec system>
- Dependency install: <command>
- Test pyramid mapping:
  - Unit: <tool>
  - Component: <tool, if applicable>
  - Integration: <tool>
  - Blackbox/E2E: <tool>
- Shell wrapper for commands (if any): <e.g. fish -lc "...">
```
