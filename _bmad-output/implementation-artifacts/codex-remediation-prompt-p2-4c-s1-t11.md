# Codex Remediation Prompt — P2-4c S1 (T11 HAND-BACK)

**Status:** Claude T11 HANDED BACK S1 (party-mode 5/5, no impasse). Build on your UNCOMMITTED S1 tree (do NOT revert it); ONE consolidated remediation cycle (T1–T10), then Claude re-runs T11. Do NOT commit/flip.
**Authority:** `spec-p2-4c-reading-path-tuple-refactor.md` (§0 D1/D3 BINDING) · `reading-path-gap-resolution-G2-G3-2026-06-22.md` · `p2-4c-s1-t11-code-review-2026-06-23.md` (the full findings).
**Why hand-back (not patch-forward):** the green battery is partially VACUOUS — a shape-pin certified the `card_grid→top_down` bug, so the gate can't certify its own repair. Every MUST-FIX correction must be RED-first (author/repair the assertion, prove it RED against the current tree, then fix).

## MUST-FIX (all RED-first)
**MF-A — `derive_primary_name` is non-total + test-locked.** `scripts/utilities/reading_path_derivation.py`: add explicit `card_grid` and `two_pane` branches BEFORE the `top_down` fallthrough (card_grid→its own primary; two_pane→oppositional-pair primary). **Rewrite the wrong pin `tests/utilities/test_reading_path_derivation.py:17` RED-first** — flip `card_grid→top_down` to the correct primary, watch it FAIL on the current tree, then land the branches green. Do NOT preserve the wrong pin.

**MF-B — opposition-cue over-fires + S1 over-reaches into S3 (D1).** `reading_path_classifier.py:424-431` `_has_opposition_cue`: replace the bare `before|after|pro|con` alternation with the spec-named cues only, word-boundaried, **requiring the cue to bridge two distinct elements** (not a lone token in one text blob). **Per D1: S1 must FLAG (provisional signal, stay `multi_column`) — it must NOT SET `two_up_comparison`/`comparison_pair`.** Remove the S1 label-set path; the oppositional upgrade is S3's job. (Ties to SF-4 provisional flag.)

**MF-C — transform-signal must be STRUCTURAL, not a prose substring (D3).** `reading_path_classifier.py:408-421` `_has_transform_sequence`: stop matching prose substrings (`then`/`produces`/`feeds`). Gate `enumerated_process` on a D3 structural signal — a connector/arrow KIND between distinct elements, OR a transform verb bridging two distinct element refs. A substring inside one blob does not qualify. **Ownership ruling (Mary):** the STRUCTURAL over-fire is S1-code-owned (fix now); fine cue-weight calibration defers to P2-4b — do not over-tune the lexicon here, just kill the structural false-positive.

## SHOULD-FIX (fold into the same diff)
- **SF-1 — derive, don't except (AC-S1-3 invariant).** Thread `macro_layout` so `center_out`/`diagram_driven` are derivable via `derive_primary_name` (kill the `forced_primary` tuple→name drift at the source). Only if macro_layout is genuinely unavailable at the call site: fall back to documenting the escape hatch + a test asserting tuple/name agreement. Prefer threading.
- **SF-2 — D3 permutability fixture pair** (promoted to MUST for re-T11 by Murat): two inputs identical except element order → assert same tuple for peers / order-sensitivity for a true process.
- **SF-3 — card_grid reachability:** order `_looks_like_grid` before `_looks_multi_column` (currently shadowed) + a precedence shape-pin.
- **SF-4 — provisional flag:** implement the `multi_column` provisional flag MF-B/D1 route to; pin it. Add a one-line attestation in the catalog/spec that the A3 quarantine flag was removed per the operator-ratified D1 (un-quarantine) — cite the D1 record (catalog §11).

## NIT
- Remove dead `_looks_z`/`_looks_f_pattern`/`_has_ordinal`/`_SCORERS` OR wire `_looks_z` to the spec's "optional z-flag" (and emit it). Currently AC-S1-4's tightened-`_looks_z` is enforced by never calling it — make it real or remove it.
- Add a classify-path test pinning `with_classified_reading_path(...).image_roles is None` and `.callout_intent is None` in S1.

## BINDING re-T11 pass-bar (Murat — all six RED-first against the pre-fix tree)
1. D3 permutability fixture pair.
2. Opposition-cue negative controls: bare `before`/`after` AND `pro`/`con` each → NOT two_up_comparison (and per D1, S1 stays multi_column + sets the flag).
3. Transform-verb-in-prose negative control: narrative "then" → NOT enumerated_process.
4. `card_grid` → its correct non-default primary (the corrected MF-A pin).
5. `two_pane` → its correct non-default primary.
6. `forced_primary`/derived tuple→name round-trip (explicit primaries survive derivation; no DEFAULT collapse).

## Process riders (Mary — MANDATORY in your re-handoff packet)
- **Baseline-diff attestation:** paste clean-HEAD SHA (`829bc53`) + stash-proof that the 14 contract failures are ambient (NOT S1-introduced) and that your remediation adds zero new reds.
- One cohesive diff, one commit-intent (Claude commits at T11). Battery GREEN; lockstep exit 0; ruff; lint-imports; no production-path mocks.
