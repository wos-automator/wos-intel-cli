"""ADB access: screenshot, tap, back and the device check (TS-1.1).

Deliberately offers no swipe/zoom and no macOS input: the map must never be moved (FR-4.2).
"""

from __future__ import annotations

import logging
import re
import subprocess

import cv2
import numpy as np
import numpy.typing as npt

from wos_intel.config import DeviceConfig

log = logging.getLogger(__name__)

Image = npt.NDArray[np.uint8]

_SIZE_RE = re.compile(r"Physical size:\s*(\d+)x(\d+)")
_FOCUS_KEYS = ("mCurrentFocus", "mFocusedApp")


class AdbError(RuntimeError):
    """ADB is unavailable, the device is not ready, or a command failed."""


class Adb:
    """Thin wrapper around the ``adb`` binary, always addressing one explicit serial."""

    def __init__(self, config: DeviceConfig) -> None:
        self._config = config

    @property
    def serial(self) -> str:
        return self._config.serial

    def _run(self, *args: str) -> bytes:
        command = [self._config.adb_path, "-s", self._config.serial, *args]
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=self._config.command_timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise AdbError(f"adb binary not found: {self._config.adb_path}") from exc
        except subprocess.TimeoutExpired as exc:
            raise AdbError(f"adb timed out: {' '.join(args)}") from exc
        if result.returncode != 0:
            detail = result.stderr.decode(errors="replace").strip()
            raise AdbError(f"adb {' '.join(args)} failed: {detail}")
        return result.stdout

    def _text(self, *args: str) -> str:
        return self._run(*args).decode(errors="replace")

    def check(self) -> None:
        """Verify device state, resolution and that the game is in the foreground."""
        state = self._text("get-state").strip()
        if state != "device":
            raise AdbError(f"device {self.serial} is not ready (state: {state or 'unknown'})")

        size = _SIZE_RE.search(self._text("shell", "wm", "size"))
        expected = (self._config.width, self._config.height)
        if size is None or (int(size.group(1)), int(size.group(2))) != expected:
            found = size.group(0) if size else "unknown"
            raise AdbError(
                f"resolution must be {expected[0]}x{expected[1]}, device reports {found}"
            )

        focus = [
            line.strip()
            for line in self._text("shell", "dumpsys", "window").splitlines()
            if any(key in line for key in _FOCUS_KEYS)
        ]
        if not any(self._config.package in line for line in focus):
            raise AdbError(f"{self._config.package} is not in the foreground")

    def screenshot(self) -> Image:
        """Return the current screen as a BGR image."""
        data = self._run("exec-out", "screencap", "-p")
        image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            raise AdbError("screencap did not return a decodable PNG")
        height, width = image.shape[:2]
        if (width, height) != (self._config.width, self._config.height):
            raise AdbError(f"unexpected screenshot size {width}x{height}")
        return image.astype(np.uint8, copy=False)

    def tap(self, x: int, y: int) -> None:
        if not (0 <= x < self._config.width and 0 <= y < self._config.height):
            raise AdbError(f"tap outside the screen: {x},{y}")
        self._run("shell", "input", "tap", str(x), str(y))

    def back(self) -> None:
        self._run("shell", "input", "keyevent", "KEYCODE_BACK")
