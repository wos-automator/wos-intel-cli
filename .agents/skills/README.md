# Agent Skill Library

Shared, project-independent workflows for coding agents. A project adopts the library unchanged and keeps everything project-specific in its `AGENTS.md`.

## Layers

| Layer | Where | Holds |
|---|---|---|
| Project | `AGENTS.md` | components and their profiles, deviating commands, test limits, commit scopes, extra rules; links to the skills |
| Workflow | `<skill>/SKILL.md` | language-free procedures: specification, implementation, fixes, done check, commit |
| Method | `spec-system/`, `definition-of-done/` | the rules the workflows apply |
| Toolchain | `toolchain/SKILL.md` + `toolchain/<profile>/` | the task contract, one profile per language and build tool |
| Environment | `environment/SKILL.md` + `environment/shells/`; personal: `~/.agents/environment/` | how commands are started on a machine |

Lookup: `AGENTS.md` → workflow skill → method / toolchain → profile, each loaded only when needed. A removed profile folder makes the agent infer the commands from the project's task definitions.

## Task Contract

Workflows never name commands, only tasks: `check`, `test`, `lint`, `format-check`, `typecheck`, `validate-specs`. Each project exposes them through its task runner; see [toolchain](toolchain/SKILL.md).

## Adopting the Library

```sh
git subtree add --prefix .agents/skills <library-repo> main --squash
git subtree pull --prefix .agents/skills <library-repo> main --squash
```

Then write the project's `AGENTS.md`: components with profiles, test limits, commit scopes, and the skill table. Do not edit the vendored files for one project; a change that is right for every project goes upstream.
