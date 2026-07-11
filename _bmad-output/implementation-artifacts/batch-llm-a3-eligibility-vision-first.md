# Story: batch-llm-a3-eligibility-vision-first — Eligibility matrix

**Status:** done  
**Epic:** `epic-batch-llm-execution-mode`  
**Kanban key:** `batch-llm-a3-eligibility-vision-first`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate:** single-gate  
**Depends:** A1 (authored in parallel; merged after A1 green)  
**SSOT:** `batch-llm-execution-mode-stories-2026-07-10.md` §A3

## Story

As the Marcus-SPOC runtime, I need an on-disk batch-eligibility matrix with criteria (a)–(e) so v1 only routes vision (07G) when `execution_mode=batch`.

## Acceptance Criteria

1. `runtime/config/llm_batch_eligibility.yaml` lists known sites with `batch_eligible`, `v1_routed`, `criteria_met`, `rationale`.
2. Criteria (a)–(e) defined on disk; vision meets all five and is `v1_routed: true`.
3. Workbook / enrichment / Mine-6 / Gary / Enrique / monolithic Irene-G0-CD-Marcus = not eligible (or not v1-routed).
4. Loader exposes `is_v1_batch_routable` / `v1_routable_sites()` → `("vision",)` only.
5. CLOSE = matrix + loader only — B6 reads it later; no live API.

## Dev Agent Record

### Completion Notes

- Rubric (a)–(e) authored from research STRONG reasons (fan-out, join key, no mid-HIL, contract schema, OpenAI LLM).
- Vision rationale cites prior good-read batch id + LiteLLM dispatch delta.
- Hermetic shape-pin + negative validation tests green.

### File List

- `runtime/config/llm_batch_eligibility.yaml`
- `app/runtime/llm_batch_eligibility.py`
- `tests/runtime/llm_batch/test_batch_eligibility_matrix.py`
- `_bmad-output/implementation-artifacts/batch-llm-a3-eligibility-vision-first.md`
