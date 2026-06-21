# Reading-Path Patterns Catalog — Design Decisions (party-mode design round, 2026-06-21)

**Status:** RATIFIED (5-voice party-mode design round; Caravaggio/Winston/Murat/Mary/John; converged, no impasse). **Operator-confirmed:** hybrid (c) architecture + the Z-default refinement. **Branch:** `fidelity-perception-arc-2026-06-19`. This is the design authority for the patterns-catalog work and the hybrid pattern-ID classifier; the autonomous run + dev agent read this at T1.

## Problem framing (the JTBD — John)
The deliverable is **VO narration that tracks a slide in natural scan order**, not a slide taxonomy. Pattern identification is a *means*. Named patterns are **exception handlers**, admitted only when a slide demonstrably narrates *wrong* under the default. Suggestive names are NOT enough — each admitted pattern is a **narration instruction** the script writer consumes.

## D3 — Architecture: HYBRID (c) (Winston; operator-confirmed)
- **Deterministic geometry classifier** (`scripts/utilities/reading_path_classifier.py` + `ordered_element_keys_for_reading_path`) stays the **authoritative, reproducible scan-order producer + default** — preserves cache-prefix determinism under the no-mocks live regime (downstream narration tests pin the ordered keys).
- The **live gpt-5.5 perceiver** emits a near-free **in-band pattern HINT** (one extra structured field on the existing call — no second image upload).
- A **separate catalog-guided gpt-5.5 classification call escalates ONLY** on low-confidence / geometry-vs-hint disagreement / a hinted pattern with no defined scan order. LLM proposes, geometry disposes, default always catches. Every divergence is logged (LLM-proposed + geometry-cross-check + resolution) for audit.
- Fixes the `_looks_z` over-claim two ways: tighten the predicate from catalog-derived thresholds AND let the hint disconfirm Z on headline/art layouts.

## Default refinement (Caravaggio; operator-confirmed — amends "keep Z as default")
- **Z stays a first-class GENUINE pattern** — the *matched* default for slides that are confidently sparse-with-no-stronger-anchor.
- The **no-confidence FALLBACK is `top_down` position-order** (walk the real perceived bounding boxes top→bottom, left→right within rows) — NOT Z. Falling back to Z asserts a diagonal sweep the slide may not have; position-order claims only what is always true (the boxes' physical order).
- `free_form` (no clean rows / overlapping art) falls back to position-order with a softer, impressionistic cadence. The default is a **rigorously-defined catalog entry**, not a failure state.

## D2 — Catalog entry schema (Caravaggio + Mary)
Each pattern entry carries:
- **`structural_signature`** — the content-blind geometry/element-kind/count conditions that identify it (for the classifier).
- **`perceptual_rationale`** — why the eye scans this way (cognitive basis).
- **`reading_direction`** — explicit LTR/Western assumption flag (Z/F are LTR phenomena; hard-code it so RTL/CJK isn't silently broken later).
- **`canonical_scan_order`** — the ordered element-role traversal.
- **`entry_anchor`** + **`resolution_beat`** — where narration STARTS (first fixation, often not reading-order #1) and the closing/transition beat before the slide cuts.
- **`dwell_profile`** — per-element-class weighting: dominant=long dwell+emphasis, supporting=quick beat, decorative=SKIP (if the eye doesn't stop, the voice doesn't). *(Single most important field for the script writer.)*
- **`emphasis_targets`** — first-class: which 1–2 elements carry vocal stress.
- **`narration_delta`** (Mary) — one line: how narrating THIS pattern differs from the position-order default. **A pattern with no narration-delta does not exist.**
- **`modifier_handling`** — how content-genre tags (CTA / quote / stat) ride on top of the geometry without changing scan order (e.g., a Z slide with a CTA narrates Z-order but lands the resolution_beat on the CTA).
- **`exemplars`** + **`near_misses`** — corpus slide IDs (traceable to the 68); what it's NOT vs neighbors.
- **`confidence_and_fallback`** — ambiguity behavior → position-order default.
- **CUT:** no color/typography/palette field (mood, not scan order — the writer's job).

## Taxonomy (Caravaggio) — scan-distinct, not content-genre
Reading-path = *where the eye goes*, NOT what the slide is about. Content-genres (CTA) become **tags**, not patterns.
- Keep: `z_pattern` (sparse/diagonal), `f_pattern` (dense-text/left-margin skim), `center_out` (absorbs hub-and-spoke), `top_down` (vertical stack + the position-order fallback), `grid_quadrant`, `sequence_numbered` (numerals override geometry; highest-confidence).
- Split `multi_column` → **`two_up_comparison`** (A↔B ping-pong/contrast cadence) + **`triptych_3up`** (left→center→right march).
- Promote **`headline_dominant`** (single dominant fixation → optional descent; terminates, unlike center_out) + **`image_dominant`** (focal subject first, then text — perceiver reports the focal element).
- `free_form` = graceful no-dominant-geometry fallback (defined entry).
- **Z vs F discriminator = density** (Z sparse, F dense-text). **timeline** → fold into sequence/triptych unless ≥4 real exemplars. **CTA / hub-and-spoke** → not patterns.
- **Target ~10–13, NOT a vanity 14; count is DATA-DETERMINED** (could be ~3 net-new beyond the 7, or ~11 total — evidence decides).

## D4 — Discovery method: ANCHORED CLUSTERING (Mary + Murat + John)
1. **Fix a content-blind feature vector FIRST** (~6–8 perceiver-derived features, no subject matter): primary-anchor position, anchor count, reading-vector, text-density band, focal-singularity, CTA-presence, whitespace-dominance. (These the perceiver already emits — no new extraction.)
2. **Fit-to-existing-patterns + default pass** over the working set → demonstrates the existing catalog (operator use #1) + quarantines the **residue** (= John's "failures").
3. **Cluster ONLY the residue** bottom-up on the fixed feature vector → candidate emergent patterns.
4. **Two-source rule (Murat):** clustering features come from the *perceiver* (independent), NOT the classifier-under-test's labels; operator scan-order labels are the ground-truth axis.

### Admission rubric (a candidate becomes a catalog pattern ONLY if ALL hold)
- **N≥4 corpus exemplars** AND spanning **≥2 content genres** (kills topic-creep — a single-genre cluster is a genre, not a path).
- **Behavioral-distinctness / non-overlap:** would make the narrator read the slide in a *different order or grouping* than every existing pattern (stated `narration_delta`); not a sub-case of an existing pattern.
- **Stability:** survives 2–3 clustering perturbations (drop 10% / reseed).
- Fails any bar → goes to the **default bucket**, not the catalog. Prefer a smaller catalog + strong default over sprawl (N patterns → ~N² pairwise-distinguishability obligations — Murat).

## Validation discipline (Murat + Mary)
- **Held-out reserved BEFORE definition** — stratified ~20% (~14 of 68), manifest committed pre-definition (see `reading-path-holdout-split-2026-06-21.md`). The 68 cannot be both training and held-out, or the ≥80% gate is self-grading.
- **Catalog definitions under test** — each entry pins positive + negative exemplar slides as golden fixtures; a definition edit that silently reclassifies a pinned exemplar FAILS CI. The catalog is code; it gets a test file.
- **Pre-registered accuracy bar** — top-1 ≥ 0.85 on catalog-matchable slides + a **confusion matrix** (must show `_has_ordinal`→`sequence_numbered` and Z/F are not systematically confused).
- **Hybrid arbitration under test** — pin slides where geometry + LLM disagree; assert the documented tiebreak.
- **Default-degradation RED-first** — a slide yielding empty `visual_elements` or no-confident-match must return a named `default`/`unknown` low-confidence outcome and CONTINUE (not whole-run error-pause — closes the filed `vision-perceiver-empty-visual-elements-degradation` gap). The default must be observable/counted (a run where 40/68 fall to default is visible).
- **Vacuous-skip → must-fail** (Murat standing dissent) — a deliberate key-vocab mismatch must FAIL/XFAIL, never silently SKIP.
- **LLM classifier** validated via recorded-real responses behind a parse seam + key-gated live runs (the pattern shipped for the perceiver).

## Sequencing (John + Mary reconciled)
**Default-first, cluster-the-residue, define-on-failure** = Mary's anchored clustering (fit-to-existing + cluster residue). The John(≤3) vs Caravaggio/Mary(~11) gap is NOT a design disagreement — same method + bar; the **count is data-determined** by the evidence.

## No-mocks / live (operator standing directive)
Perception + LLM pattern-ID are real live gpt-5.5 calls. Determinism for tests comes from recorded-real responses behind the parse seam, never a fixture on the production path. Cost is not a constraint.

## Filing (Mary — must land so this doesn't drift)
- Versioned catalog artifact `reading-path-patterns-catalog.md` (v-stamped, frozen-at-trial per pack-versioning discipline) with the admission rubric as its governance header + exemplar slide IDs + the explicit default entry.
- Held-out split manifest committed pre-definition (done — see companion file).
- Backlinks: catalog ↔ deferred-inventory `vo-narration-layout-tracking-trained-patterns` (this catalog is its prerequisite substrate) + ↔ P2-4b calibration (catalog is the conformance-scoring rubric).
