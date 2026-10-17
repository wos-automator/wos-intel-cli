"""Main loop / state machine of an Intel run (TS-3.x).

Every decision is based on a fresh screenshot; taps only go to detected targets, with the
one documented exception of the exit tap on the rewards screen (FR-4.1).
"""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable, Collection
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Protocol

import cv2

from wos_intel.config import Config, Point
from wos_intel.detect import (
    Action,
    Detector,
    Image,
    Match,
    MissionType,
    Screen,
    State,
    Status,
    Symbol,
)
from wos_intel.state import StateStore

log = logging.getLogger(__name__)

INTEL_STATES = frozenset({State.INTEL, State.INTEL_CLAIMABLE})
RESULT_STATES = frozenset({State.VICTORY, State.DEFEAT})

ACTION_FOR: dict[MissionType, Action] = {
    MissionType.COMBAT: Action.EXPLORE,
    MissionType.HUNT: Action.ATTACK,
    MissionType.BOSS: Action.ATTACK,
    MissionType.RESCUE: Action.RESCUE,
}


class Outcome(StrEnum):
    NOTHING_TO_DO = "nothing to do"
    OUT_OF_STAMINA = "not enough stamina"
    NO_TROOPS = "no troops or march slots available"
    MISSION_LIMIT = "mission limit reached"
    DRY_RUN = "dry run finished"
    WRONG_SCREEN = "game is neither on the Intel screen nor on the world map"
    TOO_MANY_FAILURES = "too many consecutive failures"

    @property
    def ok(self) -> bool:
        return self not in (Outcome.WRONG_SCREEN, Outcome.TOO_MANY_FAILURES)


class Device(Protocol):
    def check(self) -> None: ...
    def screenshot(self) -> Image: ...
    def tap(self, x: int, y: int) -> None: ...
    def back(self) -> None: ...


class StepFailed(Exception):
    """An expected screen did not appear in time."""


class MissionRejected(Exception):
    """A plausibility or safety check failed; the mission is skipped for this run."""


class RunEnded(Exception):
    """The run has to end regularly from within a mission."""

    def __init__(self, outcome: Outcome) -> None:
        super().__init__(outcome.value)
        self.outcome = outcome


def mission_cost(config: Config, kind: MissionType) -> int:
    costs = config.costs
    return {
        MissionType.HUNT: costs.hunt,
        MissionType.RESCUE: costs.rescue,
        MissionType.COMBAT: costs.combat,
        MissionType.BOSS: costs.boss,
    }[kind]


def _ring_y(config: Config, symbol: Symbol) -> int:
    symbols = config.symbols
    offset = (
        symbols.ring_offset_boss if symbol.type is MissionType.BOSS else symbols.ring_offset_pin
    )
    return symbol.y + offset


def find_occluder(config: Config, target: Symbol, symbols: Collection[Symbol]) -> Symbol | None:
    """A symbol that covers the click point of ``target``: close to it and further in front."""
    covering = [
        other
        for other in symbols
        if other != target
        and math.hypot(other.x - target.x, other.y - target.y) < config.symbols.overlap_distance
        and _ring_y(config, other) > _ring_y(config, target)
    ]
    return max(covering, key=lambda other: _ring_y(config, other), default=None)


def choose_target(
    config: Config, candidates: list[Symbol], symbols: Collection[Symbol]
) -> tuple[Symbol, Point]:
    """Pick the mission to start and where to tap it (SPEC §3.5 step 5).

    ``candidates`` are the workable symbols in processing order, ``symbols`` everything
    detected. A covered symbol yields to a workable symbol in front of it; if the one in
    front cannot be worked on, the tap moves to the disc edge opposite to it.
    """
    target = candidates[0]
    for _ in candidates:
        occluder = find_occluder(config, target, symbols)
        if occluder is None:
            return target, target.point
        if occluder not in candidates:
            distance = math.hypot(target.x - occluder.x, target.y - occluder.y) or 1.0
            radius = config.symbols.edge_tap_radius
            return target, (
                round(target.x + (target.x - occluder.x) / distance * radius),
                round(target.y + (target.y - occluder.y) / distance * radius),
            )
        target = occluder
    return target, target.point


class Runner:
    """Drives one run: claim rewards, start missions, stop when nothing is left."""

    def __init__(
        self,
        config: Config,
        device: Device,
        detector: Detector,
        store: StateStore,
        *,
        dry_run: bool = False,
        debug_dir: Path | None = None,
        failure_dir: Path | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        now: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._config = config
        self._device = device
        self._detector = detector
        self._store = store
        self._dry_run = dry_run
        self._debug_dir = debug_dir
        self._sleep = sleep
        self._clock = clock
        self._now = now
        self._failure_dir = failure_dir
        self._step = 0
        self._last: tuple[Screen, Image] | None = None
        self._attempted: list[Symbol] = []
        self._unclaimed = 0
        self._expert_used = False
        self.missions_started = 0

    # ------------------------------------------------------------------ primitives

    def _observe(self) -> tuple[Screen, Image]:
        """Fresh screenshot and its state; a hint bubble over it is tapped away first."""
        screen, image = self._look()
        for _ in range(self._config.limits.max_back):
            if screen.state is not State.HINT or self._dry_run:
                break
            self._tap_match(screen.matches["hint"])
            screen, image = self._look()
        return screen, image

    def _look(self) -> tuple[Screen, Image]:
        image = self._device.screenshot()
        screen = self._detector.detect_state(image)
        self._step += 1
        log.info("state %s", screen.state)
        if self._debug_dir is not None:
            symbols = self._detector.detect_symbols(image) if screen.state in INTEL_STATES else []
            self._debug_dir.mkdir(parents=True, exist_ok=True)
            target = self._debug_dir / f"{self._step:04d}-{screen.state}.png"
            cv2.imwrite(str(target), self._detector.annotate(image, screen, symbols))
        self._last = (screen, image)
        return screen, image

    def _save_failure(self) -> None:
        """Keep the screenshot a skipped mission or failed step ended on, for diagnosis."""
        if self._failure_dir is None or self._last is None:
            return
        screen, image = self._last
        self._failure_dir.mkdir(parents=True, exist_ok=True)
        target = self._failure_dir / f"failure-{self._step:04d}-{screen.state}.png"
        cv2.imwrite(str(target), image)
        log.info("saved %s", target)

    def _tap(self, point: Point, reason: str) -> None:
        log.info("tap %d,%d (%s)", point[0], point[1], reason)
        self._device.tap(point[0], point[1])
        self._sleep(self._config.timing.tap_delay)

    def _tap_match(self, match: Match) -> None:
        self._tap(match.point, match.name)

    def _back(self, reason: str) -> None:
        log.info("BACK (%s)", reason)
        self._device.back()
        self._sleep(self._config.timing.tap_delay)

    def _expect(
        self, states: Collection[State], timeout: float | None = None
    ) -> tuple[Screen, Image]:
        """Poll with fresh screenshots until one of ``states`` shows up."""
        timing = self._config.timing
        deadline = self._clock() + (timing.expect_timeout if timeout is None else timeout)
        while True:
            screen, image = self._observe()
            if screen.state in states:
                return screen, image
            if self._clock() >= deadline:
                wanted = "|".join(sorted(states))
                raise StepFailed(f"expected {wanted}, screen is {screen.state}")
            self._sleep(timing.poll_interval)

    def _recover(self) -> None:
        """Leave an unexpected screen: BACK up to ``max_back`` times, never on INTEL/WORLD."""
        for _ in range(self._config.limits.max_back):
            screen, _ = self._observe()
            if screen.state in INTEL_STATES or screen.state is State.WORLD:
                return
            if screen.state is State.REWARDS:
                self._tap(self._config.buttons.rewards_exit, "rewards exit")
            elif screen.state in RESULT_STATES:
                self._tap_match(screen.matches["exit"])
            elif screen.state is State.QUIT_CONFIRMATION:
                # The last BACK hit a screen with nothing open: one more would quit the game.
                self._tap_match(screen.matches["btn_cancel"])
                return
            else:
                self._back(f"leaving {screen.state}")

    def _enter_intel(self) -> tuple[Screen, Image]:
        """Return on the Intel screen, opening it from the world map if necessary."""
        screen, image = self._observe()
        if screen.state is State.WORLD:
            self._tap_match(screen.matches["intel_button"])
            return self._expect(INTEL_STATES)
        if screen.state not in INTEL_STATES:
            raise StepFailed(f"expected the Intel screen, screen is {screen.state}")
        return screen, image

    # ------------------------------------------------------------------ run

    def run(self) -> Outcome:
        self._device.check()
        screen, _ = self._observe()
        if screen.state is State.WORLD:
            if self._dry_run:
                match = screen.matches["intel_button"]
                log.info("dry run: would tap %d,%d (%s)", match.x, match.y, match.name)
                return Outcome.DRY_RUN
        elif screen.state not in INTEL_STATES:
            log.error("%s (state %s)", Outcome.WRONG_SCREEN.value, screen.state)
            return Outcome.WRONG_SCREEN

        failures = 0
        while True:
            try:
                outcome = self._iteration()
            except RunEnded as ended:
                return ended.outcome
            except MissionRejected as rejected:
                log.warning("mission skipped for this run: %s", rejected)
                self._save_failure()
                self._recover()
                continue
            except StepFailed as failed:
                failures += 1
                log.warning("step failed (%d in a row): %s", failures, failed)
                self._save_failure()
                if failures >= self._config.limits.max_failures:
                    return Outcome.TOO_MANY_FAILURES
                self._recover()
                continue
            if outcome is not None:
                return outcome
            failures = 0

    def _iteration(self) -> Outcome | None:
        screen, image = self._enter_intel()
        stamina = self._detector.read_stamina(image)
        log.info("stamina %s", "unreadable" if stamina is None else stamina)

        if screen.state is State.INTEL_CLAIMABLE:
            claim = screen.matches["btn_claim_all"]
            if not self._dry_run:
                self._claim(claim)
                return None
            log.info("dry run: would tap %d,%d (%s)", claim.x, claim.y, claim.name)

        symbols = self._detector.detect_symbols(image)
        for symbol in symbols:
            log.info("symbol %s", symbol.describe())
        expert = self._detector.find_expert(image)
        if expert is not None:
            log.info("expert sign at %d,%d (score %.2f)", expert.x, expert.y, expert.score)

        if self.missions_started >= self._config.limits.max_missions:
            return self._settle(Outcome.MISSION_LIMIT, symbols)

        candidates = self._candidates(symbols)
        # The expert hands out more missions once a day. Use it as soon as no regular mission
        # is left - before the boss, and even if the stamina is used up - so it is not lost.
        only_boss_left = all(symbol.type is MissionType.BOSS for symbol in candidates)
        if expert is not None and only_boss_left and not self._expert_used:
            if self._dry_run:
                log.info("dry run: would tap %d,%d (%s)", expert.x, expert.y, expert.name)
                return Outcome.DRY_RUN
            self._expert_used = True
            self._tap_match(expert)
            return None

        if stamina is not None and stamina < self._config.limits.min_stamina:
            return self._settle(Outcome.OUT_OF_STAMINA, symbols)
        if not candidates:
            return self._settle(Outcome.NOTHING_TO_DO, symbols)
        affordable = [
            symbol
            for symbol in candidates
            if stamina is None or stamina >= mission_cost(self._config, symbol.type)
        ]
        if not affordable:
            return self._settle(Outcome.OUT_OF_STAMINA, symbols)

        # The boss comes last: only once nothing else is left to work on.
        others = [symbol for symbol in affordable if symbol.type is not MissionType.BOSS]
        target, point = choose_target(self._config, others or affordable, symbols)
        if self._dry_run:
            log.info("dry run: would tap %d,%d (%s)", point[0], point[1], target.describe())
            return Outcome.DRY_RUN

        self._attempted.append(target)
        self._run_mission(target, point, self._detector.read_refresh_seconds(image))
        return None

    def _claim(self, claim: Match) -> None:
        self._tap_match(claim)
        self._expect({State.REWARDS})
        self._tap(self._config.buttons.rewards_exit, "rewards exit")
        self._expect(INTEL_STATES)
        self._unclaimed = 0

    def _settle(self, final: Outcome, symbols: list[Symbol]) -> Outcome | None:
        """Before ending with ``final``: wait for running missions and claim their rewards.

        Returns ``None`` after a claim so that the loop looks at the Intel screen again.
        """
        running = sum(symbol.status is Status.RUNNING for symbol in symbols)
        if running == 0 and self._unclaimed == 0:
            return final
        timing = self._config.timing
        if self._dry_run:
            log.info("dry run: would wait for running missions and claim all")
            return final
        log.info(
            "waiting up to %.0f s for running missions (%d shown as running, %d started "
            "since the last claim)",
            timing.completion_timeout,
            running,
            self._unclaimed,
        )
        deadline = self._clock() + timing.completion_timeout
        while self._clock() < deadline:
            self._sleep(timing.completion_poll)
            screen, _ = self._observe()
            if screen.state is State.INTEL_CLAIMABLE:
                self._claim(screen.matches["btn_claim_all"])
                return None
            if screen.state is not State.INTEL:
                raise StepFailed(f"left the Intel screen while waiting, screen is {screen.state}")
        log.warning("running missions did not finish in time; rewards are not claimed")
        return final

    def _candidates(self, symbols: list[Symbol]) -> list[Symbol]:
        boss_locked = self._store.boss_locked(self._now())
        radius = self._config.symbols.lock_radius
        candidates: list[Symbol] = []
        for symbol in symbols:
            if symbol.status is not Status.AVAILABLE:
                continue
            if symbol.type is MissionType.BOSS and boss_locked:
                log.info("boss already attacked in this refresh cycle, skipping")
                continue
            if any(
                done.type is symbol.type
                and math.hypot(done.x - symbol.x, done.y - symbol.y) <= radius
                for done in self._attempted
            ):
                continue
            candidates.append(symbol)
        return candidates

    # ------------------------------------------------------------------ mission

    def _run_mission(self, target: Symbol, point: Point, refresh_seconds: int | None) -> None:
        log.info("starting %s", target.describe())
        self._tap(point, f"{target.type} symbol")
        screen, image = self._expect({State.MISSION_DIALOG})
        shown = self._detector.dialog_type(image)
        # A notification banner ("Troops have returned to the city.") can slide over the pin
        # for a few seconds. An unreadable pin is therefore looked at again; only a pin that
        # clearly shows another type, or stays unreadable, rejects the mission.
        timing = self._config.timing
        deadline = self._clock() + timing.expect_timeout
        while shown is None and self._clock() < deadline:
            self._sleep(timing.poll_interval)
            screen, image = self._observe()
            if screen.state is not State.MISSION_DIALOG:
                raise StepFailed(f"mission dialog disappeared, screen is {screen.state}")
            shown = self._detector.dialog_type(image)
        if shown is None or shown[0] is not target.type:
            found = "no known type" if shown is None else str(shown[0])
            raise MissionRejected(f"dialog shows {found}, expected {target.type}")
        self._tap_match(screen.matches["btn_view"])

        screen = self._await_popup(target)
        expected = ACTION_FOR[target.type]
        if screen.action is not expected:
            raise MissionRejected(f"popup offers {screen.action}, expected {expected}")
        self._tap_match(screen.matches["action"])

        if target.type is MissionType.COMBAT:
            world = self._fight()
        elif target.type is MissionType.RESCUE:
            world = self._rescue()
        else:
            world = self._deploy(require_prevail=target.type is not MissionType.BOSS)
        self.missions_started += 1
        self._unclaimed += 1

        self._tap_match(world.matches["intel_button"])
        self._expect(INTEL_STATES)

        if target.type is MissionType.BOSS:
            cycle = (
                float(refresh_seconds)
                if refresh_seconds is not None
                else self._config.boss.fallback_cycle_hours * 3600
            )
            until = self._store.lock_boss(self._now(), cycle)
            log.info("boss locked until %s", until.isoformat(timespec="seconds"))

    def _await_popup(self, target: Symbol) -> Screen:
        """``WORLD_TARGET`` after "View"; a tap the game swallowed is repeated once (BUG-0028).

        Without the popup the map still shows the intel pin above the target. Only a pin of
        the expected type is tapped, at the target below it.
        """
        try:
            return self._expect({State.WORLD_TARGET})[0]
        except StepFailed:
            if self._last is None or self._last[0].state is not State.WORLD:
                raise
            pin = self._detector.world_pin(self._last[1])
            if pin is None or pin[0] is not target.type:
                raise
            match = pin[1]
            offset = self._config.symbols.world_pin_tap_offset
            log.info("popup did not open, tapping the target again")
            self._tap((match.x, match.y + offset), f"{target.type} target below its pin")
            return self._expect({State.WORLD_TARGET})[0]

    def _end_if_blocked(self, screen: Screen) -> None:
        """End the run on a "not enough stamina" or "no troops / march slots" dialog."""
        if screen.state is State.NO_STAMINA:
            self._back("not enough stamina")
            raise RunEnded(Outcome.OUT_OF_STAMINA)
        if screen.state is State.NO_TROOPS:
            self._back("no troops or march slots")
            raise RunEnded(Outcome.NO_TROOPS)

    def _fight(self) -> Screen:
        screen, _ = self._expect({State.SQUAD, State.NO_STAMINA})
        self._end_if_blocked(screen)
        self._tap_match(screen.matches["btn_fight"])
        screen, _ = self._expect(RESULT_STATES, self._config.timing.fight_timeout)
        if screen.state is State.DEFEAT:
            log.warning("fight lost")
        self._tap_match(screen.matches["exit"])
        return self._expect({State.WORLD})[0]

    def _rescue(self) -> Screen:
        screen, _ = self._expect({State.WORLD, State.NO_STAMINA})
        self._end_if_blocked(screen)
        return screen

    def _deploy(self, require_prevail: bool) -> Screen:
        screen, image = self._expect({State.DEPLOY, State.NO_STAMINA, State.NO_TROOPS})
        self._end_if_blocked(screen)
        if not self._detector.likely_to_prevail(image):
            if require_prevail:
                raise MissionRejected('"You are quite likely to prevail" is not shown')
            # The boss is attacked once per cycle whatever the odds (SPEC §5).
            log.warning('deploying without "You are quite likely to prevail"')
        self._tap_match(screen.matches["btn_deploy"])
        screen, _ = self._expect({State.WORLD, State.NO_TROOPS})
        self._end_if_blocked(screen)
        return screen
