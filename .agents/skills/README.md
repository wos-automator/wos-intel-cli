# agent-skills

Shared, project-independent workflows for coding agents (Claude Code, Codex, Gemini, …): specification, implementation, bug fixing, done check and commits, for projects in any language. A project vendors the library unchanged into `.agents/skills/` and keeps everything project-specific in its `AGENTS.md`.

## Layers

| Layer | Where | Holds |
|---|---|---|
| Project | `AGENTS.md` of the project | components and their profiles, deviating commands, test limits, commit scopes, extra rules; links to the skills |
| Workflow | `<skill>/SKILL.md` | language-free procedures: specification, implementation, fixes, done check, commit |
| Method | `spec-system/`, `definition-of-done/` | the rules the workflows apply |
| Toolchain | `toolchain/SKILL.md` + `toolchain/<profile>/` | the task contract, one profile per language and build tool |
| Environment | `environment/SKILL.md` + `environment/shells/`; personal: `~/.agents/environment/` | how commands are started on a machine |

Lookup: `AGENTS.md` → workflow skill → method / toolchain → profile, each loaded only when needed. A removed profile folder makes the agent infer the commands from the project's task definitions.

## Task Contract

Workflows never name commands, only tasks: `check`, `test`, `lint`, `format-check`, `typecheck`, `validate-specs`. Each project exposes them through its task runner; see [toolchain](toolchain/SKILL.md).

## Releases

Every project releases the same way, offline: the user signs an annotated tag `v<semver>` and pushes it; the pipeline of [release-actions](https://github.com/thst71/release-actions) verifies the signature against the repository's environment secret, runs the gate, builds the artifacts, renders each specification master as one HTML file and publishes the release with the dated release notes. Other tag names stay free for other uses. See the [release](release/SKILL.md) skill for the procedure, the workflow template and the one-time repository setup.

## Versions

The library itself has no release pipeline: a version is a signed, annotated tag `v<semver>` whose message lists the changes since the previous tag. `vendor.sh` writes the vendored version into `.agents/skills/VERSION`; release notes name it ("Built with agent-skills v0.2.0.").

## Precedence

The project's `AGENTS.md` comes first, then this library, then the user's personal instructions and skills (`~/.claude/skills`, `~/.agents/`). Personal files may cover the machine environment and how to communicate, never a project rule. For that reason the library is not linked into `.claude/skills/`: a personal skill of the same name would win there.

## Adopting the Library

Once per machine, trust the maintainer's signing key: `~/.agents/allowed_signers` holds the line `<maintainer email> namespaces="git" <ssh public key>`, with the key as published among the signing keys of the maintainer's GitHub account (`gh api users/thst71/ssh_signing_keys --jq '.[].key'`).

```sh
# first time: from a checkout of this repository
sh /path/to/agent-skills/vendor.sh v0.2.0
# later updates: the vendored copy updates itself
.agents/skills/vendor.sh v0.3.0
git commit -m "chore(agents): vendor agent-skills v0.3.0"
```

`vendor.sh` clones the tag, refuses it unless its SSH signature is by an allowed signer who is the tagger, replaces `.agents/skills/` with the tag's content (without `.github/`) and stages the result, so that every update is one signed, linear commit. A project that used `git subtree` before switches by running it once.

Then write the project's `AGENTS.md`: what the project is, a skill table linking `.agents/skills/<skill>/SKILL.md`, the precedence rule, the components with their toolchain profiles, test limits and commit scopes. Adopt the release workflow as the [release](release/SKILL.md) skill describes.

Do not edit the vendored files for one project; adapt in `AGENTS.md`. A change that is right for every project goes into this repository.

## Platforms

macOS and Linux are the targets. Windows is nice to have:

> "Is Windows a real target or just nice to have?" – Claude
>
> "Windows is nice to have, quote me quoting you in the readme :-)" – Thomas Strauß

## Contributing

- Skills are short, numbered procedures with a `Files Modified` and an `Execution Steps` section, in the style of the existing ones.
- Skills never name a language, a tool or a command; that belongs in a toolchain profile.
- Links between skills are relative (`../toolchain/SKILL.md`); CI checks that they resolve.
- Commits follow the [commit](commit/SKILL.md) skill; the scope is the skill or profile name.

## License

[LGPL-3.0-only](COPYING.LESSER) (which builds on the [GPL-3.0](COPYING)). Using the library in a project of any license is fine; changes to the library itself stay free.
