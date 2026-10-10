# BlueStacks and ADB setup

> **Sample code, potentially dangerous.** `wos-intel` sends real input to a real game account
> and may cause damage when used as is. Back up and protect everything of value to you before
> you run it, and read the [disclaimer](../../README.md#disclaimer).

`wos-intel` talks to the game only through the Android Debug Bridge (ADB). This guide gets a
BlueStacks Air instance on macOS, with *Whiteout Survival* already installed, into the state the
tool expects:

| Requirement | Value |
|---|---|
| Resolution | 720×1280, portrait |
| Pixel density | 240 DPI |
| ADB | enabled, reachable at `127.0.0.1:5555` |
| Game language | English |
| Game package | `com.gof.global` |

The menu names below are those of BlueStacks 5 and BlueStacks Air; they can differ slightly
between versions.

## 1. Install adb

```sh
brew install android-platform-tools
adb version
```

If `adb` is not on your `PATH`, set its full path as `device.adb_path` in `config.toml`.

## 2. Set the display

In BlueStacks open **Settings → Display** and choose:

- **Orientation:** Portrait
- **Resolution:** Custom, width `720`, height `1280`
- **Pixel density:** 240 DPI

Save and restart the instance. All templates and coordinates of the tool refer to exactly this
image size; with any other resolution the tool refuses to start.

## 3. Enable the Android Debug Bridge

Open **Settings → Advanced** and switch on **Android Debug Bridge (ADB)**. BlueStacks shows the
address to connect to below the switch, normally `127.0.0.1:5555`. A second instance gets another
port; use the one shown there.

## 4. Connect

```sh
adb connect 127.0.0.1:5555
adb devices
```

The instance must be listed with the state `device`:

```text
List of devices attached
127.0.0.1:5555	device
emulator-5554	device
```

BlueStacks often shows up twice, as in this example, once under its network address and once as
`emulator-5554`. That is why `wos-intel` addresses one serial explicitly in every call. It uses
`127.0.0.1:5555` by default; to use another one, set `ANDROID_SERIAL` or `device.serial` in
`config.toml`:

```sh
set -x ANDROID_SERIAL 127.0.0.1:5565     # fish
export ANDROID_SERIAL=127.0.0.1:5565     # bash, zsh
```

`adb connect` has to be repeated after BlueStacks or the ADB server was restarted.

## 5. Check the connection

```sh
adb -s 127.0.0.1:5555 shell wm size       # Physical size: 720x1280
adb -s 127.0.0.1:5555 shell wm density    # Physical density: 240
adb -s 127.0.0.1:5555 exec-out screencap -p > /tmp/wos.png && open /tmp/wos.png
```

The screenshot must show the game in portrait, 720×1280 pixels.

## 6. Prepare the game

- Set the game language to **English**; titles and buttons are recognised by their English text.
- Start the game and close all popups, until you see the **world map** or the **Intel screen**.
- Leave the map where it is. The tool finds the Intel button on the right edge of the world map.

Then run a dry run, which only looks and logs:

```sh
uv run python -m wos_intel run --dry-run
```

On the world map it ends with a line like

```text
INFO    state WORLD
INFO    dry run: would tap 663,862 (intel_button)
INFO    finished: dry run finished (0 mission(s) started)
```

The setup is complete. Continue with the [usage guide](usage.md).

## Problems

| Message | Cause and fix |
|---|---|
| `adb binary not found: adb` | `adb` is not installed or not on the `PATH` (step 1) |
| `adb get-state failed: error: device '127.0.0.1:5555' not found` or `device 127.0.0.1:5555 is not ready` | ADB is switched off in BlueStacks, or `adb connect` is missing (steps 3 and 4) |
| `adb ... failed: error: device offline` | Run `adb kill-server`, then `adb connect 127.0.0.1:5555` again |
| `resolution must be 720x1280, device reports ...` | Display settings differ (step 2); restart the instance after changing them |
| `com.gof.global is not in the foreground` | The game is not running or another app is in front |
| `game is neither on the Intel screen nor on the world map` | A popup or another game screen is open; close it (step 6) |
