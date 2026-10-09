"""Command line interface: ``python -m wos_intel run|detect|snap`` (TS-1.2)."""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import cv2
import numpy as np

from wos_intel.adb import Adb, AdbError
from wos_intel.config import Config, ConfigError, load_config
from wos_intel.detect import DetectError, Detector
from wos_intel.flow import INTEL_STATES, Runner
from wos_intel.state import StateStore

log = logging.getLogger("wos_intel")

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m wos_intel",
        description="Automates the Intel missions in Whiteout Survival via ADB.",
    )
    parser.add_argument("--config", type=Path, help="path to config.toml")
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="claim rewards and start all available missions")
    run.add_argument("--dry-run", action="store_true", help="detect and log, never tap")
    run.add_argument("--debug", action="store_true", help="save annotated screenshots per step")

    detect = commands.add_parser("detect", help="run the detection on an image file")
    detect.add_argument("image", type=Path)

    snap = commands.add_parser("snap", help="save an ADB screenshot as ref/<name>.png")
    snap.add_argument("name")
    snap.add_argument("--force", action="store_true", help="overwrite an existing file")
    return parser


def _run(config: Config, dry_run: bool, debug: bool) -> int:
    runner = Runner(
        config,
        Adb(config.device),
        Detector(config),
        StateStore(config.path(config.paths.state_file)),
        dry_run=dry_run,
        debug_dir=config.path(config.paths.debug) if debug else None,
        failure_dir=config.path(config.paths.debug),
    )
    outcome = runner.run()
    log.info("finished: %s (%d mission(s) started)", outcome.value, runner.missions_started)
    return EXIT_OK if outcome.ok else EXIT_FAILED


def _detect(config: Config, path: Path) -> int:
    loaded = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if loaded is None:
        log.error("cannot read image %s", path)
        return EXIT_USAGE
    image = np.asarray(loaded, dtype=np.uint8)
    if image.shape[:2] != (config.device.height, config.device.width):
        log.error("image must be %dx%d", config.device.width, config.device.height)
        return EXIT_USAGE

    detector = Detector(config)
    screen = detector.detect_state(image)
    log.info("state %s", screen.state)
    for match in screen.matches.values():
        log.info("match %s %.2f at %d,%d", match.name, match.score, match.x, match.y)
    symbols = detector.detect_symbols(image) if screen.state in INTEL_STATES else []
    if screen.state in INTEL_STATES:
        stamina = detector.read_stamina(image)
        refresh = detector.read_refresh_seconds(image)
        log.info("stamina %s", "unreadable" if stamina is None else stamina)
        log.info("refresh in %s", "unreadable" if refresh is None else f"{refresh} s")
    for symbol in symbols:
        log.info("symbol %s", symbol.describe())

    target = path.with_suffix(".debug.png")
    cv2.imwrite(str(target), detector.annotate(image, screen, symbols))
    log.info("wrote %s", target)
    return EXIT_OK


def _snap(config: Config, name: str, force: bool) -> int:
    if not name or Path(name).name != name:
        log.error("name must be a plain file name without directories")
        return EXIT_USAGE
    target = config.path(config.paths.ref) / f"{name.removesuffix('.png')}.png"
    if target.exists() and not force:
        log.error("%s already exists (use --force to overwrite)", target)
        return EXIT_USAGE
    image = Adb(config.device).screenshot()
    target.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(target), image)
    log.info("wrote %s", target)
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s",
        stream=sys.stdout,
        force=True,
    )
    try:
        config = load_config(args.config)
        if args.command == "run":
            return _run(config, args.dry_run, args.debug)
        if args.command == "detect":
            return _detect(config, args.image)
        return _snap(config, args.name, args.force)
    except (AdbError, ConfigError, DetectError) as exc:
        log.error("%s", exc)
        return EXIT_FAILED


if __name__ == "__main__":
    raise SystemExit(main())
