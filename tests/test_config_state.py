"""Configuration loading and the persistent boss lock (US-1.3, US-3.4)."""

from __future__ import annotations

import dataclasses
import json
import tomllib
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from wos_intel.config import PROJECT_ROOT, Config, ConfigError, load_config
from wos_intel.state import StateStore

NOW = datetime(2026, 10, 9, 19, 0, 0)


@pytest.mark.unit
def test_defaults_follow_the_spec() -> None:
    config = Config()

    assert config.device.serial == "127.0.0.1:5555"
    assert config.device.package == "com.gof.global"
    assert (config.device.width, config.device.height) == (720, 1280)
    assert config.timing.tap_delay == 1.0
    assert config.timing.poll_interval == 0.7
    assert config.timing.expect_timeout == 8.0
    assert config.timing.fight_timeout == 60.0
    assert config.timing.queue_poll == 60.0
    assert config.timing.queue_timeout == 900.0
    assert config.event.tolerance_minutes == 10.0
    assert config.event.expert_hours == 2.0
    assert config.limits.max_missions == 30
    assert config.symbols.match_threshold == 0.75
    assert config.buttons.threshold == 0.9
    assert config.buttons.intel_button_threshold == 0.85
    assert config.buttons.rewards_exit == (360, 180)


@pytest.mark.integration
def test_shipped_config_file_equals_the_built_in_defaults() -> None:
    shipped = load_config(PROJECT_ROOT / "config.toml", env={})

    assert shipped == Config()


@pytest.mark.integration
def test_shipped_config_file_documents_every_setting() -> None:
    with (PROJECT_ROOT / "config.toml").open("rb") as handle:
        data = tomllib.load(handle)

    for section in dataclasses.fields(Config):
        if section.name in ("base_dir", "regions"):
            continue
        expected = {f.name for f in dataclasses.fields(getattr(Config(), section.name))}
        assert set(data[section.name]) == expected, section.name
    assert set(data["regions"]) == set(Config().regions)


@pytest.mark.integration
def test_file_overrides_and_base_dir(tmp_path: Path) -> None:
    file = tmp_path / "config.toml"
    file.write_text(
        "[timing]\ntap_delay = 2\n[buttons]\nrewards_exit = [300, 200]\n"
        "[symbols]\ndialog_pin_scales = [0.7, 1]\n[regions]\nbtn_view = [1, 2, 3, 4]\n",
        encoding="utf-8",
    )

    config = load_config(file, env={})

    assert config.timing.tap_delay == 2.0
    assert config.timing.poll_interval == 0.7
    assert config.buttons.rewards_exit == (300, 200)
    assert config.symbols.dialog_pin_scales == (0.7, 1.0)
    assert config.regions["btn_view"] == (1, 2, 3, 4)
    assert config.regions["btn_fight"] == Config().regions["btn_fight"]
    assert config.path("templates") == tmp_path / "templates"
    assert config.path("/abs/state.json") == Path("/abs/state.json")


@pytest.mark.integration
def test_android_serial_overrides_the_file(tmp_path: Path) -> None:
    file = tmp_path / "config.toml"
    file.write_text('[device]\nserial = "from-file"\n', encoding="utf-8")

    assert load_config(file, env={}).device.serial == "from-file"
    assert load_config(file, env={"ANDROID_SERIAL": "emulator-5554"}).device.serial == (
        "emulator-5554"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("[nonsense]\na = 1\n", "unknown section"),
        ("[timing]\ntap_dealy = 1\n", "unknown key"),
        ('[timing]\ntap_delay = "fast"\n', "expected a number"),
        ("[limits]\nmax_missions = 1.5\n", "expected an integer"),
        ("[limits]\nmax_missions = true\n", "boolean"),
        ("[buttons]\nrewards_exit = [1]\n", "expected 2 integers"),
        ("[device]\nserial = 5\n", "expected a string"),
        ("[regions]\nbtn_view = [1, 2]\n", "x0, y0, x1, y1"),
        ("timing = 3\n", "must be a table"),
        ("[timing\n", "config.toml"),
    ],
)
def test_invalid_files_are_rejected(tmp_path: Path, content: str, message: str) -> None:
    file = tmp_path / "config.toml"
    file.write_text(content, encoding="utf-8")

    with pytest.raises(ConfigError, match=message):
        load_config(file, env={})


@pytest.mark.integration
def test_boss_lock_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "state.json"
    store = StateStore(path)
    assert not store.boss_locked(NOW)

    until = store.lock_boss(NOW, 3600)

    assert until == NOW + timedelta(hours=1)
    again = StateStore(path)
    assert again.boss_locked(NOW + timedelta(minutes=59))
    assert not again.boss_locked(NOW + timedelta(hours=1))
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["boss"]["attacked_at"] == NOW.isoformat()
    assert not path.with_suffix(".json.tmp").exists()


@pytest.mark.integration
@pytest.mark.parametrize("content", ["{broken", "[]", '{"boss": 3}', '{"boss": {}}'])
def test_unusable_state_file_means_not_locked(tmp_path: Path, content: str) -> None:
    path = tmp_path / "state.json"
    path.write_text(content, encoding="utf-8")

    assert not StateStore(path).boss_locked(NOW)


@pytest.mark.integration
def test_lock_keeps_unrelated_state(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"other": 1}', encoding="utf-8")

    StateStore(path).lock_boss(NOW, 60)

    assert json.loads(path.read_text(encoding="utf-8"))["other"] == 1


@pytest.mark.integration
def test_event_hold_round_trip_keeps_the_boss_lock(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    store = StateStore(path)
    store.lock_boss(NOW, 3600)
    assert not store.holding(NOW)

    store.hold(NOW + timedelta(hours=8))

    again = StateStore(path)
    assert again.holding(NOW + timedelta(hours=7, minutes=59))
    assert not again.holding(NOW + timedelta(hours=8))  # the event has started
    assert again.boss_locked(NOW)


@pytest.mark.integration
@pytest.mark.parametrize(
    "content", ["{broken", '{"event": 3}', '{"event": {}}', '{"event": {"hold_until": "x"}}']
)
def test_unusable_event_hold_means_not_holding(tmp_path: Path, content: str) -> None:
    path = tmp_path / "state.json"
    path.write_text(content, encoding="utf-8")

    assert not StateStore(path).holding(NOW)
