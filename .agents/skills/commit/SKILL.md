---
name: commit
description: >-
  Commit finished work with a Conventional Commits message that traces to its requirements, user story or defect, so changelogs can be generated from the history.
---

# Skill: Commit

Record one finished unit of work (a user story, a defect fix or a specification change) as one commit with a Conventional Commits message.

## Files Modified

- None; this skill only stages and commits.

## Message Format

```
<type>(<scope>)<!>: <summary>

<body>

<footers>
```

- **type** (required):

  | Type | Use for |
  |---|---|
  | `feat` | a user story, a new or changed behaviour |
  | `fix` | a defect (`BUG-xxxx`) or a behaviour that violates its requirement |
  | `perf` | faster or cheaper without a change in behaviour |
  | `refactor` | code restructured, behaviour unchanged |
  | `test` | tests only |
  | `docs` | specification, release notes or other documentation only |
  | `chore` | tooling, dependencies, templates, `.gitignore`, project files |

- **scope** (optional, lower case): the module or area; use the scopes listed in `AGENTS.md`, plus `spec` and `agents` (this skill library).
- **`!`** after the scope marks a breaking change: a removed or renamed setting, command or file path, or a changed default the operator has to know about. It requires a `BREAKING CHANGE:` footer.
- **summary**: imperative mood, lower case start, no full stop, at most 72 characters for the whole first line. It says what the change does, not which item it implements.
- **body** (optional): why the change was needed and what behaves differently, wrapped at 72 characters. Leave out what the diff already shows.
- **footers** (one per line, `Token: value`):
  - `Refs: US-x.y, FR-x.y, TS-x.y` – the traced items; required for `feat` and `fix`.
  - `Fixes: BUG-xxxx` – the defect ID, if there is one.
  - `BREAKING CHANGE: <what changed and what to do>` – with `!`.
  - The attribution trailers the harness asks for (e.g. `Co-Authored-By:`) come last.

## Execution Steps

1. **Quality Gate**: Run the `check` task (see [toolchain](../toolchain/SKILL.md)); commit only when it passes.
2. **Scope Check**: One commit per user story, defect or specification change. If the working tree mixes several, stage them separately (`git add <paths>`). Never stage unrelated files of the user (IDE folders, scratch files).
3. **Message**: Write the message in the format above. Pick the type from the main effect: a story that also adds tests and spec items is `feat`, not `test` or `docs`.
4. **Commit**: Pass the message through a heredoc (`git commit -F - <<'EOF' … EOF`) so that backticks and line breaks survive. If commit signing fails, do not bypass it (`--no-gpg-sign`, `-n`); report it and ask the user.
5. **Push**: Only when the user asks for it.

## Examples

```
feat(detect): detect the firebeast pin as a hunt

A second HUNT mask, cut from ref/flame-and-fangs-missions.png, finds the
gold firebeast pin of the running Flame and Fangs event.

Refs: US-6.5, FR-5.5, TS-5.3
```

```
fix(flow): claim rewards while waiting for a free march queue

The wait for a free queue slept 60 s without looking at the screen, so
finished hunts stayed unclaimed. It now checks every 10 s and tries the
hunt again right after the claim.

Refs: US-3.8, FR-3.9, TS-3.6
```

```
feat(config)!: shorten the wait for running missions to 5 min

BREAKING CHANGE: the default completion_timeout is 300 s instead of
900 s; set it in [timing] of config.toml to keep the old wait.
Refs: US-5.7, FR-3.7
```
