# Amendment — Durable all-six requires integrated local E2E (2026-07-10)

**Status:** Binding amendment to `phase2-six-mine-now-final-close-2026-07-10.md`  
**Trigger:** Shadow-monitor / operator requirement — per-slice evidence is not enough for durable “all six complete”; need one product workflow.

## Required bar (now MET)

1. `plan-dialogue` (or `plan-ratify`) produces planning companions + LOs in one `runs/<uuid>/`
2. Irene Pass-1 consumes that planning context and emits `irene-pass1.lesson-plan.json`
3. `lesson_plan["collateral"]` auto-derives `ComponentSelection`
4. `trial start` consumes that selection through the local runner/package-builder path
5. SME resolution exercised without silent Tejal reuse
6. Canonical / drill / prose checked in the same evidence chain as **named non-E2E adjuncts**
7. Final evidence includes run ids, verdict JSON, command transcript, and clear negative/fail-loud witnesses
8. **No Gamma / published deck** unless claimed (not claimed)

## Seam fix landed with this amendment

`start_trial()` previously only re-resolved **ratified** intent YAML when given `lesson_plan_collateral_intent_path`. Plan-JSON companions were ignored inside `start_trial` even when CLI `_resolve_start_component_selection` had already derived selection. Fixed: plan-JSON companions with `collateral`/`plan_units` are loaded via `load_selection_from_lesson_plan_json` and threaded into `component_selection` + receipt (`lesson_plan_selection_source`).

## Liveproof

| Field | Value |
|-------|-------|
| Driver | `scripts/utilities/bank_mine_integrated_e2e_liveproof.py` |
| Primary run | `runs/8099669e-e677-4578-9889-a62250c38fb0/` |
| Evidence | `_bmad-output/implementation-artifacts/evidence/mine-integrated-e2e-20260710T024036Z/` |
| Verdict | `pass: true` |
| Selection | `{deck, motion, workbook}` via `plan_collateral` → `narrated-deck-with-workbook` |
| Compose digest | `c53873edfaa9d570…` |
| Collateral forced | `false` (live Irene emitted present workbook collateral) |
| Negatives | absent-collateral fail-loud; unknown SME hard-fail; empty drill refuse |

## Adjunct note (honest)

Canonical validator, drill projector, and prose uplift are stamped in the same evidence pack as **named non-E2E adjuncts** — not claimed as in-graph production-walk steps of this E2E.

## Prior per-slice closes

Remain valid as component closes. Durable program close for “all six complete” now additionally requires this integrated E2E (or equivalent).
