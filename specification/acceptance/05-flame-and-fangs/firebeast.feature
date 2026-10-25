@FR-5.5
Feature: Firebeast pin
  During the Flame and Fangs event a gold pin with the head of the firebeast appears on the
  Intel screen. It is a hunt like any other.

  @AT-5.1
  Scenario: The firebeast is a gold hunt
    When the detection runs on the reference screenshot "flame-and-fangs-missions.png"
    Then the HUNT symbol at about 430,279 has the tier GOLD
