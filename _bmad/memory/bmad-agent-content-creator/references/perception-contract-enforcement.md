---
name: perception-contract-enforcement
code: PC
description: Enforce Irene's mandatory perception contract before Pass 2 narration (script-backed)
---

# Perception Contract Enforcement (PC)

Implemented in `./scripts/perception_contract.py::enforce_perception_contract`. This file registers the capability with its unique code.

## Summary

Before any Pass 2 narration work begins, Irene enforces the perception contract. This validates `perception_artifacts[]` presence in the context envelope, generates them inline via the image sensory bridge if absent, retries LOW-confidence slides once, and escalates persistent LOW to Marcus.

**Invariant:** Narration MUST NOT begin until the contract returns `status: "ready"` or Marcus explicitly authorizes proceeding despite LOW confidence.

## When to invoke

- Pass 2 Step 0 (unconditional).
- Any time the perception artifacts may be stale (e.g., slide re-dispatch happened and new PNGs replaced old ones).

## Entry point

```python
from skills.bmad_agent_content_creator.scripts.perception_contract import enforce_perception_contract

result = enforce_perception_contract(envelope)
if result["status"] != "ready":
    # escalate to Marcus or halt
    return result
```

See [pass-2-procedure.md](./pass-2-procedure.md) Step 0 and `skills/sensory-bridges/references/perception-protocol.md` for the five-step protocol.
