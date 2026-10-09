# wos-intel – Specification

Automates the **Intel missions** in *Whiteout Survival* (BlueStacks Air on macOS):
detect the mission symbols on the Intel screen, start missions, collect rewards,
until no work is left or the stamina no longer suffices.

This file is the working basis for Claude Code. All coordinates refer to the
**Android image 720×1280** (`adb exec-out screencap -p`), not to the
macOS window.

---

## 1. Framework

| Item | Decision |
|---|---|
| Language | Python 3.11+ |
| Libraries | `opencv-python`, `numpy`; nothing that needs a server |
| Device access | ADB only: `adb exec-out screencap -p` (image), `adb shell input tap/swipe`, `adb shell input keyevent KEYCODE_BACK` |
| Device | `ANDROID_SERIAL` (default `127.0.0.1:5555`); on "more than one device" always set `-s` |
| Resolution | 720×1280 portrait (`adb shell wm size` → `Physical size: 720x1280`); check at start, otherwise abort |
| Package | `com.gof.global` |
| macOS input | **no** mouse/keyboard input through macOS (proved unreliable: the map shifts) |

Related tool: `wos-watchdog.sh` (crash restart + Endless Trial macro).
`wos-intel` is a program of its own; merging the two later is **not** part of this specification.

---

## 2. Screens and states

| State | Distinguishing feature | Reference image |
|---|---|---|
| `INTEL` | Title "Intel" top left, banner "Refreshes In: …" top centre | `ref/intel-x.png` |
| `INTEL_CLAIMABLE` | like `INTEL`, plus the green button **"Claim All"** bottom centre (≈ 360,1128) | `ref/intel-xxx.png` |
| `REWARDS` | Banner "Rewards", text "Tap anywhere to exit" at the bottom | `ref/intel-xxxx.png` |
| `MISSION_DIALOG` | Dialog in the centre, title = mission name (e.g. "A Hero's Journey Lv. 10"), at the top a **pin with the type symbol** (≈ 360,368), rewards, "Intel Expires In", blue button **"View"** (≈ 360,933, `templates/btn_view.png`) | `ref/combat-1-dialog.png` |
| `WORLD_TARGET` | World map, target in the centre (≈ 360,735), above it a **popup** with mission name, rewards and action button at ≈ 360,628: **Explore** (blue, combat, `btn_explore_top.png`), **Attack** (orange, hunt, with "Recommended Power", `btn_attack.png`), **Rescue** (green, missing). Below the label is the stamina cost ("10") | Combat: `ref/combat-2-world-explore.png`; hunt: `ref/hunt-2-world-attack.png`; **Rescue missing** |
| `DEPLOY` | Title "Deploy", hero cards, troop sliders, hint **"You are quite likely to prevail"** (green, ≈ 360,606, `text_likely_prevail.png`), march time, button **Deploy 10** bottom right (≈ 548,1215, `btn_deploy.png`). Detected through `btn_deploy` (the title alone is too similar to "Squad Settings") | `ref/hunt-3-deploy.png` |
| `SQUAD` | Title **"Squad Settings"** top left, "VS" battle view, hero grid, at the bottom **Quick Deploy** (blue, ≈ 192,1201) and **Fight** (green, ≈ 528,1201, `templates/btn_fight.png`) | `ref/combat-3-squad-fight.png` |
| `VICTORY` | Lettering **"Victory!"** (`templates/title_victory.png`), rewards, "Tap anywhere to exit" (≈ 360,1140) | `ref/combat-4-victory.png` |
| `DEFEAT` | presumably analogous to `VICTORY` with a different title | **missing** |
| `WORLD` | normal world map; on the right the round **Intel button** (blue tile, white circle with two strokes) at **≈ 663,862** (`templates/intel_button.png`) | visible in `ref/combat-2-world-explore.png` |
| `UNKNOWN` | none of these | – |

> **Still open:** hunt (`WORLD_TARGET` with Attack, troop selection with Deploy, result),
> rescue (`WORLD_TARGET` with Rescue, what appears afterwards), boss, `DEFEAT`, not-enough-stamina dialog.
> Until then Claude Code implements these steps with placeholder templates and `--dry-run`.

**Rescue without a reference image:** flow like hunt, but the popup button is labelled **"Rescue"**
(green, cost 12) and there is **no** deploy step – the mission starts immediately after the tap.
As no template exists yet, additionally classify the action button in the popup **by its colour**:
region ≈ x 245–475, y 598–660; median hue of the pixels with S>120 and V>120 (OpenCV scale 0–179):
measured Explore **105** (blue), Attack **12** (orange); Rescue expected **≈ 50–75** (green, like "Fight"/"Claim All").
On the first real rescue, take a reference image with `snap` and cut `btn_rescue.png` from it.

**Important:** `WORLD_TARGET` has **no** free-standing button in the middle of the screen, but a popup above
the target. Always search for the button by template (search area y 250–700), never tap a fixed coordinate.
The world map has further round buttons (e.g. red skull timer ≈ 663,545, paw button ≈ 663,955) –
the Intel button is the one with the two strokes.

State detection always uses a **fresh screenshot** – never chain taps blindly.
After every tap: wait briefly (initial value 1.0 s, configurable), screenshot, check the state.

---

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

---

## 4. Stamina

- Shown at the top right of the Intel screen (barrel symbol, e.g. "2,035"). Verified:
  2,057 → 2,047 after a hunt (−10) → 2,035 after a rescue (−12).
- Reading: digit OCR by template matching on single digits (no Tesseract dependency),
  region ≈ x 595–675, y 25–60. The comma is the thousands separator.
- Before every mission: `stamina >= cost(type)`, otherwise skip the mission.
  Stamina < 10 → the program ends regularly.
- Fallback if OCR fails: carry on, but detect a "not enough stamina" dialog
  (reference image still missing) and then end.

---

## 5. Flow (main loop)

```
start:
  check device (adb get-state, wm size, game in the foreground)
  state = detect()
  if WORLD: tap Intel button → INTEL
  if not INTEL*: abort with a message (no guessing)

loop:
  image = screenshot()
  if INTEL_CLAIMABLE: tap "Claim All" → REWARDS → tap top centre (≈ 360,180, above the
        rewards) → INTEL ; continue
  symbols = detect_symbols(image)            # AVAILABLE only, sorted by tier
  remove BOSS if already attacked in this refresh cycle
  BOSS to the end: the boss is attacked exactly once, and only when no workable symbol
        other than it is left
  if none (or none affordable):
        if missions are still running (RUNNING detected, or started in this run and not
        yet collected): wait on the Intel screen until "Claim All" appears
        (screenshot every 10 s, at most 15 min, both configurable), then "Claim All"
        as above and continue with loop
        otherwise: end ("nothing to do" or "not enough stamina")
  s = symbols[0]
  if stamina < cost(s): skip s
  tap s.click_point → expect MISSION_DIALOG
        check the type: match the pin in the dialog (≈ 335–385 / 345–395) against the type mask
        → tap "View"
  → expect WORLD_TARGET → search for the action button in the popup by template and tap it
        (COMBAT: Explore; HUNT/BOSS: Attack; RESCUE: Rescue)
  COMBAT:    → expect SQUAD → tap "Fight" (NOT "Quick Deploy"; heroes are preselected)
             → expect VICTORY | DEFEAT (the fight takes time; timeout here 60 s)
             → tap "Tap anywhere to exit" (≈ 360,1140) → expect WORLD
  HUNT/BOSS: → expect DEPLOY
             Safety rule: only if "You are quite likely to prevail" (green) is visible,
             otherwise BACK, lock the mission for this run, continue.
             Do NOT change troops/heroes (use the game's preset).
             → tap "Deploy" → expect WORLD (march starts; the mission turns RUNNING on INTEL)
             Note: the troops are on their way after the deploy. If the next deploy shows a
             hint about missing troops/march slots, BACK and end the run (reference image missing).
  RESCUE:    tapping "Rescue" starts the mission immediately; no further step → expect WORLD
  → back to Intel: on WORLD tap the Intel button (right) → expect INTEL
  BOSS: remember in the state (derive the refresh cycle from the timer "Refreshes In" or
        store timestamp + timer, file state.json)
```

**End of the run:** the program does not end as long as missions are running. If only
`RUNNING` missions are left, it waits for them to finish and collects the rewards with "Claim All";
the player does not have to collect anything by hand. If the waiting time runs out, the run ends
regularly with a note in the log.

Every step `expect X` waits at most N seconds (default 8) with a screenshot every 0.7 s.
On timeout: `BACK` up to 3×, then detect again; after 3 failures in a row the program ends.

---

## 6. Safety

- Never confirm shop, purchase, offer or diamond dialogs. Unknown dialog → `BACK`.
- Never swipe or zoom on the map.
- No tap outside detected targets, except the documented "top centre" on `REWARDS`.
- Upper limit of missions per run (default 30) against endless loops.

---

## 7. Operation

```
python -m wos_intel run            # normal operation
python -m wos_intel run --dry-run  # detects and logs, does not tap
python -m wos_intel detect image.png  # detection on a file, writes image.debug.png
python -m wos_intel snap name      # ADB screenshot to ref/name.png (collect references)
```

- Log with timestamp on stdout: detected state, symbols (type/tier/status/position), taps.
- `--debug` saves, per step, the image with the hits drawn in under `debug/`.
- Configuration (thresholds, waiting times, coordinates) in `config.toml`.

---

## 8. Project structure

```
wos_intel/
  __main__.py      CLI
  adb.py           screenshot (PNG → numpy), tap, back, device check
  detect.py        states, symbols, status, tier, stamina OCR
  flow.py          main loop / state machine
  state.py         state.json (boss lock per refresh cycle)
templates/         masks and button cut-outs (cut from ref/)
ref/               ADB reference screenshots
tests/             pytest: detection against ref/ with expected results (table in 3.5)
config.toml
```

**Acceptance criteria:**
1. `detect` returns on `ref/intel-x.png`, `-xx.png`, `-xxx.png` exactly the symbols and statuses from
   section 3.5 and from the description below (tests).
2. `--dry-run` on the real device logs correct symbols without tapping.
3. A real run works on all `AVAILABLE` missions (the boss last and exactly once), waits
   for running missions, collects all rewards and ends cleanly.

### Reference images (content)
- `intel-x.png`: golden paw bottom right is running (`RUNNING`), all others `AVAILABLE`, boss present.
- `intel-xx.png`: additionally the purple tent top left `RUNNING`.
- `intel-xxx.png`: tent and golden paw `DONE` (green check marks), "Claim All" visible.
- `intel-xxxx.png`: `REWARDS` after "Claim All"; a tap top centre leads back to `INTEL`.
- `combat-1-dialog.png`: `MISSION_DIALOG` of a combat mission ("A Hero's Journey Lv. 10", blue axe pin), button View.
- `combat-2-world-explore.png`: `WORLD_TARGET` with popup and button "Explore 10"; Intel button on the right at ≈ 663,862.
- `combat-3-squad-fight.png`: `SQUAD` ("Squad Settings"), buttons Quick Deploy / Fight.
- `combat-4-victory.png`: `VICTORY` with "Tap anywhere to exit".
- `hunt-1-dialog.png`: `MISSION_DIALOG` of a hunt ("Beast Hunting Lv. 10", purple paw pin), button View.
- `hunt-2-world-attack.png`: `WORLD_TARGET` with popup "Lv. 22 Giant Elk", button "Attack 10" (orange);
  Intel button here with a red badge (match 0.94 – threshold for `intel_button` therefore 0.85).
- `hunt-3-deploy.png`: `DEPLOY` with "You are quite likely to prevail" and button "Deploy 10".

### Templates
Symbol masks: `paw_mask`, `tent_mask`, `axe_mask`, `skull_mask` (+ colour cut-outs), `check` (green check mark).
Buttons/titles: `btn_view`, `btn_explore`, `btn_explore_top`, `btn_attack`, `btn_fight`, `btn_deploy`,
`btn_claim_all`, `intel_button`, `intel_button_badge`, `dialog_pin_axe`, `dialog_pin_paw`,
`title_intel`, `title_squad_settings`, `title_deploy`, `title_victory`, `text_tap_anywhere`, `text_likely_prevail`.
Button matching in colour (BGR) with `TM_CCOEFF_NORMED`, threshold 0.9 (exception `intel_button`: 0.85).
For Explore/Attack match only the label half (`*_top`/`btn_attack`) – the cost figure below it can vary.
Do not use `title_deploy` alone for state detection (0.77 against "Squad Settings").

Cross-check (every template against all reference images, values ≥ 0.6): every button template hits only
its own screen with 1.00; `btn_view` both dialogs; `intel_button` 1.00 / 0.94 (with badge).
