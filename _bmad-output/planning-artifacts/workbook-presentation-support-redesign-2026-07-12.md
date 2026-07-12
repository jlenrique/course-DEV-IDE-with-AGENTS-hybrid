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

## 6. Open threads (not yet designed)

- **REVIEW posture** — the other half of "support," where beat-②'s friction marks come home to roost (self-close the loop; aggregate into the term-long self-portrait). **Next up.**
- **Depth payload organization** — prose depth keyed per-slide vs. some other structure (the core "during/review" value; slides are glance-only by design).
- **Glossary + Trends** — formal promotion to standard sections; placement (Sally: glossary may want to be a *running margin*, not back-matter; Trends/Hot-Topics as the "sequel hook / door left ajar").

**Resolved since v1 of this doc:** concrete pre-work draft (Part 2 + Part 4, §3 / §5) · reproduction architecture + `pre_work_producer` spec (§5) · lesson-type-detection finding (§4 test) · LO SSOT = ratified lesson plan (§5.3).

---

## Appendix — party cast (for provenance of the ideas above)

🧠 Carson (brainstorming facilitator) · 🎬 Caravaggio (presentation master) · 📖 Sophia (storyteller / dual-coding) · 🎨 Maya (design-thinking / JTBD) · ✏️ Sally (UX). Session mode, operator-steered, 2026-07-12.
