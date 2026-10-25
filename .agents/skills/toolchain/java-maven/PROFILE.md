# Profile: Java / Maven

- Ecosystem: Java 21, `pom.xml`; use the wrapper `./mvnw` when the project has one, `mvn` otherwise
- Task runner: Maven lifecycle phases and plugin executions; always pass `-B` (batch mode)
- Dependency install: `mvn -B dependency:resolve`
- Add a dependency: edit `pom.xml` (only when approved)

## Contract Mapping

| Task | Command |
|---|---|
| `check` | `mvn -B verify` (compile, Surefire, Failsafe, analysis and spec validation bound to `verify`) |
| `test` | `mvn -B test` |
| `lint` | `mvn -B checkstyle:check spotbugs:check` (or whatever analysis the `pom.xml` binds) |
| `format-check` | `mvn -B spotless:check` |
| `typecheck` | `mvn -B compile` |
| `validate-specs` | `mvn -B -q exec:exec@validate-specs` (an `exec-maven-plugin` execution running `.agents/skills/spec-system/bin/validate-specs`, bound to `verify`) |

- Test durations: Surefire and Failsafe write the time of every test to `target/surefire-reports/` and `target/failsafe-reports/` (`TEST-*.xml`) by default; do not switch the reports off.

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | JUnit 5 + Mockito, via Surefire | `mvn -B test` |
| Component | JUnit 5 + Mockito, one class or package with collaborators mocked | `mvn -B test -Dtest='<Pattern>'` |
| Integration | JUnit 5 + Testcontainers, classes named `*IT.java`, via Failsafe | `mvn -B verify -DskipUTs` (if configured) |
| Blackbox | REST Assured (API), Selenium/Playwright-Java (UI), in a Maven profile | `mvn -B verify -P e2e` |

- Blackbox tests run with Failsafe against the packaged artifact (`integration-test` comes after `package`); the build passes its path as a system property, e.g. `<command.jar>${project.build.directory}/${project.build.finalName}.jar</command.jar>` under `systemPropertyVariables`. Surefire excludes their packages (`**/blackbox/**`, `**/bdt/**`).
- With Checkstyle's `google_checks.xml`, the suffix `IT` counts as an abbreviation; name such classes `…Test` in their own package instead.

## BDT

Only for requirements-based blackbox testing (see [spec-system](../../spec-system/SKILL.md), BDT): [Cucumber-JVM](https://github.com/cucumber/cucumber-jvm) runs the feature files on the JUnit Platform and writes Cucumber JSON.

- Test dependencies: the BOM `io.cucumber:cucumber-bom` (import), `io.cucumber:cucumber-java`, `io.cucumber:cucumber-junit-platform-engine`, `org.junit.platform:junit-platform-suite`. The `json` plugin of Cucumber 8 needs a JSON library on the test classpath: `tools.jackson.core:jackson-databind`.
- Task: `bdt` = `mvn -B verify -P bdt`; the profile `bdt` runs the suite class with Failsafe against the packaged artifact, as the blackbox tests above. `test` does not run it (Surefire excludes `**/bdt/**`). The steps drive the product from outside (`ProcessBuilder` for a CLI, an HTTP client for an API, Playwright-Java for a web UI).
- One suite class in the test package `bdt` binds all scenarios; the report goes to `build/bdt/`, as in every profile, although Maven builds into `target/`:

```java
@Suite
@IncludeEngines("cucumber")
@SelectDirectories("specification/acceptance")
@ConfigurationParameter(key = GLUE_PROPERTY_NAME, value = "<package>.bdt")
@ConfigurationParameter(key = PLUGIN_PROPERTY_NAME, value = "json:build/bdt/cucumber.json,pretty")
class RunAcceptanceTest {}
```

```xml
<profile>
  <id>bdt</id>
  <build>
    <plugins>
      <plugin>
        <artifactId>maven-failsafe-plugin</artifactId>
        <configuration>
          <includes>
            <include>**/bdt/RunAcceptanceTest.java</include>
          </includes>
        </configuration>
        <executions>
          <execution>
            <goals>
              <goal>integration-test</goal>
              <goal>verify</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>
</profile>
```

- The Cucumber JSON carries tags with `@` and URIs `file:specification/…`; spec-validator matches by test ID only.

## Debug Leftovers

- `System.out.println` / `System.err.println`, `printStackTrace()`
- Unused imports, commented-out code

## Release

- `version`: `mvn -B -q help:evaluate -Dexpression=project.version -DforceStdout`; the version is `<version>` in `pom.xml`.
- `dist`: `mvn -B package -DskipTests`, then copy `target/*.jar` to `dist/`.

Pull Request steps (job `check` of the pull request template):

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
          cache: maven
      - run: mvn -B verify
      # BDT only:
      - run: mvn -B verify -P bdt
```

Release Build steps:

```yaml
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "21"
          cache: maven
      - run: mvn -B verify
      - run: test "$(mvn -B -q help:evaluate -Dexpression=project.version -DforceStdout)" = "${{ needs.verify.outputs.version }}"
      - run: mkdir -p dist && cp target/*.jar dist/
      # BDT only:
      - run: mvn -B verify -P bdt
```
