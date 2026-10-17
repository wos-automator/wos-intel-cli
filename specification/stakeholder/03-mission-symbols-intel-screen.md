## 3. Mission symbols on the Intel screen

### 3.1 Structure of a symbol
- A **pin** (drop shape) with a coloured rim; at the top a **dark disc** (radius ≈ 27 px),
  inside it a **white symbol**. On the ground below, a glowing ring – **not clickable**.
- **Click point = centre of the disc.**
- Exception **boss**: no pin, but an orange flame shield with a white skull
  (centre ≈ middle of the skull).

### 3.2 Types

| Type | Symbol | Template | Flow | Stamina |
|---|---|---|---|---|
| `HUNT` | paw | `templates/paw_mask.png` | Tap → **View** → **Attack** → **Deploy** (deploy screen) → world map, march is under way | 10 |
| `RESCUE` | tent | `templates/tent_mask.png` | Tap → **View** → **Rescue** (green popup button) → mission starts immediately, no deploy | 12 |
| `COMBAT` | crossed halberds | `templates/axe_mask.png` | Tap → **View** → **Explore** → **Fight** (Squad Settings) → **Victory** → tap → world map | 10 |
| `BOSS` | skull in flames | `templates/skull_mask.png` | like `HUNT`, but attack **only once per refresh cycle** and **only when no other workable symbol is left** | 10 |

### 3.3 Tier (pin colour)
`GOLD > PURPLE > BLUE`. Determined through the hue of the pin rim or of the disc.
Measured disc values (HSV, OpenCV scale): blue V≈146 S≈218; purple V≈81 S≈252; gold: light orange.
Processing order: highest tier first, within the same tier from top to bottom.
Exception `BOSS`: regardless of the tier always **last** (see 5).

### 3.4 Status

| Status | Feature | Measured value | Action |
|---|---|---|---|
| `AVAILABLE` | disc strongly coloured, no check mark | median saturation of the non-white pixels in the disc **≥ 150** | work on it |
| `RUNNING` | whole pin half transparent/greyed out, visually in the back | median saturation **< 130** (measured 38–101) | skip |
| `DONE` | green check mark in a white circle at the top right of the disc (offset ≈ +24/−24 px) | green component (HSV 45–75 / S≥120 / V≥120), area 40–600 px, near the disc | skip; "Claim All" becomes visible |

### 3.5 Detection method (verified by prototype)
1. Search area: y 170–1050 (mask out title/timer at the top, level bar and Claim All at the bottom).
2. **White mask** of the image: HSV `(0,0,215)–(180,45,255)`.
3. `cv2.matchTemplate(mask, template_mask, TM_CCOEFF_NORMED)`; threshold **0.75**;
   non-maximum suppression within a radius of 20 px. (Prototype: real hits 0.82–1.00.)
   **Second pass for dimmed symbols:** a running symbol is half transparent and too dark for
   the white mask (running boss in `ref/intel-boss-running.png`: score 0.51).
   Therefore additionally search with the wider mask HSV `(0,0,190)–(180,70,255)` (running
   boss: 0.82 at 518,700, disc saturation 99; other types there ≤ 0.46). The second
   pass also finds strongly coloured symbols that the first one narrowly misses (partly covered;
   measured on the device: score 0.76 at saturation 224). The status therefore follows 3.4
   alone here as well (saturation/check mark), not which pass found the symbol.
4. Per hit: status according to 3.4, tier according to 3.3.
5. **Overlap:** symbols can cover one another. Template matching on the white mask
   usually still finds covered symbols (partial occlusion). Before the tap, check whether another
   detected symbol lies closer than 30 px to the click point **and further in front** (= larger y
   of the ground ring). Then work on the front one first or – if the front one is `RUNNING`/`DONE`
   – move to an uncovered part of the disc (point on the disc rim
   opposite the covering symbol).
6. **Plausibility check after the tap:** the opened `MISSION_DIALOG` must match the expected
   type (template of the type symbol in the dialog or button text). If not: `BACK`, lock the
   symbol for this run, continue.
   **Notification banner:** messages such as "Troops have returned to the city." or "We have
   wiped out Giant Elk!" slide across the dialog for a few seconds and cover the
   pin (`ref/hunt-1-dialog-banner.png`, `ref/rescue-1-dialog-banner.png`). If the type is **not
   recognisable**, therefore do not abort at once, but check the dialog again until the timeout
   (8 s, every 0.7 s). The symbol is locked only if the pin clearly shows a **different** type
   or stays unreadable until the timeout. Otherwise workable missions would be skipped and the
   boss attacked too early.

Prototype: `tools/prototype_detect.py` (threshold 0.75). Results = **expected values for the tests**
(type, x, y, score, disc saturation, status):
```
intel-x    paw 336,289 AVAILABLE | paw 483,315 AVAILABLE | tent 287,351 AVAILABLE
           axe 340,378 AVAILABLE | paw 275,677 AVAILABLE | axe 568,680 AVAILABLE | skull 518,700 AVAILABLE
           (golden paw 566,737 is running – the white mask does not find it; still safeguard detection through saturation)
intel-xx   like intel-x, but tent 287,351 0.88 sat 38 RUNNING
intel-xxx  like intel-x, but tent 287,351 DONE and paw 564,737 0.83 sat 184 DONE
           green check marks at 311,328 and 587,714
```
Tolerance for positions in tests: ±6 px.

### 3.6 Expert (additional missions, once a day)

Once a day a small **white sign pointing to the left with the bust of a person** appears at the
top left of the Intel screen – the expert (`ref/intel-expert-available.png`,
centre ≈ 59,210, template `templates/expert_sign.png`). A tap on it delivers further missions.

- Detection: colour template like the buttons (threshold 0.9), search area x 0–160, y 140–290.
  Cross-check: ≤ 0.57 on all other reference images.
- **Rule:** when no regular mission other than the boss is workable any more and the sign is
  visible, tap the sign – **before** the boss and even when the stamina no longer suffices.
  The offer exists only once a day; it must not expire.
- As long as regular missions are workable, the sign stays untouched.
- A visible sign is always logged (position, score), even when it is not tapped –
  in particular with `--dry-run`.
- At most one tap per run. Afterwards evaluate the Intel screen again (new symbols).
- **Still open:** what appears after the tap (dialog, animation) is not covered by a reference
  image. If something other than the Intel screen appears, the normal recovery applies
  (`BACK`), and the screenshot is stored under `debug/`.
