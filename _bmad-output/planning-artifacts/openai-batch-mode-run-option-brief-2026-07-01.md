# OpenAI Batch Mode Run Option - Handoff Brief

**Date:** 2026-07-01  
**Amended:** 2026-07-10 — LiteLLM hookup research folded (`technical-litellm-batch-hookup-research-2026-07-10.md`); operator pull-forward active.  
**Purpose:** Operator-selectable runtime modality for the Marcus-SPOC production app.  
**Boundary:** This is product work only if it improves the Marcus-SPOC runtime orchestrator. Concierge/proofing runs may inform defects and design constraints, but must not become the product target.

> **⛔ CORRECTION (operator-confirmed 2026-07-01; binding — body below retained verbatim for audit):** the "Anthropic candidate… Fable 5" mentions in this brief (perception-candidate list, eval-harness comparison) are **SUPERSEDED**. Fable 5 (`claude-fable-5`) is the **IDE/AGENT model** — it powers Claude Code + spawned agents and is **never invoked by production runs**. The pipeline standard stays **OpenAI GPT-5 family**; batch mode = provider Batch via **LiteLLM** + smaller OpenAI models (gpt-5-mini/nano) per node where harness-proven. Canonical framing: `epic-batch-llm-execution-mode-spec-2026-07-01.md`.

> **⛔ CORRECTION (operator 2026-07-10; binding):** LiteLLM is **already installed** on this machine (`.venv` **1.90.2**). Spec/build work is **hookup + declare in pyproject + test** — not a future install. Product Batch path = LiteLLM Files + Batches SDK (`create_file` / `create_batch` / retrieve / file content), `custom_llm_provider="openai"` first. Do **not** use `litellm.batch_completion` as the cost-savings path (parallel sync ≠ Batch API).

> **⛔ CORRECTION (research 2026-07-10):** Batch perception rows use multimodal **`/v1/chat/completions`** (LiteLLM `create_batch` endpoint Literal). Earlier `/v1/responses` Batch wording in this brief is **superseded for v1**. Workbook generation is **not** batch-eligible today (deterministic; no OpenAI).
>
> **⛔ CORRECTION (operator 2026-07-10; binding):** product **batch model = realtime model** — `gpt-5.5` (or nearest GPT-5-family member available on Batch). The scratch `gpt-4.1-mini` vision batch is a **quality baseline only**, not the product default.

## Executive Summary

Add a first-class run-start `execution_mode` switch that routes selected LLM-backed nodes:

- `realtime`: current synchronous behavior.
- `batch`: submit the same node request body to a provider batch endpoint, wait/poll/resume, then feed the returned artifacts into the same downstream contract.

The first candidate node behind the switch is slide perception / image analysis. It is naturally batchable because each slide can be analyzed independently, joined by `custom_id` / `slide_id`, and consumed later by Irene/Quinn-R/07G without changing downstream data shape.

The intended invariant: **the run-start switch changes transport and timing only for specific eligible request sites; node inputs and outputs remain contract-equivalent to realtime.**

## Why This Matters

Potential benefits:

- Lower cost for eligible OpenAI Batch calls.
- Additional input-token savings when prompt caching hits.
- Higher practical throughput for per-slide perception: one request per slide, parallelized by provider infrastructure.
- Better model choice flexibility: use slower/higher-quality GPT-5-family models where wall-clock delay is acceptable.

Main tradeoff:

- Batch is asynchronous. OpenAI Batch has a 24h completion window; our observed GPT-5-family jobs ranged from about 1 minute to about 41 minutes, while some mini/nano jobs remained in progress longer. A batch-mode production run must be allowed to pause and resume.

## Official References

- OpenAI Batch guide: https://developers.openai.com/api/docs/guides/batch
- OpenAI Batch cookbook example: https://developers.openai.com/cookbook/examples/batch_processing
- OpenAI prompt caching guide: https://developers.openai.com/api/docs/guides/prompt-caching
- OpenAI Prompt Caching 201 cookbook: https://developers.openai.com/cookbook/examples/prompt_caching_201

## Local Scratch Evidence

> **BINDING FINDING (operator-confirmed; mine this — do not rediscover):** OpenAI Batch API calls against multimodal endpoints have **already succeeded** at producing **good PNG slide reads** — completed vision batches returned **usable JSON perception artifacts** on real Gamma-export PNGs from the leg3 c-u03 probe deck. Provider-side feasibility of “Batch can read PNGs well enough for perception” is **settled** as a quality baseline.
>
> **Dispatch delta (operator 2026-07-10; binding):** production dispatch is via **LiteLLM** Files + Batches SDK (`create_file` / `create_batch` / retrieve / `file_content`, `custom_llm_provider="openai"`), not a copy of this scratchpad’s raw OpenAI client. Expect **different dispatch details** (wrapper kwargs, receipt/response shapes, errors). Remaining work = LiteLLM hookup + prove dispatch through that façade + pause/resume + SPOC switch + contract parity vs realtime `perceive_png` — not a first proof that Batch vision works, and not an assumption that LiteLLM plumbing matches the smoke script 1:1.

Scratch sidecar:

`scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py`

Useful commands already working:

```powershell
# Heartbeat
python scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py heartbeat-submit `
  --model gpt-5-nano `
  --max-output-tokens 1000 `
  --reasoning-effort low `
  --text-verbosity low

# Two-slide vision batch
python scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py vision-submit `
  --model gpt-4.1-mini `
  --image scratchpad/leg3-c-u03-persubslide-bundle/gamma-export/c-u03-persubslide-probe_slide_01.png `
  --image scratchpad/leg3-c-u03-persubslide-bundle/gamma-export/c-u03-persubslide-probe_slide_02.png

# Batch prompt-cache probe
python scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py cache-submit `
  --model gpt-5-nano `
  --max-output-tokens 1000 `
  --count 2 `
  --repeat 80 `
  --prefix-kind shared `
  --prompt-cache-key openai-shared-cache-probe-gpt5nano-20260701 `
  --prompt-cache-retention 24h `
  --reasoning-effort low `
  --text-verbosity low

# Poll and fetch results
python scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py poll --batch-id <batch_id> --once
python scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py results --batch-id <batch_id>

# Realtime cache probe for comparison
python scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py realtime-cache-probe `
  --model gpt-5-mini `
  --max-output-tokens 1000 `
  --count 3 `
  --repeat 80 `
  --prompt-cache-key openai-realtime-cache-probe-gpt5mini-20260701 `
  --prompt-cache-retention 24h `
  --reasoning-effort low `
  --text-verbosity low
```

Representative results:

- **`batch_6a457bcac6488190b79224e61ea89b26` (PRIMARY PNG-READ PROOF):** `gpt-4.1-mini`, two-slide vision batch on `c-u03-persubslide-probe_slide_01.png` + `_02.png`, completed 2/2, **usable JSON perception artifacts / good reads**.
- `batch_6a457ea8e08481909cc6457a9f25442a`: `gpt-5-nano`, heartbeat, completed 1/1 with visible JSON.
- `batch_6a45781aa2bc8190b62bc3ec389e0c41`: `gpt-5`, heartbeat, completed 1/1 with visible JSON, about 41 minute turnaround.
- `batch_6a4581c643a48190b933482132430efe`: `gpt-5-nano`, shared-prefix cache probe, completed 2/2, one row reported `5248` cached input tokens.
- Several `gpt-5-mini` / `gpt-5-nano` jobs remained in progress longer. Treat observed turnaround as variable, not guaranteed.

Prompt caching was proven in realtime for GPT-5-family models:

- `gpt-5`: second realtime request cached `5376 / 5392` input tokens.
- `gpt-5-mini`: subsequent realtime requests cached `5248 / 5392` input tokens.
- `gpt-5-nano`: subsequent realtime requests cached `5248 / 5392` input tokens.

Batch prompt caching was also observed, but not guaranteed per row:

- In `batch_6a4581c643a48190b933482132430efe`, row 1 cached `5248 / 5312` input tokens; row 2 cached `0 / 5312`.

## Proposed Product Shape

At the beginning of a production run, Marcus-SPOC exposes a deliberate operator choice:

```text
LLM execution mode for eligible nodes:
[ realtime ] Complete interactively using synchronous calls.
[ batch    ] Submit eligible requests as provider batches, pause/resume as needed.
```

This is not an optional implementation idea. It is the product surface being specified: a run-level mode choice. The implementation may still route only eligible nodes through batch internally.

Add a run-level or node-level option:

```yaml
llm_execution:
  default_mode: realtime
  nodes:
    perception:
      mode: batch
      provider: openai
      model: gpt-5-mini
      reasoning_effort: medium
      text_verbosity: low
      max_output_tokens: <calibrated>
      prompt_cache_key_strategy: stable_perception_v1
      prompt_cache_retention: 24h
```

Recommended default for slide perception/image analysis:

- `reasoning_effort: medium`
- `text_verbosity: low`
- model candidates: compare `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, plus existing realtime/default model.

Rationale:

- Medium reasoning gives enough visual/layout interpretation room.
- Low verbosity keeps JSON compact and schema-following.
- High output cap avoids the hidden-reasoning starvation observed in tiny GPT-5 heartbeats.

## Architecture Requirements

1. Preserve node contract.
   - Realtime and batch must accept the same logical perception inputs and produce the same logical perception artifacts.
   - Downstream nodes should not know or care which transport produced the artifact.

2. Treat batch as an execution adapter.
   - Submit JSONL rows.
   - Persist batch receipt and input manifest.
   - Poll or resume later.
   - Download output/error files.
   - Join rows by stable `custom_id`.
   - Validate each row against the same schema used by realtime.

3. Add run pause/resume semantics.
   - A production run in batch mode should enter a clear "waiting for provider batch" state.
   - Resume should be idempotent: polling completed batches repeatedly must not duplicate artifacts or alter downstream state.

4. Persist enough audit state.
   - provider, endpoint, model, batch id, input file id, output file id, request counts, submitted_at, completed_at, token usage, cached tokens, per-row status, per-row errors.

5. Cost reporting.
   - Final report should break down realtime/batch calls, input tokens, cached input tokens, output tokens, reasoning tokens, failed rows, retries, and estimated cost.
   - Model cost should support three scenarios:
     - conservative: no cache hits
     - observed: actual cached-token accounting
     - projected: recent average cache hit ratio by node/model/profile

## Candidate Node: Slide Perception

Batch unit:

- one row per slide image
- `custom_id = <run_id>:<slide_id>` or similar
- request body uses **`/v1/chat/completions`** (LiteLLM Batch endpoint; multimodal `image_url` data-URI — mirrors `perceive_png`)
- prompt contains stable schema/instructions first, variable slide image/content last

> **Superseded (2026-07-10):** earlier draft said `/v1/responses`. LiteLLM `create_batch` does not accept that endpoint Literal today.

Expected output:

- same `VisionProviderResponse` / `PerceptionArtifact` / slide-read shape as realtime
- strict JSON parse
- schema validation before downstream consumption
- failures isolated per slide, then either fail-loud or retry according to existing gate policy

**Non-candidates (2026-07-10):** `workbook_producer`, workbook enrichment, Mine-6 prose uplift — no LLM. Irene Pass-1/2 main, G0 extraction, CD, pre-gate Marcus — weak/no (monolithic and/or HIL-adjacent).

Prompt caching design:

- Put stable perception instructions, JSON schema, rubric, and shared run context before dynamic slide-specific payload.
- Put image and slide-specific details last.
- Use a stable `prompt_cache_key` per node/profile/prompt version, not per slide.
- Track `usage.input_tokens_details.cached_tokens`.

## Model Comparison Plan

Before choosing a production default, run the same frozen slide set through:

- current app/default realtime model
- OpenAI `gpt-5`
- OpenAI `gpt-5-mini`
- OpenAI `gpt-5-nano`
- Anthropic candidate when available, e.g. Fable 5, plus Opus/Sonnet baseline if useful

Compare:

- schema validity
- OCR/extracted text fidelity
- visual-element coverage
- layout/reading-path quality
- figure/numeric fidelity
- downstream Irene Pass-2 usefulness
- 07G pass/fail behavior
- cost and turnaround

Likely hypothesis:

- `gpt-5-mini` may be the best value default if quality is close enough.
- full `gpt-5` may be reserved for high-stakes or ambiguous perception.
- `gpt-5-nano` may be useful for cheap heartbeat/routing or simple OCR/layout tasks, but needs quality proof.

## Turnaround Expectations

OpenAI Batch has a 24h completion window. Design the app as if a batch-mode run may pause for hours.

Observed today:

- some `gpt-4.1-mini` jobs completed quickly
- `gpt-5-nano` heartbeat/cache jobs completed quickly in some cases
- full `gpt-5` heartbeat completed in about 41 minutes
- some `gpt-5-mini` and `gpt-5-nano` jobs remained in progress longer
- Anthropic batches were remarkably quick in our smoke tests, but do not assume OpenAI will match that consistently

Operator-facing wording should be explicit:

> Batch mode may reduce cost and improve throughput, but can pause the production run while provider processing completes. Choose realtime when interactive turnaround matters; choose batch when quality/cost are more important than immediate completion.

## Cautions

- The operator switch is run-level, but implementation should still route only eligible request sites through batch. Non-eligible nodes remain realtime or use their own node profile.
- Do not change downstream contracts. Batch is transport, not semantics.
- Do not let hidden reasoning consume all output budget. Calibrate `max_output_tokens`.
- Do not rely on prompt cache hits per row. Measure actual `cached_tokens`.
- Do not assume Batch result order. Join by `custom_id`.
- Do not assume all rows succeed. Parse and validate per row.
- Do not mark a run failed just because batch turnaround is slow unless it expires/fails or exceeds an operator policy.
- Keep provider-specific mechanics behind an adapter. LangGraph should be able to let each agent/node choose its own LLM resource/profile.

## Suggested BMAD Work Structure

This deserves a formal epic (party green-light → create-epics-and-stories). Research already filed:

`_bmad-output/planning-artifacts/research/technical-litellm-batch-hookup-research-2026-07-10.md`

Suggested epic stories (see amended epic for A0–B6 detail):

1. **A0 LiteLLM dep + naming-trap docs**
2. **A1/A3 registry + eligibility matrix** (vision first; workbook out)
3. **B1 LiteLLM Batch adapter scaffold** (Files + Batches SDK; not raw OpenAI-only; not `batch_completion`)
4. **B2 Perception batch route** (`/v1/chat/completions` multimodal)
5. **B3 Pause/resume**
6. **A2 Quality harness** (LiteLLM-backed; rebuild missing smoke)
7. **B4/B5 Cost + cache**
8. **B6 Run-start switch** (gated on B3+B4)

## Current Recommendation

Proceed with party green-light on the **amended** epic. First eligible node = **07G slide perception** via **LiteLLM Batch** already installed on this machine. Hook up, declare dependency, test (T0–T7). Do not promote the switch until pause/resume + cost accounting land. Workbook customization is next **after** Batch — not a batch transport target.
