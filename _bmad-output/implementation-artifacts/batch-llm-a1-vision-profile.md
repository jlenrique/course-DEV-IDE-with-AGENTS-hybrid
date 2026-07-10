# Story: batch-llm-a1-vision-profile — Vision LLM execution profile

**Status:** done  
**Epic:** `epic-batch-llm-execution-mode`  
**Kanban key:** `batch-llm-a1-vision-profile`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate:** single-gate  
**Depends:** A0 done  
**SSOT:** `batch-llm-execution-mode-stories-2026-07-10.md` §A1

## Story

As the Marcus-SPOC runtime, I need a vision-first `llm_execution` profile so batch mode can use the **same model as realtime** (`gpt-5.5`, or nearest GPT-5-family Batch-available member) without changing the economics cascade file.

## Acceptance Criteria

1. `runtime/config/llm_execution.yaml` defines `nodes.vision` with realtime + batch profiles (`provider`, `model`, `max_completion_tokens`, optional reasoning/verbosity/cache fields).
2. Realtime cascade `vision → gpt-5.5` unchanged (`model_cascade.yaml` / `load_cascade`).
3. Batch profile model **`gpt-5.5`** (matches realtime); `batch_model_fallback_family: gpt-5`; harness baseline id retained as evidence-only.
4. Loader `app/runtime/llm_execution_config.py` validates and resolves realtime vs batch profiles.
5. CLOSE = profile registry only — not Batch adapter, not perception route.

## Dev Agent Record

### Completion Notes

- Config adjacent to cascade under `runtime/config/`.
- Operator correction 2026-07-10: batch model = realtime (`gpt-5.5`), not harness `gpt-4.1-mini`.
- Hermetic tests: load defaults, resolve modes, cascade untouched, reject missing vision/batch.
- Dispatch delta noted in YAML comments (LiteLLM product path ≠ scratch smoke client).

### File List

- `runtime/config/llm_execution.yaml`
- `app/runtime/llm_execution_config.py`
- `tests/runtime/llm_batch/test_llm_execution_profile.py`
- `_bmad-output/implementation-artifacts/batch-llm-a1-vision-profile.md`
