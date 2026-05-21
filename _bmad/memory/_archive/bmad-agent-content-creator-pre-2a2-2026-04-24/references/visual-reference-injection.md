---
name: visual-reference-injection
code: VR
description: Select visual elements from perception artifacts; weave into narration with deictic references (script-backed)
---

# Visual Reference Injection (VR)

Implemented in `./scripts/visual_reference_injector.py::inject_visual_references` (per-slide) and `inject_all_slides` (whole-manifest). This file registers the capability with its unique code.

## Summary

For each slide in Pass 2, select `visual_references_per_slide` (default 2, ±1 tolerance per run config) visual elements from the perception artifacts. Weave them as **explicit deictic references** into narration — naming the element with spatial context and narrating an insight about it.

Example deictic form: *"Notice the **peak on the right side of the curve** — that's where the drug reaches maximum concentration about 90 minutes after dosing."*

## When to invoke

- Pass 2 Step 2, per-slide during narration composition.
- Re-run when `perception_artifacts` refresh mid-Pass-2 (e.g., after a slide re-dispatch).

## Entry points

```python
from skills.bmad_agent_content_creator.scripts.visual_reference_injector import (
    inject_visual_references, inject_all_slides
)

slide_refs = inject_visual_references(slide_id, perception, params)
deck_refs = inject_all_slides(perception_artifacts, narration_params)
```

Output shape: `visual_references[]` metadata per segment, populated into the segment manifest for downstream QA (Vera G4 extension).

See [pass-2-procedure.md](./pass-2-procedure.md) Step 2 and `state/config/narration-script-parameters.yaml` for `visual_references_per_slide`.
