# Reading-Path Patterns — Operator Review Round 1 (live notes)

**Started:** 2026-06-22. **Method:** operator reviews ONE working slide at a time, gives their eye's immediate read; Claude captures it verbatim-ish + a provisional fit; pattern/naming decisions are HELD until the full 54 are seen, then clustered from the operator's actual responses (data-determined, no quota).
**Corpus:** `C:\Users\juanl\OneDrive\Desktop\z-2026-06-21` (working set = 54; the 14 held-out are NEVER shown — see `reading-path-holdout-split-2026-06-21.md`).
**Catalog under review:** `reading-path-patterns-catalog.md` (v0-draft).

---

## Emerging axes / candidate-pattern observations (updated as we go)
- **UNIVERSAL NARRATION PRINCIPLE (operator @ `6_Idea-vs-Opportunity` turn) — CTA / CONTACT / LITERAL-STRING SLIDES: CUE THE PURPOSE, DON'T READ THE STRING.** For CTA/contact cards, give an audio cue of the screen's purpose/content (e.g. "Contact JCPH by email, phone, or your favorite channel…") — do NOT literally read out addresses, emails, URLs, phone numbers, or social handles. Generalizes: never voice raw literal strings; narrate their gist/intent.
- **UNIVERSAL NARRATION PRINCIPLE (operator @ `4_Leadership-and-Risk-Awareness-in-Public-Health`) — TEXT-HEAVY SLIDES: SCAFFOLD BEFORE DETAIL.** For dense slides, VO begins with the title, then provides **structure/scaffolding by naming the other headings/subheadings** (a brief table-of-contents / outline / chapter-subheadings preview), THEN walks the detailed content. Orient the listener to the slide's skeleton before the flesh.
- **UNIVERSAL NARRATION PRINCIPLE (operator @ `4_`) — CADENCE MATCHES SLIDE DENSITY; PACING > WORD-VOLUME.** "Ad"-type slides (a few bold, brief messages) get equally brief narration — one or two sentences. Pacing/timing matters more than volume of words. → narration cadence should be a per-pattern field (poster/ad = sparse+slow; exposition = denser).
- **DIMENSION (operator @ `3_`) — IMPOSED DIRECTION / SEQUENCE, broader than explicit enumeration.** Sequence can be imposed not only by numerals but by **directional cues** — arrows, connectors, flow (here: big arrows connecting spark → build → drive). Suggests generalizing `sequence_numbered` into a broader "directed-order" family (numerals OR arrows/flow impose the scan order), OR a sibling `directed_flow` pattern. The classifier should detect arrow/connector geometry as an order signal, not just ordinals.
- **UNIVERSAL NARRATION PRINCIPLE (operator @ `3_`) — CALLOUTS ALWAYS GET DIRECT VO.** Every slide scan must hunt for callouts (e.g. "YOU START HERE") and ensure each gets **direct VO narration treatment** — never skipped. (Pairs with the title-anchor rule below.)
- **UNIVERSAL NARRATION PRINCIPLE (operator @ `1_Turning-Ideas-into-Action`) — TITLE-ANCHOR-THEN-SYNTHESIZE.** VO should ALWAYS open by echoing the bold title in some way (anchor the reader to the starting point), THEN proceed to summary / highlights / points of emphasis. **NEVER literal page-reading** ("I am reading this page to you because you can't read"). Applies across patterns; the title is the first-impression anchor even on top-down text slides.
- **IMAGERY IS A SPECTRUM, not binary (operator refined @ `2_Same-Process-Different-Context`).** Image VO-treatment is the real discriminator, and there are ≥3 tiers:
  1. **Decorative / evocative** — sets tone/mood/theme; **VO gives it NO comment.** (e.g. `1_From-Idea-to-Action`, `1_The-Modern-Clinicians-Dilemma`, the `2_An-Era` top banner.)
  2. **Illustrative (in-between)** — MAY be referenced in VO but is NOT technical/instructional; **does NOT need a detailed walk-through.** (e.g. `2_Same-Process-Different-Context` side images.)
  3. **Technical / instructional** — content the VO **must walk through** (diagrams, canvases, charts, frameworks).
  4. **Pointer / iconographic (operator @ `4_`)** — small icons that **signal a message's domain/category** (calendar = a time/date fact; staff of Asclepius = a medical-profession fact). NOT narrated as images; they *type* the adjacent message unit. VO need not mention them, but they aid the writer in inferring each box's intent.
  This cuts directly against the catalog's `image_dominant`, which currently says "narrate what is in the image" — only tier 3 wants that. Implication: the reading-path pattern may need an orthogonal **image-role tag** {decorative | illustrative | instructional} rather than (or in addition to) a single `image_dominant` pattern. **Original working name retained:** `message_led_decorative_companion` = message-left/right(or top) + a TIER-1 decorative image.

---

## 🔑 EMERGING SYNTHESIS — a slide is a COMPOSITION, not one flat label (crystallizing @ `5_Common-Obstacles`)
The operator's reads keep decomposing each slide along **independent axes**, not a single pattern enum. The hybrid classifier likely needs to emit a small **tuple**, not one label:
1. **MACRO-LAYOUT** — the dominant spatial split. Recurring values so far: `split_image_text` (≈half decorative/evocative image | half text — **the most common; side-agnostic**, image L or R or top), `full_bleed_text_hero` (divider/poster), `columns` (N peer columns), `two_pane_comparison` (oppositional), `single_text_block` (exposition).
2. **IMAGE-ROLE tier** {1 decorative · 2 illustrative · 3 instructional · 4 pointer/iconographic} — drives whether/how VO treats the image.
3. **TEXT MICRO-STRUCTURE** — independent of layout: `enumerated`/`process` (order load-bearing), `peer_boxes` (coordinate, order = read-order), `dense_exposition`, `hero_message`, `comparison_pair`.
4. **NARRATION CADENCE** — sparse/slow (poster/ad) ↔ dense (exposition); pacing > word-volume.
> The catalog's flat 7-pattern enum collapses these axes and is WHY `_looks_z`/`image_dominant`/`diagram_driven` over-claim. **Strong round-1 recommendation forming: refactor the catalog from a flat enum into this compositional tuple (or at minimum split image-role out of the pattern).** Confirm with operator at synthesis.

### Sub-finding — COMPARISON is a text-substructure that can render full-width OR nested (memorialized per operator @ `6_Idea-vs-Opportunity`)
`two_up_comparison` (vertically-symmetric contrast w/ per-side subheadings) appears BOTH as a full-width slide (`2_`, `2_Same-Process`, `3_Two-Processes`) AND nested in the text half of a `split_image_text` (`6_Idea-vs-Opportunity`). → model comparison as a **text-substructure** (`comparison_pair`), NOT a separate macro-layout; it composes with any macro. Same narration delta either way: establish both sides → walk the contrast. **N≥4 CLEARED (4 fits) → `two_up_comparison` ADMITTED (answers Q4 for this pattern).** Apply this "macro × nested-substructure" decomposition to all remaining slides where reliable.

### Build requirement — PRODUCTION SLIDE-ANALYSIS LLM MUST BE ≥ THIS CAPABILITY (operator directive @ `6_Idea-vs-Opportunity` turn)
The LLM invoked for reading-path/slide analysis during PRODUCTION runs must be **at least as capable as the model doing this review** — operator named **OpenAI gpt-5.5**. The corpus scan already ran on gpt-5.5 and `vision-perceiver-real` made perception live on gpt-5.5; this directive extends the same floor to the hybrid classifier's **LLM-escalation leg** (the catalog-guided disambiguation call). Do NOT downgrade the escalation model to a cheaper tier. Memorialize in the classifier spec.

## Per-slide operator reads

### `1_From-Idea-to-Action-Population-Health-Leadership`  — catalog said: f_pattern (FLAGGED)
- **Operator read:** Two-column layout. Right image's color/shape catches the eye first, near-simultaneous with the left headline. Image sets tone/mood/concept — NOT technical, NOT an instructional graphic; it is **decorative**. The image **needs no comment**. Eye goes to the left headline for the message.
- **Narration delta (operator-implied):** lead with the LEFT message; do NOT narrate the image.
- **Provisional fit:** NOT `f_pattern` (confirmed misfit). NOT `image_dominant` as defined (that says narrate the image — operator says don't). → candidate `message_led_decorative_companion` (HELD).
- **Perception note:** right element tagged `kind: photo` (correct-ish; rich illustration).

### `1_` (bare divider)  — catalog said: diagram_driven (divider bucket)
- **Operator read:** Centered headline; eye lands on "THE INFLECTION POINT". Text-hero divider. Classic, high-impact, big single 'impression' text-based message. (No image.)
- **Narration delta:** single-impression text beat; speak the headline message; nothing else competes.
- **Provisional fit:** `headline_dominant` / text-hero (NOT diagram_driven). Distinct from slide-1's decorative-companion case: here there is NO image at all — pure centered text-hero. Supports admitting a text-hero pattern (Q3) AND a bare-divider sub-case (Q5).

### `1_The-Modern-Clinicians-Dilemma`  — catalog said: diagram_driven
- **Operator read:** Eye lands on the clinician image first, then headline. Very much like `1_From-Idea-to-Action`: image is tone-setting / concept-evoking, NOT technical/instructional → **needs no VO direct addressing.**
- **Provisional fit:** `message_led_decorative_companion` (HELD). 2nd exemplar of the candidate group. NOT diagram_driven (the perceiver's `kind` mislabel again — it's a decorative scene, not a structured diagram).

### `1_Turning-Ideas-into-Action-HII-Meeting-Preparation`  — catalog said: sequence_numbered
- **Operator read:** Classic text-based exposition slide. Read top-down, left-right, like reading a page in a book. Bold title is the first impression. VO must begin by echoing the title to anchor, then proceed to summary/highlights/emphasis — never literal page-reading.
- **Provisional fit:** `top_down` (text-exposition). NOTE catalog had this as `sequence_numbered` — operator read it as plain top-down reading order, NOT numeral-driven. Possible sequence_numbered over-trigger (the `_has_ordinal` prose false-positive the catalog already flagged). Revisit at clustering.

### `2_` (bare divider name, but is a comparison slide)  — catalog said: diagram_driven
- **Operator read:** Beautiful vertically-symmetrical slide comparing two paradigms (Clinical Reasoning / Design Thinking). Bold top message read first — strong impression, sets the framing of the comparison/mapping between two ways of thinking. VO should echo the framing statement THEN walk through the comparison/mapping.
- **Narration delta:** title-anchor (framing) → walk the two-side comparison/mapping (side A vs side B), not a diagonal/top-down sweep.
- **Provisional fit:** **`two_up_comparison` — FIRST GENUINE FIT.** The catalog had this pattern defined-but-NOT-admitted (0 fits). This is evidence toward admitting it (bears on Q4). Watch for ≥3 more across the corpus to clear the N≥4 bar.

### `2_A-Structured-Approach-to-Developing-Ideas`  — catalog said: z_pattern
- **Operator read:** Classic exposition with enumerated blocks of info. VO references the title then walks through each numbered item one by one with summary/highlights — ideally voicing the number ("Number One", "next", "Number Three").
- **Narration delta:** strict ascending ordinal walk; speak the ordinals aloud.
- **Provisional fit:** **`sequence_numbered`** (clean). NOTE catalog had this as `z_pattern` — another `_looks_z` over-claim; operator reads it as numbered, not diagonal.

### `2_An-Era-of-Unprecedented-Change`  — catalog said: diagram_driven
- **Operator read:** Eye lands on headline. Top image is decorative (mood/concept only) → needs no comment. Slide is essentially a **three-column** type; narration, after noting the headline message, progresses **left → right, column to column.**
- **Narration delta:** title-anchor → left-to-right column sweep (one column at a time).
- **Provisional fit:** **`multi_column` — FIRST GENUINE FIT** (catalog had it defined-but-NOT-admitted; bears on Q4). Also reinforces the decorative-image axis (top decorative banner, no VO). NOT diagram_driven.

### `2_Same-Process-Different-Context`  — catalog said: z_pattern
- **Operator read:** Another vertically-symmetrical compare/contrast of two systems/models/paradigms. VO establishes the comparison using the title + each side's subheadings (if present), then recounts whatever is stated about the comparison. Side images are **tier-2 illustrative** (could be referenced, not technical/instructional, no detailed walk-through).
- **Provisional fit:** **`two_up_comparison` — 2nd GENUINE FIT** (with `2_`). NOT z_pattern (another `_looks_z` over-claim). Imagery = tier 2.

### `2_Structured-Approach-to-Population-Health`  — catalog said: image_dominant
- **Operator read:** Pattern identical to the previous enumerated text-only info blocks (`2_A-Structured-Approach`); categorize and narrate the same way.
- **Provisional fit:** **`sequence_numbered`** (text-only enumerated blocks). NOTE catalog had this as `image_dominant` — clear misclassification (operator sees no dominant image; it's enumerated text).

### `3_` (bare divider)  — catalog said: diagram_driven
- **Operator read:** Beautiful poster/broadside "ad". Three big, bold, briefly-stated messages (spark / build / drive). Critical "YOU START HERE" callout. Big arrows connect spark→build→drive imposing a sequence.
- **Narration delta:** poster text-hero + a directional 3-beat flow (spark→build→drive); MUST voice the "YOU START HERE" callout directly.
- **Provisional fit:** text-hero poster WITH imposed directional sequence (arrows) → `directed_flow`/broadened-`sequence_numbered` candidate (see new dimension above). NOT diagram_driven. Also a bare-divider (Q5) but content-rich, not a plain title divider like `1_`.

### `3_The-Education-Gap`  — catalog said: sequence_numbered
- **Operator read:** Very like earlier slides. Bold title calling attention to itself; right image purely **decorative (tier 1, evocative/concept-stimulating, needs no comment)**; text-based content for VO summary/highlighting.
- **Provisional fit:** `message_led_decorative_companion` (tier-1 image). NOT sequence_numbered (catalog miss).

### `3_The-Ideal-State-5-Step-Process`  — catalog said: sequence_numbered
- **Operator read:** A **"process slide."** Downward-aligned big arrows make the first impression; title announces the steps (5 steps); labels for each step. Demands narration that addresses the process **step by step.**
- **Provisional fit:** `directed_flow` / **process** — sits at the intersection of imposed-direction (arrows) AND enumeration (5 steps). Confirms the broadened "directed-order" family. Operator coins the term **"process slide"** — candidate pattern name. Catalog's `sequence_numbered` is the closest existing label and is acceptable here, but the ARROWS (not just numerals) are the dominant cue.

### `3_Two-Processes-One-Mind`  — catalog said: z_pattern
- **Operator read:** `two_up_comparison`, illustrative (tier-2) images, narrate the contrast. Confirms the recurring shape: vertically-symmetrical slide comparing/contrasting left & right panes, with slide title + large per-side subheadings (one per pane) calling out the intended comparison/contrast.
- **Provisional fit:** **`two_up_comparison` — 3rd GENUINE FIT** (with `2_`, `2_Same-Process`). One more clears N≥4. NOT z_pattern. Imagery tier 2.

### `4_` (bare divider)  — catalog said: diagram_driven
- **Operator read:** Another "ad"-inspired bold display. Three short, critical messages hit immediately; **4 boxes** provide supporting detail. Could be narrated in ~2 sentences — but word choice should closely echo the on-screen text. **Boxes encapsulate message units; images are "pointers"** (tier-4 iconographic: calendar→time fact, Asclepius staff→medical fact).
- **Narration delta:** brief, high-impact; echo the on-screen phrasing; one beat per boxed message unit; icons not narrated.
- **Provisional fit:** text-hero/poster "ad" + boxed message units + tier-4 pointer icons. NOT diagram_driven. Related to the text-hero family; "boxed message units" is a recurring layout primitive worth a tag.

### `4_Leadership-and-Risk-Awareness`  — catalog said: image_dominant
- **Operator read:** Mirror image of the most-seen pattern: evocative (tier-1) image on one side, text (title + subheading + some narrative copy) on the other. The image is the initial momentary impact but **must be taken in with the context of the counterposing textual content.**
- **Provisional fit:** `message_led_decorative_companion` — **4th exemplar** (now the most-frequent pattern). KEY: **side-agnostic** — image/text may be on either side ("mirror image"); the classifier must not hard-code image-on-right. Catalog's `image_dominant` is the closest existing label but mis-prescribes "narrate the image"; operator wants message-led with image as context, not subject.

### `4_Leadership-and-Risk-Awareness-in-Public-Health`  — catalog said: z_pattern
- **Operator read:** Has a tier-1 image that sets tone/concepts but needs no VO attention. Relatively **dense with text** → VO highlights the title, then scaffolds via other headings/subheadings, then summarizes the detailed content (see new scaffold-before-detail principle).
- **Provisional fit:** dense-text exposition WITH a decorative companion image → `top_down`/exposition + tier-1 image. NOT z_pattern. (Variant of message-led where the text side is dense.)

### `4_The-Critical-Gap`  — catalog said: f_pattern (FLAGGED)
- **Operator read (cold):** Evocative image at right, no VO needed; text at left for narration. [matches the catalog flag — confirmed NOT f_pattern.]
- **Provisional fit:** `message_led_decorative_companion` — **5th exemplar**, tier-1 image. **CONFIRMS Q2:** this f_pattern flag was a misfit; operator independently classifies it as message-led decorative.

### `4_The-Innovators-DNA-is-Clinical-DNA`  — catalog said: image_dominant  — **(Claude-led; operator AGREED)**
- **Claude read:** Title top-left + three parallel columns (photo + heading + 2-line caption: Deep Empathy / Intellectual Curiosity / Resilience). `multi_column` (3 coordinate facets), tier-1 decorative photos (no walk-through), narrate title→left-to-right one beat per column.
- **Operator:** AGREED multi_column. ("perfect analysis and inferring of implications for VO.")
- **STRUCTURAL DISCRIMINATOR confirmed:** `multi_column` = N **parallel/coordinate** peer facets (no tension); `two_up_comparison` = 2 **oppositional** sides with per-side subheadings. **2nd multi_column fit** (with `2_An-Era`). Catalog's `image_dominant` was wrong (images are incidental, not the subject).

### `5_` (bare divider)  — catalog said: diagram_driven  — **(Claude-led; operator AGREED)**
- **Claude read:** Course opener — Jefferson brand + "COURSE 1", giant "Diagnose the system." headline, value-prop subtitle, course-detail footer; faint tilted "CLINICAL NOTE" form + blueprint bg on the right. text-hero divider; tier-1 decorative form; sparse cadence.
- **Operator:** AGREED text-hero divider. Emphasized: the Clinical Note "could look like a diagram or technical, but it's just a stylized, semi-transparent background image that sets mood/conceptual space — beautiful, but NOT technical, instructional, or even illustrative; no need to narrate."
- **CLASSIFIER RULE reinforced:** `kind: diagram` from the perceiver does NOT imply instructional. A semi-transparent/background/cropped "diagram" is **tier-1 decorative**. The hybrid must gate `diagram_driven` on the diagram being FOREGROUND + opaque + structurally load-bearing, not merely present. (3rd time this trap appears: `4_The-Critical-Gap`, `7_Healthcares`, now `5_`.) Strong evidence `diagram_driven` is over-claimed (Q1).

### `5_Common-Obstacles`  — **(Claude-led; operator AGREED)**
- **Claude read:** Left ~38% maze photo (tier-1 decorative). Right: title + 4 stacked bordered "boxed message units" (peer items, not numbered). `top_down` boxed peer-list + decorative companion image.
- **Operator:** AGREED top_down boxed list. Named the macro-pattern: mood/concept image on ≈half the screen + expository text (light/heavy, structured/not) on the opposing side — **a slide type seen very often** → `split_image_text` macro-layout (see synthesis block above).
- **Tuple:** macro=`split_image_text` · image-role=1 · text-substructure=`peer_boxes` · cadence=moderate.

### `5_Obstacles-in-Building-the-Ideal-State`  — **(Claude-led; operator AGREED)**
- **Claude read:** A/B twin of `5_Common-Obstacles` (same content, NO image, 5 cards in a 3+2 grid + bottom summary). tuple: macro=`card_grid` · image-role=none · text-substructure=`peer_boxes`+summary/segue · cadence=dense. Row-major read order; bottom summary = resolution/transition beat.
- **Operator:** AGREED (read order correct). KEY NUANCE: the boxes have **no obvious visual pattern/sequence** — only the **semantics** (read the title + upper-left box first) confirm that natural reading-order ("Z") is correct.
- **PRINCIPLE — SEMANTICS CONFIRM ORDER WHEN GEOMETRY IS NEUTRAL.** For peer grids with no imposed sequence (no numerals/arrows/tension), default to **natural reading-order (row-major / "Z")**, and confirm via semantic reading (title→first box), not geometry alone. This is a GENUINE default-fallback case (validates the catalog's `top_down`-default) — and shows true "Z/reading-order" lives here: peer content, no other ordering cue.
- **A/B-TWIN INSIGHT:** same content rendered as (image + 4 stacked boxes) vs (no image + 5-card grid) → confirms **macro-layout is independent of content** and must be detected from geometry, not topic.

### `5_The-Real-Barrier`  — catalog said: z_pattern  — **(Claude-led; operator AGREED)**
- **Claude read:** Title top-left → 3 right-pointing chevron panels (icons: lightbulb/lock/shield) + heading + gloss (Not Lack of Ideas / Missing Structure / Absent Safety). Called `multi_column` (peers), NOT process, despite chevron styling; icons tier-4 pointers.
- **Operator:** AGREED multi_column, chevrons are decorative direction. Note: the mild implied flow makes sense only in **semantic/narrative** context (given obstacles → physicians HAVE ideas but LACK process/safe-space) — so VO may carry a light connective thread across the peers even though they're coordinate.
- **CLASSIFIER FLAG — directional SHAPE ≠ process.** Chevron/arrow geometry can be decorative; gate `process`/`directed_flow` on the CONTENT being sequential (steps transform) vs peer (coordinate facets). Refines the imposed-direction dimension. tuple: macro=`multi_column` · image-role=4 · text=`peer_boxes`(L→R) · cadence=moderate.
- **PRINCIPLE — peer slides may still get light connective narration** when the semantic context implies a thread (not just disconnected box-reading).

### `6_` (bare divider)  — catalog said: image_dominant  — **(Claude-led; operator AGREED)**
- **Claude read:** Giant centered "Apply." headline + contact block + APPLY/URL + blueprint-corner bg. text-hero divider, **CTA/closing-card** sub-type. Tier-1 decorative bg (perceiver `kind:diagram` mislabel #4). Sparse cadence.
- **Operator:** AGREED text-hero CTA card.
- **NEW SUB-TYPE:** `text_hero` divider has functional sub-types: section-opener (`1_`, `5_`) vs **CTA/contact card** (`6_`). Same macro/scan; differ in narration role (CTA cards may be near-skip/visual-only end cards). Catalog's `image_dominant` label = wrong.

### `6_Idea-vs-Opportunity`  — catalog said: image_dominant  — **(Claude-led; operator AGREED + praised)**
- **Claude read:** split_image_text macro (left lightbulb photo, tier-1 decorative) with a **`two_up_comparison` nested in the text half** (Idea vs Opportunity, 2 labeled columns). 4th comparison fit → clears N≥4.
- **Operator:** AGREED; "excellent recognition of the macro pattern with another sometimes-macro pattern (the comparison, vertically-symmetrical) inserted. Memorialize and apply." → done in synthesis block.
- **CTA narration rule** also issued this turn (cue purpose, don't read literal strings) — see universal principles.
- **Production-LLM floor** directive issued this turn (≥ gpt-5.5) — see build-requirement block.
- **tuple:** macro=`split_image_text` · image-role=1 · text-substructure=`comparison_pair` · cadence=moderate.

### `6_Ideas-vs-Opportunities-A-Crucial-Distinction`  — catalog said: z_pattern  — **(Claude-led; operator AGREED)**
- **Claude read:** A/B twin of `6_Idea-vs-Opportunity`, prose-dense. Full-width title → Idea col (para + embedded tier-1 lightbulb photo) | Opportunity col (paras) → full-width closing synthesis/segue. `two_up_comparison` (5th fit) + closing synthesis. Image embedded IN the column, not a clean split → image placement incidental, comparison substructure constant.
- **Operator:** AGREED comparison twin.
- **tuple:** macro=comparison(2-col, full-width) · image-role=1(inline) · text=`comparison_pair`+synthesis/segue · cadence=dense.

### `6_Your-Hidden-Superpower`  — catalog said: image_dominant  — **(Claude-led; operator AGREED)**
- **Claude read:** Left ~45% doctor-patient illustration (tier-1 decorative). Right: title + 3 vertically-stacked icon+text callouts (Patient Proximity / Deep Domain Expertise / Intrinsic Drive to Heal). Clean recurring tuple: macro=`split_image_text` · text=vertical `peer_boxes` · image-role=1 + tier-4 pointer icons · cadence=moderate. Same shape as `5_Common-Obstacles`.
- **Operator:** AGREED split_image_text peer list. (Stopped here for the day — 26/54.)

---

## Progress (round 1) — 26 / 54 working slides reviewed (≈48%), 2026-06-22
**DONE (26):** all of prefixes 1–6 (1_, 1_From-Idea-to-Action, 1_The-Modern-Clinicians-Dilemma, 1_Turning-Ideas-into-Action · 2_, 2_A-Structured-Approach-to-Developing-Ideas, 2_An-Era, 2_Same-Process, 2_Structured-Approach-to-Population-Health · 3_, 3_The-Education-Gap, 3_The-Ideal-State-5-Step-Process, 3_Two-Processes-One-Mind · 4_, 4_Leadership-and-Risk-Awareness, 4_Leadership-and-Risk-Awareness-in-Public-Health, 4_The-Critical-Gap, 4_The-Innovators-DNA · 5_, 5_Common-Obstacles, 5_Obstacles-in-Building-the-Ideal-State, 5_The-Real-Barrier · 6_, 6_Idea-vs-Opportunity, 6_Ideas-vs-Opportunities-A-Crucial-Distinction, 6_Your-Hidden-Superpower).

**REMAINING (28) — resume here next session, Claude-leads-then-operator-confirms mode:**
- **7_**: 7_, 7_Cognitive-Skills-in-Action, 7_From-Idea-to-Value-The-Framework, 7_Healthcares-Most-Valuable-Asset *(last of the 3 f_pattern-flagged)*
- **8_**: 8_Expected-Value-vs-Expected-Utility, 8_Our-Mission-Transform-Insights-Into-Impact, 8_The-Science-Behind-the-Connection
- **9_**: 9_Expected-Value-vs-Expected-Utility, 9_From-Bedside-to-Innovation, 9_The-Transformation
- **10_**: 10_Delivering-Value-in-Population-Health, 10_Delivering-Value-in-Public-Health, 10_Seize-the-Opportunity, 10_Youre-Already-an-Innovator
- **12_**: 12_Value-Proposition-Canvas, 12_Value-Proposition-Canvas-Aligning-Products-with-Customer-Needs *(watch for genuine `diagram_driven`/instructional-image — the canvas is a real framework)*
- **14_**: 14_What-Drives-Us-Toward-Opportunities
- **15_**: 15_Understanding-Motivation-Types
- **16_**: 16_Motivation-in-Health-Interventions, 16_Motivation-in-Public-Health-Interventions
- **17_**: 17_Leadership-Examples-in-Population-Health
- **18_**: 18_The-future-of-population-health-needs-YOU
- **19_**: 19_You-as-the-Ideal-Public-Health-Leader, 19_Your-Unique-Leadership-Qualities *(catalog's only `center_out` is here)*
- **20_**: 20_Resources-to-Enhance-Your-Journey
- **21_**: 21_Summary-The-Journey-of-Public-Health-Leadership
- **22_**: 22_Your-Next-Steps
- **NEVER SHOW (held-out 14):** 1_Diagnosis-Innovation, 3_Achieving-the-Ideal-State, 5_Check-Your-Understanding, 6_All-of-them-belong-to-BOTH, 8_Decision-Making-Foundations, 9_Comparing-Expected-Value-and-Expected-Utility, 11_*, 13_Effective-Problem-Solving-Approach, 15_Types-of-Motivation, 17_Examples-of-Effective-Leadership-in-Public-Health, 18_The-Future-of-Public-Health-Leadership, 20_Resources-for-Entrepreneurship-and-Innovation, 21_Key-Takeaways, 22_Next-Steps-Your-Path-Forward.

---

## 🔁 REUSABLE "SLIDE-PERCEPTION TRAINING" PROTOCOL (operator asked to memorialize the mechanics — repeat anytime)
A lightweight, resumable session format for refining the slide-perception / reading-path function from the operator's eye:
1. **One slide at a time**, by filename only (operator opens it from their own folder; do NOT rely on chat image rendering). Never show a held-out slide.
2. **Two interaction modes** (upgrade mid-session): **(A) operator-leads** — operator gives their immediate "eye read" (first fixation → scan order → image role → VO implication); Claude captures + provisional fit. **(B) Claude-leads** (after enough exemplars) — Claude reads PNG + perception JSON, proposes the tuple + VO treatment, operator confirms/corrects. Mode B is faster and doubles as a live test of the classifier's own reasoning.
3. **Capture each read** as: operator words (verbatim-ish) + provisional **tuple** (macro × image-role × text-substructure × cadence) + catalog-label delta. **Hold pattern naming/admission** until ≥4 exemplars across ≥2 genres (the catalog's own rubric).
4. **Track cross-cutting axes & universal narration principles separately** from per-slide reads (top of this file) — they generalize across patterns.
5. **Live notes file = single source of truth**; survives context loss; resume from the Progress block.
6. **Close** → synthesize → tune catalog → party green-light → NEW CYCLE classifier build → P2-4b calibration on the held-out 14.
> This protocol is itself a deliverable: it lets us re-train/refine perception cheaply whenever the corpus or product evolves. Memory: `[[feedback_slide_perception_training_protocol]]`.

---

## ⚙️ OPERATIONALIZATION — how the APP turns this evolving knowledge into better VO (answer to operator's closing question)
**The catalog is a versioned KNOWLEDGE ASSET (data, not code) that two runtime stages consume; training sessions like today's are the L3-learning loop that compounds it.**

Pipeline today: Gary exports slide PNGs → **vision specialist** perceives each PNG (live gpt-5.5 multimodal) → `PerceptionArtifact` (elements + bboxes + kinds) → **reading-path classifier** assigns the pattern → **Irene Pass-2** writes narration grounded in perceived visuals + scan order → verify-node conformance check.

Operationalization design (what to build, encoding today's findings):
1. **Refactor the catalog from a flat 7-enum into the COMPOSITIONAL TUPLE** `{macro_layout, image_role[per-element 1–4], text_substructure, narration_cadence}` + per-value **narration deltas** + the **universal principles** (title-anchor; scaffold-before-detail; callouts-always-VO; cue-don't-read-literal-strings; pacing>volume; peers-can-carry-light-thread). This is the structured prompt context for both LLM stages.
2. **Hybrid (c) classifier:** (a) cheap **deterministic geometry** pass detects macro-layout signals (tightened `_looks_z`; columns / split / grid / chevrons / numerals / arrows) — authoritative + counted; (b) **image-role tagging** by the perceiver — emit a ROLE tier per image element, NOT just `kind` (fixes the `kind:diagram`≠instructional trap seen 4×); (c) **gpt-5.5 LLM-escalation** (catalog-guided, ≥gpt-5.5 floor — operator directive) ONLY on ambiguity/low-confidence/geometry-LLM disagreement, returning the tuple with cited near-misses; (d) **default-degradation** → `top_down` reading-order, observable/counted.
3. **Irene Pass-2 is conditioned on the tuple:** the classified pattern selects its `script_writer_guidance` (narration delta + cadence + image-role handling) → scan-order-faithful, image-role-aware VO (decorative→no comment; illustrative→optional touch; instructional→walk through; pointer→type the message unit, don't narrate). Verify-node enforces the `reading_path` field; P2-4b's ≥80% conformance gate measures it.
4. **Learning loop (compounding):** each training session → operator-labeled exemplars + refined definitions → **catalog version bump** → optional geometry-threshold re-tune + Pass-2 guidance update → **P2-4b calibration** on the held-out 14 (top-1 ≥0.85 + ≥80% conformance, operator labels independently = anti-anchoring). Catalog = the L3 memory artifact in the three-layer intelligence model; it gets smarter as gpt-N improves AND as we run more training rounds.
5. **Governance:** building the classifier is a substrate change → party green-light the tuned catalog FIRST, then NEW CYCLE (Claude spec → Codex T1–T10 → Claude T11 + bmad-code-review), then P2-4b. No-mocks/real-live throughout (≥gpt-5.5).
</content>
