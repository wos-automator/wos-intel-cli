# Profile: Go / Task

- Ecosystem: Go 1.23, `go.mod`
- Task runner: [Task](https://taskfile.dev) (`Taskfile.yml`); a `Makefile` with the same target names is an equivalent alternative (`make <task>`)
- Run a contract task: `task <task>` (e.g. `task check`)
- Dependency install: `go mod download`; `go mod tidy` after import changes
- Add a dependency: `go get <module>` (only when approved)

## Contract Mapping

```yaml
tasks:
  lint:           { cmds: [golangci-lint run] }
  format-check:   { cmds: ["test -z \"$(gofmt -l .)\""] }
  typecheck:      { cmds: [go build ./...] }
  test:           { cmds: [go test ./... -race -cover, go test -tags=integration ./...] }
  validate-specs: { cmds: [go run ./tools/validate-specs] }
  check:          { cmds: [task: typecheck, task: lint, task: format-check, task: test, task: validate-specs] }
```

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | `testing` + `testify/assert`, table-driven | `go test ./...` |
| Component | `testify`, one package's public API with dependencies faked via interfaces | `go test ./<pkg>/...` |
| Integration | `testcontainers-go`, behind the `integration` build tag | `go test -tags=integration ./...` |
| Blackbox | `testscript` (`rogpeppe/go-internal`) for a CLI, Playwright-go for a web UI | per project, named in `AGENTS.md` |

## Debug Leftovers

- `fmt.Println` / `log.Println` used for debugging
- Unused imports or variables (the compiler rejects them), dead code
