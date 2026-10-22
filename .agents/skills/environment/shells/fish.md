# Shell: fish

The user's `PATH` (version managers, `uv`, `poetry`, Homebrew tools, …) is set up in the fish configuration. A harness that starts commands in `bash` or `sh` does not load it.

- Run every toolchain command in a fish login shell: `fish -lc "uv run poe check"`.
- Commands that only use system tools (`git`, `ls`, `grep`) may run without the wrapper.
- Quoting: inside `fish -lc "…"`, backticks, `$` and double quotes are interpreted twice. Do not edit files with `sed` or `echo` inside the wrapper; use the harness's file editing tools.
