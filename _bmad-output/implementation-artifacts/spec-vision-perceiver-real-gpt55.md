# Spec — `vision-perceiver-real` (live gpt-5.5 vision perceiver)

**Status:** READY-FOR-DEV · **Class:** S · **Branch:** `fidelity-perception-arc-2026-06-19`
**Workflow:** party-mode green-light 5/5 GREEN-WITH-AMENDMENTS (no impasse) → `bmad-quick-dev` (dev agent) → `bmad-code-review` → done.
**Green-light record:** `proposal-vision-perceiver-real-gpt55-2026-06-21.md` + party round 2026-06-21 (Winston/John/Murat/Mary/Amelia).
**Tier:** R2 (~6 files, ~250-300 LOC incl. tests). Standalone substrate enabler that **PRECEDES** the P2-4b labeling kit (D7, unanimous).
**Operator directives (binding):** (1) no mocks/predicted/temporary — everything real, live API calls to intended models; (2) BMAD-sanctioned workflow + party + dev agent. **Model id: `gpt-5.5` (operator-confirmed; Tier-2 add ratified by the green-light round).**

## Problem

The "committed" vision specialist is a fixture/contract stub, not a live perceiver: `app/specialists/vision/provider.py::perceive_png` POSTs PNG bytes to a pinned `VISION_PROVIDER_ENDPOINT` (NOT configured in `.env`); default model `vision-fixture-v1`; only a hand-authored slide-01 golden fixture exists. This blocks P2-4b reading-path calibration over real slides and violates directive (1). Make perception a real, live `gpt-5.5` multimodal OpenAI call.

## Pre-code verifications (DONE at spec time — dev re-confirms A4)

- 6 PNGs at `runs/compositor/assembly-bundle/visuals/slide-0{1..6}.png` are genuine frozen-corpus frames (Jun-19 production render; slide-01 = the real `slide-1-the-economic-structural-reality` frame). ✓
- `gpt-5.5` absent from `app/models/registry.yaml`, `runtime/config/openai_pricing.yaml`, `runtime/config/model_cascade.yaml` → Tier-2 add required (ratified). ✓
- No test pins vision-output `cache_prefix` BYTES (vision tests `json.loads` then assert fields; cache-hit baseline keys on the selector hash over `{specialist_id,model_id,temperature,system_prompt_hash}`, not vision output). Dev RE-CONFIRMS before flipping done (A4). ✓ (provisional)

## Scope / files

1. **`app/specialists/vision/provider.py`** — `perceive_png(png_path, *, slide_id, model_id=..., ...)` **keeps its signature** but makes a real `gpt-5.5` multimodal call via the house pattern: `make_chat_model("vision")` (`app/models/adapter.py`) → `ChatOpenAI`; PNG → base64 `data:image/png;base64,...` `image_url` content block in a `HumanMessage` + a structured perception prompt demanding the `VisionProviderResponse` JSON. Use `chat.with_structured_output(VisionProviderResponse)` OR prompt-demand + parse. Retire the httpx pinned-endpoint path, `ENDPOINT_ENV`/`API_KEY_ENV`/`DEFAULT_MODEL_ID="vision-fixture-v1"`, and the `endpoint`/`api_key`/`client` kwargs.
2. **`app/specialists/vision/_act.py`** — update `_provider_model_id()` to read the real model id; keep the retry loop and taxonomy intact (A2/A3).
3. **`app/specialists/vision/model_config.yaml`** — retire the `provider:` fixture block; set `default_model: gpt-5.5` + `per_node_overrides.act: gpt-5.5`. Update in lockstep with `_provider_model_id()` (A3).
4. **`app/models/registry.yaml`** — add `gpt-5.5` entry, `available: true` (per D13 registry-bump policy — read the file header first).
5. **`runtime/config/openai_pricing.yaml`** — add `gpt-5.5` row: `input_per_1m_tokens_usd: 5.0`, `output_per_1m_tokens_usd: 30.0` (verified OpenAI pricing 2026-06-21). **`runtime/config/model_cascade.yaml`** — add `vision:` specialist entry (`model: gpt-5.5`) for economics labeling. These land TOGETHER; re-run `python -m app.runtime.cascade_config validate` (Winston #1).
6. **Tests** (see Test plan).

## Acceptance criteria

- **AC-1 (real call):** `perceive_png` makes a genuine `gpt-5.5` multimodal call over PNG bytes via the house `ChatOpenAI` adapter; the fixture/pinned-endpoint path is removed and unreachable from production. No `vision-fixture-v1` default remains.
- **AC-2 (model resolution):** `gpt-5.5` present in registry (`available:true`) + pricing ($5/$30) + cascade `vision` entry; `cascade_config validate` PASSES; `selector.resolve("vision")` returns `gpt-5.5` without `ModelResolutionError`.
- **AC-3 (error taxonomy preserved — Amelia A2):** the real call maps provider/SDK exceptions onto the EXISTING tagged errors so `_act.py::_is_retryable_provider_error` is untouched: timeout → `VisionProviderTimeout`; 429/5xx → `status_code`-bearing `VisionProviderError`; transport → `tag="vision.provider.transport"`. The non-retryable `vision.reading-path.unclassifiable` path is unchanged.
- **AC-4 (structured output — Winston #2/D4):** malformed-JSON handling retries through the existing taxonomy, bound ≤3; no new ad-hoc retry loop. JSON validated against `VisionProviderResponse`.
- **AC-5 (bbox provenance — Winston #4/D3):** the perception prompt instructs the model that bboxes are approximate normalized `[x1,y1,x2,y2]` region estimates (0..1), and the `PerceptionArtifact`/`VisionProviderResponse` docstring records provenance = LLM-estimated, coarse (classifier buckets into thirds).
- **AC-6 (cache-prefix — Winston #3 / Amelia A4 / Murat #5):** the diff enumerates every test touching vision `cache_prefix`; none pin exact bytes (re-scope to structural/field assertions if any do). Keep `temperature=0.0`. Confirm no `end_to_end` baseline pins vision-output bytes.
- **AC-7 (RED-first error-pause — Murat #6):** a deterministic test (recorded/crafted classification-failure response) proving an unclassifiable HIGH/perceived result PAUSES and does NOT retry — authored RED **before** the `_act.py` rewrite.
- **AC-8 (live non-vacuous — Murat #2/#3, Mary #6):** `@pytest.mark.llm_live` test perceives the 6 real PNGs; `pytest.skip` when `OPENAI_API_KEY` absent. Non-vacuous assertions on slide-01: perceived text contains anchors `$4.5T`, `74%`, `3x`; element-count band; every bbox in `[0,1]` with `x+w<=1`,`y+h<=1`; `confidence == "HIGH"`; `reading_path` ∈ the 7-pattern enum. Assert on bucket (or ±0.05 coord tolerance on ground-truthed anchors), NOT raw coords. Raw responses captured to disk on the live run (Mary #6).
- **AC-9 (recorded-real seam — Murat #1):** deterministic unit tests feed RECORDED-REAL gpt-5.5 responses (provenance metadata: capture date, model id, prompt hash, source PNG) through parse→validate→classify. Recordings live under a labeled path and are NEVER reachable as a production return path. Existing deterministic unit tests keep monkeypatching `perceive_png` (Amelia A4) — do NOT convert them to live.
- **AC-10 (clean):** ruff clean; `lint-imports` KEPT count unchanged; sandbox-AC PASS; full focused vision suite green.

## Test plan (RED-first per Murat)

1. RED: AC-7 unclassifiable→non-retryable error-pause test (before `_act.py` touch).
2. RED→GREEN: AC-9 recorded-real parse/validate/classify unit tests.
3. GREEN: AC-8 key-gated live roundtrip over the 6 PNGs (extend `tests/specialists/vision/test_vision_live_roundtrip.py`).
4. Rewrite the 1 httpx `MockTransport` test in `test_vision_provider_and_act.py` → stubbed-`chat.invoke` (Amelia: that test dies with the endpoint path).
5. Regression: vision suite + `cascade_config validate` + lint-imports + ruff + sandbox-AC.

## Out of scope (scope fence — John #3)

No labeling-kit affordances. No cascade gold-plating beyond the required rows. No non-OpenAI backend abstraction (Winston). The P2-4b labeling kit consumes this enabler's real output AFTER it lands.

## Post-close filings (Mary — binding, done at code-review/close)

- Anti-pattern in `docs/dev-guide/dev-agent-anti-patterns.md`: "Fixture-backed contract mistaken for live capability."
- Deferred-inventory `specialist-liveness-audit`: sweep all 14 specialists for the `-fixture-v*` / unconfigured-`_ENDPOINT` / golden-only signature (direction-may-flip caveat; reactivate before any trial claiming a specialist is live).
- `docs/trials/cross-trial-learnings.md`: bidirectional cross-tracker-drift entry.
- `docs/STATE-OF-THE-APP.md` §11: legible correction of the P2-2 "real PerceptionArtifact" line → "contract + fixture; perceiver went live at `vision-perceiver-real`."

## Definition of done

AC-1..AC-10 green; `bmad-code-review` passed; live verification over the 6 real PNGs shown to operator (raw responses on disk); Mary's 4 filings landed; pushed. → unblocks the P2-4b labeling kit on genuine perception.
