# S7 Phase 2 — Course Source Management, Ingestion & Lesson-Planning Inputs (Stories A/B/C/D)

**Date:** 2026-07-08 (session 20)
**Status:** **PARTY-RATIFIED 4/4 GO-W-AMENDMENTS (all folded) — story-ready; dev dispatch gated on the formal S7 Phase-1 + Pass-2 close (ceremony executing this session).**
**Ratification record:** [`s7-phase2-party-record-2026-07-08.md`](../planning-artifacts/s7-phase2-party-record-2026-07-08.md) (per-voice verbatim + consensus §5).
**Requirements source:** operator brief [`s7-phase2-course-source-management-brief-2026-07-08.md`](../planning-artifacts/s7-phase2-course-source-management-brief-2026-07-08.md). Program SSOT: [`lesson-plan-rationale-platform-positioning-2026-07-07.md`](../planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md) §4.
**Execution mode (operator-directed, standing):** `bmad-quick-dev`-style spec → monitor SOP pre-dispatch poll → **fresh dev agent, RED-first** → SOP dev-complete poll + 3-lane `bmad-code-review` → RED-first remediation → orchestrator re-verify → **live / live-safe witness (PASS required; never close offline-green)** → commit (standing strays excluded) → SOP close poll. One dev lane.

---

## 0. Program shape (binding)

**Sequencing:** formal S7+Pass-2 close (gate, this session) → **Story A** → **Story B ∥ Story C** (independent) → **Story D** → the **selection-edge spine** (`lesson-plan-directs-production-collateral-to-selection-edge`) is filed BY NAME as the immediate next arc in Story D's close-out artifact — never back into the general inventory pool (John binding).

**Reconciliation with the filed Phase-2 items (party §5.1):** spine untouched-in-scope / hardened-in-binding (D ends at a contract-tested `ComponentSelection` boundary); `course-and-sme-registry` SPLIT (identity core → Story A; styleguide/voice/approval-routing stays deferred, blocking prerequisite before any HAI 510 production run); `course-purpose-and-operator-owned-lo-inputs` EXPANDED (substrate via B+D; Irene-signature change + operator LO-ratification surface stay filed, re-trigger "after Story D lands"); `collateral-projector-family` UNTOUCHED (Story C = source EVIDENCE records, input-side; projectors = generated FORMS, output-side — hard boundary).

**Operator source-purpose clarification (2026-07-08, post-ratification / pre-dispatch; binding):** the syllabi supplied in the two new course containers are **reference examples of a course source type**, not the courses' real production source content. HAI 510 is a **new-build course** whose real source will arrive as four modules of recorded lecture video plus corresponding slides. PHS 620 is an **existing-course enhancement** effort whose real source will come through Confluence and Canvas access to current course content. Phase-2 source ingestion/enrichment must therefore model source **availability and purpose** honestly: "syllabus-only seed/reference" is not "source-complete"; absent local lectures/slides or pending Confluence/Canvas access are expected gaps, not crashes and not `source_grounded` evidence. Lesson-planning inputs must preserve enough of this source-purpose context for the later ratified lesson plan to establish a clear production direction, an asset-building task list, and a suitable workflow choice for downstream consumers. This clarification does **not** authorize remote Confluence/Canvas ingestion in Stories A-D unless explicitly added by a later story/gate; it prevents the seed syllabi from being over-claimed as complete source packages.

**Binding constraints (every story):**
- ⛔ **SPOC-product-only** (brief AC-8): PHS 620 / HAI 510 are fixtures + evidence, never design targets. Any AC justifiable only as "so the seed courses import cleanly" is struck.
- **Lesson-leaf runtime contract** (brief §1.2) — mechanically ENFORCED from Story A on; the `runtime_contract` YAML stanza is declared policy and explicitly does NOT satisfy AC-6 alone (Murat binding).
- **Source buckets ≠ asset folders** (§1.3): bucket names are detection *hints*, never classification authority.
- **Gap handling is a core function** (§1.5), **SOURCE+LOs are KING**: derived lesson-level LOs enter as `inferred`/`needs_sme_review`, never silent `source_grounded`; syllabus-derived declarations never substitute for missing real source content.
- **No LMS over-modeling** (§5.1): no grading/points/policy models — syllabus policies stay raw source. Manifest fields require a named consumer.
- **Tejal-styleguide fallback explicit, never silent** (§5.5): non-Tejal SME styleguide resolution yields marked-fallback-or-gap (witness in Story D).
- **Tier ruling:** Stories A/B/C Tier-1 (zero `pipeline-manifest.yaml` edits — the new package is a SIBLING of `lesson_plan/`, and `composer.py`/`trial.py` are not in `block_mode_trigger_paths`); Story D Tier-1 **iff** its negative-AC fence holds. Any breach = STOP + party re-scope (Tier-2 governance event).
- **Baseline hygiene (Murat):** score by causation-isolation (reds ON ∖ reds OFF, isolated `-n 0` re-runs) vs the ~81-82 pre-existing baseline ledger, re-snapshotted at each story open. **Fixture-inertness witness** required for every story adding files under `course-content/courses/` (fixtures-only run, zero baseline delta). Brittle content assertions run against **frozen fixture copies**; the live containers are reserved for live-safe evidence runs asserting structural invariants only (they are operator working directories and WILL mutate).

**Substrate ground-truth (Amelia, verified at HEAD `caf312d6`):** the seeded containers already carry a de-facto `schema_version: 0.1` (`course.yaml` with course_id / sme.name / course.{code,title,module_count_expected} / runtime_contract; HAI additionally source_references + full modules list; PHS 620's 15 `module.yaml`s are `title: TBD / status: placeholder` — **asymmetry is a feature, tests must pass on both**). Zero code reads these files today; the only runtime course handle is `_course_key()` at `app/marcus/cli/trial.py:248-255` (a path, not an entity). Corpus enumeration has ONE chokepoint: `_walk_corpus_files` at `app/composers/section_02a/composer.py:34-43`, reached by (1) `compose_and_write` (`cli_adapter.py:31`) ← `trial.py:386` [START walk G0], (2) `g0_enrichment_wiring._enumerate` (`g0_enrichment_wiring.py:421-430`) ← `production_runner.py:2656` [START] **and** `:3383` [CONTINUATION] — a guard there covers both walks by construction. Pattern templates: `collateral_spec.py` (schema idioms), `generate_capability_overlay.py` → `capability-overlay.yaml` (generator + committed snapshot + staleness check). Corrected citations: `app/marcus/cli/front_door.py:136-194`, `app/models/state/component_selection.py` (SSOT §3's paths were stale).

**HOLD-for-operator register (block only the named action, not spec/dev):** (1) PHS 620 slug renames — B-2 gate; (2) legacy-`.doc` long-term policy (extractor vs convert-on-intake) — until decided, `format_unsupported` gap; (3) HAI 510 companion reading-list acquisition; (4) HAI 510 lecture-video/slide source delivery path; (5) PHS 620 Confluence/Canvas access and source-capture policy; (6) lesson-leaf granularity inside `modules/<slug>/lessons/`; (7) operator LO-ratification surface; (8) first production-target course; (9) gap-ledger committed-vs-evidence disposition (provisional ruling in Story A stands unless overridden); (10) asset kinds beyond the evidence-grounded core.

---

## Story A — Course-source container registry, manifest scan, and the lesson-leaf runtime guard

**Job:** the app can discover/read/validate the two seeded course containers, emit a deterministic source manifest + gap ledger, and the production runtime REFUSES broad course/module roots — protecting live spend before any other Phase-2 code exists.

### Deliverables

- **A-D1 (FIRST, live-proven first — the guard).** Broad-root refusal at the single enumeration chokepoint `_walk_corpus_files` (`app/composers/section_02a/composer.py:34-43`): refuse when the supplied `corpus_dir` contains a container sentinel — `course.yaml` or `module.yaml` present, or a `modules/` subdirectory — raising the composer's typed error family (e.g. `DirectiveCompositionError` with a distinct `non-runnable-scope` tag) **before any file ingestion and before any API client is constructed** (fail before spend). Marker-presence alone decides refusal; one `yaml.safe_load` of `runtime_contract` may enrich the error MESSAGE only. Belt-and-suspenders: extend the existing CLI fail-loud block at `app/marcus/cli/trial.py:375-381` with the same check (friendlier message naming the lesson-leaf contract + the brief). A lesson leaf under `modules/<m>/lessons/<l>/` carries neither sentinel → passes.
- **A-D2.** NEW sibling package `app/marcus/course_source/` (NOT under `lesson_plan/` — keeps the diff physically off `block_mode_trigger_paths`):
  - `models.py` — Pydantic v2 family mirroring `collateral_spec.py` idioms (`ConfigDict(extra="forbid", validate_assignment=True)`, closed enums, `OPEN_ID_REGEX_PATTERN` reuse): `CourseRecord`, `ModuleRecord`, `SourceScope = Literal["course","shared","module","lesson"]`, `SourceManifestEntry`, `GapEntry`. Validates the operator-seeded `schema_version: "0.1"`. SME fields = identity ONLY (`sme` name/role/attribution/owning-course) — no styleguide/voice/routing fields (deferred half of `course-and-sme-registry`). The model family may carry an explicit source-purpose / source-availability marker only if it serves gap reporting or lesson-planning input; it must not over-model LMS state.
  - `registry.py` — YAML read-through loader `load_course(course_root) -> CourseRecord` (no cache, no DB).
  - `manifest_scan.py` — read-only deterministic scanner: walks the container, classifies scope **by path position** (`sources/course/`→course, `sources/shared/`→shared, `modules/<m>/sources/`→module, `modules/<m>/lessons/<l>/`→lesson), reuses the repo's content-hash discipline (`file_content_hash` pattern per `g0_enrichment_wiring.py:433-443`), and RECONCILES declaration vs disk — drift is reported as gap entries, never silently trusted either way. Stable ordering; run-twice byte-identical.
- **A-D3 (manifest/ledger disposition — party §5.4 provisional ruling).** Source manifest = **generated + committed snapshot** under the course container (declared vs detected fields structurally separated so regeneration never clobbers human input) + a **regenerate-and-diff drift check script** (L1-check pattern; fails loud on any delta; runs in the offline suite). Gap ledger = **generated-only into timestamped evidence dirs**; the committed manifest may carry a `gap_summary` block (counts + gap ids only, never the full ledger). Neither file joins `block_mode_trigger_paths`.

### Acceptance criteria

- **A-AC1 (guard, course root):** the REAL production entry (the same CLI/path live runs use — not a test helper) pointed at `course-content/courses/aziz-nazha-hai-510-generative-ai-in-healthcare/` fails loud with the typed refusal, zero files ingested, zero API clients constructed.
- **A-AC2 (guard, module root):** same for a `modules/<slug>/` root (contains `module.yaml`).
- **A-AC3 (guard, positive control):** a proven lesson leaf (`studio-smoke-min`-class + the tejal leaves) still runs/pauses exactly as at baseline — the guard's RED tests include this must-still-pass (Amelia's false-positive risk).
- **A-AC4 (registry):** `load_course` parses BOTH seeded containers; PHS 620's asymmetry (no `modules:` list in course.yaml, `title: TBD` placeholders) is VALID-with-gaps, not an error; malformed/missing required fields fail loud.
- **A-AC5 (scope):** scope classification is pure path-position; round-trip tested for all four scopes on both containers.
- **A-AC6 (gaps-not-crashes):** empty `sources/` and `lessons/` dirs (the seeded reality) produce gap entries, never crashes — §1.5 exercised for real on day one. The HAI 510 missing companion reading list is emitted as a named gap entry (with an access-coaching note field, per the coaching rule). The scan must distinguish "syllabus/reference present" from "real source content present": HAI 510 lecture videos/slides absent from the local container and PHS 620 Confluence/Canvas access pending are represented as explicit source-availability gaps when declared or observed, never silently promoted to complete source coverage.
- **A-AC7 (determinism):** scan run twice → byte-identical manifest + ledger (stable ordering, content digests). No LLM anywhere in the derivation path (deterministic-gap rule).
- **A-AC8 (drift gate):** the check script regenerates from disk and diffs against the committed snapshot, failing loud on delta; a deliberate-drift RED test proves the teeth.
- **A-AC9 (fixture-inertness):** with the containers present and ZERO code diff, the pre-existing test tree scores zero delta vs the baseline-red ledger (docx-stray category watched).
- **A-AC-L (live-safe witness — Murat's ratified Q7 shape):** one scanner command per course root →
  `evidence/s7p2-two-course-scan-<ts>/{phs-620,hai-510}/{manifest.yaml,gap-ledger.yaml}` + `broad-root-refusal.log` (typed refusal, nonzero exit, captured from the REAL entry) + `negative-control.log` (non-course dir → "not a course container"). Scripted deterministic assertions: 15-vs-4 module asymmetry matches ground truth; the PHS syllabus file appears with a detected kind + honest ingestion status; ledgers non-empty; refusal fired BEFORE any ingestion; **grep-witness: no `phs`/`hai`/course-slug literal in the `app/` source diff** (same code, two materially different structures). Zero API spend.

### RED-first plan
Guard reds first (AC1/AC2 fail at baseline — the runtime happily walks a course root today; AC3 green at baseline as the pin). Then registry/model reds off frozen fixture copies of both containers; scanner determinism + drift-gate reds; fixture-inertness run.

### Out of scope (fence)
Syllabus parsing (Story B). Asset records (Story C). Bundles (Story D). Any container mutation. Any styleguide/SME-routing field. Any `pipeline-manifest.yaml` edit.

---

## Story B — Syllabus-derived module metadata: extraction + PROPOSAL only

**Job:** parse both supplied syllabi into provenance-carrying module-metadata **proposals** (titles/topics/LOs/bucket suggestions) without mutating a single container file. The syllabi are reference/course-structure sources, not complete production source packages; Story B must not infer that a module's real lecture, slide, reading, lab, assignment, or Canvas/Confluence content is present merely because a syllabus row names it. Application of proposals is a separate operator-gated leg (**B-2**, not this story).

### Deliverables
- **B-D1 (readers — zero new dependencies, Amelia-verified):** HAI 510 syllabus `.docx` via already-shipped `python-docx>=1.1` (`pyproject.toml:24`; first read-side use — write-side proven at `workbook_producer.py:49`). PHS 620 `PHS 620 Syllabus 2025.doc` is **NOT binary Word — it is a MIME/MHTML Confluence export** (verified by byte inspection): parse via stdlib `email` + HTML strip. Any file the readers cannot verifiably extract → explicit `format_unsupported` gap record; **no third state** — mojibake must be structurally unable to enter metadata (post-extraction sanity sentinel required).
- **B-D2 (extraction artifact):** a machine-readable module-metadata **proposal** (YAML) per course: proposed topic-bearing slugs (brief §2.1 table = PHS draft; HAI slugs already aligned — verify not invent), module titles/topics, course-level LOs (PHS: 12; HAI: 6), learner profile/audience, optional source-bucket suggestions — EVERY field carrying a `source_ref` anchor (syllabus path + row/section locator).
- **B-D3 (proposal-only fence):** the story writes ONLY the proposal artifact + tests; the container trees are byte-untouched (asserted).
- **B-D4 (fixture-tracking honesty — found at the close commit):** the HAI 510 syllabus `.docx` is **gitignored** (`course-content/**/*.docx`, `.gitignore:77` binary-media convention) — it exists locally but does NOT ride the committed container (the PHS `.doc` DOES commit — MHTML text). Story B therefore (a) commits a **frozen extracted-text fixture** of each syllabus under `tests/fixtures/` (committable, satisfies Murat's pinning rule), (b) treats the live `.docx` as machine-local evidence input, and (c) MAY propose a narrow gitignore exception for syllabus sources at its SOP pre-dispatch poll (operator convention — do not override silently). The Story-A scanner records the `.docx` in the manifest with a `tracked: false` provenance flag so the manifest never lies about clone-reproducibility.

### Acceptance criteria
- **B-AC1 (anti-fabrication — a test, not a guideline):** a module with no syllabus row yields `status: missing` — never an invented title. Every emitted field has a provenance anchor; an anchor-less field fails validation.
- **B-AC2 (no-mojibake):** extraction ends in exactly one of two states — sentinel-verified text (PHS: contains "Teaching Learning Seminar" AND yields 12 course LOs; HAI: 6 LOs, 4 modules) or `format_unsupported` gap. A corrupted-decode fixture RED-proves the third state is impossible.
- **B-AC3 (cross-course):** 15 metadata records vs 4; PHS proposed slugs match the brief §2.1 table (or divergence is explained field-by-field); HAI slugs confirmed against the container.
- **B-AC4 (fence):** `git status` over `course-content/courses/` is empty after the full suite + live run (byte-untouched containers). Content assertions run against frozen fixture copies (live syllabi may be edited by the operator).
- **B-AC5 (fixture-inertness + causation-isolation):** per program rules.
- **B-AC-L (live-safe witness):** run the real extractor against the two REAL syllabus files on disk; proposal artifacts land in the evidence dir (extends the Story-A evidence shape with `module-metadata.yaml` per course); assertions B-AC1..B-AC3 scripted + deterministic. Zero API spend. **Parse the PHS `.doc` in the story's first days, not at close** (John).

### Out of scope (fence)
**B-2 (separate, operator-gated leg):** applying proposals — `git mv` of the 15 PHS module dirs to topic-bearing slugs + `module.yaml` rewrites + bucket scaffolding — dispatches ONLY on explicit operator confirmation of the proposal artifact, executed once (renames churn every provenance ref — never iteratively). No LLM extraction in B (deterministic parse only; an LLM-assist later would emit `inferred`-status fields per the gap-honesty rule). No policy/grading modeling (points tables stay raw source).

---

## Story C — Canonical asset record contract (schema-shape story)

**Job:** the minimal, closed, teeth-bearing record shape for "what the course provides / what's missing" — the evidence boundary between raw sources and downstream consumers.

**Scaffold discipline (per CLAUDE.md):** this is a schema-shape story — read `docs/dev-guide/pydantic-v2-schema-checklist.md` + use `docs/dev-guide/scaffolds/schema-story/` at T1; deliverable = Pydantic-v2 model family + emitted JSON-Schema mirror + shape-pin tests + SCHEMA_CHANGELOG entry.

### Deliverables
- **C-D1:** `CanonicalAssetRecord` (in `app/marcus/course_source/asset_records.py`): `asset_id`, `asset_kind` (**closed enum v0.1**: `reading`, `lecture`, `lab`, `assignment`, `assessment`, `discussion_prompt`, `syllabus`, `project_artifact` — trim/confirm at T1 against consumers; widening is a later governance act, not a runtime flag), `course_id`/`module_id`/`lesson_id?`, `source_refs`, `learning_objective_refs`, **unified status enum** (ONE vocabulary for asset records AND gap entries — John's migration-prevention amendment): `source_grounded | partial | inferred | missing | required_gap | draft_gap_fill | needs_sme_review`, kind-specific `content` payload, `gaps`, `review.sme_required`.
- **C-D2 (vocabulary reconciliation — C-1):** `asset_kind` strings reconciled with the existing vocabularies before minting anything new — `g0_enrichment_wiring.py:396-413` `_TYPE_KEYWORDS` (`discussion_forum`, `assignment_instructions`, `exercise_lab`, `reference_citation`) and `app/marcus/lesson_plan/source_type.py` / `source_point.py` / `produced_asset.py`. A documented mapping table where names differ; no forked enums.
- **C-D3 (boundary doc):** the "when does a source become a canonical record" contract — ingestion TAGS, enrichment CANONICALIZES; a syllabus row is evidence-of-REQUIREMENT, not content.

### Acceptance criteria
- **C-AC1 (the §5.4 teeth — mandatory, Murat):** `status: source_grounded` with empty content-bearing `source_refs` **fails validation** (model_validator). Triple-layer red-rejection on both closed enums; `validate_assignment=True`; round-trip serialization; shape-pin tests.
- **C-AC2 (syllabus-row honesty):** records derived from syllabus rows alone carry `status ∈ {missing, required_gap, inferred}` with the syllabus anchor as the REQUIREMENT ref — constructor-level test proves `source_grounded` is unreachable from row-only evidence.
- **C-AC3 (LO honesty — SOURCE+LOs KING):** derived lesson-level LO records enter as `inferred`/`needs_sme_review`; a red test proves silent `source_grounded` promotion is impossible.
- **C-AC4 (projector exclusion — Winston):** the story adds ZERO projection/generation code; records model source EVIDENCE only (input-side). Grep-AC: no imports from `workbook_enrichment.py`/projector modules.
- **C-AC5 (honest emission witness, live-safe):** deterministic emission over the real HAI 510 syllabus rows + the (empty) source pools → **zero records claim `source_grounded`** — the seeded emptiness makes "everything is a gap" the honest output, and the suite proves the system says so.
- **C-AC6:** JSON-Schema mirror emitted + pinned; SCHEMA_CHANGELOG entry; fixture-inertness + causation-isolation per program rules.

### Out of scope (fence)
Projector family (own filed item; hard boundary). Deferred kinds (`case`, `dataset`, `slide_seed`/`script` split, `quiz`-vs-`assessment`). Any LLM tagging (later entries would be `inferred`-status by rule). Any consumer wiring.

---

## Story D — Lesson-planning input bundle prototype (fenced)

**Job:** ONE artifact that packages everything lesson planning should eventually receive — proving the derives-from half of the vision is assembled and consumable — while structurally guaranteeing the directs-into half (the selection edge) stays its own arc.

### Deliverables
- **D-D1:** `LessonPlanningInputBundle` model + builder (in `app/marcus/course_source/input_bundle.py`): course profile + purpose, course-level LOs, learner profile, module profile + module-level LOs, scoped source manifest (course/shared/module/lesson DISTINGUISHABLE — no flattening), canonical asset records, **gap ledger riding inside the bundle** (Irene must plan around declared gaps), operator-selected focus, available workflow/collateral capability list. Loader/read API. Consumes Story A/B/C outputs.
- **D-D1a (source-purpose carry-through):** the bundle preserves the source-development purpose needed by lesson planning and later workflow selection: HAI 510 = new-build from recorded lectures/slides; PHS 620 = enhancement of an existing complete course via Confluence/Canvas. This is context for planning, asset-task-list formation, and future selection-edge work; D still does not build the `collateral → ComponentSelection` derivation edge.
- **D-D2 (the John amendment — contract test at the spine's boundary):** an acceptance test proving the bundle is consumable by the selection edge with ZERO reshaping, validated against the REAL input shape of `app/models/state/component_selection.py` (not a paraphrase). This is the spine's input contract, not the spine.
- **D-D3 (§5.5 witness — Murat R3):** styleguide resolution carrying a non-Tejal SME identity (aziz-nazha) yields an **explicitly marked fallback** (`fallback: true` + reason) or a `sme_styleguide_missing` gap entry — never a bare Tejal guide id presented as native. (Five lines of honesty, not a routing system — Winston.)
- **D-D4 (close-out obligation):** Story D's close-out artifact files the selection-edge spine BY NAME as the immediate next arc (with the S8 prose arc interleaved per operator priority).

### Acceptance criteria
- **D-AC1 (reproducibility):** bundles built for one module of EACH course; run twice → stable-ordered byte-identical output; schema-valid.
- **D-AC2 (scope preservation):** course LOs and module LOs remain distinguishable in the bundle (structural assertions — brief AC-3's no-corpus-blob rule).
- **D-AC3 (gap ride-along):** the bundle's `gap_ledger` section is populated from the Story-A scan for the chosen modules; access-coaching notes present on fetchable-material gaps.
- **D-AC3a (planning-direction inputs):** bundles expose the source-purpose and source-availability state distinctly enough that a later ratified lesson plan can produce a clear production direction, asset-building task list, and workflow recommendation without treating syllabi as complete source content.
- **D-AC4 (contract test):** D-D2 passes against the real `ComponentSelection` shape.
- **D-AC5 (NEGATIVE fence — Amelia D-1, hard AC):** the story's diff touches NONE of `app/marcus/lesson_plan/composition.py`, `app/models/state/component_selection.py`, `app/marcus/lesson_plan/bundle_catalog.py`, `app/marcus/cli/front_door.py`, nor ANY `block_mode_trigger_paths` entry; no Irene-dispatch wiring; no `collateral → ComponentSelection` derivation code. Enforced by a diff-scope check at review + a grep witness. Breach = STOP + party re-scope (Tier-2 event).
- **D-AC6 (close witness):** schema-valid reproducible bundles on disk for both courses + the contract test + a documented consumption seam = the close (Murat's stricter reading, ratified). A live Irene Pass-1 smoke consuming the bundle is OPTIONAL COLOR, recorded if run, never the close witness. Fixture-inertness + causation-isolation per program rules.

### Out of scope (fence)
The selection edge (next arc, by name). `course_purpose` as an actual Irene Pass-1 input + the operator LO-ratification surface (filed residue, re-triggers at D-close). Any styleguide routing beyond the D-D3 honesty marker.

---

## Program close proof (brief §6 Q7 — ratified)

Story-A/B evidence shape (two manifests + two gap ledgers + two module-metadata proposals + refusal + negative control, zero spend) is the FIRST generalizability proof. At D-close, John's extension completes it: + two schema-valid reproducible input bundles (one per course) + the `ComponentSelection` contract test green + the D-D3 fallback witness. **Two materially different course structures (15-module academic MHTML-`.doc` vs 4-module professional `.docx`), zero video, zero Gamma spend, no full course build.**
