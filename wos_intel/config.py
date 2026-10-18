"""Configuration: defaults in code, overrides from ``config.toml`` (TS-1.3)."""

from __future__ import annotations

import dataclasses
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

Point = tuple[int, int]
Region = tuple[int, int, int, int]  # x0, y0, x1, y1 (exclusive end)
Hsv = tuple[int, int, int]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_NAME = "config.toml"
SERIAL_ENV = "ANDROID_SERIAL"


class ConfigError(ValueError):
    """Raised for unknown sections/keys or wrongly typed values in the config file."""


@dataclass(frozen=True)
class DeviceConfig:
    serial: str = "127.0.0.1:5555"
    adb_path: str = "adb"
    package: str = "com.gof.global"
    width: int = 720
    height: int = 1280
    command_timeout: float = 15.0


@dataclass(frozen=True)
class TimingConfig:
    tap_delay: float = 1.0
    poll_interval: float = 0.7
    expect_timeout: float = 8.0
    fight_timeout: float = 60.0
    completion_timeout: float = 900.0
    completion_poll: float = 10.0
    reconnect_delay: float = 60.0
    reconnect_timeout: float = 120.0
    queue_poll: float = 60.0
    queue_timeout: float = 900.0


@dataclass(frozen=True)
class LimitsConfig:
    max_missions: int = 30
    max_back: int = 3
    max_failures: int = 3
    min_stamina: int = 10


@dataclass(frozen=True)
class CostConfig:
    hunt: int = 10
    rescue: int = 12
    combat: int = 10
    boss: int = 10


@dataclass(frozen=True)
class SymbolConfig:
    search_y: Point = (170, 1050)
    white_lo: Hsv = (0, 0, 215)
    white_hi: Hsv = (180, 45, 255)
    dim_white_lo: Hsv = (0, 0, 190)
    dim_white_hi: Hsv = (180, 70, 255)
    match_threshold: float = 0.75
    nms_radius: int = 20
    disc_radius: int = 26
    disc_white_lo: Hsv = (0, 0, 200)
    disc_white_hi: Hsv = (180, 60, 255)
    available_min_saturation: int = 150
    running_max_saturation: int = 130
    check_lo: Hsv = (45, 120, 120)
    check_hi: Hsv = (75, 255, 255)
    check_min_area: int = 40
    check_max_area: int = 600
    check_offset: Point = (24, -24)
    check_tolerance: int = 14
    hue_gold: int = 16
    hue_blue: int = 109
    hue_purple: int = 143
    overlap_distance: int = 30
    edge_tap_radius: int = 20
    ring_offset_pin: int = 55
    ring_offset_boss: int = 65
    lock_radius: int = 12
    dialog_pin_region: Region = (300, 320, 420, 500)
    dialog_pin_scales: tuple[float, ...] = (0.60, 0.70, 0.75, 0.80)
    dialog_pin_threshold: float = 0.75
    world_pin_region: Region = (280, 580, 440, 740)
    world_pin_scales: tuple[float, ...] = (0.55, 0.60, 0.65, 0.70)
    world_pin_threshold: float = 0.75
    world_pin_tap_offset: int = 70


@dataclass(frozen=True)
class ButtonConfig:
    threshold: float = 0.9
    intel_button_threshold: float = 0.85
    action_region: Region = (0, 250, 720, 700)
    color_region: Region = (245, 598, 475, 660)
    color_min_saturation: int = 120
    color_min_value: int = 120
    color_min_fraction: float = 0.6
    hue_explore: Point = (95, 115)
    hue_attack: Point = (5, 20)
    hue_rescue: Point = (50, 75)
    rewards_exit: Point = (360, 180)


@dataclass(frozen=True)
class OcrConfig:
    white_lo: Hsv = (0, 0, 225)
    white_hi: Hsv = (180, 40, 255)
    stamina_region: Region = (595, 25, 675, 60)
    timer_region: Region = (215, 108, 510, 146)
    march_region: Region = (185, 195, 250, 232)
    # "Opens in HH:MM:SS" of the Flame and Fangs icon: pure white on a light map
    countdown_region: Region = (590, 1228, 695, 1254)
    countdown_lo: Hsv = (0, 0, 235)
    countdown_hi: Hsv = (180, 25, 255)
    # "Intel Expires In HH:MM:SS" of the mission dialog: dark grey on a light dialog
    expiry_region: Region = (380, 800, 500, 890)
    dark_lo: Hsv = (0, 0, 40)
    dark_hi: Hsv = (180, 120, 110)
    glyph_min_height_ratio: float = 0.75
    glyph_min_height: int = 10
    glyph_max_aspect: float = 1.3
    glyph_threshold: float = 0.6
    max_stamina_digits: int = 6


@dataclass(frozen=True)
class BossConfig:
    fallback_cycle_hours: float = 8.0


@dataclass(frozen=True)
class PathConfig:
    templates: str = "templates"
    ref: str = "ref"
    debug: str = "debug"
    state_file: str = "state.json"


def _default_regions() -> dict[str, Region]:
    return {
        "title_intel": (60, 10, 220, 75),
        "btn_claim_all": (150, 1050, 570, 1210),
        "title_rewards": (200, 260, 520, 380),
        "expert_sign": (0, 140, 160, 290),
        "btn_view": (150, 780, 570, 1010),
        "btn_deploy": (360, 1150, 720, 1280),
        "btn_fight": (330, 1140, 720, 1265),
        "title_victory": (150, 380, 570, 560),
        "text_tap_anywhere": (150, 1080, 570, 1220),
        "text_likely_prevail": (120, 570, 600, 640),
        "intel_button": (600, 700, 720, 1000),
        "intel_button_badge": (600, 700, 720, 1000),
        "text_simple_battle_mode": (0, 640, 720, 1160),
        "text_quit_game": (200, 540, 520, 680),
        "btn_cancel": (40, 720, 360, 860),
        "text_logged_in_elsewhere": (0, 520, 720, 700),
        "btn_reconnect": (360, 720, 720, 880),
        "event_icon": (560, 1100, 720, 1280),
    }


@dataclass(frozen=True)
class Config:
    device: DeviceConfig = field(default_factory=DeviceConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    costs: CostConfig = field(default_factory=CostConfig)
    symbols: SymbolConfig = field(default_factory=SymbolConfig)
    buttons: ButtonConfig = field(default_factory=ButtonConfig)
    ocr: OcrConfig = field(default_factory=OcrConfig)
    boss: BossConfig = field(default_factory=BossConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    regions: dict[str, Region] = field(default_factory=_default_regions)
    base_dir: Path = PROJECT_ROOT

    def path(self, relative: str) -> Path:
        """Resolve a configured path relative to the directory of the config file."""
        candidate = Path(relative)
        return candidate if candidate.is_absolute() else self.base_dir / candidate


def _coerce(section: str, key: str, default: Any, value: Any) -> Any:
    """Convert a TOML value to the type of the default it overrides."""
    where = f"[{section}] {key}"
    if isinstance(default, bool) or isinstance(value, bool):
        raise ConfigError(f"{where}: boolean values are not supported")
    if isinstance(default, tuple):
        if not isinstance(value, list) or not all(isinstance(v, (int, float)) for v in value):
            raise ConfigError(f"{where}: expected a list of numbers")
        if all(isinstance(d, int) for d in default):
            if not all(isinstance(v, int) for v in value) or len(value) != len(default):
                raise ConfigError(f"{where}: expected {len(default)} integers")
            return tuple(value)
        return tuple(float(v) for v in value)
    if isinstance(default, float):
        if not isinstance(value, (int, float)):
            raise ConfigError(f"{where}: expected a number")
        return float(value)
    if isinstance(default, int):
        if not isinstance(value, int):
            raise ConfigError(f"{where}: expected an integer")
        return value
    if not isinstance(value, str):
        raise ConfigError(f"{where}: expected a string")
    return value


def _override_section(section: str, default: Any, values: dict[str, Any]) -> Any:
    known = {f.name for f in dataclasses.fields(default)}
    unknown = sorted(set(values) - known)
    if unknown:
        raise ConfigError(f"[{section}]: unknown key(s) {', '.join(unknown)}")
    coerced = {k: _coerce(section, k, getattr(default, k), v) for k, v in values.items()}
    return dataclasses.replace(default, **coerced)


def _override_regions(default: dict[str, Region], values: dict[str, Any]) -> dict[str, Region]:
    regions = dict(default)
    for name, value in values.items():
        ok = isinstance(value, list) and len(value) == 4 and all(isinstance(v, int) for v in value)
        if not ok:
            raise ConfigError(f"[regions] {name}: expected [x0, y0, x1, y1]")
        regions[name] = (value[0], value[1], value[2], value[3])
    return regions


def find_config_file() -> Path | None:
    """Return ``config.toml`` from the working directory or the project root, if present."""
    for directory in (Path.cwd(), PROJECT_ROOT):
        candidate = directory / DEFAULT_CONFIG_NAME
        if candidate.is_file():
            return candidate
    return None


def load_config(path: Path | None = None, env: dict[str, str] | None = None) -> Config:
    """Load the configuration; ``ANDROID_SERIAL`` overrides the configured serial."""
    environment = os.environ if env is None else env
    config_file = path if path is not None else find_config_file()
    config = Config()
    if config_file is not None:
        try:
            with config_file.open("rb") as handle:
                data = tomllib.load(handle)
        except tomllib.TOMLDecodeError as exc:
            raise ConfigError(f"{config_file}: {exc}") from exc
        sections: dict[str, Any] = {}
        for name, values in data.items():
            if name == "base_dir" or name not in {f.name for f in dataclasses.fields(Config)}:
                raise ConfigError(f"unknown section [{name}]")
            if not isinstance(values, dict):
                raise ConfigError(f"[{name}] must be a table")
            if name == "regions":
                sections[name] = _override_regions(config.regions, values)
            else:
                sections[name] = _override_section(name, getattr(config, name), values)
        config = dataclasses.replace(config, base_dir=config_file.resolve().parent, **sections)
    serial = environment.get(SERIAL_ENV, "").strip()
    if serial:
        config = dataclasses.replace(
            config, device=dataclasses.replace(config.device, serial=serial)
        )
    return config
