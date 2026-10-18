"""Persistent run state in ``state.json``: boss lock (TS-3.4) and event hold (TS-5.2)."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


class StateStore:
    """Remembers until when the boss must not be attacked and rewards must not be claimed."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def _load(self) -> dict[str, Any]:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as exc:
            log.warning("ignoring unreadable state file %s: %s", self._path, exc)
            return {}
        return data if isinstance(data, dict) else {}

    def boss_locked_until(self) -> datetime | None:
        boss = self._load().get("boss")
        if not isinstance(boss, dict):
            return None
        try:
            return datetime.fromisoformat(str(boss.get("locked_until")))
        except ValueError:
            log.warning("ignoring invalid boss lock in %s", self._path)
            return None

    def boss_locked(self, now: datetime) -> bool:
        until = self.boss_locked_until()
        return until is not None and now < until

    def lock_boss(self, now: datetime, cycle_seconds: float) -> datetime:
        """Lock the boss until the current refresh cycle ends; returns the end time."""
        until = now + timedelta(seconds=cycle_seconds)
        data = self._load()
        data["boss"] = {"attacked_at": now.isoformat(), "locked_until": until.isoformat()}
        self._save(data)
        return until

    def holding(self, now: datetime) -> bool:
        """True while rewards are held for the Flame and Fangs event that starts later."""
        event = self._load().get("event")
        if not isinstance(event, dict):
            return False
        try:
            until = datetime.fromisoformat(str(event.get("hold_until")))
        except ValueError:
            log.warning("ignoring invalid event hold in %s", self._path)
            return False
        return now < until

    def hold(self, until: datetime) -> None:
        """Claim nothing until the event starts at ``until``, also in later runs."""
        data = self._load()
        data["event"] = {"hold_until": until.isoformat(timespec="seconds")}
        self._save(data)

    def _save(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(self._path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, self._path)
