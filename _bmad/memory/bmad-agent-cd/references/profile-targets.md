---
name: profile-targets
code: PT
description: Initial numeric anchors for slide_mode_proportions per experience profile (visual-led, text-led) — program-validated bootstrap for directive emission
---

# Experience Profile Targets (20c-12 bootstrap)

These profile anchors define initial numeric targets for `slide_mode_proportions`.

## Visual-Led

- `literal-text`: `0.15`
- `literal-visual`: `0.25`
- `creative`: `0.60`

## Text-Led

- `literal-text`: `0.60`
- `literal-visual`: `0.25`
- `creative`: `0.15`

Both targets satisfy the sum-to-1.0 contract and are intentionally opposite-weighted to support profile A/B behavior in downstream resolver work.
