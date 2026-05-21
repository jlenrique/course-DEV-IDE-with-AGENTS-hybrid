# Kira Capabilities

- Parse `motion_plan.yaml` directives from an envelope payload or file path.
- Generate per-slide Kling motion requests through the shipped Kling client lane.
- Write `[bundle]/motion/<slide_id>.progress.json` during generation.
- Write `[bundle]/motion/<slide_id>.json` terminal receipts with cost tracking.
- Emit `[bundle]/recovery/inspection/<slide_id>/` notes for failed slides.
- Abort cleanly on budget exhaustion before attempting subsequent slides.
