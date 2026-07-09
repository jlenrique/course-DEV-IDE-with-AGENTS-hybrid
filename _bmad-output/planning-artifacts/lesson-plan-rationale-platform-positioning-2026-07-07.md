# Lesson-Plan-as-Rationale Platform — Positioning Assessment + S7 Operator-Gate Record

**Date:** 2026-07-07 (session 19, Class P — S7 workbook-spec operator review/edit/approval gate, party record §9)
**Author lens:** Marcus-SPOC orchestration + operator (juanleon)
**Status:** operator-ratified design record — feeds the S7 spec author + establishes the Phase-2 "lesson-plan-as-rationale" backlog
**Related:** `workbook-component-design-2026-06-25.md` · `canonical-production-conversation-arc-greenlight-party-record-2026-07-06.md` §9 · `workbook-completeness-research-report-2026-07-06.md` · `deferred-inventory.md §Lesson-Plan-as-Rationale Platform`

---

## 0. Why this record exists

The canonical-arc §9 gate is binding: **the operator reviews/edits/approves the workbook's purpose, contents, design-structure, and sources BEFORE S7 dev dispatch** (overrides autonomous-party consensus). This session executed that gate. Two things came out of it: (a) a ratified S7 design (the workbook = a **narrated-deck companion workbook**, one member of a **collateral** family), and (b) a grounded reading of how far today's platform is from the operator's larger vision — which set the S7 scope boundary and opened a Phase-2 backlog.

**The operator's stated vision (verbatim intent):** *"The lesson plan is the rationale for everything — it derives from the LOs + course source material + course purpose. The lesson plan directs production into (available) workflows, and it identifies collateral. Soon we'll add additional SMEs (faculty) and additional courses. So anything we do must generalize, and must ingest a variety of course content and put it — through enrichment — into fungible forms well suited to downstream work."*

---

## 1. Ratified S7 design decisions (the §9 gate output)

| # | Decision | Ruling |
|---|---|---|
| 1 | **Core scope:** retire the tejal hardcoding (`_CH2_KC`/`_CH3_KC`/`_FURTHER_READING`/objectives); the producer consumes the **real emitted `CollateralSpec`** from `lesson_plan["collateral"]` + the G0 enrichment projection; **prove it live in-graph on a non-tejal corpus** (side-door `produce_tejal_workbook.py` dead as evidence) | ✅ **Confirmed** |
| 2 | **Wire the S6 Scite research→DOI channel** into 07W (populate the References/DOI section from the live `research_entries`; `research_entries=()` retired). Empty DOI section acceptable only when a run genuinely yields zero Scite rows (recorded, not a failure) | ✅ **Confirmed** |
| 3 | **Learner-ready re-voiced prose** (real `prose_revoicer`, execute the Irene review, composed answer prose) | ⏸️ **Deferred to its own arc at S8** — S7's S2 narrative keeps the honest `REVOICE-REQUIRED` markers |
| 4 | **Gate gaps** — word-form numeral audit (G1 is symbol-only; touches the frozen-neck `figure_tokens.py`) + semantic claim↔source audit (`SEMANTIC_TRIPWIRE` stub) | ⏸️ **Deferred until AFTER the wiring is proven + a real workbook has been seen** (operator-directed) |
| 5 | **The Depth-delta narrative is the heart** (the real reason the workbook exists); S2 re-voiced narrative stays a marked placeholder until the S8 prose arc | ✅ **Confirmed** |
| 6 | **Naming/taxonomy:** the artifact is a **"narrated-deck companion workbook"**; **"collateral"** is the family umbrella (already the schema's `CollateralSpec`); **add a `kind` discriminant to the collateral artifact model now** (e.g. `kind: "deck-companion-workbook"`) so future kinds slot in without a schema migration — but build **no** family machinery in S7 | ✅ **Confirmed** |
| 7 | **Two-phase split:** S7 = workbook producer-generalization + live in-graph proof. The "lesson-plan-as-rationale that directs production" spine is **Phase 2**, its own backlog (§4 below) | ✅ **Confirmed** |

**Irene-vs-adapter — resolved.** The schema already draws the boundary: **Irene Pass-1 owns rationale/intent** (which collateral, sections↔LOs, `depth_delta`, research *intent*); **producer + adapters + enrichment own resolution/content**. Irene *already emits* the full `collateral.workbook.sections` by design (`app/specialists/irene_pass1/_act.py:274-325, 471-531`). So S7 does **not** build a parallel adapter authoring path — it **consumes Irene's real emitted `CollateralSpec` and proves it live**, which simultaneously retires the tejal constants AND closes the "workbook.sections not yet witnessed live" gap. "Adapter" survives only as the deterministic resolution layer the schema anticipates (corpus assessments → `Exercise` slots, `answer_key_source_ref` resolution) — underneath Irene, never instead of it.

---

## 2. What the workbook holds (ratified section model)

Grounded in the design doc + the real produced artifact (`_bmad-output/artifacts/workbooks/tejal-apc-c1-m1-p2-trends@1.md`).

| Section | Holds | Why | State today | S7 disposition |
|---|---|---|---|---|
| S0 Overview | title, unit binding, dual-coding statement | orients the learner | ✅ solid | generalize |
| S1 Learning Objectives | Part-2 LOs w/ Bloom verb, bound to sections | anchors every section to an objective | ✅ renders | generalize |
| S2 Transcript-narrative (re-voiced) | readable prose per segment, `REVOICE-REQUIRED` | the *read* rendering of the throughline | ⚠️ near-duplicate of S3 until prose arc | keep as marked placeholder |
| **Depth-delta narrative** | per chapter: deferred depth + develop brief | **THE HEART** — the depth the deck omits | ✅ real authored depth | generalize (from Irene `depth_delta`) |
| S3 Transcript of Record | verbatim heard narration | faithful record | ✅ solid | generalize |
| S4 Figures | slide PNGs + caption + source_ref | check visuals vs sources | ✅ solid | generalize |
| S5 Exercises | Bloom-tagged self-checks + answer-key source_ref | test grasp | ⚠️ prompts + ref only | generalize prompts; worked answers → prose arc |
| Answer Key | worked answers | self-check keys | ❌ only source_ref today | render corpus correct-answer text (plumbing); new prose → S8 arc |
| S6 Cited research / further reading | corpus refs + required reading + **S6 DOIs** | path to primary sources | ❌ not rendered today | **build (core S7)** |
| S7 Human Review footer | Irene review checkbox + halo note | honesty guard | ✅ (unchecked) | keep |

---

## 3. Platform positioning — how ready are we to generalize? (evidence-based)

Grounded scan of the ingest → G0-enrichment → Irene-Pass-1 → composition → front-door → workbook paths. **Distinguishes designed/wired from proven-on-a-non-tejal-corpus.**

| Capability | Verdict | Evidence |
|---|---|---|
| **Varied-content ingestion** | ✅ **READY (proven)** | Generic corpus-dir walk + resilient decode (`g0_enrichment_wiring.py:421-475`); ran live off-tejal on `studio-smoke-min` through G0→G1 (`evidence/s5-3b-acl-liveproof-20260707T080341Z`). No tejal keying in the ingest path. |
| **Enrichment → fungible forms** | 🟡 **PARTIAL** | `G0EnrichmentResult` (`g0_enrichment.py:369-434`) is a general, non-workbook-shaped substrate — but only ONE projector exists (`workbook_enrichment.py:296 project_enrichment_to_workbook_inputs`); no drill/job-aid/quiz projector. |
| **Lesson-plan-as-rationale** | 🟡 **PARTIAL** | Irene is corpus-agnostic and emits the full CollateralSpec schema, but plans from **corpus + references only** — no `course_purpose`, no operator-owned governing LO set as first-class inputs. |
| **Lesson-plan-directs-workflows** | 🔴 **NOT YET** | Production is chosen by a **static front-door bundle pick** (`front_door.py:136-194` + `bundle_catalog.py:209-238`), structurally disconnected from `lesson_plan["collateral"]`. **Nothing reads the collateral spec to derive the `ComponentSelection`.** The code's own docstring (`component_selection.py:5-9`) says the plan *should* select components — it doesn't. |
| **Multi-course** | 🔴 **NOT YET** | No course registry / per-course config; the `<lesson_slug>` directory name is the only course handle. |
| **Multi-SME** | 🔴 **NOT YET** | No SME/faculty entity anywhere in code; styleguide roster hardcoded to one faculty (Tejal) in `state/config/gamma-style-guides.yaml`. |

**The single biggest generalization blocker:** the lesson plan does **not** occupy the "rationale-for-everything / identifies-collateral / directs-workflows" position. Irene emits a rich `CollateralSpec` and, *separately*, the operator picks a 3-item bundle whose fixed `ComponentSelection` decides what runs. The missing **derivation edge** (`collateral → ComponentSelection`) is what stands between today and the vision. The downstream composition machinery (`composition.py`) is already a clean fail-closed typed DAG that could consume a plan-derived selection — the mechanism exists; only the derivation edge is missing.

**Bottom line:** the *front half* (ingest → enrichment → LO extraction → corpus-agnostic Pass-1) generalizes well and is proven off-tejal to G1. The *governance spine the operator describes* is largely **aspirational** today.

---

## 4. Phase-2 backlog — the "lesson-plan-as-rationale platform" program

These are **each their own arc**, sequenced after the workbook is proven end-to-end (S7 + S8). Filed in `deferred-inventory.md`.

1. **`lesson-plan-directs-production-collateral-to-selection-edge`** — the derivation edge: `lesson_plan["collateral"].declaration/workbook/research_goals` ⇒ `ComponentSelection` ⇒ composed graph. **The spine of the whole vision.** Composition machinery already exists; this is the missing edge. *Trigger: after S7/S8 prove the workbook end-to-end; operator-prioritized.*
2. **`course-and-sme-registry`** — first-class course + faculty/SME identity: per-course config, per-SME voice/styleguide/attribution/approval-routing. Retire the single-faculty (Tejal) styleguide hardcoding. **Prerequisite to "additional faculty" being real.** *Trigger: operator onboards a second course or SME.*
3. **`course-purpose-and-operator-owned-lo-inputs`** — make `course_purpose` + a ratified operator-owned LO set first-class inputs to Irene Pass-1 (today: corpus + references only). Completes the operator's "LOs + source + purpose" triad so the plan can genuinely be "the rationale for everything." *Trigger: with item 1 or when a course needs purpose-governed planning.*
4. **`collateral-projector-family`** — a projector family (drill / job-aid / quiz / summary) off the general `G0EnrichmentResult` substrate, so "fungible forms" is plural. Plugs into the `kind` discriminant added in S7. Retire the `mechanism_only_never_produced` status + tejal default of the one existing form. *Trigger: operator requests a second collateral kind.*

---

## 5. S7 scope boundary (honest)

- ✅ **S7 closes:** workbook producer generalizes (no tejal constants); consumes real Irene `CollateralSpec` + enrichment; DOI channel wired; **first non-tejal workbook ever produced**, in-graph, live-proven (also serves S8's composed proof).
- ❌ **S7 does NOT close:** the `collateral → ComponentSelection` derivation edge (workflow still chosen by the front-door bundle pick — acceptable for a proof where the operator picks the workbook bundle); course/SME registry; `course_purpose` input; the projector family. All → Phase-2 (§4).
