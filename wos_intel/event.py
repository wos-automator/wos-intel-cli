"""Flame and Fangs pre-event rules: which missions to claim, hold or ignore (TS-5.2, SPEC 3.7)."""

from __future__ import annotations

from enum import StrEnum


class Group(StrEnum):
    """What to do with a mission the day before the event, by its expiry."""

    CLAIM = "claim"  # expires before the event: finish it and claim the reward
    HOLD = "hold"  # expires with the event start: finish it, claim it during the event
    IGNORE = "ignore"  # expires after the event start: leave it for the event


class Phase(StrEnum):
    """Claim missions come first: unclaimed missions block the next refresh."""

    CLAIM = "claim"
    HOLD = "hold"


def classify(expires_in: float, until_start: float, tolerance: float) -> Group:
    """Group of a mission expiring in ``expires_in`` s, the event starting in ``until_start`` s."""
    if expires_in < until_start - tolerance:
        return Group.CLAIM
    if expires_in > until_start + tolerance:
        return Group.IGNORE
    return Group.HOLD
