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
  if no regular mission other than the BOSS is workable any more and the expert sign
        (top left, 3.6) is visible: tap the sign (once per run) ; continue with loop
  BOSS to the end: the boss is attacked exactly once, and only when no workable symbol
        other than it is left
  if none (or none affordable):
        if missions are still running (RUNNING detected, or started in this run and not
        yet collected): wait on the Intel screen until "Claim All" appears
        (screenshot every 10 s, at most 5 min, both configurable), then "Claim All"
        as above and continue with loop;
        stop waiting early when a workable mission appears (continue with loop), or
        when no symbol is RUNNING any more and only the boss was started since the
        last claim (a lost boss pays nothing, so "Claim All" never comes)
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
             Exception BOSS: the boss is attacked even with "You are not likely to prevail" (red,
             `ref/boss-3-deploy.png`) – once per refresh cycle, regardless of the
             odds. The following safety rule applies to HUNT only.
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
regularly with a note in the log. A started hunt, combat or rescue is always waited for in full:
its pin can be hidden behind another symbol, so "no running symbol" does not mean it is done.

**Busy march queues (BUG-0014):** a hunt or boss target needs a free march queue; combat and
rescue do not. If all march queues are busy (the world map shows "Marching 6/6"), no more hunt
or boss targets can be started. The run then works only on the targets that are neither hunt
nor boss, and leaves hunt and boss for later instead of ending. This is a new feature.

Every step `expect X` waits at most N seconds (default 8) with a screenshot every 0.7 s.
On timeout: `BACK` up to 3×, then detect again; after 3 failures in a row the program ends.
