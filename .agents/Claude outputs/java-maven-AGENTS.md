# Workspace Guidelines & Rules

> Sample AGENTS.md for a Java / Maven project — adjust project name, package paths, and chapter names before use.

## Terminal Execution Environment

If commands need a specific shell or login environment to resolve tools correctly (a version manager like SDKMAN or jenv, a non-default shell), document the exact wrapper command here, the same way a fish/PATH convention would be documented on another project. Omit this section entirely if the default shell resolves `mvn`/`java` correctly.

---

## Toolchain

> Machine-readable summary for agent skills (create-requirement, create-tech-specification, create-user-story, create-new-feature, update-requirement, definition-of-done, etc.). Keep this in sync with the sections below if commands ever change.

- Ecosystem: Java 21 / Maven
- Quality gate command: `mvn -B verify` (compiles, runs unit tests via Surefire, integration tests via Failsafe, and any static analysis bound to the `verify` phase)
- Spec validation command: `mvn -q exec:java@validate-specs` (a small validator class bound to a dedicated `exec-maven-plugin` execution, so it runs as part of `verify`)
- Dependency install: `mvn -B dependency:resolve` (or `mvn install`, which also builds)
- Test pyramid mapping:
  - Unit: JUnit 5 + Mockito (`mvn test`, via Surefire)
  - Component: JUnit 5 + Mockito, slice-style tests against a single class/package with collaborators mocked
  - Integration: JUnit 5 + Testcontainers, classes named `*IT.java`, run by Failsafe during `mvn verify`
  - Blackbox/E2E: REST Assured (API) or Selenium/Playwright-Java (UI), run via a dedicated Maven profile
- Shell wrapper for commands: none by default — Maven resolves its own toolchain via `JAVA_HOME`; add one only if a shell or version-manager quirk requires it

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
| **Integration test** | Persistence, service chains, external systems | JUnit 5 + Testcontainers (`*IT.java`, Failsafe) | For data layer / cross-service flows |
| **Blackbox test** | End-to-end critical journeys | REST Assured / Selenium / Playwright-Java | Critical user or API flows |

### Reference Traceability
- Requirements reference stakeholder needs / constraints (`FR-x.y`, `NFR-x`).
- Technical specifications reference requirements (`FR-x.y`).
- User stories reference technical specifications and requirements (`TS-x.y`, `FR-x.y`).
- Any artifact change requires an impact analysis on downstream/upstream artifacts.
- Validate cross-references and includes with `mvn -q exec:java@validate-specs`.

---

## Definition of Done (DoD)

An implementation task is complete ONLY when:
1. `mvn -B verify` passes completely:
   - Full test suite passes (unit + integration).
   - Compilation passes without errors.
   - Static analysis (Checkstyle/SpotBugs, or whatever this project binds to `verify`) passes without errors or warnings.
   - Specification cross-references and includes validate cleanly.
2. No `System.out.println`/leftover debug logging, unused variables, or dead code remain.
3. Code adheres to existing architectural patterns and styling conventions.
4. `docs/release-notes/<version>.adoc` is updated with relevant Features, Fixes, or Breaking Changes and requirement traceability links.

---

## Self-Correction & Debugging Protocol

- **Do Not Guess**: Read stack traces and error messages carefully before editing code.
- **Isolate**: Reproduce defects with a minimal automated test before modifying code.
- **Limit Loops**: If a test or build fails more than 3 times for the same reason, stop and ask the user for guidance.
- **Zero Unapproved Dependencies**: Do not add new Maven dependencies unless specified in the technical specification or requested by the user.

---

## Model-Specific Directives

- **Reasoning Models (Gemini Thinking, OpenAI o-series)**: Do not over-refactor outside requested scope. Omit conversational fluff and manual planning chatter in final responses; output direct technical results.
- **Claude Models**: Zero laziness policy (no placeholders). Match whitespace precisely when editing code.
- **GPT-4o Models**: Strictly adhere to tool schemas and verify file contents before editing.
