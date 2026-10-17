## 4. Stamina

- Shown at the top right of the Intel screen (barrel symbol, e.g. "2,035"). Verified:
  2,057 → 2,047 after a hunt (−10) → 2,035 after a rescue (−12).
- Reading: digit OCR by template matching on single digits (no Tesseract dependency),
  region ≈ x 595–675, y 25–60. The comma is the thousands separator.
- Before every mission: `stamina >= cost(type)`, otherwise skip the mission.
  Stamina < 10 → the program ends regularly.
- Fallback if OCR fails: carry on, but detect a "not enough stamina" dialog
  (reference image still missing) and then end.
