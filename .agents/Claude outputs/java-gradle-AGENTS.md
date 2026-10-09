# Workspace Guidelines & Rules

> Sample AGENTS.md for a Java / Gradle project — adjust project name, package paths, and chapter names before use.

## Terminal Execution Environment

If commands need a specific shell or login environment to resolve tools correctly (a version manager like SDKMAN, a non-default shell), document the exact wrapper command here. Usually unnecessary with Gradle, since the wrapper script (`./gradlew`) pins its own Gradle version and resolves `JAVA_HOME` itself — omit this section unless something else in the environment needs it.

---

## Toolchain

> Machine-readable summary for agent skills (create-requirement, create-tech-specification, create-user-story, create-new-feature, update-requirement, definition-of-done, etc.). Keep this in sync with the sections below if commands ever change.

- Ecosystem: Java 21 / Gradle (Kotlin DSL)
- Quality gate command: `./gradlew check` (Gradle's built-in `check` lifecycle task — runs `test` plus any verification tasks wired into it, e.g. Checkstyle/SpotBugs/ktlint)
- Spec validation command: `./gradlew validateSpecs` (a custom task that checks anchors and `include::` directives resolve)
- Dependency install: implicit — Gradle resolves dependencies on first task run; use `./gradlew dependencies` to pre-fetch without building
- Test pyramid mapping:
  - Unit: JUnit 5 + Mockito (`./gradlew test`)
  - Component: JUnit 5 + Mockito, slice-style tests against a single class/package with collaborators mocked
  - Integration: JUnit 5 + Testcontainers, in a separate `src/integrationTest` source set, run via `./gradlew integrationTest` (wired into `check`)
  - Blackbox/E2E: Selenium/Playwright-Java or REST Assured, in a separate `src/e2eTest` source set, run via `./gradlew e2eTest`
- Shell wrapper for commands: none by default — always invoke via the wrapper (`./gradlew`, not a bare `gradle`)

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
| **Unit test** | Single methods, validators, pure logic | JUnit 5 + Mockito | Always, for pure logic/utilities |
| **Component test** | A single class/package in isolation, collaborators mocked | JUnit 5 + Mockito | For every non-trivial component |
| **Integration test** | Persistence, service chains, external systems | JUnit 5 + Testcontainers (`integrationTest` source set) | For data layer / cross-service flows |
| **Blackbox test** | End-to-end critical journeys | REST Assured / Selenium / Playwright-Java (`e2eTest` source set) | Critical user or API flows |

### Reference Traceability
- Requirements reference stakeholder needs / constraints (`FR-x.y`, `NFR-x`).
- Technical specifications reference requirements (`FR-x.y`).
- User stories reference technical specifications and requirements (`TS-x.y`, `FR-x.y`).
- Any artifact change requires an impact analysis on downstream/upstream artifacts.
- Validate cross-references and includes with `./gradlew validateSpecs`.

---

## Definition of Done (DoD)

An implementation task is complete ONLY when:
1. `./gradlew check` passes completely:
   - Full test suite passes (unit + integration + e2e, whichever are wired into `check`).
   - Compilation passes without errors.
   - Static analysis (Checkstyle/SpotBugs/ktlint, whatever this project binds to `check`) passes without errors or warnings.
   - Specification cross-references and includes validate cleanly.
2. No `System.out.println`/leftover debug logging, unused variables, or dead code remain.
3. Code adheres to existing architectural patterns and styling conventions.
4. `docs/release-notes/<version>.adoc` is updated with relevant Features, Fixes, or Breaking Changes and requirement traceability links.

---

## Self-Correction & Debugging Protocol

- **Do Not Guess**: Read stack traces and error messages carefully before editing code.
- **Isolate**: Reproduce defects with a minimal automated test before modifying code.
- **Limit Loops**: If a test or build fails more than 3 times for the same reason, stop and ask the user for guidance.
- **Zero Unapproved Dependencies**: Do not add new Gradle dependencies unless specified in the technical specification or requested by the user.

---

## Model-Specific Directives

- **Reasoning Models (Gemini Thinking, OpenAI o-series)**: Do not over-refactor outside requested scope. Omit conversational fluff and manual planning chatter in final responses; output direct technical results.
- **Claude Models**: Zero laziness policy (no placeholders). Match whitespace precisely when editing code.
- **GPT-4o Models**: Strictly adhere to tool schemas and verify file contents before editing.
