# Codex Dev Prompt — P2-4b Reading-Path Classifier Recalibration (NEW CYCLE, dual-gate)

**You are Codex, the dev agent (T1–T10).** Claude pre-authored this; Claude runs T11 (battery + `bmad-code-review` + the honest re-measure + commit + flip). **Do NOT relitigate the party-ratified scope below.** Party green-light: **5/5 GREEN-WITH-AMENDMENTS, no impasse** (record: `p2-4b-honest-measurement-and-recalibration-2026-06-23.md` §4.5).

## Why this cycle exists (the measured failure — every number tagged)
The BUILT reading-path tuple classifier (S1 geometry + S2 image-role + S3 escalation) was measured FAIR for the first time on FRESH substrate (14 held-out re-perceived under S2 `role_tier`, live gpt-5.5): **subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23** → primary-key top-1 **0.071** (1/14), full-tuple **0.000**, macro **0.50**, image_role **0.21**, escalation **0.93**. FAIL vs ≥0.85. Fresh re-perception did NOT move it (≈ the stale 0.071) → **the defects are classifier LOGIC, not perception staleness.** Evidence: `reading-path-holdout-rescan-2026-06-23/honest-built-classifier-measurement.json` + per-slide table in the spec §2.

## Discipline (HARD FENCES — violating any is a T11 reject)
- **No mocks; live gpt-5.5+ for any model call; first-run-stands; no retry-to-green.**
- **Frozen gold is NEVER re-labeled** to make the classifier pass. Record the gold content-hash in your handoff §0 (`reading-path-holdout-gold-labels.json`); Claude re-verifies at T11. Only CLASSIFIER LOGIC moves; perceptions + gold + scoring harness denominator stay frozen.
- **Logic-only, generalizable fixes:** NO `if slide_id == …`, NO gold-keyed lookup tables, NO thresholds tuned to the specific 14. Every change must articulate a RULE (fix the mechanism, not the symptom on slide N). Claude T11 audits the diff for this.
- **No-peeking:** tune against AGGREGATE axis numbers, NOT per-slide gold pass/fail. The final per-slide conformance score is computed ONCE by Claude at T11.
- **Provenance on every number** you report: `(built-classifier, frozen-fresh-14, gold-known-to-dev)`.
- **Additive non-regression:** P2-1/2/3/4a/4c stay green. Never leave the 4-file lockstep / manifest half-modified (this cycle should NOT touch the pack/manifest — confirm at T1).

## The three work items — ORDER: A → B → C (with the C-split below)

### A. Macro geometry (`scripts/utilities/reading_path_classifier.py`) — owner of the 50% floor
Symptom: over-predicts `multi_column`, confusing it with `single_text_block` (3_/11_/13_/17_), `card_grid` (20_/22_), `two_pane` (9_). Fix: tighten column detection (require real gutter + row-band + peer-count evidence) and add explicit discriminators for **card_grid** (≥2 rows × ≥2 cols) and **two_pane** (2 balanced panes + per-side heading). Axis target (isolated, macro-only fixture): **macro ≥0.85**. Land + freeze + record the macro-only number BEFORE B.

### B. image_role tiering + authoritative dominant (S2 `role_tier` perceiver prompt + `reading_path_classifier.py`) — the coupled, harder axis; FOLD LAST
Two sub-fixes:
1. **Sharpen the decorative-vs-illustrative `role_tier` rubric** — the perceiver over-tiers decorative images as illustrative (gold tier-1 photos returned 2/2.5). Rule: a tone/mood image with no internal labels, not referenced by the text, = tier 1 even if photographic.
2. **Promote an authoritative slide-level `dominant_image_role` into substrate** — RESOLVED PRECONDITION (T1 check done): the gold encodes an authoritative per-slide `image_role`; the classifier emits only per-element `image_roles` + the dominant is currently synthesized by the analysis scaffold `scripts/analysis/reading_path_p2_4b_run._dominant_image_role`. Emit a deterministic, area/geometry-weighted `dominant_image_role` field from `reading_path_classifier.py`, co-located with per-element role_tier (auditable + re-derivable without re-perception), **fold the decorative/illustrative rubric INTO this emission**, and **DELETE the scaffold `_dominant_image_role`** (no shadow second path). The harness then READS the authoritative field. Axis target (isolated, image_role-only fixture): **image_role ≥0.70**.

### C. Escalation (`scripts/utilities/reading_path_escalation.py`) — SPLIT
- **C-early (orthogonal confidence anchor, may land first/independently):** narrow `callout_kind_present` (fired 13/14) — it must NOT trigger on the mere presence of a callout-kind element. Re-base on genuine ambiguity.
- **C-late (after A+B corrected):** wire the **≤20% ceiling to the REAL escalation ledger** (PRECONDITION per Murat — if the re-run still reads the scaffold ceiling the escalation number is meaningless) + add the geometry/role-disagreement trigger + the G3 retry-to-green fence (escalation decided on S1/S2 signals only, frozen before S3, exactly-once-per-escalated-slide). Target: escalation ∈ **(0%, 20%]**.

## RED-first test scaffolding (binding — author RED before logic)
1. **Three per-axis fixtures** (macro-only, image_role-only, escalation-only) extracted from the 14 frozen perceptions, asserting the TARGET labels.
2. **The full 14-slide integration harness** (`scripts/analysis/reading_path_p2_4b_measure_fresh.py`) run after each axis lands — measures all five metrics so cross-axis regressions surface.
3. **A pinned S1/S2/S3 regression snapshot** — capture current emissions on the existing P2-4c green-test slides; assert the INTENDED deltas explicitly (escalation MUST change on slides X/Y, must NOT change on Z). A rewrite that passes the new bar but silently flips an S3-green slide is a reject.
4. **Perturbation guard:** reorder element lists / re-feed 3–4 slides → emitted tuple must be STABLE (catches knobs fit to surface noise).
5. Tripwires wired as harness ASSERTIONS: escalation ∈(0%,20%]; default ≤25%; foreground-gate negatives (8_, 13_ NOT diagram_driven); multi_column quarantine (no residual over-predict).

## Acceptance (re-run over the SAME frozen fresh perceptions — gold frozen)
- **SUCCESS bar (clean close):** primary-key ≥0.857 (12/14) AND full-tuple ≥0.80 AND escalation ∈(0%,20%] AND per-axis floors **macro ≥0.85 + image_role ≥0.70** (simultaneous, no trading) AND default ≤25% AND tripwires green.
- **CONDITIONAL-PASS [0.70,0.85):** OPERATOR-GATED (a sub-0.85 bar). Claude surfaces this to the operator separately; do NOT assume it. Author to the success bar.
- Report per-axis before/after deltas + the three internal-seam numbers (post-A, post-B, post-C) in your handoff. State the n=14 quantization (1 slide ≈ 0.071) and the CI caveat.

## Files in scope / do-NOT-modify
- **In scope:** `scripts/utilities/reading_path_classifier.py`, `scripts/utilities/reading_path_escalation.py`, the S2 `role_tier` perceiver prompt, new per-axis fixtures under `tests/`, and DELETE `scripts/analysis/reading_path_p2_4b_run._dominant_image_role` (move the authority into the classifier).
- **Do NOT modify:** the frozen gold, the 14 frozen fresh perceptions, the scoring harness math (`reading_path_p2_4b_score.py` — score logic frozen), the v4.2 pack / pipeline manifest / 4-file lockstep (confirm untouched at T1).

## Handoff → Claude T11
Deliver to `_bmad-output/implementation-artifacts/_codex-handoff/p2-4b-recalibration-ready-for-review.md`: gold-hash §0, per-axis + seam numbers, the honest re-measure output, baseline-diff attestation (any "pre-existing" failure needs pasted clean-HEAD RED evidence), regression-snapshot results. Claude T11 = battery + 3-layer `bmad-code-review` + independent re-measure (first-run-stands) + logic-only diff audit + commit + flip.
