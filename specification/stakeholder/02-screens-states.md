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
> rescue (`WORLD_TARGET` with Rescue, what appears afterwards), `DEFEAT`, not-enough-stamina dialog.
> Boss: reference images `ref/boss-1-dialog.png`, `boss-2-world-attack.png`, `boss-3-deploy.png` exist.
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
