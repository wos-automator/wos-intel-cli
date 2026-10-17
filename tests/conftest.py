"""Shared fixtures: reference screenshots, synthetic screens and a scripted fake game."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import cv2
import numpy as np
import pytest

from wos_intel.config import PROJECT_ROOT, Config
from wos_intel.detect import Detector, Image

REF_DIR = PROJECT_ROOT / "ref"
TEMPLATE_DIR = PROJECT_ROOT / "templates"

Point = tuple[int, int]

VIEW: Point = (360, 932)
BOSS_VIEW: Point = (360, 870)
ACTION: Point = (360, 615)
FIGHT: Point = (530, 1202)
DEPLOY: Point = (550, 1215)
RESULT_EXIT: Point = (360, 1140)
CLAIM_ALL: Point = (360, 1127)
REWARDS_EXIT: Point = (360, 180)
INTEL_BUTTON: Point = (663, 862)
EXPERT: Point = (59, 210)
HINT: Point = (341, 856)
CANCEL: Point = (210, 787)
RECONNECT: Point = (520, 802)
WORLD_TARGET: Point = (360, 731)  # below the intel pin at 360,661
EXPERT_AREA = (10, 165, 105, 255)

BOSS: Point = (518, 700)
TENT: Point = (287, 351)
AXE_PURPLE: Point = (340, 378)
AXE_BLUE: Point = (568, 680)
PAW_PURPLE: Point = (275, 677)
PAW_BLUE_LEFT: Point = (336, 289)
PAW_BLUE_RIGHT: Point = (483, 315)

POPUP_BUTTON = (245, 598, 475, 660)
POPUP_BACKGROUND = (250, 245, 240)


def load_ref(name: str) -> Image:
    image = cv2.imread(str(REF_DIR / f"{name}.png"), cv2.IMREAD_COLOR)
    assert image is not None, name
    return np.asarray(image, dtype=np.uint8)


def _fill(image: Image, region: tuple[int, int, int, int], colour: tuple[int, int, int]) -> Image:
    out = image.copy()
    x0, y0, x1, y1 = region
    out[y0:y1, x0:x1] = colour
    return out


def make_world() -> Image:
    """World map without a popup button: the Explore button is painted over."""
    return _fill(load_ref("combat-2-world-explore"), POPUP_BUTTON, POPUP_BACKGROUND)


def make_rescue_popup() -> Image:
    """World-map popup whose action button is green, as SPEC §2 expects for Rescue."""
    out = load_ref("combat-2-world-explore")
    x0, y0, x1, y1 = POPUP_BUTTON
    hsv = cv2.cvtColor(out[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    hsv[..., 0] = 60
    out[y0:y1, x0:x1] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return out


def make_dialog(mask_name: str) -> Image:
    """Mission dialog whose pin shows the given symbol mask (no reference exists for these)."""
    out = load_ref("combat-1-dialog")
    centre = (360, 368)
    cv2.circle(out, centre, 21, (90, 30, 60), -1)
    mask = cv2.imread(str(TEMPLATE_DIR / f"{mask_name}.png"), cv2.IMREAD_GRAYSCALE)
    assert mask is not None
    scaled = cv2.resize(mask, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_AREA)
    height, width = scaled.shape[:2]
    top, left = centre[1] - height // 2, centre[0] - width // 2
    out[top : top + height, left : left + width][scaled > 127] = (255, 255, 255)
    return out


def with_expert(name: str) -> Image:
    """An Intel reference with the expert sign of intel-expert-available.png pasted in."""
    out = load_ref(name)
    x0, y0, x1, y1 = EXPERT_AREA
    out[y0:y1, x0:x1] = load_ref("intel-expert-available")[y0:y1, x0:x1]
    return out


def make_deploy_unlikely() -> Image:
    """Deploy screen without the green "You are quite likely to prevail" hint."""
    return _fill(load_ref("hunt-3-deploy"), (150, 585, 570, 628), (104, 53, 13))


def make_defeat() -> Image:
    """Result screen without the "Victory!" title."""
    return _fill(load_ref("combat-4-victory"), (150, 380, 570, 560), (40, 30, 20))


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.fixture(scope="session")
def detector(config: Config) -> Detector:
    return Detector(config)


@pytest.fixture(scope="session")
def images() -> dict[str, Image]:
    loaded = {path.stem: load_ref(path.stem) for path in sorted(REF_DIR.glob("*.png"))}
    loaded["world"] = make_world()
    loaded["rescue-popup"] = make_rescue_popup()
    loaded["rescue-dialog"] = make_dialog("tent_mask")
    loaded["deploy-unlikely"] = make_deploy_unlikely()
    loaded["defeat"] = make_defeat()
    loaded["expert-only-boss-running"] = with_expert("intel-boss-running")
    loaded["expert-and-missions"] = with_expert("intel-x")
    return loaded


def near(a: Point, b: Point, tolerance: int = 25) -> bool:
    return abs(a[0] - b[0]) <= tolerance and abs(a[1] - b[1]) <= tolerance


class FakeGame:
    """Scripted stand-in for the device: taps move between reference screenshots.

    ``transitions`` maps a screen name to ``(tap point, next screen)`` pairs. A tap that
    matches no pair is recorded in ``stray_taps`` and leaves the screen unchanged.
    """

    def __init__(
        self,
        images: dict[str, Image],
        start: str = "intel-x",
        intel: str = "intel-x",
        overrides: dict[str, list[tuple[Point, str]]] | None = None,
    ) -> None:
        self._images = images
        self.screen = start
        self.taps: list[tuple[str, Point]] = []
        self.stray_taps: list[tuple[str, Point]] = []
        self.backs: list[str] = []
        self.checked = 0
        # screen -> (fake time, next screen): the screen changes by itself once the time is up
        self.timed: dict[str, tuple[float, str]] = {}
        # screen -> (seconds, next screen): every visit turns into the next screen after
        # that many seconds, e.g. a dialog whose notification banner fades away
        self.transient: dict[str, tuple[float, str]] = {}
        self.entered = 0.0
        self.clock: FakeClock | None = None
        symbols = [
            (BOSS, "hunt-1-dialog"),
            (TENT, "combat-1-dialog"),
            (AXE_PURPLE, "combat-1-dialog"),
            (AXE_BLUE, "combat-1-dialog"),
            (PAW_PURPLE, "hunt-1-dialog"),
            (PAW_BLUE_LEFT, "hunt-1-dialog"),
            (PAW_BLUE_RIGHT, "hunt-1-dialog"),
        ]
        self.transitions: dict[str, list[tuple[Point, str]]] = {
            "intel-x": list(symbols),
            "intel-xx": list(symbols),
            "intel-xxx": [(CLAIM_ALL, "intel-xxxx"), *symbols],
            "intel-xxxx": [(REWARDS_EXIT, intel)],
            "expert-only-boss-running": [(EXPERT, "intel-x")],
            "expert-and-missions": [(EXPERT, "intel-x"), *symbols],
            "combat-1-dialog": [(VIEW, "combat-2-world-explore")],
            "hunt-1-dialog": [(VIEW, "hunt-2-world-attack")],
            "rescue-dialog": [(VIEW, "rescue-popup")],
            "boss-1-dialog": [(BOSS_VIEW, "boss-2-world-attack")],
            "boss-2-world-attack": [(ACTION, "boss-3-deploy")],
            "boss-3-deploy": [(DEPLOY, "world")],
            "combat-2-world-explore": [(ACTION, "combat-3-squad-fight")],
            "hunt-2-world-attack": [(ACTION, "hunt-3-deploy")],
            "rescue-popup": [((360, 629), "world")],
            "combat-3-squad-fight": [(FIGHT, "combat-4-victory")],
            "combat-4-victory": [(RESULT_EXIT, "world")],
            "defeat": [(RESULT_EXIT, "world")],
            "hunt-3-deploy": [(DEPLOY, "world")],
            "deploy-unlikely": [(DEPLOY, "world")],
            "world": [(INTEL_BUTTON, intel)],
            "world-simple-battle-mode": [(HINT, "world")],
            "hunt-2-world-no-popup": [(INTEL_BUTTON, intel)],
            "boss-2-world-no-popup": [(INTEL_BUTTON, intel)],
            "world-target-vanished": [(INTEL_BUTTON, intel)],
            "dialog-logged-in-elsewhere": [(RECONNECT, "world")],
        }
        self.back_transitions: dict[str, str] = {
            "combat-1-dialog": intel,
            "hunt-1-dialog": intel,
            "rescue-dialog": intel,
            "hunt-1-dialog-banner": intel,
            "rescue-1-dialog-banner": intel,
            "boss-1-dialog": intel,
            "boss-2-world-attack": "world",
            "boss-3-deploy": "boss-2-world-attack",
            "combat-2-world-explore": "world",
            "hunt-2-world-attack": "world",
            "rescue-popup": "world",
            "hunt-3-deploy": "hunt-2-world-attack",
            "deploy-unlikely": "hunt-2-world-attack",
        }
        for name, pairs in (overrides or {}).items():
            self.transitions[name] = pairs + self.transitions.get(name, [])

    def check(self) -> None:
        self.checked += 1

    def screenshot(self) -> Image:
        if self.clock is not None and self.screen in self.timed:
            at, target = self.timed[self.screen]
            if self.clock.now >= at:
                del self.timed[self.screen]
                self.screen = target
        if self.clock is not None and self.screen in self.transient:
            duration, target = self.transient[self.screen]
            if self.clock.now - self.entered >= duration:
                self.screen = target
        return self._images[self.screen]

    def tap(self, x: int, y: int) -> None:
        self.taps.append((self.screen, (x, y)))
        for point, target in self.transitions.get(self.screen, []):
            if near((x, y), point):
                self.screen = target
                self.entered = self.clock.now if self.clock is not None else 0.0
                return
        self.stray_taps.append((self.screen, (x, y)))

    def back(self) -> None:
        self.backs.append(self.screen)
        self.screen = self.back_transitions.get(self.screen, self.screen)

    def taps_on(self, screen: str) -> list[Point]:
        return [point for name, point in self.taps if name == screen]


class FakeClock:
    """Monotonic clock that only advances when the code under test sleeps."""

    def __init__(self) -> None:
        self.now = 0.0

    def sleep(self, seconds: float) -> None:
        self.now += seconds

    def clock(self) -> float:
        return self.now


@pytest.fixture
def game_factory(images: dict[str, Image]) -> Callable[..., FakeGame]:
    def factory(**kwargs: object) -> FakeGame:
        return FakeGame(images, **kwargs)  # type: ignore[arg-type]

    return factory


@pytest.fixture
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "state.json"
