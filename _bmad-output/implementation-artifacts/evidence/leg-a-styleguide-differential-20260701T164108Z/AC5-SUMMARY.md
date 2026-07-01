# AC#5 — Live Styleguide Differential Proof (Leg-A) — PASS

**Date:** 2026-07-01. **Branch:** dev/gamma-styleguide-library-2026-07-01. **Real Gamma, first-run-stands (re-run once after a corpus-title fix, before any differential judgment).**

## Result: PASS (no-vacuous-green)
Two CD-owned styleguides rendered the SAME 3 C1M1 Part-3 slides (LOW/MED/HIGH source-detail spectrum) into **measurably different** real Gamma output, spanning Classic + Studio.

| Detail | Classic `classic-freeform-x-cards` | Studio `hil-2026-apc-studio-image-card` | Diff |
|---|---|---|---|
| LOW `p3-low-summary` | 2400×1538 a=1.56 673KB (Tejal illustration) | 2400×1350 **a=1.778 (16:9)** 2225KB (full-bleed) | ✅ |
| MED `p3-med-physicianship` | 2400×1754 a=1.368 480KB | 2400×1350 16:9 1518KB | ✅ |
| HIGH `p3-high-maze` | 2400×1730 a=1.387 898KB | 2400×1350 16:9 3602KB | ✅ |

- `resolved_settings_differ` = True (Classic: theme njim9kuhfnljvaa / illustration / fluid / condense; Studio: production_mode studio / template g_nv5q4da69qiiu8q).
- Studio SPANNED — real 16:9 full-bleed cards passed `_assert_studio_image_card` (aspect ≥ 1.4). No fallback needed.
- Every slide distinct sha + distinct aspect + large size delta.

## Files
- True Classic outputs: `render-A-classic/A_p3-*.png` (+ `A_A_pages/`).
- True Studio outputs: `render-B-studio/gary_A_studio_0*.png` (16:9).
- `result.json` (driver's raw, contains the row-parse artifact), `result_corrected.json` (authoritative re-judge from true files), `run.log`.

## Honest caveats
1. **Edge#8 reproduced live (filed):** a single `gamma_settings` entry still paid-dispatched an UNBOUND fixture-B deck — `_normalized_gamma_settings` always returns [A, B]. Extra credits spent; the `A_*`/`B_*` split in the render dirs is this. Strengthens the filed `styleguide-retire-default-variant-pair` / single-variant-binds-one follow-on.
2. **Driver row-parse bug (scratchpad only):** the driver's `gary_slide_output` collection mixed the extra-B rows, so its inline judge compared the wrong pair; re-judged from the true files on disk. Pipeline unaffected.
3. **Title-matcher gotcha (pre-existing, concierge backlog):** first run failed `gamma.export.brief-unmatched` on a source title with an apostrophe ("The Intrapreneur's Maze" → Gamma slug "The-Intrapreneurs-Maze"); fixed by cleaning the corpus title (bodies unchanged). Not a Leg-A seam defect.
4. **Source-detail-spectrum hypothesis** (does source-detail degree modulate style expression?) is best isolated by a SAME-FORMAT A/B (Classic-vs-Classic across LOW/MED/HIGH); here the Classic-vs-Studio format gulf dominates the aspect/size metric. Natural Phase-2 experiment; LOOK verdict stays operator-eye.

## Driver
`scratchpad/leg_a_styleguide_differential_proof.py`.
