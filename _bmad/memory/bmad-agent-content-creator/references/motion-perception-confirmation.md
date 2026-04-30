---
name: motion-perception-confirmation
code: MC
description: Validate approved motion assets; produce video perception confirmations for non-static segments (script-backed)
---

# Motion Perception Confirmation (MC)

Implemented in `./scripts/perception_contract.py::enforce_motion_perception_contract`. This file registers the capability with its unique code.

## Summary

After motion-plan hydration (MP), any non-static segment must have its approved motion asset verified: the file is readable, the duration matches, and the video sensory bridge produces a perception artifact that Irene can cite in narration ("visible action: ...").

Static segments bypass this step — they're governed by the approved slide PNG plus image perception artifacts (from PC).

## Fail-closed behavior

- Unreadable motion asset → halt.
- Asset duration inconsistent with manifest → halt.
- LOW-confidence motion perception after retry → escalate to Marcus.

## When to invoke

- Pass 2 Step 4 (motion-enabled only, for every non-static segment).
- Before returning the final manifest to Marcus.

## Entry point

```python
from skills.bmad_agent_content_creator.scripts.perception_contract import (
    enforce_motion_perception_contract
)

result = enforce_motion_perception_contract(manifest, motion_plan)
if result["status"] != "ready":
    return result
```

See [pass-2-procedure.md](./pass-2-procedure.md) Step 4 and `skills/sensory-bridges/references/perception-protocol.md` for the video-bridge protocol.
