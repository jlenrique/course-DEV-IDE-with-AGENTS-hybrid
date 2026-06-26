# Design Spec — Companion Workbook Component (grounded in the tejal lesson)

**Status:** design spike (NOT a build story) — feeds a later NEW CYCLE build story
**Date:** 2026-06-25
**Author lens:** Irene + instructional-design
**Prerequisite ruling:** John (PM) party-mode ruling — before the workbook can be an honestly-recommendable bundle component (B3 = deck + motion + workbook), we must design what the workbook *is*, grounded in a real lesson, not generically.
**Grounding lesson:** `course-content/courses/tejal-apc-c1-m1-p2-trends/` — APC C1M1 **Part 2: The Macro Trends & The Case for Change** (Chapters 2 & 3). Audience: practicing physicians training to become clinical innovators / intrapreneurs.
**Frozen deck (read-only inputs):** `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/` (run `C1-M1-PRES-20260419B`; `segment-manifest.yaml` schema 1.1, **14 clustered motion segments** derived from the 6 source slides).
**Substrate this design targets:** `app/marcus/lesson_plan/workbook_producer.py` (`WorkbookProducer`, braid S2) + `app/marcus/lesson_plan/collateral_spec.py` (`CollateralSpec`/`WorkbookSpec`, braid S1) + the Irene→Tracy→Texas research leg (braid S3) + the L2 audit `app/specialists/_shared/source_fidelity_audit.py`.

---

## 1. Purpose + the dual-coding contract

### 1.1 Purpose

The workbook is the **read-in-depth companion** to the perception-tuned glance-deck. The deck + tight VO and the workbook are **dual-coding partners**: the deck carries the *glance* channel (perception-tuned slides, tight ≤~33s-per-card narration); the workbook carries the *read* channel (the depth deliberately kept OFF the slides and out of heard-only narration). The VO can stay tight *because* the workbook carries the depth. The workbook is the durable artifact a physician-learner keeps, re-reads, works through, and follows to primary sources.

For the tejal lesson specifically, the workbook must let a busy clinician who watched the 14-card motion deck (a) re-read the argument as self-contained prose, (b) check the load-bearing figures against their real sources (CMS, JAMA, Academic Medicine, etc.), (c) test their own grasp via the Chapter 2/3 knowledge checks, and (d) follow the required reading (Beauchamp) and intro video into deeper study.

### 1.2 The boundary rule (what goes where)

| Channel | Carries | Tejal example | Must NOT carry |
|---|---|---|---|
| **Glance-deck (slide)** | The single perception-tuned claim per card + one figure; numerals shown where the eye lands | Slide 1 dual-axis chart: "$5.2T", "Independent ↓ / Employed ↑" | Paragraph prose; full citation; multi-step reasoning |
| **Heard narration (VO)** | The tight spoken throughline that animates the slide; deixis-laden ("watch the physician", "as this chart shows") | Card-01 identity reframe over the motion clip | Anything that needs re-reading; bibliographic detail; exercises |
| **Workbook (read)** | Self-contained re-voiced prose; the *deferred depth* (the "why it matters", mechanism, caveats); transcript of record; exercises + answer keys; full citations + further reading | The mechanism of *why* administrative waste drives burnout (system-design framing), the primary-source basis of "25%", the Ch2/Ch3 self-checks | Perception chrome; motion; anything that contradicts the deck |

**Binding boundary invariant (already enforced in code as AC-8):** the workbook narrative body must be a **proper superset** of the VO script — strictly more content than the heard narration (`workbook_narrative ⊋ VO_script`), and not a disjoint rewrite (the VO content must be represented). The **depth-delta** (`DepthDeltaContract.deferred_depth`) is the load-bearing field that names, per section, exactly what depth moved off the slide INTO the workbook. That field *legitimizes* the tight VO; an empty depth-delta is a contract violation, not a soft warning.

---

## 2. Section model for THIS tejal lesson

Ordered sections for the tejal Part-2 workbook. For each: content, upstream source artifact, and fidelity rule. **(v1)** / **(deferred)** tags map to §6.

The lesson decomposes into two pedagogical chapters that the workbook should mirror:
- **Chapter 2 — The Macro Trends** (slides 1–2 + part of 3): economic/structural reality, the human cost (waste + burnout). Serves **LO2** (Analyze macro-economic/structural trends).
- **Chapter 3 — The Case for Change** (slides 3–5): knowledge explosion + new tech, consumer shift / digital front door, the leadership gap. Serves **LO3/LO4** (idea-vs-opportunity, root-cause of systemic failure) — both `deferred_to_part2` per Irene Pass-1.
- **Part-2 Summary** (slide 6): the synthesis + call to lead.

### S0. Title + Overview (front matter) — **(v1)**
- **Contains:** lesson title, the unit/objective binding, a one-paragraph "how to use this workbook with the deck" note, and the dual-coding statement (this is the read-companion).
- **Source:** `plan_unit` + `ProductionContext.lesson_plan_revision` (producer already emits an `Overview` block).
- **Fidelity rule:** no claims; structural only. No fidelity gate beyond id-binding.

### S1. Learning Objectives — **(v1, NEW vs producer)**
- **Contains:** the Part-2 learning objectives the workbook serves, each with its Bloom verb. For tejal: **LO2 (Analyze)** macro trends; **LO3/LO4** (idea-vs-opportunity, root-cause) introduced. Each objective links to the sections that serve it.
- **Source:** `irene-pass1.md` LO block (LO1–LO5; LO2/LO3/LO4 are the Part-2-relevant ones) → surfaced via `WorkbookSection.learning_objective_id` bindings. **GAP:** the producer binds `learning_objective_id` per section but does not render a front "Learning Objectives" section (see §7).
- **Fidelity rule:** every objective listed must be bound by ≥1 section's `learning_objective_id`; no orphan objective, no phantom objective.

### S2. Narrative / explainer — per chapter, the deferred depth — **(v1, core)**
- **Contains:** the fuller, self-contained read-prose per chapter — the depth deliberately kept off the glance-slides. E.g. for Ch2: the *system-design* reframe of burnout (burnout is a system-design problem, not a resilience failure; the workarounds clinicians invent are the innovation surface) — the deck only glances this; the workbook argues it. For Ch3: the mechanism of "static training can't keep up" (50yr→73-day doubling) and what *safe AI oversight* actually requires.
- **Source:** `WorkbookSection.narrative_intent` + `DepthDeltaContract.deferred_depth` (the brief), re-voiced from the Pass-2 `narration_text` via the `prose_revoicer` seam. In v1 the deterministic default embeds verbatim narration + a `REVOICE-REQUIRED` marker (writer Paige/Sophia → self-contained read-prose; Irene validates).
- **Fidelity rule:** body-assertion fidelity (§5): numerals must trace to source (L2 FAIL-mode); prose claims spot-checked by operator. The re-voiced prose must not introduce claims absent from the deck/source.

### S3. Transcript (of record) — **(v1)**
- **Contains:** the full Pass-2 transcript, segment by segment, anchored by `segment_id`, covering all 14 cards. This is the verbatim heard-narration of record — distinct from S2 (S2 is re-voiced read-prose; S3 is the literal transcript).
- **Source:** `segment-manifest.yaml::segments[].narration_text` via `load_transcript_segments` (producer already emits `Transcript-narrative`).
- **Fidelity rule:** 100% segment coverage, zero phantom (AC-5, already enforced). Verbatim — no drift from the manifest text.

> **Note on S2 vs S3 overlap:** today the producer fuses these into one `Transcript-narrative` block (verbatim + revoice marker) plus a `Depth-delta narrative` block. The design separates the **literal transcript** (S3) from the **re-voiced explainer** (S2) as distinct sections so the reader gets both a clean read and a faithful record. This is a producer composition change, not new substrate (see §7).

### S4. Key figures — slide visuals with captions — **(v1)**
- **Contains:** the embedded slide figures (charts/infographics) with caption + `source_ref`. For tejal: the Slide-1 dual-axis NHE/employment chart, the Slide-2 waste/burnout infographic, the Slide-5 leadership-gap bar chart, etc.
- **Source:** `segment-manifest.yaml::segments[].visual_file` + `visual_references[]` → `gamma-export/*.png` in the bundle (producer already emits `Figures` via `add_picture`).
- **Fidelity rule:** caption + `source_ref` required per figure; figure file resolved against the bundle dir (missing file → caption-only, no fabricated image). Numerals visible in a figure count as on-slide presence (figure-grounding bar).

### S4b. Key-figures claim table — **(deferred to v-next)**
- A tabular digest of the load-bearing numeric claims with their sources (e.g. "$5.2T NHE — CMS NHE Fact Sheet"; "25% admin waste — Shrank et al., JAMA 2019"; "73-day doubling — Densen 2011"; "67% want leadership / 18% trained — Jackson 2023"). Deferred because it duplicates S2+S6 and needs the word-form-numeral gap closed first (§5).

### S5. Exercises / self-check — **(v1, see §3)**
- **Contains:** the worked exercises + self-check questions. For tejal these are **the real Chapter 2 and Chapter 3 Knowledge Checks** (5 questions each, already Bloom-tagged in the corpus) plus optional apply-level transfer prompts.
- **Source:** `WorkbookSpec.sections[].exercises[]` (Bloom level + `answer_key_source_ref`). The corpus already carries the question + correct-answer text at `assessments/chapter-{2,3}-knowledge-check.md` — these are the grounding for the exercise prompts/keys. **GAP:** no bridge ingests the corpus assessments into `Exercise` specs today; exercises come only from the hand-authored `WorkbookSpec` (see §7).
- **Fidelity rule:** G3 — every exercise carries a Bloom level + a present, resolvable `answer_key_source_ref`. Answer-key prose must trace to source (the corpus KC answers are themselves source-grounded).

### S6. Cited research / further reading — **(v1 thin → v-next rich)**
- **Contains:** (a) the per-slide academic references already in the corpus (CMS NHE Fact Sheet; AMA Practice Ownership; **Shrank et al., JAMA 2019**; Medscape Burnout 2024; **Densen 2011**; **Isaranuwatchai et al., JMIR 2018**; AMA AI Report; **Jackson Physician Search 2023**; **Rotenstein et al., Academic Medicine 2021**); (b) the required reading (**Beauchamp, "Healthcare's Trillion-Dollar Problem"**, Medium) + intro video (YouTube); (c) the live-research cited entries with **real DOIs** from the Texas/Scite leg (braid S3 `research_entries`).
- **Source:** corpus slide `**References:**` lines + `references/*.md` + S3 `research_entries` (each a `{citation_id, source_ref, provider, source_id, title, source_hash}` from an accepted `TexasRow`).
- **Fidelity rule:** G2 — every citation resolves to a real `source_ref` in this run's retrieval set (`unsourced_citations == 0`); no invented refs/DOIs. **GAP:** the producer *audits* citations but does not *render* a citations/further-reading section into the doc body (see §7).

### S7. Human Review Checkpoint (footer) — **(v1)**
- **Contains:** the Irene review marker + the no-reading-path-halo note.
- **Source:** producer constants (already emitted).
- **Fidelity rule:** the honesty footer; not learner-facing content.

---

## 3. Exercises design

- **Kinds (v1):** the two corpus Knowledge Checks — **recall** (Ch2 Q1 structural shift; Ch3 Q1 doubling time), **understand** (Ch2 Q2 25% waste), **analyze** (Ch2 Q3 burnout driver; Ch3 Q4 leadership-gap consequence), **apply** (Ch2 Q5 transport-delay dilemma; Ch3 Q3 digital front door), **evaluate** (Ch2 Q4 supply/demand; Ch3 Q5 Beauchamp care-failure category). These map cleanly onto the closed `BloomLevel` enum (`remember/understand/apply/analyze/evaluate/create`).
- **How many (v1):** the 10 corpus KC questions, partitioned Ch2 (5) / Ch3 (5). v1 minimal cut may ship a **representative subset (≥3, spanning ≥3 Bloom levels)** to prove the component, with the full 10 as the v1-complete target.
- **How generated/grounded:** authored **backward from sourced content + objectives** (G3). The prompt + correct answer already exist in the corpus assessments and are source-grounded (each KC answer traces to a slide claim, which traces to a slide reference). The `Exercise.prompt_intent` is the pedagogical intent; the producer composes the worked prompt prose; `answer_key_source_ref` pins the answer to a real source. **No fabricated questions** in v1 — use the corpus KCs.
- **Answers / keys:** each exercise carries `bloom_level` + `answer_key_source_ref` (asserted present, G3). The **worked answer prose** is the producer's job (composed under G1 fidelity); the key cites its `source_ref`. v1 renders an answer key section (or inline answers) derived from the corpus "Correct Answer" lines.
- **Deferred:** fill-in affordances (blank answer lines, response boxes, DOCX form fields) — `braid-workbook-worksheet-fillin-affordances`. Auto-*generated* novel exercises beyond the corpus KCs — deferred (v1 grounds in existing assessments to avoid net-new fabrication risk).

---

## 4. Citations / research

- **Two citation tiers land in S6:**
  1. **Corpus-native references** — already present per slide and in `references/` (CMS, JAMA, Academic Medicine, Beauchamp, the intro video). These are deck-traceable and ship in v1.
  2. **Live-research cited entries** — from the braid S3 Irene→Tracy→Texas→Scite/Consensus leg: each accepted `TexasRow` mints `{citation_id, source_ref, provider, source_id, title, source_hash}` with a **real DOI** (link constructed as `https://doi.org/{doi}`). These enrich the load-bearing claims (e.g. a primary-source citation behind the "25% administrative waste" or "73-day doubling" figures).
- **How injected + linked:** S3 makes accepted entries available on the run record under `research_entries`; the producer consumes them as `research_supplements` (the L2 citation-acceptance channel) AND renders them into the S6 citations/further-reading section. Each entry is **linked to lesson content** by binding to a `segment_id`/`source_ref` (the claim it supports) or to a `ResearchEnrichmentGoal.binds_to_objective_id`. Markdown is the canonical injection substrate (S3 fills the MD; DOCX renders from the same model — citations flow to DOCX automatically).
- **Fidelity (G2):** `audit_citation_fidelity` asserts `unsourced_citations == 0` — every rendered citation resolves to a real `source_ref` in this run's retrieval set; the citation→`source_ref`→source-hash manifest rides on the sidecar. **No invented citations or DOIs.**
- **GAP:** today `audit_citation_fidelity` runs but `compose_workbook` does **not** emit a rendered citations/further-reading block from `research_entries` — the `References` block only lists `segment_id -> source_ref`. The build story must render S6 from the corpus references + S3 entries (see §7).

---

## 5. Fidelity / honesty gates for a net-new prose-fabrication surface

The workbook is a **net-new prose-fabrication surface** (re-voiced narrative + exercise prose + composed answer keys) — higher fabrication risk than the deck. Gates, stated honestly:

- **G1 — Body-assertion fidelity (numeric, FAIL-mode):** `audit_workbook_numeric_fidelity` runs the frozen-neck L2 audit over the workbook body in **FAIL-mode** (`unsourced_numeric == 0`); a numeral that cannot be cleared against the source set fails the workbook boundary. Already wired in `workbook_producer.py`.
  - ⚠️ **Named limitation — word-form numerals are NOT gated.** The L2 tokenizer (`_FIGURE_RE`) is **symbol-only** (`25%`, `$5.2T` caught). **This lesson is heavy with word-form numerals** — "nearly **one-fifth**", "**over half** of physicians", "doubling every **fifty** years", "**two-thirds**". Those pass un-audited. This is material for tejal specifically. Filed: `braid-workbook-wordform-numeral-gap`. Do not over-claim coverage.
- **G1 — Body-assertion fidelity (prose, named operator spot-check):** the operator reads N prose claims and confirms each is deck-traceable or `source_ref`-traceable; recorded in Completion Notes. This is the human gate over the re-voiced narrative + answer-key prose.
- **G2 — Citation fidelity:** `unsourced_citations == 0`; manifest attached (§4).
- **G3 — Exercise/answer-key fidelity:** Bloom level present + `answer_key_source_ref` resolvable, per exercise.
- **G4 — No reading-path halo:** the workbook advances no fresh-naive-holdout / reading-path generalization claim (footer note already emitted).
- **G6 — Believed-green discipline:** acceptance = the real DOCX+MD artifact on the frozen tejal deck, not a green unit suite. Live deps, first-run-stands.

**NET-NEW / DEFERRED (flag explicitly):** the **general semantic claim audit** — a non-numeric "does this prose sentence actually follow from a cited source" check — is **net-new and deferred** (`braid-workbook-l2-semantic-claim-citation-audit`; L2 semantic leg is a stub, `SEMANTIC_TRIPWIRE=None`, untuned until ≥3 tracked runs). v1 covers numerals (symbol-only, FAIL-mode) + the named operator prose spot-check. **Do not claim L2 covers semantic faithfulness.**

---

## 6. Minimal v1 cut (the smallest real tejal workbook that proves the component)

**v1 = a real DOCX+MD produced on the frozen tejal deck containing:**

| Section | v1? | Why |
|---|---|---|
| S0 Title + Overview | ✅ v1 | Already emitted; trivial |
| S1 Learning Objectives | ✅ v1 | Small NEW render; surfaces LO2/LO3/LO4 from the bindings — cheap, high pedagogical value |
| S2 Narrative/explainer (deferred depth) | ✅ v1 | Core dual-coding payload; deterministic revoice default + REVOICE markers (live writer deferred) |
| S3 Transcript of record | ✅ v1 | Already emitted (segment coverage) |
| S4 Key figures (slide visuals) | ✅ v1 | Already emitted (`add_picture`) |
| S5 Exercises / self-check | ✅ v1 | Ship the corpus Ch2/Ch3 KCs (≥3 spanning ≥3 Bloom levels minimum; 10 full as target) |
| S6 Cited research / further reading | ✅ v1 (thin) | Render corpus references + Beauchamp/video now; S3 DOI'd entries when the research leg is live |
| S7 Human Review footer | ✅ v1 | Already emitted |
| S4b Key-figures claim table | ⛔ v-next | Duplicative; blocked on word-form-numeral gap |
| Worksheet fill-in affordances | ⛔ v-next | `braid-workbook-worksheet-fillin-affordances` |
| Live prose-delegation (Paige/Sophia writer) | ⛔ v-next | Seam ships v1; live writer couples to Marcus finale |
| PDF render leg | ⛔ v-next | New dependency governance (`braid-workbook-pdf-render-leg`) |
| General semantic claim audit | ⛔ v-next | `braid-workbook-l2-semantic-claim-citation-audit` |

**v1 acceptance witness:** one DOCX + one canonical MD under `_bmad-output/artifacts/workbooks/` for the frozen `tejal-apc-c1-m1-p2-trends` deck (DP6 frozen reuse, empty-intersection stamp), passing G1/G2/G3, with all 14 segments covered, ≥1 figure embedded, ≥3 Bloom-spanning exercises, and a rendered citations section — reviewed by the operator prose spot-check.

---

## 7. Gaps vs the existing `workbook_producer.py`

What the producer **already supports** (do not rebuild): registry-widened `workbook` modality; Markdown-canonical → DOCX-deliverable single-source render; output-root containment; Overview / Transcript-narrative / Depth-delta / Figures / Exercises / References blocks; figure embed (`add_picture`) with caption + `source_ref`; `prose_revoicer` seam + `REVOICE-REQUIRED` markers; 100% segment coverage + phantom rejection (AC-5); AC-8 superset gate; G1 numeric FAIL-mode; G2 citation-audit path; G3 exercise fidelity; DP6 reuse stamp; sidecar with audits.

**Gaps the design needs added (for the build story):**

1. **Render a first-class "Learning Objectives" section (S1).** The producer binds `learning_objective_id` per section but never surfaces an objectives block. Add: render objectives (with Bloom verbs) from the section bindings; assert no orphan/phantom objective. *Small composition change.*
2. **Separate transcript-of-record (S3) from re-voiced explainer (S2).** Today both live in one `Transcript-narrative` block + a `Depth-delta narrative` block. Design wants a clean literal transcript section AND a distinct narrative/explainer section. *Composition change; no new substrate.*
3. **Ingest corpus assessments into `Exercise` specs.** No bridge today turns `assessments/chapter-{2,3}-knowledge-check.md` (real Bloom-tagged Q+A) into `WorkbookSpec.sections[].exercises[]`. Either Irene Pass-1 (S1) emits them, or a small adapter maps the KC markdown → `Exercise(prompt_intent, bloom_level, answer_key_source_ref)`. *New thin adapter (S1-side or producer-side).*
4. **Render an answer key.** `Exercise` carries `answer_key_source_ref` but the producer emits no worked-answer prose / answer key block. Add an answer-key render (from corpus "Correct Answer" lines) under G1/G3. *Composition change.*
5. **Render the citations / further-reading section (S6) from `research_entries` + corpus references.** Today `audit_citation_fidelity` validates citations but `compose_workbook` emits only `segment_id -> source_ref` lines — it does not render a real bibliography. Add: render (a) corpus per-slide references, (b) `references/*.md` (Beauchamp, video), (c) S3 DOI'd `research_entries` with `https://doi.org/{doi}` links, each linked to the claim/segment it supports. *Composition + a thin S2↔S3 `research_entries` handoff contract.*
6. **Close (or keep named) the word-form-numeral gap.** Material for tejal (one-fifth, over half, fifty years). v1 keeps it named/deferred (`braid-workbook-wordform-numeral-gap`); the build story must NOT claim full numeric coverage.
7. **`WorkbookSpec` content authoring for tejal.** The producer consumes a `WorkbookSpec`; no tejal-specific spec instance exists yet. The build story (or its S1 sibling) must author the real tejal `CollateralSpec` — sections bound to LO2/LO3/LO4, depth-deltas naming the deferred depth per chapter, the 10 KC exercises, and the research-enrichment goals (e.g. "learner needs the primary-source basis for the 25% administrative-waste figure"). *This is the real content-design deliverable that turns the producer from a mechanism into a real workbook.*

**Build-story shape:** mostly **composition + thin adapters on proven substrate** (gaps 1, 2, 4, 5) + one real content-authoring artifact (gap 7) + a deferred-named limitation (gap 6) + a small assessment-ingest adapter (gap 3). No new render dependency; DOCX/MD path is reused. Frozen tejal deck, DP6 reuse.
