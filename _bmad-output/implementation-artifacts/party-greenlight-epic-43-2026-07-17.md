# Party green-light record — Epic 43 (HIL Surface Tabular Coverage)

**Date:** 2026-07-17 · **Verdict:** 5/5 SIGN-WITH-RIDERS
**Seats:** Winston (architect) · John (PM) · Amelia (dev) · Murat (test architect) · Sally (UX / operator-surface lens)
**Proposal:** `_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md`
**Trigger:** operator trial `5169a872` (2026-07-17) — G0 directive confirm rendered as a raw YAML dump; two read-only code audits established that the tabular projector (built in Epic 42-1) covers only G0 identity+enrichment while all 14 gate poll-surfaces have no renderer. Operator directive: **scope to all gates.**

## Decisions

1. **Green-light epic scope (all gates):** YES, unanimous.
2. **4-slab decomposition / story cut (43-1..43-12):** accepted with re-ordering (R1, R6).
3. **Sequencing:** Slab 1 first; low-frequency gates (motion, research/workbook) last.
4. **43-10 coverage test RED-first:** YES, as a shrinking-allowlist registry test (R3).
5. **Three operator pins correctly generalized:** confirmed (no raw human dumps / renderer-per-content-type / ACs name each surface + coverage test).
6. **Risks acknowledged:** additive-within-v1 projection contract (R7); stdout/stderr split hard invariant (R4); pure-render zero-live-spend replay (R2).

## Binding riders

- **R1 (Winston):** 43-2 generic scaffold + registry lands FIRST in Slab 1; 43-1 plugs into it. Scaffold before bespoke.
- **R2 (Amelia):** Slab-0 fixtures (real `directive.yaml` / `decision-card-*.json` / poll-surface dicts from `5169a872` + `bc747b51`) captured before any renderer; nested-value summarization bounded (`_summarize_context_entry`).
- **R3 (Murat):** 43-10 RED-first registry test, shrinking known-unrendered allowlist 15→0; 43-12 fails if non-empty.
- **R4 (Amelia):** stdout machine-JSON / stderr human-surface split = hard invariant, re-asserted per emit-touching story.
- **R5 (Sally):** raw-access affordance defined epic-wide (not just G0 `[e]dit`); width-aware/fixed-width description column.
- **R6 (John):** motion (43-7) + research/workbook (43-9) sequenced last.
- **R7 (Winston):** operator-surface projection additions additive-within-v1 (AD-4/35.9).

## Dispatch order

`Slab-0 fixtures` → 43-2 → 43-10 → 43-1 → 43-3 → 43-4 → 43-5 → 43-6 → 43-8 → 43-7 → 43-9 → 43-11 → 43-12.

## Consensus

No impasse; the party-mode impasse chain was not invoked. Riders are enforced by tests (R3/R4) and contract discipline (R7), not prose. Fresh-dev-agent per story; `bmad-code-review` before each `done`.
