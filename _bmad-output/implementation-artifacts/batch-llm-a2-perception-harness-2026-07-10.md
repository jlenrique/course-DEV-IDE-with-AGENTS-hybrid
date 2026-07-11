# Story A2 — Perception eval harness (LiteLLM)

Status: done  
Date: 2026-07-10  
Epic: Batch LLM Execution Mode  
Depends: B1 (done); may trail B2 (done)  
Party: GO-WITH-AMENDMENTS (2026-07-10) — MUST folded below  
Code-review: APPROVE (2026-07-10)

## Goal

Rebuild a **LiteLLM-backed** perception quality harness that compares **realtime vs batch** on the **same model family** (`gpt-5.5` / nearest GPT-5-family), using frozen leg3 c-u03 probe PNGs. Informs fallback **only if** Batch rejects `gpt-5.5`. Not a smoke-script clone; not provider-feasibility rediscovery.

## Acceptance Criteria

1. Frozen slides = evidence PNGs (slide_01 + slide_02 only):
   - `_bmad-output/implementation-artifacts/evidence/leg3-cu03-subslide-invariant-20260701T021037Z/gamma-export/c-u03-persubslide-probe_slide_01.png`
   - `..._slide_02.png`
2. Offline scaffolding runnable without network: fixture layout, scoring schema, compare report shape, hermetic unit tests.
3. Optional `--run-live` arm: LiteLLM Files+Batches path vs realtime façade on `gpt-5.5` (or configured vision profiles); writes compare report under evidence/scratch. **Never gates CI/story done.**
4. Documents harness baseline batch id `batch_6a457bcac6488190b79224e61ea89b26` as narrative only (non-executable; gpt-4.1-mini quality baseline).
5. Does **not** expand into Irene/G0 platform eval; vision/07G only.
6. No `litellm.batch_completion`; no `app/models/adapter.py` edits.
7. **Eval sidecar only** — no mutation of production defaults / eligibility / vision routing / fallback; reuse B1+B2 only.
8. Compare = semantic/score deltas only — forbid byte-identical / exact-match parity claims; hermetic green ≠ live quality proven.
9. Scoring asserts ≥1 non-vacuous field; pin CLI + hermetic test paths + golden compare-report shape.

## Paths (pinned)

- Module: `app/runtime/llm_batch/perception_harness.py`
- CLI: `scripts/utilities/run_perception_batch_harness.py`
- Tests: `tests/runtime/llm_batch/test_perception_harness.py`
- Schema/golden: `tests/runtime/llm_batch/fixtures/perception_harness/`

## DoD

- `pytest` hermetic suite green without API keys.
- Live arm gated `--run-live` (skip/fence when no key).
- Story → done after code-review.

## Out of scope

A1-EXT; workbook; live invoice; production default batch.
