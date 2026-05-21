# Memory

Curated long-term knowledge. Session logs live in `sessions/`; this file is the durable distillation.

## Current Delegation State

_Updated per session. If there's an active delegation cycle, record:_

- **Run ID + module/lesson:**
- **Pass:** 1 or 2
- **Phase:** intake / design / delegation / review / assembly / return
- **Writers engaged:**
- **Perception status (Pass 2):**
- **Motion plan status (Epic 14):**
- **Next planned action:**
- **Known blockers:**

## Writer Performance Patterns

_Learned over many delegations. Promote to durable patterns when stable._

- (empty — accumulates across sessions)

## Cluster Patterns

_What clustering choices worked. What concept densities mapped well to what interstitial counts. What master behavioral intents gave clean bridge cadence._

- (empty)

## Routing Learnings

_Content type X → writer Y → returns aligned on first pass at Z% rate. Pairings that need extra briefing._

- (empty)

## Operator Preferences

_Promoted from BOND when stable._

- (empty)

## Open Questions

_Things the operator hasn't resolved that affect future delegations. Date-stamped._

- (empty)

## Known Gotchas

_Perception corner cases, motion-asset pitfalls, narration-parameter quirks — things I learned the hard way and future-me needs to know._

- **2026-04-17**: `narration_profile_controls` are 11 keys from the Creative Director's creative directive, resolved into `state/config/narration-script-parameters.yaml` by the CD→resolver pipeline. Read from the active parameters file, not from raw CD output.
- **2026-04-17**: When perception artifacts refresh mid-Pass-2 (e.g., after slide re-dispatch), re-run `visual_reference_injector` against the refreshed artifacts. Do not reuse stale `visual_references[]` metadata.
- **2026-04-17**: Cluster interstitials' `behavioral_intent` must subordinate to the cluster's `master_behavioral_intent`. It may intensify or modulate but not contradict or redirect. Review at write-time, not just assembly-time.

## Historical Context

_Anchors that help me understand "why things are the way they are" across sessions._

- **2026-04-17**: Migrated from legacy sidecar (`_bmad/memory/irene-sidecar/`) to BMB sanctum (`_bmad/memory/bmad-agent-content-creator/`) as Epic 26 Story 26-2. Old sidecar deprecated but retained for Epic 27 cleanup. Marcus (26-1) was the pilot.
- **2026-04-17**: Legacy SKILL.md (203 lines) split into this sanctum (identity/doctrine) + `references/` (operational runbooks, 10 new stub refs for capability codes that previously shared refs or were script-backed).
- **Epic 23 (2026-04-15)**: Cluster-aware Pass 2 closed. Live mode is cluster-aware refinement. G4 criteria expanded from 15 to 19 with cluster extensions.
- **Epic 13 (2026-04-05)**: Mandatory perception contract added. Pass 2 narration never begins without `perception_contract.py::enforce_perception_contract` returning `status: "ready"`.
- **Epic 14 (2026-04-05)**: Motion-enabled workflow variant. Gate 2M is separate from Gate 2. Motion is additive; static is still the default.
