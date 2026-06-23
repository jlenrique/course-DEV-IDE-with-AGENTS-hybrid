# Codex Dev Prompt — P2-4c **S2** (per-element image-role tier emission)

**Cycle:** NEW CYCLE — Codex T1–T10 + self-review → Claude T11 (battery + 3-layer `bmad-code-review` + party CLOSE + commit + flip done). Do NOT commit/flip.
**Prereq:** **S1 must be merged first** (S2 extends S1's classifier + the additive schema). **Class S.** Branch `fidelity-perception-arc-2026-06-19`.
**Authority:** `spec-p2-4c-reading-path-tuple-refactor.md` (§0 v1.1, §5 S2, §6 G2 [RESOLVED — see below], §7) · `reading-path-patterns-catalog.md` v1.1 (§2 AXIS 2 image_role) · `reading-path-gap-resolution-G2-G3-2026-06-22.md` (the party resolution; BINDING) · pydantic-v2 checklist.

## G2 resolution (party-ratified — BINDING)
**Placement = perceiver-primary + deterministic geometry gate/backfill.** Tier is a SEMANTIC judgment → the perceiver (which already sees pixels + emits `kind` per element) emits `role_tier`; geometry gates impossible tiers OUT and backfills when the perceiver is terse. **No new model round-trip** — `role_tier` rides the EXISTING perception call with the tier rubric inlined into the perception prompt.

## Scope = S2 ONLY
Per-element `role_tier` emission + the deterministic cue/gate/backfill + populate the existing `image_roles` field + the scoring/quarantine rules + the agreement harness. **NOT the escalation call (that's S3).**

## Files in scope
- `app/specialists/vision/payload_contract.py` — add optional `role_tier` to each `visual_elements[]` entry (the list is already `list[dict[str, Any]]`; element-level addition is free).
- `app/specialists/vision/provider.py` (or wherever `_perception_prompt`/`PERCEPTION_SYSTEM_MESSAGE` live) — inline the tier rubric + instruct emit `"role_tier": "1|2|2_5|3|4"` per element with a one-word eye-verb justification.
- `app/models/perception/perception_artifact.py` — add the `RoleTier` closed enum {`"1","2","2_5","3","4"`} if S1 didn't; `image_roles` field already exists (S1).
- `scripts/utilities/reading_path_classifier.py` — compute geometry cues + hard-gates + the prior backfill; populate `image_roles` from per-element tiers (replace the S1 null/stub).
- Tests under `tests/`.

## DO NOT MODIFY
- S1's geometry macro-layout / derivation / `_looks_z` logic (extend only).
- The escalation predicate / S3 call (S3 territory).

## Tasks (T1–T10)
**T1 — readings + baseline-diff attestation** (clean-HEAD evidence for any "pre-existing" claim).

**T2 — `RoleTier` enum + contract** (pydantic-v2: closed Literal, triple-layer red-rejection, `"2_5"` round-trips). `role_tier` optional per element; `None` = "perceiver not consulted / deterministic prior stood" (do NOT default to a tier — that hides the decision).

**T3 — deterministic geometry cues + HARD-GATES** (per element, no model call): `area_pct`, `centrality`, `edge_bleed`, `text_overlaps_image`, `internal_label_count` (OCR/text boxes fully inside the image bbox), `caption_adjacent`, `is_in_icon_set` (≥3 same-size small kinds in a row), `aspect_bucket`. HARD-GATES:
- `kind∈{icon,logo} AND area_pct<0.05` → **LOCK tier 4** (done, no perceiver).
- `internal_label_count == 0` → **tier 3 RULED OUT** (no structure to walk = nothing to narrate; this gate alone kills the kind:diagram-was-decorative bug).
- `edge_bleed AND text_overlaps_image AND internal_label_count==0` → strong tier-1 prior.

**T4 — perceiver-primary tier + backfill.** Among non-locked elements the perceiver assigns the final tier via the eye-verb rubric (feel→1 / glance→2 / confirm→2.5 / trace→3 / tag→4) with cited referential-language evidence. Where the perceiver omits `role_tier`, backfill with the deterministic prior table (decorative<0.05&¬caption→1@.75; chart/table&caption→2.5@.7; diagram&area≥.25&central≥.6→3@.45 [deliberately low]; photo→2@.6; else 2@.3). Populate `artifact.image_roles`.

**T5 — scoring + quarantine rules (BINDING):**
- LIVE scored tiers = **{1, 2, 4}**. **2.5 FOLDS→2** for A6 primary-key scoring. **Tier 3 QUARANTINED** (emittable + side-channel, excluded from scored top-1) until an operator-confirmed exemplar promotes it.
- 2.5 + 3 emissions are recorded to a side-channel + **flagged for S3 escalation/harvest** (the escalation log becomes the promotion-evidence pipeline).
- **Provenance metadata** per tier in the rubric artifact: `exemplar_count`, `sources` (reviewed-26 / held-out), `retest_marker: confirmed|provisional`. Tiers 2.5/3 carry `provisional` + "promote on first operator-confirmed exemplar". `12_Value-Prop-Canvas` = the designated tier-3 promotion probe (route to operator confirm; do NOT self-promote).

**T6 — agreement harness:** a double-labeled Cohen's κ check on the reviewed-26 image set over the **4-value folded scored set** {1,2,4 (+2.5→2)}; pass-bar **κ≥0.6**; ALSO a separate soft-middle {1,2} sub-κ ≥0.6 (else fold 1+2 → {presentational, instructional, pointer} fallback). **Emit a confusion-matrix artifact** (not just a scalar) so disagreement that leaks into 3↔4 is visible.

**T7 — RED-first fixtures:** one per tier (decorative_pure→1; illustrative_supporting→2; evidentiary_chart→2[side-channel 2.5]; instructional_diagram→3[quarantined]; pointer_chip/icon-set→4); the `kind:diagram` decorative negative control (→ NOT tier 3); the `internal_label_count==0` tier-3-ruled-out gate; ≥1 **borderline-stability** fixture per soft boundary (1↔2, 2↔2.5) asserting a STABLE label is produced (not that it's "correct"). Fold-in: the deferred `vision-perceiver-empty-visual-elements-degradation` (empty `visual_elements` HIGH/perceived → controlled, image_roles=[] not a raise).

**T8 — additive non-regression** (S1 + P2-4a green). **T9 — battery** (lockstep exit 0, ruff, lint-imports, diff-check; no production-path mocks — recorded-real perceiver responses behind the parse seam only). **T10 — self-review + handoff** (`_codex-handoff/p2-4c-s2-ready-for-review.md`: per-AC evidence, RED→green transcript, κ + confusion matrix, baseline-diff attestation).

## Pass-bar (Claude T11)
Scored tier set {1,2,4} with 2.5→2 fold + tier-3 quarantine enforced in code; κ≥0.6 (4-value) + soft-middle sub-κ≥0.6 + confusion-matrix artifact; tier-4 size-lock + tier-3 internal-label-gate as RED negative controls; provenance metadata present; `image_roles` populated (not null); S1 + P2-4a green; no production-path mocks.
