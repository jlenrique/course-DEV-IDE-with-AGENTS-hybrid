# Story: batch-llm-b1-runtime-adapter — LiteLLM Batch adapter scaffold

**Status:** done  
**Epic:** `epic-batch-llm-execution-mode`  
**Kanban key:** `batch-llm-b1-runtime-adapter`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate:** single-gate (`bmad-code-review` before done) — **CLOSED** via `batch-llm-b1-code-review-2026-07-10.md`  
**Depends:** A0 done  
**SSOT:** `batch-llm-execution-mode-stories-2026-07-10.md` §B1  
**Party epic green-light:** `batch-llm-party-greenlight-2026-07-10.md`

## Story

As the Marcus-SPOC runtime, I need a LiteLLM Files+Batches adapter under `app/runtime/llm_batch/` so perception (and later eligible nodes) can submit/poll/join provider Batch jobs without touching `make_chat_model` / realtime ChatOpenAI.

## Acceptance Criteria

1. Wrap LiteLLM `create_file` / `create_batch` / `retrieve_batch` / `file_content` (+ cancel); `custom_llm_provider="openai"`; `endpoint="/v1/chat/completions"`.
2. Receipts under `runs/<uuid>/llm_batch/receipt.json` via normalized `BatchReceipt`.
3. Join by `custom_id`; out-of-order OK; failed row isolated.
4. Pre-upload JSONL size estimate + fail-loud oversize (`tag=llm_batch.jsonl.oversize`); default budget 200 MiB.
5. Hermetic anti-`batch_completion` guard (AST + injectable callable refuse).
6. **Not** a raw OpenAI-only client; **not** edits to `app/models/adapter.py`.
7. Dispatch delta: normalize LiteLLM returns into receipt/join types (T0).

**CLOSE claim:** scaffold only — not vision route, not SPOC switch, not pause class.

## Out of scope

- B2 perception JSONL from PNGs / `_parse_response`
- B3 `waiting_for_provider_batch`
- B6 run-start switch / `RunState.llm_execution_mode`

## Tasks

- [x] Modules: `adapter`, `jsonl`, `join`, `receipts`, `errors`
- [x] Hermetic tests: join, size, mocked submit/receipt, anti-batch_completion
- [x] ruff clean on package
- [x] `bmad-code-review` triage → fold MUST fixes
- [x] Flip Kanban to `done`

## Dev Agent Record

### Completion Notes

- Injectable SDK callables for hermetic T0.
- `submit_and_receipt` + `join_completed_output` happy path covered with mocks.
- Premature `RunState.llm_execution_mode` / `llm_execution_mode.py` **reverted** — belongs in B2/B6 create-story, not B1.

### File List

- `app/runtime/llm_batch/{__init__,adapter,jsonl,join,receipts,errors}.py`
- `tests/runtime/llm_batch/test_{join_custom_id,anti_batch_completion,adapter_scaffold}.py`
- `_bmad-output/implementation-artifacts/batch-llm-b1-runtime-adapter.md`
