# OpenAI Batch Mode Run Option - Handoff Brief

**Date:** 2026-07-01  
**Purpose:** Operator-selectable runtime modality for the Marcus-SPOC production app.  
**Boundary:** This is product work only if it improves the Marcus-SPOC runtime orchestrator. Concierge/proofing runs may inform defects and design constraints, but must not become the product target.

> **⛔ CORRECTION (operator-confirmed 2026-07-01; binding — body below retained verbatim for audit):** the "Anthropic candidate… Fable 5" mentions in this brief (perception-candidate list, eval-harness comparison) are **SUPERSEDED**. Fable 5 (`claude-fable-5`) is the **IDE/AGENT model** — it powers Claude Code + spawned agents and is **never invoked by production runs**. The pipeline standard stays **OpenAI GPT-5**; batch mode = OpenAI GPT-5 batch + smaller OpenAI models (gpt-5-mini/nano) per node. Canonical framing: `epic-batch-llm-execution-mode-spec-2026-07-01.md` §Model policy.

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

- `batch_6a457bcac6488190b79224e61ea89b26`: `gpt-4.1-mini`, two-slide vision batch, completed 2/2, usable JSON perception artifacts.
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
- request body uses `/v1/responses`
- prompt contains stable schema/instructions first, variable slide image/content last

Expected output:

- same `PerceptionArtifact` / slide-read shape as realtime
- strict JSON parse
- schema validation before downstream consumption
- failures isolated per slide, then either fail-loud or retry according to existing gate policy

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

This likely deserves a small epic or sprint if productionized, because it touches runtime orchestration, provider adapters, cost reporting, and node contracts.

Suggested epic:

**Epic: Run-Start Batch LLM Execution Mode**

Candidate stories:

1. **Batch execution adapter scaffold**
   - OpenAI Batch client wrapper.
   - JSONL builder, submit, poll, cancel, result download.
   - Persistent receipts and row-level parsing.

2. **Perception node batch route**
   - One request per slide.
   - Same output contract as realtime perception.
   - Join by `slide_id`.
   - Fail-loud schema validation.

3. **Run pause/resume for batch wait**
   - Batch-submitted state.
   - Idempotent poll/resume.
   - Operator-visible status and timeout/expiry behavior.

4. **Model/profile registry**
   - Node-level provider/model/reasoning/verbosity/max-output profile.
   - Start with `perception: gpt-5-mini, medium reasoning, low verbosity`.
   - Allow A/B quality comparison across standard/mini/nano.

5. **Cost and latency reporting**
   - Final report records batch ids, turnaround, tokens, cached tokens, reasoning tokens, estimated cost.
   - Compare realtime vs batch.

6. **Quality evaluation harness**
   - Frozen slide set.
   - Compare current/default, `gpt-5`, `gpt-5-mini`, `gpt-5-nano`, and Anthropic candidates.
   - Score perception quality and downstream script usefulness.

7. **Prompt caching optimization**
   - Stable-prefix prompt layout.
   - `prompt_cache_key` strategy.
   - Cache-hit metrics.
   - Regression pin for stable prompt prefix.

## Acceptance Criteria

- A batch-mode perception run produces schema-valid perception artifacts equivalent in shape to realtime.
- Batch output is joined by `custom_id` and is robust to out-of-order rows.
- Failed rows are visible and actionable.
- Run can pause and resume without duplicate downstream execution.
- Final report includes batch ids, turnaround, token usage, cached-token usage, and cost estimate.
- Operator can choose realtime vs batch at run start; the app then routes eligible nodes according to the selected mode and node profiles.
- Quality comparison across at least full `gpt-5` and `gpt-5-mini` is completed before choosing a default.
- Prompt caching is measured, not assumed.

## Current Recommendation

Proceed as a first-class run-start mode switch, initially with slide perception as the eligible batched node.

Start with slide perception because it is the cleanest batch boundary. Use `gpt-5-mini` with `reasoning_effort=medium`, `text_verbosity=low`, and calibrated output budget as the first likely value profile, while comparing quality against full `gpt-5` and the current realtime/default model.

Do not promote the switch into normal production use until the run pause/resume story and final report cost accounting are in place.
