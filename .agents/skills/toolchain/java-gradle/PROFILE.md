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
| `validate-specs` | `validateSpecs` (an `Exec` task running `.agents/skills/spec-system/bin/validate-specs`) |

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

## Release

- `version`: `./gradlew -q properties --property version | sed 's/^version: //'`; the version is `version` in `build.gradle.kts` or `gradle.properties`.
- `dist`: `./gradlew assemble`, then copy `build/libs/*.jar` to `dist/`.

Release Build steps:

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew check
      - run: test "$(./gradlew -q properties --property version | sed 's/^version: //')" = "${{ needs.verify.outputs.version }}"
      - run: ./gradlew assemble && mkdir -p dist && cp build/libs/*.jar dist/
```
