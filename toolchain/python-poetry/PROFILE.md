# Profile: Python / Poetry

- Ecosystem: Python 3.12, `pyproject.toml`, `poetry.lock`
- Task runner: [poethepoet](https://poethepoet.natn.io) as a dev dependency (`poetry add --group dev poethepoet`), tasks under `[tool.poe.tasks]`
- Run a contract task: `poetry run poe <task>` (e.g. `poetry run poe check`)
- Dependency install: `poetry install`
- Add a dependency: `poetry add <pkg>` / `poetry add --group dev <pkg>` (only when approved)

## Contract Mapping

```toml
[tool.poe.tasks]
lint = "ruff check ."
format-check = "ruff format --check ."
typecheck = "mypy ."
test = "pytest"
validate-specs = ".agents/skills/spec-system/bin/validate-specs"
check = ["lint", "format-check", "typecheck", "test", "validate-specs"]
```

## Test Pyramid Tooling

Levels are pytest markers, registered under `[tool.pytest.ini_options] markers` with `--strict-markers`.

| Level | Tooling | Run one level |
|---|---|---|
| Unit | pytest | `poetry run pytest -m unit` |
| Component | pytest + `pytest-mock`, a single module or class with collaborators mocked | `poetry run pytest -m component` |
| Integration | pytest + `tmp_path` (files), `testcontainers-python` (services) | `poetry run pytest -m integration` |
| Blackbox | pytest + `subprocess` (CLI), `pytest-playwright` (web UI) or `httpx` (API) | `poetry run pytest -m blackbox` |

## Debug Leftovers

- `print()` (ruff rule `T20` catches it), `breakpoint()`, `pdb` imports
- Unused imports and variables (ruff `F`)
- `# type: ignore` without an error code

## Release

- `version`: `poetry version --short`; the version is `[project] version` (or `[tool.poetry] version`) in `pyproject.toml`.
- `dist`: `poetry build` (sdist and wheel into `dist/`), as poe tasks `version` and `dist`.

Release Build steps:

```yaml
      - run: pipx install poetry
      - run: poetry install
      - run: poetry run poe check
      - run: test "$(poetry version --short)" = "${{ needs.verify.outputs.version }}"
      - run: poetry run poe dist
```
