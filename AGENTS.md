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
- **Chapter-Level Modularization:** To optimize token usage and context clarity:
  - Master entry points reside at the root: `specification-web.adoc`, `tech-specification-web.adoc`, `backlog-web.adoc`, `release-notes.adoc`.
  - Feature/domain chapters reside in subdirectories:
    - Requirements: `docs/specifications/<chapter>.adoc`
    - Technical Specifications: `docs/tech-specifications/<chapter>.adoc`
    - Backlog User Stories: `docs/backlog/<chapter>.adoc`
    - Release Notes: `docs/release-notes/<version>.adoc`
  - Master files include chapters via `include::docs/<folder>/<chapter>.adoc[]`.
  - When researching or updating a specific feature, load only its respective chapter files to conserve context window tokens.

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
4. `docs/release-notes/<version>.adoc` is updated with relevant Features, Fixes, or Breaking Changes and requirement traceability links.

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
