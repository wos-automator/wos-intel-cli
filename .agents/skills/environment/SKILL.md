---
name: environment
description: >-
  Identify the user's shell and platform and apply the matching instructions for running terminal commands, before the first command of a session.
---

# Skill: Environment

How to run commands on the user's machine. This is about the machine, not the project: it never changes which commands a project runs, only how they are started.

## Execution Steps

1. **Identify**: Determine the shell and platform from the harness's environment information, or from `$SHELL` and `uname -s`.
2. **Look up** the instructions for that shell, first match wins:
   1. `~/.agents/environment/<shell>.md` – the user's own, machine-specific file
   2. `shells/<shell>.md` next to this file – the shared default
3. **Apply** them to every command. When neither file exists, run commands as they are; if a tool is not found, check whether a login shell or version manager provides it, and tell the user.

## Shells

- [fish](shells/fish.md)
