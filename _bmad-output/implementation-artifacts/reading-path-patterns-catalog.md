# Reading-Path Patterns Catalog — v0-DRAFT (for operator review round 1)

**Status:** DRAFT — proposed identifications + definitions + script-writer guidance grounded in the live gpt-5.5 scan of 54 working slides (`reading-path-corpus-scan/evidence-report.md`). NOT yet built into the production classifier; awaiting operator review rounds.
**Version:** v0-draft 2026-06-21. **Design authority:** `reading-path-patterns-design-decisions-2026-06-21.md`. **Held-out:** the 14 reserved slides were NOT used here.
**Reading direction:** all patterns assume Western LTR (hard-coded assumption; revisit for RTL/CJK).

## Governance header — admission rubric (a pattern is in the catalog ONLY if ALL hold)
1. **N≥4 corpus exemplars** spanning **≥2 content genres** (kills topic-creep).
2. **Behavioral-distinctness:** narrates in a *different order/grouping* than every other pattern — stated as a one-line **narration-delta**. No delta → not a pattern.
3. **Non-overlap:** not a sub-case of an existing pattern.
4. **Stability:** survives clustering perturbation.
Failing any bar → the slide routes to the **DEFAULT** (`top_down` position-order), not a new pattern. **No 2× quota** — the catalog lands where evidence leaves it.

## Headline finding from the scan
The deterministic `_looks_z` predicate **over-claimed `z_pattern` on 43/54 slides (24 of them false-positives)** — it fires on any ≥4-element 2×2 spread containing a headline/callout kind, swallowing focal/visual-hero slides that have **no genuine diagonal sweep**. The two genuinely emergent patterns the corpus surfaced are **`image_dominant`** (15) and **`diagram_driven`** (9) — both currently mislabeled Z. Fixing this over-claim is the #1 job of the hybrid (c) classifier.

---

## ADMITTED PATTERNS

### 1. `z_pattern` — sparse diagonal sweep  *(genuine N≈19)*
- **structural_signature:** sparse slide (text-density low/medium), 4–7 elements in a 2×2 spread, **no single element ≥45% area**, no numeric markers, no dominant focal visual.
- **perceptual_rationale:** with nothing commanding fixation, the LTR eye runs its default trajectory.
- **canonical_scan_order:** top-left → top-right → (diagonal) → bottom-left → bottom-right.
- **entry_anchor:** top-left element. **resolution_beat:** bottom-right element.
- **dwell_profile:** even, light dwell across the four corners; decorative elements skipped.
- **emphasis_targets:** top-left (entry) + bottom-right (resolution).
- **narration_delta:** *only* pattern with a true diagonal corner-to-corner sweep.
- **modifier_handling:** a CTA lands the resolution_beat on the CTA.
- **near_misses:** `image_dominant` (has a focal hero — Z does not); `headline_dominant` (single text fixation, not a sweep).
- **exemplars:** `2_A-Structured-Approach-to-Developing-Ideas`, `2_Same-Process-Different-Context`, `13_Problem-Solving-Framework`, `5_The-Real-Barrier`, `7_From-Idea-to-Value-The-Framework`.
- **confidence_and_fallback:** if focal-singularity detected → reclassify (image/diagram); else default.

### 2. `image_dominant` — focal visual hero first  *(NEW; N=15; photo×14 + illustration×1)*
- **structural_signature:** one **photo/illustration** element is the largest area AND ≥~2× the next; supporting text beside/below.
- **perceptual_rationale:** a photographic/illustrative subject (face, scene, object) captures fixation before any text.
- **canonical_scan_order:** focal image subject → primary text (title/claim) → supporting text → CTA.
- **entry_anchor:** the focal image's subject. **resolution_beat:** the claim/CTA the image illustrates.
- **dwell_profile:** long dwell on the image subject (narrate what's *in* it), medium on the paired claim, skip decorative chrome.
- **emphasis_targets:** the image subject + the paired headline.
- **narration_delta:** narration LEADS with the perceived image content ("a clinician at a bedside…"), not the top-left text — the single biggest divergence from Z.
- **modifier_handling:** CTA → resolution beat; stat overlay → dwell within the image beat.
- **near_misses:** `z_pattern` (no focal hero); `diagram_driven` (hero is a structured diagram, not a photo).
- **exemplars:** `10_Youre-Already-an-Innovator`, `16_Motivation-in-Health-Interventions`, `18_The-future-of-population-health-needs-YOU`, `7_Cognitive-Skills-in-Action`, `8_Our-Mission-Transform-Insights-Into-Impact`, `4_Leadership-and-Risk-Awareness`, `6_Idea-vs-Opportunity` (+8 more).
- **confidence_and_fallback:** focal element kind ∈ {photo, illustration, image} drives this; else consider `diagram_driven` or default.

### 3. `diagram_driven` — structured-visual internal logic  *(NEW-CANDIDATE; N=9; diagram focal)*
- **structural_signature:** the dominant element is a **diagram/canvas/framework** (largest area, structured sub-parts) — e.g., a 2×2 canvas, a process figure, a relationship map.
- **perceptual_rationale:** the eye follows the diagram's *internal* structure (its arrows/cells/flow), not the slide's outer geometry.
- **canonical_scan_order:** diagram entry node → follow the diagram's internal flow → surrounding labels → caption.
- **entry_anchor:** the diagram's labeled start/center. **resolution_beat:** the diagram's conclusion/output node or caption.
- **dwell_profile:** dwell proportional to the diagram's own emphasis; narrate the structure's logic, not box-by-box geometry.
- **emphasis_targets:** the diagram's focal node + its takeaway.
- **narration_delta:** narration tracks the *diagram's* logic (which may run against slide geometry) — distinct from both Z and image_dominant.
- **near_misses:** `center_out` (radial hub → use center_out); `sequence_numbered` (if the diagram is explicitly numbered → use sequence_numbered); `image_dominant` (photo hero, not structured).
- **exemplars:** `12_Value-Proposition-Canvas`, `19_Your-Unique-Leadership-Qualities`, `1_The-Modern-Clinicians-Dilemma`, `2_An-Era-of-Unprecedented-Change`, `9_The-Transformation` (+4 dividers).
- **OPERATOR-REVIEW FLAG:** this is the catalog's least-settled entry — it may partly collapse into `center_out` / `sequence_numbered` on closer look. Your call on whether `diagram_driven` is one pattern, splits, or folds.
- **confidence_and_fallback:** if radial → center_out; if numbered → sequence_numbered; else default.

### 4. `sequence_numbered` — numerals override geometry  *(genuine N=5)*
- **structural_signature:** explicit ordinal markers (1-2-3, step A/B/C, numbered list).
- **perceptual_rationale:** the eye obeys numerals regardless of position.
- **canonical_scan_order:** ascending ordinal order.
- **entry_anchor:** item 1. **resolution_beat:** final item.
- **dwell_profile:** even dwell per step; emphasis on step verbs.
- **narration_delta:** strict numeric order — the only pattern where geometry is *ignored*. Highest classifier confidence.
- **near_misses:** prose like "first… then…" WITHOUT per-element numerals must NOT trigger this (the `_has_ordinal` over-trigger — calibration rider).
- **exemplars:** `3_The-Ideal-State-5-Step-Process`, `5_Obstacles-in-Building-the-Ideal-State`, `10_Seize-the-Opportunity`, `1_Turning-Ideas-into-Action-HII-Meeting-Preparation`, `3_The-Education-Gap`.

### 5. `f_pattern` — dense-text left-margin skim  *(genuine? N=3 — CALIBRATION FLAG)*
- **structural_signature (intended):** text-heavy (paragraphs/bullets, left-aligned); reader skims top line → shorter 2nd line → left-margin vertical.
- **canonical_scan_order:** top line full → second line partial → left-edge vertical skim.
- **narration_delta:** left-margin vertical skim (vs Z's diagonal).
- **OPERATOR-REVIEW FLAG:** the deterministic predicate fired on 3 **LOW-density, horizontal, 3-element** slides (`1_From-Idea-to-Action`, `4_The-Critical-Gap`, `7_Healthcares-Most-Valuable-Asset`) — the OPPOSITE of dense-text. The current `f_pattern` heuristic looks **mis-calibrated**; these 3 are likely `image_dominant` or simple title slides. Recommend re-examining the F predicate.
- **near_misses:** `z_pattern` (diagonal vs vertical-skim); density is the discriminator.

### 6. `center_out` — central anchor radiates  *(genuine N=1)*
- **structural_signature:** a dominant central element (0.35–0.65 center band) with satellites radiating.
- **canonical_scan_order:** center → satellites clockwise/by-salience → back to center.
- **narration_delta:** hub-first then spokes, returning to center (absorbs hub-and-spoke).
- **exemplars:** `19_You-as-the-Ideal-Public-Health-Leader`.
- **near_misses:** `diagram_driven` (structured flow, not radial).

### 7. `top_down` — vertical stack  *(genuine N=2; ALSO the DEFAULT)*
- **structural_signature:** vertically-stacked elements, high text density, no focal hero, no numerals.
- **canonical_scan_order:** top → bottom, left→right within a row.
- **narration_delta:** plain physical reading order — claims nothing about diagonals or hierarchy.
- **exemplars:** `21_Summary-The-Journey-of-Public-Health-Leadership`, `10_Delivering-Value-in-Public-Health`.

---

## DEFAULT / FALLBACK (defined entry, not a failure state)
**`top_down` position-order** is the **no-confidence fallback** (Caravaggio + operator-ratified — NOT Z). When the hybrid is low-confidence or geometry/LLM disagree with no clear winner: narrate elements in perceived bounding-box order (top→bottom, left→right within rows). `free_form` (overlapping art / no clean rows) = position-order with a softer, impressionistic cadence. The default must be **observable/counted** so a run where many slides fall to default is visible.

## DEFINED-BUT-NOT-ADMITTED (zero evidence in the working set; deferred — no quota)
`two_up_comparison`, `triptych_3up`, `grid_quadrant`, `multi_column`, `headline_dominant` (text-hero) — **0 genuine fits** in the 54 working slides. Per the N≥4 rubric they are NOT admitted now. Definitions retained as stubs; admit only if the held-out set or a future corpus surfaces ≥4 exemplars across ≥2 genres. (Note: `headline_dominant` candidates exist but their dominant-by-area element was a photo/diagram, so they classified as `image_dominant`/`diagram_driven` — operator may want a text-hero split.)

---

## PROPOSED IDENTIFICATIONS (54 working slides; AFTER the hybrid reassigns over-claimed Z)
**Distribution:** `image_dominant` 15 · `z_pattern` 19 · `diagram_driven` 9 · `sequence_numbered` 5 · `f_pattern` 3 (flagged) · `top_down` 2 · `center_out` 1.

**image_dominant (15):** 10_Youre-Already-an-Innovator, 14_What-Drives-Us-Toward-Opportunities, 16_Motivation-in-Health-Interventions, 18_The-future-of-population-health-needs-YOU, 20_Resources-to-Enhance-Your-Journey, 2_Structured-Approach-to-Population-Health, 4_Leadership-and-Risk-Awareness, 5_Common-Obstacles, 6_Idea-vs-Opportunity, 6_Ideas-vs-Opportunities-A-Crucial-Distinction, 6_Your-Hidden-Superpower, 7_Cognitive-Skills-in-Action, 8_Our-Mission-Transform-Insights-Into-Impact, 8_The-Science-Behind-the-Connection, 9_Expected-Value-vs-Expected-Utility.

**diagram_driven (9):** 12_Value-Proposition-Canvas, 19_Your-Unique-Leadership-Qualities, 1_, 1_The-Modern-Clinicians-Dilemma, 2_, 2_An-Era-of-Unprecedented-Change, 5_, 6_, 9_The-Transformation.

**z_pattern (19, genuine):** 10_Delivering-Value-in-Population-Health, 12_Value-Proposition-Canvas-Aligning-Products-with-Customer-Needs, 13_Problem-Solving-Framework, 15_Understanding-Motivation-Types, 16_Motivation-in-Public-Health-Interventions, 17_Leadership-Examples-in-Population-Health, 22_Your-Next-Steps, 2_A-Structured-Approach-to-Developing-Ideas, 2_Same-Process-Different-Context, 3_, 3_Two-Processes-One-Mind, 4_, 4_Leadership-and-Risk-Awareness-in-Public-Health, 4_The-Innovators-DNA-is-Clinical-DNA, 5_The-Real-Barrier, 7_, 7_From-Idea-to-Value-The-Framework, 8_Expected-Value-vs-Expected-Utility, 9_From-Bedside-to-Innovation.

**sequence_numbered (5):** 10_Seize-the-Opportunity, 1_Turning-Ideas-into-Action-HII-Meeting-Preparation, 3_The-Education-Gap, 3_The-Ideal-State-5-Step-Process, 5_Obstacles-in-Building-the-Ideal-State.

**f_pattern (3, FLAGGED likely-misfit):** 1_From-Idea-to-Action-Population-Health-Leadership, 4_The-Critical-Gap, 7_Healthcares-Most-Valuable-Asset.

**top_down (2):** 10_Delivering-Value-in-Public-Health, 21_Summary-The-Journey-of-Public-Health-Leadership.

**center_out (1):** 19_You-as-the-Ideal-Public-Health-Leader.

> The reassignment of the 24 over-claimed-Z slides → image_dominant/diagram_driven is the PROPOSAL the hybrid will encode (LLM hint + tightened `_looks_z`). The deterministic classifier as-is still labels these `z_pattern`; the hybrid fixes it.

---

## SCRIPT-WRITER GUIDANCE (Irene Pass-2 — per-pattern narration instruction)
- **image_dominant:** open by narrating *what is in the image* (the perceiver reports the subject), then connect to the headline claim, then supporting points; land on the takeaway/CTA. Do NOT recite the image as "an image of…"; speak to its content.
- **z_pattern:** narrate corner-to-corner — orient (top-left), expand (top-right), develop (diagonal/bottom-left), resolve (bottom-right).
- **diagram_driven:** narrate the diagram's *logic* (the flow/relationship it encodes), entry node → output; let the structure, not the slide grid, set the order.
- **sequence_numbered:** strict 1→N; one beat per step; emphasize the step's verb.
- **top_down / DEFAULT:** walk elements in physical reading order; even cadence; safe for any unmatched slide.
- **center_out:** hub first (the central claim), then spokes, brief return to the hub for closure.
- **f_pattern:** lead the top line, sample the left margin; for dense text, summarize don't recite.
- **Universal:** skip decorative elements (if the eye doesn't stop, the voice doesn't); 1–2 emphasis targets per slide; the resolution beat is the transition to the next slide.

## OPEN QUESTIONS FOR OPERATOR REVIEW (round 1)
1. **`diagram_driven`** — keep as a distinct pattern, or fold parts into `center_out`/`sequence_numbered`? (least-settled entry.)
2. **`f_pattern` mis-calibration** — the 3 fits are low-density; re-examine the F predicate / reassign those 3?
3. **`headline_dominant`** — do you want a text-hero pattern split out of `image_dominant` (when the first fixation is a big headline over a background photo, e.g., the dividers "Apply." / "THE INFLECTION POINT")?
4. **Unpopulated patterns** — OK to leave `two_up_comparison`/`triptych_3up`/`grid_quadrant`/`multi_column` defined-but-not-admitted until evidence appears (no quota)?
5. **Bare `N_.png` dividers** — treat as a divider sub-case (short headline + background visual), or just image_dominant/diagram_driven as classified?
