# S7 Phase 2 Brief - Course Source Management, Ingestion, and Enrichment

**Date:** 2026-07-08  
**Status:** planning brief for BMAD party-mode/spec authoring  
**Audience:** Marcus-SPOC orchestrator, BMAD party-mode team, S7 Phase 2 spec author, dev/review agents  
**Related:** `lesson-plan-rationale-platform-positioning-2026-07-07.md`, `canonical-arc-s7-workbook-generalization.md`, `course-content/courses/`, `docs/ONBOARDING.md`

---

## 0. Purpose

S7 Phase 1 proved that the workbook producer can consume real in-graph lesson-plan/collateral/enrichment inputs instead of Tejal-specific constants. Phase 2 is the right moment to strengthen the upstream substrate: how course source material is organized, ingested, normalized, enriched, and used by lesson planning to select appropriate workflows and collateral.

This brief records the operator decisions and early source evidence from two real courses:

- **PHS 620 - Teaching Learning Seminar**, Juan Leon, 15 modules.
- **HAI 510 - Generative AI in Healthcare**, Aziz Nazha, 4 modules.

The goal is not to add course-content bookkeeping for its own sake. The goal is to make the Marcus-SPOC product more robust across SMEs, courses, modules, lessons, and heterogeneous source materials while preserving the current production boundary: workflows should run from a lesson-level corpus leaf, not from a broad course or module root.

---

## 1. Decisions To Carry Into S7 Phase 2

### 1.1 Course containers are now required

The prior source layout was sufficient for isolated proofing corpora, but not for production of whole courses. A real course can have course-level authority, module-level source pools, lesson-level corpora, and shared supporting material. Therefore, a course-specific container should become the standard source-management shape under `course-content/courses/`.

Minimum course shape:

```text
course-content/courses/<course-slug>/
  COURSE.md
  course.yaml
  sources/
    course/
    shared/
  modules/
    <module-slug>/
      MODULE.md
      module.yaml
      sources/
      lessons/
```

The folder hierarchy should encode **scope and provenance**, not downstream asset type. Asset typing belongs to ingestion/enrichment.

### 1.2 Runtime input remains lesson-leaf scoped

Current workflows recursively ingest a supplied input directory. Until the runtime explicitly understands course/module roots, the safe contract is:

- `course_root`: metadata and source management only; not directly runnable.
- `module_root`: module source management only; not directly runnable.
- `lesson_corpus_leaf`: runnable input for current Marcus-SPOC workflows.

This should remain explicit in `course.yaml`:

```yaml
runtime_contract:
  runnable_input_scope: lesson_corpus_leaf
  do_not_run_from:
    - course_root
    - module_root
```

S7 Phase 2 can add discovery/selection logic, but should not silently reinterpret broad roots as runnable corpora.

### 1.3 Source category folders are allowed; canonical asset folders are premature

The syllabi reveal useful source categories, especially readings, lecture/presentation material, labs, assignments, assessments, discussion prompts, and project artifacts. These can exist as **source buckets** when they help operators place material.

Do not pre-create canonical downstream asset folders such as `discussion_forum/`, `script/`, `quiz/`, `workbook/`, or `slide_deck/` as if the source has already been classified. Instead:

1. Raw/source material enters a scoped source pool.
2. Ingestion analyzes and tags resources.
3. Enrichment produces canonical asset records when evidence supports a type.
4. Lesson planning records gaps where required assets are missing, inferred, or need SME/operator review.

This keeps the system robust when a module provides only seeds, notes, links, scripts, partial slides, or a syllabus row rather than completed assets.

### 1.4 Course-level and module-level learning objectives are both first-class

Course-level objectives, learner profile, catalog/admin details, and syllabus policies should live at course scope. Module-level objectives and module-specific source material should live at module scope. Lesson-level objectives may be authored or derived during lesson planning.

S7 Phase 2 should make this hierarchy visible to Irene/lesson planning rather than flattening every source into one corpus blob.

### 1.5 Gap handling is a core function, not an error case

The workflow should expect incomplete source packages. Gap detection and gap-filling recommendations are central to lesson planning. Canonical asset records should be able to distinguish:

- source-grounded material,
- missing but required material,
- inferred material,
- generated gap-fill draft,
- SME/operator review required,
- blocked item requiring external source or policy judgment.

---

## 2. Evidence From The Two Seed Courses

### 2.1 PHS 620 syllabus signals

The PHS 620 syllabus is a Confluence-exported `.doc` in the course-level source pool. It provides:

- course code, modality, session, instructor, contact, course description;
- required textbook and notes on library access;
- 12 course learning objectives;
- a 15-week/module course calendar;
- weekly discussion topics, readings/resources, live round-table presentation topics, assignments, and feedback/evaluation items;
- assignment point allocation table;
- course policies including participation, late work, writing standards, AI tool use, grading, academic integrity, and administrative policies.

The syllabus supports upgrading generic `module-01` ... `module-15` folders to topic-bearing slugs and metadata.

Recommended PHS 620 module slugs:

| Module | Recommended slug | Syllabus signal |
|---|---|---|
| 01 | `module-01-adult-learner-course-introduction` | Adult learner, course introduction, onboarding, learner profile |
| 02 | `module-02-stakeholders-addie-course-projects` | Accreditors/stakeholders, ADDIE, project proposal |
| 03 | `module-03-hybrid-lessons-mixed-modality` | Online vs classroom, Gagne, UDL, mixed modality |
| 04 | `module-04-presentation-skills-lecture-design` | Presentation skills, lecture rehearsal |
| 05 | `module-05-virtual-audience-online-instruction` | Virtual audience, online instructional activity, online lecture delivery |
| 06 | `module-06-feedback-assessment-lesson-prerecording` | Feedback, assessment, prerecording completed lesson |
| 07 | `module-07-final-lesson-design-implementation-roadmap` | Prerecorded presentations, implementation roadmap |
| 08 | `module-08-its-framework-project-design` | AI/ITS resources, project candidates, ITS framework mapping |
| 09 | `module-09-requirements-objectives-cruces` | Requirements, objectives, instructional activities, cruces |
| 10 | `module-10-design-critiques-project-presentations` | Design critiques and project design presentation |
| 11 | `module-11-project-alpha` | Alpha build/deployment |
| 12 | `module-12-usability-testing-project-beta` | Usability testing and beta deployment |
| 13 | `module-13-project-performance-validation` | Performance data and validation |
| 14 | `module-14-project-validation-real-world-transfer` | Validation data, outcomes, real-world context |
| 15 | `module-15-reflection-transfer-of-learning` | Reflection, concluding consult, transfer of learning |

PHS 620 also suggests optional module source buckets:

```text
sources/
  readings/
  discussion-prompts/
  live-session/
  assignments/
  assessments/
  feedback/
```

These should be source buckets only. Canonical discussion/assessment/workbook records should be produced by ingestion/enrichment, not by folder naming alone.

### 2.2 HAI 510 syllabus signals

The HAI 510 syllabus is a `.docx` in the course-level source pool. It confirms:

- synchronous virtual format;
- four weeks, two hours per week;
- each session combines a didactic lecture and hands-on lab;
- target audience spans health sciences/research faculty, clinicians/educators, program directors/leaders, and informatics leaders;
- no prerequisites;
- six course learning objectives;
- final project requiring a prototyped real-world AI solution;
- recommended readings list exists as a companion source, organized by module.

The current four module slugs are aligned with the syllabus:

| Module | Slug | Syllabus signal |
|---|---|---|
| 01 | `module-01-foundations-of-ai-in-healthcare` | AI paradigms, predictive vs generative AI, model landscape, tool comparison lab |
| 02 | `module-02-how-llms-work-and-prompt-engineering` | deep learning, transformers, tokenization, embeddings, RLHF, prompt lab |
| 03 | `module-03-ethics-and-challenges` | hallucination, bias, privacy/security, HIPAA/FDA, adversarial attacks, audit lab |
| 04 | `module-04-agentic-ai` | agents, multi-agent design, workflow automation, multi-agent workflow lab |

HAI 510 suggests module source buckets:

```text
sources/
  readings/
  lecture/
  lab/
```

It also suggests a course-level cross-module project source bucket:

```text
sources/
  final-project/
```

The companion recommended reading list is a high-value missing source. It should be requested or explicitly filed as a gap before downstream enrichment claims a complete readings substrate.

---

## 3. Proposed S7 Phase 2 Product Shape

### 3.1 Course source registry

Introduce a minimal course-source registry that can read course containers and expose:

- course identity: `course_id`, code, title;
- SME/faculty identity;
- expected module count;
- source references;
- module list with stable slugs and titles;
- source pools by scope: course, shared, module, lesson;
- runtime safety contract.

This should be intentionally small. It is a source-management substrate, not a full LMS model.

### 3.2 Source manifest and provenance

Each source pool should be able to produce or maintain a source manifest. At minimum, the manifest should capture:

- source path or URL;
- scope: course/shared/module/lesson;
- owner course and module if applicable;
- human label/title;
- detected or declared source kind;
- ingestion status;
- provenance notes;
- gaps or follow-up needed.

The manifest may be materialized as YAML/JSON or generated dynamically, but the spec should require deterministic, reviewable evidence.

### 3.3 Canonical asset records

When ingestion identifies a resource as a discussion forum seed, lecture script, lab, assignment, assessment, slide seed, reading, case, dataset, or workbook-relevant support, enrichment should emit canonical records with a stable shared shape:

```yaml
asset_id: <stable-id>
asset_kind: <discussion_forum|script|lab|assignment|assessment|slide_seed|reading|case|dataset|...>
course_id: <course-slug>
module_id: <module-slug>
lesson_id: <lesson-slug-or-null>
source_refs: []
learning_objective_refs: []
status: <source_grounded|partial|inferred|missing|required_gap|draft_gap_fill|needs_sme_review>
content:
  # kind-specific normalized payload
gaps: []
review:
  sme_required: true|false
```

The concrete schema can evolve, but S7 Phase 2 should establish the architectural commitment: downstream consumers should not parse arbitrary syllabus rows or raw notes directly when a canonical asset record exists.

### 3.4 Lesson planning input bundle

Irene/lesson planning should eventually receive a richer bundle:

- course profile and purpose;
- course-level learning objectives;
- learner profile/audience;
- module profile and module-level objectives;
- scoped raw/canonical sources;
- source manifest and gap ledger;
- operator-selected focus for the lesson/part;
- available workflow/collateral capabilities.

Phase 2 should not have to solve every workflow-selection edge, but should make this input shape explicit enough that future stories can connect `lesson_plan["collateral"]` to `ComponentSelection`.

---

## 4. Suggested Acceptance Criteria For The Upcoming Spec

The BMAD party should refine these into story-ready ACs.

1. **Course containers recognized:** The app has a documented, test-covered way to discover/read the two seeded course containers without treating course/module roots as runnable corpora.
2. **Module metadata grounded in syllabi:** PHS 620 and HAI 510 module metadata can be populated from syllabus-derived titles/topics, with explicit source provenance.
3. **Scoped source pools preserved:** Course-level, shared, module-level, and lesson-level sources remain distinguishable through ingestion.
4. **Manifest/gap evidence produced:** A dry-run or live-safe source scan can produce a reviewable manifest and gap ledger for each seed course.
5. **Canonical asset boundary defined:** Ingestion/enrichment has a documented contract for when a source becomes a canonical asset record, and when it remains raw/partial/missing.
6. **Lesson-leaf runtime safety enforced:** Existing production runs cannot accidentally ingest an entire course container when only a lesson corpus is intended.
7. **Two real courses used as fixtures/evidence:** PHS 620 and HAI 510 are used to test generalizability across long academic-course structure and short professional-development structure.
8. **No proofing-vehicle distortion:** Changes must strengthen the Marcus-SPOC product, not merely make a one-off course-import demo pass.

---

## 5. Risks And Design Traps

### 5.1 Over-modeling the LMS

The app does not need a complete LMS schema. Keep the model focused on source management, provenance, lesson planning, workflow selection, enrichment, and collateral generation.

### 5.2 Premature asset folders

Do not encode downstream asset types as folders before ingestion. A syllabus row named "assignment" is evidence, not a canonical assignment object.

### 5.3 Recursive ingestion hazards

The current runtime can recursively consume a directory. Broad source containers must not become accidental input roots.

### 5.4 Syllabus over-trust

Syllabi are authoritative course sources, but they are still incomplete for production. HAI 510 explicitly references a companion reading list; PHS 620 references linked pages/resources and assignments that need source capture. Missing companion material should become gap ledger entries.

### 5.5 Hidden SME/styleguide coupling

Course containers introduce real SME plurality. Any S7 Phase 2 story that reads SME identity should avoid silently reusing a single Tejal styleguide path unless it is explicitly marked as a fallback or gap.

---

## 6. Recommended Party-Mode Questions

Ask the fully spawned BMAD party to resolve these before spec freeze:

1. What is the smallest registry/manifest shape that lets the app distinguish course, module, lesson, and shared source scope without building an LMS?
2. Should source manifests be committed files, generated artifacts, or both?
3. What canonical asset kinds are needed now for S7 Phase 2, and which should remain deferred?
4. How should gap records flow into lesson planning and operator review?
5. What hard guard prevents broad course/module roots from being used as runnable corpora?
6. Which source fields are required for multi-SME support now, and which belong to a later styleguide/approval-routing story?
7. What is the first live proof that demonstrates genuine generalizability across PHS 620 and HAI 510 without requiring a full course build?

---

## 7. Recommended Initial Story Split

### Story A - Course source container registry and manifest scan

Read the seeded course folders, validate `course.yaml`/`module.yaml`, scan source pools, and emit a reviewable manifest plus gaps. No workflow generation yet.

### Story B - Syllabus-derived module metadata and source bucket normalization

Use the two syllabi to normalize module titles/topics and optional source buckets. Preserve provenance and do not fabricate missing material.

### Story C - Canonical asset record contract

Define and test the minimal canonical asset record shape for source-grounded, partial, inferred, missing, and SME-review-needed resources.

### Story D - Lesson-planning input bundle prototype

Build the first integration point that packages course/module/source manifest/gap context for Irene or the lesson-planning layer. This story can stop short of automatic workflow selection if needed.

---

## 8. Handoff Note To Spec Author

S7 Phase 2 should be framed as a generalization and robustness arc for course source management feeding lesson planning and workflow selection. It should not be framed as "make PHS 620 and HAI 510 work" except as real fixture/evidence courses. The right close proof is a small, honest, live or live-safe demonstration that the app can read two materially different course structures, preserve scope/provenance, identify useful source categories, and surface gaps without corrupting the current lesson-leaf runtime contract.

