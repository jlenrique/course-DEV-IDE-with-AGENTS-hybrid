---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - _bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md
status: greenlit-with-amendments
greenlight: party-mode 2026-07-12 (John/PM · Winston/architect · Amelia/dev · Murat/test) — 4/4 GO-WITH-AMENDMENTS; orchestrator concurs; amendments A1–A10 §Green-light amendments are BINDING pre-dev
prd: _bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md (§13 PRD layer)
created: 2026-07-12
---

# Presentation-Support Workbook — Epic Breakdown (Epics 36–40)

## Overview

Decomposes the presentation-support workbook redesign (design-doc §0–§13, which serves as the PRD per §13) into implementable epics and stories. The workbook is the async **preview + review** scaffold around the weekly presentation (live HAI / recorded HIL); its design-time party judgment is encoded as a **run-time producer + gates + golden exemplars** (no party per run). Requirements source: the design doc §13 PRD layer (FR1–FR17, NFR1–NFR8).

**Governance:** `lesson_plan`-layer producers are **M3-safe** (import `lesson_plan`, never `marcus.orchestrator`). Any diff touching `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` or the pipeline graph order (Epic 38) is **pipeline-lockstep** — party consensus + regime doc at T1. Per sprint governance, this doc is **draft-pending-party-greenlight**: `bmad-party-mode` green-light precedes dev; `bmad-code-review` precedes any story `done`.

> **⛔ Read the `## Green-light amendments` section at the bottom first — it is BINDING and GOVERNS on conflict.** The green-light party (2026-07-12) returned 4/4 GO-WITH-AMENDMENTS; amendments A1–A10 restructure the stories (notably: split 37.2 → 37.2a/37.2b; the true build order is a DAG, not the epic numbering; Epic 38 is graph-topology surgery, not a reorder). The story bodies below are the pre-amendment draft; where they conflict with the amendments, the amendments win.

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
| FR16 (two research asks + graph order) | 38.1, 38.2, 38.3 — *38.2 re-homed to the Epic-39 wave 2026-07-15 (key verbatim); FR16's Ask-B leg asserts at the 39-wave close bar (wave-3940-kickoff-party-record)* |
| FR9 (Door-Ajar trends) | 38.2, 39.2 — *travels with re-homed 38.2; asserts at the 39-wave close bar* |
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

## Green-light amendments (party-mode 2026-07-12) — BINDING, folded

**Verdict:** 4/4 **GO-WITH-AMENDMENTS** — John (PM), Winston (architect), Amelia (dev), Murat (test); orchestrator concurs. Consensus = approval to proceed once A1–A10 are folded into the story ACs (this section is the fold + the audit record). Operator may override asynchronously.

### MUST amendments (binding pre-dev)

- **A1 — Split the deep-dive; resequence; build the DAG not the numbering.** Split **Story 37.2 → 37.2a** (deep-dive *skeleton*: re-voice/expand from narration, superset-of-VO, bold terms — **no** Ask-A dependency) **+ 37.2b** (enrichment: inline-cited net-new depth from the Ask-A pool + the A2 coverage gate + reject-uncited — **depends on 38.1**). True build order is a DAG: `36 → {37.1, 37.3, 37.4, 37.2a} → 38.1 → 37.2b → 38.3 → 39.1 → 38.2 → 39.2 → 40`. **Sprint-planning ingests the DAG, not the epic numbers.** (John M1, Winston MF-4, Amelia #1)
- **A2 — Give the binding cite-sources requirement teeth (citation *coverage*, not just resolvability).** G2 (`unsourced_citations == 0`) only checks that citations *which exist* resolve — a load-bearing enriched sentence with **no** citation sails through. Define a machine-detectable **enrichment-sentence class**: any deep-dive sentence **not traceable to the VO/narration source span** MUST carry a resolvable citation → **FAIL gate** (built on the A3 superset-delta). If full coverage-detection proves infeasible, state honestly that coverage is **operator-spot-check + WARN** and stop calling it G2-enforced. (Murat M1, Amelia #2) — **37.2b**
- **A3 — Define “superset-of-VO” operationally.** Not string-containment (re-voicing transforms the text). Define as a **claim/concept-set** predicate: `VO-claim-set ⊆ deep-dive-claim-set`, with a specified extraction method + false-negative posture. This is also the substrate for A2’s enrichment-delta. (Murat M2) — **37.2a**
- **A4 — Name the leashed-LLM execution seam + injectable writer contracts.** The terminal producer is pinned **model-free** (mirrors `default_glossary_writer`). Decision: an **in-graph node emits the `PreWorkBrief` / review brief; the terminal producer stays deterministic-consume** (preserving the `_act.py` no-model-client pin). Add named injectable writer contracts, each with a **deterministic stub** (mirror `GlossaryWriter`): `SceneComposer`, `PromiseTransformer`, `DeepDiveWriter`, `CheckWriter`, `ReflectionWriter` — so goldens run offline (NFR3). (Winston MF-1, Amelia #3) — **36.1 / 37.1 ACs**
- **A5 — Epic 38 is graph-topology + intake-contract surgery, not a reorder.** (i) **Hoist** deep-dive-skeleton production **out of the terminal leaf into an upstream node** that emits the ability-scoped research demand; (ii) **two asks = two named packets, each with its own witnessed digest** — specify the relation to the single-`packet_digest` guarantee and **re-point 39.1 → Ask-A digest, 39.2 → Ask-B digest**; (iii) **segregate 38.3 as an explicitly orchestrator-layer story** (NOT the `lesson_plan` M3-safe blanket), with its own reviewer discipline + lockstep surface. **Epic 38 gets its own party round on the graph shape before any code.** (Winston MF-2/MF-3/MF-5)
- **A6 — Mode parity (HIL/HAI) needs a story.** Add an explicit **`mode` input + a parity AC** (new **Story 37.6** or folded into 36.4/37.5): render both HIL (recorded) and HAI (live); assert the **mechanism is identical and only the encounter-label copy differs**. (John M2)
- **A7 — Bookend / self-portrait vs the per-learner non-goal.** The producer emits the **callback prompt/template** referencing the learner’s own beat-② mark — **NOT the value** (per-learner content is a non-goal). **FR3 trimmed** to the single-week instrument + a “keep-this” instruction; the **term-long self-portrait aggregation is deferred** (filed in design-doc §13.2 non-goals). (John M3/M4) — **FR3/FR6, 36.1, 37.1**
- **A8 — References section owner.** Assign **37.5** to **assemble + dedupe + render** the consolidated References / Further-Reading section (FR12, §10 §10) that inline citations resolve into. (John M5)
- **A9 — Golden semantics + fixture creation + gate taxonomy.** (i) Golden ACs: **byte-identical** on deterministic beats; **structural shape-pin + gate-assertions** on leashed-LLM beats (explicitly **not** byte-match). (ii) Declare **fixture-creation work**: capture the Part-2 gem into structured fixtures; **ADD a Part-4 adequacy golden + a skill-build fixture + a boundary/ambiguous classifier case**. (iii) Add a **gate-taxonomy table** to each producer’s DoD: *gate → FAIL | WARN → witness (automated | operator spot-check)*. (Amelia #4/#5, Murat M3/M4)
- **A10 — Make the semantic ACs testable.** 36.2 “no friction the deck cannot pay off” → **testable proxy** (friction `source_ref` resolves to a slide in the promise/payoff set) **+ operator spot-check**; provenance binds the **seed**, so add a **light faithfulness check** that the composed Scene doesn’t drift from its cited seed. (Amelia #6, Murat S4)

### SHOULD amendments (non-blocking, recorded)
Split the lesson-type detector out of 36.2 (Amelia, Murat M3) · relabel the spoiler-guard as weak-heuristic-WARN + operator spot-check (Murat S1, Amelia) · confirm word-form-numeral coverage in numeric fidelity + add a word-form witness to the Part-2 fixture (Murat S3) · concrete per-learner negative linguistic test on beats 2–4 (Murat S2) · name the lesson-plan **ratification-status** field/seam (Winston SF-1) · one shared adequacy/empty-honesty helper across 36.2/37.2 (Winston SF-4, Amelia) · pull the term-highlight MD→DOCX decision into 39.1 T1 with a plain-bold fallback (Winston SF-3, Amelia).

### Next
Epic 38 requires a **dedicated graph-shape party round** before its code (A5). Otherwise, with A1–A10 folded, the plan is green-lit for `bmad-sprint-planning` → per-story fresh dev → `bmad-code-review` before `done`.

---

## Epic 38 graph-shape decision (party-mode 2026-07-12) — RATIFIED

**Round:** Winston (architect, decision owner) + Amelia (dev — **BUILDABLE-WITH-CHANGES**); orchestrator concurs. Satisfies amendment A5's "dedicated graph-shape round before Epic-38 code."

**Key finding (Amelia):** A5's "hoist deep-dive-skeleton *out of* the terminal leaf" is a misnomer — the deep-dive prose is **not produced anywhere today** (`_act.py` is a model-free terminal leaf that only consumes `run.json`). The work is purely **additive**; the model-free pin survives by construction.

### Node topology — a terminal "workbook band"

```
… → 15 (operator handoff; narration + segment manifest on disk)
   → 07W.1  Pre-work + Deep-Dive SKELETON     [LEASHED · model_config]  SceneComposer·PromiseTransformer·DeepDiveWriter(skeleton) → emits briefs + bolded term set
   → 07W.2  Ask A — ability-scoped enrichment  [ORCHESTRATOR wiring · model-free]  Tracy+Texas scoped to 07W.1 terms → Ask-A packet
   → 07W.3  Enrichment + Check + Reflection     [LEASHED · model_config]  DeepDiveWriter(enrich+cite+A2)·CheckWriter·ReflectionWriter
   → 07W.4  Ask B — hot-topics (LAST)           [ORCHESTRATOR wiring · model-free]  separate late Tracy call → Ask-B packet
   → 07W    Terminal render leaf — UNCHANGED     [DETERMINISTIC-CONSUME · model-free pin intact]  composes briefs + Ask-A(glossary) + Ask-B(Door-Ajar) → MD+DOCX
```

- **A4 resolved:** leashed LLM executes **only** in `07W.1` + `07W.3` (in-graph nodes carrying `model_config_ref`). `07W`'s no-model-client invariant is load-bearing and stays untouched. Execution mirrors the `research_wiring` precedent: runner hooks keyed by node id, **mirrored in both walk bodies** with a continuation-walk parity test (the band is reached only on the continuation walk, like `04.55`).

### Three packets · three digests · one witness rule each

| Packet | Node | specialist_id | Consumers |
|---|---|---|---|
| Generic research (**unchanged**) | `04.55` | `research_wiring` | irene_intake, spoc_receipt, future_collateral |
| **Ask-A enrichment pool** (new) | `07W.2` | `ask_a_enrichment` | deep-dive enrich (37.2b) + glossary (39.1) |
| **Ask-B hot-topics** (new) | `07W.4` | `ask_b_hot_topics` | Door-Ajar / trends (39.2) |

- `research_packet.load_research_packet` is **parameterized by `(specialist_id, node_id)`**; today's `04.55`/`research_wiring` becomes the default (existing consumers untouched). Two digests come **for free** per-load. Add `resolve_for_enrichment_pool` (Ask-A) + `resolve_for_hot_topics` (Ask-B). **39.1 re-points** glossary → Ask-A; **39.2 re-points** trends → Ask-B; **37.2b** reads Ask-A.
- The "single-digest" guarantee narrows correctly to **one digest per packet, witnessed identically by every consumer of that packet** — shape-pin tests assert each consumer witnesses its *intended* digest (A/B/C).

### Layer boundary (M3 held)

- **lesson_plan (model-free):** `research_packet` generalization + two resolvers; `glossary`/`trends` re-point; pre-work / `review_projection` brief-shapers; the injectable **writer contracts + deterministic stubs** (`SceneComposer`, `PromiseTransformer`, `DeepDiveWriter`, `CheckWriter`, `ReflectionWriter`) — drive offline goldens (NFR3).
- **orchestrator (not the M3 blanket):** the manifest node band, runner hooks, Tracy+Texas dispatch, and the **live** writer *instantiation* in `07W.1`/`07W.3`. Packets cross the M3 wall **disk-mediated** (same seam as `04.55`).

### Lockstep surface

Tier-2 (new pipeline steps). `pipeline-manifest.yaml` (4 node adds + `07W` re-point) and `production_runner.py` are already trigger paths; **ADD** the new orchestrator wiring module (e.g. `app/marcus/orchestrator/workbook_wiring.py`) and **`app/marcus/lesson_plan/research_packet.py`** (intake contract now load-bearing across 3 consumers) to `block_mode_trigger_paths`. **Pack tier = v4.2-lineage refinement** (terminal-sidecar `sub_phase_of` nodes feeding nothing downstream) — **not** a v4.3 family bump; hold **new learning-event types to zero** this pass. Confirm at T1 with the regime doc.

### Story reshape (folds into A1's DAG)

- **38.0 (NEW) — Two-packet intake contract** (lesson_plan, M3-safe): generalize `research_packet.py`; add both resolvers, each with its own witnessed digest; `04.55` untouched. **Lands first.**
- **38.3 split (Amelia):** **38.3a** (lesson_plan consume side: readers + AC-pinned **cross-layer string-contract test**, fixture-`run.json`-tested, zero orchestrator diff) + **38.3b** (orchestrator: the 4-node band + `07W` re-point + runner hooks + two-walk parity + live writer instantiation + `block_mode` adds + regime doc at T1). Build 38.3b **with deterministic stubs first** (prove topology offline).
- **38.1 / 38.2:** fill nodes `07W.2` / `07W.4` (Ask-A / Ask-B Tracy+Texas wiring).
- **Ownership boundary (resolves the 37.2a-vs-38 ambiguity):** **37.2a authors** the `DeepDiveWriter(skeleton)` contract+stub (lesson_plan); **38.3b instantiates/positions** it in node `07W.1`. Skeleton *creation* = Epic 37; node *positioning* = Epic 38. No `_act.py`/graph collision.

**Runtime node order:** `15 → 07W.1 → 07W.2(A) → 07W.3 → 07W.4(B) → 07W`.
**Build order (extends A1's DAG):** `38.0 → 38.3b(band w/ stubs) → {36, 37.1, 37.2a, 37.3, 37.4 writers} → 38.3a → 38.1 → 37.2b → 39.1 → 38.2 → 39.2 → 40`.

### Residual risks (flagged, non-blocking)
Two new live LLM calls in the workbook path (cost/latency; stubs keep goldens offline) · leashed-on-leashed scoping (weak skeleton mis-aims Ask-A — spot-check witness) · three-packet mis-resolution (digest shape-pins guard) · two-walk parity (both walk bodies + parity test) · pack-tier stays in-lineage only if zero new learning events / no operator-surface touch (confirm T1).

---

## Next gates (sprint governance)

1. **`bmad-party-mode` green-light** of this epic/story breakdown (status flips from `draft-pending-party-greenlight`).
2. **`bmad-sprint-planning`** to add Epics 36–40 to `sprint-status.yaml`.
3. Per story: fresh dev agent → **`bmad-code-review`** before `done`.
4. Acceptance = real DOCX + MD on the frozen tejal deck (Part 2 primary; Part 4 for the adequacy/lesson-type path), gates green, operator prose spot-check.
