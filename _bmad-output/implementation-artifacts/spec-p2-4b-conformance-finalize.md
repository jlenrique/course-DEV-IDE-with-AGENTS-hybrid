# Spec — P2-4b Conformance-Finalize (reading-path arc)

**Status:** PRE-STAGE READY (harness + gold built; the live run is gated on S2+S3 landing).
**Date:** 2026-06-23. **Author:** Claude. **Branch:** `fidelity-perception-arc-2026-06-19`.
**Depends on:** S1 (deterministic geometry — landed) + S2 (image-role tier emission) + S3 (gpt-5.5 escalation) per catalog §9.2. P2-4b is the **conformance gate that closes the P2-4c build**.

---

## 0. The FLIPPED methodology (recorded; reserve consumed)

The original P2-4b design (catalog §9.6) was **"operator labels the held-out 14 independently (anti-anchoring) → score the classifier against operator gold."** That design assumed a naive held-out reserve.

**Operator-authorized flip (2026-06-22, `holdout-confirm-deny-kit-2026-06-22.md`):** the operator had already completed round-1 training (26 slides), so the reserve is no longer kept naive. The flow became:

1. **Claude LABELS** the 14 held-out slides via the catalog v1 approach (from live gpt-5.5 perceptions, not filenames).
2. **Operator CONFIRMS / DENIES** each (12 CONFIRM / 2 DENY: 17_, 21_).
3. The confirmed set + the 3 ratified decisions (D1/D2/D3) become the **frozen gold** (`reading-path-holdout-gold-labels-2026-06-23.md`).

**Consequence (operator-accepted):** labeling these 14 **CONSUMES the held-out reserve** — they are no longer naive for any future independent-label scoring. This supersedes the prior independent-label P2-4b design; flagged to party at the next gate (non-blocking, governance record).

> **⚠️ CORRECTION (S3-T11, 2026-06-23) — the 0.93 is NOT the built classifier.** An earlier version of this spec implied "P2-4b is already at 0.93 / one command (`run_live`)." The S3-T11 live dry-run disproved that: **0.93 = the catalog-approach (Claude-in-loop labels) vs gold; the BUILT deterministic classifier scored primary-key 0.071** on the held-out (on STALE perceptions captured pre-S2-role_tier → geometry-backfill-only — an un-fair number, but far from 0.93), and the escalation predicate **over-fired at 93%** (vs the 20% ceiling). **The built classifier's honest accuracy is UNMEASURED.** P2-4b is therefore a **real 4-leg calibration milestone, NOT a rubber-stamp** (see §4). Every metric below carries `(subject, substrate-freshness)`.

**Why this measures conformance:** P2-4b runs the *built classifier* over the 14 held-out perceptions → EMITTED tuples → scores EMITTED-vs-GOLD via the harness. The classifier was NOT tuned on these gold labels, so it is a legitimate conformance measurement (catalog-as-implemented vs operator-confirmed catalog-as-intended). **The held-out confirm/deny round was NOT this run** — it scored *Claude's catalog-guided labels* (subject=catalog-approach) as the "emitted" set (→ 0.93), which measures human/Claude labeling, not the deterministic predicate. Different subjects; do not equate them.

---

## 1. The A6 scoring contract + thresholds

Per catalog v1.1 §9.4 + `reading-path-gap-resolution-G2-G3-2026-06-22.md`:

### IN the scored top-1 (the headline metric)
- **PRIMARY-KEY top-1** = STRICT exact match on `macro_layout × image_role`, image_role folded to the live-scored set **{1, 2, 4}** (2.5 → 2; tier 3 quarantined/excluded). No partial credit.
- **THRESHOLD: ≥ 0.85.** (Catalog-approach/Claude-labels dry run: 0.93 ✅. **Built-classifier on stale perceptions: 0.071 ❌ — UNMEASURED-fair; needs fresh re-perception. The threshold has NOT been met by the built classifier.**)

### Full-tuple
- **FULL-TUPLE exact match** = exact on `macro_layout × image_role × text_substructure × narration_cadence` (callout_intent + quarantined tiers excluded).
- **THRESHOLD: ≥ 0.80.** (Held-out dry run: 12/14 = 0.857 ✅.)

### Reported, NOT scored into top-1
- **Per-axis confirm vectors:** `text_substructure`, `narration_cadence` (+ `macro_layout`, `image_role` individually for transparency). Reported as a vector, never folded into top-1 (prevents a strong macro masking a vacuous secondary axis).
- **`callout_intent`** — **PROBATIONARY separate per-axis vector**, EXCLUDED from both the primary-key top-1 and the full-tuple match (D2). Advisory floor: double-labeled agreement ≥0.80 / κ≥0.6 before it can ever be promoted into a scored axis. `inform`/null = no-op default (not scored). The held-out gold carries 4 real callout acts (5_ challenge_quiz, 18_ invite_response, 22_ directive_cta, 21_ takeaway_imperative).
- **tier-2.5** — folds → 2 (scored as illustrative).
- **tier-3** — **QUARANTINED**: emittable + side-channel, EXCLUDED from the scored top-1; promoted only on operator-confirmed exemplars. (None of the 14 carry one.)

### Artifacts
- **macro_layout confusion matrix** emitted per run.
- **Contamination check (A6 rider):** record, per held-out slide, whether its gold invokes a gated/retired pattern (`diagram_driven`/`f_pattern`). If ≥2 of 14 legitimately want one, the retirement was overfit and the 0.85 is contaminated. (Held-out: 0 — the `diagram_driven` foreground-gate held on 8_ + 13_.)
- **`multi_column` quarantine status:** per D1, `multi_column` EXITS the A3 quarantine at N≥4 (reviewed 2_/4_/5_ + held-out 17_ = N≥4 across ≥2 genres) → it now COUNTS toward the top-1 denominator; 17_ stays scored (no metric laundering).

---

## 2. The scoring harness (built; pre-stage deliverable)

`scripts/analysis/reading_path_p2_4b_score.py` — a PURE, deterministic harness:

- **Input:** a list of `(slide_id, emitted_tuple, gold_tuple)` triples (`ReadingPathTuple` dataclass: `macro_layout`, `image_role`, `text_substructure`, `narration_cadence`, `callout_intent`, `derived_primary`).
- **Output:** a `ScoreReport` with primary-key top-1, full-tuple rate, per-axis vectors, callout_intent probation vector, macro confusion matrix, quarantine list, per-slide detail, and PASS/FAIL vs the thresholds.
- **Folding logic:** `fold_image_role()` — 2.5→2, 3→quarantine-sentinel, none→None, {1,2,4} unchanged.
- **It does NOT touch** the live classifier, perceiver, or any vision/perception substrate — it scores triples the caller supplies. (Constraint: S2 files are mid-edit by Codex; the harness is deliberately decoupled.)
- **Self-test:** `tests/analysis/test_reading_path_p2_4b_score.py` — 18 tests, ruff-clean, proves the A6 math on SYNTHETIC fixtures (13/14 primary-key → 0.929; folding edge cases; tier-3 quarantine; callout exclusion; macro-mismatch breaks key). `build_demo_rows()` + `__main__` reproduce the held-out round numbers.

---

## 3. How P2-4b runs once S2 + S3 land (the live run)

> Do NOT run any of this against the working tree while S2 is mid-edit. This section is the run plan for AFTER S2+S3 are merged + green.

1. **Inputs ready:** the 14 held-out perceptions (`reading-path-holdout-scan/perceptions/*.json` + `holdout-perception-summary.json`) + the frozen gold (`reading-path-holdout-gold-labels-2026-06-23.md`).
2. **Run the built classifier** (S1 geometry + S2 image-role tiers + S3 escalation, end-to-end) over each of the 14 held-out perceptions → an EMITTED `ReadingPathTuple` per slide. This is the only leg that touches the (by-then-merged) S2/S3 substrate.
   - The S3 escalation leg is the live ≥gpt-5.5 catalog-guided tuple-delta call; first-run-stands, no retry-to-green, with the retry-to-green fence (escalation decided on S1/S2 signals only, frozen before S3, exactly-once-per-escalated-slide assertion — G3).
3. **Build the triples:** pair each emitted tuple with its gold by `slide_id` → 14 `(slide_id, emitted, gold)` rows.
4. **Score:** `score(rows)` → the `ScoreReport`. Emit the summary + confusion matrix + per-slide table + the `escalation_ledger.json` (from S3) as run artifacts.
5. **Check the RED tripwires (G3 / catalog §9.5):**
   - DEFAULT-degradation ceiling ≤ ~25% (anti-vacuity).
   - over-escalation FAIL if rate > 20%; zero-escalation FAIL if 0% with a known-ambiguous slide.
   - `diagram_driven` foreground-gate negative control (8_, 13_ assert NOT diagram_driven).
   - `multi_column` quarantine flag flipped correctly (now counts toward denominator).

---

## 4. The REAL P2-4b — a 4-leg calibration milestone (NOT a rubber-stamp)

The held-out confirm/deny round was the **catalog-approach** dry run (Claude's v1 labels vs gold → 0.93) — it measures human/Claude labeling, NOT the built classifier. The harness self-test reproduces *that* arithmetic with synthetic emitted tuples:
```
.venv/Scripts/python.exe scripts/analysis/reading_path_p2_4b_score.py
```
But the S3-T11 live dry-run of the **built** classifier (`reading_path_p2_4b_run.run_live()`) scored **0.071 on stale perceptions** + **93% escalation**. So the real P2-4b has **four legs** (ratified S3-T11 party 5/5):
1. **Re-perceive** the 14 held-out PNGs under S2's `role_tier` prompt (kills the stale-substrate confound — the 0.071 was on pre-S2 perceptions with geometry-backfill-only image_roles).
2. **Recalibrate** the escalation predicate (esp. the over-broad `callout_kind_present`; the threshold can't precede recalibration — chicken/egg) + wire the ≤20% ceiling to the REAL ledger.
3. **Re-measure** the built classifier's honest primary-key/macro/image_role accuracy on fresh substrate via `run_live()`.
4. **(contingent) Improve** macro (geometry ~50% — owned by S1-geometry, not S3) + image_role if the fair re-measure still falls short.
**No "0.93 / one-command / already-passing" claim is valid for the built classifier until leg 3 produces a number on fresh perception.**

→ primary-key 13/14 = 0.929 (PASS ≥0.85); full-tuple 12/14 = 0.857 (PASS ≥0.80); macro 13/14; image_role 14/14; text_substructure 13/14; cadence 14/14; callout_intent 3/4 (probation, advisory); confusion: `multi_column → two_pane : 1` (the 17_ miss).

This proves the harness math BEFORE the live S2/S3 classifier exists. When S2/S3 land, swap the synthetic `build_demo_rows()` emitted set for the real classifier output over the 14 held-out perceptions; the gold + scoring stay identical.

---

## 5. What a PASS / FAIL means

**PASS (gate closes P2-4c):**
- primary-key top-1 ≥ 0.85 AND full-tuple ≥ 0.80 on the live classifier's emitted-vs-gold over the 14.
- DEFAULT ≤ ~25%; escalation rate in (0%, 20%]; foreground-gate + quarantine tripwires green.
- Contamination check clean (< 2 of 14 want a gated/retired pattern).
→ The catalog-as-implemented conforms to the operator-confirmed catalog-as-intended; P2-4c ships; tier-2.5/3 + callout_intent stay quarantined pending their harvests.

**FAIL (one or more):**
- top-1 < 0.85 or full-tuple < 0.80 → the S1/S2/S3 implementation diverges from gold; triage per-axis + the confusion matrix to find the diverging axis (macro vs image-role) and the specific slides; fix the geometry/tier/escalation logic; re-run (NOT re-label the gold — gold is frozen).
- DEFAULT > 25% → anti-vacuity ceiling breached (route-everything-to-default classifier); FAIL.
- escalation rate > 20% → "secretly LLM-always" detector trips; FAIL.
- escalation rate = 0% with a known-ambiguous slide → dead-code detector; FAIL.
- contamination ≥ 2/14 → a retired pattern was overfit; the 0.85 is contaminated; re-open the retirement decision (party-mode), do NOT silently pass.

**Frozen-gold discipline:** P2-4b NEVER re-labels gold to make the classifier pass. The gold is the operator-confirmed frozen authority; only the implementation moves.

---

## 6. Deliverables of this pre-stage

| Deliverable | Path | Status |
|---|---|---|
| Frozen gold (14 tuples) | `_bmad-output/implementation-artifacts/reading-path-holdout-gold-labels-2026-06-23.md` | DONE |
| Scoring harness | `scripts/analysis/reading_path_p2_4b_score.py` | DONE (ruff-clean) |
| Harness self-test | `tests/analysis/test_reading_path_p2_4b_score.py` | DONE (18 pass) |
| This spec | `_bmad-output/implementation-artifacts/spec-p2-4b-conformance-finalize.md` | DONE |

**Not in this pre-stage (gated on S2+S3):** the live classifier run over the 14 held-out perceptions + the real emitted-vs-gold score + the escalation ledger + the tripwire run. Those execute once S2/S3 are merged and green.

---

## 7. Authority chain
`holdout-confirm-deny-kit-2026-06-22.md` (verdicts + RESULTS) → `reading-path-gap-resolution-G2-G3-2026-06-22.md` (A6 IN/OUT + G2 tier rubric + G3 escalation) → `reading-path-patterns-catalog.md` v1.1 §9 (build contract) / §9.4 (A6) / §9.5 (RED fixtures) / §11 (D1–D3) → this spec + the harness + the frozen gold.
