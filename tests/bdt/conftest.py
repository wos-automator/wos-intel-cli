"""Steps of the acceptance scenarios: the CLI as a separate process, no device."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from pytest_bdd import given, parsers, then, when

from wos_intel.config import PROJECT_ROOT

REF_DIR = PROJECT_ROOT / "ref"
TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} ")
SYMBOL = re.compile(r" symbol (\w+) (\w+) (\w+) at (\d+),(\d+) ")
TIERS = {"GOLD": 3, "PURPLE": 2, "BLUE": 1}
TOLERANCE = 6  # px, SPEC.md §3.5
# Test IDs and trace tags (AT-1.1, FR-1.4, NFR-2) identify scenarios; they are no pytest markers.
_ID = re.compile(r"[A-Z][A-Z0-9]*-\d+(\.\d+)*")


def pytest_bdd_apply_tag(tag: str, function: Callable[..., Any]) -> bool | None:
    return True if _ID.fullmatch(tag) else None


@dataclass
class Session:
    """What a scenario has set up and what the last command returned."""

    screenshot: Path | None = None
    result: subprocess.CompletedProcess[str] | None = None

    def run(self, *args: str) -> None:
        self.result = subprocess.run(
            [sys.executable, "-m", "wos_intel", *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    @property
    def done(self) -> subprocess.CompletedProcess[str]:
        assert self.result is not None, "no command has run"
        return self.result

    def symbols(self) -> list[tuple[str, str, str, int, int]]:
        """The logged symbols as (type, tier, status, x, y), in the order of the log."""
        return [
            (kind, tier, status, int(x), int(y))
            for kind, tier, status, x, y in SYMBOL.findall(self.done.stdout)
        ]

    def symbol_at(self, kind: str, x: int, y: int) -> tuple[str, str, str, int, int]:
        near = [
            symbol
            for symbol in self.symbols()
            if symbol[0] == kind
            and abs(symbol[3] - x) <= TOLERANCE
            and abs(symbol[4] - y) <= TOLERANCE
        ]
        assert len(near) == 1, f"{kind} at {x},{y}: {near or self.done.stdout}"
        return near[0]


@dataclass
class Detections:
    """``detect`` runs once per reference screenshot and test session; scenarios share it."""

    folder: Path
    results: dict[str, subprocess.CompletedProcess[str]] = field(default_factory=dict)


@pytest.fixture
def session() -> Session:
    return Session()


@pytest.fixture(scope="session")
def detections(tmp_path_factory: pytest.TempPathFactory) -> Detections:
    return Detections(tmp_path_factory.mktemp("detect"))


@given(parsers.parse('a copy of the reference screenshot "{name}"'))
def reference_copy(session: Session, tmp_path: Path, name: str) -> None:
    session.screenshot = tmp_path / name
    shutil.copy(REF_DIR / name, session.screenshot)


@when(parsers.parse('I run "{command}" on the screenshot'))
def run_on_screenshot(session: Session, command: str) -> None:
    assert session.screenshot is not None
    session.run(command, str(session.screenshot))


@when(parsers.parse('the detection runs on the reference screenshot "{name}"'))
def detect_reference(session: Session, detections: Detections, name: str) -> None:
    if name not in detections.results:
        copy = detections.folder / name
        shutil.copy(REF_DIR / name, copy)
        session.run("detect", str(copy))
        detections.results[name] = session.done
    session.result = detections.results[name]


@when(parsers.re(r'I run wos-intel with the arguments "(?P<arguments>[^"]*)"'))
def run_with_arguments(session: Session, arguments: str) -> None:
    session.run(*arguments.split())


@then(parsers.parse("the exit code is {code:d}"))
def exit_code(session: Session, code: int) -> None:
    assert session.done.returncode == code, session.done.stderr


@then(parsers.parse('the screen state is "{state}"'))
def screen_state(session: Session, state: str) -> None:
    assert f" state {state}\n" in session.done.stdout, session.done.stdout


@then(parsers.parse("exactly {count:d} symbols are reported"))
def symbol_count(session: Session, count: int) -> None:
    assert len(session.symbols()) == count, session.done.stdout


@then(parsers.parse("a {kind} symbol with status {status} is reported at about {x:d},{y:d}"))
def symbol_status(session: Session, kind: str, status: str, x: int, y: int) -> None:
    assert session.symbol_at(kind, x, y)[2] == status


@then(parsers.parse("the {kind} symbol at about {x:d},{y:d} has the tier {tier}"))
def symbol_tier(session: Session, kind: str, x: int, y: int, tier: str) -> None:
    assert session.symbol_at(kind, x, y)[1] == tier


@then("the symbols are listed by tier, highest first, then from top to bottom")
def symbol_order(session: Session) -> None:
    keys = [(-TIERS[tier], y, x) for _, tier, _, x, y in session.symbols()]
    assert len(keys) > 1
    assert keys == sorted(keys), session.done.stdout


@then(parsers.parse("the stamina reads {stamina:d}"))
def stamina_reads(session: Session, stamina: int) -> None:
    assert f" stamina {stamina}\n" in session.done.stdout, session.done.stdout


@then(parsers.parse("the refresh timer reads {hours:d}:{minutes:d}:{seconds:d}"))
def timer_reads(session: Session, hours: int, minutes: int, seconds: int) -> None:
    total = (hours * 60 + minutes) * 60 + seconds
    assert f" refresh in {total} s\n" in session.done.stdout, session.done.stdout


@then("every log line starts with a timestamp")
def timestamped(session: Session) -> None:
    lines = session.done.stdout.splitlines()
    assert lines
    assert all(TIMESTAMP.match(line) for line in lines), session.done.stdout


@then(parsers.parse('the log names the state "{state}" and the stamina {stamina:d}'))
def state_and_stamina(session: Session, state: str, stamina: int) -> None:
    assert f"state {state}\n" in session.done.stdout
    assert f"stamina {stamina}\n" in session.done.stdout


@then(parsers.parse("the log lists {count:d} symbols, among them:"))
def symbols(session: Session, count: int, datatable: list[list[str]]) -> None:
    assert session.done.stdout.count(" symbol ") == count
    for (symbol,) in datatable[1:]:
        assert f" symbol {symbol} " in session.done.stdout


@then(parsers.parse('the debug image "{name}" lies next to the screenshot'))
def debug_image(session: Session, name: str) -> None:
    assert session.screenshot is not None
    assert (session.screenshot.parent / name).is_file()


@then("the usage names the commands run, detect and snap")
def usage(session: Session) -> None:
    assert session.done.stderr.startswith("usage: ")
    assert "{run,detect,snap}" in session.done.stderr
