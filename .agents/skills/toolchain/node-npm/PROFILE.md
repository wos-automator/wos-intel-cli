# Profile: Node / npm

- Ecosystem: Node.js (active LTS), `package.json`, `package-lock.json`; TypeScript where the project has a `tsconfig.json`
- Task runner: npm scripts in `package.json`
- Run a contract task: `npm run <task>` (e.g. `npm run check`)
- Dependency install: `npm ci`; `npm install` only to change the lockfile
- Add a dependency: `npm install <pkg>` / `npm install --save-dev <pkg>` (only when approved)

## Contract Mapping

```json
"scripts": {
  "lint": "eslint . --max-warnings 0",
  "format-check": "prettier --check src",
  "typecheck": "tsc --noEmit",
  "test": "vitest run --coverage --reporter=default --reporter=junit --outputFile.junit=build/test/junit.xml",
  "validate-specs": ".agents/skills/spec-system/bin/validate-specs",
  "check": "npm run lint && npm run format-check && npm run typecheck && npm run test && npm run validate-specs"
}
```

- `test` runs once and always measures coverage; keep the watch mode under another name (e.g. `test:watch`). There is no separate coverage script or pipeline step.
- Test durations: the JUnit reporter writes the time of every test to `build/test/junit.xml`, next to the console output; `build/` belongs in `.gitignore` and the ESLint ignores.
- `coverage.thresholds` in the Vitest configuration make coverage part of the gate: set them to today's values, rounded down, raise them when coverage grows and never lower them to make a change pass. ESLint ignores the `coverage/` output.
- `--max-warnings 0` makes lint warnings fail the gate, as the [definition-of-done](../../definition-of-done/SKILL.md) demands.
- A component below the project root calls the launcher with a relative path and passes the root: `../.agents/skills/spec-system/bin/validate-specs ..`.
- `version` is an npm lifecycle script; do not define a script of that name (see Release).

## Test Pyramid Tooling

| Level | Tooling | Run one level |
|---|---|---|
| Unit | Vitest | `npx vitest run <file or folder>` |
| Component | Vitest + Testing Library (`jsdom`), collaborators mocked with `vi.mock` | `npx vitest run <file or folder>` |
| Integration | Vitest with real collaborators and in-memory fakes (e.g. `fake-indexeddb`, `msw`) | `npx vitest run <file or folder>` |
| Blackbox | Playwright against the built app (`vite preview`) or the running service | `npx playwright test` |

- Unit, component and integration tests sit next to the code as `*.test.ts(x)`; Playwright tests in `e2e/`.
- Results must not depend on the machine: tests that format dates or numbers pin `LC_ALL` and `TZ` in the Vitest configuration (set `process.env` before the workers start).

## BDT

Only for requirements-based blackbox testing (see [spec-system](../../spec-system/SKILL.md), BDT): [playwright-bdd](https://vitalets.github.io/playwright-bdd) turns the feature files into Playwright tests and writes Cucumber JSON.

- Dev dependencies: `@playwright/test`, `playwright-bdd`; the browser with `npx playwright install chromium` (CI: `npx playwright install --with-deps chromium`).
- Task: `"bdt": "bddgen && playwright test"`.
- Step definitions in `e2e/steps/*.ts` with `createBdd()`; generated tests in `.features-gen/` (ignored by git and by ESLint and Prettier).

```ts
// playwright.config.ts
const testDir = defineBddConfig({
  features: "specification/acceptance/**/*.feature",
  steps: "e2e/steps/*.ts",
});
export default defineConfig({
  testDir,
  reporter: [cucumberReporter("json", { outputFile: "build/bdt/cucumber.json" }), ["html", { open: "never" }]],
  use: { baseURL: "http://localhost:4173" },
  webServer: { command: "npm run build && npm run preview", url: "http://localhost:4173", reuseExistingServer: !process.env.CI },
});
```

- The Cucumber JSON carries tags with `@` and one element per example row.
- `tsconfig.json` needs the `node` types for `process` in the configuration files.

## Debug Leftovers

- `console.log` / `console.debug` (ESLint `no-console`), `debugger`
- `.only` and unexplained `.skip` in tests
- `// @ts-ignore`, `// @ts-expect-error` and `eslint-disable` without a reason
- Unused imports and variables (`@typescript-eslint/no-unused-vars`, `noUnusedLocals`)

## Security

`npm audit --audit-level moderate` reports vulnerable dependencies. It depends on the advisory database of the day, so it is no contract task; a project that gates on it says so in `AGENTS.md` and runs it in its pipeline.

## Release

- `version`: `node -p "require('./package.json').version"`; the version is `version` in `package.json`.
- A project that takes the version from the tag instead (e.g. injected at build time) has no `version` task and leaves `version` in `package.json` as it is: it is not maintained, and the release does not compare it. `package.json` cannot hold a comment, so `AGENTS.md` says so.
- `dist`: a package runs `npm pack --pack-destination dist`; a web app archives its build (`tar -czf dist/<name>-<version>.tar.gz -C build .`). An app delivered as a container image has no `dist`; its image is built in the workflow (see [release](../../release/SKILL.md), Adoption).

Pull Request steps (job `check` of the pull request template):

```yaml
      - uses: actions/setup-node@v5
        with:
          node-version: lts/*
          cache: npm
      - run: npm ci
      - run: npm run check
      - run: npm audit --audit-level moderate   # only where AGENTS.md gates on it
      # BDT only:
      - run: npx playwright install --with-deps chromium
      - run: npm run bdt
```

Release Build steps:

```yaml
      - uses: actions/setup-node@v5
        with:
          node-version: lts/*
          cache: npm
      - run: npm ci
      - run: npm run check
      - run: test "$(node -p "require('./package.json').version")" = "${{ needs.verify.outputs.version }}"
      - run: npm run dist
      # BDT only:
      - run: npx playwright install --with-deps chromium
      - run: npm run bdt
```
