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

- Test durations: every test task writes the time of every test to `build/test-results/<task>/` (`TEST-*.xml`) and `build/reports/tests/<task>/` by default; do not switch the reports off.

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | JUnit 5 + Mockito | `./gradlew test` |
| Component | JUnit 5 + Mockito, one class or package with collaborators mocked | `./gradlew test --tests '<Pattern>'` |
| Integration | JUnit 5 + Testcontainers, source set `src/integrationTest` | `./gradlew integrationTest` |
| Blackbox | REST Assured (API), Selenium/Playwright-Java (UI), source set `src/e2eTest` | `./gradlew e2eTest` |

- `integrationTest` and `e2eTest` are JVM test suites (`testing { suites { register<JvmTestSuite>("e2eTest") { … } } }`), each with its source set and a test task of the same name; `check` does not run them, but compiles, lints and format-checks their sources.
- Blackbox tests run against the packaged artifact; the build passes its path as a system property, with the jar as task input:

```kotlin
targets.all {
    testTask.configure {
        val commandJar = tasks.jar.flatMap { it.archiveFile }
        inputs.file(commandJar).withPathSensitivity(PathSensitivity.NONE)
        jvmArgumentProviders.add(CommandLineArgumentProvider { listOf("-Dcommand.jar=${commandJar.get().asFile}") })
    }
}
```

## BDT

Only for requirements-based blackbox testing (see [spec-system](../../spec-system/SKILL.md), BDT): [Cucumber-JVM](https://github.com/cucumber/cucumber-jvm) runs the feature files on the JUnit Platform and writes Cucumber JSON.

- Task: `bdt`, the test task of a JVM test suite `bdt` (sources in `src/bdt/java`), configured against the packaged artifact like the blackbox tests above; not part of `check`. The steps drive the product from outside (`ProcessBuilder` for a CLI, an HTTP client for an API, Playwright-Java for a web UI).
- Dependencies of the suite; the `json` plugin of Cucumber 8 needs a JSON library on its classpath:

```kotlin
register<JvmTestSuite>("bdt") {
    useJUnitJupiter()
    dependencies {
        implementation(platform("io.cucumber:cucumber-bom:<version>"))
        implementation("io.cucumber:cucumber-java")
        implementation("io.cucumber:cucumber-junit-platform-engine")
        implementation("org.junit.platform:junit-platform-suite")
        implementation("tools.jackson.core:jackson-databind:<version>")
    }
}
```

- One suite class in the package `bdt` binds all scenarios; the working directory of the test task is the project folder:

```java
@Suite
@IncludeEngines("cucumber")
@SelectDirectories("specification/acceptance")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "<package>.bdt")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME, value = "json:build/bdt/cucumber.json,pretty")
class RunAcceptanceTest {}
```

- The Cucumber JSON carries tags with `@` and URIs `file:specification/…`; spec-validator matches by test ID only.

## Debug Leftovers

- `System.out.println` / `System.err.println`, `printStackTrace()`
- Unused imports, commented-out code

## Release

- `version`: `./gradlew -q properties --property version | sed -n 's/^version: //p'` (Gradle 9 prints a header before the property); the version is `version` in `build.gradle.kts` or `gradle.properties`.
- `dist`: `./gradlew assemble`, then copy `build/libs/*.jar` to `dist/`.

Pull Request steps (job `check` of the pull request template):

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew check
      # BDT only:
      - run: ./gradlew bdt
```

Release Build steps (the version check is a block scalar: `version: ` in a plain scalar is not valid YAML):

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew check
      - run: |
          test "$(./gradlew -q properties --property version | sed -n 's/^version: //p')" = "${{ needs.verify.outputs.version }}"
      - run: ./gradlew assemble && mkdir -p dist && cp build/libs/*.jar dist/
      # BDT only:
      - run: ./gradlew bdt
```
