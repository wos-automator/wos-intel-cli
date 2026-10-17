# wos-intel – Specification

Automates the **Intel missions** in *Whiteout Survival* (BlueStacks Air on macOS):
detect the mission symbols on the Intel screen, start missions, collect rewards,
until no work is left or the stamina no longer suffices.

This file is the working basis for Claude Code. All coordinates refer to the
**Android image 720×1280** (`adb exec-out screencap -p`), not to the
macOS window.

The sections live in separate files; `SPEC.md §n` refers to the file numbered `n`.
Read only the section you need.

- [§1 Framework](specification/stakeholder/01-framework.md)
- [§2 Screens and states](specification/stakeholder/02-screens-states.md)
- [§3 Mission symbols on the Intel screen](specification/stakeholder/03-mission-symbols-intel-screen.md) (§3.1–§3.6)
- [§4 Stamina](specification/stakeholder/04-stamina.md)
- [§5 Flow (main loop)](specification/stakeholder/05-flow.md)
- [§6 Safety](specification/stakeholder/06-safety.md)
- [§7 Operation](specification/stakeholder/07-operation.md)
- [§8 Project structure](specification/stakeholder/08-project-structure.md)
