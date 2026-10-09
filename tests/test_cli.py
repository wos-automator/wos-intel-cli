"""The command line interface, in-process and as a separate process (US-1.2)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
from pytest_mock import MockerFixture

from tests.conftest import REF_DIR, load_ref
from wos_intel.__main__ import main
from wos_intel.adb import Adb, AdbError
from wos_intel.config import PROJECT_ROOT

TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} ", re.MULTILINE)


def project_config(tmp_path: Path) -> Path:
    """A config file in ``tmp_path`` that uses the real templates but its own ref/debug/state."""
    file = tmp_path / "config.toml"
    file.write_text(f'[paths]\ntemplates = "{PROJECT_ROOT / "templates"}"\n', encoding="utf-8")
    return file


@pytest.mark.blackbox
def test_detect_as_a_process_reports_the_spec_table(tmp_path: Path) -> None:
    image = tmp_path / "intel-xxx.png"
    shutil.copy(REF_DIR / "intel-xxx.png", image)

    result = subprocess.run(
        [sys.executable, "-m", "wos_intel", "detect", str(image)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert TIMESTAMP.search(result.stdout)
    assert "state INTEL_CLAIMABLE" in result.stdout
    assert "stamina 2035" in result.stdout
    assert result.stdout.count(" symbol ") == 8
    assert "RESCUE PURPLE DONE at 287,351" in result.stdout
    assert "HUNT GOLD DONE at 564,737" in result.stdout
    assert (tmp_path / "intel-xxx.debug.png").is_file()


@pytest.mark.blackbox
def test_usage_error_without_a_command() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "wos_intel"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 2
    assert "run" in result.stderr and "detect" in result.stderr and "snap" in result.stderr


@pytest.mark.integration
def test_detect_rejects_unreadable_and_wrongly_sized_images(tmp_path: Path) -> None:
    assert main(["detect", str(tmp_path / "missing.png")]) == 2

    small = tmp_path / "small.png"
    cv2.imwrite(str(small), np.zeros((100, 100, 3), dtype=np.uint8))
    assert main(["detect", str(small)]) == 2
    assert not (tmp_path / "small.debug.png").exists()


@pytest.mark.integration
def test_snap_writes_into_the_ref_directory(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch.object(Adb, "screenshot", return_value=load_ref("intel-x"))
    config = str(project_config(tmp_path))

    assert main(["--config", config, "snap", "rescue-1"]) == 0

    saved = cv2.imread(str(tmp_path / "ref" / "rescue-1.png"))
    assert saved is not None
    assert np.array_equal(saved, load_ref("intel-x"))


@pytest.mark.integration
def test_snap_does_not_overwrite_without_force(tmp_path: Path, mocker: MockerFixture) -> None:
    shot = mocker.patch.object(Adb, "screenshot", return_value=load_ref("intel-x"))
    config = str(project_config(tmp_path))
    assert main(["--config", config, "snap", "a"]) == 0

    assert main(["--config", config, "snap", "a.png"]) == 2
    assert shot.call_count == 1
    assert main(["--config", config, "snap", "a", "--force"]) == 0
    assert main(["--config", config, "snap", "../outside"]) == 2


@pytest.mark.integration
def test_run_dry_run_with_debug_images(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch.object(Adb, "check")
    mocker.patch.object(Adb, "screenshot", return_value=load_ref("intel-x"))
    tap = mocker.patch.object(Adb, "tap")
    back = mocker.patch.object(Adb, "back")

    code = main(["--config", str(project_config(tmp_path)), "run", "--dry-run", "--debug"])

    assert code == 0
    tap.assert_not_called()
    back.assert_not_called()
    assert [path.name for path in sorted((tmp_path / "debug").iterdir())] == [
        "0001-INTEL.png",
        "0002-INTEL.png",
    ]
    assert not (tmp_path / "state.json").exists()


@pytest.mark.integration
def test_run_fails_on_the_wrong_screen(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch.object(Adb, "check")
    mocker.patch.object(Adb, "screenshot", return_value=load_ref("hunt-3-deploy"))
    tap = mocker.patch.object(Adb, "tap")

    assert main(["--config", str(project_config(tmp_path)), "run"]) == 1
    tap.assert_not_called()


@pytest.mark.integration
def test_device_and_config_errors_exit_with_one(
    tmp_path: Path, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    mocker.patch.object(
        Adb, "check", side_effect=AdbError("com.gof.global is not in the foreground")
    )
    assert main(["--config", str(project_config(tmp_path)), "run"]) == 1
    assert "not in the foreground" in capsys.readouterr().out

    broken = tmp_path / "broken.toml"
    broken.write_text("[nonsense]\n", encoding="utf-8")
    assert main(["--config", str(broken), "run"]) == 1

    empty = tmp_path / "empty" / "config.toml"
    empty.parent.mkdir()
    empty.write_text("", encoding="utf-8")
    assert main(["--config", str(empty), "run"]) == 1
    assert "template missing" in capsys.readouterr().out
