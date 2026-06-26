# Charter — Refined Pre-Planning Analysis + Content-Preparation Pipeline

**Status:** RATIFIED by party-mode (Winston, Marcus, Irene, Texas) 2026-06-26 — 4/4 consensus; operator "agreed on all points."
**Builds on:** the G0-enrichment cycle (S1 LO schema ✅, S2 enrichment brick ✅, S3 Irene refinement loop ✅, all committed) and `g0-enrichment-cycle-charter-2026-06-26.md` + `lo-schema-ratification-2026-06-26.md`.
**Proven live (2026-06-26):** an LLM "Instructional Designer" pre-pass extracted **188 typed components** from ONE messy 150KB course-outline doc (56 slide / 38 narration / 34 reference_citation / 22 quiz / 11 motion_script_storyboard / 10 assignment_instructions / 7 learning_objective / 7 discussion_forum / 1 workbook), each with a document-hierarchy locator + verbatim excerpt. Intra-document component extraction WORKS.

## Governing principle (binding)
SOURCE content + LOs are KING — complete + reliably accessed **AND CLEAN**. Downstream consumers (Gary slides, narration, quiz, workbook, motion) must read a robust, universal, provenance-anchored representation — NOT the raw messy source. The pre-planning analysis types + extracts components from within source docs; the content-preparation pipeline transforms them into downstream-ready artifacts.

## The pipeline (ratified)
```
[1 component-extraction]  LLM Instructional-Designer pass: each enumerated source doc → N typed components
                          (closed 10-type enum + other:; each {component_id, parent_source, type, label,
                          locator (Part/Page/Slide path), verbatim excerpt}). Replaces S2's file-level typing.
        ↓
[2 Texas pass-0]          NORMALIZE + provenance-freeze (LOSSLESS): typed component → universal .md with
                          front-matter {component_id, type, part, locator, source_ref, verbatim_excerpt,
                          content_fingerprint(sha256), extraction_provenance, resolution_status,
                          normalization_version}. RESOLVE the 34 reference_citation + external links
                          (AMA/JAMA/PubMed/YouTube) via PubMed/scite/Consensus → resolved_ref or failed
                          (NEVER fabricated). Verbatim preserved; NO paraphrase at this layer.
        ↓
[3 Irene pass-1]          PEDAGOGICAL annotation overlay (reads Texas's clean corpus, NOT raw source):
                          {lo_refs (point at extracted LOs, never re-author), bloom, pedagogical_role
                          (definition|motivation|worked_example|synthesis|assessment|practice), sequence
                          (teaches_after, prerequisite_concepts), assessment_link, teachable flag,
                          companion}. Only on pedagogically-load-bearing types.
        ↓
[4 deterministic materializer]  PURE writer (ZERO LLM): partition by type and/or Part, assemble front-matter,
                          derive filenames, write files/folders, idempotency by (component_id,
                          source_excerpt_sha, transform_version). Same input → byte-identical output.
        ↓
[5 Marcus G0-enrichment gate]  ONE gate + materialize sub-knob (by-type / by-Part / named-subset / none).
                          Manifest = ALWAYS-complete in-graph LEDGER (every component accounted for).
                          Materialization = operator-directed PROJECTION of a subset + a coverage receipt
                          ("materialized 47 of 188; 141 retained in-graph"). Un-materialized ≠ unaccounted.
```

## Ownership (ratified — split by LAYER, not by type)
- **Component-extraction:** the SPOC-side LLM pre-pass (enhances/replaces S2 typing). Marcus-owned (custodial).
- **Texas pass-0 (provenance + citation resolution):** non-negotiably Texas. Lossless normalization; the 34 citations + external links resolved via his retrieval leg. Texas goes FIRST (freeze provenance before design touches it).
- **Irene pass-1 (pedagogy):** non-negotiably Irene. Annotation points at the extracted LOs; does NOT re-author them (refinement stays in S3/Pass-1 — no land-grab).
- **Deterministic materializer:** a pure writer module (Winston's line — no LLM in the writer).
- **Marcus-SPOC:** owns the gate, the manifest-as-ledger, the provenance RED guarantee, and DIRECTS which subset materializes (operator-confirmed).

## Binding rules
- **Provenance is RED:** every materialized block carries `{locator + verbatim-excerpt sha}` tied to the frozen manifest; absent or hash-mismatched = hard fail. Verbatim quoted in the .md with annotation AROUND it (source vs. transform side-by-side). A transform is never a silent rewrite.
- **Determinism:** Texas + Irene are LLM/retrieval (SPOC-side); the materializer/writer is pure deterministic (replay-safe).
- **Completeness vs materialization:** the manifest ledger always accounts for ALL components; materialization is an optional operator-directed projection with a coverage receipt. Un-materialized = accounted-and-retained-in-graph.
- **No fabricated citations:** Texas resolves live or marks `failed` with reason.
- **Build discipline (carried):** modular/DRY/existing-patterns; NO mocks — each completed component LIVE-tested as it lands ([[feedback_incremental_live_testing_not_deferred]]); live proof mandatory after offline close, not deferred to the very end; never cite a credential as a blocker without a proven failed attempt ([[reference_live_openai_key_dotenv_override]]).

## Universal-md schema (ratified sketch — Texas front-matter + Irene overlay)
```yaml
---
# Texas pass-0 (provenance, lossless) ↓
component_id: apc-c1m1-comp-0042
type: slide                         # closed enum (matches extraction taxonomy)
part: "Part 2"
locator: {page: 14, slide: 14, para: null}
source_ref: "course-outline-v3.docx#p14"
verbatim_excerpt: "…"               # never paraphrased at this layer
content_fingerprint: "sha256:9f3c…"
extraction_provenance: {agent: "id-llm-prepass", run: "…"}
resolution_status: resolved | unresolved | failed   # for reference_citation
resolved_ref: null                  # filled by Texas retrieval (DOI etc.)
normalization_version: tex-norm-v1
# Irene pass-1 (pedagogy, overlay) ↓
lo_refs: [LO-2]                     # POINTS at extracted LOs; never re-authors
bloom: apply
pedagogical_role: worked_example
sequence: {teaches_after: [comp-0031], prerequisite_concepts: […]}
assessment_link: comp-0077         # the quiz that tests this LO
teachable: true
transform_model: gpt-5.5
transform_version: 1
generated_at: <stamped post-run>
---
<clean normalized body, with verbatim quoted and annotation around it>
```

## Story breakdown (proposed — for create-epics-and-stories)
- **P1 — Component extraction** (redesign S2 typing leg): enumerate files (A6) → LLM segments each doc into N typed components with locator+excerpt; reconcile = every file covered by ≥1 component; decision-card shows components grouped by file/Part. *(Foundational; the proven piece.)*
- **P2 — Texas pass-0** (provenance-normalization + citation resolution): typed component → universal .md front-matter (Texas layer); resolve the reference_citation/external links (live retrieval) → resolved/failed.
- **P3 — Irene pass-1** (pedagogical annotation overlay): lo_refs/bloom/role/sequence/assessment_link on load-bearing types; reads Texas's clean corpus.
- **P4 — Deterministic materializer + Marcus gate knob**: pure writer (partition/front-matter/write/idempotency) + the one-gate materialize sub-knob + coverage receipt.
- **P5 — Downstream wiring + lesson-plan dev/execution**: Gary/narration/workbook/quiz consume the universal md; Irene Pass-1 lesson plan opens on the annotated corpus (LO→slide→quiz pre-wired).
Each: spec → dev → T11 → LIVE-segment test (incremental) → party-close. Strict-ish sequence P1 → P2 → P3 → P4 → P5 (P2/P3 partially parallel after P1).

## Honest scope note
This is a multi-story epic (~5 stories) on top of the completed S1/S2/S3. The original goal's "run E2E to Gary twice" DoD now sits AFTER this expanded pipeline lands. Build incrementally with live tests per component; the E2E-twice is the terminal confirmation once P1–P5 are in.
