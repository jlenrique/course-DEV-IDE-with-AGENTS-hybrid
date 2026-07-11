# Story R1 — Posture runtime on production seam

Status: done  
Date: 2026-07-10  
Epic: Agentic Research Foundations  
Depends: R0 (done)  
Party: GO-WITH-AMENDMENTS folded (Amelia single-seam MUST)

## Goal

Replace one-shot generic Scite search shaping with **posture-aware** intent emission (corroborate / gap_fill / embellish) on the **single** production seam (`research_wiring` / IreneTracyBridge), flag-gated. Texas dispatcher remains the only fetch path.

## Acceptance Criteria

1. Single seam: posture-aware `DeterministicPostureSelector` **or** implement `PostureDispatcher` and swap the bridge call site — not both fantasies.  
2. All three postures emit valid `RetrievalIntent` without `NotImplementedError`.  
3. Flag-OFF (`MARCUS_RESEARCH_DETECTIVE_LIVE` unset/false): bit-identical to today’s selector path.  
4. Hermetic: reuse `tests/fixtures/retrieval/tracy_smoke/`; extend contracts.  
5. **LIVE (operator binding):** Scite dispatch for ≥1 corroborate + ≥1 gap_fill from Tejal/fixture `research_goals`; evidence under `_bmad-output/implementation-artifacts/evidence/research-r1-*/`.  
6. No Tracy→HTTP bypass; no `scripts/api_clients/` fork.

## DoD

Hermetic green **and** authentic live evidence pack. Default flag may remain OFF after live probe if R3+R4 not yet green (document in Completion Notes).

## Completion Notes (2026-07-10)

- **Seam chosen:** posture-aware `DeterministicPostureSelector` (production); `PostureDispatcher` is a thin façade over the same selector — not a second shaping fantasy.
- **Flag:** `MARCUS_RESEARCH_DETECTIVE_LIVE` default remains OFF (R3+R4 not green yet). Flag-OFF intent text + hint params bit-identical to pre-R1.
- **Hermetic:** 20 tests green (`test_research_r1_posture_runtime.py` + updated `test_tracy_postures.py`).
- **Live:** `evidence/research-r1-20260710T211425Z/` — corroborate DOI `10.1145/3368308.3415426`; gap_fill DOI `10.46542/pe.2023.231.491498`.

## Out of scope

Consensus triangulation (R2/R3); credibility fields (R4); Jefferson (R5); hard pause (R7); LLM Tracy graph.
