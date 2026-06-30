# Coverage-Assurance Interlock — ratified design record

Date: 2026-06-30. Branch: `dev/concierge-production-substrate-2026-06-29`. Class S.
Parent arc: Concierge Production Substrate. SSOT party record: `concierge-substrate-party-record-2026-06-29.md` (Round 3).
Briefing: `_bmad-output/implementation-artifacts/claude-code-brief-topic-coverage-assurance-before-leg1b-2026-06-29.md`.
Status: **party-ratified (5/5 consensus, no impasse); operator granularity ruling applied; awaiting operator sign-off to open `bmad-create-story`.**

## Why (operator directive, 2026-06-30)
Strengthen fidelity assurance to include **granular tracking of the topics/points stipulated in course SOURCE NOTES** (= per-slide PRESENTATION/speaker notes — notes earmarked for use WITH the slides). Required deliverable: an **operator-facing PRODUCTION REPORT** — a receipt ledger accounting for **ALL** source-note points, each mapped to a slide screen OR a narration (or a deliberate, signed exclusion). Inserted BEFORE Leg-1b, because Leg-1b (`warm_callback`) is the first leg that authors new learner-facing words and must anchor them to source-backed prior teaching.

## The gap this closes (scout-verified)
The substrate has deep **CONTAINMENT** (deliverable→source: Vera-R7 [built but UNWIRED], figure-grounding G5, numeric-drift WARN-only, SourceRef) but **zero source→deliverable COVERAGE**. You can prove "the callback is contained" while never checking "did every source-note point get carried somewhere." Coverage is a genuinely orthogonal new axis — narrow, and mostly an annotation + derived-receipt layer over substrate that already exists.

## OPERATOR RULING (governs this design)
**Granularity = ASSERTION-LEVEL REQUIRED FIRST.** v1 ships ONLY when the segmenter that re-segments a slide's presentation-note block into atomic teaching-assertions is proven bounded + active. The `block_level_v1` provenance value is a DIAGNOSTIC/escalation signal only — it is NOT an acceptable v1 ship state. If assertion-level re-segmentation proves unbounded/unreliable in the T0 spike, **STOP and escalate to the operator** (do not fall back to block-level and ship a coarse report). Rationale: the report must account for ALL points at the teaching-assertion grain; a multi-claim note block counted as one point understates coverage.

## Ratified v1 contract

### Identity (Winston + Irene, via Quinn's child-id reframe)
- `source_point_id = component_id + "#" + ordinal` — a CHILD sub-locator inside the EXISTING id space (no new id namespace; no new `source_type`). Root authority stays `component_id`.
- A `source_point` = one **teaching assertion** (claim / instruction / caution / framing the instructor intends a learner to take from a slide). Finer than a `TypedComponent` (a notes block ≈ 2–4 assertions); produced by re-segmenting the slide's presentation-note text inside the existing P1 extraction.
- Each point carries: parent `component_id`, `slide_key` (the parent's existing `Slide N` locator), `verbatim_text`, risk flags, and a `segmentation` provenance stamp ∈ {`assertion_level`, `block_level_v1`}. **v1 ships only at `assertion_level`** (operator ruling).
- **CAVEAT (Winston, binding):** the `#ordinal` child-id is a sub-locator, **never promoted to a join key**. All downstream joins key on the parent `component_id`; points are projection rows. "One identity, one gate, one record, one renderer."

### Coverage intent — a SET, not an enum (Irene)
- `coverage_intents: set[{gist_on_slide, detail_in_narration, deliberately_excluded}]`, non-empty per point.
- Assigned **derived-first** from component type + `pedagogical_role`; **LLM refines only at ambiguity** (and only at a resolved anchor — Murat); **every `deliberately_excluded` is operator-signed** (no silent exclusion).
- Default **slides=gist, narration=detail**; forced **BOTH** (visible anchor AND spoken) when the point is LO-load-bearing OR a safety/clinical caution/negation OR the slide's organizing claim.

### Two orthogonal axes, joined per point, NEVER merged (Vera)
- **Axis A — coverage** (source→deliverable): `{covered_on_slide, covered_in_narration, both, deliberately_excluded, missing}`. The NEW axis this interlock owns.
- **Axis B — containment** (deliverable→source): `{verbatim_preserved, altered, risky}` — Vera-R7 territory, NOT recomputed here.
- The operator report is the **join** (rows = source points × per-row containment verdict). A `missing` point has no containment verdict — it's a pure coverage hole.

### Risk taxonomy → drives verbatim_required + R7 binding (Vera + Irene)
- `{clinical_claim | numeric | dosing | negation | comparator | exemplary_language}`. `verbatim_required` is a **deterministic floor** (numbers/doses/negations/comparators/named clinical terms/testable definitions) — LLM/operator may not downgrade it. R7 binds HARDEST (token-identity) on the verbatim set; semantic-containment (fidelity-of-meaning) elsewhere.

### vouch_level — honesty fuse (Vera, binding precondition)
- Per containment-cell enum: `vouch_level ∈ {verified, advisory_caveat, not_assessed}`.
- `verified` ONLY for deterministic string/span matches (verbatim/numeric/dosing). `negation`/`comparator` → `advisory_caveat` (the bag-of-words flipped-negation false-negative is DISCLOSED, never hidden as a green vouch).
- **CAVEAT (Vera, binding):** a render-time assertion — no containment cell may display `verified` without a `vouch_level` stamp; missing/`not_assessed` cannot render as verified.
- R7 binds **at report-generation time** (this interlock is R7's first REPORTING caller; Leg-1b is its first AUTHORING caller). Same function, two bind sites.

### Teeth — deterministic anchor FIRST (Murat)
- Resolution order per point: a **deterministic locator anchor** (`source_point → {component_id|narration_segment_id, slide_key}`) resolves FIRST. **No anchor → forced `missing`, regardless of any LLM.** The LLM only characterizes content AT a resolved anchor (bounded, never open search). `verbatim_required` = deterministic span-presence, no LLM. The judge NEVER promotes a `missing`.
- LLM-judge guardrails: first-run-stands, no retry-to-green, temp-0, pinned model, prompt-hash logged. (Mirrors the existing `SEMANTIC_TRIPWIRE=None` discipline.)

### Fail-loud vs advisory split (Murat)
- **BLOCK before audio spend** iff `must_cover ∧ (missing ∨ verbatim_absent) ∧ no_planned_surface` — a set-difference at the existing both-walks UDAC gate (`resolve_consumed_assets`→`_pause_at_error`).
- Everything fuzzy (`altered_or_risky`, negation/comparator semantics, low-confidence anchored judgments) → **WARN / ledger-only** until a **≥3-run calibration window**. Every point still appears on the receipt with a status (full accountability); only deterministically-certain, money-on-the-line failures halt.

### Insertion seam / receipt (Winston)
- AUTHORED `coverage_intents` ride `G0EnrichmentResult` via `repin_additive` (frozen side — the proven P2-citations / P3-pedagogy additive-tuple pattern).
- OBSERVED `coverage-receipt.json` is a `RunAssetEntry` on the UDAC Run-Asset-Index (run side). Opposite sides of the freeze line.
- The receipt is **DERIVED** by projecting joins that already exist at the dispatch site (the `ReconcileView` pattern) — **no producer self-report channel**, **no coverage store outside the RAI**. The narration role-seed matcher's silent 0/>1 drop (`enrichment_consumption.py:335`) becomes a logged `missing`.
- **No new node/edge, no `digest_schema_version` bump → stays OUT of the block-mode regime.**

### Report surface (scout)
- Coverage **plan** view → G0E decision card (pre-authoring). Coverage **receipt** → **Storyboard-B HTML** (`storyboard_html_emitter.py`, per-slide, operator-facing, PRE-SPEND). Structured ledger persisted alongside `run_summary.yaml` / the RAI.
- Report columns: source-point (slide_key + human "Slide N / note") · intent-set · coverage status · containment verdict + `vouch_level`. Honest denominator: the report declares its `segmentation` grain on its face (v1 = `assertion_level`).

## Model tier — BINDING (operator, 2026-06-30)
Every LLM-backed function in this interlock MUST run on a **high-capability frontier model (gpt-5 class — the intended production model)**, never a cheap/small model. These are judgment functions over scholarly/clinical content and are **essential to scholarly content delivery** — a weak model here silently undermines the coverage + fidelity guarantee. Applies to: (a) presentation-note → teaching-assertion **segmentation**; (b) coverage-intent **refinement at ambiguity**; (c) content-presence **judgment at a resolved anchor**; (d) any **audit/report-generation** LLM assist. No mocks — the live slice exercises the real model ([[feedback_no_mocks_real_live_apis]]).

**Determinism — FREEZE-ONCE-PER-RUN + SPAN-ANCHORED (operator ruling 2026-06-30, T0-spike-driven).** gpt-5 is a reasoning model and is NOT seed-reproducible cross-run (spike: 13 vs 11 assertions on the same block under a pinned seed; paraphrase wording drifts). So determinism is NOT chased via seed; instead: segment ONCE per run, FREEZE on the `corpus_fingerprint`-keyed `G0EnrichmentResult` (the P1/P2/P3 pattern → first-run-stands by construction), and key `source_point` identity on the VERBATIM SOURCE SPAN (stable) not the paraphrase (drifts). Cross-run reproducibility sacrificed (±1–2 points), kept honest by the `segmentation` stamp. Reuse the P3 `build_pedagogy_annotations` gpt-5 binding (`PEDAGOGY_LIVE_MODEL="marcus"`→gpt-5); temperature bound at construction (gpt-5 rejects per-call temp=0). **MANDATORY harness discipline (spike-proven): a hard PER-REQUEST `OpenAI(timeout=…, max_retries=0)` on every call (a missing per-request timeout hung the first spike ~8 min); generous `max_completion_tokens` (reasoning models return EMPTY if too small); `reasoning_effort="low"`.** Live-key recipe [[reference_live_openai_key_dotenv_override]]; FOREGROUND + flushed [[reference_live_llm_extraction_foreground]].

**Spike verdict (2026-06-30): GO.** gpt-5 segmentation bounded (10–13 assertions/block, ≤15 ceiling) + faithful + atomic on the real `**Narration (Speaker Notes):**` deck. Evidence `evidence/coverage-t0-spike-controlled.json`.

## v1 IN vs DEFERRED (named, not silent)
**IN:** child-id schema + active assertion-level segmenter (operator-gated; escalate if unbounded); intent-as-set; two axes; risk taxonomy → verbatim floor; vouch_level; deterministic-anchor teeth; derived RAI receipt; fail-loud-before-audio on must-cover; R7 reporting binding; Storyboard-B render; presentation-notes only.
**DEFERRED (named follow-ons):** deterministic corpus-wide matcher; full Leg-4 UDAC completion; workbook-surface gating; hard verbatim *enforcement* beyond floor+advisory; ≥3-run-calibrated promotion of fuzzy WARN→gate; the span/dependency-aware negation/comparator detector (the `directed-voice-vera-r7-wire-clinical-lexicon` hard-gate triad).

## Leg-1b acceptance-bar amendments (dispositioned)
1. **Each `warm_callback` cites ≥1 `source_point_id` anchor** → **structural GATE**: anchor exists ∧ upstream via `teaches_after` ∧ covered-not-excluded (referential-integrity, not an LLM vibe-check).
2. **Callback passes Vera-R7 vs those anchors** → **WARN field** in v1 (semantic teeth uncalibrated; recorded, not blocking).
3. **No new clinical/numeric/comparator/negation/term** → **SPLIT**: numeric/term *introduction* (deterministic) = GATE; comparator/negation *flip* (bag-of-words FN) = WARN.
4. **Live slice includes a coverage receipt** → **GATE + strengthen**: the negative/fail-loud path must be demonstrated (real or ablated must-cover point → block before audio).
5. **A `detail_required_in_narration` point is NOT satisfied by a plausible slide alone** → **keystone HARD GATE** (deterministic: a detail-in-narration point whose only resolved anchor is a slide → NOT covered). Lands once v1's slide-vs-narration status distinction is live.

## Arc re-sequence
`coverage-assurance-interlock` (NEW, this story) → **Leg-1b** (now CONSUMES the source-point anchors; DUAL-GATE per Murat) → Leg-2 (motion bundle) → Leg-3 (callback + clustering; preceded by the read-only confirm-scope spike) → Leg-4 (asset/fidelity ledgers; folds in the deferred verbatim/calibration items). No other legs reorder.
- The interlock opens with a **T0 half-day ingest/segmentation spike** with a **NUMERIC escalation threshold** (max assertions/block, max latency/pass) written into the AC (John's caveat). Spike outcome under the operator ruling: assertion-level proven bounded → segmenter ships active; unbounded/unreliable → **escalate to operator** (no coarse-ship fallback).

## Consensus
5/5 ACCEPT (John, Winston, Murat, Vera, Irene), no impasse — Dr. Quinn synthesis dissolved the granularity fault line (identity space stays component-rooted; unit of accounting becomes assertion-level via child sub-ids). Three binding caveats written into AC: child-id-never-a-join-key (Winston); render-time vouch_level gate (Vera); provenance-stamp-is-load-bearing (Irene). Operator overrode the staged-fallback with **assertion-level-required-first**.
