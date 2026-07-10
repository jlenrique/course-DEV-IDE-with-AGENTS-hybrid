# Story: batch-llm-b6-land-switch — SPOC opt-in `llm_execution_mode` (land)

**Status:** done  
**Epic:** `epic-batch-llm-execution-mode`  
**Kanban key:** `batch-llm-b6-land-switch`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate:** single-gate  
**Depends:** B1 done; B2 done; A3 done  
**Does NOT depend on:** B3, B4 (those gate **B6-promote** only)  
**Party:** John/Winston/Amelia/Murat **4/4 GO-WITH-AMENDMENTS** — `batch-llm-b6-land-party-greenlight-2026-07-10.md`  
**Code-review:** PASS-WITH-FIXES → folded — `batch-llm-b6-land-code-review-2026-07-10.md`

## Story

As the Marcus-SPOC operator, I need a run-start **opt-in** `realtime|batch` switch so a production trial can route A3-eligible vision perception through the B2 Batch transport — while every standard/unset run stays on the existing realtime path with **zero** Batch side effects.

## Seam (party-folded)

1. `RunState.llm_execution_mode: Literal["realtime","batch"] = "realtime"`
2. CLI: `trial start --llm-execution-mode {realtime,batch}` default `realtime`; `trial-start.json` + wait-note stub
3. `run_production_trial(..., llm_execution_mode=...)` sets field on initial `RunState`
4. `apply_llm_execution_mode_overlay`: vision + exact `batch` only; never overlay realtime; strip key from non-vision
5. Pause wording: land stub only (B3 owns pause class)

## Acceptance Criteria

1. **Default OFF / realtime (T7):** MET — spies on create_file/create_batch/submit/batch_route; no `llm_batch/`
2. **Opt-in ON:** MET — CLI → RunState → vision payload overlay; receipt records `batch`
3. **Invalid values:** MET — argparse choices + RunState Literal
4. **Vision-only:** MET — overlay helper + strip leak
5. **Resume continuity:** MET — model_dump / validate round-trip; legacy missing key → realtime
6. **SPOC surface:** MET — `trial start --llm-execution-mode`
7. **Pause wording stub:** MET — `llm_batch_wait_note` on batch receipt only
8. **Non-claims:** MET — no B3/B4/promote

## Tasks

- [x] Party green-light — fold MUST
- [x] RED→GREEN: RunState, CLI, receipt, overlay, T7
- [x] `bmad-code-review` → done

## Dev Notes

- Field name **`llm_execution_mode`** — not `run_constants.execution_mode`
- Do not edit `app/models/adapter.py`
