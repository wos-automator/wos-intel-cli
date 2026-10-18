"""Cuts the templates that are derived from ref/ screenshots: digit glyphs and the CUTS below.

Usage: python tools/cut_templates.py

Each digit source names a reference image, a region and the digits visible in it. The
glyphs are normalised exactly like the OCR does at runtime (wos_intel.detect).
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wos_intel.config import Config, Region
from wos_intel.detect import DIGITS_DIR, normalize_glyph, segment_glyphs

# tag, reference image, region (x0, y0, x1, y1), expected glyphs ("/" = glyph to skip),
# text colour ("white" or "dark")
DIGIT_SOURCES: tuple[tuple[str, str, Region, str, str], ...] = (
    ("stamina-a", "intel-x", (595, 25, 675, 60), "2047", "white"),
    ("stamina-b", "intel-xxx", (595, 25, 675, 60), "2035", "white"),
    ("timer-a", "intel-x", (375, 108, 510, 146), "065927", "white"),
    ("timer-b", "intel-xx", (375, 108, 510, 146), "065910", "white"),
    ("timer-c", "intel-xxx", (375, 108, 510, 146), "065905", "white"),
    ("timer-d", "intel-boss-running", (375, 108, 510, 146), "024603", "white"),
    ("stamina-c", "intel-boss-running", (595, 25, 675, 60), "1975", "white"),
    ("timer-e", "intel-expert-available", (375, 108, 510, 146), "005443", "white"),
    ("stamina-d", "intel-expert-available", (595, 25, 675, 60), "2165", "white"),
    ("troops", "hunt-3-deploy", (82, 178, 265, 212), "169830/169830", "white"),
    ("power", "hunt-3-deploy", (530, 178, 675, 212), "1155314530", "white"),
    # dark "Intel Expires In HH:MM:SS" of the mission dialogs (SPEC 3.7); no 6 in them yet
    ("expiry-a", "combat-1-dialog", (380, 800, 500, 890), "135107", "dark"),
    ("expiry-b", "hunt-1-dialog", (380, 800, 500, 890), "134842", "dark"),
    ("expiry-c", "hunt-1-dialog-banner", (380, 800, 500, 890), "145941", "dark"),
    ("expiry-d", "rescue-1-dialog-banner", (380, 800, 500, 890), "145919", "dark"),
)

# name, reference image, region
CUTS: tuple[tuple[str, str, Region], ...] = (
    ("title_rewards", "intel-xxxx", (268, 300, 454, 342)),
    # inside of the white sign, without the map behind its rounded corners
    ("expert_sign", "intel-expert-available", (26, 178, 92, 242)),
    # first line of the hint bubble, BUG-0002
    ("text_simple_battle_mode", "world-simple-battle-mode", (98, 840, 585, 872)),
    # "Quit game?" confirmation after BACK, BUG-0006
    ("text_quit_game", "dialog-quit-game", (280, 588, 440, 628)),
    ("btn_cancel", "dialog-quit-game", (150, 765, 270, 810)),
    # "The account has been logged in on another device.", BUG-0095a
    ("text_logged_in_elsewhere", "dialog-logged-in-elsewhere", (60, 588, 660, 620)),
    ("btn_reconnect", "dialog-logged-in-elsewhere", (435, 782, 605, 822)),
    # creature head of the Flame and Fangs icon, without its countdown (SPEC 3.7)
    ("event_icon", "flame-and-fangs-announced", (612, 1158, 680, 1200)),
)


def main() -> int:
    config = Config()
    ref = config.path(config.paths.ref)
    templates = config.path(config.paths.templates)
    digits = templates / DIGITS_DIR
    digits.mkdir(parents=True, exist_ok=True)
    for stale in digits.glob("[0-9]_*.png"):
        stale.unlink()

    written: set[str] = set()
    masks = {
        "white": (config.ocr.white_lo, config.ocr.white_hi),
        "dark": (config.ocr.dark_lo, config.ocr.dark_hi),
    }
    for tag, name, (x0, y0, x1, y1), expected, colour in DIGIT_SOURCES:
        image = np.asarray(cv2.imread(str(ref / f"{name}.png")), dtype=np.uint8)
        lo, hi = masks[colour]
        glyphs = segment_glyphs(
            image[y0:y1, x0:x1],
            lo,
            hi,
            config.ocr.glyph_min_height_ratio,
            config.ocr.glyph_min_height,
            config.ocr.glyph_max_aspect,
        )
        if len(glyphs) != len(expected):
            sys.stderr.write(f"{tag}: expected {len(expected)} glyphs, found {len(glyphs)}\n")
            return 1
        for index, (char, glyph) in enumerate(zip(expected, glyphs, strict=True)):
            if not char.isdigit():
                continue
            cv2.imwrite(str(digits / f"{char}_{tag}-{index}.png"), normalize_glyph(glyph))
            written.add(char)

    missing = sorted(set("0123456789") - written)
    if missing:
        sys.stderr.write(f"no glyph for digit(s): {', '.join(missing)}\n")
        return 1

    for name, source, (x0, y0, x1, y1) in CUTS:
        image = np.asarray(cv2.imread(str(ref / f"{source}.png")), dtype=np.uint8)
        cv2.imwrite(str(templates / f"{name}.png"), image[y0:y1, x0:x1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
