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
test = "pytest --junitxml=build/test/junit.xml --durations=10"
validate-specs = ".agents/skills/spec-system/bin/validate-specs"
check = ["lint", "format-check", "typecheck", "test", "validate-specs"]
```

- Coverage runs with the tests: `pytest-cov` and `addopts = ["--strict-markers", "--cov=<package>", "--cov-fail-under=<n>"]`; set `<n>` to today's value, rounded down, raise it when coverage grows and never lower it to make a change pass. Code that runs only as a separate process (`__main__.py`) is omitted under `[tool.coverage.run]`.
- Test durations: `--junitxml` writes the time of every test to `build/test/junit.xml`, `--durations=10` prints the ten slowest; `build/` belongs in `.gitignore`.
- Ruff leaves out the vendored library: `extend-exclude = [".agents"]` under `[tool.ruff]`. Recent ruff versions also format the Python examples in Markdown files, and the library is not the project's code.

## Test Pyramid Tooling

Levels are pytest markers, registered under `[tool.pytest.ini_options] markers` with `--strict-markers`.

| Level | Tooling | Run one level |
|---|---|---|
| Unit | pytest | `poetry run pytest -m unit` |
| Component | pytest + `pytest-mock`, a single module or class with collaborators mocked | `poetry run pytest -m component` |
| Integration | pytest + `tmp_path` (files), `testcontainers-python` (services) | `poetry run pytest -m integration` |
| Blackbox | pytest + `subprocess` (CLI), `pytest-playwright` (web UI) or `httpx` (API) | `poetry run pytest -m blackbox` |

## BDT

Only for requirements-based blackbox testing (see [spec-system](../../spec-system/SKILL.md), BDT): [pytest-bdd](https://pytest-bdd.readthedocs.io) runs the feature files and writes Cucumber JSON.

- Dev dependency: `pytest-bdd`; marker `bdt` under `markers`; the `test` task deselects it (`pytest -m 'not bdt' --junitxml=build/test/junit.xml --durations=10`).
- Task: `bdt = { shell = "mkdir -p build/bdt && pytest -m bdt --no-cov --cucumberjson=build/bdt/cucumber.json" }`. pytest-bdd does not create the folder of its report; `--no-cov`, because the product runs as a separate process.
- `tests/bdt/test_acceptance.py` binds all scenarios: `pytestmark = pytest.mark.bdt` and `scenarios("../../specification/acceptance")`; the steps live in `tests/bdt/conftest.py` and drive the product from outside (`subprocess` for a CLI, `pytest-playwright` for a web UI, `httpx` for an API).
- pytest-bdd turns tags into markers; with `--strict-markers`, test IDs and trace tags must not become markers:

```python
_ID = re.compile(r"[A-Z][A-Z0-9]*-\d+(\.\d+)*")


def pytest_bdd_apply_tag(tag: str, function: Callable[..., Any]) -> bool | None:
    return True if _ID.fullmatch(tag) else None
```

- The Cucumber JSON carries tags without `@` and URIs relative to the features folder; spec-validator reads both forms.

## Debug Leftovers

- `print()` (ruff rule `T20` catches it), `breakpoint()`, `pdb` imports
- Unused imports and variables (ruff `F`)
- `# type: ignore` without an error code

## Release

- `version`: `poetry version --short`; the version is `[project] version` (or `[tool.poetry] version`) in `pyproject.toml`.
- `dist`: `poetry build` (sdist and wheel into `dist/`), as poe tasks `version` and `dist`.

Pull Request steps (job `check` of the pull request template):

```yaml
      - run: pipx install poetry
      - run: poetry install
      - run: poetry run poe check
      # BDT only:
      - run: poetry run poe bdt
```

Release Build steps:

```yaml
      - run: pipx install poetry
      - run: poetry install
      - run: poetry run poe check
      - run: test "$(poetry version --short)" = "${{ needs.verify.outputs.version }}"
      - run: poetry run poe dist
      # BDT only:
      - run: poetry run poe bdt
```
