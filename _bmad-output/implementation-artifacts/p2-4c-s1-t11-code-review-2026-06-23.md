# P2-4c S1 — Claude T11 Code Review + Close Record (2026-06-23)

**Outcome:** HAND BACK to Codex (party-mode 5/5, no impasse). S1 did NOT flip done. Codex's S1 dev code stays UNCOMMITTED in the working tree for re-work; Claude's T11 diff is review/governance docs only.
**Branch:** `fidelity-perception-arc-2026-06-19`. **Base HEAD:** `829bc53`.

## Battery (independently reproduced, not handoff-trusted)
- Focused reading-path slice (7 files): 66 passed. Acceptance Auditor wider slice: 77 passed.
- Lockstep `check_pipeline_manifest_lockstep.py`: exit 0. ruff: clean. lint-imports: 15 kept / 0 broken.
- Enum additive verified: all 7 legacy values RETAINED + 5 new (split_image_text, two_up_comparison, text_hero_divider, enumerated_process, diagram_driven) = 12; nothing removed. dp-v1.5→dp-v1.6.
- **Baseline-diff:** broader sweep showed 14 `tests/contracts/` failures → stashed S1, re-ran on clean HEAD `829bc53` → **identical 14 fail** ⇒ AMBIENT (pre-existing repo debt), NOT S1-introduced. S1 added zero new reds.
- Reverted 6 `tests/fixtures/vision/recordings/slide-*.json` (test-run rot: timestamp + absolute-path + live-recapture variance via `test_vision_live_roundtrip.py`; the deferred `vision-recording-normalize-on-write` issue) — not part of S1.

## 3-layer review findings (deduplicated)
**MUST-FIX (3, all production classifier code):**
- **MF-A** — `derive_primary_name` missing `card_grid`/`two_pane` branches → collapse to `top_down` DEFAULT (mislabel + pollutes the anti-vacuity ceiling); **shape-pin test locks the wrong `card_grid→top_down`** (test-locked bug → green battery is partially vacuous as a gate).
- **MF-B** — `_has_opposition_cue` matches bare `before/after/pro/con` → false `two_up_comparison`; S1 over-reaches into S3's deferred oppositional job (D1 says S1 FLAGS, stays multi_column).
- **MF-C** — `_has_transform_sequence` matches prose substrings ("then") → false `enumerated_process` (D3 permutability violation). Ownership: structural over-fire = S1-code fix; fine cue-weight calibration defers to P2-4b (Mary).

**SHOULD-FIX (4):** SF-1 forced_primary (center_out/diagram_driven) bypasses derivation → tuple→name drift (AC-S1-3 invariant); SF-2 missing D3 permutability fixture (promoted to MUST for re-T11); SF-3 card_grid shadowed by multi_column; SF-4 `provisional` flag dropped without D1-supersession attestation.
**NIT (2):** dead `_looks_z`/`_looks_f_pattern`/`_has_ordinal`/`_SCORERS` + unemitted "optional z-flag"; no classify-path None-ness test.

## Party-mode CLOSE gate — 5/5 HAND BACK (no impasse)
Winston / Murat / Mary / Amelia / John, all ratify. Key points: the test-lock makes the gate vacuous (Murat — independently forces hand-back); all 3 MUST-FIX are the over-claim disease the story cures, not deferrable calibration (John); derive-don't-except for SF-1 (Amelia/Winston); one cohesive Codex diff. Binding re-T11 pass-bar = the 6 RED-first fixtures + 3 governance riders (see `codex-remediation-prompt-p2-4c-s1-t11.md`).

## Disposition
NEXT = operator dispatches Codex on `codex-remediation-prompt-p2-4c-s1-t11.md` (T1–T10 remediation on the uncommitted tree) → Claude re-T11. Governance filings: anti-pattern "green test certifies a bug" (dev-agent-anti-patterns); 14 ambient contract failures + hand-back logged to deferred-inventory; baseline-diff attestation now mandatory in NEW CYCLE re-handoffs.
