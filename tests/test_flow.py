"""The run loop against a scripted fake game built from the reference screenshots (US-3.x)."""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pytest
from pytest_mock import MockerFixture

from tests.conftest import (
    ACTION,
    AXE_BLUE,
    AXE_PURPLE,
    BOSS,
    BOSS_VIEW,
    CANCEL,
    CLAIM_ALL,
    DEPLOY,
    EXPERT,
    FIGHT,
    HINT,
    INTEL_BUTTON,
    PAW_BLUE_LEFT,
    PAW_BLUE_RIGHT,
    PAW_PURPLE,
    RECONNECT,
    RESULT_EXIT,
    REWARDS_EXIT,
    TENT,
    VIEW,
    WORLD_TARGET,
    FakeClock,
    FakeGame,
    near,
)
from wos_intel.config import Config
from wos_intel.detect import Detector, MissionType, Status, Symbol, Tier
from wos_intel.flow import Outcome, Runner, choose_target, find_occluder, mission_cost
from wos_intel.state import StateStore

pytestmark = pytest.mark.component

NOW = datetime(2026, 10, 9, 19, 0, 0)

GameFactory = Callable[..., FakeGame]


def make_runner(
    game: FakeGame,
    detector: Detector,
    state_file: Path,
    config: Config | None = None,
    **kwargs: object,
) -> Runner:
    clock = FakeClock()
    game.clock = clock
    if config is None:
        # short completion wait: the fake game never finishes a march unless a test says so
        config = Config()
        timing = dataclasses.replace(config.timing, completion_timeout=WAIT)
        config = dataclasses.replace(config, timing=timing)
    return Runner(
        config,
        game,
        detector,
        StateStore(state_file),
        sleep=clock.sleep,
        clock=clock.clock,
        now=lambda: NOW,
        **kwargs,  # type: ignore[arg-type]
    )


WAIT = 30.0


def tapped(game: FakeGame, screen: str, point: tuple[int, int]) -> bool:
    return any(near(tap, point, 8) for tap in game.taps_on(screen))


def test_full_run_starts_every_plausible_mission(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory()
    runner = make_runner(game, detector, state_file)

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.checked == 1
    assert game.stray_taps == []
    # 2 combat missions (axes) and 3 hunts (paws); the fake answers the boss and the tent
    # with a dialog of another type, so both are rejected by the plausibility check.
    assert runner.missions_started == 5
    assert len(game.taps_on("combat-3-squad-fight")) == 2
    assert len(game.taps_on("hunt-3-deploy")) == 3
    assert all(near(tap, FIGHT, 8) for tap in game.taps_on("combat-3-squad-fight"))
    assert all(near(tap, DEPLOY, 8) for tap in game.taps_on("hunt-3-deploy"))
    assert all(near(tap, RESULT_EXIT, 8) for tap in game.taps_on("combat-4-victory"))
    assert len(game.taps_on("world")) == 5
    assert all(near(tap, INTEL_BUTTON, 8) for tap in game.taps_on("world"))


def test_missions_are_processed_by_tier_then_top_down(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory()

    make_runner(game, detector, state_file).run()

    # by tier, then top-down; the boss (gold) only once nothing else is left
    order = [TENT, AXE_PURPLE, PAW_PURPLE, PAW_BLUE_LEFT, PAW_BLUE_RIGHT, AXE_BLUE, BOSS]
    taps = game.taps_on("intel-x")
    assert len(taps) == len(order)
    assert all(near(tap, point, 8) for tap, point in zip(taps, order, strict=True))


def test_mismatching_dialog_is_closed_with_back_and_not_retried(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory()

    make_runner(game, detector, state_file).run()

    # tent -> axe dialog, boss -> paw dialog: BACK without ever tapping "View" for them
    assert game.backs == ["combat-1-dialog", "hunt-1-dialog"]
    assert len(game.taps_on("hunt-1-dialog")) == 3
    assert len(game.taps_on("combat-1-dialog")) == 2
    assert sum(near(tap, BOSS, 8) for tap in game.taps_on("intel-x")) == 1


def test_claim_all_then_rewards_exit(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(start="intel-xxx")

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert tapped(game, "intel-xxx", CLAIM_ALL)
    assert game.taps_on("intel-xxxx") == [REWARDS_EXIT]
    assert game.taps[0] == ("intel-xxx", game.taps_on("intel-xxx")[0])
    assert game.stray_taps == []


def test_run_starting_on_the_world_map_opens_intel_first(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(start="world")

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.taps[0][0] == "world"
    assert near(game.taps[0][1], INTEL_BUTTON, 8)


def test_simple_battle_mode_hint_at_the_start_is_tapped_away(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """BUG-0002: the hint covers the world map the run starts on."""
    game = game_factory(start="world-simple-battle-mode")

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.taps[0] == ("world-simple-battle-mode", HINT)
    assert near(game.taps[1][1], INTEL_BUTTON, 8)
    assert "world-simple-battle-mode" not in game.backs
    assert game.stray_taps == []


def test_simple_battle_mode_hint_during_a_mission_costs_no_failure(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """BUG-0002: the hint appears on the world map a hunt returns to."""
    game = game_factory(overrides={"hunt-3-deploy": [(DEPLOY, "world-simple-battle-mode")]})
    runner = make_runner(game, detector, state_file)

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert runner.missions_started == 5
    assert game.taps_on("world-simple-battle-mode") == [HINT, HINT, HINT]
    assert "world-simple-battle-mode" not in game.backs
    assert game.stray_taps == []


@pytest.mark.parametrize("start", ["hunt-3-deploy", "combat-1-dialog", "intel-xxxx"])
def test_run_aborts_without_input_on_any_other_screen(
    game_factory: GameFactory, detector: Detector, state_file: Path, start: str
) -> None:
    game = game_factory(start=start)

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.WRONG_SCREEN
    assert not outcome.ok
    assert game.taps == []
    assert game.backs == []


@pytest.mark.parametrize("start", ["intel-x", "intel-xxx", "world"])
def test_dry_run_never_touches_the_device(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
    start: str,
) -> None:
    game = game_factory(start=start)
    caplog.set_level("INFO")

    outcome = make_runner(game, detector, state_file, dry_run=True).run()

    assert outcome is Outcome.DRY_RUN
    assert game.taps == []
    assert game.backs == []
    assert not state_file.exists()
    assert "dry run: would tap" in caplog.text


def test_dry_run_logs_symbols_and_stamina(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("INFO")

    make_runner(game_factory(), detector, state_file, dry_run=True).run()

    assert "state INTEL" in caplog.text
    assert "stamina 2047" in caplog.text
    assert caplog.text.count("symbol ") == 7
    assert "BOSS GOLD AVAILABLE at 518,700" in caplog.text


def test_run_ends_when_stamina_is_below_minimum(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=9)
    game = game_factory()

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.OUT_OF_STAMINA
    assert outcome.ok
    assert game.taps == []


def test_unaffordable_mission_is_skipped(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=11)
    game = game_factory()

    outcome = make_runner(game, detector, state_file).run()

    # everything affordable is worked off; only the 12-stamina rescue is left at the end
    assert outcome is Outcome.OUT_OF_STAMINA
    assert not tapped(game, "intel-x", TENT)
    assert tapped(game, "intel-x", AXE_PURPLE)


def test_run_continues_when_stamina_is_unreadable(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=None)
    game = game_factory()
    runner = make_runner(game, detector, state_file)

    assert runner.run() is Outcome.NOTHING_TO_DO
    assert runner.missions_started == 5


def test_hunt_without_prevail_hint_is_not_deployed(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"hunt-2-world-attack": [(ACTION, "deploy-unlikely")]})
    runner = make_runner(game, detector, state_file)

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.taps_on("deploy-unlikely") == []
    assert game.backs.count("deploy-unlikely") == 3
    assert runner.missions_started == 2
    assert "world" not in game.backs
    assert "intel-x" not in game.backs


def test_lost_fight_is_dismissed_and_the_run_continues(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"combat-3-squad-fight": [(FIGHT, "defeat")]})
    runner = make_runner(game, detector, state_file)

    assert runner.run() is Outcome.NOTHING_TO_DO
    assert len(game.taps_on("defeat")) == 2
    assert runner.missions_started == 5


def test_rescue_starts_without_deploy(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"intel-x": [(TENT, "rescue-dialog")]})
    runner = make_runner(game, detector, state_file)

    assert runner.run() is Outcome.NOTHING_TO_DO
    assert game.taps_on("rescue-dialog") == [VIEW]
    assert len(game.taps_on("rescue-popup")) == 1
    assert runner.missions_started == 6
    assert game.stray_taps == []


def banner_game(game_factory: GameFactory, banner_seconds: float | None) -> FakeGame:
    """Device run of 2026-10-10: hunt and rescue dialogs open under a notification banner.

    The banner hides the pin; after ``banner_seconds`` it is gone (``None``: it stays).
    The boss answers with its real dialog.
    """
    game = game_factory(
        overrides={
            "intel-x": [
                (PAW_PURPLE, "hunt-1-dialog-banner"),
                (PAW_BLUE_LEFT, "hunt-1-dialog-banner"),
                (PAW_BLUE_RIGHT, "hunt-1-dialog-banner"),
                (TENT, "rescue-1-dialog-banner"),
                (BOSS, "boss-1-dialog"),
            ]
        }
    )
    if banner_seconds is not None:
        game.transient["hunt-1-dialog-banner"] = (banner_seconds, "hunt-1-dialog")
        game.transient["rescue-1-dialog-banner"] = (banner_seconds, "rescue-dialog")
    return game


def test_missions_under_a_notification_banner_are_started_before_the_boss(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = banner_game(game_factory, banner_seconds=3.0)
    runner = make_runner(game, detector, state_file)

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    # nothing is tapped and nothing is closed while the pin is hidden
    assert game.taps_on("hunt-1-dialog-banner") == []
    assert game.taps_on("rescue-1-dialog-banner") == []
    assert game.backs == []
    assert game.stray_taps == []
    # every regular mission is started: 3 hunts, 1 rescue, 2 combats - and then the boss
    assert len(game.taps_on("hunt-3-deploy")) == 3
    assert len(game.taps_on("rescue-popup")) == 1
    assert len(game.taps_on("combat-3-squad-fight")) == 2
    assert runner.missions_started == 7
    intel_taps = game.taps_on("intel-x")
    assert len(intel_taps) == 7
    assert near(intel_taps[-1], BOSS, 8)
    assert sum(near(tap, BOSS, 8) for tap in intel_taps) == 1


def test_boss_is_not_attacked_before_a_mission_delayed_by_a_banner(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = banner_game(game_factory, banner_seconds=3.0)

    make_runner(game, detector, state_file).run()

    screens = [screen for screen, _ in game.taps]
    boss_dialog = screens.index("boss-1-dialog")
    last_regular = max(
        index
        for index, screen in enumerate(screens)
        if screen in ("hunt-3-deploy", "rescue-popup", "combat-3-squad-fight")
    )
    assert last_regular < boss_dialog


def test_dialog_that_stays_unreadable_is_closed_after_the_timeout(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = banner_game(game_factory, banner_seconds=None)
    runner = make_runner(game, detector, state_file)

    runner.run()

    assert game.taps_on("hunt-1-dialog-banner") == []
    assert game.backs.count("hunt-1-dialog-banner") == 3
    assert game.backs.count("rescue-1-dialog-banner") == 1
    assert runner.missions_started == 3  # the two combats and the boss


def test_popup_with_unexpected_action_is_rejected(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"hunt-1-dialog": [(VIEW, "combat-2-world-explore")]})
    runner = make_runner(game, detector, state_file)

    assert runner.run() is Outcome.NOTHING_TO_DO
    # hunts end up on an "Explore" popup: never tapped; only the 2 real combat missions run
    assert len(game.taps_on("combat-2-world-explore")) == 2
    assert runner.missions_started == 2


def test_target_whose_popup_did_not_open_is_tapped_again(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """BUG-0028: the game swallowed the tap that opens the popup of the hunt target."""
    game = game_factory(
        overrides={
            "hunt-1-dialog": [(VIEW, "hunt-2-world-no-popup")],
            "hunt-2-world-no-popup": [(WORLD_TARGET, "hunt-2-world-attack")],
        }
    )
    runner = make_runner(game, detector, state_file)

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert runner.missions_started == 5
    assert game.taps_on("hunt-2-world-no-popup") == [WORLD_TARGET] * 3
    assert len(game.taps_on("hunt-3-deploy")) == 3
    assert game.stray_taps == []


def test_pin_of_another_type_is_not_tapped(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """A combat target that ends on a map showing a hunt pin is not tapped there."""
    game = game_factory(overrides={"combat-1-dialog": [(VIEW, "hunt-2-world-no-popup")]})

    make_runner(game, detector, state_file).run()

    taps = game.taps_on("hunt-2-world-no-popup")
    assert len(taps) == 2  # one Intel button tap per combat target, never the hunt pin
    assert all(near(tap, INTEL_BUTTON, 8) for tap in taps)
    assert game.taps_on("combat-3-squad-fight") == []
    assert game.stray_taps == []


def test_boss_whose_popup_did_not_open_is_tapped_again_and_locked(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """BUG-0098: the game swallowed the tap that opens the popup of the boss."""
    game = game_factory(
        overrides={
            "intel-x": [(BOSS, "boss-1-dialog")],
            "boss-1-dialog": [(BOSS_VIEW, "boss-2-world-no-popup")],
            "boss-2-world-no-popup": [(WORLD_TARGET, "boss-2-world-attack")],
        }
    )
    runner = make_runner(game, detector, state_file)

    assert runner.run() is Outcome.NOTHING_TO_DO

    taps = game.taps_on("boss-2-world-no-popup")
    assert len(taps) == 1 and near(taps[0], WORLD_TARGET, 8)
    assert len(game.taps_on("boss-3-deploy")) == 1
    assert runner.missions_started == 6
    assert StateStore(state_file).boss_locked_until() is not None
    assert game.stray_taps == []


def test_boss_is_not_locked_when_its_popup_never_opens(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(
        overrides={
            "intel-x": [(BOSS, "boss-1-dialog")],
            "boss-1-dialog": [(BOSS_VIEW, "boss-2-world-no-popup")],
        }
    )
    runner = make_runner(game, detector, state_file)

    runner.run()

    assert game.taps_on("boss-3-deploy") == []
    assert StateStore(state_file).boss_locked_until() is None


def test_boss_is_locked_for_the_refresh_cycle(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"intel-x": [(BOSS, "boss-1-dialog")]})
    runner = make_runner(game, detector, state_file)

    assert runner.run() is Outcome.NOTHING_TO_DO

    assert runner.missions_started == 6
    refresh = timedelta(hours=6, minutes=59, seconds=27)
    assert StateStore(state_file).boss_locked_until() == NOW + refresh


def test_boss_lock_falls_back_to_configured_cycle(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_refresh_seconds", return_value=None)
    game = game_factory(overrides={"intel-x": [(BOSS, "boss-1-dialog")]})

    make_runner(game, detector, state_file).run()

    assert StateStore(state_file).boss_locked_until() == NOW + timedelta(hours=8)


def test_locked_boss_is_not_tapped(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    StateStore(state_file).lock_boss(NOW - timedelta(hours=1), 2 * 3600)
    game = game_factory()

    make_runner(game, detector, state_file).run()

    assert not tapped(game, "intel-x", BOSS)


def test_expired_boss_lock_is_ignored(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    StateStore(state_file).lock_boss(NOW - timedelta(hours=3), 2 * 3600)
    game = game_factory()

    make_runner(game, detector, state_file).run()

    assert tapped(game, "intel-x", BOSS)


def test_boss_is_attacked_once_after_everything_else(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"intel-x": [(BOSS, "boss-1-dialog")]})

    make_runner(game, detector, state_file).run()

    taps = game.taps_on("intel-x")
    assert near(taps[-1], BOSS, 8)
    assert sum(near(tap, BOSS, 8) for tap in taps) == 1
    assert game.taps_on("boss-1-dialog") == [BOSS_VIEW]


def test_boss_is_deployed_even_when_not_likely_to_prevail(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    game = game_factory(overrides={"intel-x": [(BOSS, "boss-1-dialog")]})
    runner = make_runner(game, detector, state_file)

    runner.run()

    assert len(game.taps_on("boss-2-world-attack")) == 1
    assert len(game.taps_on("boss-3-deploy")) == 1
    assert near(game.taps_on("boss-3-deploy")[0], DEPLOY, 8)
    assert "boss-3-deploy" not in game.backs
    assert runner.missions_started == 6
    assert game.stray_taps == []
    assert 'deploying without "You are quite likely to prevail"' in caplog.text


def test_boss_is_attacked_when_it_is_the_only_affordable_mission(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=10)
    game = game_factory(overrides={"intel-x": [(BOSS, "boss-1-dialog")]})

    make_runner(game, detector, state_file).run()

    assert not tapped(game, "intel-x", TENT)
    assert tapped(game, "intel-x", BOSS)
    assert near(game.taps_on("intel-x")[-1], BOSS, 8)


def test_run_waits_for_running_missions_and_claims_them(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    # intel-xx shows the tent as RUNNING; after 200 s of fake time it is done (intel-xxx)
    game = game_factory(start="intel-xx", intel="intel-xx")
    game.timed["intel-xx"] = (200.0, "intel-xxx")
    game.transitions["intel-xxx"] = [(CLAIM_ALL, "intel-xxxx")]
    game.transitions["intel-xxxx"] = [(REWARDS_EXIT, "intel-x")]
    game.back_transitions["combat-1-dialog"] = "intel-x"
    runner = make_runner(game, detector, state_file, Config())

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert runner.missions_started == 5
    assert len(game.taps_on("intel-xxx")) == 1
    assert near(game.taps_on("intel-xxx")[0], CLAIM_ALL, 8)
    assert game.taps_on("intel-xxxx") == [REWARDS_EXIT]
    assert game.clock is not None and 200.0 <= game.clock.now < 900.0
    assert game.stray_taps == []
    # the boss was rejected before the wait; the tent, available again on the fake's
    # intel-x after the claim, is rejected afterwards
    assert game.backs == ["hunt-1-dialog", "combat-1-dialog"]


def test_waiting_for_running_missions_gives_up_after_the_timeout(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    game = game_factory(start="intel-xx", intel="intel-xx")
    caplog.set_level("INFO")

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert "waiting up to 30 s for running missions (1 shown as running" in caplog.text
    assert "did not finish in time" in caplog.text
    assert game.stray_taps == []
    assert "intel-xx" not in game.backs


def test_running_boss_is_not_tapped_but_waited_for(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    game = game_factory(start="intel-boss-running")
    caplog.set_level("INFO")

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.taps == []
    assert game.backs == []
    assert "BOSS GOLD RUNNING at 518,700" in caplog.text
    assert "waiting up to 30 s for running missions (1 shown as running" in caplog.text


def test_expert_is_tapped_when_no_regular_mission_is_left(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    # only the running boss is on the screen; the expert then hands out the missions of intel-x
    game = game_factory(start="expert-only-boss-running")
    runner = make_runner(game, detector, state_file)

    runner.run()

    assert game.taps[0][0] == "expert-only-boss-running"
    assert near(game.taps[0][1], EXPERT, 8)
    assert len(game.taps_on("expert-only-boss-running")) == 1
    assert runner.missions_started == 5
    assert game.stray_taps == []


def test_expert_comes_after_the_regular_missions_and_before_the_boss(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(start="expert-and-missions", intel="expert-and-missions")

    make_runner(game, detector, state_file).run()

    taps = game.taps_on("expert-and-missions")
    regular = [TENT, AXE_PURPLE, PAW_PURPLE, PAW_BLUE_LEFT, PAW_BLUE_RIGHT, AXE_BLUE]
    assert len(taps) == len(regular) + 1
    assert all(near(tap, point, 8) for tap, point in zip(taps, regular, strict=False))
    assert near(taps[-1], EXPERT, 8)
    # the boss is only tapped afterwards, on the screen the expert leads to
    assert [near(tap, BOSS, 8) for tap in game.taps_on("intel-x")] == [True]


def test_expert_is_left_alone_while_regular_missions_are_available(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    game = game_factory(start="intel-expert-available")
    caplog.set_level("INFO")

    outcome = make_runner(game, detector, state_file, dry_run=True).run()

    assert outcome is Outcome.DRY_RUN
    # the sign is reported as seen, but the planned tap is a mission
    assert "expert sign at 59,210 (score 1.00)" in caplog.text
    assert "expert_sign" not in caplog.text
    assert "dry run: would tap 380,323 (RESCUE GOLD AVAILABLE" in caplog.text


def test_expert_is_used_even_without_stamina(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=9)
    game = game_factory(start="expert-only-boss-running")

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.OUT_OF_STAMINA
    assert len(game.taps) == 1
    assert near(game.taps[0][1], EXPERT, 8)


def test_expert_is_tapped_only_once_per_run(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(start="expert-only-boss-running")
    game.transitions["expert-only-boss-running"] = []  # the sign stays whatever is tapped

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert len(game.taps) == 1
    assert game.backs == []


def test_dry_run_reports_the_expert_tap(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    game = game_factory(start="expert-only-boss-running")
    caplog.set_level("INFO")

    outcome = make_runner(game, detector, state_file, dry_run=True).run()

    assert outcome is Outcome.DRY_RUN
    assert game.taps == []
    assert "dry run: would tap 59,210 (expert_sign)" in caplog.text


def test_nothing_running_ends_without_waiting(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=9)
    game = game_factory()

    assert make_runner(game, detector, state_file).run() is Outcome.OUT_OF_STAMINA
    assert game.clock is not None and game.clock.now == 0.0


def test_dry_run_reports_the_wait_instead_of_waiting(
    game_factory: GameFactory,
    detector: Detector,
    state_file: Path,
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocker.patch.object(detector, "read_stamina", return_value=9)
    game = game_factory(start="intel-xx")
    caplog.set_level("INFO")

    outcome = make_runner(game, detector, state_file, dry_run=True).run()

    assert outcome is Outcome.OUT_OF_STAMINA
    assert "dry run: would wait for running missions and claim all" in caplog.text
    assert game.taps == [] and game.clock is not None and game.clock.now == 0.0


def test_screenshot_of_a_skipped_mission_is_kept(
    game_factory: GameFactory, detector: Detector, state_file: Path, tmp_path: Path
) -> None:
    game = game_factory()

    make_runner(game, detector, state_file, failure_dir=tmp_path / "debug").run()

    saved = sorted(path.name for path in (tmp_path / "debug").iterdir())
    assert len(saved) == 2
    assert all(name.startswith("failure-") and "MISSION_DIALOG" in name for name in saved)


def test_mission_limit_ends_the_run(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    config = Config()
    config = dataclasses.replace(config, limits=dataclasses.replace(config.limits, max_missions=1))
    game = game_factory()
    runner = make_runner(game, detector, state_file, config)

    assert runner.run() is Outcome.MISSION_LIMIT
    assert runner.missions_started == 1


def test_run_ends_after_three_consecutive_failures(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory()
    game.transitions["intel-x"] = []  # symbol taps have no effect

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.TOO_MANY_FAILURES
    assert not outcome.ok
    assert len(game.taps) == 3
    assert game.backs == []  # still on INTEL: BACK would leave the screen


def test_unknown_screen_is_left_with_back(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    game = game_factory(overrides={"intel-x": [(BOSS, "intel-xxxx-stuck")]})
    game._images["intel-xxxx-stuck"] = game._images["hunt-3-deploy"]  # not a mission dialog
    game.back_transitions["intel-xxxx-stuck"] = "intel-x"

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.backs.count("intel-xxxx-stuck") == 1
    assert game.taps_on("intel-xxxx-stuck") == []


def test_quit_confirmation_after_back_is_cancelled(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """BUG-0006: BACK on a screen with nothing open asks "Quit game?"."""
    game = game_factory(overrides={"intel-x": [(BOSS, "city")]})
    game._images["city"] = np.zeros((1280, 720, 3), dtype=np.uint8)  # UNKNOWN
    game.back_transitions["city"] = "dialog-quit-game"
    game.transitions["dialog-quit-game"] = [(CANCEL, "world")]

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.backs.count("city") == 1
    assert "dialog-quit-game" not in game.backs
    assert game.taps_on("dialog-quit-game") == [CANCEL]
    assert game.stray_taps == []


def record_tap_times(game: FakeGame, monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, float]]:
    """(screen, fake time) of every tap."""
    times: list[tuple[str, float]] = []
    original = game.tap

    def tap(x: int, y: int) -> None:
        assert game.clock is not None
        times.append((game.screen, game.clock.now))
        original(x, y)

    monkeypatch.setattr(game, "tap", tap)
    return times


def test_session_is_reclaimed_a_minute_after_a_login_elsewhere(
    game_factory: GameFactory, detector: Detector, state_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """BUG-0095a: the player logged in on another device before the run started."""
    game = game_factory(start="dialog-logged-in-elsewhere")
    runner = make_runner(game, detector, state_file)
    times = record_tap_times(game, monkeypatch)

    outcome = runner.run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.taps[0] == ("dialog-logged-in-elsewhere", RECONNECT)
    assert times[0][1] >= 60.0
    assert near(game.taps[1][1], INTEL_BUTTON, 8)
    assert game.backs.count("dialog-logged-in-elsewhere") == 0
    assert game.stray_taps == []


def test_login_elsewhere_during_a_mission_costs_no_failure(
    game_factory: GameFactory, detector: Detector, state_file: Path
) -> None:
    """BUG-0095a: the session is taken over while the hunts are deployed."""
    game = game_factory(overrides={"hunt-3-deploy": [(DEPLOY, "dialog-logged-in-elsewhere")]})

    outcome = make_runner(game, detector, state_file).run()

    assert outcome is Outcome.NOTHING_TO_DO
    assert game.taps_on("dialog-logged-in-elsewhere") == [RECONNECT] * 3
    assert len(game.taps_on("combat-3-squad-fight")) == 2
    assert game.stray_taps == []


def test_expect_polls_until_the_timeout(
    game_factory: GameFactory, detector: Detector, state_file: Path, mocker: MockerFixture
) -> None:
    game = game_factory()
    game.transitions["intel-x"] = []
    shots = mocker.spy(game, "screenshot")

    make_runner(game, detector, state_file).run()

    # per failed step: 1 screenshot for the Intel screen, then polling every 0.7 s for 8 s
    # (13 screenshots), then 1 for the recovery after the first two failures
    assert shots.call_count == 1 + 3 * (1 + 13) + 2


def symbol(
    kind: MissionType, x: int, y: int, status: Status = Status.AVAILABLE, tier: Tier = Tier.BLUE
) -> Symbol:
    return Symbol(kind, x, y, 1.0, 220, status, tier)


def test_choose_target_without_overlap(config: Config) -> None:
    first = symbol(MissionType.HUNT, 100, 300)
    second = symbol(MissionType.COMBAT, 300, 300)

    assert choose_target(config, [first, second], [first, second]) == (first, (100, 300))


def test_choose_target_prefers_the_workable_symbol_in_front(config: Config) -> None:
    back = symbol(MissionType.HUNT, 100, 300, tier=Tier.GOLD)
    front = symbol(MissionType.COMBAT, 110, 320)

    assert find_occluder(config, back, [back, front]) == front
    assert find_occluder(config, front, [back, front]) is None
    assert choose_target(config, [back, front], [back, front]) == (front, (110, 320))


def test_choose_target_taps_the_disc_edge_opposite_a_blocked_occluder(config: Config) -> None:
    back = symbol(MissionType.HUNT, 100, 300)
    front = symbol(MissionType.COMBAT, 100, 325, status=Status.RUNNING)

    target, point = choose_target(config, [back], [back, front])

    assert target == back
    assert point == (100, 280)


def test_symbols_further_apart_than_the_overlap_distance_do_not_occlude(config: Config) -> None:
    back = symbol(MissionType.HUNT, 100, 300)
    front = symbol(MissionType.COMBAT, 100, 331)

    assert find_occluder(config, back, [back, front]) is None


def test_boss_ring_offset_counts_for_the_depth_order(config: Config) -> None:
    pin = symbol(MissionType.HUNT, 100, 305)
    boss = symbol(MissionType.BOSS, 100, 300)

    # the boss ring is 65 px below its centre, the pin ring 55 px: the boss is in front
    assert find_occluder(config, pin, [pin, boss]) == boss


def test_mission_costs(config: Config) -> None:
    assert mission_cost(config, MissionType.HUNT) == 10
    assert mission_cost(config, MissionType.RESCUE) == 12
    assert mission_cost(config, MissionType.COMBAT) == 10
    assert mission_cost(config, MissionType.BOSS) == 10
