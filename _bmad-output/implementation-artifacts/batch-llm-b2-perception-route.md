# Story: batch-llm-b2-perception-route — Vision Batch route (07G)

**Status:** done  
**Epic:** `epic-batch-llm-execution-mode`  
**Kanban key:** `batch-llm-b2-perception-route`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate:** single-gate  
**Depends:** B1 done; A1 + A3 done  
**Party:** Winston/Amelia/Murat **3/3 GO-WITH-AMENDMENTS** (2026-07-10) — MUST folded  
**Code-review:** PASS-WITH-FIXES → folded — `batch-llm-b2-code-review-2026-07-10.md`  
**John path:** OFF non-interference MUST-1; B2 before B6-land

## Story

As the Marcus-SPOC runtime, when a run opts into `llm_execution_mode=batch`, I need 07G vision perception to submit multimodal `/v1/chat/completions` Batch rows via LiteLLM, join by `custom_id`, and parse with the **same** `_parse_response` as realtime — and when mode is realtime/unset, the existing `act`/`perceive_png` path must run **unchanged**.

## Acceptance Criteria

1. **Mode source (Amelia MUST-1):** Payload key `llm_execution_mode` inside vision `_payload(state)` / `cache_prefix` JSON. Only exact `"batch"` enables ON. Unset / `"realtime"` / `""` / any other value → OFF. (B6 may later also set `RunState`; B2 does not require RunState field.)
2. **ON — whole-act single submit (Winston MUST-2):** When ON + A3 vision routable, `act` takes batch branch **once** for the full slide set: N JSONL rows → **one** LiteLLM Batch job → join → each row through `_parse_response`. Not N mini-batches.
3. **ON — JSONL:** `custom_id=<run_id>:<slide_id>`; system + text **before** `image_url`; model + `max_completion_tokens` from A1 batch profile (`gpt-5.5` / 8192).
4. **ON — parse:** `extract_assistant_text` → shared `provider._parse_response` (export or documented private import; no fork). Failed/malformed row fail-loud **with `custom_id` in the error message** (no realtime repair loop on batch).
5. **ON — resume-from-receipt (Winston MUST-1 / Murat T4a):** If `runs/<run_id>/llm_batch/receipt.json` exists with `batch_id`, **poll+join only** — never re-upload/re-create. Hermetic pin: second entry does not call create_file/create_batch. Corrupt receipt → `vision.batch.receipt-corrupt` (no re-submit). Stale `row_count` → `vision.batch.receipt-stale`.
6. **ON — poll API:** `poll_until_terminal(adapter, batch_id, *, run_id, row_count, model, sleep_fn, interval_s, timeout_s)` → updated receipt; terminal `completed|failed|expired|cancelled`; fail-loud if not `completed`. Injectable `sleep_fn` for T2. B3 owns pause class later.
7. **OFF — affirmative spy pin (John MUST-1 / Murat T1):** Modes `{missing, "realtime", "", "not-batch", "BATCH"}` → zero adapter submit/upload/create; zero JSONL build; zero `llm_batch/` write/dir; `perceive_png` path used. **Forbidden CLOSE evidence:** “existing vision suite green” alone.
8. **Eligibility fail-loud (Murat T3):** `mode=batch` + not routable → tagged `vision.batch.ineligible` before any Files API call; no silent realtime fallback.
9. **runs_root:** injectable default `Path("runs")` (or explicit kwarg into batch route); OFF tests assert no dir create.
10. Realtime `perceive_png` signature/behavior unchanged; existing vision act tests remain green as **regression** (not OFF proof).

**CLOSE claim:** hermetic ON route + OFF spy pin + T1/T2. **Non-claims:** SPOC switch (B6), pause class (B3), production readiness, live LiteLLM parity, byte-identical prose. T3 live optional for CLOSE.

## Party MUST folded (2026-07-10)

| Seat | Verdict | Folded |
| --- | --- | --- |
| Winston | GO-WITH-AMENDMENTS | whole-act single submit; resume-from-receipt |
| Amelia | GO-WITH-AMENDMENTS | payload mode source; poll API; message builder; body→text; runs_root; test paths; eligibility tag; `_parse_response` export |
| Murat | GO-WITH-AMENDMENTS | affirmative OFF spy; T1/T2 named; eligibility hermetic; resume fence; claim fence |

## Tasks

- [x] Party green-light + fold MUST
- [x] Mode resolver + OFF spy tests (RED then GREEN)
- [x] `build_perception_openai_messages` + T1 prefix pin
- [x] `batch_route.py` + poll_until_terminal + resume-from-receipt
- [x] Wire `_act.act` whole-act batch branch
- [x] T2 parse + fail-loud row; eligibility fail-loud
- [x] Regression: `tests/specialists/vision/test_vision_provider_and_act.py`
- [x] `bmad-code-review` → done (MUST folded; 65 hermetic passed)

## Dev Notes

- Files: `app/specialists/vision/batch_route.py`; tests under `tests/specialists/vision/test_jsonl_builder_prefix.py`, `test_batch_row_to_vision_response.py`, `test_batch_route_off_noninterference.py`
- Do not edit `app/models/adapter.py`
- Product batch model = `gpt-5.5` (A1)
