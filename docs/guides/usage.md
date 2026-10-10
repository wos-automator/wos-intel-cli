# Usage guide

> **Sample code, potentially dangerous.** `wos-intel` sends real input to a real game account
> and may cause damage when used as is. Back up and protect everything of value to you before
> you run it, and read the [disclaimer](../../README.md#disclaimer).

This guide assumes that BlueStacks and ADB are set up as described in
[BlueStacks and ADB setup](bluestacks-setup.md) and that `uv sync` has been run once in the
project directory.

All commands have the form

```sh
uv run python -m wos_intel [--config <file>] <command>
```

## Before a run

- The game is in the foreground and shows the **world map** or the **Intel screen**.
- Heroes and troops for hunts are the ones the game preselects; the tool never changes them.
- Do not use the BlueStacks window while a run is active.

## Dry run

```sh
uv run python -m wos_intel run --dry-run
```

A dry run takes screenshots, logs the detected screen, the stamina, every symbol and the tap it
would send, and ends without tapping. Use it after every change to the setup or the configuration.

## Run

```sh
uv run python -m wos_intel run
```

The run

1. checks the device state, the resolution and that the game is in the foreground,
2. opens the Intel screen from the world map,
3. collects finished missions with "Claim All",
4. starts the available missions, highest tier first,
5. taps the daily expert sign once no regular mission is left,
6. attacks the boss last, once per refresh cycle,
7. waits for running missions (up to 15 minutes) and collects their rewards,
8. ends with a line such as `finished: nothing to do (7 mission(s) started)`.

The log goes to standard output with a timestamp per line. To keep it:

```sh
uv run python -m wos_intel run | tee run.log
```

### How a run ends

| Final message | Meaning | Exit code |
|---|---|---|
| `nothing to do` | Every mission is done and collected | 0 |
| `not enough stamina` | The stamina is below the cost of the remaining missions | 0 |
| `no troops or march slots available` | The game reported missing troops or march slots | 0 |
| `mission limit reached` | `limits.max_missions` missions were started (default 30) | 0 |
| `dry run finished` | `--dry-run` was given | 0 |
| `game is neither on the Intel screen nor on the world map` | Wrong start screen; nothing was tapped | 1 |
| `too many consecutive failures` | Three steps in a row did not lead to the expected screen | 1 |

Errors of the device check and of the configuration also end with exit code 1; a wrong command
line ends with 2.

### When a mission is skipped

A mission is skipped for the rest of the run when a check fails, for example when the dialog
shows another mission type than the tapped symbol, or when a hunt is not "quite likely to
prevail". The tool backs out with BACK and saves the screenshot as
`debug/failure-<step>-<STATE>.png`, so you can see what it saw.

### The boss lock

After the boss was attacked, `state.json` stores until when it is locked, derived from the
"Refreshes In" timer. Until then later runs leave the boss alone. Delete `state.json` to lift the
lock by hand.

## Debug images

```sh
uv run python -m wos_intel run --debug
```

`--debug` additionally saves one annotated screenshot per step under `debug/`, with the detected
state, the template matches and every symbol drawn in. It can be combined with `--dry-run`.

## Detection on a file

```sh
uv run python -m wos_intel detect ref/intel-x.png
```

`detect` runs the detection on a 720×1280 image without a device, logs state, stamina, refresh
timer and symbols, and writes the annotated image next to the input as `<name>.debug.png`. It is
the quickest way to check a threshold change.

## Collecting reference screenshots

```sh
uv run python -m wos_intel snap rescue-2-world
```

`snap` saves the current screen as `ref/<name>.png`. An existing file is only overwritten with
`--force`. New screens, for example the rescue popup, are needed as references before templates
can be cut for them.

World-map screenshots show player names, alliance tags and your state number. Remove them before
you commit such an image.

## Configuration

The tool reads `config.toml` from the working directory, otherwise from the project directory;
`--config <file>` names another one. Without a file the built-in defaults apply, and the shipped
`config.toml` lists exactly those. A file only needs the values it changes:

```toml
[device]
serial = "127.0.0.1:5565"

[limits]
max_missions = 10

[timing]
tap_delay = 1.5
```

| Section | Content |
|---|---|
| `device` | serial, path to `adb`, package, resolution, timeout per ADB call |
| `timing` | waits after taps, polling intervals, timeouts for screens, fights and running missions |
| `limits` | missions per run, BACK presses during recovery, consecutive failures, minimum stamina |
| `costs` | stamina cost per mission type |
| `symbols`, `buttons`, `ocr`, `regions` | colour ranges, thresholds and search regions of the detection |
| `boss` | lock duration if the refresh timer cannot be read |
| `paths` | folders for templates, references and debug images, and the state file |

The environment variable `ANDROID_SERIAL` overrides `device.serial`. Unknown sections or keys
are rejected with an error, so a typo does not go unnoticed.

## Troubleshooting

| Symptom | What to do |
|---|---|
| The run stops at the device check | See the table in [BlueStacks and ADB setup](bluestacks-setup.md#problems) |
| `state UNKNOWN` on a screen that looks right | Check the game language (English) and the resolution; run `detect` on a `snap` of that screen to see the match scores |
| Symbols are missing in the log | Run `run --dry-run --debug` and look at the annotated image under `debug/` |
| A mission is skipped every time | Look at the `debug/failure-*.png` of that step; the log line before it names the failed check |
| The boss is not attacked | It is locked for the current refresh cycle (`state.json`), or other missions are still available |
| Taps arrive too early on a slow machine | Raise `timing.tap_delay` and `timing.expect_timeout` |
