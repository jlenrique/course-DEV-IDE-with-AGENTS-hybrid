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

---

## 4. Open threads (not yet designed)

- **REVIEW posture** — the other half of "support," where beat-2's friction marks come home to roost. (Not yet brainstormed.)
- **Chime mechanics** — *how* does the producer make beat-3's pertinent-ability vows reliably **rhyme** with beat-1's scene, week after week, without an author hand-tuning each one? (Where the Irene / lesson-plan pipeline must actually deliver.)
- **Depth payload organization** — prose depth keyed per-slide vs. some other structure (the core "review/during" value).
- **Glossary + Trends** — formal promotion to standard sections; placement (Sally: glossary may want to be a *running margin*, not back-matter; Trends/Hot-Topics as the "sequel hook / door left ajar").
- **Concrete draft** — mock the three-beat pre-work page on the tejal leadership-bridge lesson to react to something real.

---

## Appendix — party cast (for provenance of the ideas above)

🧠 Carson (brainstorming facilitator) · 🎬 Caravaggio (presentation master) · 📖 Sophia (storyteller / dual-coding) · 🎨 Maya (design-thinking / JTBD) · ✏️ Sally (UX). Session mode, operator-steered, 2026-07-12.
