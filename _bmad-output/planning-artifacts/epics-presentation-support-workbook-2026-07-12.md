---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - _bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md
status: draft-pending-party-greenlight
prd: _bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md (§13 PRD layer)
created: 2026-07-12
---

# Presentation-Support Workbook — Epic Breakdown (Epics 36–40)

## Overview

Decomposes the presentation-support workbook redesign (design-doc §0–§13, which serves as the PRD per §13) into implementable epics and stories. The workbook is the async **preview + review** scaffold around the weekly presentation (live HAI / recorded HIL); its design-time party judgment is encoded as a **run-time producer + gates + golden exemplars** (no party per run). Requirements source: the design doc §13 PRD layer (FR1–FR17, NFR1–NFR8).

**Governance:** `lesson_plan`-layer producers are **M3-safe** (import `lesson_plan`, never `marcus.orchestrator`). Any diff touching `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` or the pipeline graph order (Epic 38) is **pipeline-lockstep** — party consensus + regime doc at T1. Per sprint governance, this doc is **draft-pending-party-greenlight**: `bmad-party-mode` green-light precedes dev; `bmad-code-review` precedes any story `done`.

## Requirements Inventory

See design-doc **§13.4 (FR1–FR17)** and **§13.5 (NFR1–NFR8)**. Not duplicated here; the FR coverage map below binds them to stories.

### FR Coverage Map

| Requirement | Epic / Story |
|---|---|
| FR1 (3-beat pre-work) | 36.1 |
| FR2 (Scene reverse-engineer + lesson-type) | 36.2 |
| FR3 (Friction Scale instrument) | 36.1 |
| FR4 (Promise = ratified LOs → abilities) | 36.3 |
| FR14 (LO SSOT = ratified plan) | 36.3 |
| FR5 (5-beat review) | 37.1 |
| FR6 (Bookend = learner friction mark) | 37.1 |
| FR7 (Deep Dive cited read-prose) | 37.2 |
| FR8 (Check-on-Learning retrieval) | 37.3 |
| FR10 (Reflection shifted-question) | 37.4 |
| FR16 (two research asks + graph order) | 38.1, 38.2, 38.3 |
| FR9 (Door-Ajar trends) | 38.2, 39.2 |
| FR11 (Glossary downstream) | 39.1 |
| FR12 (References/citations) | 37.2, 39.1 |
| FR13 (Cover) | 40.1 |
| FR15 (adequacy honesty) | 36.2, 37.2 (per-story gates) |
| FR17 (drops) | 36.4 / 37.5 (render excludes) |
| NFR1–NFR8 | every story DoD (per-story ACs) |

## Epic List

- **Epic 36 — Pre-work producer** (`prework_projection.py`): the 3-beat preview (Scene · Friction Scale · Promise), lesson-type detection, gates, Part-2 golden.
- **Epic 37 — Review + deep-dive producer** (`review_projection.py`): the 5-beat review, cited deep-dive, retrieval check, shifted-question reflection.
- **Epic 38 — Research asks & pipeline reorder** (Tracy/Texas): Ask-A enrichment pool, Ask-B hot-topics, demand-driven graph order.
- **Epic 39 — Glossary + Trends promotion & render**: glossary downstream of deep-dive (inline markers + separate section); trends as the Door-Ajar.
- **Epic 40 — Cover**: hero placeholder + art-brief, creative journey-TOC, provenance block.

**Cross-epic ordering:** 36 → 37 (review's bookend consumes pre-work's friction) → 38 (research feeds 37's deep-dive + 39) → 39 (glossary downstream of 37.2's bolded terms) → 40 (cover TOC reads the final section model). 38.1 (Ask A) must land before 37.2's cited deep-dive can enrich; 38.2 (Ask B) runs last. Any two agents touching `workbook_producer/_act.py` render or the pipeline graph serialize by rule.

---

## Epic 36: Pre-work producer

The preview on-ramp: a deterministic 3-beat frame with two leashed-LLM beats, reproducing the party's Part-2 gem per-run without a party.

### Story 36.1: Pre-work contract + deterministic frame + Friction Scale

As the runtime, I want a `PreWorkBrief` contract and the deterministic pre-work frame, so that every course renders the same stable weekly ritual with a byte-identical friction instrument.

**Acceptance Criteria:**
- **Given** the design-doc §3 three-beat frame **When** `app/marcus/lesson_plan/prework_projection.py` lands with a frozen `PreWorkBrief` (scene, friction_scale spec, promise vows, provenance) **Then** the model is Pydantic-v2 strict with a shape-pin test, and imports only `lesson_plan` (M3-safe — no `marcus.orchestrator`).
- **Given** FR3 **When** the Friction Scale is rendered **Then** it is a **deterministic template** (rate 0–10 · locate · one honest line + anchors + "keep this for review" hook) that renders byte-identical across lessons/courses (golden test), with the low anchor believable (not "0 = frictionless").
- **Given** NFR2 **When** the frame renders **Then** beat structure + honesty framing are deterministic (no model call).

### Story 36.2: Scene extraction + lesson-type detection + adequacy gate

As the runtime, I want the Scene reverse-engineered from the SME presentation, so that the preview grounds in real, pay-off-able friction — never invented.

**Acceptance Criteria:**
- **Given** FR2 + the design-doc reverse-engineering contract **When** the Scene is composed **Then** its friction **traces to slide/narration provenance** (a `source_ref`), **SME-authored scenarios are harvested first** (e.g. Part-2 Ch2 Q5), and no friction the deck cannot pay off is surfaced.
- **Given** the §4 finding **When** lesson type is detected **Then** the scene archetype is selected (fresh-pain lecture / bridge-identity capstone / skill-build) and validated against the Part-2 (fresh-pain) and Part-4 (bridge) fixtures.
- **Given** FR15 (adequacy) **When** source is thin (Part-4-class) **Then** the producer **degrades honestly or requests source**, never fabricates (adequacy gate test).

### Story 36.3: Promise transform (ratified LOs → ability vows)

As the runtime, I want the Promise to transform the ratified lesson-plan LOs into pertinent-ability vows, so that beat-③ half-rhymes with the scene without spoiling it and never renders "unresolved."

**Acceptance Criteria:**
- **Given** FR14 (LO SSOT) **When** the Promise is built **Then** it reads LOs from Irene's **ratified** lesson plan (`lesson_plan_from_run`), transforms them into pertinent-ability vows (respect-not-replace), and **eliminates the "objective statement unresolved" placeholder** on a ratified-plan fixture.
- **Given** FR4 + the spoiler-guard **When** vows render **Then** a **spoiler-guard** check confirms the Promise foreshadows the territory without handing over the answer (test over the Part-2 fixture: no beat-③ bullet restates the scene's resolution verbatim).
- **Given** §5.3 **When** the plan is **not** ratified **Then** the Promise degrades-with-record (no finality claim).

### Story 36.4: Wire pre-work into producer + Part-2 golden + gates

As the runtime, I want pre-work composed into the workbook and pinned by a golden, so that the reproduction contract is enforced and drift is caught.

**Acceptance Criteria:**
- **Given** the existing `workbook_producer/_act.py::build_workbook_inputs` **When** pre-work wires in **Then** the `PreWorkBrief` renders into the workbook front matter via the Markdown-canonical → DOCX path (no new render dependency, NFR6).
- **Given** NFR8 **When** the producer runs on the frozen tejal Part-2 deck **Then** the output matches the **Part-2 pre-work golden** (few-shot exemplar + shape-pin) and the gates pass (provenance, no-spoiler, adequacy).
- **Given** FR17 **When** the workbook renders **Then** the transcript, slide screenshots, and claim table are **absent** from the workbook body.

---

## Epic 37: Review + deep-dive producer

The review off-ramp: the 5-beat consolidation carrying all four watchwords on a learner-owned thread, with the cited deep-dive as the depth payload.

### Story 37.1: Review 5-beat frame + Bookend

As the runtime, I want the deterministic 5-beat review frame with the friction-callback bookend, so that review consolidates on the learner's own thread.

**Acceptance Criteria:**
- **Given** FR5 **When** `app/marcus/lesson_plan/review_projection.py` lands **Then** it renders the five beats (Bookend · Deep Dive · Check · Door-Ajar · Reflection) in order, M3-safe, with deterministic shells for the learner-pen beats.
- **Given** FR6 **When** the Bookend renders **Then** it surfaces the learner's own pre-work friction mark (from the `PreWorkBrief`), cashing the "keep this for review" cheque written in 36.1.
- **Given** NFR4 **When** review renders **Then** only beats 1 & 5 are learner-written; beats 2–4 are lesson-level (the producer never promises per-learner content).

### Story 37.2: Deep Dive — cited read-prose (depth payload)

As the runtime, I want the deep-dive re-voiced and expanded from the narration with inline citations, so that the read-channel carries real, sourced depth beyond the glance-deck.

**Acceptance Criteria:**
- **Given** FR7 + §7 **When** the deep dive composes **Then** it re-voices + expands the SME narration to the depth-delta (via the `prose_revoicer` seam), organized **per-ability**, as a **proper superset of the VO** (AC-8 invariant test), never contradicting the deck.
- **Given** the §7 **binding cite-sources requirement** **When** any load-bearing / enriched claim renders **Then** it carries an **inline citation** resolvable in References, and **G2 (`unsourced_citations == 0`) passes**; **uncited enrichment is rejected** (test: an unsourced enrichment sentence fails the gate).
- **Given** FR11 wiring **When** key terms render **Then** they are **bolded inline as markers** for the downstream glossary (39.1).
- **Given** NFR1 **When** numerals render **Then** numeric-fidelity (FAIL-mode) passes; the operator prose spot-check is recorded; semantic audit remains WARN-deferred.

### Story 37.3: Check on Learning (retrieval)

As the learner, I want an active-recall self-check that tests the abilities the presentation promised, so that the beat-③ promise becomes proof.

**Acceptance Criteria:**
- **Given** FR8 **When** the check renders **Then** it is **retrieval** (produce-from-memory), not a re-read, and each item tests a **beat-③ ability** (promise→proof mapping test).
- **Given** NFR1 **When** answers/keys render **Then** each answer traces to source (grounded; no fabricated key).

### Story 37.4: Closing Reflection (shifted-question transfer)

As the learner, I want a closing reflection that applies the abilities to my own friction, so that I measure capability gained, not pain relieved.

**Acceptance Criteria:**
- **Given** FR10 + Sophia's rule **When** the reflection renders **Then** it asks what the learner can now **name / see / do** about her friction (capability), and **does NOT re-rate** the 0–10 (no re-rate affordance present — test).
- **Given** the fused bookend+transfer intent **When** it renders **Then** it references the learner's beat-② friction and asks for one concrete move.

### Story 37.5: Wire review into producer + golden

As the runtime, I want review composed into the workbook and pinned by a golden, so that the whole review is reproducible.

**Acceptance Criteria:**
- **Given** the producer wiring **When** review composes **Then** the five beats render via Markdown → DOCX (NFR6), after the presentation-encounter marker.
- **Given** NFR8 **When** run on the frozen tejal Part-2 deck **Then** the output matches the **Part-2 review/deep-dive golden**; gates (G2 cite, superset-of-VO, numeric) pass.

---

## Epic 38: Research asks & pipeline reorder (Tracy + Texas)

Makes research **demand-driven by the workbook's own abilities** — two distinct asks, never smeared, with the graph reordered so the finest-grained research runs last.

### Story 38.1: Ask A — concept/narrative enrichment knowledge pool

As the runtime, I want a concept-enrichment research pass scoped to the lesson's own concepts, so that the deep-dive writer has credible sourced knowledge to expand with (and the glossary can render from the same pool).

**Acceptance Criteria:**
- **Given** §8 Ask A + §8.1 **When** Tracy+Texas run scoped to the lesson's key concepts/terms **Then** the result is a **cited, credibility-tiered knowledge pool** (upstream), consumed by the deep-dive (37.2) and available to the glossary (39.1) — one pass, shared SSOT (research_packet intake idiom).
- **Given** NFR1 **When** the pool is built **Then** rows missing provenance/`source_ref` are skipped into `known_losses` (never invented); empty-honesty on no usable rows.

### Story 38.2: Ask B — hot-topics / trends (late, scoped)

As the runtime, I want a separate hot-topics research pass scoped to the specific abilities/scene, so that the Door-Ajar is finely focused and honest, not a discipline survey.

**Acceptance Criteria:**
- **Given** §8 Ask B **When** the hot-topics pass runs **Then** it is a **separate Tracy call, run last**, scoped to the beat-③ abilities (and the scene when possible); ungrounded/injected topics are marked `unusable` (existing `reject_model_prior_topic`).
- **Given** FR9 **When** trends render **Then** they are bounded + honest (no forecasting-theater; empty-honesty when thin).

### Story 38.3: Production graph reorder (demand-driven)

As the runtime, I want the production graph reordered so research follows the abilities, so that enrichment and trends are demand-driven, not a generic upfront sweep.

**Acceptance Criteria:**
- **Given** §8 sequence **When** the graph runs **Then** order is: ratified LOs → pre-work scene/friction → deep-dive skeleton → **Ask A** → check → **Ask B (last)** → compose.
- **Given** NFR7 (lockstep) **When** the graph order / `block_mode_trigger_paths` change **Then** the change is **party-consensus + regime-doc-at-T1**, and the lockstep checker passes; Ask B is a **late narrowly-scoped Tracy pass distinct from the upfront `04.55` research wiring** (the generic upfront mint is not the source for these consumers).

---

## Epic 39: Glossary + Trends promotion & render

Promotes the two research-derived components to **standard** sections with the corrected render.

### Story 39.1: Glossary downstream of the deep-dive + inline-marker/separate-section render

As the learner, I want key terms bolded where they appear and defined in a dedicated encyclopedia section, so that I get vocabulary-for-status without back-matter I never reach.

**Acceptance Criteria:**
- **Given** §8.1 (downstream) **When** the glossary renders **Then** entries are generated for **exactly the terms the deep-dive bolded (37.2)**, **from the Ask-A pool** (no re-research; optional targeted top-up only for an uncovered bolded term).
- **Given** FR11 + §6.2 **When** the render changes **Then** terms are **bolded inline as markers** in the deep-dive and full **encyclopedia entries live in their own section** (reversing the current trailing-block-only render), with entry provenance preserved (`GLOSSARY_CAPABILITY_NOTE`, tier, citation).
- **Given** the term-highlight render open thread **When** MD → DOCX renders **Then** the inline marker links/associates to the entry (anchor or explicit convention; decided + tested).

### Story 39.2: Trends / Hot-topics as the Door-Ajar

As the learner, I want a bounded "where the field is going" callout scoped to my abilities, so that the lesson opens a forward quest.

**Acceptance Criteria:**
- **Given** FR9 + §6.1 beat-4 **When** the Door-Ajar renders **Then** it composes the **Ask-B (38.2)** trends/hot-topics as a standard review beat (existing `trends_projection` render), honest + bounded, with empty-honesty when thin.

---

## Epic 40: Cover

The workbook's front door — spec'd now, Gamma illustration left as a placeholder per operator.

### Story 40.1: Cover producer (placeholder hero + TOC + provenance)

As the learner, I want an eye-grabbing, navigable, provenanced cover, so that the workbook has a front door I trust and can navigate.

**Acceptance Criteria:**
- **Given** §12 Part 1 **When** the cover renders **Then** the hero is a **named placeholder slot + deterministic art-brief** derived from the scenario/topics (visibly a placeholder in trials; no fabricated final-art claim); a later Gamma step can swap the image with no layout change.
- **Given** §12 Part 2 **When** the TOC renders **Then** it is the creative **journey-TOC** (Before you watch → [presentation] → After you watch) with friendly labels, generated deterministically from the §10 section model.
- **Given** §12 Part 3 **When** provenance renders **Then** it shows the unit/objective binding, SME, run id, date, deck reference, the **G2 citation/fidelity stamp**, and the "how to use with the deck" dual-coding note (absorbing old S0 + S7). Deterministic from run metadata.

---

## Next gates (sprint governance)

1. **`bmad-party-mode` green-light** of this epic/story breakdown (status flips from `draft-pending-party-greenlight`).
2. **`bmad-sprint-planning`** to add Epics 36–40 to `sprint-status.yaml`.
3. Per story: fresh dev agent → **`bmad-code-review`** before `done`.
4. Acceptance = real DOCX + MD on the frozen tejal deck (Part 2 primary; Part 4 for the adequacy/lesson-type path), gates green, operator prose spot-check.
