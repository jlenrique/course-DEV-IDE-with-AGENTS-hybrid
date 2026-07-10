# Batch LLM Execution Mode — Story-ready split (2026-07-10)

**Status:** **v1 CLOSED 2026-07-10** (all stories done except A1-EXT TRAIL/deferred)  
**Epic SSOT:** `_bmad-output/planning-artifacts/epic-batch-llm-execution-mode-spec-2026-07-01.md`  
**Close letter:** `_bmad-output/implementation-artifacts/batch-llm-epic-v1-close-2026-07-10.md`  
**Party:** `_bmad-output/planning-artifacts/batch-llm-party-greenlight-2026-07-10.md` (4/4 GO-WITH-AMENDMENTS) + formal CLOSE 4/4  
**Research:** `_bmad-output/planning-artifacts/research/technical-litellm-batch-hookup-research-2026-07-10.md`  
**Branch:** `dev/batch-mode-2026-07-10`  
**Gate mode:** single-gate per story unless noted; B3 dual-attention on two-walks (Winston)

> Brownfield epic — not a greenfield PRD→Architecture CE chain. Stories below are the binding decomposition.

> **Prior PNG Batch good-reads (brief — mine):** `batch_6a457bcac6488190b79224e61ea89b26` (`gpt-4.1-mini`, leg3 c-u03 probe PNGs ×2, **2/2 usable JSON**). Provider multimodal Batch vision quality is **settled** as baseline. **Product dispatch = LiteLLM** — expect different client/receipt details than the scratch smoke; A1/A2/B2/T3 prove LiteLLM-mediated path + parity, not “can Batch read PNGs?” and not 1:1 smoke-script cloning.

---

## Sequencing (binding)

```text
A0 → A1-vision + A3-vision-first → B1 → B2 ∥ A2 → B3 → B4 → B5 → B6-land
                                                      └──────────→ B6-promote (only after B3+B4 done)
A1-EXT = TRAIL (deferred-inventory; not ready-for-dev in v1)
```

---

## Story A0 — LiteLLM dependency honesty

**Status:** done (2026-07-10) — story file `batch-llm-a0-litellm-dep.md`  
**Files:** `pyproject.toml`; `app/runtime/llm_batch/__init__.py`; `tests/runtime/llm_batch/test_litellm_dep_smoke.py`

**AC:**
1. `litellm>=1.90.2,<2` in project dependencies; lock/sync so fresh venv installs it.
2. Import smoke + `importlib.metadata.version("litellm")` starts with `1.90`.
3. Research path cited in module/story notes; naming trap documented (Batch ≠ `batch_completion`).
4. CLOSE may claim dep honesty only — not adapter hookup.

**DoD:** hermetic tests green; no live API.

---

## Story A1-vision — Vision LLM execution profile

**Status:** done (2026-07-10) — `batch-llm-a1-vision-profile.md`  
**Depends:** A0  
**Files:** `runtime/config/llm_execution.yaml`; `app/runtime/llm_execution_config.py`; `tests/runtime/llm_batch/test_llm_execution_profile.py`

**AC:**
1. `llm_execution.nodes.vision` profile: model, reasoning/verbosity as applicable, `max_completion_tokens`, `default_mode: realtime`, optional `batch` profile override.
2. Realtime cascade `vision → gpt-5.5` unchanged when batch profile unset/unused.
3. Batch profile **defaults to the same model as realtime (`gpt-5.5`)**, or nearest GPT-5-family member available on Batch if `gpt-5.5` is rejected — **not** `gpt-4.1-mini` (harness baseline id is evidence-only).

**DoD:** unit tests for load/defaults; T7 precursor (realtime path untouched).
**Dev note:** cite brief §Local Scratch Evidence + epic §Evidence already in hand. Operator 2026-07-10: batch model parity with realtime.

---

## Story A3-vision-first — Eligibility matrix (vision enforced)

**Status:** done (2026-07-10) — `batch-llm-a3-eligibility-vision-first.md`  
**Depends:** A1-vision (can parallelize authoring; merge after A1)  
**Files:** `runtime/config/llm_batch_eligibility.yaml`; `app/runtime/llm_batch_eligibility.py`; `tests/runtime/llm_batch/test_batch_eligibility_matrix.py`

**AC:**
1. Matrix lists known LLM sites with `batch_eligible` + rationale (a)–(e).
2. Vision = true; workbook/enrichment/prose/Gary/Enrique/etc. = false with rationale.
3. v1 router (when B6 lands) reads matrix and only routes vision.

**DoD:** schema/shape pin test; no live API.

---

## Story B1 — `app/runtime/llm_batch/` adapter scaffold

**Status:** backlog → next create-story / RED-first  
**Depends:** A0  
**Files:** `app/runtime/llm_batch/{__init__,adapter,jsonl,join,receipts}.py`  
**Tests:** `tests/runtime/llm_batch/test_join_custom_id.py`, `test_anti_batch_completion.py`, size-budget unit

**AC:**
1. Wrap LiteLLM `create_file`/`create_batch`/`retrieve_batch`/`file_content` (+ async twins as needed); `custom_llm_provider="openai"`; `endpoint="/v1/chat/completions"`.
2. Receipts under `runs/<uuid>/llm_batch/`.
3. Join by `custom_id`; out-of-order OK; failed row isolated.
4. Pre-upload JSONL size estimate + fail-loud oversize (tagged).
5. Hermetic guard: production adapter must not call `batch_completion`.
6. **Not** a raw OpenAI-only client; **not** edits to `app/models/adapter.py`.
7. **Dispatch delta:** do not copy scratchpad OpenAI client call shapes blindly — normalize LiteLLM return objects into our receipt/join types; pin that normalization in T0.

**DoD:** T0 (+ anti-batch_completion + size). CLOSE = scaffold only.
**Dev note:** brief PNG good-reads inform *what success looks like*; B1 owns *how* we dispatch via LiteLLM.

---

## Story B2 — Perception batch route

**Depends:** B1, A1-vision, A3-vision-first  
**Files:** vision batch entry (extend `vision/_act.py` or sibling `batch_route.py`); reuse `provider._parse_response`, `PERCEPTION_SYSTEM_MESSAGE`, `_perception_prompt`  
**Tests:** `test_jsonl_builder_prefix.py` (T1), `test_batch_row_to_vision_response.py` (T2), optional `test_litellm_batch_live.py` (T3 `@llm_live`)

**AC:**
1. One row/slide; `custom_id=<run_id>:<slide_id>`; multimodal chat completions body; `max_completion_tokens` set.
2. Stable prompt prefix before `image_url`; T1 prefix pin.
3. Parse via shared `_parse_response`; malformed row fail-loud per id.
4. Resume-from-receipt: never re-submit existing batch on poll/resume.
5. Realtime `perceive_png` unchanged when mode=realtime.

**DoD:** T1+T2 required. T3 optional for story CLOSE; required before production/default claims.
**Dev note:** T3 proves **LiteLLM-mediated** submit→join→parse + parity vs `perceive_png` on the **same frozen PNGs** as the brief smoke. Quality baseline: `batch_6a457bcac6488190b79224e61ea89b26`. Do **not** assume dispatch kwargs/receipt shapes match the raw-OpenAI scratch client.

---

## Story A2 — Perception eval harness

**Depends:** B1 (batch transport available); may trail B2  
**AC:** frozen slides = leg3 c-u03 probe PNGs (brief fixtures); compare realtime vs batch on **same model family** (`gpt-5.5` / nearest); LiteLLM-backed smoke rebuilt from brief harness; informs fallback only if Batch rejects `gpt-5.5`.

**DoD:** harness runnable offline for scoring scaffolding; live arms gated `--run-live`.
**Dev note:** prior raw-OpenAI Batch already yielded good reads (quality baseline). A2 rebuilds under **LiteLLM** — comparative quality/model selection + dispatch-through-façade, not provider feasibility, not smoke-script clone.

## Story B3 — `waiting_for_provider_batch` pause/resume

**Depends:** B2  
**Files:** `production_runner.py` (+ recover CLI as needed)  
**Gate:** dual-attention on two-walks (Winston)

**AC:**
1. Distinct status — not gate-pause / not error-pause stamp.
2. Idempotent poll/resume from receipt; cancel/expiry behavior; operator-visible.
3. Zero duplicate perception artifacts on double-resume (T5).
4. Two-walks side-effect ownership named and tested.

**DoD:** T5 + T6 as applicable. Blocks B6-promote.

---

## Story B4 — Cost + latency reporting

**Depends:** B1 (receipts); ideally after B2/B3 have real runs  
**AC:** self-aggregate usage from output files; three scenarios; realtime vs batch breakdown. No Enterprise-only LiteLLM cost dependency.

**DoD:** unit + fixture from sample output JSONL. Blocks B6-promote.

---

## Story B5 — Prompt-cache optimization

**Depends:** B2  
**AC:** stable `prompt_cache_key`; measure cached_tokens; prefix-drift pin.

**DoD:** hermetic prefix pin; live cache measurement optional/fenced.

---

## Story B6-land — SPOC `execution_mode` switch (opt-in)

**Depends:** B1, B2, A3  
**AC-land:** Marcus-SPOC/trial-start exposes `realtime|batch`; routes vision only; pause wording; non-eligible stay realtime.

**DoD:** CLI/config tests; T7 realtime regression. **Does not** set batch as default.

---

## Story B6-promote — Promote batch to normal production (gated)

**Depends:** B3 `done`, B4 `done`, B6-land `done`  
**AC-promote:** only then may docs/defaults treat batch as a normal production option (still operator-chosen). Sprint-status must show B3+B4 done.

**DoD:** checklist gate in story; Murat re-check allowed.

---

## Deferred (not v1 ready-for-dev)

| ID | Disposition |
|---|---|
| A1-EXT all-node tiering | deferred-inventory trail |
| Workbook batch | N/A — no LLM |
| Multi-provider LiteLLM Batch | after openai-first green |
| `/v1/responses` Batch | wait for LiteLLM endpoint support |

---

## Test map (Murat fences)

| Test | Required for |
|---|---|
| T0, T1, T2, T6, T7 | hermetic CLOSE |
| T3, T4, T5 | liveproof / production claims |
| T4 | shape/contract parity **not** byte identity |
