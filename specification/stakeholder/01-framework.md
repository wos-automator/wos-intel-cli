## 1. Framework

| Item | Decision |
|---|---|
| Language | Python 3.11+ |
| Libraries | `opencv-python`, `numpy`; nothing that needs a server |
| Device access | ADB only: `adb exec-out screencap -p` (image), `adb shell input tap/swipe`, `adb shell input keyevent KEYCODE_BACK` |
| Device | `ANDROID_SERIAL` (default `127.0.0.1:5555`); on "more than one device" always set `-s` |
| Resolution | 720×1280 portrait (`adb shell wm size` → `Physical size: 720x1280`); check at start, otherwise abort |
| Package | `com.gof.global` |
| macOS input | **no** mouse/keyboard input through macOS (proved unreliable: the map shifts) |

Related tool: `wos-watchdog.sh` (crash restart + Endless Trial macro).
`wos-intel` is a program of its own; merging the two later is **not** part of this specification.
