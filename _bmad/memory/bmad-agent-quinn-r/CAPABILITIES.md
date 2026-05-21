# Capabilities

## Quality Review

- Two-mode quality rubric:
  - G2C pre-composition storyboard-bound authorization.
  - G3B post-composition forensic review of assembled artifacts.
- G5 pre-composition QA:
  - words-per-minute review against narration profile controls.
  - VTT monotonicity.
  - storyboard-to-narration coverage completeness.
  - motion-vs-narration duration coherence.
  - advisory-vs-blocking partition.

## Runtime Surfaces

- `app/specialists/quinn_r/_act.py` for the bounded act body.
- `app/specialists/quinn_r/quality_control_dispatch.py` for deterministic
  quality-control helper consumption.
- `app/specialists/quinn_r/sensory_bridges_dispatch.py` for perception helper
  consumption.
- `state/config/schemas/authorized-storyboard.schema.json` for the G2C
  `authorized-storyboard.json` write contract.

