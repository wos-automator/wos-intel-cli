Feature: Mission symbols
  On the Intel screen every mission symbol is reported with type, click point, status and tier.
  The expected symbols of the reference screenshots are those of SPEC.md §3.5; positions are
  accurate to 6 px.

  @AT-2.2 @FR-2.2
  Scenario Outline: A reference Intel screen shows exactly its mission symbols
    When the detection runs on the reference screenshot "<screenshot>"
    Then exactly <count> symbols are reported

    Examples:
      | screenshot             | count |
      | intel-x.png            | 7     |
      | intel-xx.png           | 7     |
      | intel-xxx.png          | 8     |
      | intel-boss-running.png | 1     |

  @AT-2.3 @FR-2.2 @FR-2.3
  Scenario Outline: Type, position and status of each mission symbol
    When the detection runs on the reference screenshot "<screenshot>"
    Then a <type> symbol with status <status> is reported at about <x>,<y>

    Examples:
      | screenshot             | type   | x   | y   | status    |
      | intel-x.png            | HUNT   | 336 | 289 | AVAILABLE |
      | intel-x.png            | HUNT   | 483 | 315 | AVAILABLE |
      | intel-x.png            | RESCUE | 287 | 351 | AVAILABLE |
      | intel-x.png            | COMBAT | 340 | 378 | AVAILABLE |
      | intel-x.png            | HUNT   | 275 | 677 | AVAILABLE |
      | intel-x.png            | COMBAT | 568 | 680 | AVAILABLE |
      | intel-x.png            | BOSS   | 518 | 700 | AVAILABLE |
      | intel-xx.png           | HUNT   | 336 | 289 | AVAILABLE |
      | intel-xx.png           | HUNT   | 483 | 315 | AVAILABLE |
      | intel-xx.png           | RESCUE | 287 | 351 | RUNNING   |
      | intel-xx.png           | COMBAT | 340 | 378 | AVAILABLE |
      | intel-xx.png           | HUNT   | 275 | 677 | AVAILABLE |
      | intel-xx.png           | COMBAT | 568 | 680 | AVAILABLE |
      | intel-xx.png           | BOSS   | 518 | 700 | AVAILABLE |
      | intel-xxx.png          | HUNT   | 336 | 289 | AVAILABLE |
      | intel-xxx.png          | HUNT   | 483 | 315 | AVAILABLE |
      | intel-xxx.png          | RESCUE | 287 | 351 | DONE      |
      | intel-xxx.png          | COMBAT | 340 | 378 | AVAILABLE |
      | intel-xxx.png          | HUNT   | 275 | 677 | AVAILABLE |
      | intel-xxx.png          | COMBAT | 568 | 680 | AVAILABLE |
      | intel-xxx.png          | BOSS   | 518 | 700 | AVAILABLE |
      | intel-xxx.png          | HUNT   | 564 | 737 | DONE      |
      | intel-boss-running.png | BOSS   | 518 | 700 | RUNNING   |

  @FR-2.4
  Rule: The tier is the colour of the disc

    @AT-2.4
    Scenario Outline: Tier of each mission symbol
      When the detection runs on the reference screenshot "intel-xxx.png"
      Then the <type> symbol at about <x>,<y> has the tier <tier>

      Examples:
        | type   | x   | y   | tier   |
        | HUNT   | 564 | 737 | GOLD   |
        | BOSS   | 518 | 700 | GOLD   |
        | RESCUE | 287 | 351 | PURPLE |
        | COMBAT | 340 | 378 | PURPLE |
        | HUNT   | 275 | 677 | PURPLE |
        | HUNT   | 336 | 289 | BLUE   |
        | HUNT   | 483 | 315 | BLUE   |
        | COMBAT | 568 | 680 | BLUE   |

    @AT-2.5
    Scenario: The symbols are listed by tier, then from top to bottom
      When the detection runs on the reference screenshot "intel-xxx.png"
      Then the symbols are listed by tier, highest first, then from top to bottom
