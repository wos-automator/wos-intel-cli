# Workspace Guidelines & Rules

> Sample AGENTS.md for a Go project — adjust project name, module path, and chapter names before use.

## Terminal Execution Environment

If commands need a specific shell or login environment to resolve tools correctly (a Go version manager like `asdf` or `gvm`, a non-default shell), document the exact wrapper command here. Usually unnecessary — Go's own tooling resolves via `GOROOT`/`GOPATH`/`GOBIN` rather than a login shell config — so omit this section unless something else in the environment needs it.

---

## Toolchain

> Machine-readable summary for agent skills (create-requirement, create-tech-specification, create-user-story, create-new-feature, update-requirement, definition-of-done, etc.). Keep this in sync with the sections below if commands ever change.
>
> Build tool: [Task](https://taskfile.dev) (`Taskfile.yml`), chosen over a bare Makefile for cross-platform consistency and a readable YAML syntax close to the `npm run <script>` pattern this convention is modeled on. A Makefile is an equally valid zero-extra-dependency alternative — the `check`/`validate-specs` targets below map onto it 1:1 if preferred.

- Ecosystem: Go 1.23 / Task (`Taskfile.yml`) + `go.mod`
- Quality gate command: `task check` (runs `go build ./...`, `golangci-lint run`, `go test ./... -race -cover`, and spec validation, in that order)
- Spec validation command: `task validate-specs` → `go run ./tools/validate-specs`
- Dependency install: `go mod tidy`
- Test pyramid mapping:
  - Unit: standard `testing` package + `testify/assert` (`go test ./...`)
  - Component: `testify`, table-driven tests against a single package's public API with dependencies faked via interfaces
  - Integration: `testcontainers-go`, gated behind a `integration` build tag (`go test -tags=integration ./...`, wired into `task check`)
  - Blackbox/E2E: Playwright-go for a web UI, or `testscript` (`rogpeppe/go-internal/testscript`) for a CLI tool — pick whichever matches the project's shape
- Shell wrapper for commands: none by default; add one only if a Go version manager needs a login-shell PATH

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
| **Unit test** | Single functions, pure logic | `testing` + `testify/assert` | Always, for pure logic/utilities |
| **Component test** | A single package's public API, dependencies faked via interfaces | `testify`, table-driven | For every non-trivial package |
| **Integration test** | Persistence, service chains, external systems | `testcontainers-go` (`integration` build tag) | For data layer / cross-service flows |
| **Blackbox test** | End-to-end critical journeys | Playwright-go (web) or `testscript` (CLI) | Critical user or API flows |

### Reference Traceability
- Requirements reference stakeholder needs / constraints (`FR-x.y`, `NFR-x`).
- Technical specifications reference requirements (`FR-x.y`).
- User stories reference technical specifications and requirements (`TS-x.y`, `FR-x.y`).
- Any artifact change requires an impact analysis on downstream/upstream artifacts.
- Validate cross-references and includes with `task validate-specs`.

---

## Definition of Done (DoD)

An implementation task is complete ONLY when:
1. `task check` passes completely:
   - Full test suite passes, run with `-race`.
   - `go build ./...` compiles without errors.
   - `golangci-lint run` passes without errors or warnings.
   - Specification cross-references and includes validate cleanly.
2. No `fmt.Println`/`log.Println` debug leftovers, unused imports, or dead code remain.
3. Code adheres to existing architectural patterns and styling conventions.
4. `docs/release-notes/<version>.adoc` is updated with relevant Features, Fixes, or Breaking Changes and requirement traceability links.

---

## Self-Correction & Debugging Protocol

- **Do Not Guess**: Read stack traces and error messages carefully before editing code.
- **Isolate**: Reproduce defects with a minimal automated test before modifying code.
- **Limit Loops**: If a test or build fails more than 3 times for the same reason, stop and ask the user for guidance.
- **Zero Unapproved Dependencies**: Do not run `go get` to add new modules unless specified in the technical specification or requested by the user.

---

## Model-Specific Directives

- **Reasoning Models (Gemini Thinking, OpenAI o-series)**: Do not over-refactor outside requested scope. Omit conversational fluff and manual planning chatter in final responses; output direct technical results.
- **Claude Models**: Zero laziness policy (no placeholders). Match whitespace precisely when editing code.
- **GPT-4o Models**: Strictly adhere to tool schemas and verify file contents before editing.
