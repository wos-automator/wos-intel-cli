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
- `intel-boss-running.png`: only the boss left, dimmed (`RUNNING`, attack under way); stamina 1,975,
  timer 02:46:03 (the bold digits "46" touch and have to be separated for the digit OCR).
- `intel-xxx.png`: tent and golden paw `DONE` (green check marks), "Claim All" visible.
- `intel-expert-available.png`: `INTEL` with the expert sign top left (≈ 59,210), eight `AVAILABLE` symbols
  (among them a golden tent and a golden axe), stamina 2,165, timer 00:54:43.
- `intel-xxxx.png`: `REWARDS` after "Claim All"; a tap top centre leads back to `INTEL`.
- `combat-1-dialog.png`: `MISSION_DIALOG` of a combat mission ("A Hero's Journey Lv. 10", blue axe pin), button View.
- `combat-2-world-explore.png`: `WORLD_TARGET` with popup and button "Explore 10"; Intel button on the right at ≈ 663,862.
- `combat-3-squad-fight.png`: `SQUAD` ("Squad Settings"), buttons Quick Deploy / Fight.
- `combat-4-victory.png`: `VICTORY` with "Tap anywhere to exit".
- `hunt-1-dialog.png`: `MISSION_DIALOG` of a hunt ("Beast Hunting Lv. 10", purple paw pin), button View.
- `hunt-1-dialog-banner.png`, `rescue-1-dialog-banner.png`: `MISSION_DIALOG` (hunt and "Rescue Survivors
  Lv. 10" respectively, View at ≈ 360,883), each with a notification banner over the pin – type not recognisable.
- `hunt-2-world-attack.png`: `WORLD_TARGET` with popup "Lv. 22 Giant Elk", button "Attack 10" (orange);
  Intel button here with a red badge (match 0.94 – threshold for `intel_button` therefore 0.85).
- `hunt-3-deploy.png`: `DEPLOY` with "You are quite likely to prevail" and button "Deploy 10".
- `boss-1-dialog.png`: `MISSION_DIALOG` of the boss ("Ultimate Bounty: No. 17"). The dialog is
  lower than for hunt/combat: button View at ≈ 360,870, skull shield at ≈ 356,430
  (smaller than in the hunt/combat dialog, mask ×0.60 instead of ×0.75).
- `boss-2-world-attack.png`: `WORLD_TARGET` of the boss with button "Attack 10".
- `boss-3-deploy.png`: `DEPLOY` of the boss with "You are not likely to prevail" (red).

### Templates
Symbol masks: `paw_mask`, `firebeast_mask`, `tent_mask`, `axe_mask`, `skull_mask` (+ colour cut-outs), `check` (green check mark).
Buttons/titles: `btn_view`, `btn_explore`, `btn_explore_top`, `btn_attack`, `btn_fight`, `btn_deploy`,
`btn_claim_all`, `intel_button`, `intel_button_badge`, `dialog_pin_axe`, `dialog_pin_paw`,
`title_intel`, `title_squad_settings`, `title_deploy`, `title_victory`, `text_tap_anywhere`, `text_likely_prevail`,
`expert_sign`.
Button matching in colour (BGR) with `TM_CCOEFF_NORMED`, threshold 0.9 (exception `intel_button`: 0.85).
For Explore/Attack match only the label half (`*_top`/`btn_attack`) – the cost figure below it can vary.
Do not use `title_deploy` alone for state detection (0.77 against "Squad Settings").

Cross-check (every template against all reference images, values ≥ 0.6): every button template hits only
its own screen with 1.00; `btn_view` both dialogs; `intel_button` 1.00 / 0.94 (with badge).
