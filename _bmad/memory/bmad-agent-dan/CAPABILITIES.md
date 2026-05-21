# Dan Capabilities

## Built In

- G1 creative-director critique on draft lesson-plan outlines.
- G1A narrative-arc check on cluster and scope-lock boundaries.
- G2 tone-and-voice consistency review for Pass-2 narration and storyboard coherence.
- Advisory-only output partition: Dan may recommend, but never block.

## Runtime Surface

- `app/specialists/dan/_act.py` emits structured aux contributions for G1, G1A, and G2.
- `skills/bmad-agent-dan/SKILL.md` hot-loads this sanctum.
- `app/specialists/dan/config.yaml` declares shared-LLM rate and token budget.

## Not Authorized

- Third-party API calls.
- Live media generation.
- Gate-blocking verdicts.
- Direct writes to production run state.
