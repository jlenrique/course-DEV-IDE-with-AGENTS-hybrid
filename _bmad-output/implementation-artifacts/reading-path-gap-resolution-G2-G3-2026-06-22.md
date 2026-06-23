# Reading-Path Gap Resolution — G2 + G3 (party-mode, 2026-06-22)

**Context:** P2-4c S2/S3 were gated on three implementation gaps (spec §6). G1 (peer-vs-oppositional) was already resolved by D1 (explicit-cue discriminator → S3). This record resolves **G2** (image-role tier-assignment rubric) and **G3** (ambiguity-escalation predicate) via a fully-spawned `bmad-party-mode` round — **Caravaggio, Amelia, Murat, Mary, Winston** — run in parallel with Codex's live S1 build (planning only; non-conflicting). **No impasse.** Binding on the S2/S3 Codex prompts.

## G2 — image-role tier assignment → PERCEIVER-PRIMARY + DETERMINISTIC GEOMETRY GATE/BACKFILL
Tier {1 decorative / 2 illustrative / 2.5 evidentiary / 3 instructional / 4 pointer} is a SEMANTIC judgment (decorative-diagram vs instructional-diagram is identical in pixels — only intent/traceability separates them). Resolution:
- **Perceiver-primary (Winston):** the perceiver already sees pixels + emits `kind` per element — it emits `role_tier` on the EXISTING call (no new round-trip) with the tier rubric INLINED into the perception prompt.
- **Eye-verb rubric (Caravaggio):** each element answers one question — feel→1 / glance→2 / glance-to-confirm→2.5 / **trace→3** / tag→4 — with cited referential-language evidence. Per-tier observable signatures defined (area/centrality/edge-bleed/text-overlap/internal-labels/icon-set/caption-adjacency).
- **Deterministic geometry GATES + backfill (Caravaggio + Amelia):** geometry rules tiers OUT and backfills. HARD-GATES: `icon AND area<5%`→LOCK tier 4; **`internal_label_count==0`→tier 3 RULED OUT** (the single gate that kills the kind:diagram-was-decorative bug, seen 4×); `edge_bleed AND text_overlaps_image AND no labels`→tier-1 prior. Amelia's `(tier, prior_conf)` table backfills when the perceiver omits `role_tier`; `None` = "perceiver not consulted" (never default to a tier).
- **Scoring + quarantine (Murat + Mary):** image_role is HALF the A6 primary key, so tier-stability gates the metric. LIVE scored tiers = **{1, 2, 4}**; **2.5 FOLDS→2**; **tier 3 QUARANTINED** (emittable + side-channel, excluded from scored top-1) — both promoted only on operator-confirmed exemplars. Gate: double-labeled **Cohen's κ≥0.6** on the 4-value folded set + a soft-middle {1,2} sub-κ≥0.6 (else fold further) + a **confusion-matrix artifact**. Provenance metadata per tier (`exemplar_count`, `sources`, `retest_marker`). Evidence ledger: {1,2,4} LIVE (reviewed-26 + held-out); {2.5,3} DORMANT/provisional (2.5 = zero exemplars, minted by review; 3 = unconfirmed, `12_Value-Prop-Canvas` is the promotion probe).
- **Harvest coupling (Mary):** 2.5/3 candidate-hits route to S3 escalation → the escalation log IS the promotion-evidence pipeline for the dormant tiers.

## G3 — escalation predicate + S3 architecture → INLINE-CATALOG DEFAULT + TRIGGERED TUPLE-DELTA CALL
- **No standing third call (Winston):** the catalog is small enough to inline into the perceiver's system prompt, so the default path (role_tier + callout_intent + self-confidence) rides the one pixel-seeing call. **S3 is a TRIGGERED separate ≥gpt-5.5 catalog-guided tuple-delta call**, fired only on ambiguity.
- **Predicate (Amelia + Winston), deterministic, computed upstream + FROZEN before S3:** `escalate = macro_margin<θ ∨ opposition_cue_hit ∨ callout_kind_present ∨ (numbered ∧ ¬transform_verb) ∨ low_conf_role_elements>0 ∨ tuple_disagreement(classifier vs perceiver) ∨ confidence==LOW/score<τ ∨ (tier-2.5/3 candidate-hit)`. θ/τ start PERMISSIVE, tunable; calibrate after Trial-1 (Mary — don't hard-freeze on unmeasured ambiguity rate).
- **One delta call (Amelia):** S3 returns `{layout_delta, callout_intents[], process_kind, role_overrides[]}`, does only the `fired[]` jobs, null for unfired. Merges over the S1/S2 tuple. Live gpt-5.5; recorded-real parse-seam only; malformed→degrade-counted.
- **Observable + bounded (Murat):** `escalation_ledger.json` always recorded; **paired RED tripwires** — over-escalation (FAIL if rate>20%, the "secretly LLM-always" detector) + zero-escalation (FAIL if 0% with a known-ambiguous slide, the dead-code detector).
- **Retry-to-green FENCE (Murat, critical):** escalation decided on S1/S2 signals only + frozen before S3; S3 single-shot; **call-count assertion = exactly once per escalated slide**; NO path conditions escalation/re-invocation on the gold label or top-1 match.

## Scoring contract (A6) after G2/G3 — what's IN vs OUT of the primary-key top-1
- **IN (scored):** `macro_layout` × `image_role∈{1,2,4}` (2.5→2 folded; 3 quarantined).
- **OUT (probationary per-axis vectors, reported not scored):** `callout_intent` (until κ≥0.6 + N≥4/value harvest), tier 2.5 + tier 3 (until operator-confirmed exemplars), `text_substructure` + `narration_cadence` (per-axis vector per A6).

## S2 / S3 task boundary
- **S2** = per-element `role_tier` (perceiver-primary + geometry gate/backfill) + populate `image_roles` + scoring/quarantine + κ harness. NO escalation call.
- **S3** = the upstream predicate + `escalation_ledger` + the single triggered ≥gpt-5.5 tuple-delta call (D1 oppositional / D2 callout_intent / D3 process-confirm / role-override) + tripwires + retry-to-green fence.

**Follow-ons filed:** `callout-intent-speech-act-axis-harvest` (D2) + the new tier-2.5/tier-3 promotion probes (route `12_Value-Prop-Canvas` to operator confirm for tier 3). Calibrate θ/τ + the κ/agreement floors after Trial-1.
