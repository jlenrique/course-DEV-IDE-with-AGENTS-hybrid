# 07G Read-Path Review — narration cadence vs. perceived reading-path

**Run:** `concierge-part1-narrated-20260630` · **Deck:** C1M1 Part 1 (9 final slides)
**Perception source:** live gpt-5.5 vision (`reading_path_source: llm_primary` on all 9) · **No mocks.**
**Inputs correlated:** `perception/perception-artifacts.json` (this stage) × `narration/segment-manifest.yaml` (drafted narration, one segment per card ordinal).

This review asks one question per slide: **does the narration's spoken order/cadence follow the eye's perceived reading-path?** Recommendations are advisory only — narration is **not** rewritten here.

| # | slide_id | perceived reading_path (macro · text · cadence · img-role) | narration follows? |
|---|----------|-----------------------------------------------------------|--------------------|
| 1 | c1m1-p1-s01 | split_image_text · dense_exposition · dense · role 1 | **yes** |
| 2 | c1m1-p1-s02 | enumerated_process · enumerated_process · moderate · role 3 | **yes** |
| 3 | c1m1-p1-s03 | grid_quadrant · peer_boxes · dense · (no image) | **yes** |
| 4 | c1m1-p1-s04 | multi_column · peer_boxes · dense · role 2 | **yes** |
| 5 | c1m1-p1-s05 | top_down · peer_boxes · dense · (no image) | **yes — with note** (middle lexicon rows skipped by design) |
| 6 | c1m1-p1-s06 | two_up_comparison · comparison_pair · dense · role 1 | **yes** |
| 7 | c1m1-p1-s07 | two_up_comparison · comparison_pair · dense · role 2_5 | **yes** |
| 8 | c1m1-p1-s08 | two_up_comparison · comparison_pair · moderate · role 1 | **yes** |
| 9 | c1m1-p1-s09 | grid_quadrant · peer_boxes · dense · role 4 | **MISMATCH** (four visible pillar cards not tracked by the compressed recap) |

No slide carries a deterministic `oppositional_cue` flag, and every comparison-pair slide (6/7/8) is narrated in the perceived left→right / no-net→net order, so there is **no oppositional-cue conflict** anywhere in the deck.

---

## Per-slide detail

### Slide 1 — Welcome & The Modern Clinician's Dilemma — FOLLOWS
Perceived: left illustration (tier-1 decorative, "give it no comment") + right-side top-down text stack (title → "Tejal Naik, M.D." → trained-not-to-create paragraph → innovation-mindset definition → "Clinical Reactor to Systemic Innovator" reframe). Narration walks exactly that right-column order — self-introduction, the "trained to follow, not create" framing, the barrier, the innovation-mindset definition, the "designer of it / dormant within you" reframe — and correctly gives the decorative image no airtime. Dense cadence matches the copy-heavy panel. No change.

### Slide 2 — The Innovator's "Hero's Journey" — FOLLOWS
Perceived: a load-bearing (tier-3) journey diagram the eye must trace through three ordered waypoints, ending at the deliverables endpoint. Narration tracks the enumerated process precisely: Course 1 "Sparking Innovation" → Course 2 "Building the Solution" → Course 3 "Driving Impact" → "tangible playbook and the foundation for an executive one-pager." The spoken order IS the diagram's path. No change.

### Slide 3 — The Lineage of Physician Innovators — FOLLOWS
Perceived: five coordinate peer cards (3+2 grid), no image. Narration enumerates them in exact card order — ED tele-triage → informatics/Abridge → Geisinger/Glenn Steele → Gawande's checklist → Longmire/Medable. For a peer grid the eye can scan in any order, but the voice imposes the same left-to-right, top-to-bottom sweep the layout invites. Dense cadence matches the citation-heavy cards. No change.

### Slide 4 — Expectations & Mental Frameworks — FOLLOWS
Perceived: two side-by-side peer columns (Growth Mindset / Dweck | Psychological Safety / Edmondson) above a bottom course-contract callout whose intent the model read as directive. Narration moves left column → right column → bottom contract ("we must collectively commit to maintaining psychological safety"), honoring both the multi-column scan and the directive callout. No change.

### Slide 5 — The Innovation Lexicon — FOLLOWS (with note)
Perceived: title → intro → an eight-row term/definition table, read top-down (classifier: `top_down` / `peer_boxes`, dense). Narration anchors at the top (Innovation, Intrapreneurship), then deliberately jumps to "the last three definitions … the psychological engine" (First Principles, Psychological Safety, Growth Mindset) and hands the rest to the learner: "Take a moment to review this lexicon." This is sound treatment of a dense reference table — you do not read eight definitions aloud — but the voice never touches the three middle rows (Systemic Friction, Root Cause vs. Symptom, Functional Flexibility) the eye still scans.
**Recommendation (advisory):** add a single bridging clause acknowledging the middle rows (e.g., "…the middle terms — systemic friction, root cause versus symptom, functional flexibility — you'll meet again in Part 2…") so the spoken cadence covers the same vertical span the eye traverses, instead of skipping the table's center.

### Slide 6 — The Tightrope & The Net — FOLLOWS
Perceived: left two-up comparison (labeled "No Safety Net: Compliance & Fear" vs "Psychological Safety: Innovation & Risk-Taking") paired with a full-height tightrope/net image (tier-1 metaphor). Narration delivers the comparison in perceived order — no-net (stick to the script, rigid, a single fall is ruin) → net (failure as data, empowered to take creative risks) — and leans on the tightrope/net metaphor the image depicts. No change.

### Slide 7 — The "Wicked" World of Innovation — FOLLOWS
Perceived: left exposition + a dominant right-side Kind-vs-Wicked comparison exhibit (tier-2_5, confirmed against text) with a "Watch on YouTube" directive CTA. Narration runs Kind environments → Wicked environments → the David Epstein video CTA ("Watch this breakdown…") → the post-video "Range" takeaway — matching both the two-up contrast and the mid-slide CTA placement. No change.

### Slide 8 — The Track vs. The Jungle — FOLLOWS
Perceived: left Kind (the track) vs Wicked (the jungle) comparison pair + a right illustrative image (tier-1) that depicts the named metaphor; moderate cadence (lighter text than slide 7). Narration: trained on "the track — a 'Kind' environment" → "system innovation is the jungle… a 'Wicked' environment" → "you can't bring track shoes to a jungle… be functionally flexible." Spoken order = perceived comparison order, and moderate pacing fits the lighter panel. No change. (Note: 7 and 8 are intentional reinforcement of the same Kind/Wicked axis — concept+video on 7, metaphor on 8 — and the narration does not become redundant.)

### Slide 9 — Part 1 Summary — MISMATCH (recommend a cadence/order tweak)
Perceived: a four-card peer grid of explicitly titled pillars — **The Gap · The Mission · The Journey · The Mindset** — with a bottom "Up Next — Part 2 … bring your identified friction points and unmet needs" directive callout (the only image-like element is a tier-4 icon). The eye is invited to read four labeled cards in turn.
The narration is a single compressed recap ("You've established your mental framework and embraced … 'Range' … your clinical specialization is a strength — but solving systemic friction requires functional flexibility … ready to transition from a clinical tactician to a systemic intrapreneur … In Part 2 …"). It maps *loosely* to the pillars (specialization-vs-friction ≈ The Gap; transition-to-intrapreneur ≈ The Mission; "this mindset" ≈ The Mindset) but **does not name or walk the four cards in grid order**, and The Journey pillar is essentially untouched. A learner scanning four titled cards hears a flowing paragraph that never tags them — the spoken cadence fights the four-card visual scan.
**Recommendation (advisory):** lightly restructure the summary so it touches the four pillars in their perceived grid order — Gap → Mission → Journey → Mindset — one beat each, then land on the "Up Next" directive (including the explicit "bring your friction points and unmet needs" instruction the card states but the current narration drops). This realigns the recap's cadence with the eye's four-card sweep without adding new content.

---

## Bottom line
- **8 of 9 slides:** narration's spoken order and cadence follow the perceived reading-path cleanly; comparison slides (6/7/8) are narrated in perceived contrast order; directive callouts (4, 7) are honored.
- **1 mismatch (slide 9):** four titled summary cards vs. a compressed recap that doesn't track them — recommend a four-beat reorder to follow the grid.
- **1 soft note (slide 5):** dense lexicon table whose three middle rows the voice skips by design — recommend a one-clause bridge.
- **No oppositional-cue conflicts** anywhere; cadence labels (dense/moderate) align with perceived text density on every slide.
