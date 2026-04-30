# Mike Sidecar — Does Not Apply

**Agent:** Mike (Compositor)
**Role:** Deterministic script-driven audio/video compositor
**Status:** Sidecar intentionally absent — see below

## Why this stub exists

Mike is the operator-persona handle for the `compositor` skill. The compositor is a deterministic, script-driven assembly step — it executes the segment manifest plus timing contracts to produce composited video. It does not make judgment calls, does not delegate to other specialists, and does not accumulate cross-session patterns that would benefit from a learning-memory sidecar.

This stub exists only so that any future enumeration routine (e.g., a sidecar-coverage audit, a script that iterates `skills/*/` and expects a matching `_bmad/memory/{agent}-sidecar/`) finds a deliberate "does not apply" marker rather than flagging a missing sidecar.

## Do not populate

- No `patterns.md`, `chronology.md`, or `access-boundaries.md` should be added here.
- If a future learning mechanism becomes relevant to compositor behavior (e.g., timing-drift patterns that only show up across many runs), reconsider the decision explicitly rather than drifting into ad-hoc sidecar writes.

## References

- Skill: `skills/compositor/SKILL.md`
- Persona-vs-lane note: "Mike" is the persona handle; "compositor" remains the skill and contract term.

## Creation

- **2026-04-16:** Created during the P0 remediation pass to head off any future sidecar-coverage sweep that might waste time hunting for a compositor learning memory that does not exist by design.
