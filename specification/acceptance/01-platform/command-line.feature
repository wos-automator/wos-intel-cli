@FR-1.3
Feature: Command line interface
  The operator starts wos-intel as "python -m wos_intel <command>". These scenarios need no
  device: they run the detection on a reference screenshot and check the usage errors.

  @AT-1.1 @FR-1.4
  Scenario: Detect a reference screenshot
    Given a copy of the reference screenshot "intel-xxx.png"
    When I run "detect" on the screenshot
    Then the exit code is 0
    And every log line starts with a timestamp
    And the log names the state "INTEL_CLAIMABLE" and the stamina 2035
    And the log lists 8 symbols, among them:
      | symbol                        |
      | RESCUE PURPLE DONE at 287,351 |
      | HUNT GOLD DONE at 564,737     |
    And the debug image "intel-xxx.debug.png" lies next to the screenshot

  @AT-1.2
  Scenario Outline: A usage error names the commands
    When I run wos-intel with the arguments "<arguments>"
    Then the exit code is 2
    And the usage names the commands run, detect and snap

    Examples:
      | arguments |
      |           |
      | fly       |
