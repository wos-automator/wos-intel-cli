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
  test:           { cmds: [mkdir -p build/test, "go run gotest.tools/gotestsum@v1.13.0 --junitfile build/test/junit.xml -- ./... -race -cover", "go run gotest.tools/gotestsum@v1.13.0 --junitfile build/test/junit-integration.xml -- -tags=integration ./..."] }
  validate-specs: { cmds: [.agents/skills/spec-system/bin/validate-specs] }
  check:          { cmds: [task: typecheck, task: lint, task: format-check, task: test, task: validate-specs] }
```

- Test durations: `gotestsum` runs `go test` and writes the time of every test to `build/test/junit*.xml`; it is run with `go run` at a pinned version, not added to `go.mod`. `build/` belongs in `.gitignore`.

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | `testing` + `testify/assert`, table-driven | `go test ./...` |
| Component | `testify`, one package's public API with dependencies faked via interfaces | `go test ./<pkg>/...` |
| Integration | `testcontainers-go`, behind the `integration` build tag | `go test -tags=integration ./...` |
| Blackbox | `testscript` (`rogpeppe/go-internal`) for a CLI, Playwright-go for a web UI | per project, named in `AGENTS.md` |

## BDT

Only for requirements-based blackbox testing (see [spec-system](../../spec-system/SKILL.md), BDT): [godog](https://github.com/cucumber/godog) runs the feature files from `go test` and writes Cucumber JSON.

- Module: `github.com/cucumber/godog` (`go get`, only when the user approved BDT).
- The scenarios live in a test package `bdt/` behind the build tag `bdt`, so that `test` does not run them; its steps drive the built product from outside (`os/exec` for a CLI, `net/http` for an API).
- Task: `bdt: { cmds: [mkdir -p build/bdt, go test -tags=bdt ./bdt/...] }`.

```go
//go:build bdt

func TestAcceptance(t *testing.T) {
	suite := godog.TestSuite{
		ScenarioInitializer: initializeScenario, // sc.Step(`^I greet "([^"]*)"$`, …)
		Options: &godog.Options{
			Format:   "cucumber:../build/bdt/cucumber.json,pretty",
			Paths:    []string{"../specification/acceptance"},
			TestingT: t,
			Strict:   true, // undefined and pending steps fail
		},
	}
	if suite.Run() != 0 {
		t.Fatal("acceptance scenarios failed")
	}
}
```

- The Cucumber JSON carries tags with `@`, the feature's tags on every scenario, and URIs relative to the test package; spec-validator matches by test ID only.

## Debug Leftovers

- `fmt.Println` / `log.Println` used for debugging
- Unused imports or variables (the compiler rejects them), dead code

## Release

- `version`: none; the tag is the version, passed to the binary with `-ldflags "-X main.version=…"`.
- `dist`: `goreleaser release --clean --skip=publish` with `checksum: disable: true` in `.goreleaser.yaml` (publish-release writes the checksums over all assets); archives land in `dist/`.

Pull Request steps (job `check` of the pull request template):

```yaml
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - uses: golangci/golangci-lint-action@v8
      - uses: arduino/setup-task@v2
        with:
          version: 3.x
          repo-token: ${{ secrets.GITHUB_TOKEN }}
      - run: task check
      # BDT only:
      - run: task bdt
```

Release Build steps:

```yaml
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - uses: golangci/golangci-lint-action@v8
      - uses: arduino/setup-task@v2
        with:
          version: 3.x
          repo-token: ${{ secrets.GITHUB_TOKEN }}
      - run: task typecheck format-check test validate-specs
      # BDT only:
      - run: task bdt
      - uses: goreleaser/goreleaser-action@v6
        with:
          version: "~> v2"
          args: release --clean --skip=publish
      - run: mkdir archives && mv dist/*.tar.gz dist/*.zip archives/ && rm -rf dist && mv archives dist
```
