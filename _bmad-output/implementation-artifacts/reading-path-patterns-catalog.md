# Reading-Path Patterns Catalog — v1 (compositional-tuple form)

**Status:** v1 — TUNED from operator-led slide-perception training **round 1 (26/54 slides reviewed, operator-CLOSED 2026-06-22)** and **`bmad-party-mode` GREEN-WITH-AMENDMENTS (6/6, no impasse, 2026-06-22)**. Supersedes the v0-draft flat-7-enum (which was INVALIDATED: the flat enum is *why* `_looks_z` / `image_dominant` / `diagram_driven` over-claimed). Party amendments A1–A10 applied (see §10). **Ratified for the classifier-refactor spec.**
**Version:** v1 2026-06-22 (party-ratified). **Design authority:** `reading-path-patterns-design-decisions-2026-06-21.md` (rubric + hybrid-(c) architecture) + `reading-path-operator-review-round1-notes.md` (the round-1 evidence; single source of truth). **Held-out:** the 14 reserved slides were NOT used here and must NOT be (P2-4b calibration only).
**Reading direction:** Western LTR (hard-coded assumption; revisit for RTL/CJK).

---

## 0. What changed from v0-draft → v1 (round-1 evidence)
1. **A slide is a COMPOSITION, not one flat label.** The reading path is now a **compositional tuple** `{macro_layout × image_role(per-element, 1–4) × text_substructure × narration_cadence}`. The classifier emits the tuple; a human-readable **primary pattern name** is derived from `macro_layout × dominant text_substructure` for back-compat.
2. **IMAGE-ROLE split out as an orthogonal per-element axis** (4 tiers). This fixes the v0 `image_dominant` error ("narrate the image") — only tier-3 instructional images get a walk-through; most slide images are tier-1 decorative and get **no VO**.
3. **ADMIT `two_up_comparison`** (5 fits in the reviewed 26 — clears N≥4): comparison is a **text-substructure** that renders full-width (macro `two_pane`) OR nested in the text half of a `split_image_text`.
4. **ADMIT `multi_column`** (3 fits in the reviewed 26 — operator-admitted at 3; expect more in the unreviewed 28): N≥3 **parallel/coordinate peer** facets (no tension), distinct from oppositional `two_up_comparison`.
5. **ADMIT `text_hero_divider`** (5 fits — was Q3 "headline_dominant"): full-bleed single-impression headline/poster, with sub-types **section-opener** vs **CTA/contact card**.
6. **REASSIGN `f_pattern`** (Q2): 2 of 3 v0-flagged slides confirmed misfit → `split_image_text` decorative. `f_pattern` kept **defined at 0 confirmed exemplars** (mis-calibrated predicate retired from active firing).
7. **GATE `diagram_driven`** (Q1): the perceiver's `kind:diagram` ≠ instructional. Seen 4× in the 26 as decorative/semi-transparent/background. Admit `diagram_driven` ONLY when the diagram is **foreground + opaque + structurally load-bearing**. 0 confirmed instructional fits in the reviewed 26 (candidate: `12_Value-Proposition-Canvas`, unreviewed).
8. **DEMOTE `z_pattern`** (the v0 over-claim, 43/54, 24 false-pos): genuine "Z" is just **natural reading-order over peer content when geometry imposes no other order** — i.e. the DEFAULT applied to a peer grid. **PARTY-RATIFIED (A2): DEMOTE, not retire** — z_pattern survives only as a rare **narration-cadence flag** ("corner-to-corner anchor sweep"), usable ONLY when tier-1 hero elements sit at diagonal extremes with nothing competing between them. It is NOT a macro-layout. Demote (not delete) keeps the schema additive (no enum value removed → lockstep stays minor). Most v0 Z-labels reassign to `split_image_text` / `two_up_comparison` / `multi_column` / `top_down`.

---

## 1. Governance header — admission rubric (a pattern is admitted ONLY if ALL hold)
1. **N≥4 corpus exemplars** spanning **≥2 content genres** (kills topic-creep).
2. **Behavioral-distinctness:** narrates in a *different order/grouping* than every other pattern — stated as a one-line **narration-delta**. No delta → not a pattern.
3. **Non-overlap:** not a sub-case of an existing pattern.
4. **Stability:** survives clustering perturbation.
Failing any bar → the slide routes to the **DEFAULT** (`top_down` position-order), not a new pattern. **No 2× quota.**
*Round-1 exception logged for transparency (PARTY-RATIFIED A3 — named, reasoned, time-boxed):* `multi_column` is admitted at **N=3** in the reviewed subset by explicit operator directive (structurally unambiguous; ≥4 expected once the unreviewed 28 are classified). It is stamped **PROVISIONAL — `admitted-by-operator-directive, N=3 sub-rubric, auto-demote if unreviewed-28 + held-out do not lift it to N≥4-across-≥2-genres`**, AND **QUARANTINED for measurement**: it may be *emitted* by the classifier but is **EXCLUDED from the top-1 ≥0.85 denominator** until N≥4 corroborates (Murat's anti-contamination rider; enforced in code, not convention). This preserves the "no quota / land where evidence leaves it" principle as auditable rather than negotiable.

---

## 2. THE COMPOSITIONAL TUPLE (4 axes)

### AXIS 1 — `macro_layout` (the dominant spatial split; detected from geometry, content-blind)
| value | signature | how VO treats it |
|---|---|---|
| **`split_image_text`** | ≈half image \| half text; **side-agnostic** (image L, R, or top). THE MOST COMMON shape. | message-led: narrate the text side; image per its role tier. |
| **`text_hero_divider`** | full-bleed, one dominant centered headline/poster; little/no body. | single-impression beat; sparse cadence. Sub-types: section-opener / CTA-contact. |
| **`multi_column`** | N≥3 **parallel peer** columns (coordinate facets, no tension). | title-anchor → left-to-right, one beat per column. |
| **`two_pane`** | 2 **oppositional** panes, vertically symmetric, per-side subheadings. | establish framing → walk side A vs side B (carries `comparison_pair`). |
| **`card_grid`** | peer cards/boxes in a grid (e.g. 3+2), no imposed sequence. | row-major reading-order; bottom summary = resolution beat. |
| **`single_text_block`** | vertically-stacked text, no focal hero. | top→bottom reading order; scaffold-before-detail if dense. |

**Side-agnostic rule:** `split_image_text` must NOT hard-code image-on-right — image/text may be on either side ("mirror image"; e.g. `4_Leadership-and-Risk-Awareness`). Detect from geometry.

### AXIS 2 — `image_role` (per-element tier; the real VO discriminator)
| tier | name | VO treatment |
|---|---|---|
| **1** | **decorative / evocative** | sets tone/mood/concept. **NO VO comment.** (incl. semi-transparent/background "diagrams".) |
| **2** | **illustrative** | MAY be lightly referenced; **NOT** technical → no detailed walk-through. |
| **2.5** | **evidentiary / exhibit** *(party A4, Caravaggio; `unconfirmed-in-reviewed-26 — validate at P2-4b`)* | screenshot / chart / photo-as-proof. The eye **glances to verify the claim, then returns to text** — distinct from both flavor (2) and instruction (3). VO = **one "as you can see here…" beat**, not a walk-through. Candidate carrier: results/canvas/exhibit slides (watch `12_Value-Proposition-Canvas`, unreviewed). |
| **3** | **instructional / technical** | content the VO **MUST walk through** (diagram/canvas/chart/framework, foreground+opaque+load-bearing). |
| **4** | **pointer / iconographic** | small icon that **types** the adjacent message unit (calendar→time fact; Asclepius→medical). Not narrated as an image; aids the writer in inferring the box's intent. |
**Emitted per image element by the perceiver — NOT a single slide-level label, and NOT inferred from `kind` alone.** The 4× `kind:diagram`≠instructional trap (`4_The-Critical-Gap`, `7_Healthcares`, `5_`, `6_`) is fixed here. The tier-2.5 evidentiary band was added by party review (not observed in the reviewed 26) — carry as provisional; confirm/discard at P2-4b.

### AXIS 3 — `text_substructure` (independent of layout)
| value | signature | narration-delta |
|---|---|---|
| **`enumerated_process`** | order load-bearing — imposed by **numerals OR arrows/flow/connectors**. | strict order walk; speak ordinals/step-verbs; one beat per step. |
| **`peer_boxes`** | coordinate items (boxed or stacked), no imposed sequence. | natural reading-order; **semantics confirm order when geometry is neutral**; peers MAY carry a light connective thread. |
| **`comparison_pair`** | 2 oppositional sides w/ per-side subheadings (admitted as `two_up_comparison`). | establish both sides → walk the contrast. **Composes with any macro** (full-width `two_pane` OR nested in `split_image_text`). |
| **`dense_exposition`** | paragraphs / heavy copy. | title-anchor → **scaffold** (name the headings) → walk detail; summarize, don't recite. |
| **`hero_message`** | one big headline / 1–3 bold messages. | single-impression beat; echo on-screen phrasing; sparse. |

### AXIS 4 — `narration_cadence` (pacing > word-volume)
`sparse_slow` (poster/ad/divider — 1–2 sentences) ↔ `moderate` (split/peer) ↔ `dense` (exposition). Cadence is a first-class field; it matches slide density.

---

## 3. UNIVERSAL VO PRINCIPLES (apply across ALL patterns)
1. **Title-anchor-then-synthesize.** Always open by echoing the bold title (anchor the start), then summary/highlights/emphasis. **Never literal page-reading.**
2. **Scaffold-before-detail.** On dense slides, after the title, name the other headings/subheadings (a brief outline) before walking the detailed content.
3. **Callouts always get direct VO.** Hunt every slide for callouts (e.g. "YOU START HERE") and narrate each — never skip.
4. **Cue-don't-read-literal-strings.** For CTA/contact/literal-string content, voice the gist/intent ("contact JCPH by email or phone…") — never read raw emails, URLs, phone numbers, handles.
5. **Cadence matches density.** Poster/ad slides → brief, slow narration; exposition → denser. Pacing/timing > word-volume.
6. **Peers may carry a light connective thread.** Coordinate (peer) items may get light connective narration when the semantic context implies a thread — not just disconnected box-reading.

---

## 4. ADMITTED PATTERNS (recognizable composite tuples; primary `reading_path` names)
Each = a recurring tuple with N≥4 (or operator-admitted) + a distinct narration-delta. Exemplars cite **reviewed** slides from the 26.

### 4.1 `split_image_text` *(MOST COMMON; N=9 reviewed exemplars, pinned below — clears N≥4)*
- **tuple:** macro=`split_image_text` · image-role=1 (usually) · text=`peer_boxes`|`dense_exposition`|`comparison_pair` · cadence=moderate.
- **scan/narration:** title-anchor on the text side → walk the text substructure; image gets VO **only** per its tier (tier-1 → none). Side-agnostic.
- **exemplars:** `1_From-Idea-to-Action`, `1_The-Modern-Clinicians-Dilemma`, `3_The-Education-Gap`, `4_Leadership-and-Risk-Awareness`, `4_The-Critical-Gap`, `5_Common-Obstacles`, `6_Your-Hidden-Superpower`, `6_Idea-vs-Opportunity` (nested comparison), `4_Leadership-and-Risk-Awareness-in-Public-Health` (dense variant).
- **replaces** the v0 `image_dominant` for these slides (image is context, not subject).

### 4.2 `two_up_comparison` *(ADMITTED; 5 fits — clears N≥4)*
- **tuple:** macro=`two_pane` (full-width) OR `split_image_text` (nested) · text=`comparison_pair` · image-role=1–2 · cadence=moderate→dense.
- **scan/narration:** title-anchor establishes the framing → walk side A vs side B (per-side subheadings) → closing synthesis/segue if present. NOT a diagonal/top-down sweep.
- **discriminator:** 2 **oppositional** sides w/ subheadings (vs `multi_column`'s coordinate peers).
- **exemplars:** `2_` (Clinical Reasoning/Design Thinking), `2_Same-Process-Different-Context`, `3_Two-Processes-One-Mind`, `6_Idea-vs-Opportunity` (nested), `6_Ideas-vs-Opportunities-A-Crucial-Distinction` (full-width prose + closing synthesis).

### 4.3 `multi_column` *(ADMITTED PROVISIONAL at N=3, QUARANTINED from pass-bar; operator directive + party A3)*
- **tuple:** macro=`multi_column` · text=`peer_boxes` (L→R) · image-role=1 or 4 · cadence=moderate.
- **scan/narration:** title-anchor → left-to-right, one beat per column; may carry a light connective thread.
- **discriminator:** N≥3 **parallel/coordinate** facets, no tension; chevron/arrow STYLING does NOT make it a process (gate `enumerated_process` on content being sequential, not on decorative chevron shape).
- **exemplars:** `2_An-Era-of-Unprecedented-Change`, `4_The-Innovators-DNA-is-Clinical-DNA`, `5_The-Real-Barrier` (chevrons, peers).

### 4.4 `text_hero_divider` *(ADMITTED; 5 fits — was Q3 headline_dominant)*
- **tuple:** macro=`text_hero_divider` · text=`hero_message` · image-role=1 (background) · cadence=`sparse_slow`.
- **scan/narration:** single high-impact beat; speak the headline message; nothing competes.
- **sub-types:** **section-opener** (`1_` "THE INFLECTION POINT", `5_` course-opener) — orient/transition; **CTA / contact card** (`6_` "Apply.", `3_` poster) — cue purpose, don't read literal strings; may be near-skip end-cards.
- **exemplars:** `1_`, `3_`, `4_`, `5_`, `6_` (bare dividers).
- **replaces** v0 `diagram_driven`/`image_dominant` for bare dividers.

### 4.5 `enumerated_process` *(broadened from `sequence_numbered`; N=3 reviewed fits, pinned below, + directed-flow family)*
- **tuple:** macro=any · text=`enumerated_process` · cadence=moderate.
- **scan/narration:** strict order walk (1→N); speak ordinals/step-verbs; one beat per step.
- **broadening:** order may be imposed by **numerals OR arrows/connectors/flow** (the "directed-order" family). Detect arrow/connector geometry as an order signal, not just ordinals. Operator term: **"process slide."**
- **exemplars:** `2_A-Structured-Approach-to-Developing-Ideas`, `2_Structured-Approach-to-Population-Health`, `3_The-Ideal-State-5-Step-Process` (arrows+steps); `3_` poster (spark→build→drive directed flow).
- **guard:** prose "first…then…" WITHOUT per-element markers must NOT trigger this (`_has_ordinal` over-trigger).

### 4.6 `top_down` exposition *(ADMITTED + the DEFAULT)*
- **tuple:** macro=`single_text_block`|`card_grid` · text=`dense_exposition`|`peer_boxes` · cadence=dense.
- **scan/narration:** plain physical reading order (top→bottom, row-major); title-anchor → scaffold-before-detail on dense slides.
- **exemplars:** `1_Turning-Ideas-into-Action-HII-Meeting-Preparation`, `4_Leadership-and-Risk-Awareness-in-Public-Health` (dense), `5_Obstacles-in-Building-the-Ideal-State` (card grid; semantics confirm order).

---

## 5. DEFINED-BUT-GATED / DEFERRED
> **Evidentiary discipline (party A5, Mary):** "0 confirmed in the reviewed 26" ≠ "does not exist in the 54." These entries are tagged **`0 confirmed — re-test against unreviewed-28 + held-out`**, NOT hard-deleted. Absence of evidence over a 26-slide sample is not evidence of absence.
- **`diagram_driven`** — DEFINED, **GATED** on foreground+opaque+load-bearing (image-role tier 3). **0 confirmed instructional fits in the reviewed 26 — `re-test against unreviewed-28`.** Candidate: `12_Value-Proposition-Canvas` (unreviewed — a real framework; watch). Do NOT fire on decorative/background/semi-transparent diagrams. ("0 instructional diagrams exist" is unproven on this sample.)
- **`f_pattern`** — DEFINED at **0 confirmed exemplars — `re-test against unreviewed-28`**; predicate retired from active firing (mis-calibrated; fired on low-density slides that are actually `split_image_text`). Re-admit only on genuine dense-text left-margin-skim evidence.
- **`center_out`** — DEFINED, N=1 (`19_You-as-the-Ideal-Public-Health-Leader`, unreviewed). Keep.
- **`z_pattern`** — **DEMOTED (party-ratified A2)** to a rare narration-cadence flag (see §0.8 / §4 not-a-macro). Genuine "Z" = natural reading-order over peer content when geometry imposes no other order = the DEFAULT applied to `peer_boxes`. Most v0 Z-labels reassign to `split_image_text` / `two_up_comparison` / `multi_column` / `top_down`. NOT deleted (keeps schema additive).
- **`triptych_3up`, `grid_quadrant`** — defined stubs; 0 fits; deferred (no quota).

---

## 6. DEFAULT / FALLBACK (defined entry, not a failure state)
**`top_down` position-order** is the no-confidence fallback (operator-ratified — NOT Z). When the hybrid is low-confidence or geometry/LLM disagree with no clear winner: narrate elements in perceived bounding-box order (top→bottom, left→right within rows). **`peer_boxes` with neutral geometry resolves to this default**, semantics-confirmed (title→first box). The default must be **observable/counted** so default-heavy runs are visible.

---

## 7. SCRIPT-WRITER GUIDANCE (Irene Pass-2 — keyed to the tuple)
The classified tuple selects the narration treatment. Image-role drives image VO **regardless of pattern**:
- **image-role 1 (decorative):** no comment. **2 (illustrative):** optional light touch. **3 (instructional):** walk the structure's logic (entry→output), not box-by-box geometry. **4 (pointer):** don't narrate; let it type the message unit.
- **`split_image_text`:** title-anchor the text side → walk the text substructure; image per tier.
- **`two_up_comparison`:** establish framing → side A vs side B → synthesis/segue.
- **`multi_column`:** title-anchor → L→R one beat per column; light thread if implied.
- **`text_hero_divider`:** one impression beat; sparse. CTA/contact → cue purpose, don't read strings.
- **`enumerated_process`:** strict order; speak ordinals/step-verbs.
- **`top_down`/DEFAULT:** physical reading order; scaffold-before-detail if dense.
- **Universal:** apply §3 principles 1–6 on every slide; the resolution beat is the transition to the next slide.

---

## 8. BUILD DIRECTIVE — production slide-analysis LLM floor (operator, binding)
The LLM on the hybrid classifier's **escalation leg** (catalog-guided disambiguation) must be **≥ OpenAI gpt-5.5** — at least as capable as the model used for this review. Do NOT downgrade to a cheaper tier. No mocks: perception + pattern-ID are real live gpt-5.5 calls; test determinism via recorded-real responses behind a parse seam only, never a fixture on the production path.

---

## 9. CARRY-FORWARD — BUILD CONTRACT (party-ratified; binding on the classifier-refactor spec)

### 9.1 Schema = ADDITIVE (A1; Winston + Amelia)
- `reading_path` **stays a closed enum** = the **derived PRIMARY NAME** (computed from the tuple via a pure function). No enum value removed.
- Add the tuple as **NEW OPTIONAL sibling fields**: `macro_layout`, `image_roles: list[ImageRole]` (per-element, tiers {1, 2, 2.5, 3, 4}), `text_substructure`, `narration_cadence`.
- Vocab bump **dp-v1.5 → dp-v1.6 (additive MINOR, Tier-2)** — not a major. Manifest/pack delta = fields added, nothing removed → pipeline-lockstep stays minor.
- **Pin the tuple→primary-name derivation in ONE module with its own shape-pin test** (the load-bearing invariant; projection cannot drift silently).
- Existing P2-4a red-rejection / shape-pin tests must stay GREEN (additive non-regression).

### 9.2 Build SPLIT into 3 stories (A8; Amelia)
- **S1 — deterministic geometry** (NO LLM, no perceiver change): macro-layout detection + scan-order + default-degradation counter + tightened `_looks_z` + tuple→primary-name derivation. **First RED slice; proves the additive schema + non-regression with zero LLM risk.**
- **S2 — per-element image-role tier emission** (perceiver contract change: emit tier, not just `kind`).
- **S3 — gpt-5.5 ambiguity-escalation arbitration** (≥gpt-5.5 floor, no downgrade) returning the tuple + cited near-misses; recorded-real responses behind a parse seam only, never a production-path fixture.

### 9.3 Implementation GAPS to close before S2/S3 open (A9; Amelia)
1. **`multi_column` peers vs `two_pane` oppositional sides** — needs a deterministic geometric discriminant (column-count / gutter-symmetry / equal-vs-asymmetric width / parallel-vs-opposed content) OR an explicit decision to route this distinction to S3 LLM escalation. Caravaggio's guard: `split_image_text` = ONE message + ONE image; two peer contents weighed against each other ⇒ comparison/columns. **Spec must state whether peer-vs-oppositional is a geometry call or an LLM call.**
2. **Image-role tier-assignment rubric** — map observable features (bbox area %, centrality, caption-adjacency, count, foreground/opacity) → tier {1, 2, 2.5, 3, 4}. Deterministic-in-geometry vs perceiver-judgment must be decided.
3. **Ambiguity-escalation trigger predicate** — a measurable predicate (top-2 macro-layout margin / `_looks_z` near-miss band) so escalation rate is observable + testable + cost-accountable.

### 9.4 Conformance-measurement contract (A6; Murat — binding on P2-4b)
- **Top-1 ≥0.85 = STRICT exact match on the PRIMARY KEY `{macro_layout × image_role}` only** (no partial credit). This is the headline narration-driver metric.
- **`text_substructure` + `narration_cadence` reported as a SEPARATE per-axis conformance vector** — NEVER folded into top-1 (prevents a strong macro masking a vacuous secondary axis). *(absorbs John's A10 trim: secondary axes exist but do not gate the headline metric.)*
- **≥80% conformance = full-tuple exact match** across all axes. Two numbers, two bars.
- **Per-axis confusion matrix emitted** as an artifact.
- **`multi_column` EXCLUDED from the top-1 denominator** until N≥4 (A3 quarantine, enforced in code).
- **Contamination check:** record, per held-out slide, whether its gold label invokes a gated/retired pattern (`diagram_driven`/`f_pattern`). If ≥2 of 14 legitimately want one, the retirement was overfit and the 0.85 is contaminated — a recorded observable, not a footnote.

### 9.5 RED-first fixtures — non-negotiable pass-bar (A7; Murat)
1. **Default-degradation counter + ceiling** — DEFAULT/top_down emission counted + reported per run; **DEFAULT ≤ ~25%** ceiling; a route-everything-to-DEFAULT classifier must FAIL. (anti-vacuity tripwire, RED first.)
2. **`diagram_driven` foreground-gate negative control** — decorative/background image (not foreground+opaque+load-bearing) ⇒ assert NOT `diagram_driven`.
3. **`kind:diagram` ≠ instructional trap** — `kind:diagram` but illustrative/non-load-bearing ⇒ assert NOT `diagram_driven` (standing negative control; the exact 26-slide finding).
4. **`multi_column` quarantine** — assert it is excluded from the top-1 denominator until the evidence flag flips (in code, not convention).
5. **Escalation parse-seam** — malformed/empty gpt-5.5 escalation response degrades to DEFAULT, **counted**, never crashes or silently mislabels.

### 9.6 P2-4b calibration (operator-gated; unchanged)
Operator labels the held-out 14 independently (anti-anchoring) → primary-key top-1 ≥0.85 + ≥80% full-tuple conformance. The 28 unreviewed working slides + remaining counts (`multi_column` ≥4, genuine `diagram_driven`, tier-2.5 evidentiary, f_pattern) re-confirm here. Tags throughout this catalog marked `re-test at P2-4b` / `re-test against unreviewed-28` resolve here.

---

## 10. PARTY-MODE DISPOSITION (2026-06-22) — GREEN-WITH-AMENDMENTS, 6/6, no impasse
Fully-spawned `bmad-party-mode`: Winston (architect), John (PM), Murat (test architect), Mary (analyst), Amelia (dev), Caravaggio (presentation). **Unanimous GREEN-WITH-AMENDMENTS; Quinn→John impasse chain NOT triggered.** The three open dispositions resolved: **#1** z_pattern → DEMOTE (A2); **#2** multi_column → ADMIT provisional + quarantined (A3); **#3** schema → ADDITIVE enum-plus-optional-tuple (A1).

| ID | Amendment | Source | Where applied |
|---|---|---|---|
| A1 | Additive schema: enum primary-name + optional tuple fields, dp-v1.6 minor, pinned derivation + shape-pin test | Winston, Amelia | §9.1 |
| A2 | z_pattern DEMOTE (not retire) → rare cadence-flag; keeps schema additive | Amelia, Caravaggio, +all | §0.8, §5 |
| A3 | multi_column admit PROVISIONAL + QUARANTINED (excluded from top-1 denominator until N≥4; auto-demote tripwire) | Winston, John, Murat, Mary | §1, §4.3, §9.4 |
| A4 | Add image-role tier 2.5 evidentiary/exhibit (glance-to-verify beat); provisional, validate at P2-4b | Caravaggio | §2 AXIS 2 |
| A5 | Evidentiary discipline: pin `~` counts to slide-IDs; f_pattern/diagram_driven = "0, re-test against unreviewed-28"; tag untested tuple cells + cadence axis `unconfirmed, re-test at P2-4b` | Mary, Murat | §4, §5, §9.6 |
| A6 | Conformance contract: strict primary-key top-1 (≥0.85) + separate per-axis vector + full-tuple ≥80% + per-axis confusion + contamination check | Murat | §9.4 |
| A7 | Five RED-first fixtures as non-negotiable build pass-bar | Murat | §9.5 |
| A8 | Split hybrid-(c) build into S1 (geometry, first RED) / S2 (image-role) / S3 (LLM escalation) | Amelia | §9.2 |
| A9 | Close 3 implementation gaps before S2/S3 (peer-vs-oppositional discriminant; tier-assignment rubric; escalation trigger predicate) | Amelia | §9.3 |
| A10 | Scope: macro_layout + image_role + 6 VO principles are the value payload; cadence + text_substructure must NOT gate the headline metric | John | absorbed into §9.4 (secondary axes off top-1) |

**Watch-item (not blocking, Caravaggio):** a possible third `text_hero_divider` sub-type — `title/cover` establishing-shot — distinct from section-opener; flag if it appears in the unreviewed 28, do not pre-build.
