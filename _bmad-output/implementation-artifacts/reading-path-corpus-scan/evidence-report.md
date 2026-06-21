# Reading-Path Corpus Scan — Evidence Report (Phase 2b + first-pass 2c)

**Captured:** 2026-06-21T22:39:39.183721+00:00  
**Model:** `gpt-5.5` (live, no mocks; first-run-stands)  
**Corpus:** `C:\Users\juanl\OneDrive\Desktop\z-2026-06-21`  
**Working set:** 54 slides (68 corpus MINUS 14 held-out; held-out NOT perceived).  
**Perceived OK:** 54 / 54; **errors:** 0.

This is an EVIDENCE artifact (data for the orchestrator's Phase 2c admission + Phase 3 catalog draft). It does NOT author the catalog, decide admission, name patterns, or write narration-deltas.

## Feature vector — derivation (D4; two-source rule)

All features derived from the PERCEIVER output ONLY, never the classifier label:

- **primary_anchor_position** — v-band/h-band (thirds) of the largest-area positioned element (dominant fixation target).
- **anchor_count** — count of `visual_elements` carrying a usable bbox.
- **reading_vector** — `diagonal`/`vertical`/`horizontal`/`point` from the spatial spread of element centers (x_spread/y_spread vs 0.25).
- **text_density_band** — `low`(<120) / `medium`(<400) / `high` from `extracted_text` char count (Z-vs-F axis).
- **focal_singularity** — one element's area ≥0.45 of total AND ≥2× the next (single-hero signal).
- **cta_presence** — CTA token in text/kinds (content-genre TAG, not a path).
- **whitespace_dominance** — positioned elements cover <0.30 of slide area (sparsity signal).

## Distribution summary — fit-to-existing-patterns

| fitted pattern | count |
|---|---|
| `z_pattern` | 43 |
| `sequence_numbered` | 5 |
| `f_pattern` | 3 |
| `top_down` | 2 |
| `center_out` | 1 |
| **residue (UNCLASSIFIABLE)** | **0** |

**`_looks_z` over-claim flags (24):** `10_Youre-Already-an-Innovator`, `12_Value-Proposition-Canvas`, `14_What-Drives-Us-Toward-Opportunities`, `16_Motivation-in-Health-Interventions`, `18_The-future-of-population-health-needs-YOU`, `19_Your-Unique-Leadership-Qualities`, `1_`, `1_The-Modern-Clinicians-Dilemma`, `20_Resources-to-Enhance-Your-Journey`, `2_`, `2_An-Era-of-Unprecedented-Change`, `2_Structured-Approach-to-Population-Health`, `4_Leadership-and-Risk-Awareness`, `5_`, `5_Common-Obstacles`, `6_`, `6_Idea-vs-Opportunity`, `6_Ideas-vs-Opportunities-A-Crucial-Distinction`, `6_Your-Hidden-Superpower`, `7_Cognitive-Skills-in-Action`, `8_Our-Mission-Transform-Insights-Into-Impact`, `8_The-Science-Behind-the-Connection`, `9_Expected-Value-vs-Expected-Utility`, `9_The-Transformation`.

These are slides where the geometry classifier returned `z_pattern` but the feature vector indicates a headline/image/free-form-dominant slide (focal singularity, point/vertical reading vector, or sparse-with-≤3-anchors) — i.e. no genuine diagonal sweep. They are prime residue candidates and are folded into the residue clustering pass below.

## Bare `N_.png` slides (likely section dividers)

| slide_id | title | n | fitted | feature vector |
|---|---|---|---|---|
| `1_` | THE INFLECTION POINT | 6 | `z_pattern` | anchor=middle-center; n=6; vec=diagonal; dens=medium+focal |
| `2_` | Clinical reasoning = innovation thinking | 15 | `z_pattern` | anchor=middle-center; n=15; vec=diagonal; dens=medium+focal |
| `3_` | ONE ARC. Three courses. | 11 | `z_pattern` | anchor=top-center; n=11; vec=diagonal; dens=medium |
| `4_` | 9 credits. 12 months. Online. | 11 | `z_pattern` | anchor=middle-right; n=11; vec=diagonal; dens=medium |
| `5_` | Diagnose the system. | 7 | `z_pattern` | anchor=middle-center; n=7; vec=diagonal; dens=medium+focal |
| `6_` | Apply. | 7 | `z_pattern` | anchor=middle-center; n=7; vec=diagonal; dens=medium+focal/cta |
| `7_` | The cohort pressure-tests the work. | 10 | `z_pattern` | anchor=middle-center; n=10; vec=diagonal; dens=low |

## Per-slide table

| slide_id | perceived title | n | feature vector | fitted | conf | residue? |
|---|---|---|---|---|---|---|
| `10_Delivering-Value-in-Population-Health` | Delivering Value in Population Health | 9 | anchor=top-center; n=9; vec=diagonal; dens=medium+ws | `z_pattern` | 0.98 | n |
| `10_Delivering-Value-in-Public-Health` | Delivering Value in Public Health | 4 | anchor=middle-center; n=4; vec=vertical; dens=high | `top_down` | 0.98 | n |
| `10_Seize-the-Opportunity` | Seize the Opportunity | 5 | anchor=middle-right; n=5; vec=diagonal; dens=medium+focal/cta | `sequence_numbered` | 0.98 | n |
| `10_Youre-Already-an-Innovator` | You're Already an Innovator | 5 | anchor=middle-left; n=5; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `12_Value-Proposition-Canvas` | Value Proposition Canvas | 8 | anchor=middle-left; n=8; vec=diagonal; dens=high+focal/cta | `z_pattern` | 0.88 | z? |
| `12_Value-Proposition-Canvas-Aligning-Products-with-Customer-Needs` | Value Proposition Canvas: Aligning Products with | 10 | anchor=middle-left; n=10; vec=diagonal; dens=high+cta | `z_pattern` | 0.97 | n |
| `13_Problem-Solving-Framework` | Problem-Solving Framework | 9 | anchor=middle-left; n=9; vec=diagonal; dens=medium | `z_pattern` | 0.92 | n |
| `14_What-Drives-Us-Toward-Opportunities` | What Drives Us Toward Opportunities? | 7 | anchor=middle-left; n=7; vec=diagonal; dens=high+focal/cta | `z_pattern` | 0.98 | z? |
| `15_Understanding-Motivation-Types` | Understanding Motivation Types | 6 | anchor=middle-left; n=6; vec=diagonal; dens=high+cta | `z_pattern` | 0.98 | n |
| `16_Motivation-in-Health-Interventions` | Motivation in Health Interventions | 7 | anchor=middle-right; n=7; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `16_Motivation-in-Public-Health-Interventions` | Motivation in Public Health Interventions | 8 | anchor=middle-left; n=8; vec=diagonal; dens=high | `z_pattern` | 0.98 | n |
| `17_Leadership-Examples-in-Population-Health` | Leadership Examples in Population Health | 7 | anchor=middle-left; n=7; vec=diagonal; dens=medium | `z_pattern` | 0.96 | n |
| `18_The-future-of-population-health-needs-YOU` | Your Call to Action | 6 | anchor=middle-left; n=6; vec=diagonal; dens=medium+focal/cta | `z_pattern` | 0.99 | z? |
| `19_You-as-the-Ideal-Public-Health-Leader` | You as the Ideal Public Health Leader | 8 | anchor=middle-center; n=8; vec=diagonal; dens=high | `center_out` | 0.99 | n |
| `19_Your-Unique-Leadership-Qualities` | Your Unique Leadership Qualities | 9 | anchor=middle-center; n=9; vec=diagonal; dens=medium+focal | `z_pattern` | 0.99 | z? |
| `1_` | THE INFLECTION POINT | 6 | anchor=middle-center; n=6; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `1_From-Idea-to-Action-Population-Health-Leadership` | From Idea to Action: Population Health Leadershi | 3 | anchor=middle-right; n=3; vec=horizontal; dens=low+focal | `f_pattern` | 0.98 | n |
| `1_The-Modern-Clinicians-Dilemma` | The Modern Clinician's Dilemma | 6 | anchor=middle-right; n=6; vec=diagonal; dens=low+focal | `z_pattern` | 0.98 | z? |
| `1_Turning-Ideas-into-Action-HII-Meeting-Preparation` | Turning Ideas into Action: HII Meeting Preparati | 3 | anchor=middle-center; n=3; vec=vertical; dens=high+focal | `sequence_numbered` | 0.99 | n |
| `20_Resources-to-Enhance-Your-Journey` | Resources to Enhance Your Journey | 6 | anchor=middle-left; n=6; vec=diagonal; dens=medium+focal | `z_pattern` | 0.96 | z? |
| `21_Summary-The-Journey-of-Public-Health-Leadership` | Summary: The Journey of Public Health Leadership | 2 | anchor=middle-center; n=2; vec=vertical; dens=high+focal | `top_down` | 0.98 | n |
| `22_Your-Next-Steps` | Your Next Steps | 7 | anchor=top-center; n=7; vec=diagonal; dens=medium+cta | `z_pattern` | 0.94 | n |
| `2_` | Clinical reasoning = innovation thinking. | 15 | anchor=middle-center; n=15; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `2_A-Structured-Approach-to-Developing-Ideas` | A Structured Approach to Developing Ideas | 10 | anchor=bottom-center; n=10; vec=diagonal; dens=high | `z_pattern` | 0.99 | n |
| `2_An-Era-of-Unprecedented-Change` | An Era of Unprecedented Change | 8 | anchor=top-center; n=8; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `2_Same-Process-Different-Context` | Same Process, Different Context | 9 | anchor=middle-left; n=9; vec=diagonal; dens=high | `z_pattern` | 0.92 | n |
| `2_Structured-Approach-to-Population-Health` | Structured Approach to Population Health | 6 | anchor=middle-right; n=6; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `3_` | ONE ARC. Three courses. | 11 | anchor=top-center; n=11; vec=diagonal; dens=medium | `z_pattern` | 0.97 | n |
| `3_The-Education-Gap` | The Education Gap | 6 | anchor=middle-right; n=6; vec=diagonal; dens=medium+focal | `sequence_numbered` | 0.98 | n |
| `3_The-Ideal-State-5-Step-Process` | The Ideal State: 5-Step Process | 11 | anchor=top-center; n=11; vec=diagonal; dens=medium+ws | `sequence_numbered` | 0.98 | n |
| `3_Two-Processes-One-Mind` | Two Processes, One Mind | 6 | anchor=middle-left; n=6; vec=diagonal; dens=medium+ws | `z_pattern` | 0.99 | n |
| `4_` | 9 credits. 12 months. Online. | 11 | anchor=middle-right; n=11; vec=diagonal; dens=medium | `z_pattern` | 0.98 | n |
| `4_Leadership-and-Risk-Awareness` | Leadership & Risk Awareness | 6 | anchor=middle-left; n=6; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `4_Leadership-and-Risk-Awareness-in-Public-Health` | Leadership and Risk Awareness in Public Health | 6 | anchor=middle-right; n=6; vec=diagonal; dens=high+cta | `z_pattern` | 0.98 | n |
| `4_The-Critical-Gap` | The Critical Gap | 3 | anchor=middle-right; n=3; vec=diagonal; dens=low+focal | `f_pattern` | 0.98 | n |
| `4_The-Innovators-DNA-is-Clinical-DNA` | The Innovator's DNA is Clinical DNA | 7 | anchor=middle-center; n=7; vec=diagonal; dens=medium | `z_pattern` | 0.97 | n |
| `5_` | Diagnose the system. | 7 | anchor=middle-center; n=7; vec=diagonal; dens=medium+focal | `z_pattern` | 0.95 | z? |
| `5_Common-Obstacles` | Common Obstacles | 6 | anchor=middle-left; n=6; vec=diagonal; dens=medium+focal/cta | `z_pattern` | 0.98 | z? |
| `5_Obstacles-in-Building-the-Ideal-State` | Obstacles in Building the Ideal State | 7 | anchor=middle-left; n=7; vec=diagonal; dens=high | `sequence_numbered` | 0.99 | n |
| `5_The-Real-Barrier` | The Real Barrier | 10 | anchor=middle-center; n=10; vec=diagonal; dens=medium+ws | `z_pattern` | 0.98 | n |
| `6_` | Apply. | 7 | anchor=middle-center; n=7; vec=diagonal; dens=medium+focal/cta | `z_pattern` | 0.98 | z? |
| `6_Idea-vs-Opportunity` | Idea vs. Opportunity | 6 | anchor=middle-left; n=6; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `6_Ideas-vs-Opportunities-A-Crucial-Distinction` | Ideas vs. Opportunities: A Crucial Distinction | 7 | anchor=middle-left; n=7; vec=diagonal; dens=high+focal | `z_pattern` | 0.99 | z? |
| `6_Your-Hidden-Superpower` | Your Hidden Superpower | 8 | anchor=middle-left; n=8; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `7_` | The cohort pressure-tests the work. | 10 | anchor=middle-center; n=10; vec=diagonal; dens=low | `z_pattern` | 0.97 | n |
| `7_Cognitive-Skills-in-Action` | Cognitive Skills in Action | 5 | anchor=middle-left; n=5; vec=diagonal; dens=medium+focal | `z_pattern` | 0.99 | z? |
| `7_From-Idea-to-Value-The-Framework` | From Idea to Value: The Framework | 10 | anchor=middle-center; n=10; vec=diagonal; dens=high | `z_pattern` | 0.98 | n |
| `7_Healthcares-Most-Valuable-Asset` | Healthcare's Most Valuable Asset | 3 | anchor=middle-right; n=3; vec=horizontal; dens=medium+focal | `f_pattern` | 0.98 | n |
| `8_Expected-Value-vs-Expected-Utility` | Expected Value vs. Expected Utility | 9 | anchor=middle-left; n=9; vec=diagonal; dens=high | `z_pattern` | 0.95 | n |
| `8_Our-Mission-Transform-Insights-Into-Impact` | Our Mission: Transform Insights Into Impact | 5 | anchor=middle-left; n=5; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `8_The-Science-Behind-the-Connection` | The Science Behind the Connection | 7 | anchor=middle-right; n=7; vec=diagonal; dens=medium+focal/ws | `z_pattern` | 0.98 | z? |
| `9_Expected-Value-vs-Expected-Utility` | Expected Value vs. Expected Utility | 4 | anchor=middle-right; n=4; vec=diagonal; dens=medium+focal | `z_pattern` | 0.98 | z? |
| `9_From-Bedside-to-Innovation` | From Bedside to Innovation | 5 | anchor=bottom-left; n=5; vec=diagonal; dens=medium | `z_pattern` | 0.99 | n |
| `9_The-Transformation` | The Transformation | 8 | anchor=middle-right; n=8; vec=diagonal; dens=low+focal | `z_pattern` | 0.95 | z? |

## Candidate residue clusters (first-pass — DATA, not decisions)

Clustered on the feature-vector signature (reading_vector, text_density_band, focal_singularity, whitespace_dominance, anchor-count bucket). Includes slides that did not fit OR fit only via the over-eager `_looks_z`. The orchestrator decides admission (N≥4, ≥2 genres, behavioral-distinctness, stability) — this tool does NOT.

### RC01 — size 11 — single-focal-element, medium-text-density, diagonal-spread, ~5.55-anchors

- **signature:** `['diagonal', 'medium', True, False, '4-6']`
- **centroid:** `{"reading_vector": "diagonal", "text_density_band": "medium", "focal_singularity": true, "whitespace_dominance": false, "anchor_count_bucket": "4-6", "mean_anchor_count": 5.55, "mean_char_count": 226.6, "mean_coverage_area": 0.726, "cta_fraction": 0.18}`
- **members:** `10_Youre-Already-an-Innovator`, `18_The-future-of-population-health-needs-YOU`, `1_`, `20_Resources-to-Enhance-Your-Journey`, `2_Structured-Approach-to-Population-Health`, `4_Leadership-and-Risk-Awareness`, `5_Common-Obstacles`, `6_Idea-vs-Opportunity`, `7_Cognitive-Skills-in-Action`, `8_Our-Mission-Transform-Insights-Into-Impact`, `9_Expected-Value-vs-Expected-Utility`

### RC02 — size 7 — single-focal-element, medium-text-density, diagonal-spread, ~8.71-anchors

- **signature:** `['diagonal', 'medium', True, False, '7+']`
- **centroid:** `{"reading_vector": "diagonal", "text_density_band": "medium", "focal_singularity": true, "whitespace_dominance": false, "anchor_count_bucket": "7+", "mean_anchor_count": 8.71, "mean_char_count": 271.4, "mean_coverage_area": 0.977, "cta_fraction": 0.14}`
- **members:** `16_Motivation-in-Health-Interventions`, `19_Your-Unique-Leadership-Qualities`, `2_`, `2_An-Era-of-Unprecedented-Change`, `5_`, `6_`, `6_Your-Hidden-Superpower`

### RC03 — size 3 — single-focal-element, high-text-density, diagonal-spread, ~7.33-anchors, CTA-prevalent

- **signature:** `['diagonal', 'high', True, False, '7+']`
- **centroid:** `{"reading_vector": "diagonal", "text_density_band": "high", "focal_singularity": true, "whitespace_dominance": false, "anchor_count_bucket": "7+", "mean_anchor_count": 7.33, "mean_char_count": 788.0, "mean_coverage_area": 0.558, "cta_fraction": 0.67}`
- **members:** `12_Value-Proposition-Canvas`, `14_What-Drives-Us-Toward-Opportunities`, `6_Ideas-vs-Opportunities-A-Crucial-Distinction`

### RC04 — size 1 — single-focal-element, low-text-density, diagonal-spread, ~6.0-anchors

- **signature:** `['diagonal', 'low', True, False, '4-6']`
- **centroid:** `{"reading_vector": "diagonal", "text_density_band": "low", "focal_singularity": true, "whitespace_dominance": false, "anchor_count_bucket": "4-6", "mean_anchor_count": 6.0, "mean_char_count": 103.0, "mean_coverage_area": 0.737, "cta_fraction": 0.0}`
- **members:** `1_The-Modern-Clinicians-Dilemma`

### RC05 — size 1 — single-focal-element, low-text-density, diagonal-spread, ~8.0-anchors

- **signature:** `['diagonal', 'low', True, False, '7+']`
- **centroid:** `{"reading_vector": "diagonal", "text_density_band": "low", "focal_singularity": true, "whitespace_dominance": false, "anchor_count_bucket": "7+", "mean_anchor_count": 8.0, "mean_char_count": 90.0, "mean_coverage_area": 0.642, "cta_fraction": 0.0}`
- **members:** `9_The-Transformation`

### RC06 — size 1 — single-focal-element, sparse/whitespace-heavy, medium-text-density, diagonal-spread, ~7.0-anchors

- **signature:** `['diagonal', 'medium', True, True, '7+']`
- **centroid:** `{"reading_vector": "diagonal", "text_density_band": "medium", "focal_singularity": true, "whitespace_dominance": true, "anchor_count_bucket": "7+", "mean_anchor_count": 7.0, "mean_char_count": 271.0, "mean_coverage_area": 0.294, "cta_fraction": 0.0}`
- **members:** `8_The-Science-Behind-the-Connection`

## Per-slide errors

_(none — all 54 working slides perceived successfully)_
