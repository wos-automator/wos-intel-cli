# Profile: Java / Gradle

- Ecosystem: Java 21, Gradle with Kotlin DSL (`build.gradle.kts`)
- Task runner: Gradle; always the wrapper `./gradlew`, never a bare `gradle`
- Run a contract task: `./gradlew <task>`; contract names in camelCase (`formatCheck`, `validateSpecs`)
- Dependency install: implicit on the first task run; `./gradlew dependencies` pre-fetches
- Add a dependency: edit `build.gradle.kts` (only when approved)

## Contract Mapping

| Task | Gradle task |
|---|---|
| `check` | `check` (built-in lifecycle task; wire every task below into it with `dependsOn`) |
| `test` | `test` (+ `integrationTest`) |
| `lint` | `checkstyleMain`, `spotbugsMain` or the project's analysis |
| `format-check` | `spotlessCheck` |
| `typecheck` | `compileJava` / `classes` |
| `validate-specs` | `validateSpecs` (custom task checking anchors and `include::` directives) |

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | JUnit 5 + Mockito | `./gradlew test` |
| Component | JUnit 5 + Mockito, one class or package with collaborators mocked | `./gradlew test --tests '<Pattern>'` |
| Integration | JUnit 5 + Testcontainers, source set `src/integrationTest` | `./gradlew integrationTest` |
| Blackbox | REST Assured (API), Selenium/Playwright-Java (UI), source set `src/e2eTest` | `./gradlew e2eTest` |

## Debug Leftovers

- `System.out.println` / `System.err.println`, `printStackTrace()`
- Unused imports, commented-out code
