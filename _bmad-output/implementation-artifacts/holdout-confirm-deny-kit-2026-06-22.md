# Held-Out 14 — Reading-Path Confirm/Deny Kit (P2-4b, flipped methodology)

**Date:** 2026-06-22. **Author:** Claude (catalog v1 approach). **For:** operator confirm/deny.
**Methodology (operator-authorized flip):** the operator already did round-1 training (26 slides); the held-out reserve is no longer kept naive. **Claude labels these 14 via the catalog v1 approach; the operator confirms/denies each.** This supersedes the prior "operator-labels-independently-then-score" P2-4b design (recorded for governance; flag to party at the next gate — not blocking). NOTE: labeling these 14 **consumes the held-out reserve** — they are no longer naive for any future independent-label scoring (operator-accepted).
**Provenance:** live gpt-5.5 `perceive_png` over the 14 held-out PNGs, 14/14 perceived, 0 errors (`reading-path-holdout-scan/holdout-perception-summary.json` + per-slide `perceptions/*.json`). First-run-stands; no retry-to-green. Labels are my catalog-guided judgment from the PERCEIVED elements/geometry — **not** the filenames.
**Catalog authority:** `reading-path-patterns-catalog.md` v1 (tuple `{macro_layout × image_role × text_substructure × narration_cadence}` + 6 VO principles + A1–A10).

---

## How to review (≈20–30 min)
1. Open each PNG by filename from `C:\Users\juanl\OneDrive\Desktop\z-2026-06-21`.
2. Read my proposed **primary pattern + scan order + image-role calls** against what your eye actually does.
3. Mark each row **CONFIRM** or **DENY** (and for DENY, the correction). The detail entries below carry my rationale, confidence, and top near-miss so you can see *why* I called it.
4. Pay extra attention to the **🚩 scrutiny flags** (low-confidence / known-wrong-default / gate tests).

**What your confirm/deny yields (A6 metric):** confirmed primary-key `{macro_layout × image_role}` ÷ 14 = the **top-1** number; per-axis confirm rate + full-tuple confirm rate fall out of the per-field marks. `multi_column` is quarantined (excluded from the top-1 denominator until N≥4) — none of the 14 is a pure multi_column anyway.

## Distribution of my proposed primary labels (14)
| primary reading_path | count | slides |
|---|---|---|
| `two_up_comparison` | 4 | 8_, 9_, 15_, 17_ |
| `enumerated_process` | 4 | 3_, 11_, 13_, 21_ |
| `top_down` (incl. card_grid + DEFAULT) | 4 | 5_, 18_, 20_, 22_ |
| `split_image_text` | 2 | 1_, 6_ |
| `diagram_driven` | 0 | — (gate held: 2 `kind:diagram` elements ruled tier-1 decorative — see 8_, 13_) |
| `multi_column` (pure) | 0 | — (5_, 17_ carry multi-peer substructure but aren't pure) |
| `text_hero_divider` / `center_out` | 0 | — |

**Gate tests inside this set (please scrutinize):**
- **`diagram_driven` foreground-gate:** `8_` (monitor_chart `kind:diagram`) and `13_` (rounded bars `kind:diagram`) — I ruled BOTH **tier-1 decorative**, NOT instructional → NOT `diagram_driven`. This is exactly the `kind:diagram`≠instructional trap; confirm I gated correctly.
- **🚩 known-wrong-default anchors:** `5_` and `8_` — the naive top-to-bottom / geometric default leads with a **decorative photo** (top banner / right-third photo). VO should SKIP it and lead with the title/question/comparison. These are the anti-vacuity anchors (default IS wrong here).
- **Demote-z evidence:** the current (pre-P2-4c) 7-enum classifier called **8 of 14 `z_pattern`**; under v1 none are z (they resolve to comparison / process / peer-grid / split). Confirms the over-claim the refactor fixes.

---

## Confirm/deny summary table
| # | slide (filename, .png) | proposed primary | macro_layout | dominant image_role | text_substructure | cadence | conf | CONFIRM / DENY |
|---|---|---|---|---|---|---|---|---|
| 1 | `1_Diagnosis-Innovation` | split_image_text | split_image_text | 1 decorative | hero_message+sentence | moderate | high | ☐ / ☐ |
| 2 | `3_Achieving-the-Ideal-State` | enumerated_process | single_text_block | 4 pointer (icons) | enumerated_process (5 steps) | dense | med-high | ☐ / ☐ |
| 3 | `5_Check-Your-Understanding` 🚩 | top_down | single_text_block (+banner) | 1 decorative | hero question + 3 peer options | moderate | medium | ☐ / ☐ |
| 4 | `6_All-of-them-belong-to-BOTH` | split_image_text | split_image_text | 1 decorative | hero_message+sentence | sparse-moderate | high | ☐ / ☐ |
| 5 | `8_Decision-Making-Foundations` 🚩 | two_up_comparison | split_image_text | 1 decorative (photo+monitor) | comparison_pair (EV vs EU) | moderate | high | ☐ / ☐ |
| 6 | `9_Comparing-Expected-Value-and-Expected-Utility` | two_up_comparison | two_pane | none | comparison_pair + synthesis | dense | high | ☐ / ☐ |
| 7 | `11_Value-Creation-in-Innovation` | enumerated_process | multi_column | none | enumerated_process (01/02/03) | dense | high | ☐ / ☐ |
| 8 | `13_Effective-Problem-Solving-Approach` 🚩 | enumerated_process | multi_column | 1 decorative (bars) | enumerated_process (3 steps) | dense | medium | ☐ / ☐ |
| 9 | `15_Types-of-Motivation` | two_up_comparison | split_image_text | 2 illustrative | comparison_pair (extrinsic vs intrinsic) | moderate | high | ☐ / ☐ |
| 10 | `17_Examples-of-Effective-Leadership-in-Public-Health` 🚩 | two_up_comparison | two_pane | 2 illustrative | two parallel panels (Global/Local) | dense | medium | ☐ / ☐ |
| 11 | `18_The-Future-of-Public-Health-Leadership` | top_down | single_text_block | none | dense_exposition (+Questions? callout) | dense | high | ☐ / ☐ |
| 12 | `20_Resources-for-Entrepreneurship-and-Innovation` | top_down | card_grid (2×2) | none | peer_boxes + summary | dense | high | ☐ / ☐ |
| 13 | `21_Key-Takeaways` | enumerated_process | split_image_text | 1 decorative | enumerated_process (4 numbered) | moderate | med-high | ☐ / ☐ |
| 14 | `22_Next-Steps-Your-Path-Forward` | top_down | card_grid (2×2) | 4 pointer (icons) | peer_boxes + closing | dense | medium | ☐ / ☐ |

---

## Per-slide detail (rationale · scan order · near-miss · current-classifier contrast)

### 1. `1_Diagnosis-Innovation` — *Diagnosis = Innovation*
- **Perceived:** left full-height clinician/patient photo | right title + one body sentence; whitespace-heavy right.
- **Tuple:** macro `split_image_text` · image_roles [photo→**1 decorative**] · text `hero_message`+sentence · cadence `moderate`. **Primary: `split_image_text`.**
- **Scan order:** title → body sentence (SKIP photo, tier-1). **VO:** title-anchor → one-line synthesis; do not narrate the photo.
- **Confidence:** high. **Near-miss:** text_hero (rejected — there's a paired body sentence + a half-slide photo). **Current classifier:** `top_down` (missed the split).

### 2. `3_Achieving-the-Ideal-State` — *Achieving the Ideal State*
- **Perceived:** title TL; 5 vertically-stacked chevron panels (icon + heading + paragraph): Build it → Launch it → Iterate → Measure it → Learn; summary at bottom.
- **Tuple:** macro `single_text_block` (vertical) · image_roles [5 icons→**4 pointer**] · text `enumerated_process` (5 process steps) · cadence `dense`. **Primary: `enumerated_process`.**
- **Scan order:** title → step1…step5 (icon types each step, not narrated) → summary. **VO:** walk the 5-step cycle in order; icons cue the step, no image narration.
- **Confidence:** med-high. **Near-miss:** top_down peer-list (rejected — Build→Launch→Iterate→Measure→Learn is a sequential process, not coordinate peers). **Current:** `z_pattern` (over-claim).

### 3. `5_Check-Your-Understanding` 🚩 *(known-wrong-default anchor)* — *Check Your Understanding*
- **Perceived:** top photo banner (meeting, 0–36%) | title + question prompt + 3 horizontal answer boxes (Active Listening / Data Analysis / Experimentation).
- **Tuple:** macro `single_text_block` (+ top decorative banner) · image_roles [banner→**1 decorative**] · text hero question + **3 peer option boxes** · cadence `moderate`. **Primary: `top_down`.**
- **Scan order:** title → question → option L → option M → option R (SKIP banner). **🚩 The geometric default leads with the photo banner (wrong) — VO must lead with the title/question.**
- **Confidence:** medium. **Near-miss:** `multi_column` (the 3-option row read L→R). **Current:** `z_pattern` (and its scan put `top_photo` FIRST — the wrong-default this slide anchors).

### 4. `6_All-of-them-belong-to-BOTH` — *All of them belong to BOTH*
- **Perceived:** left full-height healthcare-workers photo | right large title + one explanatory sentence. (Reads as the answer/reveal to slide 5's quiz.)
- **Tuple:** macro `split_image_text` · image_roles [photo→**1 decorative**] · text `hero_message`+sentence · cadence `sparse-moderate`. **Primary: `split_image_text`.**
- **Scan order:** title → subtitle (SKIP photo). **VO:** deliver the "BOTH" punchline, then the one-line why.
- **Confidence:** high. **Near-miss:** text_hero_divider (rejected — photo half + body sentence). **Current:** `top_down`.

### 5. `8_Decision-Making-Foundations` 🚩 *(gate test + known-wrong-default)* — *Decision-Making Foundations*
- **Perceived:** left two-thirds title + two columns (Expected Value | Expected Utility, header+bullets); right third full-height medical-office photo containing a monitor showing a branching chart (`kind:diagram`).
- **Tuple:** macro `split_image_text` (photo right) carrying comparison · image_roles [office_photo→**1 decorative**, monitor_chart→**1 decorative** (NOT instructional — background, not foreground/opaque/load-bearing)] · text `comparison_pair` (EV vs EU) · cadence `moderate`. **Primary: `two_up_comparison`.**
- **Scan order:** title → Expected Value col → Expected Utility col (SKIP photo + monitor). **🚩 Gate test:** the `kind:diagram` monitor must NOT trigger `diagram_driven`. **🚩 Known-wrong-default:** the current classifier scanned the photo+monitor FIRST.
- **Confidence:** high. **Near-miss:** split_image_text (if the EV/EU pair is read as generic body rather than a contrast). **Current:** `sequence_numbered` (mis-fire — no ordinals).

### 6. `9_Comparing-Expected-Value-and-Expected-Utility` — *Comparing Expected Value and Expected Utility*
- **Perceived:** title upper-left; two side-by-side bullet boxes (Expected Utility | Expected Value); bottom summary sentence. No images. (A/B twin of slide 8 minus the photo.)
- **Tuple:** macro `two_pane` · image_roles [none] · text `comparison_pair` + closing synthesis · cadence `dense`. **Primary: `two_up_comparison`.**
- **Scan order:** title → left box → right box → bottom summary. **VO:** establish the contrast → walk each side → synthesize.
- **Confidence:** high. **Near-miss:** multi_column (rejected — 2 oppositional sides w/ subheadings, not ≥3 coordinate peers). **Current:** `z_pattern` (over-claim).

### 7. `11_Value-Creation-in-Innovation` — *Value Creation in Innovation*
- **Perceived:** title TL; three columns explicitly numbered 01 / 02 / 03 (Is the Need Real? → Does the Solution Meet the Need? → Willing to Pay?); wide summary bottom.
- **Tuple:** macro `multi_column` (3 cols) · image_roles [none] · text `enumerated_process` (explicit 01/02/03 — numerals override geometry) · cadence `dense`. **Primary: `enumerated_process`.**
- **Scan order:** title → 01 → 02 → 03 → summary. **VO:** walk the numbered evaluation sequence; speak the ordinals.
- **Confidence:** high. **Near-miss:** multi_column (if the numbers were mere labels — but they're a logical evaluation sequence). **Current:** `sequence_numbered` (correct via ordinals; → `enumerated_process` in v1).

### 8. `13_Effective-Problem-Solving-Approach` 🚩 *(enumerated-vs-multi_column borderline + gate test)* — *Effective Problem-Solving Approach*
- **Perceived:** title TL; three columns each topped by a pale rounded bar (`kind:diagram`); columns "Determine the Best Solution" → "Explore Additional Benefits" → "Evaluate Against Alternatives" (text: First… / Next… / Finally…); summary bottom. Bars staggered ascending L→R.
- **Tuple:** macro `multi_column` (3 cols) · image_roles [3 bars→**1 decorative** (NOT instructional)] · text `enumerated_process` (First/Next/Finally — sequential method) · cadence `dense`. **Primary: `enumerated_process`.**
- **Scan order:** title → col1 → col2 → col3 → summary. **🚩 Gate test:** the `kind:diagram` bars must NOT trigger `diagram_driven`.
- **Confidence:** medium. **🚩 Near-miss:** `multi_column` — these are borderline (3 columns; the sequence is prose-implied First/Next/Finally, not per-element numerals; the catalog warns prose-only ordinals shouldn't force a sequence). **Your call here is the key disambiguation.** **Current:** `sequence_numbered`.

### 9. `15_Types-of-Motivation` — *Types of Motivation*
- **Perceived:** left photo (balance scale w/ coins + heart) | right title + 2 stacked boxes (Extrinsic Motivation / Intrinsic Motivation, bullets).
- **Tuple:** macro `split_image_text` carrying comparison · image_roles [scale_photo→**2 illustrative** (the scale metaphor maps to the two motivation types — a light touch, not pure decoration)] · text `comparison_pair` (extrinsic vs intrinsic) · cadence `moderate`. **Primary: `two_up_comparison`.**
- **Scan order:** title → extrinsic box → intrinsic box (light optional touch on the scale image). **VO:** contrast the two motivation types; may briefly reference the balance image.
- **Confidence:** high (tuple) / the image-tier 2-vs-1 is the soft call. **Near-miss:** split_image_text (macro) / image_role 1 if you read the scale as purely decorative. **Current:** `z_pattern`.

### 10. `17_Examples-of-Effective-Leadership-in-Public-Health` 🚩 *(2-coordinate vs oppositional)* — *Examples of Effective Leadership in Public Health*
- **Perceived:** title top; two side-by-side photos (Global Leaders | Local Champions) each w/ heading + paragraph; two concluding lines bottom.
- **Tuple:** macro `two_pane` · image_roles [2 photos→**2 illustrative**] · text **two parallel panels** (Global / Local) · cadence `dense`. **Primary: `two_up_comparison`.**
- **Scan order:** title → left photo+Global → right photo+Local → bottom conclusions. **VO:** establish both example-categories → walk each → conclude.
- **Confidence:** medium. **🚩 Near-miss / gap:** these two panels are **parallel-coordinate, not oppositional** — closer to a 2-wide `multi_column` than a true contrast. The catalog has no clean "2 coordinate columns" slot (two_up=oppositional-2, multi_column=≥3). **Flagging as a possible catalog gap — your read decides.** **Current:** `z_pattern`.

### 11. `18_The-Future-of-Public-Health-Leadership` — *The Future of Public Health Leadership*
- **Perceived:** title UL; intro paragraph; centered "Questions?" callout; Q&A paragraph; conclusion paragraph. No images. (Closing/Q&A slide.)
- **Tuple:** macro `single_text_block` · image_roles [none] · text `dense_exposition` (+ a centered "Questions?" callout) · cadence `dense`. **Primary: `top_down`.**
- **Scan order:** title → intro → **Questions? callout (must get VO — callouts-always-VO)** → Q&A paragraph → conclusion. **VO:** title-anchor → scaffold → walk; voice the Questions? prompt.
- **Confidence:** high. **Near-miss:** none strong. **Current:** `top_down` (matches).

### 12. `20_Resources-for-Entrepreneurship-and-Innovation` — *Resources for Entrepreneurship and Innovation*
- **Perceived:** title top; four bordered resource cards in a 2×2 grid; summary bottom. No images (text cards).
- **Tuple:** macro `card_grid` (2×2) · image_roles [none] · text `peer_boxes` + summary · cadence `dense`. **Primary: `top_down`** (peer grid → natural row-major reading-order = the DEFAULT; semantics confirm).
- **Scan order:** title → card TL → card TR → card BL → card BR → summary (row-major). **VO:** name each resource in reading order; close on the summary.
- **Confidence:** high. **Near-miss:** multi_column (rejected — it's a 2×2 grid of peers, not ≥3 parallel columns). **Current:** `z_pattern` (over-claim — this is exactly the genuine peer-grid reading-order v1 demotes z→default for).

### 13. `21_Key-Takeaways` — *Key Takeaways*
- **Perceived:** title + 4 numbered takeaways (1–4) stacked vertically left; right full-height compass photo.
- **Tuple:** macro `split_image_text` (compass right) · image_roles [compass→**1 decorative**] · text `enumerated_process` (4 numbered takeaways) · cadence `moderate`. **Primary: `enumerated_process`.**
- **Scan order:** title → takeaway 1 → 2 → 3 → 4 (SKIP compass). **VO:** walk the four numbered takeaways in order.
- **Confidence:** med-high. **Near-miss:** split_image_text (macro) — primary could be split_image_text if you read the numbered list as ordinary body; I chose enumerated because the 1–4 numerals drive the read. **Current:** `multi_column` (mis-fire — the list is vertical, not columns; the right photo created 2 horizontal buckets).

### 14. `22_Next-Steps-Your-Path-Forward` 🚩 *(peer vs sequence)* — *Next Steps: Your Path Forward*
- **Perceived:** title; four callout sections in a 2×2 grid w/ circular icons (Assess Strengths / Build Knowledge / Connect with Mentors / Develop an Action Plan); two closing text blocks (incl. HII Meeting date).
- **Tuple:** macro `card_grid` (2×2) · image_roles [4 icons→**4 pointer**] · text `peer_boxes` + closing · cadence `dense`. **Primary: `top_down`.**
- **Scan order:** title → card TL → TR → BL → BR (row-major) → closing remember → closing meeting. **VO:** row-major through the four next-steps; icons type each, not narrated; the meeting line is a cue (date OK to state).
- **Confidence:** medium. **🚩 Near-miss:** `enumerated_process` — "Next Steps" could imply an ordered sequence rather than peer actions; I read them as coordinate (no numerals, do-in-any-order) → top_down. **Your call.** **Current:** `z_pattern`.

---

## Notes for the operator
- **DENY format:** for any DENY, note which axis is wrong (primary / macro / image_role / substructure / cadence / scan-order) and the correction — that pins the per-axis confirm rate and feeds the next tuning round.
- **My lowest-confidence calls (look here first):** `13_` (enumerated vs multi_column), `17_` (oppositional vs 2-coordinate — possible catalog gap), `5_` (top_down vs multi_column option-row), `22_` (peer vs sequence), and the `15_` image-tier (1 vs 2).
- **After your verdicts return:** I finalize the A6 numbers (primary-key top-1, per-axis, full-tuple), fold corrections into a catalog v1.1 + the P2-4c spec, and (if you want) proceed to the build. P2-4b conformance is NOT finalized until your verdicts land.
