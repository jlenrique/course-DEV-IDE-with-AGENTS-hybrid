# Codex Dev Prompt — P2-4c **S3** (triggered catalog-guided escalation tuple-delta call)

**Cycle:** NEW CYCLE — Codex T1–T10 + self-review → Claude T11. Do NOT commit/flip.
**Prereq:** **S1 + S2 merged first.** **Class S.** Branch `fidelity-perception-arc-2026-06-19`.
**Authority:** `spec-p2-4c-reading-path-tuple-refactor.md` (§0 v1.1, §5 S3, §6 G1/G3 [RESOLVED], §7) · `reading-path-patterns-catalog.md` v1.1 (§2 AXIS 5 callout_intent, §4.2 oppositional, §4.5 enumerated_process) · `reading-path-gap-resolution-G2-G3-2026-06-22.md` (BINDING) · memory `feedback_no_mocks_real_live_apis`, `feedback_operator_cost_not_constraint_run_gated_validation`.

## 0. BUILT-SUBSTRATE GROUNDING (post-S1/S2 close, refreshed 2026-06-23) — CONSUME, don't re-derive
S1 is DONE and S2 is finalizing; the escalation predicate must **consume the flags S1/S2 already emit on the `PerceptionArtifact`**, not re-implement detection:
- **S1 emits `reading_path_flags: list[ReadingPathFlag] | None`** — already carries `"oppositional_cue"` when the explicit opposition cue is present (S1 FLAGS, never upgrades — D1). So the predicate's **`opposition_cue_hit` = `"oppositional_cue" in (artifact.reading_path_flags or [])`** — do NOT re-run the lexicon (S1 owns it). (Guard: None-check `reading_path_flags` — it's nullable; see follow-on `reading-path-flags-none-guard`.)
- **S2 emits `image_role_flags: list[ImageRoleFlag] | None`** — carries `"tier_2_5_candidate"` and `"tier_3_quarantined"`. So the predicate's **tier-2.5/3 harvest-route hit = those flags present**; **`low_conf_role_elements`** = elements the S2 backfill left low-confidence / `role_tier is None` in the full-length `image_roles` (S2 MF-A fix makes `image_roles` index-aligned 1:1 with `visual_elements`, with `None` sentinels — consume positionally, None = unscored).
- **`derive_primary_name(macro_layout, text_substructure)`** (S1, pinned module) is the projection; S3's `layout_delta` (`two_pane`) re-derives the primary via this same function — do NOT set the primary name directly.
- **`image_role_scoring.py`** (S2) owns the κ/fold/quarantine; S3 does NOT re-score — it only emits `role_overrides` that S2's scoring later consumes.
- Tuple-disagreement subpredicate = deterministic `macro_layout`/`text_substructure` vs the perceiver-emitted `role_tier`/cadence already on the artifact.

## G3 resolution (party-ratified — BINDING)
**Default path needs NO third call:** S2 already emits `role_tier` + `callout_intent` on the perceiver's pixel call with the catalog inlined. **S3 is a TRIGGERED, single ≥gpt-5.5 catalog-guided call that returns a TUPLE-DELTA**, fired ONLY when the upstream predicate says the slide is ambiguous. It is NOT a standing per-slide call.

## Scope = S3 ONLY
The upstream escalation predicate + the `escalation_ledger` observable + the single triggered ≥gpt-5.5 tuple-delta call + the merge of its delta + the bounding tripwires + the retry-to-green fence. S3's delta jobs: **D1** oppositional refinement (`multi_column`→`two_pane`/`two_up_comparison` when an opposition cue is present), **D2** `callout_intent` labeling (unresolved cases), **D3** process-confirm (`enumerated_process` vs `peer_boxes`), and **role-override** for low-confidence / 2.5 / 3 tiers.

## Files in scope
- `scripts/utilities/reading_path_classifier.py` (or a new `reading_path_escalation.py`) — the predicate + ledger + delta-merge.
- A thin escalation client (reuse the house `ChatOpenAI`/cascade ≥gpt-5.5; NOT a new bespoke client) + a parse-seam for the structured tuple-delta.
- `app/specialists/vision/` only if the inline-catalog default-path prompt needs the catalog cues (coordinate with S2; do not re-do S2's role_tier work).
- Tests.

## DO NOT MODIFY
- S1 geometry / S2 tier logic except to CONSUME their outputs.
- Any scoring rule that puts `callout_intent` or tier-2.5/3 INTO the primary-key top-1 (they stay out — probation).

## Tasks (T1–T10)
**T1 — readings + baseline-diff attestation.**

**T2 — escalation predicate (deterministic, computed in S1/S2 pass, FROZEN before S3).** `escalate = (macro_margin < θ_macro) OR opposition_cue_hit OR callout_kind_present OR (numbered_present AND NOT transform_verb_present) OR (low_conf_role_elements>0) OR tuple_disagreement (deterministic-classifier vs perceiver-emitted) OR (artifact.confidence=="LOW" or confidence_score<τ) OR (any tier-2.5/3 candidate hit — harvest route)`. Each subpredicate individually unit-tested. Lexicons (`OPPOSITION_LEXICON`, `TRANSFORM_VERB_LEXICON`) in versioned files. **Thresholds (θ_macro, τ) start PERMISSIVE and are TUNABLE — do NOT hard-freeze; calibrate after Trial-1.** The rate they produce is what's under test, not the θ.

**T3 — `escalation_ledger.json` (always recorded, even when escalate=false — you need the denominator + the why-not).** Per slide: `{slide_id, escalate, subpredicates:{...}, fired:[...], trigger_reason}`. Escalation rate = count(escalate)/total.

**T4 — the single triggered S3 call.** ONE ≥gpt-5.5 catalog-guided call per escalated slide, returning a tuple-delta: `{layout_delta:{two_pane:bool}|null, callout_intents:[{element_id,intent}], process_kind:"enumerated_process"|"peer_boxes"|null, role_overrides:[{element_id,role_tier}]}`. The call receives `fired[]` and does ONLY the fired jobs; each delta field is null/empty when its subpredicate didn't fire (testable: S3 never volunteers a delta for an unfired question). No mocks — live gpt-5.5; recorded-real responses behind the parse seam ONLY, never a production-path fixture. Malformed/empty response → degrade to the S1/S2 label, COUNTED, never crash/mislabel.

**T5 — merge.** Apply the delta over the S1/S2 tuple. `two_pane` upgrade sets the oppositional primary name (D1). `callout_intent` populates the existing nullable field — **but stays OUT of the primary-key + full-tuple top-1** (probationary per-axis vector). `process_kind` corrects text_substructure (D3). `role_overrides` correct image_roles (2.5→2 fold + tier-3 quarantine still apply at scoring).

**T6 — bounding tripwires (paired RED, both mandatory):** (a) **over-escalation** — test FAILS if escalation_rate > 20% on the baseline fixture set ("secretly LLM-always" detector); (b) **zero-escalation** — test FAILS if rate == 0% on a fixture set containing ≥1 known-ambiguous slide (dead-code detector).

**T7 — retry-to-green FENCE (critical, RED-first):** escalation decided UPSTREAM on S1/S2 signals only and FROZEN before S3 runs; S3 is single-shot; **call-count assertion: S3 invoked EXACTLY once per escalated slide**; NO code path conditions escalation OR re-invocation on the gold label or on top-1 match. A test asserts no gold-label-conditioned escalation path exists.

**T8 — additive non-regression** (S1+S2+P2-4a green). **T9 — battery** (lockstep exit 0, ruff, lint-imports; a live ≥gpt-5.5 smoke on ≥1 genuinely-ambiguous slide proving the delta path end-to-end — operator-gated leg may be run per `feedback_operator_cost_not_constraint_run_gated_validation` via a fresh independent subagent, first-run-stands). **T10 — self-review + handoff** (`_codex-handoff/p2-4c-s3-ready-for-review.md`: per-AC evidence, escalation_ledger sample + rate, the paired-tripwire + call-count evidence, baseline-diff attestation, live-smoke transcript).

## Pass-bar (Claude T11)
Predicate frozen upstream + per-subpredicate tests; `escalation_ledger` emitted; paired over/zero tripwires green; call-count fence green (exactly-once); S3 = one live ≥gpt-5.5 call/escalated-slide returning a delta, parse-seam only (no production-path mock); `callout_intent` + tier-2.5/3 stay OUT of the primary-key scoring; malformed-response degrade-counted; S1+S2+P2-4a green. After S3: **P2-4b finalize** scores the built classifier's tuples vs the operator-confirmed held-out labels (primary-key top-1 ≥0.85 + per-axis vector; callout_intent + 2.5/3 excluded pending their harvests).
