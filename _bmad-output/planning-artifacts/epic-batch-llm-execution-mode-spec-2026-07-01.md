# EPIC SPEC — Run-Start Batch LLM Execution Mode + Node-Level Model/Profile Registry

**Status:** **v1 CLOSED 2026-07-10** (party CLOSE 4/4; close letter `batch-llm-epic-v1-close-2026-07-10.md`). A1-EXT remains TRAIL/deferred. **Authored:** 2026-07-01 from `openai-batch-mode-run-option-brief-2026-07-01.md`. **Amended:** 2026-07-10 research + party green-light. **Governance:** party record `_bmad-output/planning-artifacts/batch-llm-party-greenlight-2026-07-10.md`. **Boundary (binding):** product work ONLY if it improves the Marcus-SPOC runtime orchestrator; proofing runs inform defects/constraints, never the target [[feedback_spoc_is_goal_not_concierge_proofing_runs]].

**⛔ Model policy (operator-confirmed 2026-07-01; transport amended 2026-07-10):** production models stay in the **OpenAI GPT-5 family** for v1 (cascade today: vision → `gpt-5.5`). Batch mode uses **LiteLLM’s Batch + Files SDK** (`custom_llm_provider="openai"` first) so the same adapter can later route other providers’ batch APIs without rewriting nodes. **Fable 5 (`claude-fable-5`) is the IDE/AGENT model only — NEVER a production/pipeline model.**

**⛔ Transport policy (operator-corrected 2026-07-10):** LiteLLM is **already installed** on the operator machine (verified `.venv` dist **1.90.2**). This epic **hooks it up** (declare in `pyproject.toml`, adapter, tests) — it does **not** treat LiteLLM as a future install. Do **not** build a parallel raw-OpenAI-only Batch client as the product path.

**⛔ Endpoint correction (2026-07-10 research):** LiteLLM `create_batch` accepts endpoint Literal **`/v1/chat/completions` | `/v1/embeddings` | `/v1/completions` only** — **not** `/v1/responses`. Perception batch rows MUST use multimodal **`/v1/chat/completions`** (matches current `perceive_png` `image_url` shape). July-1 `/v1/responses` Batch wording is **superseded** for v1.

## The one binding invariant (what makes this surgical)
**Batch is TRANSPORT, not SEMANTICS.** A run-start `execution_mode` switch (`realtime | batch`) changes transport + timing for *eligible request sites only*; node inputs and outputs stay **contract-equivalent** to realtime. Downstream nodes must not know or care which transport produced an artifact — same schema, same validation. This clean adapter seam (zero downstream contract change) is precisely why the lift is "not especially heavy but must be surgical."

## The planning insight — TWO tranches by dependency + timing
The brief bundles 7 stories. They split cleanly into a **foundational tranche (node model/profile registry + eval harness)** and the **async batch machinery** — both deferred to the clean runtime boundary, Tranche A landing first as Tranche B's prerequisite. This split is the whole "optimal juncture" answer. *(The earlier "Fable-coupled, pull forward" framing of Tranche A is retracted per the 2026-07-01 operator correction — no pull-forward; Fable 5 is the agent model, not a pipeline model.)*

### TRANCHE A — Node-level model/profile registry + quality-eval harness + LiteLLM dependency honesty (FOUNDATIONAL)

Decoupled from pause/resume risk where possible. Foundational substrate before promoting the run-start switch.

- **A0 — LiteLLM dependency + hookup research closeout (NEW 2026-07-10).** Declare `litellm>=1.90.2,<2` in `pyproject.toml` (machine already has **1.90.2**). Document true Batch path; **forbid** `batch_completion` as cost path. AC: dep + import smoke; version assert starts with `1.90`; research cited; naming trap in adapter docstring. Hermetic CLOSE only — not “hookup done.”
- **A1 — Vision-first model/profile registry (party-narrowed 2026-07-10; model policy operator-corrected same day).** v1 ships `llm_execution.nodes.vision` (provider/model/reasoning/verbosity/max_completion_tokens, `default_mode: realtime`, optional **batch profile**). Realtime cascade default (`gpt-5.5`) stays byte-preserved. **Batch model MUST match realtime (`gpt-5.5`) or the nearest GPT-5-family member available on Batch** — do not default product batch to `gpt-4.1-mini` (that id remains harness baseline evidence only). **Full every-LLM-node registry is NOT a v1 bar.**
- **A2 — Perception quality-evaluation harness (v1 = 07G only).** Frozen slide set; compare realtime vs batch + gpt-5 family candidates for **perception only**. Rebuild LiteLLM-backed smoke. Do not expand into Irene/G0 platform eval in this epic’s ship claim.
- **A1-EXT — per-node model TIERING (all LLM nodes).** **TRAIL / follow-on** after first perception green. **MUST NOT gate B2–B6.** Filed in deferred-inventory; not in first-slice ready-for-dev set.
- **A3 — batch-eligibility matrix (vision-first for v1 ship).** Full matrix on disk with rationales; **v1 routing enforces vision (07G) only**. Workbook/enrichment/Mine-6 = NO. AC: vision justified on criteria (a)–(e); other nodes classified but not batch-routed in v1.

### TRANCHE B — LiteLLM Batch adapter + async run machinery (product path)

- **B1 — LiteLLM Batch adapter at `app/runtime/llm_batch/` (party-locked path).** Modules: `adapter.py`, `jsonl.py`, `join.py`, `receipts.py`. Sibling to `make_chat_model` — **`app/models/adapter.py` stays ChatOpenAI-only.** Files+Batches SDK; `endpoint="/v1/chat/completions"`; receipts under `runs/<uuid>/llm_batch/`; join by `custom_id`. **Hermetic anti-`batch_completion` import/use guard required** (docstring alone insufficient). Pre-upload JSONL size budget + fail-loud oversize. AC: submit→poll→download→join→validate under T0; size policy in AC.
- **B2 — Perception (07G) batch route.** JSONL mirrors `perceive_png` (system+text before `image_url`); **`max_completion_tokens` set explicitly**; parse via **`provider._parse_response`** (shared — no forked validator); malformed-row = fail-loud per `custom_id` (no silent skip; no fake in-batch multi-turn repair). Resume-from-receipt never re-submit. AC: schema-equivalent artifacts; T2 hermetic; optional T3 live evidence for production claims.
- **B3 — Distinct pause class `waiting_for_provider_batch`.** Not gate-pause stamp; not `paused-at-error` stamp. Reuse pause/recover *substrate*; own status + resume verb (poll/cancel/expire). Resume attaches to existing receipt/batch_id — **never re-upload on resume**. First-wins artifact write. Two-walks: side-effects on shared chokepoint or proven single-walk with parity test. AC: T5 zero duplicate artifacts on double-resume.
- **B4 — Cost + latency reporting.** Self-aggregate from output-file usage (not LiteLLM Enterprise-only). Three scenarios. AC: realtime vs batch breakdown.
- **B5 — Prompt-caching optimization.** Stable prefix pin; measure cached_tokens.
- **B6 — Run-start switch with split DoD.** **AC-land:** SPOC exposes `realtime|batch`; routes A3-eligible (vision) only; pause wording; depends on B1+B2+A3. **AC-promote:** blocked until B3+B4 `done` in sprint-status — promoting without them = governance fail.

## Party MUST amendments (folded 2026-07-10 — John/Winston/Amelia/Murat 4/4 GO-WITH-AMENDMENTS)

Binding authoring constraints for stories (do not relitigate transport/endpoint/LiteLLM):

1. A1-EXT + full-node A1 off critical path; vision-first ship.
2. Adapter path locked: `app/runtime/llm_batch/`.
3. Shared `_parse_response`; shape/contract parity ≠ byte identity (T4).
4. Distinct batch-wait pause; resume-from-receipt; JSONL size budget.
5. **Batch model = realtime model** (`gpt-5.5`) or nearest GPT-5-family Batch-available member — operator 2026-07-10 (supersedes earlier “may diverge to gpt-4.1-mini default” framing; harness `gpt-4.1-mini` smoke stays quality baseline only).
6. B6 land vs promote; hermetic vs liveproof claim fences (T0–T2/T6/T7 vs T3–T5).
7. Anti-`batch_completion` hermetic guard on product adapter.

**Claim envelope (v1 ship):** Marcus-SPOC opt-in batch for 07G; contract-equivalent perception; pause/resume without duplicate side effects; cost report; realtime unchanged; LiteLLM declared+wired. **Non-claims:** all-node tiering; workbook batch; multi-provider beyond openai first; `make_chat_model` replacement; production-default promote before B3+B4; byte-identical prose.

## ⭐ Optimal-juncture recommendation (amended 2026-07-10 — operator PULL-FORWARD)
- **2026-07-01 deferral (after Gamma arc) is SUPERSEDED** by operator pull-forward 2026-07-10 WRAPUP: next session = Batch mode switch (then workbook customization). Branch: `dev/batch-mode-2026-07-10`.
- **Internal sequencing:** **A0 (LiteLLM dep)** → A1/A3 (registry + eligibility) → **B1 (LiteLLM adapter)** → A2/B2 (harness + perception route) → B3 → B4/B5 → B6 (switch). A1-EXT may trail first perception green.
- Party GREEN-LIGHT on this amended spec before `bmad-create-epics-and-stories` / first story create.

## Dependencies / sequencing
`A0` → unlocks honest B1. `A1` + `A3` → prerequisite for B2/B6 routing. `B1` → prerequisite for B2/B3/B4. `A2` informs batch default model choice. `B6` gated on B3+B4. Workbook customization is a **separate** follow-on after Batch (not a batch-eligible node).

## Test matrix (binding — from 2026-07-10 research)
| ID | Layer | Pass bar |
|---|---|---|
| T0 | Hermetic mock LiteLLM | join by custom_id; out-of-order; failed row isolated |
| T1 | Hermetic JSONL builder | stable prompt prefix pin |
| T2 | Hermetic parse | batch row → `VisionProviderResponse` |
| T3 | Live `--run-live` | ≥2-slide LiteLLM→OpenAI Batch completes; schema-valid |
| T4 | Live parity | realtime vs batch shape parity on same PNGs |
| T5 | Integration | pause/resume idempotent; no duplicate artifacts |
| T6 | Negative | key missing / expiry / partial failure fail-loud |
| T7 | Regression | realtime path unchanged when mode=realtime |

## Guardrails / binding invariants
- **SPOC-is-the-goal** — every element earns its place by improving the SPOC runtime.
- **LiteLLM is the Batch transport** — already installed; declare + wire; no parallel raw-OpenAI Batch product path.
- **Transport-only / contract-equivalent** — downstream is transport-blind; same schema validation realtime vs batch.
- **Adapter isolation** — provider mechanics behind LiteLLM Batch adapter; realtime `make_chat_model` preserved in v1.
- **Naming trap** — never ship `batch_completion` as the cost-savings Batch mode.
- **Endpoint** — v1 perception Batch uses `/v1/chat/completions` multimodal rows (not `/v1/responses`).
- **Idempotent pause/resume** — no duplicate artifacts; two-walks side-effect discipline applies.
- **Calibrate `max_output_tokens` / `max_completion_tokens`** — avoid hidden-reasoning starvation.
- **Measure, don't assume** — `cached_tokens` measured; join by `custom_id`; validate per row; slow ≠ failed unless expiry/policy.
- **No-mocks live testing per component** for T3–T5; hermetic T0–T2 always.

## Evidence already in hand (from the brief) — BINDING

> **Operator note 2026-07-10:** OpenAI Batch endpoints have **already** been live-tested successfully for producing **good PNG slide reads** (usable JSON perception). Do **not** treat multimodal Batch vision as an open *provider* feasibility question in A1/A2/B2. Mine and reuse the brief’s scratch evidence as the **quality baseline**.
>
> **Dispatch delta (operator 2026-07-10; binding):** product calls are facilitated by **LiteLLM**, not the scratchpad’s raw OpenAI Batch client. Provider capability (PNG → good JSON) transfers; **dispatch details may differ** (LiteLLM `create_file` / `create_batch` / retrieve / `file_content` kwargs, `custom_llm_provider="openai"`, response/receipt field shapes, error wrapping, async twins). T3/T4 therefore prove the **LiteLLM-mediated dispatch path + contract parity** — they do not rediscover “can Batch read PNGs?”, and they must not assume byte-identical client plumbing to the July-1 smoke.

**PNG vision Batch — proven good reads (primary):**
| Field | Value |
| --- | --- |
| Batch id | `batch_6a457bcac6488190b79224e61ea89b26` |
| Model | `gpt-4.1-mini` |
| Result | completed **2/2**; **usable JSON perception artifacts** (good reads) |
| Fixtures | `scratchpad/leg3-c-u03-persubslide-bundle/gamma-export/c-u03-persubslide-probe_slide_01.png` + `_02.png` |
| Harness | `scratchpad/anthropic-batch-perception-smoke/openai_batch_smoke.py` → `vision-submit` |
| Brief SSOT | `openai-batch-mode-run-option-brief-2026-07-01.md` §Local Scratch Evidence |

**Supporting Batch smokes (same harness):**
- `batch_6a457ea8e08481909cc6457a9f25442a` — `gpt-5-nano` heartbeat, 1/1 visible JSON
- `batch_6a45781aa2bc8190b62bc3ec389e0c41` — `gpt-5` heartbeat, 1/1, ~41 min turnaround
- `batch_6a4581c643a48190b933482132430efe` — `gpt-5-nano` shared-prefix cache probe, 2/2; row1 `5248` cached / row2 `0` → measure, don’t assume

**Realtime prompt caching (same era):** gpt-5 / mini / nano ~5248–5376 / 5312–5392 cached on subsequent calls.

**Claim fence:** prior smoke proves **provider Batch + multimodal PNG → usable perception JSON** (quality baseline; that run used `gpt-4.1-mini`). It does **not** close LiteLLM product adapter (B1), LiteLLM-mediated dispatch parity (T3), runner pause (B3), or SPOC switch (B6). Product path wires **only** via LiteLLM Files+Batches (`endpoint="/v1/chat/completions"`, `custom_llm_provider="openai"` first). **Product batch model = realtime `gpt-5.5`** (or nearest GPT-5-family Batch-available member) — not the harness `gpt-4.1-mini` id.

## Placement in the development path (amended 2026-07-10)
1. **Operator pull-forward ACTIVE** — Batch is the live frontier on `dev/batch-mode-2026-07-10` (not waiting on Gamma-arc close).
2. **Research closed:** `_bmad-output/planning-artifacts/research/technical-litellm-batch-hookup-research-2026-07-10.md`.
3. **Next:** party GREEN-LIGHT → `bmad-create-epics-and-stories` → implement A0→B6 surgically (perception-first; workbook customization is a separate post-Batch track).

*(Fable 5 remains the IDE/agent model powering sessions that BUILD this epic — not a pipeline component.)*
