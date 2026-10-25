@FR-2.5
Feature: Stamina and refresh timer
  The Intel screen shows the stamina top right and the time until the missions refresh.

  @AT-2.6
  Scenario Outline: Stamina and refresh timer of a reference Intel screen
    When the detection runs on the reference screenshot "<screenshot>"
    Then the stamina reads <stamina>
    And the refresh timer reads <timer>

    Examples:
      | screenshot                 | stamina | timer    |
      | intel-x.png                | 2047    | 06:59:27 |
      | intel-xx.png               | 2035    | 06:59:10 |
      | intel-xxx.png              | 2035    | 06:59:05 |
      | intel-boss-running.png     | 1975    | 02:46:03 |
      | intel-expert-available.png | 2165    | 00:54:43 |
