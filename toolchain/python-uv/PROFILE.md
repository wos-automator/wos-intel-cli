# Profile: Python / uv

- Ecosystem: Python 3.11+, `pyproject.toml`, `uv.lock`
- Task runner: [poethepoet](https://poethepoet.natn.io) as a dev dependency, tasks under `[tool.poe.tasks]`
- Run a contract task: `uv run poe <task>` (e.g. `uv run poe check`)
- Dependency install: `uv sync`
- Add a dependency: `uv add <pkg>` / `uv add --group dev <pkg>` (only when approved)

## Contract Mapping

```toml
[tool.poe.tasks]
lint = "ruff check ."
format-check = "ruff format --check ."
typecheck = "mypy"
test = "pytest"
validate-specs = ".agents/skills/spec-system/bin/validate-specs"
check = ["lint", "format-check", "typecheck", "test", "validate-specs"]
```

## Test Pyramid Tooling

Levels are pytest markers, registered under `[tool.pytest.ini_options] markers` with `--strict-markers`.

| Level | Tooling | Run one level |
|---|---|---|
| Unit | pytest | `uv run pytest -m unit` |
| Component | pytest + `pytest-mock`, collaborators mocked or faked | `uv run pytest -m component` |
| Integration | pytest + `tmp_path` (files), `testcontainers-python` (services) | `uv run pytest -m integration` |
| Blackbox | pytest + `subprocess` (CLI), `pytest-playwright` (web UI) or `httpx` (API) | `uv run pytest -m blackbox` |

## Debug Leftovers

- `print()` (ruff rule `T20` catches it), `breakpoint()`, `pdb` imports
- Unused imports and variables (ruff `F`)
- `# type: ignore` without an error code

## Release

- `version`: `uv version --short`; the version is `[project] version` in `pyproject.toml`.
- `dist`: `uv build` (sdist and wheel into `dist/`), as poe tasks `version` and `dist`.

Release Build steps:

```yaml
      - uses: astral-sh/setup-uv@v6
      - run: uv sync
      - run: uv run poe check
      - run: test "$(uv version --short)" = "${{ needs.verify.outputs.version }}"
      - run: uv run poe dist
```
