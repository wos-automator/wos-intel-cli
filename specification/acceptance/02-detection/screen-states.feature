@FR-2.1
Feature: Screen states
  Every screenshot is classified as exactly one screen state. The reference screenshots in
  "ref/" were taken on the device; each one is classified as the screen it shows.

  @AT-2.1
  Scenario Outline: A reference screenshot is classified as the screen it shows
    When the detection runs on the reference screenshot "<screenshot>"
    Then the exit code is 0
    And the screen state is "<state>"

    Examples:
      | screenshot                     | state             |
      | intel-x.png                    | INTEL             |
      | intel-xx.png                   | INTEL             |
      | intel-boss-running.png         | INTEL             |
      | intel-expert-available.png     | INTEL             |
      | flame-and-fangs-announced.png  | INTEL             |
      | flame-and-fangs-missions.png   | INTEL             |
      | intel-xxx.png                  | INTEL_CLAIMABLE   |
      | intel-xxxx.png                 | REWARDS           |
      | combat-1-dialog.png            | MISSION_DIALOG    |
      | hunt-1-dialog.png              | MISSION_DIALOG    |
      | boss-1-dialog.png              | MISSION_DIALOG    |
      | hunt-1-dialog-banner.png       | MISSION_DIALOG    |
      | rescue-1-dialog-banner.png     | MISSION_DIALOG    |
      | combat-2-world-explore.png     | WORLD_TARGET      |
      | hunt-2-world-attack.png        | WORLD_TARGET      |
      | boss-2-world-attack.png        | WORLD_TARGET      |
      | hunt-3-deploy.png              | DEPLOY            |
      | boss-3-deploy.png              | DEPLOY            |
      | combat-3-squad-fight.png       | SQUAD             |
      | combat-4-victory.png           | VICTORY           |
      | hunt-2-world-queues-busy.png   | WORLD             |
      | hunt-2-world-no-popup.png      | WORLD             |
      | boss-2-world-no-popup.png      | WORLD             |
      | world-target-vanished.png      | WORLD             |
      | world-simple-battle-mode.png   | HINT              |
      | dialog-quit-game.png           | QUIT_CONFIRMATION |
      | dialog-logged-in-elsewhere.png | SESSION_LOST      |
