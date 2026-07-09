# Claim Envelope — Marcus planning ratification surface (2026-07-09)

**Branch:** `dev/lesson-planning-2026-07-09`  
**Goal file:** `goal-marcus-planning-ratification-surface-2026-07-09.txt`  
**Party:** John / Winston / Amelia / Murat — fully spawned  
**Verdict:** **GO-WITH-AMENDMENTS** (4/4)  
**Gate:** dual-gate (Murat honesty; Amelia would accept single if M5 out — dual retained)

## Operator amendment (2026-07-09 mid-session)

**W5 / full asset compose liveproof is REQUIRED for session COMPLETE.**
Prior fence of W5 OUT is overridden by operator authority.
Party re-concurrence 4/4: binding W5 done-bar = **Option A** —
`compose_and_digest` on selection from plan-ratify intent + selection delta vs
baseline + trial start threads that selection into `run_summary` (**no Gamma spend**).
Do not claim published Gamma / AFK-HIL spend walk as this W5.

## Binding claim (when done)

Operator can drive assess → elicit/confirm → ratify via a thin Marcus CLI
(`python -m app.marcus.cli plan-ratify`) that writes loadable
`planning-ratification.json` + `ratified-collateral-intent.yaml`;
`load_planning_context` and trial `--lesson-plan-collateral-intent` consume
those artifacts; **and** local compose succeeds on the changed selection (W5).
Absent path unchanged.

## MUST amendments (folded)

| # | Amendment | Source |
|---|-----------|--------|
| 1 | **AC-M5 OUT** — no Irene `lesson_plan` provenance refs this slice (John/Amelia/Murat majority; Winston dissent noted — next pipe seed) | 3/4 |
| 2 | Real CLI surface, not library-only script | John/Amelia/Murat |
| 3 | Non-interactive flags are the contract | Amelia |
| 4 | Write dir = load dir; trial start still uses existing `--lesson-plan-collateral-intent` (no auto-wire) | Winston/John |
| 5 | Recorder-only: call existing assess/ratify/write | all |
| 6 | AC-M6 absent path proven | John/Murat |
| 7 | Trial-intent consumption in liveproof (not files-only) | Murat |
| 8 | Per-component live-tests banked | Murat/operator |
| 9 | **W5 IN** — local compose on changed selection + delta + trial run_summary | Operator override + party 4/4 |

## Explicit non-claims

Full SPOC REPL rewrite; **Gamma-spend / published live deck walk** (not this W5);
lecture ingest; SME/projector; auto Irene→selection; planning_context fan-out;
lesson_plan ref emit (M5); S8 reopen; step-1 rebuild.

## Winston dissent (named)

AC-M5 IN as additive `planning_provenance` pointers — deferred to next slice
as the lesson-plan-as-pipe seed. Not blocking this close.
