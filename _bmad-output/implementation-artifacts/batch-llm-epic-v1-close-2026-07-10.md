# Epic CLOSE — Batch LLM Execution Mode (v1)

**Date:** 2026-07-10  
**Branch:** `dev/batch-mode-2026-07-10`  
**Party:** CLOSE 4/4 (John / Winston / Amelia / Murat)  
**Kanban:** `sprint-status.yaml` — all v1 stories `done`; epic `done`

## Claim envelope (what shipped)

- Opt-in `--llm-execution-mode batch` (default remains **realtime**)
- Vision / 07G only; non-eligible nodes stay realtime
- Product batch model = realtime **`gpt-5.5`** (nearest GPT-5-family fallback if Batch rejects)
- LiteLLM Files+Batches transport only — **no** `litellm.batch_completion`; **no** `app/models/adapter.py` edits
- `waiting_for_provider_batch` + `trial resume-batch`
- Cost report at `runs/<id>/llm_batch/cost-report.json`
- `prompt_cache_key` via shared `stable_perception_v1` (realtime + batch)
- A2 LiteLLM perception harness: hermetic done-bar; optional `--run-live`

## Explicit non-claims

- Batch is **not** the production default
- **A1-EXT** all-node tiering remains **TRAIL / deferred** (must not gate v1)
- Workbook is **not** batch-eligible
- Hermetic A2 green ≠ live quality proven; no byte-identical parity claims
- Live invoice accuracy / Enterprise LiteLLM cost APIs not claimed

## Story close map

| Key | Status |
|---|---|
| A0 LiteLLM dep | done |
| A1 vision profile | done |
| A3 eligibility | done |
| B1 adapter | done |
| B2 perception route | done |
| A2 perception harness | done (party GO-WITH-AMENDMENTS; review APPROVE) |
| B3 batch-wait pause | done |
| B4 cost report | done |
| B5 prompt-cache | done (party GO-WITH-AMENDMENTS; review APPROVE) |
| B6-land | done |
| B6-promote | done |
| A1-EXT | deferred (TRAIL) |

## Evidence / paths

- Stories SSOT: `_bmad-output/implementation-artifacts/batch-llm-execution-mode-stories-2026-07-10.md`
- A2: `app/runtime/llm_batch/perception_harness.py` + `scripts/utilities/run_perception_batch_harness.py`
- B5: `app/runtime/llm_batch/prompt_cache.py`
- Promote checklist: `_bmad-output/planning-artifacts/batch-llm-b6-promote-party-greenlight-2026-07-10.md`

## Formal disposition

**Epic v1 CLOSED.** Next product frontier returns to workbook artifact customization (and other deferred inventory). A1-EXT may reactivate only by explicit operator/party pull.
