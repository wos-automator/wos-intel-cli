# Workspace Guidelines & Rules

> Sample AGENTS.md for a Python / Poetry (pyproject.toml) project — adjust project name, package paths, and chapter names before use.

## Terminal Execution Environment

If commands need a specific shell or login environment to resolve tools correctly (a Python version manager like `pyenv` or `asdf`, a non-default shell), document the exact wrapper command here. Usually unnecessary — Poetry manages its own virtualenv and resolves `python`/dependencies inside it regardless of shell — so omit this section unless something else in the environment needs it.

---

## Toolchain

> Machine-readable summary for agent skills (create-requirement, create-tech-specification, create-user-story, create-new-feature, update-requirement, definition-of-done, etc.). Keep this in sync with the sections below if commands ever change.
>
> Requires `poethepoet` as a dev dependency (`poetry add --group dev poethepoet`) with tasks declared under `[tool.poe.tasks]` in `pyproject.toml`, so a single command can chain lint, format, type-check, test, and spec validation the same way `npm run check` does.

- Ecosystem: Python 3.12 / Poetry (`pyproject.toml`)
- Quality gate command: `poetry run poe check` (chains `ruff check`, `ruff format --check`, `mypy .`, `pytest`, and spec validation)
- Spec validation command: `poetry run poe validate-specs` → `python scripts/validate_specs.py`
- Dependency install: `poetry install`
- Test pyramid mapping:
  - Unit: pytest (`poetry run pytest -m unit`)
  - Component: pytest + `pytest-mock`, a single module/class with collaborators mocked
  - Integration: pytest + `testcontainers-python` (`poetry run pytest -m integration`)
  - Blackbox/E2E: `pytest-playwright` (web UI) or `httpx`-based black-box API tests
- Shell wrapper for commands: none by default; add one only if a Python version manager needs a login-shell PATH

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
| **Unit test** | Single functions, pure logic | pytest | Always, for pure logic/utilities |
| **Component test** | A single module/class in isolation, collaborators mocked | pytest + `pytest-mock` | For every non-trivial component |
| **Integration test** | Persistence, service chains, external systems | pytest + `testcontainers-python` | For data layer / cross-service flows |
| **Blackbox test** | End-to-end critical journeys | `pytest-playwright` / `httpx` black-box API tests | Critical user or API flows |

### Reference Traceability
- Requirements reference stakeholder needs / constraints (`FR-x.y`, `NFR-x`).
- Technical specifications reference requirements (`FR-x.y`).
- User stories reference technical specifications and requirements (`TS-x.y`, `FR-x.y`).
- Any artifact change requires an impact analysis on downstream/upstream artifacts.
- Validate cross-references and includes with `poetry run poe validate-specs`.

---

## Definition of Done (DoD)

An implementation task is complete ONLY when:
1. `poetry run poe check` passes completely:
   - Full test suite passes (`pytest`).
   - Type-checking passes without errors (`mypy .`).
   - Lint and formatting pass without errors or warnings (`ruff check`, `ruff format --check`).
   - Specification cross-references and includes validate cleanly.
2. No `print()` debug statements, unused variables/imports (flagged by `ruff`), or dead code remain.
3. Code adheres to existing architectural patterns and styling conventions.
4. `docs/release-notes/<version>.adoc` is updated with relevant Features, Fixes, or Breaking Changes and requirement traceability links.

---

## Self-Correction & Debugging Protocol

- **Do Not Guess**: Read stack traces and error messages carefully before editing code.
- **Isolate**: Reproduce defects with a minimal automated test before modifying code.
- **Limit Loops**: If a test or build fails more than 3 times for the same reason, stop and ask the user for guidance.
- **Zero Unapproved Dependencies**: Do not run `poetry add` for new dependencies unless specified in the technical specification or requested by the user.

---

## Model-Specific Directives

- **Reasoning Models (Gemini Thinking, OpenAI o-series)**: Do not over-refactor outside requested scope. Omit conversational fluff and manual planning chatter in final responses; output direct technical results.
- **Claude Models**: Zero laziness policy (no placeholders). Match whitespace precisely when editing code.
- **GPT-4o Models**: Strictly adhere to tool schemas and verify file contents before editing.
