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

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | JUnit 5 + Mockito, via Surefire | `mvn -B test` |
| Component | JUnit 5 + Mockito, one class or package with collaborators mocked | `mvn -B test -Dtest='<Pattern>'` |
| Integration | JUnit 5 + Testcontainers, classes named `*IT.java`, via Failsafe | `mvn -B verify -DskipUTs` (if configured) |
| Blackbox | REST Assured (API), Selenium/Playwright-Java (UI), in a Maven profile | `mvn -B verify -P e2e` |

## Debug Leftovers

- `System.out.println` / `System.err.println`, `printStackTrace()`
- Unused imports, commented-out code

## Release

- `version`: `mvn -B -q help:evaluate -Dexpression=project.version -DforceStdout`; the version is `<version>` in `pom.xml`.
- `dist`: `mvn -B package -DskipTests`, then copy `target/*.jar` to `dist/`.

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
```
