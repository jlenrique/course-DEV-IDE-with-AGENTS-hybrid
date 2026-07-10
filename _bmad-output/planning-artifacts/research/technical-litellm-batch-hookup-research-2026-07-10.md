---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/openai-batch-mode-run-option-brief-2026-07-01.md
  - _bmad-output/planning-artifacts/epic-batch-llm-execution-mode-spec-2026-07-01.md
  - app/models/adapter.py
  - app/specialists/vision/provider.py
  - docs/STATE-OF-THE-APP.md
workflowType: research
lastStep: 4
research_type: technical
research_topic: LiteLLM Batch API hookup for Marcus-SPOC run-start realtime|batch mode
research_goals: >-
  Inventory already-installed LiteLLM on this machine; map batch APIs vs current
  ChatOpenAI vision path; define adapter seam, wiring steps, and test matrix;
  correct July-1 brief assumptions (/v1/responses vs chat/completions); feed
  amended epic before party green-light.
user_name: Juanl
date: 2026-07-10
web_research_enabled: true
source_verification: true
---

# Research Report: technical — LiteLLM Batch hookup (Marcus-SPOC)

**Date:** 2026-07-10  
**Author:** Juanl (facilitated)  
**Research Type:** technical  
**Status:** COMPLETE — ready to fold into epic/brief amendments

---

## Technical Research Scope Confirmation

**Research Topic:** LiteLLM Batch API hookup for Marcus-SPOC run-start `realtime|batch` mode  
**Research Goals:** Inventory installed LiteLLM; map APIs to vision/perception; define wire+test steps; amend epic so LiteLLM is the transport (already installed — hook up, do not re-install as “future”).

**Scope (operator-confirmed via “proceed” 2026-07-10):**

- Architecture / adapter seam vs `make_chat_model`
- Implementation approaches (SDK Batch vs `batch_completion` vs proxy)
- Technology stack (litellm 1.90.2 on this machine; OpenAI as first provider)
- Integration patterns (files → batches → poll → join by `custom_id`)
- Performance / cost (async 24h window; Batch pricing; multimodal JSONL size)

**Scope Confirmed:** 2026-07-10

---

## Research Overview

Marcus-SPOC today invokes LLMs through `app.models.adapter.make_chat_model` → LangChain `ChatOpenAI`. Slide perception (`app/specialists/vision/provider.py::perceive_png`) base64-encodes PNGs into `image_url` content blocks and invokes synchronously.

STATE-OF-THE-APP already names **Batch LLM Execution Mode via LiteLLM/OpenAI-compatible transport**. This machine already has **`litellm==1.90.2`** in `.venv`. The July-1 brief/epic still describe an “OpenAI Batch client wrapper” and `/v1/responses` rows — both need correction toward **LiteLLM SDK Batch + Files** with endpoint **`/v1/chat/completions`** (the only chat endpoint LiteLLM’s `create_batch` typing accepts today).

---

## 1. Machine / repo inventory (verified locally 2026-07-10)

| Fact | Evidence | Confidence |
|---|---|---|
| LiteLLM installed in project venv | `import litellm` → `.venv\Lib\site-packages\litellm\`; dist **1.90.2** | HIGH |
| Not declared in project deps | `pyproject.toml` has no `litellm` row (langchain-openai present) | HIGH |
| Production path still ChatOpenAI | `app/models/adapter.py` imports `langchain_openai.ChatOpenAI` only | HIGH |
| Vision is multimodal chat-style | `perceive_png` → `HumanMessage` with `image_url` data-URI + `chat.invoke` | HIGH |
| Cascade default for vision | `runtime/config/model_cascade.yaml` → `vision: gpt-5.5` | HIGH |
| True Batch API surface present | `litellm.create_batch` / `acreate_batch` / `retrieve_batch` / `aretrieve_batch` / `cancel_batch` / `acancel_batch` | HIGH |
| Files API surface present | `litellm.create_file` / `acreate_file` / `file_retrieve` / `file_content` / `afile_content` | HIGH |
| `create_batch` endpoint Literal | **Only** `'/v1/chat/completions' \| '/v1/embeddings' \| '/v1/completions'` — **not** `/v1/responses` | HIGH |
| Providers for Batch (SDK typing) | `custom_llm_provider`: openai, azure, vertex_ai, bedrock, hosted_vllm | HIGH |
| `batch_completion` ≠ Batch API | Parallel fan-out helper (sync workers); **not** the 50%-off async Batch product | HIGH |

**Implication:** v1 must **declare `litellm` in `pyproject.toml`**, add a **LiteLLM Batch adapter**, and route perception JSONL through **`/v1/chat/completions`** multimodal rows — not invent a separate OpenAI-only client, and not assume `/v1/responses` until LiteLLM’s Batch endpoint Literal expands.

---

## 2. External sources (verified)

| Claim | Source | Notes |
|---|---|---|
| LiteLLM documents Batches + Files (proxy + SDK) | https://docs.litellm.ai/docs/batches | Upload file `purpose=batch` → `create_batch` → retrieve → file content |
| SDK example uses `acreate_file` + `acreate_batch(endpoint="/v1/chat/completions")` | same | Matches local signature |
| Multimodal Batch via chat/completions + `image_url` base64 is the community-proven shape | OpenAI community thread on Batch multimodal | Aligns with our current `perceive_png` message shape |
| LiteLLM also has `/responses` for realtime | https://docs.litellm.ai/docs/response_api | Useful later; **not** in `create_batch` endpoint Literal today |
| Do not confuse Batch API with `batch_completion` | GitHub discussion #8958 + docs | Naming trap — epic must forbid using `batch_completion` as the cost-savings path |

---

## 3. Architecture recommendation (adapter seam)

### Binding invariant (unchanged)
**Batch is TRANSPORT, not SEMANTICS.** Downstream still consumes `VisionProviderResponse` / `PerceptionArtifact` shapes. Nodes do not learn which transport produced the artifact.

### Recommended layout

```text
                    ┌─────────────────────────────┐
  cascade resolve → │ app.models.adapter          │  REALTIME (keep)
                    │  make_chat_model → ChatOpenAI│
                    └─────────────────────────────┘
                                      ▲
  vision.perceive_png (realtime) ─────┘

                    ┌─────────────────────────────┐
  cascade resolve → │ app.runtime.llm_batch       │  BATCH (NEW)
                    │  LiteLLM files+batches SDK  │
                    │  custom_llm_provider=openai │
                    │  endpoint=/v1/chat/completions
                    └─────────────────────────────┘
                                      ▲
  vision batch route (eligible) ──────┘  join by custom_id=run:slide
                                      │
                    production_runner pause/resume (waiting_for_batch)
```

**Do not** replace `make_chat_model` wholesale in Tranche B v1. Add a **sibling batch adapter** used only by eligible fan-out sites when `execution_mode=batch`. Realtime path stays byte-stable.

**Optional later:** LiteLLM `completion()` as an alternate realtime backend (multi-provider). Out of scope for first Batch ship — hookup target is **Batch + Files**, not rewriting every specialist invoke.

### Perception JSONL row shape (v1)

```json
{
  "custom_id": "<run_id>:<slide_id>",
  "method": "POST",
  "url": "/v1/chat/completions",
  "body": {
    "model": "gpt-5.5",
    "messages": [
      {"role": "system", "content": "<PERCEPTION_SYSTEM_MESSAGE>"},
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "<perception prompt>"},
          {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
        ]
      }
    ],
    "temperature": 0,
    "max_completion_tokens": "<calibrated>"
  }
}
```

Parse each output row → existing `_parse_response` / `VisionProviderResponse` validation. Fail-loud per row; join by `custom_id` (never order).

### July-1 correction
Brief/epic references to Batch via **`/v1/responses`** are **superseded for LiteLLM SDK v1**. Use **`/v1/chat/completions`**. Revisit `/v1/responses` batch only if LiteLLM expands `create_batch` endpoint support and we prove parity.

---

## 4. Wiring steps (implementation sequence)

### W0 — Dependency honesty
1. Add `litellm` to `pyproject.toml` with a pin compatible with installed **1.90.2** (e.g. `litellm>=1.90,<2` or exact pin after party).
2. Lock/sync so clones get the package (not venv-only tribal knowledge).
3. Smoke: `python -c "import litellm; from importlib.metadata import version; print(version('litellm'))"`.

### W1 — `app/runtime/llm_batch/` (or `app/models/batch_adapter.py`) scaffold
1. Thin wrappers: `upload_batch_jsonl`, `create_batch`, `retrieve_batch`, `download_output_jsonl`, `cancel_batch`.
2. Persist receipts under `runs/<uuid>/llm_batch/` (batch_id, input_file_id, output_file_id, submitted_at, status, model, endpoint, row counts).
3. `custom_llm_provider="openai"` default; model id from cascade/registry.
4. **Forbidden:** calling `litellm.batch_completion` for the cost-savings product path (document in module docstring).

### W2 — Perception batch route
1. Build JSONL from slide PNG set (same prompts as `perceive_png`).
2. Submit → enter runner state `waiting_for_provider_batch`.
3. Poll/resume idempotent; map rows → `VisionProviderResponse`; write same artifacts realtime would.
4. Preserve `model_resolution_trail` / economics digest fields (batch ids + token usage when present).

### W3 — Run-start switch + eligibility
1. Marcus-SPOC / trial-start: `execution_mode: realtime|batch`.
2. Registry marks `vision` (07G) `batch_eligible: true`; others false until A3 expands.
3. Do not promote switch to default production until pause/resume + cost report land.

### W4 — Multi-model (later, same adapter)
LiteLLM already routes providers; after OpenAI Batch is green, add per-node model profiles (A1/A1-EXT) without changing downstream contracts.

---

## 5. Test matrix

| ID | Layer | What | Pass bar |
|---|---|---|---|
| T0 | Hermetic | Import + wrapper unit tests with mocked LiteLLM file/batch responses | join by custom_id; out-of-order OK; failed row isolated |
| T1 | Hermetic | JSONL builder from fixture PNGs matches schema; stable prompt prefix first | byte-stable prefix pin |
| T2 | Hermetic | Parser: batch output row → `VisionProviderResponse` (reuse provider parse) | same validation errors as realtime |
| T3 | Live (`llm_live` / `--run-live`) | 2-slide OpenAI Batch via LiteLLM SDK (`gpt-5-mini` or cheaper) | status completed; 2/2 schema-valid |
| T4 | Live | Contract equivalence: same 2 PNGs realtime vs batch → shape parity (not byte-identical prose) | both validate; slide_ids match |
| T5 | Integration | Runner pause on submit + resume after completed batch; no duplicate vision artifacts | idempotent poll |
| T6 | Negative | Missing API key / expired batch / partial row failure | tagged fail-loud; no silent skip |
| T7 | Regression | Realtime vision path unchanged when `execution_mode=realtime` | existing vision tests green |

**Operator spend note:** T3/T4 are paid; gate with existing `--run-live` / `llm_live` deselection defaults.

---

## 5b. Prior live evidence (brief — mine; do not rediscover)

**OpenAI Batch multimodal PNG reads already succeeded** (brief §Local Scratch Evidence):

| Proof | Detail |
| --- | --- |
| Batch id | `batch_6a457bcac6488190b79224e61ea89b26` |
| Model | `gpt-4.1-mini` |
| Inputs | leg3 c-u03 Gamma-export PNGs slide_01 + slide_02 |
| Outcome | **2/2 completed; usable JSON perception / good reads** |
| Harness (may be absent on disk) | `scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py` `vision-submit` |

**Implication for T3/T4:** prior smoke = **provider quality baseline** (PNG → usable JSON; that run used `gpt-4.1-mini`). Product calls go through **LiteLLM**, so **dispatch details may differ**. **Product batch model = realtime `gpt-5.5`** (or nearest GPT-5-family Batch-available member) — operator 2026-07-10; do not ship `gpt-4.1-mini` as the product default. Live tests must prove **LiteLLM-mediated submit→poll→download→join→parse** + shape parity vs `perceive_png` on that model policy. Rebuild smoke under LiteLLM if scratchpad sidecar is missing — reuse the **same frozen PNGs**; treat the recorded batch id as quality narrative, not model lock.

---

## 6. Eligibility reminder (feeds epic A3)

| Site | Batch? | Why |
|---|---|---|
| **07G vision** | **STRONG — v1** | N independent multimodal calls; join `slide_id`; no mid-node HIL |
| Reading-path LLM (inside 07G) | STRONG secondary | Second fan-out after perception artifacts exist |
| Irene warm-callbacks | MAYBE later | Per-segment; after Pass-2 parse |
| Workbook producer / enrichment / Mine-6 prose | **NO** | No OpenAI today — deterministic |
| Irene Pass-1/2 main, G0 extraction, CD, pre-gate Marcus | WEAK/NO | Monolithic and/or HIL-adjacent |

---

## 7. Risks / open questions for party

1. **JSONL size:** base64 PNGs inflate batch files — may need size caps, compression policy, or file-id image references if OpenAI Batch supports them for our models (size policy in B1; T3 measures real payloads). **Multimodal Batch PNG feasibility is already proven** (see §5b) — size is an ops constraint, not a “does vision Batch work?” risk.
2. **GPT-5.5 Batch availability:** product default is **`gpt-5.5`** (same as realtime). If Batch rejects it, fall back within **GPT-5 family** only — do not silently default to `gpt-4.1-mini` (harness evidence only).
3. **Proxy vs SDK:** v1 = **SDK direct** (`custom_llm_provider=openai`). Proxy optional later for multi-account routing.
4. **Enterprise cost tracking:** LiteLLM docs mark some batch cost tracking Enterprise-only — our B4 report must read OpenAI usage from output files ourselves regardless.
5. **Missing smoke sidecar:** July-1 `scratchpad/.../openai_batch_smoke.py` may be absent on disk — rebuild under LiteLLM wrappers as the live harness (A2/T3), **reusing the same PNG fixtures + the recorded good-read batch id as the baseline narrative**. Do not treat absence of the script as absence of the finding.

---

## 8. Recommended BMAD next steps

1. Fold this research into `epic-batch-llm-execution-mode-spec-2026-07-01.md` + brief (amendments below).
2. `[PM]` `bmad-party-mode` green-light on amended epic (LiteLLM hookup + perception-first + workbook out).
3. `[CE]` `bmad-create-epics-and-stories` — ensure stories include **W0 dep pin**, **W1 LiteLLM adapter**, **T0–T7 test matrix**, then perception route + pause/resume + switch.

---

## References

- LiteLLM Batches docs: https://docs.litellm.ai/docs/batches  
- LiteLLM Responses API (realtime; not Batch endpoint today): https://docs.litellm.ai/docs/response_api  
- Local: `litellm` 1.90.2; `app/models/adapter.py`; `app/specialists/vision/provider.py`  
- Prior product framing: `docs/STATE-OF-THE-APP.md` (Batch via LiteLLM/OpenAI-compatible transport)  
- Starter artifacts: `openai-batch-mode-run-option-brief-2026-07-01.md`, `epic-batch-llm-execution-mode-spec-2026-07-01.md`  
- Prior PNG Batch good-read: `batch_6a457bcac6488190b79224e61ea89b26` (`gpt-4.1-mini`, 2/2 usable JSON) — brief §Local Scratch Evidence
