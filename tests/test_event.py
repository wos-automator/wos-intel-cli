"""Pre-event rules of the Flame and Fangs event (US-6.3)."""

from __future__ import annotations

import pytest

from wos_intel.event import Group, classify

pytestmark = pytest.mark.unit

HOUR = 3600.0
TOLERANCE = 600.0


@pytest.mark.parametrize(
    ("expires_in", "group"),
    [
        (0.0, Group.CLAIM),
        (8 * HOUR - TOLERANCE - 1, Group.CLAIM),
        (8 * HOUR - TOLERANCE, Group.HOLD),
        (8 * HOUR, Group.HOLD),
        (8 * HOUR + TOLERANCE, Group.HOLD),
        (8 * HOUR + TOLERANCE + 1, Group.IGNORE),
        (16 * HOUR, Group.IGNORE),
    ],
)
def test_classify_at_the_borders_of_the_tolerance(expires_in: float, group: Group) -> None:
    assert classify(expires_in, 8 * HOUR, TOLERANCE) is group


def test_the_13_00_example_of_the_spec() -> None:
    """At 13:00 the day before: 00:00 missions expire at 16:00, 08:00 missions at midnight."""
    until_start = 11 * HOUR
    assert classify(3 * HOUR, until_start, TOLERANCE) is Group.CLAIM
    assert classify(11 * HOUR - 42, until_start, TOLERANCE) is Group.HOLD
