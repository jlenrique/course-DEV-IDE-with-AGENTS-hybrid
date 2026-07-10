# PROOF — Marcus solicitation Claims A+B

**Stamp:** `marcus-solicitation-success-20260709T230000`  
**Status:** **COMPLETE-with-named-fenced-residuals** (party 4/4)  
**Success definition:** `marcus-solicitation-lesson-plan-success-definition-2026-07-09.md`

## Claim A — PASS (fenced consumer-root)

| Signal | Result |
|--------|--------|
| `plan-ratify` CLI wrote companion + intent | YES — `claim-a/live-run-dir/` |
| `load_planning_context` purpose/audience/rich | YES — Tejal rich |
| Selection delta changed (motion true→false) | YES |
| `compose_and_digest` on after-selection | YES — digests in `load-compose-proof.json` |
| Trial threads ratified selection | YES — spy path `trial-intent-consume.json` |
| Gamma spend | 0 |

## Claim B — PASS on emit-path (fenced: not live OpenAI)

| Signal | Result |
|--------|--------|
| Coverage receipt + purpose/audience ack | YES — pytest Claim B |
| Plan hash ≠ control | YES — `test_claim_b_plan_delta_vs_control_hashes` |
| `planning_provenance` on lesson_plan when context present | YES |
| Absent path omits provenance | YES |
| Live OpenAI Irene Pass-1 on Tejal RUN_DIR | **FENCED — not run** |
| Recording fake LLM exercises real `act()` emit | YES |

## Named fences (binding)

1. Claim B uses `_RecordingHandle` — **not** a live OpenAI Pass-1 on Tejal.
2. Claim A consumer root banked under evidence `live-run-dir`, not `runs/<uuid>/` (FG-6 residual).
3. Do **not** claim “bespoke” or “live model informed the plan.” Framing-only pipe proven.
4. Non-claims held: Gamma, SPOC REPL rewrite, lecture ingest, SME/projector.

## Pytest

- Claim A suite + Claim B handoff: **25 passed** (`per-component/03-full-claim-ab-suite.txt`)
- Claim B core predicates: **3 passed** (`claim-b/claim-b-core-predicates.txt`)

## Next for unfenced Claim B COMPLETE

One Tejal `runs/<uuid>/` Pass-1 with live model + banked `irene-pass1.md` / coverage / provenance vs control.
