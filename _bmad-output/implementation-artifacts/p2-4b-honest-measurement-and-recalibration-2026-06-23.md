# P2-4b — Honest Built-Classifier Measurement + Recalibration Spec (2026-06-23)

**Status:** MEASUREMENT DONE (the first fair built-classifier number on fresh substrate) → recalibration is a **NEW CYCLE** (Codex T1–T10 → Claude T11), party-green-light-gated.
**Branch:** `fidelity-perception-arc-2026-06-19`. **HEAD at measurement:** `b94911d`.
**Authority:** `spec-p2-4b-conformance-finalize.md` §4 (the 4-leg framing) + the frozen gold (`reading-path-holdout-gold-labels-2026-06-23.md`) + catalog v1.1 §9. **Discipline:** every number carries `(subject, substrate)`; no mocks; first-run-stands; frozen gold never re-labeled to pass.

---

## 1. The measured number (leg 1a DONE + leg 3 DONE)

**leg 1a** (re-perceive the 14 held-out under S2 `role_tier`, live gpt-5.5) = already run 2026-06-23 00:03–00:07 → `reading-path-holdout-rescan-2026-06-23/perceptions/*.json` (role_tier-aware; first-run-stands).
**leg 3** (S1/S2 classify + live S3 escalation over those fresh perceptions, score vs gold) = `scripts/analysis/reading_path_p2_4b_measure_fresh.py` (leg-3-only; reuses the frozen fresh perceptions — does NOT re-perceive, to avoid re-rolling leg 1a). Report: `reading-path-holdout-rescan-2026-06-23/honest-built-classifier-measurement.json`.

| metric | **subject=built-classifier(S1/S2/S3), substrate=fresh@2026-06-23** | bar | verdict |
|---|---|---|---|
| primary-key top-1 (`macro × image_role`) | **0.071** (1/14 — only `15_`) | ≥0.85 | ❌ FAIL |
| full-tuple | **0.000** | ≥0.80 | ❌ FAIL |
| macro_layout | 0.500 (7/14) | — | the geometry floor |
| image_role (folded {1,2,4}) | 0.214 (3/14) | — | over-tiers |
| text_substructure | 0.214 | — | — |
| narration_cadence | 0.571 | — | — |
| escalation rate | **0.929** (13/14) | ≤0.20 | ❌ FAIL |
| degraded/default rows | 0 | ≤~25% | ok |

**Headline correction (believed-green discipline):** the catalog-approach 0.93 was Claude-in-loop labeling, NOT the built classifier. **Fresh re-perception did NOT move the built number (0.071 fresh ≈ 0.071 stale)** → the defects are in the **classifier logic**, not perception staleness. The 14 fresh perceptions are HIGH-confidence and role_tier-tagged; the misses are downstream.

## 2. Per-slide diagnosis (emitted vs gold)

```
slide                         emit_macro         gold_macro          domR goldR
1_Diagnosis-Innovation        split_image_text   split_image_text     2    1     (role miss)
3_Achieving-the-Ideal-State   multi_column       single_text_block    2    4     (macro+role miss)
5_Check-Your-Understanding    single_text_block  single_text_block    4    1     (role miss)
6_All-of-them-belong-to-BOTH  split_image_text   split_image_text     2_5  1     (role miss)
8_Decision-Making-Foundations split_image_text   split_image_text     2_5  1     (role miss)
9_Comparing-EV-and-EU         multi_column       two_pane             2_5  None  (macro miss)
11_Value-Creation-in-Innov.   single_text_block  multi_column         2_5  None  (macro miss)
13_Effective-Problem-Solving  single_text_block  multi_column         2_5  1     (macro+role miss)
15_Types-of-Motivation        split_image_text   split_image_text     2    2     ✅ PRIMARY-KEY HIT
17_Examples-of-Eff-Leadership single_text_block  multi_column         2    2     (macro miss)
18_The-Future-of-PH-Lead      single_text_block  single_text_block    4    None  (macro ok)
20_Resources-for-Entrep.      multi_column       card_grid            2_5  None  (macro miss)
21_Key-Takeaways              split_image_text   split_image_text     2    1     (role miss)
22_Next-Steps-Your-Path       multi_column       card_grid            4    4     (macro miss)
```

## 3. Root causes (3 axes) — all built-classifier logic, all NEW CYCLE

### A. Macro geometry (S1) — 50%, the dominant cap on primary-key
Owner: `scripts/utilities/reading_path_classifier.py` (S1 deterministic geometry). Systematic confusions:
- **`multi_column` ↔ `single_text_block`** (3_, 11_, 13_, 17_): the column-vs-single-block detector mis-fires both directions — it cannot reliably decide whether vertically-stacked text blocks are N peer columns or one block.
- **`multi_column` ↔ `card_grid`** (20_, 22_): a 2×N card grid is read as columns.
- **`multi_column` ↔ `two_pane`** (9_): a 2-pane comparison read as columns.
→ The geometry over-predicts `multi_column`. Tighten column detection (gutter/row-band/peer-count evidence) and add card_grid (≥2 rows × ≥2 cols) + two_pane (2 balanced panes + per-side heading) discriminators. This is `reading-path-s1-geometry-macro-accuracy`.

### B. image_role (S2 role-tier + the dominant-fold rule) — 21%
Two compounding issues:
- **Perceiver over-tiers decorative→illustrative**: gold says tier 1 (decorative, no-VO) on 1_/5_/6_/8_/13_/21_; the role_tier prompt returns 2 / 2_5. The S2 `role_tier` rubric needs the decorative-vs-illustrative boundary sharpened (a tone/mood image with no internal labels and not referenced by the text = tier 1, even if photographic).
- **Dominant-fold rule is a SCAFFOLD**: `reading_path_p2_4b_run._dominant_image_role` picks the MOST load-bearing present tier (3>2_5>2>4>1), so a single minor illustrative element overrides a slide that is dominantly decorative. There is **no authoritative slide-level dominant image_role** in the classifier dump (only per-element `image_roles` + `image_role_flags`). **S2 must emit an authoritative slide-level dominant image_role** (area-weighted / largest-element rule), and the harness must consume THAT instead of the scaffold. (Fixing the scaffold alone ≠ retry-to-green: the gold is frozen; this defines the intended dominant rule once, in substrate.)

### C. Escalation over-fire (S3) — 93% (the ≤20% ceiling blown)
Owner: `scripts/utilities/reading_path_escalation.py`. `callout_kind_present` fired 13/14 — it triggers whenever any callout-kind element is present, which is nearly every slide. Tighten the escalation trigger to genuine ambiguity (e.g., low macro margin between top-2 candidates, or a tier-3 candidate, or geometry/role disagreement) and **wire the ≤20% ceiling to the REAL ledger** with the G3 retry-to-green fence (escalation decided on S1/S2 signals only, frozen before S3, exactly-once-per-escalated-slide).

## 4. Recalibration scope (the NEW CYCLE story)

One story, three coordinated work items (A geometry, B image-role dominant + tier rubric, C escalation predicate), because primary-key needs macro AND image_role and they interact. **Gate-mode: dual** (substrate classifier + escalation logic, measured-failure-driven). **Files:** `reading_path_classifier.py`, `reading_path_escalation.py`, the S2 `role_tier` perceiver prompt, and the dominant-image-role rule (promote out of the harness scaffold into substrate). **4-file lockstep / manifest:** not touched (classifier is downstream of the pack); confirm at T1.

**Acceptance (re-run, do NOT re-label gold):** `reading_path_p2_4b_measure_fresh.py` over the SAME 14 fresh perceptions → primary-key ≥0.85 AND full-tuple ≥0.80 AND escalation ∈ (0%, 20%] AND default ≤25% AND foreground-gate/quarantine tripwires green. If a bar can't be reliably reached, report the honest number at a party-ratified accepted bar (do NOT force). Re-perception is NOT part of the acceptance re-run (the fresh perceptions are frozen substrate); only the classifier logic moves.

**Governance:** party-mode green-light THIS scope before Codex opens (per goal). Codex T1–T10; Claude T11 (battery + bmad-code-review + re-measure). Contingent leg 1d (further macro/image lift) folds into the same cycle if the first pass still falls short.

## 5. Authority chain
`spec-p2-4b-conformance-finalize.md` §4 → this measurement+diagnosis → (party green-light) → Codex dev prompt → Claude T11 re-measure → P2-4b PASS/FAIL verdict → P2 epic close.
