# Workspace Guidelines & Rules

wos-intel automates the Intel missions in Whiteout Survival via ADB. This file holds the project's facts and rules; the workflows are skills in `.agents/skills/`.

## How to Work Here

1. **Environment**: Before the first terminal command, apply [environment](.agents/skills/environment/SKILL.md).
2. **Skills**: Before a matching task, read the skill and follow it. Load the referenced skills and profiles only when a step needs them.

| Task | Skill |
|---|---|
| New feature, from idea to backlog | [create-new-feature](.agents/skills/create-new-feature/SKILL.md) |
| Requirement / tech specification / user story | [create-requirement](.agents/skills/create-requirement/SKILL.md), [create-tech-specification](.agents/skills/create-tech-specification/SKILL.md), [create-user-story](.agents/skills/create-user-story/SKILL.md) |
| Change of existing specification items | [update-feature](.agents/skills/update-feature/SKILL.md), [update-requirement](.agents/skills/update-requirement/SKILL.md), [update-user-story](.agents/skills/update-user-story/SKILL.md) |
| Implement a story | [implement-user-story](.agents/skills/implement-user-story/SKILL.md) |
| Fix a defect | [fix-bug](.agents/skills/fix-bug/SKILL.md) |
| Done check | [definition-of-done](.agents/skills/definition-of-done/SKILL.md) |
| Commit | [commit](.agents/skills/commit/SKILL.md) |
| Release | [release](.agents/skills/release/SKILL.md) |
| Commands, test tooling | [toolchain](.agents/skills/toolchain/SKILL.md) |
| Specification layout and rules | [spec-system](.agents/skills/spec-system/SKILL.md) |

## Precedence

1. This file.
2. The project skills in `.agents/skills/`.
3. Personal instructions and skills of the user (e.g. `~/.claude/skills`, `~/.agents/`). They may only cover the machine environment and how to communicate; they never override a project rule or a project skill of the same purpose.

A change to a project rule is a change to this file or to `.agents/skills/`, made through the project's review. Files in `.agents/skills/` are the vendored agent-skills library (version in `.agents/skills/VERSION`): adapt it here, under "Project Facts", not by editing a skill. Update it to a new version with `.agents/skills/vendor.sh v<version>`, then commit `chore(agents): vendor agent-skills v<version>`.

---

## Project Facts

### Components

| Path | Toolchain profile |
|---|---|
| `.` (`wos_intel/`, `tools/`, `tests/`) | [python-uv](.agents/skills/toolchain/python-uv/PROFILE.md) |

The contract tasks are defined in `[tool.poe.tasks]` of `pyproject.toml`; `validate-specs` runs the library's launcher.

### Releases

Releases follow the [release](.agents/skills/release/SKILL.md) skill with `.github/workflows/release.yml`. The version lives in `[project] version` of `pyproject.toml` (task `version`). There is no `dist` task: wos-intel is installed with `git clone` and run with `uv run`, so a release carries the documentation; GitHub adds the source archives. Release tags are signed with the `wos-automator` key; its environment secret holds that key.

### Test Pyramid Limits

- Component tests replace the game with a scripted fake device.
- Blackbox tests run the CLI as a separate process (`detect`, usage errors). Runs against the real device are manual.

### Commit Scopes

`flow`, `detect`, `ocr`, `event`, `config`, `tools`.

---

## Self-Correction & Debugging Protocol

- **Do Not Guess**: Read stack traces and error messages carefully before editing code.
- **Isolate**: Reproduce defects with a minimal automated test before modifying code.
- **Limit Loops**: If a test or build fails more than 3 times for the same reason, stop and ask the user for guidance.
- **Zero Unapproved Dependencies**: Do not add new dependencies unless specified in the technical specification or requested by the user.

---

## Model-Specific Directives

- **Reasoning Models (Gemini Thinking, OpenAI o-series)**: Do not over-refactor outside requested scope. Omit conversational fluff and manual planning chatter in final responses; output direct technical results.
- **Claude Models**: Zero laziness policy (no placeholders). Match whitespace precisely when editing code.
- **GPT-4o Models**: Strictly adhere to tool schemas and verify file contents before editing.
