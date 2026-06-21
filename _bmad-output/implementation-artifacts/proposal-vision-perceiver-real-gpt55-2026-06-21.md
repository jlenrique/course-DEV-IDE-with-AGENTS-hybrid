# Proposal — Make the Vision Perceiver REAL (live gpt-5.5), retire the fixture/pinned-endpoint stub

**Date:** 2026-06-21 · **Branch:** `fidelity-perception-arc-2026-06-19` · **Class:** S (substrate)
**Workflow:** party-mode green-light (this doc) → `bmad-quick-dev` (dev agent) → `bmad-code-review` → done.
**Operator directives binding this work:**
- *"No more mocked, predicted, temporary crap — everything must be real, live, making actual API calls to their intended models, OpenAI 5.5, etc."*
- *"Keep to BMAD-sanctioned workflows (rapid dev) and work with a fully-spawned party-mode team + a dev agent for manipulating the codebase."*

## Why now (the discovery)

P2-4b's kickoff plan assumes step 2 is "run the **committed** vision perception over the PNGs." Scouting at session-START found the committed vision specialist is a **fixture/contract stub, not a live perceiver**:

- `app/specialists/vision/provider.py::perceive_png` POSTs PNG bytes to a pinned `VISION_PROVIDER_ENDPOINT` and expects a structured JSON response. **`.env` has no `VISION_PROVIDER_ENDPOINT`/`VISION_PROVIDER_API_KEY`.** Default model id is `vision-fixture-v1`.
- The only real perceived artifact on disk is a **hand-authored golden fixture for slide-01** (`tests/fixtures/perception/golden/`).
- So P2-2 built the perception *contract* + fixtures; **no live model was ever wired** that can perceive an arbitrary PNG.

This blocks the genuine "narration tracks the real slide" capability and violates the no-mocks directive. The labeling kit (and the eventual production reliability claim) needs a **real perceiver**.

## Confirmed external facts

- **`gpt-5.5` is a real OpenAI model** — API id `gpt-5.5` (snapshot `gpt-5.5-2026-04-23`), live since 2026-04-24, vision-capable, priced **$5/1M in · $30/1M out**. (Verified via OpenAI docs 2026-06-21.) No "plausible-token contamination" risk (the anti-pattern on file from when ids were fictitious).
- House real-LLM pattern: `langchain_openai.ChatOpenAI` resolved via the cascade (`app/models/adapter.py` + `app/models/selector` + `runtime/config/model_cascade.yaml`). `OPENAI_API_KEY` is present in `.env`.
- The reading-path classifier (`scripts/utilities/reading_path_classifier.py`) consumes a HIGH/perceived `PerceptionArtifact` with `visual_elements[].bbox` (normalized) + `text_blocks` + `layout_description` + `slide_title` and emits one of 7 patterns + a scan order. It is **already real/deterministic**; only its *input* (perception) is currently fake.

## Proposed change (scope for the dev agent)

1. **`app/specialists/vision/provider.py`** — `perceive_png` makes a **real gpt-5.5 multimodal call**: encode PNG → base64 `image_url` content block + a structured perception prompt demanding the `VisionProviderResponse` JSON shape (visual_elements with normalized bboxes `[x1,y1,x2,y2]` in 0..1, text_blocks, layout_description, slide_title, extracted_text, confidence, confidence_score). Route via the house `ChatOpenAI`/cascade. Parse → validate `VisionProviderResponse`. Keep fail-loud + the existing retryable-error taxonomy (timeout/429/5xx/transport).
2. **`app/specialists/vision/model_config.yaml`** — retire the `vision-fixture-v1` provider block; real model `gpt-5.5`.
3. **`runtime/config/openai_pricing.yaml`** — add `gpt-5.5` row ($5/$30). **`runtime/config/model_cascade.yaml`** — add a `vision` specialist entry (`gpt-5.5`) so `ensure_pricing_covers_cascade` stays green (vision is currently absent from the cascade).
4. **Tests** — a **live-API** test that perceives the real frozen-corpus PNGs, gated `pytest.skip` when `OPENAI_API_KEY` is absent (house rule). Deterministic parse/validation tests use **recorded real gpt-5.5 responses** (captured from an actual call, labeled as recordings — NOT invented stubs). The fixture provider is NOT the production path.
5. **Live verification** — run the real perceiver over all 6 `runs/compositor/assembly-bundle/visuals/slide-0N.png` and surface actual perceived elements + the classifier's pattern per slide.

## Decisions the party must ratify

- **D1 — Architecture:** replace pinned-endpoint httpx with house `ChatOpenAI`/cascade multimodal call? (vs. keep the endpoint contract and stand up an adapter service). *Recommend: replace.*
- **D2 — Model id:** `gpt-5.5` for vision (add pricing + cascade rows). *Recommend: yes.*
- **D3 — bbox provenance:** LLM-estimated normalized bboxes are inherently approximate; the classifier buckets into thirds so coarse boxes suffice. Accept + document the precision caveat? *Recommend: accept, document.*
- **D4 — Structured output:** enforce JSON via response_format/json-mode + parse + validate + bounded retry on malformed JSON. *Recommend: yes.*
- **D5 — Test posture under "no mocks":** production path fully live; determinism via recorded-real responses + key-gated live test. Acceptable, or stricter? *Party to rule.*
- **D6 — Cadence:** `bmad-quick-dev` (dev agent) implements → `bmad-code-review` before done. Pipeline-manifest lockstep regime applies only if a trigger path is touched (vision provider is not currently a trigger path — confirm). *Recommend: quick-dev + code-review.*
- **D7 — Relationship to P2-4b:** is this a standalone substrate enabler ("vision-perceiver-real") that PRECEDES the P2-4b labeling kit, or folded into P2-4b? *Recommend: standalone enabler first; kit + calibration follow on the real output.*

## Definition of done (this work item)

- `perceive_png` makes a real live gpt-5.5 vision call; fixture provider retired from the production path.
- Pricing + cascade cover `gpt-5.5`; configs validate.
- Live test perceives the 6 real PNGs green (key-gated); deterministic parse tests green; lint-imports / ruff / sandbox-AC clean.
- `bmad-code-review` passed.
- Live verification output (6 real perceptions + classifier patterns) shown to operator → unblocks the P2-4b labeling kit on genuine perception.
