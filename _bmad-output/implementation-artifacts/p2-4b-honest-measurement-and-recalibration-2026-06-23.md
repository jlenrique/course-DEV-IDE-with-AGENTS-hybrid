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

## 4.5. Party-mode green-light disposition (2026-06-23) — GREEN-WITH-AMENDMENTS

Roundtable: Winston (architect), John (PM), Murat (test architect), Mary (analyst), Amelia (dev). **Verdict: unanimous GREEN-WITH-AMENDMENTS** (no BLOCK, no impasse → Quinn→John chain not triggered). Binding amendments, consolidated:

### A. Scope & shape — keep ONE dual-gate NEW CYCLE story
- 3 coordinated work items, **declared hard order A → B → C** (geometry is isolable and feeds nothing downstream; escalation C must be wired AFTER B's tiering is corrected, else re-opened). NOT split — the acceptance metric is a joint function of all three; splitting adds an integration seam without reducing reviewability.
- **Three instrumented internal seams**: post-A geometry-only macro number, post-B image_role number, post-C escalation-rate number — recorded in Completion Notes BEFORE the joint re-run, plus a **per-axis before/after delta table** in T11 (attribution without re-running the arc).

### B. The bar — TIERED, pre-registered behind a veil of ignorance (n=14 quantizes at 1/14 ≈ 0.071)
- **SUCCESS bar (clean close, autonomous):** primary-key ≥0.857 (12/14) AND full-tuple ≥0.80 AND escalation ∈(0%,20%] AND per-axis floors **macro ≥0.85 + image_role ≥0.70** (all simultaneous, no trading — Murat) AND default ≤25% AND tripwires green.
- **CONDITIONAL-PASS tier [0.70,0.85) primary-key WITH macro+image_role demonstrably fixed** → ratify the measured floor, decide close-at-bar vs one-more-cycle. **⚠️ This sub-0.85 tier is an OPERATOR-GATED governance decision** (goal stop-condition: "accepting a conformance bar below 0.85") — pre-registration requires operator sign-off; NOT taken autonomously.
- **FAIL:** <0.70 primary-key OR a known-broken axis still broken → re-dispatch (no impasse-chain theater; "axis X didn't move, here's why, go again").
- Bar stated in **slide-counts**, not deceptively-precise decimals; **CI caveat recorded** (Murat: at 12/14 the Wilson interval ≈ [0.60,0.96] — a *directional* pass, not a precision claim).

### C. Overfit fences (the consumed-14 is now a DEV set the dev can see — binding)
- **A1 blind-tuning / no-peeking:** dev tunes against AGGREGATE axis numbers, NOT per-slide gold; the final per-slide conformance score is computed ONCE by an independent party (Claude T11), first-run-stands.
- **A2 per-axis floors (above) + perturbation guard:** re-perceive 3–4 slides a 2nd time under the same role_tier and/or reorder element lists → emitted tuple must be STABLE (catches knobs fit to surface noise).
- **A3 logic-only audit:** NO `if slide_id == …`, no gold-keyed lookup tables, no counts tuned to 14; every fix must articulate a generalizable RULE (fix the mechanism, not the symptom on slide N).
- **C1 gold content-hash** recorded in story §0, re-verified at T11 (immutability enforced, not promised).
- **C2 classifier-logic-only diff fence:** the fix must not touch the perception layer, the gold, or the scoring harness denominator. T11 inspects the diff surface.
- **C3 provenance label on every number:** `(built-classifier, frozen-fresh-14, gold-known-to-dev)` — never bare (direct H1/H2/H3 + H4 remediation).

### D. T1 PRECONDITIONS (resolve before any tuning)
- **Escalation-ledger wiring is a PRECONDITION, not a tripwire** (Murat): if the re-run still reads the scaffold ceiling rather than the real ledger, the escalation number is meaningless and the leg is invalid. Fix the wiring first.
- **Dominant-image-role ground truth** (Murat + Winston): does the frozen gold encode an authoritative slide-level dominant role? **If YES** → promote the rule OUT of the analysis scaffold (`_dominant_image_role`) INTO `reading_path_classifier.py` substrate as an emitted field, **delete the scaffold** (no shadow second path), and fold the decorative-vs-illustrative rubric INTO that emission (Winston: the naive max-load-bearing fold is likely itself part of the 21% defect). **If NO** → the image_role fold is partly unmeasurable; mark it NOT-MEASURED rather than score against a scaffold, and adjust the floor. T1 must answer this yes/no before tuning.

### E. Governance & evidence
- **Consumed-reserve note RATIFIED** (4/5 + Amelia pending): labeling the 14 consumed their naivety → they are now a **consumed/non-naive DEV set**; any score on them is a **resubstitution (upper-bound) estimate**, labeled consumed/non-naive wherever cited. This cycle closes P2-4b **CONFORMANCE** (logic fixed + measured on the dev set), **NOT generalization / trial-readiness.**
- **Tier-2 gate — FRESH naive holdout REQUIRED before any "ready for trial" claim** (John + Mary binding; **Mary plants a firm dissent against claiming trial-ready off the consumed-14**): operator labels ≥12–15 NEW slides, strictly naive (no confirm/deny exposure, no dev sight of gold until after scoring, first-run-stands), scored in a SEPARATE gate. Filed to deferred-inventory now (see below).
- **Per-slide gold-ambiguity audit** recorded as evidence (Winston, no re-label) to keep the honest-partial tier defensible.
- **Harvest anti-pattern H4 "inherited green"** (Mary): a passing number adopted from an adjacent artifact without re-deriving it on the artifact under test (the 0.93 belonged to the catalog-approach; it was transferred onto the built classifier because both said "escalation"). Guard: a conformance number is valid only for the exact artifact that produced it; run the artifact-under-test on fresh substrate before believing any number about it. → `docs/trials/cross-trial-learnings.md`, cross-ref H1/H2/H3.

### F. Amelia (dev) additions + orchestrator resolutions of two divergences
- **RED-first test scaffolding (binding, Amelia):** three per-axis fixtures (macro-only, image_role-only, escalation-only) extracted from the 14 frozen perceptions, authored RED before logic; the full 14-slide harness as the integration gate after each axis; **a pinned S1/S2/S3 regression snapshot** — capture what the current predicate/geometry emit on the existing green-test slides and assert the INTENDED deltas explicitly (a rewrite that passes the new bar but silently flips an S3-green slide is a T11 reject). Tripwires wired as harness assertions, not eyeballed.
- **Divergence 1 — sequencing (RESOLVED by synthesis, no impasse):** Winston/John = A→B→C (escalation last; its disagreement-trigger depends on A/B being trustworthy); Amelia = C→A→B (escalation first as an orthogonal cheap confidence anchor). **Resolution:** **A → B → C**, BUT split C: the **orthogonal `callout_kind_present` predicate-narrowing may land early** as Amelia's confidence anchor (it doesn't depend on A/B), while the **ceiling-wiring-to-real-ledger + the geometry/role-disagreement escalation trigger land last**, after A/B are corrected. Image_role tiering + the authoritative-dominant fold is the genuinely-hard last sub-step of B (the fold consumes tier output). All five agree the coupled pair (A macro + B image_role) sequences with the **fold LAST**.
- **Divergence 2 — fallback bar level (OPERATOR-GATED; spread recorded, NOT resolved autonomously):** Amelia 8/14 (0.57) + macro≥0.78 + image_role≥0.50; Winston 9/14 (0.643) + per-axis movement; John "axes-fixed" (macro≥0.80, image_role≥0.70) as the pass-bar; Murat accepts the 0.85 gate but with simultaneous per-axis floors (macro≥0.85, image_role≥0.70). **Amelia files a NAMED DISSENT against any 0.85-hard-or-FAIL framing** (on n=14 it pressures discriminator-overfitting). Since accepting any sub-0.85 bar is operator-gated (goal stop-condition), the exact fallback level is presented to the operator with this spread.

### T1 precondition — RESOLVED (read-only check, 2026-06-23)
**Does the frozen gold encode an authoritative per-slide dominant image_role?** → **YES** (the gold row carries an `image_role` field, e.g. `1`). The classifier currently emits only per-element `image_roles` + `image_role_flags` (NO slide-level dominant); the dominant is synthesized by the analysis-script scaffold `_dominant_image_role`. → **Item B is NOT blocked** (ground truth exists). The work = promote an authoritative slide-level `dominant_image_role` emission into `reading_path_classifier.py` substrate (deterministic, area/geometry-weighted, co-located with per-element role_tier so it's auditable + re-derivable without re-perception), delete the scaffold, fold the decorative-vs-illustrative rubric INTO that emission.

### Operator-gated item (surfaced at wrap-up, NOT decided autonomously)
Pre-registering the **sub-0.85 conditional-pass tier** = "accepting a conformance bar below 0.85" per the goal's stop conditions → requires operator sign-off. The Codex handoff is authored at the **≥0.857 (12/14) success bar + per-axis floors (macro≥0.85, image_role≥0.70) + all overfit fences**; the conditional-pass tier + its level (the spread above) is presented to the operator as a single decision at wrap-up. Default if the operator does not pre-register a fallback: hard ≥0.857 gate, with Amelia's dissent on record.

## 5. Authority chain
`spec-p2-4b-conformance-finalize.md` §4 → this measurement+diagnosis → (party green-light) → Codex dev prompt → Claude T11 re-measure → P2-4b PASS/FAIL verdict → P2 epic close.
