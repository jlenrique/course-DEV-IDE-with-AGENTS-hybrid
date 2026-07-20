## Deferred from: code review of migration-1-1a-runtime-substrate-environment-and-dependencies (2026-04-22)

- Broader repo bootstrap docs still point clean installs at `requirements.txt`, which does not include the migration-only `import-linter` tool. This is outside Story 1.1a's acceptance-command path and should be resolved as a separate hybrid bootstrap/docs alignment task.


## Deferred from: code review of trial-3-five-fix-batch (2026-06-11 batch; reviewed 2026-06-11)

- [blind] cd31b33 commit-hygiene defect: "PURE EXTRACTION ... suite run UNMODIFIED" proof claim is contradicted by the same commit (irene_pass1 roster change + modified tests/integration/marcus/test_run_summary_yaml_emit.py). Commits are pushed; remediation is process-tier — record at Trial-3 postmortem as a P-tier anti-pattern candidate (commit-message proof claims must be verifiable against the commit's own diff; roster change deserved its own commit).
- [edge] Per-segment trace-fixture/cost-report rebuild drops prior segments' pre-gate-Marcus runs (production_runner.py:1214-1217 rehydrates child_runs from contributions only; pause/completion overwrite trace-fixture.json + recompute cost with history=[]). Cumulative trial cost under-counted across pause cycles — relevant to the <=$3.00 trial criterion. Fold into `trial-3-pause-write-sequence-atomicity` redesign (same persistence-sequence surface).
- [blind] `specialist_calls` semantics fork between _pause_at_gate callers: start walker passes segment-local counter, resume walker passes len(production_envelope.contributions) (cumulative). _has_production_evidence can report live-call evidence from prior-segment contributions on a zero-call resume segment. Fold into `trial-3-max-specialist-calls-segment-cap-semantics` design story (same counter surface; needs the cap-semantics design decision first).
- [blind] Offline gate-traversal block now duplicated in resume branch (pending/pre_fill/child_runs-append reimplemented; same sequence lives in _pause_at_gate and start walker offline branch) — the A23 fork-at-function-granularity pattern the extraction was meant to kill. Refactor follow-on at next runner-touching story.
- [blind] TW-7c-4 PERMITTED_PYTHON_DIFFS grew +9 paths across three commits with author-written self-certifying rationale and no sunset mechanism. Governance observation for Epic-34/Trial-3 retrospective: tripwire allowlist needs an expiry/review discipline or it converges on a no-op.
- [edge] Composer >=1-primary invariant is corpus-level but section-02a-composer.j2 decides one file at a time — zero-primary directive still emittable on tie/degenerate corpora (README/url-list-only). Already-acknowledged residual of the bb81b6f fix; compose-time aggregation check is the named follow-on; operator G0 eyeball + wrangler fail-loud are the current backstops.


## Deferred from: code review of spec-phantom-delta-silent-audio-gap (2026-06-12)

- [edge] G5 `narration_segments` pass-through branch (quality_control_dispatch.py run_g5_grounding early return) bypasses phantom detection entirely: a legacy/direct payload carrying an empty-text segment still counts its slide as covered (run_g5_checks counts coverage by slide_id regardless of text). Same silent-gap family; pre-existing; spec fenced the fix to the join path. Candidate fold: count coverage only for non-empty-text segments at next G5-touching story.
- [edge] Enrique non-join branches (`segments` payload key + locked_manifest_path/manifest_path) still silent-skip empty-text rows in the TTS loop (`if not text: continue`). Pre-existing; spec "Ask First" fenced. Same silent-gap family; fold with the row above.
- [blind] Join id-truthiness policy collapses falsy delta ids (0/""/None) to "" (narration_join.py line 39 pre-existing; phantom helper mirrors it for consistency). Revisit with the dp-v2 segment-manifest schema rework alongside b-manifest-join-lossiness (same policy home).
- [edge] G5 emits no verdict-level signal when a dropped phantom's slide is covered by another real segment (witness key `phantom_segment_ids_dropped` records it in the grounded payload; enrique refuse guards the live path at node 12). Consider escalating to a G5 advisory entry at next G5-touching story — would change verdict shape, needs its own ceremony.


## Deferred from: code review of spec-dp-v1-2-hygiene-mini-batch (2026-06-12)

- [edge+blind] Ninth-seam inline-roster regex (tests/audit/test_no_silent_fixture_fallbacks.py) does not match multi-key or multi-row literal rosters; live near-instance exists at app/specialists/gary/_act.py:95 (two-key fabricated roster on the empty-input path, module NOT on ALLOWED_FIXTURE_MODULES). Widen the regex WHEN gary re-bases (taxonomy re-base slice, gary first) — widening now would fire on gary before his fix lands.
- [auditor] quinn_r residual dead subtree one level down: _act_precomposition/_act_postcomposition (+ transitively _invoke_quinn_r_llm, _assemble_quinn_r_prompt) lost their only caller (_run_gate_phase, deleted this batch) yet remain __all__-exported with zero test imports; live act body (quinn_r/_act.py) calls validators directly. Next quinn_r-touching story: either delete the subtree + __all__ rows or document why the export surface stays.
- [blind] _require_bundle_path enforces presence, not run-scopedness — an explicit repo-root bundle_path (".", "runs/enrique-narration") still writes outside a run dir. Callers own scoping today (act() injects); revisit if a non-act caller appears.


## Deferred from: code review of spec-taxonomy-rebase-live-path (2026-06-12)

- [edge MEDIUM] BuilderInputError (app/marcus/orchestrator/package_builders.py:44, plain RuntimeError, on the remaining-13 exclusions) is raised by run_builder_node — the ONLY live-walk dispatch call site NOT wrapped in except SpecialistDispatchError (production_runner.py:1332/:1771). Node-06 starvation still KILLS the trial while node-07 starvation now error-pauses. Sharpens next-tranche priority: BuilderInputError first, paired with wrapping run_builder_node in the error-pause family.
- [blind] Ninth-seam regex in-genus escapes remain: key-order evasion ([{"prompt": p, "slide_id": "s1"}] — slide_id not first key) and comprehension fabrication. Next ratchet turn; current pattern has zero app/ false positives, widening further needs a false-positive analysis.
- [edge LOW] gary act() routing: prompt-only payload (no slides) now routes into generate_gamma_variants and refuses unconditionally — a lane that can only fail. Retire prompt-only routing or document, at next gary touch. Related: {"slides": []} at act() refuses in the directive lane (GammaDispatchError missing-input), not via gamma.slides.starved.

  > **CLOSED 2026-06-17 (WAVE-0 tranche 2):** the [edge MEDIUM] BuilderInputError bullet above is RESOLVED — re-based + both call sites wrapped (spec-taxonomy-rebase-tranche-2). Node-06 starvation now error-pauses recoverably.


## Deferred from: code review of spec-taxonomy-rebase-tranche-2 (2026-06-17)

- [edge] error-pause evidence-flag inconsistency: `_pause_at_error` (production_runner.py:1148-1152) computes `_has_production_evidence` from the per-segment `specialist_calls` counter, whereas the gate-pause path passes `len(production_envelope.contributions)`. On a recover segment that re-enters §06 and immediately starves (zero dispatches this segment), the paused envelope records `production_clone_launch_evidence=False` even though prior cycles produced real LLM contributions — inconsistent evidence verdict between a gate pause and an error pause at the same trial point. **Pre-existing shared-helper convention (every error-pause caller passes the per-segment counter); NOT introduced by tranche 2.** This is the SAME finding already filed under the trial-3-five-fix-batch review (`specialist_calls semantics fork between _pause_at_gate callers`) — folds into the `trial-3-max-specialist-calls-segment-cap-semantics` design story; changing it touches all error-pause callers on a frozen engine, so out of tranche-2 scope.

## Deferred from: code review of spec-p2-3-pass2-consumes-perceived-visuals (2026-06-20)

- [edge+blind] Duplicate-handling asymmetry in Pass-2 grounding: `_slide_briefs_by_slide` (graph.py:201-212) silently first-wins on duplicate slide_id and the Gary roster loop (graph.py:124-133) emits duplicate rows, whereas `_perception_artifacts_by_slide` (graph.py:171-198) fail-loud raises on duplicate perception slide_id. Inconsistent policy → potential prompt-byte non-determinism IF upstream `slide_briefs`/`gary_slide_output` order is non-deterministic. Brief is now demoted context; upstream (package_builder/gary) emits ordered slides; no evidence of actual dup slide_ids. Low-stakes; harmonize duplicate-handling policy in a future Pass-2 robustness pass.
- [blind+edge] Perception `slide-id map` input branch (graph.py:171-177) discards the outer map keys and rebuilds the mapping purely from each artifact's inner `slide_id`; no validation that map-key == inner slide_id. A map keyed `s1` carrying inner `slide_id=s2` silently attaches to s2 (s1 → UNVERIFIED). Defensive path only — the vision node emits a LIST in production, so this branch is untested/unexercised. Add map-key==inner-slide_id validation if/when the map form is ever produced.
- [edge] `project_rich_perception_for_authoring` (pass_2_template.py:108) raises ValidationError when a legitimately-shaped rich artifact has both `source_png_path` and `artifact_path` empty (minimal model `source_image_path` has min_length=1 + PNG pattern). NON-runtime path (used only in tests/exports; never wired into `_act_pass_2`), so the "minimal envelope cannot become runtime grounding source" guarantee is intact — but the projection helper is brittle. Harden if the projection is ever used on operator-supplied artifacts.

## Deferred from: code review of canonical-arc-s1-cd-styleguide-resolution-emission (2026-07-06)

- irene-pass1 04A runner branch shares the directive parse hazard (`_gamma_settings_from_directive` unguarded yaml/decode errors crash instead of error-pausing) — pre-existing; same fix family as S1's T1 patch; own small story.
- `tests/composition/test_texas_to_cd_chain.py::…accumulates_envelope[trial_id0]` (BundleDispatchError: missing directive_path, Texas-internal) + `tests/composition/test_slab_7a_opener_composition_smoke.py` (ModuleNotFoundError: directive_composer) — pre-existing REDs verified identical at HEAD f00e3468 in a clean worktree; not S1-caused.
- Pick-time `styleguide_picker_provenance.ssot_sha256` vs resolution-time `bound_guides.ssot_digest` cross-check — deliberately NOT S1 scope; it is the S3 parity comparator's designed job.

## Deferred from: code review of canonical-arc-s3-gary-shadow-parity (2026-07-07)

- **S4 spec-time design decision — parity-clock attestation strength (Edge lane E4):** `clock_eligible=True` currently accrues on two-way digest matches where `trial_start_directive_digest` is None (gateless/`pause_at_gates=False` starts; single-file trials where `start_trial` writes `directive_digest: null`). This is F-702-letter-compliant and the SPOC product path always writes the attestation (`start_trial` → trial-start.json before any §07 dispatch), but the S4 FAIL-LOUD spec author must decide whether the S-flip parity clock requires the full three-way attestation or the two-way match suffices. Route: S4 spec §clock semantics.

## Deferred from: code review of spec-gamma-single-slide-png-title-match (2026-07-08)

- [edge] Empty `expected_slots` + lone PNG returns empty success (matched/unmatched empty); zip with orphan pages would surface unmatched_pages. Pre-existing empty-slots caller contract; fold if a caller ever materializes with zero briefs.
- [edge] Empty/opaque 1-page ZIP still title-match-only (no cardinality override) while equivalent lone PNG binds — intentional "zip unchanged" asymmetry; revisit only if live Gamma starts returning 1-page zips for single-card decks.
- [blind] No `generate_gamma_variants` integration test with opaque `gary_A.png` download; materializer unit tests cover the live shape. Optional follow-on at next Gary export touch.

## Deferred from: code review of spec-irene-literal-supersedes-styleguide-truncation (2026-07-09)

- [blind] Unknown/mistyped `fidelity` silently demotes to creative (spec Always: missing/unknown → creative). Fail-loud on typos is an Ask-First / follow-on if Irene emit hygiene needs it.
- [blind] No shared PlanUnit Pydantic `fidelity` field — dict path only this slice (spec Ask First). Honor path stays dark until Irene emits the key.
- [blind] Top-level receipt still exposes `generation_id: calls[0]` while mixed/A-B makes multiple Classic calls; per-row `generation_id` is correct. Receipt-shape follow-on if spend/recover tooling needs all ids.
- [blind] Studio + any literal hard-fails the whole variant (spec Always). Creative-only Studio / per-slide Classic split is Ask First / out of scope.
- [reject→defer note] Binary cohorting groups non-contiguous creatives into one Gamma call — intentional per binary-cohort design; adjacency restyle risk accepted; revisit only if live decks show island restyle defects.
- [edge] Mixed-cohort slides lacking `slide_id` can still synthesize colliding `slide-01` ids across cohorts if both cohorts start index at 1 — patched generation_id mapping; unique-id refuse before partition remains optional hardening.


## Deferred from: green-light of spec-irene-pass1-fidelity-emit-recovery (2026-07-09)

- [follow-on] `literal-visual-production-streamline` — brainstorm + design a less-cumbersome production path for `literal-visual` slides under the styleguide regime (rebrand PNG / §06B / URL injection). Filed in `_bmad-output/planning-artifacts/deferred-inventory.md`. Not in this slice; emit ≠ production.

## Deferred from: code review of spec-irene-pass1-fidelity-emit-recovery (2026-07-09)

- [edge] Refinement carry of fidelity is prompt-only: if the model drops recognized tags on a refinement pass, normalize does not merge them back from the incoming plan. Spec Always asks carry-forward via prompt; a deterministic merge backstop is a follow-on if live refinements strip tags.
- [blind] Soft-omit of unknown fidelity values is intentional (spec Always); fail-loud on typos remains Ask-First / sibling of the prior Gary-path defer.

## Deferred from: adversarial review of spec-fix-llm-execution-config-docstring (2026-07-10)

- [hardening] The 2026-07-10 operator binding (vision batch model MUST equal realtime; never `gpt-4.1-*` as product default) is prose-only — no validator enforces it. `_require_vision` in `app/runtime/llm_execution_config.py` only checks a batch profile exists; a config setting `batch.model: gpt-4.1-mini` loads cleanly (only guard is a value-pin test). Natural home: model validator asserting `vision.batch.model == vision.realtime.model` or rejecting `gpt-4.1-*`. Also note `batch_model_fallback_family` is declared+tested but consumed by zero production code (`batch_route.py` submits `profile.model` verbatim; no rejection detection / auto-substitute) — implement or document-as-policy decision rides with this hardening.
- source_spec: `_bmad-output/implementation-artifacts/spec-lesson-plan-json-cli-flag-docstring.md`
  summary: CLI-started trials always record `lesson_plan_selection_source: null` — `_StartSelection.selection_source` is computed (trial.py ~699/721/726) but never threaded into `start_trial`; only the programmatic seam writes the receipt field.
  evidence: Review pass 2026-07-11; `selection_source_receipt` written only at trial.py ~417/421; `start_trial_cli` passes no selection_source; consumed by bank_mine_integrated_e2e_liveproof.py:402.
- source_spec: `_bmad-output/implementation-artifacts/spec-lesson-plan-json-cli-flag-docstring.md`
  summary: When a programmatic caller passes BOTH `lesson_plan_collateral_intent_path` and `lesson_plan_collateral_receipt_path`, the receipt path is recorded as provenance even though the intent path resolved selection (trial.py ~437-438 → ~608-612).
  evidence: Review pass 2026-07-11; `lesson_plan_receipt_path = intent_path or receipt_path` ordering vs record key semantics.
- source_spec: `_bmad-output/implementation-artifacts/spec-lesson-plan-json-cli-flag-docstring.md`
  summary: The documented "start_trial re-read seam never fires on CLI invocations" property is pinned by no test or assertion — drift-bait if a future CLI change passes `lesson_plan_collateral_intent_path`.
  evidence: Review pass 2026-07-11; integration tests exercise the seam directly, none pin the CLI-bypass property.
- source_spec: `_bmad-output/implementation-artifacts/spec-malformed-plan-json-selection-negative.md`
  summary: The sniff's exception-swallow arm (trial.py ~413-415, OSError/UnicodeDecodeError/YAMLError → raw=None → intent-loader route → loader raises) has no routing-observed test; a regression re-raising from the sniff would change error type/message unpinned.
  evidence: Review pass 2 (2026-07-11); loader-level error arms are pinned but the sniff-level swallow-then-reroute is not.
- source_spec: `_bmad-output/implementation-artifacts/spec-empty-companions-smoke.md`
  summary: Design question — should empty-but-present planning companions ({} / no-usable-framing) WARN or fail instead of the current silent treat-as-absent (planning_context.py:383-385)? An operator who authored placeholder JSON gets no signal that their companions bound nothing.
  evidence: Investigation + pins 2026-07-11; current behavior is explicit design (comment at the return site) and now test-pinned as no-phantom-framing; changing it is an operator/party disposition, not a dev-auto call.
- source_spec: `_bmad-output/implementation-artifacts/spec-empty-companions-smoke.md`
  summary: Companion JSON saved with a UTF-8 BOM (utf-8-sig, common Windows editor default) is rejected as "malformed JSON" — a healthy operator-ratified file pauses the run. Candidate fix: read with encoding="utf-8-sig".
  evidence: Review pass 2026-07-11, empirically probed; planning_context.py _read_json reads strict utf-8.
- source_spec: `_bmad-output/implementation-artifacts/spec-empty-companions-smoke.md`
  summary: Non-string truthy purpose/audience values ({"purpose": 42}) are str()-coerced into phantom framing ("42") threaded to Irene — the exact fabrication class this residual guards against. Candidate fix: isinstance type-guard like source_assessment has.
  evidence: Review pass 2026-07-11; planning_context.py ~123-124 coerces without a type check.
- source_spec: `_bmad-output/implementation-artifacts/spec-empty-companions-smoke.md`
  summary: A nonexistent run_dir (typo'd runs_root/trial_id) at the runner seam returns None silently — ratified framing dropped with no signal, indistinguishable from legitimately-absent companions.
  evidence: Review pass 2026-07-11; planning_context.py ~333-336 treats missing dir as absent-files.

## Deferred from: code review of 38-3a-research-packet-consume-side (2026-07-14)

- [edge] Signed percentage surfaces such as `-5%` currently lose their sign in the shared figure-token neck and can compare as positive percentages. This behavior predates Amendment 8; address as a separate fidelity-hardening slice with explicit signed-number semantics.
- [edge] Leading-decimal percentage surfaces such as `.5%` currently suffix-match as `5%`. This behavior predates Amendment 8; address with signed/decimal token-boundary hardening rather than broadening the live-run correction.

- source_spec: `_bmad-output/implementation-artifacts/spec-38-3a-lo-overlay-bridge-fix.md`
  summary: Pin the G0 enumeration-provenance locator shape contract at the producer (corpus-relative posix, no case/unicode variance) so the exact-equality authority join has a specified upstream.
  evidence: T4 Blind Hunter — the join's locator side is unvalidated free text from the enrichment card; the consumer deliberately joins by exact equality (spec W2), so shape discipline belongs at the G0 producer, not the workbook consumer.

- source_spec: `_bmad-output/implementation-artifacts/spec-38-3a-lo-overlay-bridge-fix.md`
  summary: Harden read_slide_authority_map so pathological input (e.g. RecursionError from deeply nested JSON) is funneled into SlideAuthorityInvalidError like the rest of its failure envelope.
  evidence: T4 Edge Case Hunter — json.loads can raise RecursionError, which escapes the reader's OSError/ValueError catch and would crash every caller (workbook_wiring + the 07W bridge seam); pre-existing reader behavior, not caused by this story.

- source_spec: `_bmad-output/implementation-artifacts/spec-38-3a-pass1-head-self-parent-normalize.md`
  summary: Cover the Pass-1 REFINEMENT path against the head-self-parent live-variance tic — _validate_raw_refinement_identity runs BEFORE normalize_clusters, so the same model shape on a plan-refinement pass red-rejects as "changed immutable parent_slide_id"; consider normalizing the raw payload before the identity check (same provably-empty predicate) plus a parse-path seam test through _normalize_decoded_pass1_response.
  evidence: T4 Blind Hunter on the 38-3a normalization diff — _act.py ~L1217 ordering (identity check precedes normalization); not on the governed workbook run's critical path (delegated HIL policy never triggers Pass-1 refinement), so deferred rather than batched.

- source_spec: `_bmad-output/implementation-artifacts/party-closure-record-38-1-38-3a-2026-07-15.md`
  summary: ✅ RESOLVED 2026-07-15 EVE — LO shippability bar folded into `_assert_completed_workbook_deliverable` (`_assert_lo_overlay_conformant`): structured lo_overlay_loss record refuses with named objectives (real a940c5eb REFUSES 6/6; 8b275e5b PASSES); MD floors for callout/placeholder desync; 4 pins incl. verbatim negative witness (closure rider M-R3).
  evidence: Closure-party Murat — the verdict-honesty check asserts presence + basic conformance only; the J-A bar for trial 8b275e5b was verified by human audit. Resolved before governed run A so the bar machine-asserts every learner-facing section.

- source_spec: `_bmad-output/implementation-artifacts/party-closure-record-38-1-38-3a-2026-07-15.md`
  summary: BINDING RIDER (M-R2) on the earlier Pass-1 refinement-path defer — the refinement-identity normalization gap must ride into the NEXT Pass-1-touching story's T1 readiness reading, not sit passively in this register.
  evidence: Closure-party Murat — the same live-model tic that froze witness 5ee9ac39 red-rejects on any plan-refinement pass because _validate_raw_refinement_identity runs before normalize_clusters.

- source_spec: `_bmad-output/implementation-artifacts/party-closure-record-38-1-38-3a-2026-07-15.md`
  summary: Workbook exercise path variance + answer leakage — 8b275e5b rendered 6 knowledge-check-lifted exercises (vs 13 authored per-unit on a940c5eb) and 2 prompts carry their Correct Answer inline before the Answer Key; adjudicate fix-induced vs live variance at the epic-38 retrospective and file the answer-strip fix (Epic 39 grooming).
  evidence: Closure-party John F2 — direct diff of the two passing runs' rendered workbooks.

- source_spec: `_bmad-output/implementation-artifacts/37-2b-deep-dive-enrichment-cited.md`
  summary: Scope B5 figure-supplement clearing to the section that proved the figure — today deep-dive (and research/glossary/trends) supplements are a GLOBAL normalized-token set, so a numeral proven cited in one section also clears an identical unsourced numeral anywhere in the workbook body.
  evidence: T4 Blind Hunter on 37-2b — consistent with the existing B5 design (research titles/trends already union globally), so deferred as a design-level hardening for the next fidelity-audit batch rather than patched piecemeal.

- source_spec: `_bmad-output/implementation-artifacts/37-2b-deep-dive-enrichment-cited.md`
  summary: Populate excluded_citation_ids from 38.1 — Ask-A records credibility exclusions by raw row index and never mints citation ids for excluded rows, so the gate's excluded-vs-invented distinguishability (amendment M2a) is fixture-only until 38.1 mints ids for excluded rows.
  evidence: T4 Blind Hunter on 37-2b — upstream 38.1-side enhancement; the gate field + distinguishable row exist and are mutation-tested; production packets carry an empty list today.

- source_spec: `_bmad-output/implementation-artifacts/39-1b-exercise-merge-composition.md`
  summary: Full-tree serial suite carries ~325 inherited reds at baseline 6edf563e (manifest G0R fold/schema pins, tests/test_progress_map.py, production-runner/Gary integration fixtures with Pass-1 authority-receipt drift, styleguide/irene wiring modules, the known cost-tile red) — the per-story "suite green" claims are scoped batteries + witness replay, not full-tree green. Needs its own attribution/repair arc (likely fixture drift from the G0R gate + Pass-1 authority-receipt regime landings).
  evidence: 39-1b dev-cycle attribution 2026-07-16 — full default suite 199 failed under xdist, 195 serial; clean baseline worktree at 6edf563e reproduces the same set with the 39-1b diff absent (0 new failures attributable); details in the story Debug Log.

- source_spec: `_bmad-output/implementation-artifacts/evidence/workbook-live-hil/run-a-preflight-authorization-2026-07-16.md`
  summary: 07W.3 enrichment-writer shape hardening (BLOCKS run-A attempt 3) — the live writer emitted claims missing required fields (role/source_claim_refs) on a long (11-section) lesson; normalizer-v2-class fix required, PLUS a party ruling on failure semantics: should writer-output-invalid degrade honestly (typed recorded loss, enrichment=degraded, walk continues to 07W) instead of error-pausing and stranding the paid trial into the PARK trap? The Option B PARK policy makes every 07W.3 hard failure terminal for the trial — the degrade path would convert enrichment failures from trial-killers into visible honest losses (enrichment is an enhancement, not a walk-blocker). Interacts with the parked `07w3-provider-failure-journal-archive-recovery` design item.
  evidence: run-A attempt 2 (648de559) 2026-07-16 — full pydantic error frozen in runs/648de559.../error-pause.json; the richer 64k G0 extraction (801135a5) produces longer lessons than every prior 07W.3 witness, so this variance class will recur.

- source_spec: `_bmad-output/implementation-artifacts/40-1-cover-placeholder-hero-toc-provenance.md`
  summary: 40-1 T4 low/info hardening follow-ons (finding 1 MEDIUM fixed in-session): (2) bar does not parse the learner-visible art-brief pointer line (ghost filename/digest shown to learner passes); (3) receipt art_brief.filename not validated as bare basename (path-confusion door); (4) _identity_line mislabels ok-but-empty corpus_path; (5) hero ![ scan is Cover-section-only; (6) dangling-symlink run.json takes tolerance branch (is_file before is_symlink asymmetry); (7) dead continue after _refuse x2 in the cover clause; (8-party) rendered "Course corpus:" carries an absolute local path w/ username (J-1 tension) + Scene paragraph as theme #1 duplicates paragraph-length alt-text; duplicate NON-cover-H2 fail-loud unpinned.
  evidence: 40-1 combined T4 review 2026-07-16 (diff 681eddfb..6c6ef653) — module survives M-D3-2b; none gate the status flip.

- source_spec: operator-feedback (Juanl, live run ffa19af3, 2026-07-16)
  summary: Rename the G2B HIL surface from "Variant Selection" to "Style and Variant Selection" across HUD/decision-card/docs vocabulary — the surface couples style-slot picks (A/B treatments, each with its own styleguide) with per-slide variant selection, and the current name undersells the style half.
  evidence: Operator naming directive issued during the C1M1-P1 concierge run; pairs naturally with the hud-pre-run-settings-confirmation-surface requirement (deferred-inventory).

- source_spec: live trial 1bc3bc4e (C1M1-P1 concierge run, 2026-07-16)
  summary: LO-refinement adequacy followup normalization (BLOCKS resuming trial 1bc3bc4e and recurs on any live LO-refinement) — the live refinement model decorates AdequacyFollowup literals with annotations ("external-content-expected: expect a separate guide or workbook") and the strict parse at app/marcus/lesson_plan/irene_refinement.py L556 (SourceAdequacy.model_validate(row["adequacy"])) refuses, stranding the G0E->G0R continuation. FIX DESIGN (variance-first seam, normalizer-v2 class): normalize suggested_followups pre-validate — truncate entries prefix-matching a known literal (optionally followed by ':' / whitespace annotation) to the bare literal; DROP unknown entries with logger.warning (field is advisory-by-contract, "Never an action"). Add a parse-seam test with the witnessed decorated shapes.
  evidence: trial 1bc3bc4e resume output (pydantic literal_error on suggested_followups.1/.2); AdequacyFollowup literal at learning_objective.py L116.

- source_spec: live trials ffa19af3 + 1bc3bc4e (2026-07-16)
  summary: Corpus-shape validation belongs at pre-flight/plan-time — a slides/-less corpus leaf passed PR-PF, plan-dialogue, G0, and THREE gates before Irene Pass-1 refused it at node 04A (source.bundle.metadata-invalid: no primary slide rows). Add a corpus-shape check (slides/ presence + per-slide parse floor) to PR-PF and/or the plan-dialogue corpus intake so shape errors surface at minute one, not node 13.
  evidence: trial ffa19af3 error-pause.json; the proven corpus convention at course-content/courses/tejal-apc-c1-m1-p2-trends/.

- source_spec: live trial 3b1a9f5a (2026-07-16)
  summary: HUD stale-instance collision — a manually relaunched HUD holding port 8791 (bound to a dead trial) made the NEXT trial start fail pre-flight (hud-server-healthz=fail) with no hint about the foreign instance. The start pre-flight should detect a live-but-foreign-nonce HUD on the port and say so (or reap/supersede it); pairs with the hud-pre-run-settings-confirmation-surface requirement.
  evidence: trial 3b1a9f5a start refusal; manual HUD relaunch precedent earlier the same session.

- source_spec: session observation (2026-07-16)
  summary: Run-registry root inconsistency — the trial CLI defaults runs to state/config/runs/ while the governed runner uses runs/ (and plan-dialogue writes companions to runs/<uuid>/); monitors/evidence tooling aimed at the wrong root silently see nothing. Unify the default or surface the effective root in the start payload prominently.
  evidence: ffa19af3/1bc3bc4e registered under state/config/runs/ vs 648de559 under runs/.

- source_spec: live production trial bc747b51 (C1M1-P1 Marcus-SPOC, 2026-07-16) + operator directive mid-G0E
  summary: Bundle of HIGH operator-surface requirements for post-trial code — (1) `hil-operator-surfaces-must-be-tabular` — CLI/HUD/SPOC HIL review must use tables/containers (G0 dump + enrichment log sheaf failed reviewability; chat tables worked as exemplar); (2) `hud-lifecycle-survives-gate-pause` — HUD disconnected when trial start returned at G0E pause (8791 dead); keep HUD alive across pauses; (3) reaffirm `hud-stable-public-live-url` — public read-only page, any computer, unchanging URL; (4) expand `hud-pre-run-settings-confirmation-surface` — HUD must standing-show all ~14–16 run-defining toggles (not thin modalities slice) plus pre-walk confirm/change. Full capture + acceptance checklist + toggle table in evidence note.
  evidence: `_bmad-output/implementation-artifacts/evidence/operator-hil-display-requirements-2026-07-16.md`; trial `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/` (g0-enrichment.json, operator-surface.json, terminal `c` CommandNotFound after JSON exit); deferred-inventory rows updated same day.

- source_spec: live production trial bc747b51 (G0R pause, 2026-07-16) + operator question on approve paste
  summary: `next-action-must-not-preselect-approve` — `build_next_action` hardcodes `--verb approve` for all paused-at-gate next_action strings; HUD/agents that paste it bias HIL toward Approve despite DecisionCard verbs approve|edit|reject. Emit neutral verb choice first; never a sole approve-prefilled resume as the implied next step.
  evidence: `app/marcus/cli/next_action.py` L71-79 (`" --verb approve"`); G0R card verb Literal in `app/models/decision_cards/g0r.py`; operator-surface next_action on trial bc747b51 at G0R; deferred-inventory row + evidence note §5.

- source_spec: live production trial bc747b51 (post-G1, 2026-07-16 WRAPUP) — BLOCKING next session
  summary: `cd-contribution-missing-before-06-builder` — node 06 error-paused `builder.gary.upstream-missing` (cd absent). Node 4.75 entered; no `cd` specialist contribution on envelope; irene_pass1 present. Diagnose why Creative Director path no-ops without fail-loud; fix so §06 never sees silent CD absence (emit contribution OR refuse earlier). Do not burn recover loops until root cause known.
  evidence: `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/error-pause.json` (message §06 builder missing upstream contribution(s): cd; node_id 06); run.json specialist_ids lack cd; trace-fixture has no cd dispatch; deferred-inventory row same id.

- source_spec: `spec-status-surface-consolidation.md`
  summary: `project-context-base-doc-slim` — the hand-authored base doc under `docs/project-context.md`'s `<!-- BASE-DOC -->` marker is ~111KB (the real payload glob-loaded into ~59 skills; the consolidation only removed the ~24KB addendum stack, so the context-window cost barely moved) AND still contains ~12 dated "Update (session NN)" chronology paragraphs (2026-07-02→07-08) that belong in history, not the hot base. Evict the dated chronology + decide whether to slim the 111KB base (e.g. migrate timeless reference into ONBOARDING). A real scoped decision, deliberately NOT folded into the structural consolidation pass (operator said "preserve base doc"). Party review: John J2 + Paige P1.
  evidence: `docs/project-context.md` base doc = 111,157 B (byte-identical to pre-consolidation base); ~12 `**YYYY-MM-DD Update (session NN…)**` paragraphs remain below the marker; the file is glob-loaded as a persistent-fact by ~59 skills (`file:{project-root}/**/project-context.md` in `.claude/skills/*/customize.toml`).


## Deferred from: Story Q1.4b — final-report projector (2026-07-19)

- source_spec: `q1-4b-final-report-projector.md` (AC6 / GL-10) — **R2 WITNESS OBLIGATION (checkable comparison, not an observation).**
  summary: `q1-4b-r2-final-report-projector-witness` — Q1.4b ships the deterministic projector `app/quality/report.py::render_scorecard_final_report(*, block, history, fence_state)` + goldens OFFLINE; the LIVE run-end wiring into `production_runner`'s operator surface is DEFERRED to the upcoming Operator/HIL **R2 trial** (per GL-10; `production_runner` is a pipeline-lockstep trigger path, deliberately untouched here). On R2: (1) capture `render_scorecard_final_report(...)` output for the run to a NAMED evidence artifact under the run dir (e.g. `state/config/runs/<trial_id>/quality-final-report.md`); (2) ASSERT it EQUALS the independently-computed env truth for that run — the **Band** read from `docs/quality/project-quality-scorecard.md` §1.6 and the **fence_state** recomputed from that run's actual env (`_build_fence_state` output in `run_summary.yaml`). A mismatch = a real projector/emit defect. Do NOT run a live trial to satisfy this story; it rides the already-planned R2 shakedown.
  evidence: projector + goldens landed (`app/quality/report.py`, `tests/quality/test_scorecard_final_report.py`); `production_runner` emit path UNCHANGED (verified: no diff to `app/marcus/orchestrator/production_runner.py`). Epic source: `epics-project-quality-scorecard-2026-07-19.md` §Story Q1.4 (E2E witness bullet) + GL-10.


## Deferred from: Story Q2.1 — cost-efficiency dimension (2026-07-19)

- source_spec: `q2-1-cost-efficiency-dimension.md` (AC6 / GL-10) — **R2 COST-POSTURE WITNESS OBLIGATION (checkable comparison, not an observation).**
  summary: `q2-1-r2-cost-posture-witness` — Q2.1 ships the cost_efficiency dimension + its signal readers (`app/quality/signals.py::{budget_stop_default_signal, cost_posture_signal, cost_drift_signal, cost_transparency_signal}`) + honesty pins OFFLINE, scored from the EXISTING economics emitters (GL-15). The per-run `cost_posture` FACT already rides Q1.4a's `fence_state` in `run_summary.yaml`; the LIVE end-to-end witness is DEFERRED to the Operator/HIL **R2 trial** (per GL-10; `production_runner`/`economics.py` are pipeline-lockstep trigger paths, deliberately untouched here). On R2: (1) capture the run's actual `cost_posture` from `run_summary.yaml::fence_state.cost_posture` AND its `TrialEconomicsReport` (`cost-report.json`); (2) ASSERT `cost_posture_signal(cost-report.json)["cost_posture"]` EQUALS the `fence_state.cost_posture` for that run (the two economics reads agree by construction — a mismatch = a real emit defect); (3) if the run set `MARCUS_TRIAL_BUDGET_USD`, assert the emitted `budget_status.state` matches `check_trial_budget(total, cap)` and that `budget_stop_default_signal()` still reports the PRESET default as opt-in (`weak`) independent of that opt-in. Do NOT run a live trial to satisfy this story; it rides the already-planned R2 shakedown.
  evidence: readers + dimension + pins landed (`app/quality/signals.py`, `docs/quality/project-quality-scorecard.md` §2, `tests/quality/test_cost_efficiency_dimension.py`, `tests/quality/test_scorecard_honesty_pins.py`); `production_runner`/`economics.py` UNCHANGED (no parallel plumbing — GL-15). Epic source: `epics-project-quality-scorecard-2026-07-19.md` §Story Q2.1 (E2E cost-posture witness bullet) + GL-10.


## Deferred from: Story Q2.2 — coverage-honesty dimension (2026-07-19)

- source_spec: `q2-2-coverage-honesty-dimension.md` (AC6 / GL-10) — **R2 COVERAGE-HONESTY WITNESS OBLIGATION (checkable comparison, not an observation).**
  summary: `q2-2-r2-coverage-honesty-witness` — Q2.2 ships the coverage_honesty dimension + its signal readers (`app/quality/signals.py::{coverage_fence_default_signal, coverage_receipt_honesty_signal, coverage_narration_obligation_signal, coverage_leak_count_signal}`) + honesty pins OFFLINE, scored from the EXISTING coverage emitters (GL-15). The LIVE end-to-end witness is DEFERRED to the Operator/HIL **R2 trial** (per GL-10; `production_runner`/`coverage_gate_wiring.py`/`coverage_gate.py` are pipeline-lockstep / coverage-runtime trigger paths, deliberately untouched here). On R2: (1) if the run set `MARCUS_COVERAGE_GATE_ACTIVE`, capture the run's `coverage-receipt.json` and assert `coverage_receipt_honesty_signal(<receipt>)` distinguishes the run's real PASS/FAIL/vacuous state (a vacuous receipt must not read as a clean pass) and `coverage_narration_obligation_signal(<receipt>)` matches the gate's blocking rows; (2) assert `coverage_fence_default_signal()` still reports the PRESET default as opt-in (`weak`) independent of any ambient opt-in (`default_coverage_enforced` tracks `coverage_gate_active()` when live); (3) a mismatch = a real coverage-emit/reader defect. Do NOT run a live trial to satisfy this story; it rides the already-planned R2 shakedown.
  evidence: readers + dimension + pins landed (`app/quality/signals.py`, `docs/quality/project-quality-scorecard.md` §3, `tests/quality/test_coverage_honesty_dimension.py`, `tests/quality/test_scorecard_honesty_pins.py`); coverage runtime (`coverage_gate_wiring.py`, `coverage_gate.py`, `coverage_receipt.py`, `production_runner.py`) UNCHANGED (no parallel plumbing — GL-15). Epic source: `epics-project-quality-scorecard-2026-07-19.md` §Story Q2.2 + GL-10.


## Deferred from: Story Q2.3 — fidelity-trust dimension (2026-07-19)

- source_spec: `q2-3-fidelity-trust-dimension.md` (AC6 / GL-10) — **R2 FIDELITY-TRUST WITNESS OBLIGATION (checkable comparison, not an observation).**
  summary: `q2-3-r2-fidelity-trust-witness` — Q2.3 ships the fidelity_trust dimension + its signal readers (`app/quality/signals.py::{semantic_fence_gating_signal, fidelity_trace_honesty_signal, fidelity_audit_honesty_signal, fidelity_leak_count_signal}`) + honesty pins OFFLINE, scored from the EXISTING fidelity emitters (GL-15). The LIVE end-to-end witness is DEFERRED to the Operator/HIL **R2 trial** (per GL-10; `source_fidelity_audit.py` / `vera/_act.py` / `production_runner.py` are fidelity-runtime / pipeline-lockstep trigger paths, deliberately untouched here). On R2: (1) capture the run's actual Vera fidelity trace(s) under the run dir (`state/config/runs/<trial_id>/fidelity/*-vera-*.json`) and assert `fidelity_trace_honesty_signal(<trace>)` distinguishes the run's real PASS/FAIL state — a critical Omission/Invention/Alteration (`_hard_fail` → `HALT-AND-REMEDIATE`) must NOT read as a clean fidelity; (2) assert `semantic_fence_gating_signal()` still reports the real `SEMANTIC_TRIPWIRE["gates_production"]` posture as WARN-only (`weak`) independent of any ambient state, and — if the run flipped the tripwire to gate production — that it reports `semantic_fence_gates=True` and FT1 earns `strong`; (3) a mismatch = a real fidelity-emit/reader defect. Do NOT run a live trial to satisfy this story; it rides the already-planned R2 shakedown.
  evidence: readers + dimension + pins landed (`app/quality/signals.py`, `docs/quality/project-quality-scorecard.md` §4, `tests/quality/test_fidelity_trust_dimension.py`, `tests/quality/test_scorecard_honesty_pins.py`); fidelity runtime (`source_fidelity_audit.py`, `vera/_act.py`, `irene/graph.py`, `production_runner.py`) UNCHANGED (no parallel plumbing — GL-15). Epic source: `epics-project-quality-scorecard-2026-07-19.md` §Story Q2.3 (FR9) + GL-10.
