"""Detection against the reference screenshots; expected values are SPEC.md §3.5 (US-2.x)."""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest
from pytest_mock import MockerFixture

from tests.conftest import load_ref
from wos_intel.config import Config
from wos_intel.detect import (
    Action,
    Detector,
    Image,
    MissionType,
    State,
    Status,
    Tier,
    hue_distance,
    normalize_glyph,
)

pytestmark = pytest.mark.unit

POSITION_TOLERANCE = 6

HUNT, RESCUE, COMBAT, BOSS = (
    MissionType.HUNT,
    MissionType.RESCUE,
    MissionType.COMBAT,
    MissionType.BOSS,
)
AVAILABLE, RUNNING, DONE = Status.AVAILABLE, Status.RUNNING, Status.DONE

Expected = tuple[MissionType, int, int, Status]

INTEL_X: list[Expected] = [
    (HUNT, 336, 289, AVAILABLE),
    (HUNT, 483, 315, AVAILABLE),
    (RESCUE, 287, 351, AVAILABLE),
    (COMBAT, 340, 378, AVAILABLE),
    (HUNT, 275, 677, AVAILABLE),
    (COMBAT, 568, 680, AVAILABLE),
    (BOSS, 518, 700, AVAILABLE),
]
INTEL_XX: list[Expected] = [
    (kind, x, y, RUNNING if kind is RESCUE else status) for kind, x, y, status in INTEL_X
]
INTEL_XXX: list[Expected] = [
    *((kind, x, y, DONE if kind is RESCUE else status) for kind, x, y, status in INTEL_X),
    (HUNT, 564, 737, DONE),
]


@pytest.mark.parametrize(
    ("name", "expected"),
    [("intel-x", INTEL_X), ("intel-xx", INTEL_XX), ("intel-xxx", INTEL_XXX)],
)
def test_symbols_match_the_spec_table(
    detector: Detector, name: str, expected: list[Expected]
) -> None:
    symbols = detector.detect_symbols(load_ref(name))

    assert len(symbols) == len(expected)
    for kind, x, y, status in expected:
        hits = [
            symbol
            for symbol in symbols
            if symbol.type is kind
            and abs(symbol.x - x) <= POSITION_TOLERANCE
            and abs(symbol.y - y) <= POSITION_TOLERANCE
        ]
        assert len(hits) == 1, f"{kind} at {x},{y}"
        assert hits[0].status is status, f"{kind} at {x},{y}"
        assert hits[0].score >= 0.75


def test_dimmed_running_boss_is_found(detector: Detector) -> None:
    symbols = detector.detect_symbols(load_ref("intel-boss-running"))

    assert len(symbols) == 1
    boss = symbols[0]
    assert boss.type is BOSS
    assert boss.status is RUNNING
    assert abs(boss.x - 518) <= POSITION_TOLERANCE and abs(boss.y - 700) <= POSITION_TOLERANCE
    assert boss.saturation < 130
    assert boss.score >= 0.75


def test_vivid_symbol_found_only_by_the_dim_pass_is_available(
    config: Config, mocker: MockerFixture
) -> None:
    # A partly covered pin can miss the first pass (seen on the device: score 0.76, sat 224).
    # Its saturation decides the status, not the pass that found it.
    detector = Detector(config)
    mocker.patch.object(detector, "_disc", return_value=(224, 143))

    (symbol,) = detector.detect_symbols(load_ref("intel-boss-running"))

    assert symbol.status is AVAILABLE


def test_running_symbol_has_low_saturation(detector: Detector) -> None:
    tent = next(s for s in detector.detect_symbols(load_ref("intel-xx")) if s.type is RESCUE)

    assert tent.saturation < 130
    assert tent.score == pytest.approx(0.88, abs=0.02)


def test_tiers_follow_the_pin_colour(detector: Detector) -> None:
    tiers = {(s.x, s.y): s.tier for s in detector.detect_symbols(load_ref("intel-xxx"))}

    def tier_at(x: int, y: int) -> Tier:
        return next(
            tier for (sx, sy), tier in tiers.items() if abs(sx - x) <= 6 and abs(sy - y) <= 6
        )

    assert tier_at(564, 737) is Tier.GOLD
    assert tier_at(518, 700) is Tier.GOLD
    assert tier_at(287, 351) is Tier.PURPLE
    assert tier_at(340, 378) is Tier.PURPLE
    assert tier_at(275, 677) is Tier.PURPLE
    assert tier_at(336, 289) is Tier.BLUE
    assert tier_at(483, 315) is Tier.BLUE
    assert tier_at(568, 680) is Tier.BLUE


def test_symbols_are_sorted_by_tier_then_top_down(detector: Detector) -> None:
    symbols = detector.detect_symbols(load_ref("intel-x"))

    keys = [(-symbol.tier, symbol.y) for symbol in symbols]
    assert keys == sorted(keys)
    assert symbols[0].type is BOSS
    assert [s.type for s in symbols[1:4]] == [RESCUE, COMBAT, HUNT]


def test_nothing_is_detected_outside_the_search_band(detector: Detector) -> None:
    for name in ("combat-1-dialog", "intel-xxxx"):
        for symbol in detector.detect_symbols(load_ref(name)):
            assert 170 <= symbol.y <= 1050


@pytest.mark.parametrize(
    ("name", "state"),
    [
        ("intel-x", State.INTEL),
        ("intel-xx", State.INTEL),
        ("intel-xxx", State.INTEL_CLAIMABLE),
        ("intel-xxxx", State.REWARDS),
        ("intel-boss-running", State.INTEL),
        ("combat-1-dialog", State.MISSION_DIALOG),
        ("hunt-1-dialog", State.MISSION_DIALOG),
        ("combat-2-world-explore", State.WORLD_TARGET),
        ("hunt-2-world-attack", State.WORLD_TARGET),
        ("combat-3-squad-fight", State.SQUAD),
        ("combat-4-victory", State.VICTORY),
        ("hunt-3-deploy", State.DEPLOY),
        ("boss-1-dialog", State.MISSION_DIALOG),
        ("boss-2-world-attack", State.WORLD_TARGET),
        ("boss-3-deploy", State.DEPLOY),
        ("world", State.WORLD),
        ("rescue-popup", State.WORLD_TARGET),
        ("defeat", State.DEFEAT),
    ],
)
def test_states(detector: Detector, images: dict[str, Image], name: str, state: State) -> None:
    assert detector.detect_state(images[name]).state is state


def test_unknown_state_for_a_blank_screen(detector: Detector) -> None:
    blank = np.zeros((1280, 720, 3), dtype=np.uint8)

    assert detector.detect_state(blank).state is State.UNKNOWN


@pytest.mark.parametrize(
    ("name", "key", "point"),
    [
        ("intel-xxx", "btn_claim_all", (360, 1128)),
        ("combat-1-dialog", "btn_view", (360, 933)),
        ("boss-1-dialog", "btn_view", (360, 870)),
        ("combat-2-world-explore", "action", (360, 615)),
        ("hunt-2-world-attack", "action", (360, 615)),
        ("combat-3-squad-fight", "btn_fight", (528, 1201)),
        ("combat-4-victory", "exit", (360, 1140)),
        ("hunt-3-deploy", "btn_deploy", (548, 1215)),
        ("world", "intel_button", (663, 862)),
    ],
)
def test_tap_targets(
    detector: Detector, images: dict[str, Image], name: str, key: str, point: tuple[int, int]
) -> None:
    match = detector.detect_state(images[name]).matches[key]

    assert abs(match.x - point[0]) <= POSITION_TOLERANCE
    assert abs(match.y - point[1]) <= POSITION_TOLERANCE


@pytest.mark.parametrize(
    ("name", "action"),
    [
        ("combat-2-world-explore", Action.EXPLORE),
        ("hunt-2-world-attack", Action.ATTACK),
        ("boss-2-world-attack", Action.ATTACK),
        ("rescue-popup", Action.RESCUE),
    ],
)
def test_action_button(
    detector: Detector, images: dict[str, Image], name: str, action: Action
) -> None:
    assert detector.detect_state(images[name]).action is action


def test_intel_button_with_badge_is_found(detector: Detector) -> None:
    match = detector.find(
        load_ref("hunt-2-world-attack"), "intel_button", threshold=0.85
    ) or detector.find(load_ref("hunt-2-world-attack"), "intel_button_badge", threshold=0.85)

    assert match is not None
    assert (match.x, match.y) == (663, 862)


def test_optional_template_never_matches_while_missing(detector: Detector) -> None:
    assert detector.find(load_ref("intel-x"), "dialog_no_stamina") is None


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("combat-1-dialog", COMBAT),
        ("hunt-1-dialog", HUNT),
        ("rescue-dialog", RESCUE),
        ("boss-1-dialog", BOSS),
    ],
)
def test_dialog_type(
    detector: Detector, images: dict[str, Image], name: str, kind: MissionType
) -> None:
    shown = detector.dialog_type(images[name])

    assert shown is not None
    assert shown[0] is kind


@pytest.mark.parametrize("name", ["hunt-1-dialog-banner", "rescue-1-dialog-banner"])
def test_dialog_type_is_unknown_while_a_banner_covers_the_pin(
    detector: Detector, name: str
) -> None:
    """Screenshots of the device run: a notification banner lies over the pin."""
    image = load_ref(name)

    assert detector.detect_state(image).state is State.MISSION_DIALOG
    assert detector.dialog_type(image) is None


def test_dialog_type_is_none_without_a_pin(detector: Detector) -> None:
    assert detector.dialog_type(load_ref("hunt-3-deploy")) is None


def test_expert_sign_is_found_top_left(detector: Detector, images: dict[str, Image]) -> None:
    match = detector.find_expert(images["intel-expert-available"])

    assert match is not None
    assert abs(match.x - 59) <= POSITION_TOLERANCE and abs(match.y - 210) <= POSITION_TOLERANCE
    assert detector.find_expert(images["expert-only-boss-running"]) is not None


@pytest.mark.parametrize("name", ["intel-x", "intel-xxx", "intel-boss-running", "intel-xxxx"])
def test_expert_sign_is_not_found_when_absent(detector: Detector, name: str) -> None:
    assert detector.find_expert(load_ref(name)) is None


def test_expert_reference_screen_is_read_completely(detector: Detector) -> None:
    image = load_ref("intel-expert-available")

    assert detector.detect_state(image).state is State.INTEL
    assert detector.read_stamina(image) == 2165
    assert detector.read_refresh_seconds(image) == 54 * 60 + 43
    symbols = detector.detect_symbols(image)
    assert len(symbols) == 8
    assert all(symbol.status is AVAILABLE for symbol in symbols)
    assert sum(symbol.type is BOSS for symbol in symbols) == 1
    assert [s.type for s in symbols if s.tier is Tier.GOLD and s.type is not BOSS] == [
        RESCUE,
        COMBAT,
    ]


def test_likely_to_prevail(detector: Detector, images: dict[str, Image]) -> None:
    assert detector.likely_to_prevail(images["hunt-3-deploy"])
    assert not detector.likely_to_prevail(images["deploy-unlikely"])
    # red "You are not likely to prevail" on the boss deploy screen
    assert not detector.likely_to_prevail(images["boss-3-deploy"])


@pytest.mark.parametrize(
    ("name", "stamina"),
    [("intel-x", 2047), ("intel-xx", 2035), ("intel-xxx", 2035), ("intel-boss-running", 1975)],
)
def test_stamina(detector: Detector, name: str, stamina: int) -> None:
    assert detector.read_stamina(load_ref(name)) == stamina


def test_stamina_is_none_when_unreadable(detector: Detector) -> None:
    assert detector.read_stamina(load_ref("intel-xxxx")) is None


@pytest.mark.parametrize(
    ("name", "seconds"),
    [
        ("intel-x", 6 * 3600 + 59 * 60 + 27),
        ("intel-xx", 6 * 3600 + 59 * 60 + 10),
        ("intel-xxx", 6 * 3600 + 59 * 60 + 5),
        # 02:46:03 - the bold "46" touches and has to be cut apart
        ("intel-boss-running", 2 * 3600 + 46 * 60 + 3),
    ],
)
def test_refresh_timer(detector: Detector, name: str, seconds: int) -> None:
    assert detector.read_refresh_seconds(load_ref(name)) == seconds


def test_refresh_timer_is_none_without_banner(detector: Detector) -> None:
    assert detector.read_refresh_seconds(load_ref("hunt-3-deploy")) is None


def test_digits_from_other_screens_are_read(config: Config) -> None:
    """Glyphs cut from the Deploy screen (1, 6, 8, 9) classify digits of that size."""
    region = (82, 178, 172, 212)
    ocr = dataclasses.replace(config.ocr, stamina_region=region)
    detector = Detector(dataclasses.replace(config, ocr=ocr))

    assert detector.read_stamina(load_ref("hunt-3-deploy")) == 169830


def test_hue_distance_wraps_around() -> None:
    assert hue_distance(175, 5) == 10
    assert hue_distance(16, 109) == 87


def test_normalize_glyph_keeps_narrow_glyphs_narrow() -> None:
    narrow = np.full((20, 5), 255, dtype=np.uint8)

    canvas = normalize_glyph(narrow)

    assert canvas.shape == (16, 16)
    assert int((canvas.sum(axis=0) > 0).sum()) == 4


def test_annotate_returns_a_marked_copy(detector: Detector) -> None:
    image = load_ref("intel-x")
    screen = detector.detect_state(image)

    out = detector.annotate(image, screen, detector.detect_symbols(image))

    assert out.shape == image.shape
    assert not np.array_equal(out, image)
