---
name: motion-plan-hydration
code: MP
description: Apply Gate 2M decisions from motion_plan.yaml into segment-manifest motion fields (script-backed)
---

# Motion Plan Hydration (MP)

Implemented in `./scripts/manifest_visual_enrichment.py::apply_motion_plan_to_segments`. This file registers the capability with its unique code.

## Summary

For motion-enabled runs (Epic 14), the Gate 2M operator decisions live in `context_paths.motion_plan` / `motion_plan.yaml` keyed by `slide_id`. Irene's segment manifest inherits the following fields per segment:

- `motion_type` — static | video | manual-animation
- `motion_asset_path` — approved asset (MP4, GIF, embedded)
- `motion_source` — kling | imported | external
- `motion_duration_seconds`
- `motion_brief` — operator-supplied description
- `motion_status` — approved | generated | imported

## Fail-closed behavior

- Unknown `slide_id` in `motion_plan.yaml` → halt with scope violation.
- Non-static segment missing required fields → halt.
- `motion_enabled: false` → every segment is explicitly static; MP does not run.

## When to invoke

- Pass 2 Step 3 (motion-enabled only).
- After perception contract passes (Step 0) and narration is written (Step 2).

## Entry point

```python
from skills.bmad_agent_content_creator.scripts.manifest_visual_enrichment import (
    apply_motion_plan_to_segments
)

enriched_manifest = apply_motion_plan_to_segments(segment_manifest, motion_plan)
```

See [pass-2-procedure.md](./pass-2-procedure.md) Step 3.
