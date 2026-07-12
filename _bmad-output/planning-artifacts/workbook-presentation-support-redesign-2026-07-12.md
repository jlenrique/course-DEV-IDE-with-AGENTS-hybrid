# Design Spec — Presentation-Support Workbook (REDESIGN, pass one)

**Status:** active design (brainstorm capture — LIVING doc, updated as the design conversation proceeds)
**Date opened:** 2026-07-12
**Supersedes / extends:** [`workbook-component-design-2026-06-25.md`](workbook-component-design-2026-06-25.md) (the original S0–S7 companion-workbook spike — now partly obsolete; this doc is the pass-one redesign)
**Method:** BMAD creative party-mode brainstorm (Carson · Caravaggio · Sophia · Maya · Sally), operator-steered
**Operator:** Juanl

> **Why this doc exists:** to make the redesign durable and crash-proof. Running notes also live in session memory, but that is conversation-scoped; this file is the version-controlled source of truth. Committed to git as we go.

---

## 0. The reframe

This artifact is a **presentation-support workbook** — *one type* of workbook. Over time the app will offer other workbook options, and workbooks will be distinguished from **job aids** (a different animal: a job aid is consumed *at the moment of doing* — glance-and-go; a workbook is consumed *away from the doing*, to build the person who will later do it).

"**Support**" has two halves, wrapped around the week's presentation:
- **Preview / pre-work** — before the learner encounters the presentation.
- **Review** — after, to consolidate.

The presentation itself is deliberately **"at a glance"** by design (perception-tuned slides, tight narration). Therefore the workbook's priority payload is **prose depth** — the depth the glance-deck cannot carry (possibly keyed to specific slides, possibly organized another way — OPEN).

**Design frame kept:** every workbook element earns its place by which "support" it delivers — **recall · depth · transfer · engagement** (Carson's four supports).

---

## 1. Course / delivery context (binding)

- The course is **always an asynchronous online course.** What varies is how the presentation is *encountered*:
  - **Fully asynchronous** (e.g. the **HIL** course): the presentation is **recorded**; the student presses play whenever. No cohort synchrony, no scheduled beat, no instructor in the room to reward pre-work.
  - **Hybrid / flipped** (e.g. the **HAI** course): the lecture is **live at a specified point in the term**. Cohort synchrony + an instructor who can close the pre-work loop live.
- **Two real courses in scope now:** HIL (fully async) + HAI (hybrid). The design must serve **both**.
- **Weekly cycle:** one module = one week = **one presentation** (live in HAI, recorded in HIL). Pre-work on the front, review on the back.
- **Pre-work = pre- to *encountering the presentation*** (pre- to the live lecture in hybrid; pre- to viewing the recording in async).

**Design principle — design for the weakest support environment:** build pre-work so it **self-closes inside the workbook** (for the solitary async HIL learner at midnight, with no cohort and no instructor to reward it). The hybrid HAI live lecture then becomes a **bonus amplifier, not a dependency.**

---

## 2. Decisions locked (pass one)

| Decision | Ruling |
|---|---|
| Transcript (old S3) | **Out** of the workbook — break out as a separate, optionally-downloadable student resource. |
| Embedded slide screenshots (old S4 Figures) | **Cut** — felt like bloat/waste; students can download the source slide deck. |
| Recall / depth / transfer / engagement | **Kept** as the organizing frame. |
| Prose depth | **The priority payload** (slides are glance-only by design). Keying scheme (per-slide vs other) still OPEN. |
| "Support" scope | **Preview + Review**, wrapped around the weekly presentation. |
| First-run S0–S9 artifact | Operator no longer likes it; this redesign replaces it. |

**Standing forward-work (from the earlier conversation, still in scope):** the two research-derived components must become **standard** sections of the standard workbook design —
- **Research Glossary** (encyclopedia articles, W2 — `app/marcus/lesson_plan/glossary_projection.py`)
- **Research Trends & Hot Topics** (W3 — `app/marcus/lesson_plan/trends_projection.py`)

Both are already built + wired into `WorkbookProducer.produce()`, both anti-fabrication (never invent scholarship; explicitly-empty when the packet has no usable rows), but both are **absent from the design spec** (they postdate the 2026-06-25 doc). Promote them to first-class standard sections in this redesign.

---

## 3. PRE-WORK design (SETTLED for pass one)

Pre-work is a **stable weekly ritual** (predictable container so the learner learns the rhythm) holding **fresh weekly content** (Sally: boring-on-purpose frame; Caravaggio: "stable frame, surprising scene inside"). It is **scenario + advance organizer**, in three beats.

### The reverse-engineering contract (how the producer builds it)

- **Input:** the SME's existing presentation, which already speaks to pain points.
- **Task:** **reverse-engineer** the pre-work *from* the presentation — **extract, never invent.** (This matches the app's anti-fabrication ethos; the surfaced difficulties must be **traceable to slides/narration** and, critically, must be ones the presentation **genuinely pays off** — do not exhume a pain the talk never soothes.)
- **Extract latent difficulty:** areas of **stress, frustration, confusion, uncertainty, or simply difficult decision-making / difficult skill-building** that the presentation addresses. (So the learner-facing instrument is really a **friction / difficulty scale** — it flexes beyond "pain/suffering" to cover skill-building weeks.)
- **Objectives are respected, not replaced:** the SME's LOs are authoritative. Even if they are "dry," the pre-work **exemplifies** them through grounded/contextualized instances in the scenario, and — if they are not already in compelling **abilities** language — the pre-work **re-phrases them as such.** Respect-not-replace; re-express-not-invent.

### The three beats

1. **The Scene** — a situation drawn from the learner's world that *surfaces the kind of difficulty* the presentation addresses (a pain-elicitor / **mirror**, not a case to solve). *Optional:* one thin **orienting line** above the scene on genuinely alien-topic weeks (a toe-in-the-door advance organizer) so the learner isn't locked out cold.

2. **The Friction Scale (Your Pain-Point)** — the **signature weekly instrument**. The learner **rates it (0–10), locates it, and writes one honest line.** Modeled on triage pain scales: **un-failable**, because the learner is the sole authority on their own subjective experience — no right answer, no humiliation. ~20 seconds; survives the midnight-clinician test. **Self-closes** in review ("eight weeks ago you rated this an 8 and wrote *this* — where are you now?"). The weekly marks **aggregate into a term-long self-portrait** of the learner's practice-friction (a keepsake, not a worksheet).

3. **The Promise** — the presentation's objectives, re-voiced as **pertinent-ability vows** keyed to the friction just rated: **not** "after this lesson you will [accomplish the complete solution]," but "you will be able to *see / name / take a first move on* it." Component capacities the single presentation can actually deliver — a **half-rhyme** with the ache (foreshadow the territory and the relevant tools; never hand over the answer). This beat hands the learner off to press-play / the live room.

**Sequencing:** scenario-first by default (the swing must be *innocent* to be productive); the advance organizer *brackets* the scene — a thin orienting line above on hard weeks, the full resonant objectives below. Same three-beat frame every week regardless of order emphasis.

**The loop rings twice:** a **promise** in preview → **proof** in review.

**Mode-agnostic:** the mechanism is identical whether the presentation is live (HAI) or recorded (HIL); the live lecture only amplifies beat-3's payoff.

### Frame-generalization test (Part 2 vs Part 4)

The three-beat frame was tested on two very different C1M1 lessons:
- **Part 2 — Macro Trends** (a fresh-pain lecture): scene = the "Modern Clinician's Dilemma" (a recurring transport-delay you can't fix), harvested from the SME's own Chapter-2 Q5; friction = *the system fighting your practice*; promise = *tell system-design pain from resilience pain*.
- **Part 4 — Assessments & Bridge to Module 2** (a bridge/capstone week, one closing video + assessments): scene = *the threshold of championing an idea vs. merely having one*; friction = *the "10% idea / 90% leadership" gap* (introspective/identity, not external system-pain); promise = *see the 90% as buildable skill, not innate gift*.

**Finding:** the frame **generalizes**, but the **Scene's *archetype* is lesson-type-dependent** — a fresh-pain lecture yields an external-friction scene; a bridge/identity capstone yields an introspective-threshold scene; a dry skill-build yields a difficulty scene. **The producer must detect lesson type and select the scene archetype accordingly.** Part 4 also carries an explicit source-adequacy warning ("fail loud, don't invent missing assets"), which becomes the producer's **adequacy gate**: on thin-source weeks the pre-work degrades honestly rather than fabricating a pain the deck can't pay off.

---

## 5. Reproduction / production architecture — the `pre_work_producer`

**The problem this section answers:** a BMAD creative party generated the Part-2 gem *once*. Production (Marcus-SPOC) must reproduce that quality across many courses and runs **with no party in the loop.** The resolution is the same one the codebase already uses twice — the party is a **design-time** activity whose output is a **reusable contract + gates + a golden exemplar**, not the content itself. Content is generated **per-run by a producer**, deterministically where possible and by a *leashed* LLM only where it must.

### 5.1 The precedent to mirror (do not reinvent)

`app/marcus/lesson_plan/glossary_projection.py` (W2) and `trends_projection.py` (W3) are the exact pattern:
- a **deterministic default projector** (`default_glossary_writer`) that composes from tier-labeled rows,
- an **injectable writer seam** (`GlossaryWriter`) for a richer LLM/SME pass later,
- **anti-fabrication** (rows missing provenance/`source_ref` are skipped into `known_losses`, never invented),
- **empty-honesty** (explicitly-empty section when no usable rows),
- a **shared-SSOT intake idiom** (`research_packet.resolve_for_<consumer>` — one load path, one witnessed digest).

`pre_work_producer` is a **new sibling projector** in the same M3-safe layer (imports `lesson_plan`, never `marcus.orchestrator`), most likely `app/marcus/lesson_plan/prework_projection.py`, consumed by the workbook producer leg the same way glossary/trends are wired in `workbook_producer/_act.py::build_workbook_inputs`.

### 5.2 Decompose the gem: deterministic vs. leashed-LLM

| Beat / element | Mechanism | Notes |
|---|---|---|
| The three-beat **frame** | **Deterministic** | Structure is fixed; renders identically every week/course. |
| Beat ② **Friction Scale instrument** | **Deterministic template** | The 0–10 scale, the locate field, the one-line field, the anchors, the "keep this for review" hook. No model. Byte-identical every run. |
| Honesty framing + review hook | **Deterministic** | Fixed copy. |
| Beat ① **The Scene** | **Leashed LLM** (extraction + composition) | Synthesized from *extracted* friction; **must trace to slide/narration provenance**; **harvest SME-authored scenarios first** (e.g. Part-2 Ch2 Q5) and only compose when none exists. Scene archetype selected by lesson-type detection (§4 finding). |
| Beat ③ **The Promise** | **Leashed LLM** (transform) | **Re-voices ratified LOs** into pertinent-ability vows. Respect-not-replace; never invents an objective. |

Only **two** beats touch a model, and both are bounded to *extract* or *transform* — never to *invent*.

### 5.3 LO source of truth — Irene's **ratified** Lesson Plan (binding)

**Once ratified, Irene's Lesson Plan is the single source of truth for learning objectives.** Beat ③ transforms the **ratified** LO set — not the raw SME slide bullets, not an ad-hoc extraction. Consequences:
- The pre-work (and the workbook generally) reads LOs from the ratified lesson plan; the SME's raw objectives are *input to Irene's planning*, not the producer's LO source.
- This **eliminates the "objective statement unresolved for `uNN`" placeholder** seen in the first-run artifact: a ratified plan resolves every bound objective by definition, so beat ③ always has real LOs to transform.
- **Ratification is a precondition.** Before ratification, LOs are provisional and pre-work beat ③ must not claim finality (degrade-with-record, consistent with the app's honesty discipline).

### 5.4 The party's judgment → encoded constraints + gates

Every rule the room fought over becomes a machine-enforceable constraint, not a vibe:

| Party ruling | Enforcement mechanism |
|---|---|
| Extract, don't invent | **Provenance gate** — scene friction traces to a slide/narration `source_ref` (same discipline as workbook G1 numeric / G2 citation fidelity). |
| Pain, not solution | **Prompt constraint** on the Scene composer. |
| Half-rhyme, not spoiler | **Spoiler-guard** — a review check / named operator spot-check that beat ③ foreshadows without handing over the answer. |
| Abilities, not complete-solution LOs | **Prompt constraint** on the Promise transform (over ratified LOs). |
| Must be pay-off-able / fail loud on thin source | **Adequacy gate** — degrade honestly (or request source) rather than fabricate; Part 4's README demands exactly this. |
| Friction flexes beyond suffering | **Lesson-type detection** selects the scene archetype (fresh-pain / bridge-identity / skill-build). |

### 5.5 The Part-2 gem seeds the producer

The gem is not discarded — it becomes:
- a **few-shot exemplar** inside the Scene/Promise prompts ("here is what excellent looks like; match this shape"), and
- a **golden shape-pin test** the producer's output is validated against (mirroring the workbook's existing shape-pin discipline).

### 5.6 Where it plugs in

- **Inputs:** `run_dir` (segment-manifest narration + corpus slides for scene extraction) · Irene's **ratified** lesson plan (`lesson_plan_from_run` — LO SSOT) · optional research packet (shared intake idiom, if a scene wants a cited anchor).
- **Output:** a `PreWorkBrief` (scene, friction-scale spec, promise vows + provenance) rendered into the workbook's front matter and, later, its own emitted section — same Markdown-canonical → DOCX path as the rest of the workbook.
- **Producer discipline:** deterministic frame + two leashed LLM steps + the §5.4 gates + empty/adequacy honesty. No new render dependency.

**Build-story shape:** a new `prework_projection.py` sibling (mirrors glossary/trends) + a thin wire-in at `build_workbook_inputs` + the §5.4 gates + the Part-2 golden fixture. Design-time party judgment is now a run-time producer.

---

## 6. REVIEW design (the "off-ramp" half of support)

Review is the **heavy** consolidation half (not a light loop-close): it carries all four watchwords, woven on a **learner-owned thread** rather than stacked as sections. It subtly **bookends** pre-work, then does real work for long-term retention + application.

### 6.1 The five-beat integrated structure (each beat → a watchword)

1. **Bookend** *(learner's pen)* — the friction-callback from pre-work. Short; sets the lens. → *engagement / loop-close.*
2. **Deep Dive** *(lesson-level)* — the prose depth the glance-deck couldn't hold (see §7), with **glossary terms bolded/highlighted inline as markers**; full encyclopedia entries live in their **own separate section** (textbook style). → **DEPTH.**
3. **Check on Learning** *(retrieval, not re-read)* — active-recall self-assessment that tests the **beat-③ abilities** the presentation promised → **promise-becomes-proof.** → **RECALL.**
4. **The Door Left Ajar** *(lesson-level)* — **trends / hot-topics** as the forward hook, scoped tight to the abilities (see §8). Honest, bounded, never forecasting-theater. → **ENGAGEMENT** (pulls her toward next week).
5. **Closing Reflection** *(learner's pen)* — apply the abilities to *her* friction: "given what you can now see/name/do — one move this week." Fuses bookend + transfer. → **TRANSFER.**

### 6.2 Decisions

- **Personalization lives in the learner's pen, not per-learner generation.** Only beats 1 & 5 are learner-written; beats 2–4 are **lesson-level** (produced once per lesson), framed to *invite* her to map them onto her friction. Producible *and* personal. (The producer must NOT promise "the deep dive is about YOUR friction" — it can't generate per-student.)
- **Measurement = Sophia's shifted question, NOT re-rating.** Do not re-rate the same 0–10 (the friction often won't drop — we didn't fix her EHR this week). Instead ask what she can now **name / see / do** that she couldn't in beat ① — measuring **capability gained, not cure.** Honors that her *relationship* to the friction changed even when the friction didn't.
- **Glossary = inline markers + separate section.** Key terms/concepts in the deep dive are **bolded/highlighted** as signals; the full encyclopedia entries live in a dedicated glossary section (reverses the current producer's trailing-block-only render).

---

## 7. THE DEEP DIVE — scope · design · produce

The core "at a glance can't hold this" payload. The presentation is glance-only *by design*; this is where the deferred depth lives.

- **Scope:** the **depth-delta** — precisely what the glance-slides omitted (mechanism, "why it matters," caveats, reasoning), organized **around the abilities** (ratified LOs), sub-threaded by the presentation's arc so it reads as narrative. A **proper superset** of the heard narration (the AC-8 `workbook_narrative ⊋ VO_script` invariant), never a disjoint rewrite, never contradicting the deck.
- **Design:** self-contained **read-prose** (a reader who missed the talk can follow), distinct from the now-separate downloadable transcript. Glossary terms **bolded inline** → entries in their own section (§6.2).
- **Produce:** **re-voice + expand the SME's narration** into read-prose via the `prose_revoicer` seam (the old design's `REVOICE-REQUIRED` stub) — a **transform of real source, not invention.** The narration is already fuller than the slide (e.g. Slide 2's speaker notes carry the whole system-design argument); the deep dive blooms *that*.

> **⛔ BINDING REQUIREMENT — the in-depth narrative read MUST cite its sources (operator, 2026-07-12).** The deep-dive prose is not free-floating exposition: every **load-bearing claim** — and *especially* every piece of **wrangled/enriched detail** beyond the SME's notes — carries an **inline citation** to a credible source, resolvable in the workbook's **references / further-reading** section. **Uncited enrichment does not enter the narrative.** This is the trust backbone of the read-channel and the concrete enforcement of the anti-fabrication ethos: a reader (or reviewer) can trace any depth claim back to its source. Citations flow Markdown-canonical → DOCX with the rest of the workbook, and are audited by the existing G2 citation-fidelity gate (`unsourced_citations == 0`).

### 7.1 The enrichment problem (operator, 2026-07-12)

Re-voicing risks mere **paraphrase** — which adds no depth. Genuine expansion to the depth-delta needs **content the SME's thin notes don't contain**, and that content may **only** come from **credible sourced expert knowledge — never model priors** (that would be fabrication). This is where **Tracy + Texas** first enter: they wrangle the enriching detail (mechanism, primary evidence, nuance) from credible resources, and the re-voicer expands *that*. Every enriching sentence that enters the narrative **carries its citation**, or it does not enter. Fabrication gates on this net-new prose surface: **numeric fidelity, superset-of-VO invariant, no-new-unsourced-claims, operator prose spot-check** (general semantic claim audit honestly deferred, per the existing `braid-workbook-semantic-claim-citation-audit`).

---

## 8. RESEARCH ASKS & PRODUCTION SEQUENCE (Tracy + Texas)

**Two distinct research asks — different purpose, do not smear them (operator, 2026-07-12):**

- **Ask A — Concept / Narrative Enrichment** *(inward-deepening)*: wrangle credible expert knowledge on the **concepts the lesson already teaches** (the mechanism behind "administrative waste," the evidence on burnout-as-system-design, etc.). Feeds **both** the deep-dive prose (§7) **and** the encyclopedia glossary — same intent, so **pair them into one research pass** (the "encyclopedic terms" step). Cited + credibility-tiered.
- **Ask B — Hot Topics / Trends** *(forward-expanding)*: **where the field is moving / being contested**, scoped tight to the specific abilities (even the pre-work scenario when possible). Different query, different intent — a **separate call to Tracy, run last.** Its narrowness is what keeps it honest (not a discipline survey / forecasting theater).

### 8.1 Glossary ↔ deep-dive dependency (operator finesse, 2026-07-12)

Separate the **knowledge** from the **rendered entries** — this dissolves the apparent circularity ("do I need the encyclopedic understanding to *write* the narrative, or the narrative to know which *entries* to render?"):
- **Ask A produces an encyclopedic KNOWLEDGE POOL** on the lesson's key concepts/terms — **upstream** — and it is exactly what the deep-dive writer draws on to write an informed, cited narrative. The encyclopedic understanding **is** available to (and informs) the narrative; there is no circular wait.
- The deep-dive writing, drawing on that pool, **marks the load-bearing terms** (bolds them inline).
- The rendered **Glossary section** is generated **downstream**, for exactly those bolded terms, **from the same pool** (no re-research). Optional targeted top-up only if a bolded term went uncovered.

So: **knowledge upstream** (feeds the narrative), **rendered entries downstream** (scoped by the narrative), one Ask-A pool serving both — writer stays informed, glossary stays non-redundant. (a real graph-order change — research is demand-driven by the workbook's own abilities, finest-grained last):**

```
(1) ratified LOs → abilities
(2) pre-work scene + friction
(3) deep-dive skeleton (narration re-voiced to depth-delta, ability-organized)
(4) Ask A → Tracy+Texas enrich concepts + ground glossary  (scoped to lesson concepts)
(5) Check-on-learning (tests beat-③ abilities)
(6) Ask B → Tracy hot-topics/trends  (scoped to the specific abilities + scene) — LAST
(7) compose review
```

This inverts today's flow (research minted generically up front at node `04.55`); the workbook's trends/enrichment are **derived from its own abilities**, not a generic upfront sweep. Flag loud for the build: this is a pipeline-ordering change, and Ask B is a *late, narrowly-scoped* Tracy pass distinct from the upfront research wiring.

---

## 9. Open threads (remaining)

- **Depth payload organization** — per-slide vs. per-ability keying within the deep dive is leaning **per-ability** (§7); confirm at build.
- **Term-highlighting render** — how bolded inline markers link to the separate glossary section in Markdown→DOCX (anchor links vs. plain bold).
- **Producer build** — see §11.

**Resolved since v1:** pre-work design + draft (§3–5) · reproduction architecture (§5) · LO SSOT = ratified plan (§5.3) · full Review design (§6) · deep-dive scope/design/produce + enrichment + binding cite-sources (§7) · two-research-ask model + production sequence (§8).

---

## 10. Consolidated standard section model (SUPERSEDES the 2026-06-25 S0–S9)

**Scope ruling (operator, 2026-07-12):** everything developed *this session* is the workbook; anything in the prior design that did not find a place today is **dropped.** The new standard **presentation-support workbook** is:

| Order | Section | Watchword | Source in old design |
|---|---|---|---|
| 0 | **Cover** (hero illustration [Gamma placeholder] · creative TOC · provenance) — see §12 | — | old S0 (partly) |
| 1 | **Pre-work — The Scene** | engagement | NEW |
| 2 | **Pre-work — The Friction Scale** | engagement | NEW |
| 3 | **Pre-work — The Promise** (abilities) | — | **transformed** from S1 Learning Objectives |
| — | *[the presentation is encountered — live HAI / recorded HIL]* | — | — |
| 4 | **Review — Bookend** (friction callback) | engagement | NEW |
| 5 | **Review — Deep Dive** (cited read-prose; glossary terms bolded inline) | **depth** | **transformed** from S2 Narrative/deferred-depth |
| 6 | **Review — Check on Learning** (retrieval; tests the abilities) | **recall** | **transformed** from S5 Exercises/Answer-key |
| 7 | **Review — The Door Left Ajar** (trends / hot-topics) | **engagement** | **kept + upgraded** from S9 |
| 8 | **Review — Closing Reflection** (apply abilities to her friction) | **transfer** | NEW |
| 9 | **Encyclopedia Glossary** (separate section; entries for the bolded terms) | depth | **kept + upgraded** from S8 |
| 10 | **References / Further Reading** (citations; binding) | depth | **kept** from S6 |
| 11 | **Honesty footer** (review marker; no reading-path halo) | — | **kept** from S7 |

**DROPPED (did not find a place today):**
- **S3 Transcript of record** → broken out as a **separate, optionally-downloadable** student resource (not a workbook section).
- **S4 Key figures / embedded slide screenshots** → cut (the deck is downloadable; screenshots were bloat).
- **S4b Key-figures claim table** → cut (was already deferred; not carried forward).

---

## 11. Review / deep-dive producer spec (extends §5)

Same discipline as `pre_work_producer` (§5): a sibling projector in the M3-safe `lesson_plan` layer (e.g. `review_projection.py`), consumed by the workbook producer leg; **deterministic frame + leashed-LLM only where it must + gates + empty/adequacy honesty.**

**Deterministic (free, every run):** the 5-beat review frame; the **Bookend** template (surfaces the learner's own pre-work friction mark); the **Check-on-Learning** instrument shell; the **Closing Reflection** prompt shell; the glossary **inline-marker + separate-section** render; the honesty footer.

**Leashed-LLM (bounded to transform/extract, never invent):**
- **Deep Dive** — re-voice + expand the SME narration to the depth-delta, ability-organized; **must cite sources inline** (§7 binding requirement); superset-of-VO; no-new-unsourced-claims.
- **Check on Learning** — retrieval questions that test the **beat-③ abilities** (promise→proof), grounded in the lesson (answers trace to source).
- **Closing Reflection** — a transfer prompt keyed to the abilities + the learner's friction (asks for *capability* — name/see/do — per Sophia's shifted-question rule, **not** a re-rate).

**Gates:** G2 citation-fidelity (deep-dive + research cite real sources) · numeric fidelity · superset-of-VO invariant · spoiler-guard (promise/check alignment doesn't leak the answer) · adequacy/empty-honesty (thin-source weeks degrade, never fabricate) · lesson-type detection (scene/deep-dive archetype).

**Research wiring (§8 two-ask model):** **Ask A** (concept/narrative enrichment — feeds deep dive + glossary, one pass) and **Ask B** (hot-topics/trends — separate, last, scoped to abilities/scene). Graph-order change: research is **demand-driven by the workbook's own abilities**, replacing the generic upfront mint at node `04.55` for these consumers.

**Golden fixtures:** the Part-2 pre-work gem (§3) + a Part-2 review/deep-dive golden, as few-shot exemplars **and** shape-pin tests.

---

## 12. Cover design (operator 2026-07-12)

The cover is **one "page" in three parts** — the workbook's front door. It absorbs the front-matter role of the old S0 Overview (the "how to use with the deck" note lives in Part 3's provenance).

### Part 1 — Hero illustration  *(⏳ Gamma generation = PLACEHOLDER)*
A full-width, eye-grabbing visual keyed to **this presentation's scenario and/or topics** — visually echoing the pre-work Scene so the cover and the friction the learner is about to name are dual-coded.
- **Gamma generation is deferred to a later step.** For now the producer emits a **named placeholder slot**: a deterministic **art-brief** derived from the scenario/topics (what the illustration should depict) + alt-text, occupying the hero position. The placeholder is *spec-in-place*, never an empty box; a later Gamma step swaps the real image in without a layout change.
- **Honesty:** the placeholder is visibly a placeholder in trial runs (no fabricated "final art" claim).

### Part 2 — Creative Table of Contents
Not a dry section list — a **learner-facing map of the journey**, framed by the three-phase rhythm:
- **Before you watch** → the pre-work beats (the Scene, your Friction Scale, the Promise).
- **[The presentation]** → live (HAI) or recorded (HIL).
- **After you watch** → the review beats (bookend, deep dive, test yourself, what's next in the field, your move) + the glossary + references.
- Friendly labels ("Test yourself," not "S6 Check on Learning"); generated deterministically from the §10 section model, with optional light scenario-flavored framing.

### Part 3 — Workbook provenance details
The trust/registry block: the presentation/module it supports (unit + objective binding), the SME, the production run id, generation date, the source-bundle/deck reference, the **citation/fidelity stamp** (G2 passed, capability notes), and the **"how to use this workbook with the deck"** note (dual-coding statement — glance-deck vs. read-workbook). Deterministic from run metadata; absorbs old S0 (how-to-use) + S7 (honesty) provenance.

**Produce:** Parts 2 & 3 are **deterministic** (from the section model + run metadata); Part 1 is a **deterministic placeholder + art-brief** now, **Gamma-filled later**. No new render dependency for the placeholder path.

---

## 13. PRD layer (this doc serves as the PRD — operator 2026-07-12)

Formal requirement elements so this design doc drives `bmad-create-epics-and-stories` directly (operator delegated: augment with any missing PRD elements, then use as the PRD).

### 13.1 Goals
- Replace the disliked first-run S0–S9 workbook with a **presentation-support workbook** that measurably improves **long-term retention + application**, wrapped as **preview + review** around the weekly presentation.
- Make it **reproducible across courses/runs by a producer** — design-time judgment encoded as run-time producer + gates + golden (no party per run).

### 13.2 Non-goals / out of scope
- **Per-learner content generation** (personalization is the learner's pen only — beats 1 & 5).
- **Gamma illustration generation** (placeholder this pass — §12 Part 1).
- **PDF render · worksheet fill-in affordances · full semantic claim audit** (deferred braids).
- **Other workbook types + job aids** (future; this is the *presentation-support* type only).
- **Term-long friction self-portrait** (cross-week aggregation of the weekly friction marks) — **deferred** (amendment A7): it is cross-week per-learner state, which the producible-not-per-learner rule (NFR4) forbids in the produced artifact. Revisit if/when a per-learner runtime layer exists.

### 13.3 Users / personas
- **Primary:** the async adult professional learner (e.g. practicing physician) in **HIL** (fully async, recorded) or **HAI** (hybrid, live) courses.
- **Secondary:** the operator/SME (trust via verifiable citations); the reviewer (fidelity gates).

### 13.4 Functional requirements (FR)
- **FR1** — Pre-work renders three beats: Scene · Friction Scale · Promise (§3).
- **FR2** — The Scene is **reverse-engineered** from the SME presentation (extract-not-invent; traceable to slides; harvest SME-authored scenarios first); **lesson-type detection** selects the scene archetype (§4/§5).
- **FR3** — The **Friction Scale** is the deterministic weekly instrument (rate 0–10 · locate · one line); un-failable; carries a **"keep this for review"** instruction. *(Amendment A7: scoped to the single-week instrument; the cross-week term-long self-portrait aggregation is a non-goal — §13.2.)*
- **FR4** — The **Promise** transforms **ratified LOs** into pertinent-ability vows (respect-not-replace; half-rhyme / no-spoiler).
- **FR5** — Review renders five beats: Bookend · Deep Dive · Check-on-Learning · Door-Ajar · Reflection, each mapped to a watchword (§6).
- **FR6** — Bookend emits a **callback prompt/template** referencing the learner's own beat-② friction mark — **not** the value (per-learner content is a non-goal); the learner re-reads her own ink.
- **FR7** — Deep Dive = **cited** self-contained read-prose, re-voiced + expanded from narration to the depth-delta, ability-organized, **superset-of-VO**, glossary terms bolded inline; **must cite sources** (binding, §7).
- **FR8** — Check-on-Learning = **retrieval** self-assessment testing the beat-③ abilities (promise→proof).
- **FR9** — Door-Ajar = trends / hot-topics (Ask B), scoped tight to abilities/scene, bounded + honest.
- **FR10** — Closing Reflection = transfer prompt keyed to abilities + friction; **Sophia's shifted question** (capability, not re-rate).
- **FR11** — Encyclopedia Glossary = separate section, entries for the bolded terms, from the Ask-A knowledge pool (§8.1).
- **FR12** — References / Further Reading renders the citation set (G2).
- **FR13** — Cover = hero placeholder + art-brief · creative journey-TOC · provenance (§12).
- **FR14** — LO SSOT = Irene's **ratified** lesson plan; pre-ratification degrades honestly (§5.3).
- **FR15** — Empty/adequacy honesty: thin-source weeks degrade, never fabricate (Part-4 case).
- **FR16** — Two research asks (A enrich+glossary-knowledge; B hot-topics), **demand-driven graph order** (§8).
- **FR17** — Dropped from the workbook: transcript (separate download), slide screenshots, claim table (§10).

### 13.5 Non-functional requirements (NFR)
- **NFR1 — Anti-fabrication:** extract/transform only; uncited enrichment does not enter; numeric fidelity; superset-of-VO; general semantic audit honestly deferred (WARN).
- **NFR2 — Determinism where possible:** frame · friction-scale · TOC · provenance · honesty footer are deterministic; only Scene · Promise · Deep-Dive · Check · Reflection are leashed-LLM.
- **NFR3 — Reproducible without a party:** producer + gates + golden exemplars; per-run; mode-agnostic.
- **NFR4 — Producible, not per-learner:** lesson-level content generated once; personalization via the learner's pen only.
- **NFR5 — Mode-agnostic + weekly ritual:** identical mechanism for HIL (recorded) / HAI (live); stable frame, fresh content.
- **NFR6 — Render:** Markdown-canonical → DOCX; no new render dependency (Gamma deferred).
- **NFR7 — Governance/layering:** pipeline-lockstep if trigger paths touched; M3-safe (`lesson_plan`, never `marcus.orchestrator`).
- **NFR8 — Evidence:** golden shape-pins + fidelity gates + operator prose spot-check; trial-run witness on the frozen tejal deck.

### 13.6 Success metrics
Pre-work completion rate · friction-scale engagement · retrieval-check performance · term-long self-portrait continuity · citation-verifiability (G2 pass, zero unsourced) · HIL/HAI parity.

### 13.7 Assumptions & dependencies
- Irene's **ratified** lesson plan is available as LO SSOT.
- Tracy + Texas research leg available for Ask A / Ask B.
- Existing substrate reused: `workbook_producer` (Markdown→DOCX), `glossary_projection`, `trends_projection`, `research_packet` intake idiom, `prose_revoicer` seam.

### 13.8 Risks
- Fabrication on the net-new prose surface → mitigated by the binding cite-sources rule + gates.
- Research cost/latency of two Tracy passes per lesson.
- Lesson-type detection misclassifying the scene archetype.
- Thin-source weeks → adequacy gate must degrade honestly, never invent.

---

## Appendix — party cast (for provenance of the ideas above)

🧠 Carson (brainstorming facilitator) · 🎬 Caravaggio (presentation master) · 📖 Sophia (storyteller / dual-coding) · 🎨 Maya (design-thinking / JTBD) · ✏️ Sally (UX). Session mode, operator-steered, 2026-07-12.
