# Codex Remediation Prompt — P2-4c S2 (T11 HAND-BACK)

**Status:** Claude T11 HANDED BACK S2 (party-mode 5/5 HAND BACK, no impasse; MF-B/MF-C fold-in carried 3–2, dominant). Build on your UNCOMMITTED S2 tree (do NOT revert). ONE consolidated cycle (T1–T10) across 2 files, then Claude re-T11. Do NOT commit/flip.
**Authority:** `reading-path-gap-resolution-G2-G3-2026-06-22.md` (G2, BINDING) · `codex-dev-prompt-p2-4c-s2.md` (S2 ACs) · `p2-4c-s2-t11-code-review-2026-06-23.md` (full findings).
**Why hand-back:** battery is GREEN but green hides the defects — MF-A's corruption is silent, MF-C's κ=1.0 is a false pass. Every MUST-FIX correction must be RED-first (author the fixture, prove it RED on the current tree, then fix).

## MUST-FIX (all RED-first; one cohesive diff across `reading_path_classifier.py` + `image_role_scoring.py`)
**MF-A — `image_roles` index-misalignment (live-path, S2 blocker).** `scripts/utilities/reading_path_classifier.py` `_image_roles`/`_elements`: bbox-less `visual_elements[]` are silently dropped, so `image_roles` is shorter than `visual_elements` and positional consumers (S3 role-override `zip`s them) mis-map every element after a gap. **Fix:** emit `image_roles` as a **full-length array positionally aligned 1:1 with `visual_elements`**, with an explicit `None`/`unscored` sentinel for every dropped (bbox-less / unparseable) element — NO silent drops. (Winston: positional alignment is only safe if the arrays are guaranteed parallel; "do not zip" by comment is not a contract.) RED-first `test_image_roles_index_alignment`: a bbox-less element interleaved among positioned ones → assert `len(image_roles)==len(visual_elements)` and `image_roles[i]`↔`visual_elements[i]`.

**MF-B — tier-3 disagreement invisible to κ + confusion matrix (AC-5/T6 violation).** `scripts/utilities/image_role_scoring.py`: the harness drops ALL tier-3 pairs, so a perceiver systematically over-calling tier-3 (3↔2 / 3↔4) reports κ=1.0. **Fix:** record tier-3-involved disagreement to a side-channel (`tier3_disagreement` counter) AND surface it so the T6 "3↔4 leak must be visible" holds; a planted tier-3 disagreement must move κ off 1.0 OR register in the surfaced metric. RED-first: `score_image_role_agreement(["3","4"],["4","3"])` and `(["3",..],["2",..])` must NOT report clean agreement.

**MF-C — vacuous κ PASS on empty / all-quarantined scored set.** `image_role_scoring.py` `_cohens_kappa` returns 1.0 when `total==0`; combined with the tier-3 drop, an empty or all-tier-3 scored set → κ=1.0 → `passes=True`. **Fix:** when scored-pair count==0, set `passes=False` (or a distinct `insufficient_data` status) — never a green on zero evidence. RED-first: `score_image_role_agreement([],[])` and `(["3","3"],["3","3"])` → assert `passes is False`.

## SHOULD-FIX — FOLD IN
**SF-2 — invalid/out-of-vocab `role_tier` silently dropped to backfill.** Emit a `dropped_invalid_tier` flag (side-channel) when a present-but-invalid `role_tier` is discarded — same silent-data-loss family as MF-A; role emission must be total + explicit, no silent drops anywhere. RED-first test asserts the flag fires.

## DEFER / DOCUMENT (do NOT fix here)
- **SF-4 — icon-set cue unimplemented** (≥3 same-size icons → tier 4; icons >0.05 area currently mis-tier to 2): a FEATURE GAP (not a false-green). DEFER to P2-4b/S3; will be filed to deferred-inventory. Note it in Completion Notes.
- **SF-1 — perceiver `role_tier` bypasses geometry gates** + **SF-3 — non-empty all-bbox-less still raises:** document as known-limitations in Completion Notes (SF-1 = defensible trust-the-perceiver posture; SF-3 = loud-fail-on-fully-degenerate is arguably correct). Revisit if S3 evidence demands.
- **NITs:** borderline-stability fixture asserts a value (acceptable as determinism); dead `_has_opposition_cue` tail (pre-existing S1); magic constant `0.7072`; substring icon/logo match — optional cleanups.

## BINDING re-T11 pass-bar (RED-first; each fixture must fail on the current tree first)
1. `image_roles` full-length index-alignment with a bbox-less element (MF-A).
2. tier-3 disagreement visible in κ/matrix/side-channel (MF-B).
3. empty AND all-quarantined → `passes=False` (MF-C).
4. invalid `role_tier` → flagged, not silently dropped (SF-2).
Plus: full battery re-green (99+ reading-path/vision); lockstep 0; ruff; lint-imports 15/0; contracts = same 14 ambient (zero new reds); enum/fields stay additive; Acceptance re-confirms the 8 ACs still hold (esp. tier-3-excluded-from-scored-top-1 + kind:diagram gate unaffected by the MF-A representation change).

## Process riders (MANDATORY in your re-handoff)
- **Baseline-diff attestation:** clean-HEAD SHA + proof the 14 contract failures are ambient (zero new reds from the remediation).
- One cohesive diff, 2 files. Battery GREEN; no production-path mocks.
