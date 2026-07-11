# Story B5 — Prompt-cache optimization

Status: done  
Date: 2026-07-10  
Epic: Batch LLM Execution Mode  
Depends: B2 (done)  
Party: GO-WITH-AMENDMENTS (2026-07-10) — MUST folded below  
Code-review: APPROVE (2026-07-10); SHOULD realtime-bind pin + strategy-match folded

## Goal

Stable `prompt_cache_key` for vision perception (strategy from `llm_execution.yaml`: `stable_perception_v1`); hermetic prefix-drift pin; optional/fenced live `cached_tokens` measurement. Batch = transport only — cache key is request metadata, not a second transport.

## Acceptance Criteria

1. Shared/contracted derivation so realtime and batch cache-key behavior cannot drift.
2. Derive stable cache key from `prompt_cache_key_strategy` (not per-slide).
3. Attach key on vision batch request bodies; wire same helper on realtime vision path (minimal).
4. Hermetic unit test: prefix-stable across slides; drifts when strategy/version changes.
5. Live cache measurement optional/fenced (absence must not fail CI/story green).
6. Vision request metadata only — no `batch_completion`; no adapter.py edits; no all-node expansion.

## Paths (pinned)

- Module: `app/runtime/llm_batch/prompt_cache.py`
- Tests: `tests/runtime/llm_batch/test_prompt_cache.py`

## DoD

Hermetic pin green; live optional. Story → done after code-review.

## Out of scope

Enterprise LiteLLM cost APIs; forcing cache hits in CI.
