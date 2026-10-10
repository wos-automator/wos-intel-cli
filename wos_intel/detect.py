"""Screen analysis: states, mission symbols, status, tier and digit OCR (TS-2.x).

Everything here is a pure function of a 720x1280 BGR screenshot plus the templates.
"""

from __future__ import annotations

import itertools
import logging
import math
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from pathlib import Path

import cv2
import numpy as np
import numpy.typing as npt

from wos_intel.config import Config, Hsv, Point, Region

log = logging.getLogger(__name__)

Image = npt.NDArray[np.uint8]

GLYPH_SIZE = 16
DIGITS_DIR = "digits"


class DetectError(RuntimeError):
    """A required template is missing or unreadable."""


class State(StrEnum):
    INTEL = "INTEL"
    INTEL_CLAIMABLE = "INTEL_CLAIMABLE"
    REWARDS = "REWARDS"
    MISSION_DIALOG = "MISSION_DIALOG"
    WORLD_TARGET = "WORLD_TARGET"
    DEPLOY = "DEPLOY"
    SQUAD = "SQUAD"
    VICTORY = "VICTORY"
    DEFEAT = "DEFEAT"
    WORLD = "WORLD"
    NO_STAMINA = "NO_STAMINA"
    NO_TROOPS = "NO_TROOPS"
    UNKNOWN = "UNKNOWN"


class MissionType(StrEnum):
    HUNT = "HUNT"
    RESCUE = "RESCUE"
    COMBAT = "COMBAT"
    BOSS = "BOSS"


class Tier(IntEnum):
    BLUE = 1
    PURPLE = 2
    GOLD = 3


class Status(StrEnum):
    AVAILABLE = "AVAILABLE"
    RUNNING = "RUNNING"
    DONE = "DONE"


class Action(StrEnum):
    EXPLORE = "EXPLORE"
    ATTACK = "ATTACK"
    RESCUE = "RESCUE"


MASK_TEMPLATES: dict[MissionType, str] = {
    MissionType.HUNT: "paw_mask",
    MissionType.RESCUE: "tent_mask",
    MissionType.COMBAT: "axe_mask",
    MissionType.BOSS: "skull_mask",
}

ACTION_TEMPLATES: dict[Action, str] = {
    Action.EXPLORE: "btn_explore_top",
    Action.ATTACK: "btn_attack",
    Action.RESCUE: "btn_rescue",
}

REQUIRED_TEMPLATES: tuple[str, ...] = (
    "btn_view",
    "btn_explore_top",
    "btn_attack",
    "btn_fight",
    "btn_deploy",
    "btn_claim_all",
    "intel_button",
    "intel_button_badge",
    "title_intel",
    "title_rewards",
    "expert_sign",
    "title_victory",
    "text_tap_anywhere",
    "text_likely_prevail",
)

# Screens without a reference screenshot yet (SPEC §2 "Noch offen"). As soon as the file
# exists in templates/ it takes part in the detection; until then it never matches.
OPTIONAL_TEMPLATES: tuple[str, ...] = ("btn_rescue", "dialog_no_stamina", "dialog_no_troops")


@dataclass(frozen=True)
class Match:
    name: str
    score: float
    x: int
    y: int

    @property
    def point(self) -> Point:
        return (self.x, self.y)


@dataclass(frozen=True)
class Symbol:
    type: MissionType
    x: int
    y: int
    score: float
    saturation: int
    status: Status
    tier: Tier

    @property
    def point(self) -> Point:
        return (self.x, self.y)

    def describe(self) -> str:
        return (
            f"{self.type} {self.tier.name} {self.status} at {self.x},{self.y} "
            f"(score {self.score:.2f}, sat {self.saturation})"
        )


@dataclass(frozen=True)
class Screen:
    state: State
    matches: dict[str, Match] = field(default_factory=dict)
    action: Action | None = None


def _hsv(image: Image) -> Image:
    return np.asarray(cv2.cvtColor(image, cv2.COLOR_BGR2HSV), dtype=np.uint8)


def _in_range(hsv: Image, lo: Hsv, hi: Hsv) -> Image:
    lower = np.array(lo, dtype=np.uint8)
    upper = np.array(hi, dtype=np.uint8)
    return np.asarray(cv2.inRange(hsv, lower, upper), dtype=np.uint8)


def _crop(image: Image, region: Region) -> Image:
    x0, y0, x1, y1 = region
    return image[max(0, y0) : y1, max(0, x0) : x1]


def _best_match(image: Image, template: Image) -> tuple[float, int, int]:
    """Best ``TM_CCOEFF_NORMED`` score and the centre of the match inside ``image``."""
    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
    _, score, _, location = cv2.minMaxLoc(result)
    height, width = template.shape[:2]
    return float(score), int(location[0]) + width // 2, int(location[1]) + height // 2


def hue_distance(a: int, b: int) -> int:
    """Distance on the circular OpenCV hue scale (0-179)."""
    delta = abs(a - b) % 180
    return min(delta, 180 - delta)


def normalize_glyph(glyph: Image) -> Image:
    """Scale a binary glyph to ``GLYPH_SIZE`` height and centre it on a square canvas."""
    height, width = glyph.shape[:2]
    scaled_width = max(1, min(GLYPH_SIZE, round(width * GLYPH_SIZE / height)))
    scaled = cv2.resize(glyph, (scaled_width, GLYPH_SIZE), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((GLYPH_SIZE, GLYPH_SIZE), dtype=np.uint8)
    left = (GLYPH_SIZE - scaled_width) // 2
    canvas[:, left : left + scaled_width] = scaled
    return canvas


def _split_touching(component: Image, parts: int) -> list[Image]:
    """Cut a component made of touching glyphs at its thinnest columns."""
    width = component.shape[1]
    columns = (component > 0).sum(axis=0)
    cuts = [0]
    for index in range(1, parts):
        centre = round(index * width / parts)
        slack = max(1, width // (4 * parts))
        lo, hi = max(cuts[-1] + 1, centre - slack), min(width - 1, centre + slack)
        cuts.append(lo + int(np.argmin(columns[lo : hi + 1])))
    cuts.append(width)
    return [component[:, start:end] for start, end in itertools.pairwise(cuts)]


def segment_glyphs(
    image: Image,
    lo: Hsv,
    hi: Hsv,
    min_height_ratio: float,
    min_height: int,
    max_aspect: float,
) -> list[Image]:
    """Split white text into glyphs (left to right); separators such as ``,`` and ``:`` drop out.

    A component wider than ``max_aspect`` times its height is two or more touching digits
    (bold "46" in the refresh timer) and is cut apart.
    """
    mask = _in_range(_hsv(image), lo, hi)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
    boxes = [
        (int(stats[i][0]), int(stats[i][1]), int(stats[i][2]), int(stats[i][3]), i)
        for i in range(1, count)
        if int(stats[i][3]) >= min_height
    ]
    if not boxes:
        return []
    tallest = max(box[3] for box in boxes)
    boxes = sorted(box for box in boxes if box[3] >= min_height_ratio * tallest)
    single = sorted(box[2] for box in boxes if box[2] <= max_aspect * box[3])
    typical = single[len(single) // 2] if single else 0.75 * tallest
    glyphs: list[Image] = []
    for x, y, width, height, label in boxes:
        component = (labels[y : y + height, x : x + width] == label).astype(np.uint8) * 255
        if width > max_aspect * height:
            glyphs.extend(_split_touching(component, max(2, round(width / typical))))
        else:
            glyphs.append(component)
    return glyphs


class Detector:
    """Loads the templates once and analyses screenshots."""

    def __init__(self, config: Config) -> None:
        self._config = config
        directory = config.path(config.paths.templates)
        self._templates: dict[str, Image] = {}
        for name in REQUIRED_TEMPLATES:
            self._templates[name] = self._read(directory / f"{name}.png", cv2.IMREAD_COLOR)
        for name in OPTIONAL_TEMPLATES:
            if (directory / f"{name}.png").is_file():
                self._templates[name] = self._read(directory / f"{name}.png", cv2.IMREAD_COLOR)
        self._masks: dict[MissionType, Image] = {
            kind: self._read(directory / f"{name}.png", cv2.IMREAD_GRAYSCALE)
            for kind, name in MASK_TEMPLATES.items()
        }
        self._glyphs: list[tuple[int, Image]] = []
        for path in sorted((directory / DIGITS_DIR).glob("[0-9]_*.png")):
            self._glyphs.append((int(path.name[0]), self._read(path, cv2.IMREAD_GRAYSCALE)))
        if not self._glyphs:
            raise DetectError(f"no digit templates in {directory / DIGITS_DIR}")

    @staticmethod
    def _read(path: Path, flags: int) -> Image:
        image = cv2.imread(str(path), flags)
        if image is None:
            raise DetectError(f"template missing or unreadable: {path}")
        return np.asarray(image, dtype=np.uint8)

    # ------------------------------------------------------------------ buttons / states

    def find(
        self,
        image: Image,
        name: str,
        region: Region | None = None,
        threshold: float | None = None,
    ) -> Match | None:
        """Match a colour template inside its configured region; ``None`` below the threshold."""
        template = self._templates.get(name)
        if template is None:
            return None
        area = region if region is not None else self._config.regions.get(name)
        x0, y0 = (max(0, area[0]), max(0, area[1])) if area is not None else (0, 0)
        search = _crop(image, area) if area is not None else image
        if search.shape[0] < template.shape[0] or search.shape[1] < template.shape[1]:
            return None
        score, x, y = _best_match(search, template)
        limit = self._config.buttons.threshold if threshold is None else threshold
        if score < limit:
            return None
        return Match(name, score, x + x0, y + y0)

    def find_action_button(self, image: Image) -> tuple[Action, Match] | None:
        """Locate the Explore/Attack/Rescue button of the world-map popup.

        Templates are searched in the popup band. Rescue has no template yet, so a button
        that is green by its median hue is classified as Rescue as well (SPEC §2).
        """
        buttons = self._config.buttons
        found: list[tuple[Action, Match]] = []
        for action, name in ACTION_TEMPLATES.items():
            match = self.find(image, name, region=buttons.action_region)
            if match is not None:
                found.append((action, match))
        if found:
            return max(found, key=lambda item: item[1].score)

        hsv = _hsv(_crop(image, buttons.color_region))
        selected = (hsv[..., 1] > buttons.color_min_saturation) & (
            hsv[..., 2] > buttons.color_min_value
        )
        fraction = float(selected.mean())
        if fraction < buttons.color_min_fraction:
            return None
        hue = int(np.median(hsv[..., 0][selected]))
        if not buttons.hue_rescue[0] <= hue <= buttons.hue_rescue[1]:
            return None
        x0, y0, x1, y1 = buttons.color_region
        return Action.RESCUE, Match("btn_rescue(colour)", fraction, (x0 + x1) // 2, (y0 + y1) // 2)

    def detect_state(self, image: Image) -> Screen:
        """Classify a screenshot; the returned matches are the tap targets of that screen."""
        for name, state in (
            ("dialog_no_stamina", State.NO_STAMINA),
            ("dialog_no_troops", State.NO_TROOPS),
        ):
            dialog = self.find(image, name)
            if dialog is not None:
                return Screen(state, {name: dialog})

        rewards = self.find(image, "title_rewards")
        if rewards is not None:
            return Screen(State.REWARDS, {"title_rewards": rewards})

        exit_text = self.find(image, "text_tap_anywhere")
        if exit_text is not None:
            victory = self.find(image, "title_victory")
            if victory is not None:
                return Screen(State.VICTORY, {"exit": exit_text, "title_victory": victory})
            # No reference screenshot for a defeat yet: a result screen without the
            # "Victory!" title is treated as one.
            return Screen(State.DEFEAT, {"exit": exit_text})

        for name, state in (
            ("btn_deploy", State.DEPLOY),
            ("btn_fight", State.SQUAD),
            ("btn_view", State.MISSION_DIALOG),
        ):
            button = self.find(image, name)
            if button is not None:
                return Screen(state, {name: button})

        action = self.find_action_button(image)
        if action is not None:
            return Screen(State.WORLD_TARGET, {"action": action[1]}, action[0])

        title = self.find(image, "title_intel")
        if title is not None:
            claim = self.find(image, "btn_claim_all")
            if claim is not None:
                return Screen(State.INTEL_CLAIMABLE, {"btn_claim_all": claim})
            return Screen(State.INTEL, {"title_intel": title})

        threshold = self._config.buttons.intel_button_threshold
        for name in ("intel_button", "intel_button_badge"):
            intel = self.find(image, name, threshold=threshold)
            if intel is not None:
                return Screen(State.WORLD, {"intel_button": intel})

        return Screen(State.UNKNOWN)

    def find_expert(self, image: Image) -> Match | None:
        """The expert sign top left on the Intel screen (once a day: more missions)."""
        return self.find(image, "expert_sign")

    def likely_to_prevail(self, image: Image) -> bool:
        """True if the Deploy screen shows the green "You are quite likely to prevail"."""
        return self.find(image, "text_likely_prevail") is not None

    def dialog_type(self, image: Image) -> tuple[MissionType, float] | None:
        """Mission type shown by the pin of the mission dialog, with its match score."""
        symbols = self._config.symbols
        x0, y0, x1, y1 = symbols.dialog_pin_region
        hsv = _hsv(_crop(image, (x0, y0, x1, y1)))
        white = _in_range(hsv, symbols.white_lo, symbols.white_hi)
        best: tuple[MissionType, float] | None = None
        for kind, mask in self._masks.items():
            for scale in symbols.dialog_pin_scales:
                scaled = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                score, _, _ = _best_match(white, np.asarray(scaled, dtype=np.uint8))
                if best is None or score > best[1]:
                    best = (kind, score)
        if best is None or best[1] < symbols.dialog_pin_threshold:
            return None
        return best

    # ------------------------------------------------------------------ symbols

    def _green_checks(self, hsv: Image) -> list[Point]:
        symbols = self._config.symbols
        green = _in_range(hsv, symbols.check_lo, symbols.check_hi)
        green[: symbols.search_y[0]] = 0
        green[symbols.search_y[1] :] = 0
        count, _, stats, centroids = cv2.connectedComponentsWithStats(green)
        return [
            (int(centroids[i][0]), int(centroids[i][1]))
            for i in range(1, count)
            if symbols.check_min_area < int(stats[i][4]) < symbols.check_max_area
        ]

    def _disc(self, hsv: Image, x: int, y: int) -> tuple[int, int]:
        """Median saturation and hue of the non-white pixels of the disc around ``x, y``."""
        symbols = self._config.symbols
        radius = symbols.disc_radius
        rows, columns = np.ogrid[: hsv.shape[0], : hsv.shape[1]]
        inside = (columns - x) ** 2 + (rows - y) ** 2 <= radius * radius
        coloured = inside & (_in_range(hsv, symbols.disc_white_lo, symbols.disc_white_hi) == 0)
        if not coloured.any():
            return 0, 0
        return int(np.median(hsv[..., 1][coloured])), int(np.median(hsv[..., 0][coloured]))

    def _tier(self, hue: int) -> Tier:
        symbols = self._config.symbols
        centres = {
            Tier.GOLD: symbols.hue_gold,
            Tier.PURPLE: symbols.hue_purple,
            Tier.BLUE: symbols.hue_blue,
        }
        return min(centres, key=lambda tier: hue_distance(hue, centres[tier]))

    def _mask_hits(self, hsv: Image, lo: Hsv, hi: Hsv) -> list[tuple[float, MissionType, int, int]]:
        """Symbol mask matches (score, type, x, y) on the white mask ``lo``-``hi``."""
        symbols = self._config.symbols
        radius = symbols.nms_radius
        white = _in_range(hsv, lo, hi)
        white[: symbols.search_y[0]] = 0
        white[symbols.search_y[1] :] = 0
        hits: list[tuple[float, MissionType, int, int]] = []
        for kind, mask in self._masks.items():
            result = cv2.matchTemplate(white, mask, cv2.TM_CCOEFF_NORMED)
            height, width = mask.shape[:2]
            while True:
                _, score, _, location = cv2.minMaxLoc(result)
                if score < symbols.match_threshold:
                    break
                left, top = int(location[0]), int(location[1])
                hits.append((float(score), kind, left + width // 2, top + height // 2))
                result[
                    max(0, top - radius) : top + radius, max(0, left - radius) : left + radius
                ] = -1
        return hits

    def detect_symbols(self, image: Image) -> list[Symbol]:
        """All mission symbols of the Intel screen, highest tier first, then top-down."""
        symbols = self._config.symbols
        hsv = _hsv(image)
        radius = symbols.nms_radius

        # A running mission is drawn half transparent: its symbol is no longer white enough
        # for the normal mask. A second pass with a wider mask finds those. It also picks up
        # a vivid pin the first pass narrowly missed (partly covered), so the status of its
        # hits is decided by the saturation like for any other hit.
        kept: list[tuple[float, MissionType, int, int]] = []
        for lo, hi in (
            (symbols.white_lo, symbols.white_hi),
            (symbols.dim_white_lo, symbols.dim_white_hi),
        ):
            hits = self._mask_hits(hsv, lo, hi)
            for score, kind, x, y in sorted(hits, key=lambda item: item[0], reverse=True):
                if all(math.hypot(x - other[2], y - other[3]) >= radius for other in kept):
                    kept.append((score, kind, x, y))

        checks = self._green_checks(hsv)
        offset_x, offset_y = symbols.check_offset
        found: list[Symbol] = []
        for score, kind, x, y in kept:
            saturation, hue = self._disc(hsv, x, y)
            done = any(
                abs(check_x - (x + offset_x)) < symbols.check_tolerance
                and abs(check_y - (y + offset_y)) < symbols.check_tolerance
                for check_x, check_y in checks
            )
            if done:
                status = Status.DONE
            elif saturation >= symbols.available_min_saturation:
                status = Status.AVAILABLE
            else:
                if saturation >= symbols.running_max_saturation:
                    log.debug("%s at %d,%d: ambiguous saturation %d", kind, x, y, saturation)
                status = Status.RUNNING
            found.append(Symbol(kind, x, y, round(score, 2), saturation, status, self._tier(hue)))
        return sorted(found, key=lambda symbol: (-symbol.tier, symbol.y, symbol.x))

    # ------------------------------------------------------------------ digit OCR

    def _read_digits(self, image: Image, region: Region, last: int = 0) -> list[int] | None:
        """Classify the glyphs of a region; ``last`` keeps only the rightmost glyphs."""
        ocr = self._config.ocr
        glyphs = segment_glyphs(
            _crop(image, region),
            ocr.white_lo,
            ocr.white_hi,
            ocr.glyph_min_height_ratio,
            ocr.glyph_min_height,
            ocr.glyph_max_aspect,
        )
        if len(glyphs) < last:
            return None
        digits: list[int] = []
        for glyph in glyphs[-last:]:
            normalized = normalize_glyph(glyph)
            score, digit = max(
                (_best_match(normalized, template)[0], value) for value, template in self._glyphs
            )
            if score < ocr.glyph_threshold:
                return None
            digits.append(digit)
        return digits or None

    def read_stamina(self, image: Image) -> int | None:
        """Stamina shown top right on the Intel screen; ``None`` if it cannot be read."""
        digits = self._read_digits(image, self._config.ocr.stamina_region)
        if digits is None or len(digits) > self._config.ocr.max_stamina_digits:
            return None
        return int("".join(str(digit) for digit in digits))

    def read_refresh_seconds(self, image: Image) -> int | None:
        """Seconds left on the "Refreshes In: HH:MM:SS" banner; ``None`` if unreadable."""
        digits = self._read_digits(image, self._config.ocr.timer_region, last=6)
        if digits is None:
            return None
        h1, h2, m1, m2, s1, s2 = digits
        minutes, seconds = m1 * 10 + m2, s1 * 10 + s2
        if minutes > 59 or seconds > 59:
            return None
        return (h1 * 10 + h2) * 3600 + minutes * 60 + seconds

    # ------------------------------------------------------------------ debug image

    def annotate(self, image: Image, screen: Screen, symbols: list[Symbol]) -> Image:
        """Copy of the screenshot with the state, the matches and the symbols drawn in."""
        out = image.copy()
        red, grey, green = (0, 0, 255), (128, 128, 128), (0, 200, 0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(out, screen.state, (10, 100), font, 0.8, red, 2)
        for match in screen.matches.values():
            cv2.drawMarker(out, match.point, green, cv2.MARKER_CROSS, 24, 2)
            label = f"{match.name} {match.score:.2f}"
            cv2.putText(out, label, (match.x - 60, match.y - 16), font, 0.45, green, 2)
        for symbol in symbols:
            colour = red if symbol.status is Status.AVAILABLE else grey
            cv2.circle(out, symbol.point, self._config.symbols.disc_radius + 1, colour, 2)
            label = f"{symbol.type} {symbol.tier.name} {symbol.status}"
            cv2.putText(out, label, (symbol.x - 60, symbol.y - 32), font, 0.45, colour, 2)
        return out
