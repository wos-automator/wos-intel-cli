"""The ADB wrapper with ``subprocess.run`` mocked (US-1.1)."""

from __future__ import annotations

import subprocess
from typing import Any

import cv2
import numpy as np
import pytest
from pytest_mock import MockerFixture

from wos_intel.adb import Adb, AdbError
from wos_intel.config import DeviceConfig

pytestmark = pytest.mark.component

SERIAL = "127.0.0.1:5555"
FOCUS = "  mCurrentFocus=Window{1 u0 com.gof.global/com.unity3d.player.MyMainPlayerActivity}\n"
LAUNCHER = "  mCurrentFocus=Window{1 u0 com.uncube.launcher3/.HomeActivity}\n"


def completed(stdout: bytes = b"", returncode: int = 0, stderr: bytes = b"") -> Any:
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def png(width: int = 720, height: int = 1280) -> bytes:
    ok, data = cv2.imencode(".png", np.zeros((height, width, 3), dtype=np.uint8))
    assert ok
    return data.tobytes()


def responder(focus: str = FOCUS, size: str = "Physical size: 720x1280\n") -> Any:
    def run(command: list[str], **_: Any) -> Any:
        args = command[3:]
        if args == ["get-state"]:
            return completed(b"device\n")
        if args == ["shell", "wm", "size"]:
            return completed(size.encode())
        if args == ["shell", "dumpsys", "window"]:
            return completed(focus.encode())
        return completed()

    return run


def test_every_command_addresses_the_serial(mocker: MockerFixture) -> None:
    run = mocker.patch("wos_intel.adb.subprocess.run", side_effect=responder())
    adb = Adb(DeviceConfig())

    adb.check()
    adb.tap(10, 20)
    adb.back()

    for call in run.call_args_list:
        assert call.args[0][:3] == ["adb", "-s", SERIAL]
    assert run.call_args_list[-2].args[0][3:] == ["shell", "input", "tap", "10", "20"]
    assert run.call_args_list[-1].args[0][3:] == ["shell", "input", "keyevent", "KEYCODE_BACK"]


def test_check_passes_for_a_ready_device(mocker: MockerFixture) -> None:
    mocker.patch("wos_intel.adb.subprocess.run", side_effect=responder())

    Adb(DeviceConfig()).check()


def test_check_rejects_a_wrong_resolution(mocker: MockerFixture) -> None:
    mocker.patch(
        "wos_intel.adb.subprocess.run", side_effect=responder(size="Physical size: 1080x1920\n")
    )

    with pytest.raises(AdbError, match="720x1280"):
        Adb(DeviceConfig()).check()


def test_check_rejects_a_game_that_is_not_in_the_foreground(mocker: MockerFixture) -> None:
    mocker.patch("wos_intel.adb.subprocess.run", side_effect=responder(focus=LAUNCHER))

    with pytest.raises(AdbError, match="not in the foreground"):
        Adb(DeviceConfig()).check()


def test_check_rejects_an_offline_device(mocker: MockerFixture) -> None:
    mocker.patch("wos_intel.adb.subprocess.run", return_value=completed(b"offline\n"))

    with pytest.raises(AdbError, match="not ready"):
        Adb(DeviceConfig()).check()


def test_failed_command_raises_with_stderr(mocker: MockerFixture) -> None:
    mocker.patch(
        "wos_intel.adb.subprocess.run",
        return_value=completed(returncode=1, stderr=b"error: more than one device/emulator"),
    )

    with pytest.raises(AdbError, match="more than one device"):
        Adb(DeviceConfig()).back()


def test_missing_binary_and_timeout_raise(mocker: MockerFixture) -> None:
    run = mocker.patch("wos_intel.adb.subprocess.run", side_effect=FileNotFoundError())
    with pytest.raises(AdbError, match="not found"):
        Adb(DeviceConfig()).back()

    run.side_effect = subprocess.TimeoutExpired("adb", 15)
    with pytest.raises(AdbError, match="timed out"):
        Adb(DeviceConfig()).back()


def test_screenshot_decodes_the_png(mocker: MockerFixture) -> None:
    run = mocker.patch("wos_intel.adb.subprocess.run", return_value=completed(png()))

    image = Adb(DeviceConfig()).screenshot()

    assert image.shape == (1280, 720, 3)
    assert run.call_args.args[0][3:] == ["exec-out", "screencap", "-p"]


def test_screenshot_rejects_garbage_and_wrong_size(mocker: MockerFixture) -> None:
    run = mocker.patch("wos_intel.adb.subprocess.run", return_value=completed(b"not a png"))
    with pytest.raises(AdbError, match="decodable"):
        Adb(DeviceConfig()).screenshot()

    run.return_value = completed(png(1280, 720))
    with pytest.raises(AdbError, match="unexpected screenshot size"):
        Adb(DeviceConfig()).screenshot()


def test_tap_outside_the_screen_is_refused(mocker: MockerFixture) -> None:
    run = mocker.patch("wos_intel.adb.subprocess.run", return_value=completed())

    with pytest.raises(AdbError, match="outside"):
        Adb(DeviceConfig()).tap(720, 100)
    run.assert_not_called()


def test_no_swipe_or_text_input_is_offered() -> None:
    assert not any(name in dir(Adb) for name in ("swipe", "text", "zoom", "drag"))
