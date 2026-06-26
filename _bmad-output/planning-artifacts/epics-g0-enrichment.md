---
title: Epic — G0 Source-Content Enrichment Cycle (v1)
status: in-progress
class: S
branch: fidelity-perception-arc-2026-06-19
inputDocuments:
  - _bmad-output/planning-artifacts/g0-enrichment-cycle-charter-2026-06-26.md
  - _bmad-output/planning-artifacts/lo-schema-ratification-2026-06-26.md
ratified_by: party-mode (Winston, John, Marcus, Mary, Irene) 2026-06-26 — unanimous GREEN-WITH-AMENDMENTS, no impasse
stepsCompleted: [epic-design]
---

# Epic: G0 Source-Content Enrichment Cycle (v1)

## Goal
Move Learning-Objective identification and source-content typing UP to the G0 front door so that **source content + LOs are KING — complete + reliably accessed** before any downstream artifact is produced. Marcus-SPOC runs an LLM enrichment pre-pass conversationally (OFF the deterministic critical path); the operator confirms; Irene refines LOs in place and assesses source-content adequacy; the operator ratifies. Every downstream artifact (slides/quiz/workbook/narration) then inherits complete, provenance-anchored, adequacy-checked LOs.

## Governing principle (binding)
SOURCE content + LOs are KING. LLM inference is SPOC-side, never in the deterministic composer. Marcus-SPOC OWNS source+LOs (custodial + gate-bearing, not authorial). Completeness = operator's call (informed by what Marcus reached); reliable access = Marcus proves deterministically (RED on failure, never silently absent).

## Requirements traceability
Requirements are the binding amendments A1–A11 (charter) + the ratified schema/contract (ratification doc). Key:
- **A1** access verification deterministic + LOUD (RED on failure).
- **A2** typing + LO findings are proposals with mandatory provenance + first-class (advisory) confidence.
- **A3** mandatory real DISSENT artifact (run-level ≥1; independent-parse-sourced; variance; adjudication disposition).
- **A4** independent-parse-first ordering (anti-anchoring; deterministic ts guard).
- **A5** two human gates wired into BOTH production_runner walks.
- **A6** completeness invariant — deterministic enumeration of ALL sources stays in the composer; LLM advises, never gates a file out.
- **A7** unify the LO schema first (S1 pre-req).
- **A8** never overturn the operator's prior unilaterally.
- **A9** (Mary) source_ref = structured locator {source_id ∈ enumerated set, locator, verbatim quoted_span}.
- **A10** (Mary) manifest-confirm surfaces enumeration provenance + traversal roots.
- **A11** (Mary) dissent disposition field + variance.
- TYPE ⟂ ROLE (operator): a span's type is orthogonal to its primary/supporting/ignore role; a consumer-less type is typed accurately and may still be `supporting`.

## Stories (strict sequence S1 → S2 → S3; each: spec → dev → T11 → LIVE-segment trial → party-close)

### S1 — LO canonical schema + transition guard + adapter  (pre-req; schema-shape; single-gate) — ✅ DONE (T11-closed 2026-06-26)
Build the canonical `LearningObjective` pydantic-v2 entity (status-conditional invariant table), `SourceRef` structured locator (A9), `SourceAdequacy`, the deterministic `advance_lo(actor)` transition guard (closed edge-map), emitted JSON Schema + shape-pin tests, and a thin adapter FUNCTION over the 4 existing LO representations. Replace-and-rewire; no persisted parallel entity. Closes A7.
**DoD:** schema + guard + JSON Schema + shape-pin tests green; adapter maps all 4 reps; full suite + ruff + import-linter green; no behavior change to existing consumers (adapter byte-identity where applicable).

### S2 — G0-enrichment brick + operator confirm-gate #1  (Marcus-SPOC-owned)
Source-span typing into the 10-type closed enum + `other:<label>` escape hatch; candidate-LO extraction emitting `status=provisional` with `SourceRef`s, OFF the deterministic critical path (LLM pre-pass, corpus-state-keyed cache for replay determinism). Operator confirm-gate #1 wired into BOTH production_runner walks. A4 independent-parse-first sidecars; A3 dissent scaffold (run-level ≥1 real dissent); A10 manifest enumeration-provenance + traversal-roots surfaced at the gate. Closes A1/A2/A3/A4/A6/A10/D1/D2.
**DoD:** live G0 run on real corpus emits a typed manifest + provisional LOs with resolvable provenance; gate #1 pauses + presents the reconcilable view; dissent + independent-parse artifacts real; NO new Gamma/video/audio (upstream of Gary).

### S3 — Irene refinement loop + ratify-gate #2 + completeness assert
Irene refines `provisional→refined` in place; per-LO `SourceAdequacy` (adequate/thin/gap rubric, assessability-leg discriminator) — **ADVISORY ALERT ONLY, never a blocker** (operator + off-world SME make the final adequacy call; content may be created outside this app; a thin/gap flag may valuably suggest a research run or special artifact-creation guidance via `suggested_followups`). Emits the signed LO-delta contract (all channels: disposition codes refined-in-place/unchanged/split/merged/flagged-inadequate/proposed-new/recommend-drop). Operator gate #2 ratifies `refined→ratified` (Irene may NEVER set ratified). Completeness hard-assert is about ACCESS + ASSESSMENT-PRESENCE, not adequacy outcome: every span typed-or-ignored; every LO ≥1 resolvable SourceRef + a *populated* adequacy verdict; source unreachable=RED; a thin/gap verdict does NOT fail the assert. Closes A5/A8/A9/A11 + the operator-mandated Irene loop.
**DoD:** live run carries provisional LOs through Irene refinement + adequacy + ratify gate into a refined lesson plan; completeness assert holds (access + assessment-present); adequacy warnings surfaced (never blocking); reconciliation ledger balances.

## Epic DoD (goal)
A real trial-production run from G0 → enrichment → Irene loop → pre-planning → **hand-off-to-Gary gate, error-free, TWICE.** Validation runs do not create new Gamma/video/audio (they halt at the Gary gate) unless a regression blast-radius warrants. Vigilant regression guard throughout.

## Deferred follow-ons (→ deferred-inventory.md; not in v1)
- Native producer/consumer rewiring beyond what S2/S3 touch.
- Multi-turn Marcus↔operator LO negotiation (v1 = confirm-or-rerun at each gate).
- Acted-upon typing — routing typed slide/quiz/workbook spans INTO the generators (07W/07D.5 become consumers).
- quiz / rubric / exercise-lab / discussion-forum / assignment-instructions generators (consumer-less types today; typed-and-shown only in v1).
