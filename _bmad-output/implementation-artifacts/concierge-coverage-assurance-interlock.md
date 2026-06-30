# Story concierge-coverage-assurance-interlock: source-note topic coverage assurance + production report

Status: ready-for-dev

<!-- Arc: Concierge Production Substrate (branch dev/concierge-production-substrate-2026-06-29, Class S). Sequenced AHEAD of Leg-1b (which consumes this story's source_point anchors). Party-RATIFIED amendment 2026-06-30 (John/Winston/Murat/Irene/Vera; Dr. Quinn synthesis; 5/5 ACCEPT, no impasse) + operator rulings. AUTHORITATIVE DESIGN: _bmad-output/planning-artifacts/coverage-assurance-interlock-design-2026-06-30.md. SSOT party record: concierge-substrate-party-record-2026-06-29.md (Round 3). GATE MODE: DUAL-GATE. -->

## Story

As the production operator,
I want a **coverage-assurance layer** that tracks every atomic point in a slide's **presentation/speaker notes** and emits an operator-facing **production report** mapping each point to a slide screen or a narration (or a signed exclusion), fail-loud before audio spend on any uncovered must-cover point,
so that a true-production concierge run can **prove every important source-note point was actually carried** — closing the gap that today's containment gates (which only prove "what I authored traces to source") cannot see, and giving Leg-1b's `warm_callback` authoring a real source-point anchor substrate.

## Why this story exists (the gap it closes)

The substrate has deep **CONTAINMENT** (deliverable→source: Vera-R7, figure-grounding G5, numeric-drift, SourceRef) but **zero source→deliverable COVERAGE**. You can prove "the callback is contained" while never checking "did every source-note point reach a screen or the narration." Coverage is a genuinely orthogonal new axis. This interlock is a **prerequisite** for Leg-1b: `warm_callback` must anchor to source-backed prior teaching, and without `source_point` anchors the callback amendments have nothing to bind to.

## Binding operator rulings (ACs, not notes)

**AC-OP1 — ASSERTION-LEVEL REQUIRED FIRST.** v1 ships ONLY when the segmenter that re-segments a slide's presentation-note block into atomic teaching-assertions is proven **bounded + active**. `block_level_v1` is a DIAGNOSTIC-only provenance value, **never an acceptable v1 ship state**. If assertion-level re-segmentation proves unbounded/unreliable in the T0 spike, **STOP and ESCALATE to the operator** — there is no coarse-ship fallback.

**AC-OP2 — HIGH-CAPABILITY MODEL (essential to scholarly content delivery).** Every LLM-backed function — (a) presentation-note → teaching-assertion segmentation, (b) coverage-intent refinement at ambiguity, (c) content-presence judgment at a resolved anchor, (d) any audit/report-generation LLM assist — MUST run on a **gpt-5-class frontier model** (the intended production model), **real calls, NO mocks**. Reuse the existing gpt-5 binding path `build_pedagogy_annotations` uses (`PEDAGOGY_LIVE_MODEL="marcus"` → gpt-5); do not introduce a new model seam. **MANDATORY harness discipline (T0-spike-proven):** a hard PER-REQUEST client timeout (`OpenAI(timeout=…, max_retries=0)`) on EVERY call — without it a single slow gpt-5 reasoning call hangs indefinitely (the spike's first run hung ~8 min). Generous `max_completion_tokens` (reasoning models burn the budget on hidden reasoning first → empty output if too small); `reasoning_effort="low"` for the segmentation pass. Live FOREGROUND + flushed.

**AC-OP2-DET — Determinism = FREEZE-ONCE-PER-RUN + SPAN-ANCHORED identity (operator ruling 2026-06-30; T0-spike-driven).** gpt-5 is a reasoning model and is NOT seed-reproducible across runs (spike: slide-3 gave 13 then 11 assertions under a pinned seed; paraphrase wording drifts). Therefore: **segment ONCE per run and FREEZE on the `corpus_fingerprint`-keyed `G0EnrichmentResult` (the P1/P2/P3 pattern)** — the report is fully deterministic WITHIN the shipped run and "first-run-stands / no-retry-to-green" holds by construction. **Key `source_point` identity on the VERBATIM SOURCE SPAN, not the LLM paraphrase** (the span the model cuts is far more stable than its wording; the paraphrase is display only). Cross-run reproducibility is explicitly sacrificed (re-running a deck may yield ±1–2 points) and the `segmentation` provenance stamp keeps that honest. Do NOT chase cross-run seed-determinism — it is not achievable with gpt-5 and is not required for the gate (which operates against the frozen per-run set).

## Acceptance Criteria — the ratified contract

**AC1 — Identity rides the existing id space (no parallel registry).** `source_point_id = component_id + "#" + ordinal` — a CHILD sub-locator of the existing `TypedComponent` (`app/marcus/lesson_plan/source_type.py:217-313`). NO new id namespace; NO new `source_type` enum value (speaker notes are the existing `narration`-typed, `Slide N`-locator components). **Binding caveat (Winston):** the `#ordinal` child-id is a sub-locator, **NEVER a join key** — every downstream join keys on the parent `component_id`; `source_point`s are projection rows.

**AC2 — A `source_point` is a teaching ASSERTION.** One claim / instruction / caution / framing the instructor intends a learner to take from a slide; finer than a `TypedComponent` (a notes block ≈ 2–4 assertions), produced by re-segmenting the slide's presentation-note text. Each carries: parent `component_id`, `slide_key` (the parent's existing `Slide N` locator), `verbatim_text`, `risk_flags`, and a `segmentation` provenance stamp ∈ {`assertion_level`, `block_level_v1`}. **Binding caveat (Irene):** the `segmentation` stamp is load-bearing — the report declares its grain on its face; it is never dropped.

**AC3 — Coverage intent is a SET, not an enum.** `coverage_intents: non-empty set of {gist_on_slide, detail_in_narration, deliberately_excluded}`. Assigned **derived-first** from component type + `pedagogical_role`; the LLM refines **only at ambiguity** (and only at a resolved anchor). **Every `deliberately_excluded` is operator-signed** (no silent exclusion). Default **slides=gist / narration=detail**; forced **BOTH** when the point is LO-load-bearing OR a safety/clinical caution/negation OR the slide's organizing claim.

**AC4 — Two orthogonal axes, joined per point, NEVER merged.** Axis A **coverage** (source→deliverable): `{covered_on_slide, covered_in_narration, both, deliberately_excluded, missing}`. Axis B **containment** (deliverable→source): `{verbatim_preserved, altered, risky}` — Vera-R7 territory, NOT recomputed here. A `missing` point has no containment verdict.

**AC5 — Risk taxonomy drives the verbatim floor + R7 binding.** Each point carries ≥0 of `{clinical_claim, numeric, dosing, negation, comparator, exemplary_language}`. `verbatim_required` is a **deterministic floor** (numbers/doses/negations/comparators/named clinical terms/testable definitions) — LLM/operator may not downgrade it; it is where Vera-R7 binds hardest (token-identity), semantic-containment elsewhere.

**AC6 — `vouch_level` honesty fuse.** Per containment cell, `vouch_level ∈ {verified, advisory_caveat, not_assessed}`. **Binding caveat (Vera):** a render-time assertion — no cell may display `verified` without a `vouch_level` stamp; `verified` is reserved for deterministic string/span matches (verbatim/numeric/dosing); `negation`/`comparator` → `advisory_caveat` (the bag-of-words flipped-negation false-negative is DISCLOSED, never a green vouch). **R7 binds in THIS interlock at report-generation time** (it is R7's first REPORTING caller — `audit_rhetorical_source_containment`, `app/specialists/_shared/voice_provider_text.py:267-350`, currently UNWIRED) wherever a containment verdict prints.

**AC7 — Teeth: deterministic anchor FIRST.** Per point, a **deterministic locator anchor** resolves first (`source_point → {component_id|narration_segment_id, slide_key}`). **No anchor resolved → status forced `missing`, regardless of any LLM.** The LLM only characterizes content AT a resolved anchor (bounded, never open search). `verbatim_required` = deterministic span-presence, no LLM. The judge NEVER promotes a `missing`.

**AC8 — Fail-loud before audio spend.** BLOCK iff `must_cover ∧ (missing ∨ verbatim_absent) ∧ no_planned_surface` — a set-difference raised at the existing both-walks UDAC seam (`resolve_consumed_assets`→`_pause_at_error`, `app/marcus/orchestrator/udac_wiring.py` + `production_runner.py`), BEFORE any ElevenLabs/Descript spend. Everything fuzzy (`altered_or_risky`, negation/comparator semantics, low-confidence anchored judgments) is **WARN / ledger-only** until a **≥3-run calibration window** (mirror `SEMANTIC_TRIPWIRE=None`). Every point still appears on the receipt with a status (full accountability); only deterministically-certain, money-on-the-line failures halt.

**AC9 — Insertion seam (additive; out of block-mode).** AUTHORED `coverage_intents` ride `G0EnrichmentResult` via `repin_additive` (frozen side; mirror P2 `citation_resolutions` / P3 `pedagogy_annotations`, `app/marcus/lesson_plan/g0_enrichment.py:368-469`). OBSERVED `coverage-receipt.json` is a `RunAssetEntry` on the UDAC Run-Asset-Index (run side; `app/marcus/lesson_plan/run_asset_index.py`). Opposite sides of the freeze line. The receipt is **DERIVED** by projecting EXISTING joins at the dispatch site (the `ReconcileView` pattern) — **NO producer self-report channel, NO coverage store outside the RAI.** The narration role-seed matcher's silent 0/>1 drop (`app/marcus/orchestrator/enrichment_consumption.py:335`) becomes a **logged `missing`**. **NO new node/edge, NO `digest_schema_version` bump** → stays OUT of the block-mode regime (confirm at T1 vs `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`).

**AC10 — The production report.** Coverage PLAN view on the G0E decision card (pre-authoring); coverage RECEIPT rendered into **Storyboard-B HTML** (`app/gates/section_07c/storyboard_html_emitter.py`, per-slide, pre-spend, operator-facing); structured ledger persisted alongside `run_summary.yaml` / the RAI. Columns: source-point (slide_key + human "Slide N / note") · intent-set · coverage status · containment verdict + `vouch_level`. The report declares its `segmentation` grain (v1 = `assertion_level`).

**AC11 — LIVE slice with the negative case (per the binding per-component live-test gate).** A real run (gpt-5 segmentation + judgment, real model, no mocks) on a real presentation-notes deck: every point gets a resolved status; ≥1 real `covered_on_slide` and ≥1 real `covered_in_narration` with deterministic anchors asserted; and **the fail-loud path is exercised** — a genuinely-missing must-cover point (or a deliberately ABLATED one) trips `_pause_at_error` BEFORE audio spend, captured as evidence. **A covered-only run does NOT pass** (untested gate). Offline gates RED-first; ruff + lint-imports clean (only pre-existing C3 permitted).

## Tasks / Subtasks

- [x] **T1 Readiness + block-mode check** (AC: 9) — read the design record + party record Round 3 + this story. Confirm the seam touches NO `block_mode_trigger_paths` (additive `G0EnrichmentResult` field + a new `lesson_plan` pass + an RAI asset + a `section_07c` render; no node/edge, no digest bump). If any of that changes, read `docs/dev-guide/pipeline-manifest-regime.md` first. DEEP-READ each reused module before coding (non-negotiable): `g0_enrichment.py` (repin_additive + ReconcileView validator), `pedagogy_annotation.py` (the P3 pass + its gpt-5 binding to mirror), `source_type.py` (TypedComponent parent), `run_asset_index.py` + `udac_wiring.py` (RAI + both-walks fail-loud seam), `enrichment_consumption.py` (the joins + the :335 silent drop), `storyboard_html_emitter.py` (render surface), `voice_provider_text.py:267-350` (R7 to bind as reporting caller).
- [x] **T0/T2 INGEST-SEGMENTATION SPIKE — DONE 2026-06-30, verdict GO** (AC: OP1, OP2, OP2-DET, 2). Live gpt-5 on the real `**Narration (Speaker Notes):**` deck (`course-content/courses/tejal-apc-c1-m1-p2-trends/slides/*.md`): **bounded + faithful** — slide-1 11/11, slide-2 10/10, slide-3 13/11 assertions (max 13 ≤ 15 ceiling), latency 11–53s under a 60s per-request timeout, assertions genuinely atomic + source-faithful. **Not seed-reproducible cross-run** (the operational risk the spike caught) → resolved by the **operator ruling AC-OP2-DET (freeze-once-per-run + span-anchored identity)**, NOT escalation-to-abandon. Evidence: `_bmad-output/implementation-artifacts/evidence/coverage-t0-spike-controlled.json`; harness `scratchpad/coverage_spike_controlled.py`. Threshold to keep in code: ≤15 assertions/block (else investigate over-segmentation), 60s per-request timeout, max_retries=0.
- [x] **T3 RED — `source_point` + coverage_intent model** (AC: 1, 2, 3, 5) — child-id (`component_id#ordinal`, never a join key), assertion unit, intent-as-set (derived-first + ambiguity-only LLM + operator-signed exclusions), risk taxonomy + deterministic verbatim floor, `segmentation` stamp. Closed enums + import-time exhaustiveness guards (mirror `PedagogicalRole`/`SourceTypeLiteral` idiom).
- [x] **T4 Segmentation + intent pass (gpt-5)** (AC: OP2, 2, 3) — a P3-style `coverage_annotation.py` sibling pass mirroring `build_pedagogy_annotations` (offline + live legs; reuse its gpt-5 binding; determinism via seed/pinned-model/prompt-hash, NOT temp-0). Additive tuple onto `G0EnrichmentResult` via `repin_additive`.
- [x] **T5 RED — derived receipt + two axes + vouch_level** (AC: 4, 6, 7, 9) — `coverage-receipt.json` as a `RunAssetEntry`; coverage axis DERIVED by projecting existing joins (component→slide locator, LO→section, narration role-seed; the :335 silent drop → logged `missing`); containment axis via R7 at report-gen with the `vouch_level` render-time gate. Deterministic anchor FIRST (no anchor → `missing`).
- [x] **T6 RED — fail-loud gate** (AC: 8) — set-difference `must_cover ∧ (missing ∨ verbatim_absent) ∧ no_planned_surface` at the both-walks UDAC seam → `_pause_at_error` before audio spend; fuzzy = WARN/ledger-only. Test BOTH walks.
- [x] **T7 RED — the production report render** (AC: 10) — plan on G0E card; receipt → Storyboard-B HTML per-slide; ledger persisted; `segmentation` grain shown.
- [ ] **T8 LIVE slice + negative case** (AC: 11) — real gpt-5 run on a real notes deck; assert full accounting + ≥1 covered_on_slide + ≥1 covered_in_narration with asserted anchors; **ablate a must-cover point → confirm block fires before audio spend** (captured evidence). FOREGROUND + hard timeout + flushed; live-key recipe.
- [x] **T9 Regression + hygiene** (AC: 11) — flag-OFF byte-identical (additive); full marcus/lesson_plan + orchestrator + section_07c suites green; ruff + lint-imports (only pre-existing C3).

## Dev Notes

### Gate mode — DUAL-GATE (justified)
LLM-backed judgment over scholarly/clinical content + a NEW fail-loud gate + fidelity-sensitive (the report makes assurances an operator will trust). Per the Lesson-Planner governance idiom, this is a dual-gate story: G6-style review on the schema/enum/guard discipline AND a fidelity/quality review on the coverage+containment honesty (vouch_level, the disclosed bag-of-words caveat). Murat owns the live negative-case bar; Vera owns the vouch_level render-time gate.

### Reuse map (verified by two reuse-first scouts — DEEP-READ at T1)
- `TypedComponent` parent: `app/marcus/lesson_plan/source_type.py:217-313` (`component_id`, `parent_source_id`, `source_type`, `locator['Slide N']`, verbatim `excerpt`, `flagged_ungrounded`).
- Additive-tuple insertion: `G0EnrichmentResult` `app/marcus/lesson_plan/g0_enrichment.py:368-469`; `repin_additive` (the sanctioned additive-layer path used by P2 citations / P3 pedagogy); `ReconcileView` validator pattern `:188-255` for the fail-loud "nothing silently dropped" idiom.
- The P3 pass to MIRROR (structure + gpt-5 binding + offline/live split): `build_pedagogy_annotations` `app/marcus/lesson_plan/pedagogy_annotation.py:865`; `PedagogyAnnotation` (`lo_refs`/`pedagogical_role`/`teaches_after`/`teachable`) `:169-237`; referential invariant `:459-490`.
- Joins to PROJECT (do not rebuild): component→slide `slide_ordinal_from_locator` `app/marcus/orchestrator/enrichment_consumption.py:227`; the silent 0/>1 role-seed drop to convert to `missing` `:335`; LO→section `app/marcus/lesson_plan/workbook_enrichment.py:336`.
- Receipt infra: `RunAssetIndex`/`RunAssetEntry` `app/marcus/lesson_plan/run_asset_index.py` (digest-from-disk, `repin_additive`, `CONSUMER_REGISTRY`); both-walks fail-loud `app/marcus/orchestrator/udac_wiring.py` (`record_gate_ratification`, `resolve_consumed_assets`→`_pause_at_error`); runner seam `production_runner.py` `_udac_ratify_gate`.
- R7 (REPORTING caller only here): `audit_rhetorical_source_containment` / `assert_rhetorical_source_containment` `app/specialists/_shared/voice_provider_text.py:267-350` (PROVIDED-BUT-UNWIRED; bag-of-words negation/comparator FN is the disclosed caveat).
- Report render: `app/gates/section_07c/storyboard_html_emitter.py` (per-slide, pre-spend); persist alongside `run_summary.yaml` (`production_runner.py:844`).
- Presentation-notes substrate: markdown `**Narration (Speaker Notes):**` convention inside slide files (e.g. `course-content/courses/tejal-apc-c1-m1-p2-trends/slides/slide-1-*.md`), extracted today as ONE `narration`-typed component per block (the granularity AC-OP1/T0 addresses).

### The three binding caveats (write as code-enforced constraints)
1. **Winston:** `source_point_id` (`#ordinal`) is NEVER a join key — joins key on parent `component_id`. A reviewer seeing a join on the child-id is the design failing.
2. **Vera:** render-time assertion — no containment cell displays `verified` without a `vouch_level` stamp; negation/comparator → `advisory_caveat`.
3. **Irene:** the `segmentation` provenance stamp is load-bearing — the report declares its grain; never dropped to "simplify."

### Project structure / governance
- Verify via shipped deps, not operator CLIs. `.venv/Scripts/python.exe`; `PYTHONIOENCODING=utf-8`. Live-key recipe: `os.environ.pop("OPENAI_API_KEY", None)` sentinel + `load_dotenv(REPO/.env, override=True)`; run live FOREGROUND + hard timeout + flushed (NEVER background+monitor).
- Additive → flag-OFF/no-coverage-pass output byte-identical (regression firewall). No mocks for any live claim (real gpt-5 + real run artifacts).

## Out of scope (named)
- Leg-1b `warm_callback` AUTHORING + R7's authoring-loop wiring (this story is R7's REPORTING caller only).
- Deterministic corpus-wide matcher; full Leg-4 UDAC completion; workbook-surface gating; hard verbatim *enforcement* beyond floor+advisory; the span/dependency-aware negation/comparator detector (the `directed-voice-vera-r7-wire-clinical-lexicon` hard-gate triad); ≥3-run-calibrated promotion of fuzzy WARN→gate.

## References
- [Source: _bmad-output/planning-artifacts/coverage-assurance-interlock-design-2026-06-30.md] — the authoritative ratified design (every AC traces here).
- [Source: _bmad-output/planning-artifacts/concierge-substrate-party-record-2026-06-29.md] — Round 3 amendment + Quinn synthesis + operator rulings + the 5 Leg-1b amendment dispositions.
- [Source: _bmad-output/implementation-artifacts/claude-code-brief-topic-coverage-assurance-before-leg1b-2026-06-29.md] — the originating briefing.
- [Source: app/marcus/lesson_plan/{source_type.py,g0_enrichment.py,pedagogy_annotation.py,run_asset_index.py}] ; [app/marcus/orchestrator/{udac_wiring.py,enrichment_consumption.py,production_runner.py}] ; [app/specialists/_shared/voice_provider_text.py:267-350] ; [app/gates/section_07c/storyboard_html_emitter.py].

## Dev Agent Record
### Agent Model Used
Amelia (BMAD dev agent) on claude-opus-4-8[1m]. OFFLINE RED-first foundation only; ZERO live gpt-5/network calls (T8 live slice is the orchestrator's job).

### Debug Log References
- T1 deep-read of every reused module (findings below) — non-negotiable, done before any code.
- Offline segmenter fix: naive sentence regex split "$5.2" and "U.S." mid-span (losing the `numeric` floor on a fragment) → replaced with a boundary regex that splits only at `terminator + whitespace + capital/digit/quote`, protecting decimals + dotted abbreviations. RED captured at `test_offline_pass_segments_only_narration` / `test_offline_points_carry_derived_risk_and_verbatim_floor`, green after fix.
- Keystone RED→green: `tests/unit/marcus/orchestrator/test_coverage_gate_wiring.py` failed RED with `ImportError: cannot import name 'coverage_gate_wiring'`, then green (7 passed) after implementing the wiring module + the both-walks seam call.
- Regression-firewall judgment call: adding `coverage_annotations` to `G0EnrichmentResult` (AC9) would, like P2/P3, change the card payload even when empty. To honor the explicit AC11 byte-identical firewall, `to_card_payload` PRUNES the key when the tuple is empty (so a flag-OFF run's `g0-enrichment.json` + RAI digest are unchanged from baseline) and emits it normally when the pass ran. Documented as a deliberate refinement over P3's always-emit.

### T1 findings (file:line — current-state / what-changed / what-preserved)
- `source_type.py:217-313` `TypedComponent` (component_id / parent_source_id / source_type / locator / excerpt / flagged_*). CHANGE: none (read-only parent). PRESERVE: `source_point_id = component_id#ordinal` is a CHILD; no new id namespace, no new `source_type` value.
- `g0_enrichment.py:368-469` `G0EnrichmentResult` + `repin_additive` pattern + `ReconcileView:188-255`. CHANGE: added additive `coverage_annotations: tuple[CoverageAnnotation,...]=()` field (mirror P2/P3) + prune-when-empty in `to_card_payload`. PRESERVE: the A4 sidecar excludes, the provisional-only + A4-ts validators, byte-identical card when no coverage pass ran.
- `pedagogy_annotation.py:865/72/749/801` `build_pedagogy_annotations` offline/live split + `PEDAGOGY_LIVE_MODEL="marcus"` gpt-5 binding + import-time exhaustiveness guard + per-row resilient parse. CHANGE: none (mirrored, not edited). PRESERVE: the offline-default/live-gated structure; the parse/build helpers are offline-tested.
- `run_asset_index.py` `RunAssetEntry`/`RunAssetIndex`/`repin_additive`/`resolve_asset`/`GATE_ASSET_MAP`/`CONSUMER_REGISTRY`. CHANGE: none. PRESERVE: digest-from-disk discipline; the receipt is a derived `RunAssetEntry` payload (no parallel store).
- `udac_wiring.py` `record_gate_ratification` (both walks) + `resolve_consumed_assets`→fail-loud. CHANGE: none (the coverage gate is a SIBLING reader at the same shared seam). PRESERVE: flag-gated byte-identical-when-off pattern (copied for `MARCUS_COVERAGE_GATE_ACTIVE`).
- `production_runner.py:164` `_udac_ratify_gate` + `:1830` shared dispatch seam. CHANGE: added a flag-gated `coverage_gate_wiring.enforce_coverage_gate_before_audio(...)` call right after the UDAC guard at the single shared dispatch site (walk-invariant ⇒ both walks). PRESERVE: nothing evaluates when the flag is OFF (`if coverage_gate_active():` first).
- `enrichment_consumption.py:227/335` `slide_ordinal_from_locator` + the silent 0/>1 role-seed drop. CHANGE: none in that file; the `:335` drop is carried forward as the explicit `AnchorResolution.narration_ambiguous` signal that the receipt logs as `missing`.
- `storyboard_html_emitter.py` per-slide render. CHANGE: added additive `render_coverage_section(receipt_dict)` (empty/None ⇒ `""`, existing render byte-identical). PRESERVE: deterministic LF output; no `app.marcus` import (takes a plain dict — lane isolation).
- `voice_provider_text.py:267-350` R7 `audit_rhetorical_source_containment` (PROVIDED-BUT-UNWIRED). CHANGE: wired ONLY as the REPORTING caller in `coverage_receipt._derive_containment`. PRESERVE: the documented bag-of-words negation/comparator FN is DISCLOSED as `advisory_caveat`, never a green vouch.
- Block-mode confirmed: NONE of these paths are in `pipeline-manifest.yaml::block_mode_trigger_paths`; NO node/edge added; NO `digest_schema_version` bump. Stays out of the block-mode regime (AC9).

### Completion Notes List
- T1, T3, T4, T5, T6, T7, T9 landed GREEN + offline. T8 (live gpt-5 slice + ablated negative case) intentionally LEFT for the orchestrator (no live calls made here).
- Test results: 71 new offline tests pass across 5 suites (`test_source_point.py` 24, `test_coverage_annotation.py` 17, `test_coverage_receipt_and_gate.py` 18, `test_coverage_gate_wiring.py` 7, `test_coverage_report_and_regression.py` 6). Pre-existing `test_pedagogy_annotation.py` (46) + the g0/storyboard/udac slice (120) stay green — the additive G0EnrichmentResult field + the prune firewall break nothing.
- Keystone RED→green captured for the fail-loud gate wiring (ImportError → 7 passed) and for the offline segmenter (risk-floor RED → green).
- ruff: clean on all changed files. lint-imports: 14 kept / 1 broken — the only broken contract is the PRE-EXISTING C3 `app.specialists.workbook_producer.graph -> app.gates.resume_api` (unrelated to coverage; the "only pre-existing C3 permitted" allowance). Verified pre-existing via `git stash`.
- The 4 failures seen only in a wide `-k` batch (`test_fit_report_*`, `test_coverage_manifest_json_schema_parity`, `test_g0_poll_surface_dsl_registration`) were confirmed PRE-EXISTING on the clean stashed baseline (3 are FileNotFoundError on a missing top-level `marcus/lesson_plan/schema/*.json`; 1 is an xdist import-ordering-sensitive self-registration audit that also fails in the baseline batch). None touch coverage code.
- Spec ambiguity / judgment calls: (a) the byte-identical firewall vs the "rides G0EnrichmentResult like P2/P3" instruction — resolved by the prune-when-empty `to_card_payload` (above). (b) The coverage pass attach into `build_enrichment_result` is intentionally NOT wired yet — the FIELD exists (AC9) so the layer CAN ride; the orchestrator flips a pass flag at T8 to populate it, keeping flag-OFF byte-identical. (c) `must_cover` derived deterministically as `verbatim_required ∨ detail_in_narration-intent` (and never for an operator-signed exclusion) — the AC8 gate input.
- ZERO live/network calls confirmed: every live leg is `# pragma: no cover - live leg`; only offline + canned-fixture paths exercised. Working tree left DIRTY + GREEN for orchestrator review + the T8 live slice. Status NOT set to review; NOT committed.

### File List
New (source):
- `app/marcus/lesson_plan/source_point.py` (T3 models + child-id helpers + derived intents + verbatim floor)
- `app/marcus/lesson_plan/coverage_annotation.py` (T4 segmentation + intent pass; offline + gpt-5 live leg + canned-fixture parse/build)
- `app/marcus/lesson_plan/coverage_receipt.py` (T5 derived two-axis receipt + vouch render-gate + R7 reporting caller + plan view)
- `app/marcus/lesson_plan/coverage_gate.py` (T6 pure fail-loud gate + `CoverageAssuranceError`)
- `app/marcus/orchestrator/coverage_gate_wiring.py` (T6 env flag + disk-primary receipt I/O + both-walks seam-callable)

Modified (source):
- `app/marcus/lesson_plan/g0_enrichment.py` (AC9 additive `coverage_annotations` field + byte-identical-firewall prune in `to_card_payload`)
- `app/marcus/orchestrator/production_runner.py` (T6 flag-gated coverage-gate call at the shared dispatch seam)
- `app/gates/section_07c/storyboard_html_emitter.py` (T7 additive `render_coverage_section`)

New (tests + fixture):
- `tests/unit/marcus/test_source_point.py`
- `tests/unit/marcus/test_coverage_annotation.py`
- `tests/unit/marcus/test_coverage_receipt_and_gate.py`
- `tests/unit/marcus/orchestrator/test_coverage_gate_wiring.py`
- `tests/unit/marcus/test_coverage_report_and_regression.py`
- `tests/fixtures/coverage/live_segmentation_response.json` (canned gpt-5 response for the offline live-parse test)
