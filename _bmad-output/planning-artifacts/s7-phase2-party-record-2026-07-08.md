# S7 Phase-2 Party Record — Course Source Management Spec Revision (2026-07-08)

**Session:** 20 (Class P at this round; upgrades to S when Phase-2 dev dispatches)
**Round:** fully-spawned bmad-party-mode, canonical core (Winston / John / Murat / Amelia), each seat an independent subagent grounded on the artifacts below.
**Subject:** revise the S7 Phase-2 program so it incorporates the operator's requirements brief [`s7-phase2-course-source-management-brief-2026-07-08.md`](s7-phase2-course-source-management-brief-2026-07-08.md).
**Grounding artifacts:** the brief (full text); [`lesson-plan-rationale-platform-positioning-2026-07-07.md`](lesson-plan-rationale-platform-positioning-2026-07-07.md) (Phase-2 SSOT §3/§4); `deferred-inventory.md §Lesson-Plan-as-Rationale Platform`; the two seeded course containers `course-content/courses/{juan-leon-phs-620-teaching-learning-seminar,aziz-nazha-hai-510-generative-ai-in-healthcare}/`; `docs/ONBOARDING.md` (KG current at HEAD `caf312d6`); Amelia's seat additionally spot-verified code seams at HEAD.
**Operator context:** the operator's further notes are **indefinitely deferred** (minor workbook-content points, per operator 2026-07-08); the operator directed the party to proceed to a story-ready spec. HOLD items below therefore block only the specific actions they name (e.g., folder renames), not spec freeze.

**RESULT: 4/4 GO-W-AMENDMENTS — no impasse. All amendments folded into the ratified program (§6).**

---

## §1 Winston (verbatim)

🏗️ **Winston:**

I've read the brief, the ratified positioning record, and re-checked substrate reality against ONBOARDING §3. Let me work the whiteboard in the order of the mandate.

### 1. Reconciliation — the brief against the four filed Phase-2 items

The brief is not a fifth item competing with the four. It is the **substrate program underneath items 2 and 3, feeding item 1, orthogonal to item 4**. Per item:

**`lesson-plan-directs-production-collateral-to-selection-edge` (the spine) — LEFT UNTOUCHED, but re-sequenced-toward.** The brief explicitly stops short (§3.4: "should not have to solve every workflow-selection edge, but should make this input shape explicit enough that future stories can connect `lesson_plan["collateral"]` to `ComponentSelection`"). Story D is the spine's *input contract*, not the spine. What changes is dependency order: the positioning doc's trigger was "after S7/S8"; the brief inserts the source-management program in between, and I think that's correct — deriving a `ComponentSelection` from a lesson plan that was itself planned off a corpus blob with no course purpose, no scoped LOs, and no gap ledger would be building the spine on sand. The spine's mechanism (the clean fail-closed composition DAG) is unchanged; its *inputs* get honest first.

**`course-and-sme-registry` — ACTIVATED and SPLIT.** The filed trigger — "operator onboards a second course or SME" — has *fired*: two real courses, two SMEs, on disk. The brief's §3.1 registry is the identity/scope half of that item (course identity, SME identity, module list, source pools, runtime contract). The other half of the filed item — per-SME voice/styleguide/attribution/**approval-routing** — the brief itself defers (§5.5, Q6). So: amend the inventory entry to record the split — identity half consumed by Story A, styleguide/routing half remains deferred with its own trigger. This is the cleanest disposition; don't let Story A quietly grow the styleguide half.

**`course-purpose-and-operator-owned-lo-inputs` — EXPANDED and mostly ABSORBED.** The brief's §1.4 (course-level AND module-level LOs first-class) is a strict expansion of the filed item, and it aligns with the binding SOURCE+LOs-are-KING directive. Stories B + D deliver the substrate (syllabus-derived LOs with provenance; the bundle that carries purpose + LOs + learner profile). What remains distinct in the filed item is the **Irene Pass-1 signature change** — actually feeding the bundle into planning — plus the operator *ratification* loop over the governing LO set. That residue should stay filed, retriggered as "after Story D lands."

**`collateral-projector-family` — UNTOUCHED, and keep it that way.** This is the one place I want a hard line drawn in the spec. **Canonical asset records (Story C) are normalized *source evidence* — upstream, input-side. Projectors are *generated forms* off `G0EnrichmentResult` — downstream, output-side.** They will look superficially similar (both have kinds, both have schemas) and a spec author under time pressure will merge them. Don't. A "reading" asset record says *the course provides this reading*; a quiz projection says *we generated a quiz*. Conflating evidence with product is exactly how gap handling (§1.5) stops being honest.

### 2. Story split — validate with three amendments, plus sequencing

The A/B/C/D split is fundamentally sound: A is read-only discovery, B is normalization, C is contract, D is integration. Boring, incremental, each independently live-provable per the incremental-live-testing directive. Three amendments:

**Amendment 1 — pull the runtime guard forward into Story A (or a small A0).** The brief files the lesson-leaf guard under AC-6 but doesn't assign it a story. The recursive-ingestion hazard (§5.3) is live *today* — the containers are already on disk, and nothing stops an operator or a script from pointing a trial at a course root this afternoon. The guard is the cheapest, highest-value change in the whole program and it protects existing production before any registry exists. It belongs in A, first task, live-proven first.

**Amendment 2 — Story B is parse-and-propose, not parse-and-rename.** Populating module metadata from syllabi with provenance: dev-agent work. Renaming PHS 620's fifteen generic module slugs to topic-bearing ones: **operator gate**. Slugs are identifiers; identifiers ripple into paths, manifests, and future asset records' `module_id` refs. B should emit the *proposed* slug table (the brief's §2.1 table is a fine draft) as a reviewable artifact and stop. Also flag the mundane reality: the PHS 620 syllabus is a Confluence-exported `.doc` — parsing it is real work, and if it resists clean extraction, that's a *gap-ledger entry*, not a blocker (which is itself a nice early proof of §1.5).

**Amendment 3 — Story C is schema + boundary contract only, with the projector-family exclusion stated in the AC.** C's deliverable is the record shape, the status vocabulary (source_grounded/partial/inferred/missing/required_gap/draft_gap_fill/needs_sme_review — good enum, keep it), and the documented "when does a source become a canonical record" boundary. No content generation, no projection. The `kind` list starts minimal — see Q3 note below.

**Sequencing:**

1. **Formal S7 Phase-1 party close first.** It's pending, it's cheap, and Phase-2 stories will cite Phase-1's live evidence — close the books before opening new ones. Governance hygiene, not busywork.
2. **Story A** (registry + guard + manifest scan) — the guard is the safety precondition for everything after.
3. **Stories B ∥ C** — genuinely independent: B works the two syllabi, C works the record schema. Parallelizable if capacity allows.
4. **Story D** (input bundle prototype) — consumes A/B/C outputs; ends at "the bundle exists and Irene *could* receive it," not at Irene actually replanning.
5. **The selection-edge spine** stays where the positioning doc put it: its own arc, after D (which defines its input) and interleaved with S8 (prose arc) per operator priority. D is deliberately the last story that can land before the spine becomes buildable — that's the right handoff point.

And per the round's framing: **the spec should not freeze until the operator's additional notes land.** A/B/C/D scoping can be drafted now; freeze after the notes. *(Superseded by operator directive after the round: notes indefinitely deferred; spec proceeds — see header.)*

### 3. The §6 questions

**Q1 — smallest registry/manifest shape.** Boring technology answer: **scope is a function of path position, not a modeled entity.** `sources/course/` → course scope; `sources/shared/` → shared; `modules/<m>/sources/` → module; `modules/<m>/lessons/<l>/` → lesson. The registry then needs only: two committed declaration files (`course.yaml`: course_id/code/title, SME identity, expected module count, runtime_contract; `module.yaml`: module_id/slug/title/module-LOs/provenance), two small Pydantic v2 models mirroring the existing `app/models` discipline, and **one read-only scanner** that walks the container, computes scope from path, and reconciles declaration against disk — reporting drift as gap entries, not silently trusting either side. No database, no enrollment, no terms, no grading, no calendar. If a proposed field doesn't serve source management, provenance, lesson planning, or gap detection, it's LMS creep (§5.1) — strike it. Syllabus *policies* stay raw source material, referenced by the manifest, never modeled.

**Q2 — committed vs generated.** Both, with a strict ownership split, and the split is the point: **declarations are committed and human-owned** (`course.yaml`, `module.yaml` — the operator's statement of intent); **observations are generated and machine-owned** (the source manifest and gap ledger — deterministic scan artifacts with stable ordering and content digests, matching the envelope/digest discipline already in the substrate). Never hand-maintain a manifest — hand-maintained inventories rot within two sessions, and a rotted manifest is worse than none because downstream code trusts it. Generated manifests get *committed as evidence snapshots* at review points (the existing live-proof evidence pattern), not maintained as living files. Human judgments about gaps (dispositions, "requested from SME," waivers) go in a small committed overlay or the declaration — never edited into the generated file.

**Q5 — the hard guard.** One authoritative choke point, enforced at both entries — this substrate has already taught us the two-walk lesson about single-entry enforcement. The mechanism: a pure function, call it `assert_lesson_corpus_leaf(input_dir)`, that **fails loud if the supplied directory (or any ancestor within the container, cheaply checkable) contains a container sentinel — `course.yaml` or `module.yaml`**. Sentinel-file detection is the boring, robust choice: it needs no registry lookup, no configuration, and it protects against containers the registry has never heard of. Wire it into (a) trial-launch validation in `app/marcus/cli/trial.py` where the corpus path is accepted, and (b) the corpus-dir walk in `g0_enrichment_wiring.py` before recursive ingestion. The registry's `runtime_contract` block is the *declared* policy; the sentinel check is the *enforced* mechanism — declaration alone is not a guard. Error message names the lesson-leaf contract and points at the brief. Fail-loud, never warn-and-proceed.

**Q6 — multi-SME fields now vs deferred.** **Now:** SME identity only — `sme_id`, display name, role, attribution string, owning-course link. That's everything the registry, manifests, and provenance need. **Deferred to the styleguide/approval-routing story** (the surviving half of `course-and-sme-registry`): voice profile, styleguide binding, per-SME approval routing, per-SME model/voice config. **One thin exception that must land now:** per §5.5, any code path that resolves a styleguide while carrying a non-Tejal SME identity must emit an **explicit, recorded fallback marker** ("tejal-styleguide-fallback: no styleguide bound for sme=aziz-nazha") — a gap-ledger entry, never a silent reuse. That's five lines of honesty, not a routing system, and it keeps the deferred story honest when it arrives.

**(Q3, briefly, since C depends on it):** start the `asset_kind` vocabulary at what the two syllabi actually evidence — `reading`, `discussion_prompt`, `assignment`, `assessment`, `lab`, `lecture_material`, `project_artifact`, `syllabus` — closed enum, additive-safe versioned schema per the carrier-robustness directive. `slide_seed`, `script`, `dataset`, `case` wait for evidence.

### 4. Constraint check

- **⛔ SPOC-only / AC-8:** every story above is justified by product robustness (guard protects production; registry serves multi-course; records serve lesson planning), with PHS 620/HAI 510 as *fixtures and evidence*, never targets. If any AC in the drafted spec can only be justified as "so the two seed courses import cleanly," strike it.
- **Lesson-leaf contract (§1.2):** Amendment 1 makes it mechanically enforced, not just declared.
- **Source buckets not asset folders (§1.3):** buckets are optional operator convenience; the scanner treats bucket names as *hints* feeding detection, never as classification authority. Ingestion tags; enrichment canonicalizes.
- **Gap handling core (§1.5):** the status enum is first-class in Story C; the HAI 510 missing reading-list companion should be the *first live gap-ledger entry* — a nice honest proof.
- **Tejal fallback explicit (§5.5):** covered in Q6.
- **SOURCE+LOs KING:** §1.4's LO hierarchy plus B's provenance discipline serve it directly; the residual Irene-input story keeps the operator's ratification authority.

### 5. Dissent, risks, HOLD-for-operator

**Risks:** *Registry-vs-disk divergence* — mitigated by making the scanner a reconciler that reports drift as gaps. *Story C creeping into projection* — mitigated by the explicit exclusion AC. *.doc parsing fragility* — treat unparseable as gap-record, not blocker. *Slug renames rippling through identifiers* — mitigated by Amendment 2.

**HOLD for operator input:** (1) PHS 620 module slug renames — B proposes, operator ratifies. (2) Default disposition of generated manifests (evidence-snapshot-committed vs run-artifact-only). (3) Canonical asset kind list beyond the evidence-grounded core. (4) Spec freeze itself — draft now, freeze only after the operator's additional notes land. *(Item 4 discharged by operator directive — see header.)*

**VERDICT: GO-W-AMENDMENTS** — (1) runtime lesson-leaf guard pulled forward into Story A as its first live-proven deliverable, enforced via container-sentinel check at both trial-launch and ingest-walk entries; (2) Story B is parse-and-propose — slug renames are an operator gate; (3) Story C carries an explicit "not the projector family" exclusion AC and a closed, evidence-grounded kind enum; (4) sequencing: formal S7 Phase-1 close → A → B∥C → D → spine, with spec freeze held for the operator's additional notes; (5) amend `course-and-sme-registry` in the deferred inventory to record the identity/styleguide split, and retrigger the Irene-input residue of `course-purpose-and-operator-owned-lo-inputs` on Story D.

---

## §2 John (verbatim)

📋 **John:**

I read the brief and the positioning SSOT side by side. Let me interrogate this like the cold case it almost became — because the spine of the vision was filed "operator-prioritized" on July 7, and twenty-four hours later a new brief walks in centered on folder shapes and manifests. So: who moved the spine, and was it justified?

### 1. Reconciliation — the four filed Phase-2 items vs. the brief

**First question: does the brief re-sequence the spine behind source management?** Read the operator's verbatim vision again: *"The lesson plan is the rationale for everything — it derives from the LOs + course source material + course purpose. The lesson plan directs production into workflows, and it identifies collateral."* That sentence has two halves. **Derives-from** (inputs) and **directs-into** (outputs). The selection edge is the directs-into half. The brief builds the derives-from half. Positioning §3 says it plainly: Irene today plans from "corpus + references only — no course_purpose, no operator-owned governing LO set." A selection edge built now would direct production from an impoverished rationale. That's a demo edge, and AC-8 forbids demo edges.

Second question: was the spine ever sequenced *ahead* of this? No. Its own filed trigger reads "*after S7/S8 prove the workbook end-to-end*" — and S8 (prose arc) hasn't run. The brief isn't demoting the spine; it's filling the derives-from gap while the spine's trigger is still un-fired. **But** — and here's where I stop being generous — §3.4's language is soft: "*should make this input shape explicit enough that future stories can connect...*" "Explicit enough" and "future stories" is how spines die in inventories. I've seen that body before.

**Per-item adjudication:**

| Filed item | Verdict | Why |
|---|---|---|
| `lesson-plan-directs-production-collateral-to-selection-edge` | **UNTOUCHED in scope, AMENDED in binding** | Stays its own arc, still operator-prioritized, still THE spine. Amendment: Story D must end AT the `ComponentSelection` boundary with a **contract test** proving the input bundle is consumable by the selection edge with zero reshaping. Not "explicit enough" — acceptance-tested against `component_selection.py`'s actual input shape. The spine gets filed as the named next arc the moment D closes. |
| `course-and-sme-registry` | **AMEND — split** | Brief §3.1/Story A delivers the registry core. The per-SME voice/styleguide/approval-routing half stays deferred exactly as brief §5.5 and Q6 say. Update the inventory entry: registry-core → Phase-2 Story A; SME-styleguide-routing → deferred with the §5.5 explicit-fallback rule. |
| `course-purpose-and-operator-owned-lo-inputs` | **EXPAND** | Brief §1.4 + §3.4 substantially deliver this: course-level LOs, learner profile, course purpose land as first-class scoped inputs, wired to Irene in Story D. One sharp caveat below (§4, SOURCE+LOs). The operator-*ratification* surface for the LO set is NOT decided here — hold for operator notes. |
| `collateral-projector-family` | **UNTOUCHED** | Nothing in this brief needs a second projector. Canonical asset records are ingestion-side; projectors are enrichment-egress. Trigger unchanged. Do not let Story C scope-creep into it. |

**JTBD ordering ruling:** derives-from before directs-into — but with the D→spine handoff made contractual, not aspirational. That's the ordering that serves "the lesson plan is the rationale for everything," because a rationale with fake inputs isn't a rationale.

### 2. Story split §7 — validated, with amendments and sequencing

The A/B/C/D split is sound. Each story has a distinct job and a distinct risk profile. Do NOT merge A and B — A is deterministic filesystem/schema work; B is syllabus *parsing* (a Confluence-exported `.doc` for PHS 620 — that's a real live-parse risk, and per the incremental-live-testing rule it gets proven early, not at E2E).

**Ratified sequencing I propose:**

0. **S7 + Irene Pass-2 formal party close — FIRST, and it GATES Phase-2 dev dispatch.** It is owed; governance says so; and it's not idle ceremony — the S7 close ratifies the `kind` discriminant and the "producer consumes real CollateralSpec" facts that Stories C and D build directly on top of. Building on an unratified foundation is how you relitigate mid-story. It does NOT gate spec *authoring* — draft the Phase-2 spec in parallel, since operator notes are incoming anyway.
1. **Story A** — registry + manifest scan + gap ledger. Live-proven on both seed containers.
2. **Story B** — syllabus-derived module metadata. Amendment: the PHS 620 slug-rename table is an operator-content decision; parse and propose live, but **hold the folder mutations for operator confirmation**.
3. **Story C** — canonical asset record contract, scoped to the NOW kinds (Q3 below).
4. **Story D** — lesson-planning input bundle, amended per §1 above: ends at the ComponentSelection contract boundary, proven by contract test + one live Irene Pass-1 consumption.
5. **Selection-edge spine** — filed as the named immediate next arc at D-close. It lands *after* Phase-2, *before* anything else competes for it. That's my answer to "where does the spine land": next arc, by name, in the close-out artifact of Story D — not back into the general inventory pool.

### 3. The §6 questions, PM lens

**Q3 — canonical asset kinds NOW vs deferred.** Rubric: a kind earns NOW status only if (a) both syllabi evidence it AND (b) a current consumer or the gap ledger needs it. NOW: `reading` (both courses; feeds workbook S6/further-reading — a live consumer today), `lecture` (didactic material, both), `lab` (HAI's defining structure), `assignment`, `assessment` (feeds the workbook's Exercise/answer-key slots — live consumer), `discussion_prompt` (PHS 620 is discussion-driven, weekly). DEFERRED: `case`, `dataset`, `slide_seed` vs `script` as separate kinds (fold under `lecture` until a consumer distinguishes them), `quiz` as distinct from `assessment`, anything workbook-support-specific. Six kinds, all syllabus-evidenced, two with live consumers.

**Q4 — gap flow and operator surface.** Gaps flow to exactly two places, no new UI: (a) **into the lesson-planning input bundle** as a first-class `gap_ledger` section — Irene must plan *around* declared gaps, not hallucinate past them; (b) **into a committed, reviewable per-course gap artifact** (YAML ledger + human-readable rendering) that **Marcus-SPOC surfaces conversationally at the lesson-plan operator gate** — "here's what this module is missing before I can plan honestly." The operator-facing surface IS Marcus's conversation plus a committed file. Anything fancier is LMS over-modeling (§5.1). And per the coaching rule, gap entries for fetchable material (the HAI reading list, PHS 620's linked pages) should carry an access-coaching note, not just "missing."

**Q7 — smallest honest close proof.** No full course build. The proof is: (1) live registry/manifest scan of **both** containers → two manifests + two gap ledgers, deterministic and committed; (2) **one lesson-planning input bundle per course** — one real lesson leaf from a PHS 620 module, one from an HAI 510 module — each consumed live by Irene Pass-1 (or minimally validated against her input contract if a full Pass-1 is judged too heavy — I'd push for the live Pass-1; cost is not a constraint and the no-mocks rule applies); (3) **one negative proof:** an attempted run from `course_root` / `module_root` is refused by the hard guard (AC-6), witnessed live. Two manifests, two gap ledgers, two bundles, one refusal. Two *materially different* course shapes, zero video, zero Gamma spend. That's honest generalizability, and it's cheap enough to actually run.

Q2, briefly: manifests are **generated deterministically AND committed as reviewed evidence** — both. Q5: enforce `runtime_contract` in the front door itself — refuse any input root that carries `course.yaml`/`module.yaml` without a lesson-leaf marker. Q6: NOW = SME identity fields only (name, course binding, nullable styleguide ref with explicit fallback flag); voice/approval-routing deferred.

### 4. Scope discipline

- **What smells like bookkeeping?** Two things I'm watching. First: PHS 620's assignment point-allocation table and course policies (§2.1). Those are *source material*. No story models grading, points, or policies as structured data — they stay raw in the course pool until a consumer exists. Say so in the spec. Second: manifest field creep — §3.2's list is already at the ceiling; the spec adds nothing without a named consumer.
- **AC-8 check:** these are two REAL courses with real faculty, one of them the operator's own. This is the product's actual content, not a proofing vehicle. Clean.
- **SOURCE+LOs are KING — one genuine friction point.** Brief §1.4 says lesson-level objectives "may be authored or derived during lesson planning." The binding rule says Irene refines LOs → lesson plan **with operator**. Derived lesson LOs must enter the record as `inferred` / `needs_sme_review` in the same status vocabulary as everything else — never silently promoted to `source_grounded`. That's an amendment, not a rewrite; otherwise the brief *strengthens* the KING rule — it finally gives sources and LOs a first-class, reliably-accessed home under Marcus-SPOC ownership.

### 5. Dissent, risks, holds

**Dissent I anticipate and reject:** someone at this table will want to fold the selection edge into Phase 2 "since we're right there." No. That's how a four-story substrate arc becomes an eight-story swamp. The contract test at Story D's boundary is the concession; the edge stays its own arc.

**Risks:** (1) The PHS 620 `.doc` — parse it live in Story B's first days, not at close. (2) The S7 formal close drifting under "notes first" — that's why I gate dev dispatch on it. (3) Gap-ledger status vocabulary (§1.5's six states) and asset-record status (§3.3's seven states) are two overlapping enums — **unify them in Story C** or we'll pay a migration later.

**HOLD for operator input:** (1) PHS 620 module folder renames. (2) HAI 510 companion reading list — file as gap + request from operator; do not scrape or infer it. (3) Lesson-leaf granularity inside `modules/<slug>/lessons/` — how modules subdivide into runnable lessons/parts is the operator's call. (4) The operator-ratification surface for the governing LO set. (5) Which course is the first *production* target after the close proof.

**VERDICT: GO-W-AMENDMENTS** — (1) S7 + Irene Pass-2 formal party close executes FIRST and gates Phase-2 dev dispatch (not spec authoring). (2) Story D hardens to a contract-tested `ComponentSelection`-boundary handoff; selection-edge spine filed by name as the immediate next arc in D's close-out. (3) Inventory updates: split `course-and-sme-registry`; mark `course-purpose-and-operator-owned-lo-inputs` expanded-by-brief with ratification surface held for operator. (4) Story C scoped to six NOW kinds; unify gap-status and asset-status vocabularies. (5) Derived lesson-level LOs always enter as `inferred`/`needs_sme_review` — never silent `source_grounded`. (6) Story B holds folder renames for operator confirmation; parses the PHS 620 `.doc` live early. (7) Close proof ratified as: 2 manifests + 2 gap ledgers + 2 live Irene-consumed input bundles + 1 live root-refusal negative proof. No full course build.

---

## §3 Murat (verbatim)

🧪 **Murat:** I've read the brief and the ratified SSOT. Grounding note before I start: the SSOT's §3 table is what makes this brief testable at all — "varied-content ingestion ✅ proven, enrichment 🟡 one projector, multi-course/multi-SME 🔴 nothing" — so every witness I spec below is calibrated against what is actually proven versus designed. Here is my full position, point by point.

### 1. Witness shapes per story, and the concrete Q7 answer

**Story A — registry + manifest scan.**
- *Offline (RED-first):* unit suite on the registry loader. Parse `course.yaml`/`module.yaml` for both seeded containers; schema validation fails loud on missing/malformed fields; scope classification round-trips; `runtime_contract` block parses and is honored; empty `sources/` and `lessons/` dirs produce **gap entries, not crashes** — the seeds are mostly scaffolding today, so §1.5 gap handling is exercised for real on day one, not simulated.
- *Live-safe close proof:* run the real scanner entry over the two **real** containers on disk (deterministic, zero API spend), emitting `manifest` + `gap-ledger` into an evidence dir. Assert: PHS 620 manifest shows 15 modules, HAI 510 shows 4; the `.doc` syllabus appears with a detected kind and an honest ingestion status; gap ledger is non-empty (empty source dirs).
- *Non-negotiable AC inside A:* the broad-root refusal guard and its witness. A registry that can *read* course roots without teeth that stop the runtime from *ingesting* them is half a story.

**Story B — syllabus-derived module metadata.**
- *Offline:* parse tests over committed derived-text fixtures of both syllabi. Every emitted metadata field carries a `source_ref` anchor (syllabus path + row/section). A module with no syllabus row yields `status: missing` — **never an invented title**. That is the anti-fabrication assertion, and it must be a test, not a guideline.
- *Live-safe:* run against the real syllabus files. PHS 620's legacy `.doc` is the robustness witness: the run must end in exactly one of two states — sentinel-verified extraction (e.g., the extracted text contains "Teaching Learning Seminar" and yields 12 course LOs) or an explicit `format_unsupported` gap record. A third state — mojibake silently entering metadata — must be asserted impossible. Cross-course assertion: 15 metadata records vs 4, slugs matching the brief's tables.

**Story C — canonical asset record contract.**
- This is a **schema-shape story**. Per CLAUDE.md, the pydantic-v2 checklist and the schema-story scaffold apply: closed enums on `asset_kind`/`status` with triple-layer red-rejection, `validate_assignment=True`, round-trip serialization, shape-pin tests.
- *The teeth test I insist on:* a record with `status: source_grounded` and empty content-bearing `source_refs` must **fail validation**. That single constraint is the schema-level enforcement of §5.4. And a syllabus row is evidence-of-requirement, not content: records derived from syllabus rows alone must carry `status ∈ {missing, required_gap, inferred}` with the syllabus anchor as the *requirement* ref, never `source_grounded`.
- *Live-safe:* enrichment emits records from real HAI 510 syllabus rows and — because the `sources/` dirs are empty — assert **zero records claim `source_grounded`**. The seeded emptiness makes this a genuinely honest witness: the honest answer today is "everything is a gap," and the suite proves the system says so.

**Story D — lesson-planning input bundle.**
- *Offline:* bundle assembler over A+B+C outputs; schema-valid; **scope-preservation assertions** (course LOs and module LOs remain distinguishable — no flattening into one corpus blob); gap ledger rides inside the bundle.
- *Live-safe:* bundles for one module of each course land on disk, schema-valid, and **reproducible** — run twice, stable-ordered identical output. D closes on that plus a documented consumption seam. I explicitly dissent from any attempt to close D by wiring Irene to consume new fields — `course_purpose` as an Irene input and the `collateral → ComponentSelection` edge are Phase-2 backlog items 3 and 1 in the SSOT §4, each its own arc. A live Irene Pass-1 smoke is optional color, not the close witness.

**Q7 — the first live proof of generalizability, concretely:** One command (the Story A/B scanner), run twice, once per course root. What lands on disk:

```
evidence/s7p2-two-course-scan-<ts>/
  phs-620/  manifest.yaml  gap-ledger.yaml  module-metadata.yaml
  hai-510/  manifest.yaml  gap-ledger.yaml  module-metadata.yaml
  broad-root-refusal.log        # captured typed refusal, nonzero exit
  negative-control.log          # non-course dir → "not a course container"
```

Scripted deterministic assertions: (a) 15 vs 4 modules — asymmetric outputs matching ground truth; (b) both syllabus formats represented (`.doc` honest-gap-or-verified, `.docx` extracted); (c) every module title provenance-backed or an explicit gap; (d) zero `source_grounded` content records; (e) the broad-root refusal fired before any ingestion; (f) a grep-witness that no `phs`/`hai` literal appears in the source diff — same code, two materially different structures. That is generalizability demonstrated without building a single deck, and it is the right shape: long-academic-`.doc` vs short-PD-`.docx` is exactly the variance axis the operator seeded.

### 2. Risk ranking of the danger zones

**R1 — §5.3 recursive ingestion. Highest, and it is not hypothetical.** The ingest path is a generic recursive corpus-dir walk, and we have just placed broad, nested, semantically-heterogeneous roots on disk. Point a run at `courses/hai-510/` and it will happily ingest COURSE.md + syllabi + module scaffolding as one corpus blob — silent semantic corruption feeding an expensive live run that produces *plausible* garbage. The `course.yaml` `runtime_contract` stanza is **documentation, not a guard** — YAML declaring "do_not_run_from" enforces nothing. *Teeth:* the ingest entry refuses when a container sentinel exists at or above the supplied input root — a typed error (e.g., `NonRunnableScopeError`) raised **before any node executes and before any API client is constructed** (fail before spend). *Witness:* a test that points the **real production entry — the same one live runs use, not a test helper** — at the real HAI 510 course root and at a module root, and asserts loud typed failure with zero ingestion side effects; plus the positive control that a genuine lesson leaf still runs. And one substrate-specific trap: `production_runner` has **two node walks** (known gotcha — the start walk stops at G1). The guard sits where ingestion begins, and the witness must exercise the walk that live runs actually enter, or we will have offline-green teeth that never bite.

**R2 — §2.1 the legacy `.doc`. Second, because the hazard instance already sits on disk.** No evidence anywhere that any current reader parses legacy `.doc` — the proven ingest path is a *text* decode walk with resilient fallbacks, which against a binary format yields exactly the failure mode I rank highest in ingestion: **mojibake silently admitted as content.** Disposition: for Phase-2 this is a **gap record, not a build item** — the scanner classifies `.doc` as binary/legacy, emits `format_unsupported` with provenance, and a test asserts no decoded text from that file ever enters metadata or corpus. Whether to *build* an extractor (new dependency) versus adopt a convert-to-`.docx`-on-intake policy is an operator call — I hold it.

**R3 — §5.5 silent Tejal-styleguide fallback. High severity, latent likelihood in Phase-2 scope.** No SME entity exists in code; the styleguide roster is hardcoded to one faculty. Phase-2 stories A–D generate no decks, so the exposure is deferred — but Story D's bundle must not quietly embed a Tejal styleguide reference for an Aziz Nazha course. *Witness:* resolve styleguide for `sme != tejal` and assert the result is either an **explicitly marked fallback** (`fallback: true` + reason) or a `sme_styleguide_missing` gap-ledger entry — never a bare Tejal guide id presented as native. This test lands in Phase-2; the moment any production run touches HAI 510, this risk is promoted to R1 and full `course-and-sme-registry` becomes prerequisite, per its own trigger.

**R4 — §5.4 syllabus over-trust / gap-ledger honesty. Real but mostly design discipline.** What makes a gap record trustworthy evidence rather than fabrication — four properties, all testable: (1) **Provenance:** every gap carries an anchor to the evidence that *implies* the requirement. (2) **Re-derivability:** gaps are computed by set-difference between declared/implied requirements and the enumerated manifest, and both sides land in the same evidence dir. (3) **Determinism:** re-running the scan produces an identical ledger — the frozen-judge principle applied to gap detection. For Phase-2 the derivation path is deterministic code, **no LLM in the loop**; if later enrichment uses LLM tagging, those entries take `status: inferred` + review-required, never parity with deterministic gaps. (4) **Schema teeth:** the Story C constraint closes the fabrication route at the record level.

### 3. §6 Q2 — committed vs generated manifests, from an evidence lens

**Both, with a drift gate — and a strict split of ownership.** `course.yaml`/`module.yaml`: **committed, human-declared authority.** Source manifests: **generated deterministically, committed as snapshots** — with a check script (same pattern as the existing pipeline-manifest L1 check) that **regenerates the manifest from disk and diffs against the committed snapshot, failing loud on any delta.** Runs in the offline suite and at story gates. Without this, "committed" is a lie waiting to be discovered. Declared fields and detected fields must be structurally separated so regeneration never clobbers human input. **Gap ledgers: generated-only**, landed in timestamped evidence dirs. Committing gap ledgers invites staleness the instant the operator drops a file into `sources/` — a stale committed gap ledger is precisely the fabricated-evidence failure §5.4 warns about.

### 4. Sequencing — S7 close before Phase-2 dispatch?

**Position: YES — formal S7 + Pass-2 close is a hard precondition for Phase-2 DEV DISPATCH. Spec authoring and this ratification round may proceed in parallel; dev may not.** Three reasons: (1) The recover witness (trial `4c64db93`) has **no party concurrence yet**, and the witness workbook carries a known open red — the `numeric_audit=FAIL` word-form numeral. Dispatching Phase-2 dev on top of an unratified predecessor witness is compounding unverified claims. We do not build the second floor while the first-floor inspection is pending. (2) The numeric_audit finding's resolution directly informs Story C's status semantics for artifacts that ship with known audit reds. (3) The close is cheap — hours. There is no schedule argument against it, so the integrity argument stands unopposed.

### 5. Baseline hygiene with new corpus fixtures — confirmed, with two additions

The causation-isolation rule applies unchanged: score by **(reds ON ∖ reds OFF)** against the ~81–82 pre-existing baseline ledger, with every symmetric-difference red re-run isolated (`-n 0`), never by raw counts. Two corpus-fixture-specific extensions: (1) **Fixture-inertness witness.** Files under `course-content/courses/` are visible to any existing test that globs or walks that tree — and the baseline already contains a **docx-stray** red category, which new `.docx`/`.doc` fixtures can perturb. So each story that adds fixtures runs the pre-existing tree with **fixtures only, no code diff**, and must score zero delta versus baseline. (2) **Pinning against operator-mutable containers.** The two seeded containers are simultaneously live operator working directories and test evidence. Assertions like "`sources/` empty ⇒ gap emitted" go stale the day the operator drops in a reading list. Rule: brittle content assertions run against **frozen fixture copies**; the real containers are reserved for live-safe evidence runs asserting only structural invariants. And the baseline-red ledger gets re-snapshotted at each story open so close reports cite ledger diffs, not totals.

### 6. Dissent, risks, holds for operator

**Dissent (stated plainly):** Story D must not be pressured into proving itself via Irene consumption of new inputs or any workflow-selection wiring. D's honest close is schema-valid reproducible bundles + a documented seam. I will vote against any AC that smuggles the derivation edge into D. And the `runtime_contract` YAML stanza must not be accepted as satisfying AC-6 — declaration without a refusal guard at the real entry, with a fail-loud witness, is the definition of a gate without teeth.

**Risks to carry:** dual-use of the seeded containers (operator workspace + evidence substrate); the two-walk `production_runner` gotcha — the guard witness must cover the walk live runs actually enter.

**HOLD for operator input:** (1) **`.doc` disposition:** build an extractor vs convert-to-`.docx`-on-intake policy. Until decided, `.doc` = explicit `format_unsupported` gap. (2) **PHS 620 slug renames** — content-naming is operator authority, and renames churn every provenance ref — do it once, before Story B closes, not iteratively. (3) **HAI 510 companion reading list** — requesting/fetching it is a source-acquisition action only the operator can take; filed as a gap-ledger entry now either way.

**VERDICT: GO-W-AMENDMENTS** — (1) Formal S7 + Pass-2 close before Phase-2 dev dispatch; spec work may parallel. (2) Story A carries the broad-root refusal guard as a non-negotiable AC: typed fail-loud refusal at the real production entry, before any ingestion or API-client construction, witnessed against real course and module roots, covering both runner walks. (3) `.doc` handled as explicit `format_unsupported` gap with a no-mojibake witness; extractor-vs-convert decision held for operator. (4) Manifest policy: declared YAML committed; source manifests generated + committed snapshot + regenerate-and-diff drift gate; gap ledgers generated-only into evidence dirs. (5) Story C designated a schema-shape story with the `source_grounded`-requires-content-refs validation as mandatory teeth. (6) Fixture-inertness witness required for every story adding files under `course-content/courses/`. (7) Non-Tejal styleguide resolution must return marked-fallback-or-gap with a witness test landing in Phase-2, and becomes a blocking prerequisite before any HAI 510 production run.

---

## §4 Amelia (verbatim)

💻 **Amelia:**

Spot-checks done. Everything below is verified against HEAD, not against the SSOT's citations — two of which are stale (noted in §5).

### 1. Ground-truth: brief §3 shapes vs. substrate

**3.1 Course-source registry — genuinely NEW, but the input side is already seeded.**
- EXISTS: the two containers themselves. `aziz-nazha-hai-510-generative-ai-in-healthcare/course.yaml` carries `schema_version: 0.1`, `course_id`, `sme.name`, `course.{code,title,module_count_expected}`, `source_references`, a full `modules:` list, `status`, and the `runtime_contract` block verbatim per brief §1.2. PHS 620's `course.yaml` carries the same **minus `source_references` and the `modules:` list** (its 15 `module.yaml`s are `module_id: module-01 / title: TBD / status: placeholder`). So the operator seeded a de-facto v0.1 schema — the registry's job is to *validate and read* it, not invent it.
- NEW: zero code reads these files. `grep course.yaml` across `app/` — no hits. The only course handle in the runtime today is `_course_key()` at `app/marcus/cli/trial.py:248-255` (normalized corpus *path* as identity — a path, not an entity).
- SEAM: new package `app/marcus/course_source/` (`models.py`, `registry.py`, `manifest_scan.py`). Do NOT put it in `app/marcus/lesson_plan/` — that package is 30+ modules of run-time plan machinery and contains `composition.py`, which sits in `block_mode_trigger_paths` (`state/config/pipeline-manifest.yaml:83`). A sibling package keeps the diff physically incapable of touching lockstep paths.
- TIER: **Tier-1 clean.**

**3.2 Source manifest + provenance — NEW, with two reusable precedents.** (a) deterministic enumeration + content hashing already single-sourced — `_walk_corpus_files` (`app/composers/section_02a/composer.py:34-43`) + `file_content_hash`/`corpus_fingerprint` usage at `g0_enrichment_wiring.py:433-443`; (b) the generator+committed-derived-artifact convention — `scripts/utilities/generate_capability_overlay.py` → `state/config/capability-overlay.yaml`. The scan is read-only filesystem + hash — live-safe by construction.

**3.3 Canonical asset records — NEW model family, exact pattern already on disk.** `app/marcus/lesson_plan/collateral_spec.py` is the template to mirror — `ConfigDict(extra="forbid", validate_assignment=True)`, closed enums with triple red-rejection, `OPEN_ID_REGEX_PATTERN` reuse, verbatim-text rules. `produced_asset.py`, `source_point.py`, `source_type.py` in the same package already model asset/source identity — Story C must check them first so `asset_kind`/`source_refs` don't fork an existing vocabulary (`g0_enrichment_wiring.py:396-413` `_TYPE_KEYWORDS` already names `discussion_forum`, `assignment_instructions`, `exercise_lab`, `reference_citation` — reuse those kind strings, don't mint new ones). TIER: Tier-1.

**3.4 Lesson-planning input bundle — PARTIAL substrate, the edge stays out of scope.** EXISTS: `G0EnrichmentResult`, one projector, Irene's emitted `CollateralSpec`, the intake seam `app/marcus/intake/pre_packet.py` + `lesson_plan/step_05_pre_packet_handoff.py`. NEW: the bundle model + builder. The SSOT §3 is correct that nothing derives `ComponentSelection` from the plan — `app/marcus/cli/front_door.py:136-194` resolves a static catalog pick from `bundle_catalog.py:209-238` (all three bundles hardcode `required_inputs=("corpus_path",)`), and `app/models/state/component_selection.py:1-14`'s own docstring says the plan *should* select. Story D must NOT build that edge. TIER: Tier-1 **iff** D stops at artifact construction. The moment it wires into Irene dispatch or touches `composition.py`/`component_selection.py`, it's a Tier-2 governance event. Write that as a hard AC.

**Stories A-C: yes, Tier-1, zero pipeline-manifest edits.** D: Tier-1 with the fence above.

### 2. §5.3 recursive-ingestion guard — ONE chokepoint, contract readable in place

There is exactly **one enumeration function** and every corpus consumer funnels through it: `_walk_corpus_files` at `app/composers/section_02a/composer.py:34-43` (`sorted(corpus_dir.rglob("*"))` — this is the recursion the brief fears). Callers: (1) `compose_and_write` (`cli_adapter.py:31`) ← `trial.py:386` — START walk, G0 directive composition. (2) `g0_enrichment_wiring._enumerate` (`g0_enrichment_wiring.py:421-430`) ← `production_runner.py:2656` (START walk) **and** `production_runner.py:3383` (CONTINUATION walk).

A guard **inside `_walk_corpus_files`** lands in all three call sites and both walks automatically — the two-walk trap is defused by construction. Guard logic, no new plumbing: the function already holds `corpus_dir: Path`; refuse when `(corpus_dir / "course.yaml").exists()` or `(corpus_dir / "module.yaml").exists()` or `(corpus_dir / "modules").is_dir()` — raise `DirectiveCompositionError` naming the `runtime_contract`. **Yes, brief §1.2's block is readable right there** — PyYAML is already a dependency; one `yaml.safe_load` for the error message, marker-file presence alone is sufficient for the refusal itself. Belt-and-suspenders: a second, friendlier check at the CLI seam `trial.py:375-381` (the existing `--input must point to a corpus directory` fail-loud block is the exact precedent — extend it). `composer.py` is NOT in `block_mode_trigger_paths` → the guard is Tier-1. A lesson leaf under `lessons/<slug>/` contains neither marker — passes.

### 3. §6 Q1/Q2, implementation lens

**Q1 — smallest shape:** Pydantic v2 family in `app/marcus/course_source/models.py` mirroring `collateral_spec.py` idioms: `CourseRecord`, `ModuleRecord`, closed `SourceScope = Literal["course","shared","module","lesson"]`, `SourceManifestEntry`, `GapEntry`. Loader = YAML read-through (`registry.py::load_course(course_root) -> CourseRecord`), no cache, no DB, no LMS. Validate `schema_version: "0.1"` as seeded. Both — models AND yaml-on-disk — because the operator hand-authors the yaml and the models are the red-rejection surface.

**Q2 — committed vs generated:** repo convention is **generator + committed derived artifact with a staleness check** (`generate_capability_overlay.py` → `capability-overlay.yaml`; contrast the wart: the coverage-manifest JSON that regenerates out-of-band and drifts). Answer: **both, split by authorship.** `course.yaml`/`module.yaml` = committed, operator-authored declarations (already true). Source manifest + gap ledger = **generated, deterministic, committed under the course container** (e.g. `<course-root>/source-manifest.yaml`) carrying per-file `file_content_hash` so staleness is self-evident and re-scan is idempotent. Do NOT add them to `block_mode_trigger_paths` — course content is not pipeline substrate.

### 4. Story split A-D — validation + amendments

- **A (registry + manifest scan): RIGHT-SIZED.** RED-first: fixture = the two real containers; asymmetry is a feature — PHS 620 has no `modules:` list and `title: TBD` placeholders, HAI 510 is fully enumerated; tests must pass on both. Single-session diff: 1 new package, ~3 modules + tests. **Amendment A-1: fold the §5.3 guard into Story A** — it's ~15 lines in `composer.py` + `trial.py`, satisfies brief AC-6, and A is the story that defines the marker files the guard keys on.
- **B (syllabus-derived metadata): TOO FAT AS WRITTEN — split.** The reader problem is smaller than feared but real: HAI 510 syllabus is genuine `.docx` → `python-docx>=1.1` already ships (`pyproject.toml:24`, proven importable — `workbook_producer.py:49` uses it write-side today). PHS 620 `PHS 620 Syllabus 2025.doc` is **not binary Word — I read its first bytes: it's a MIME/MHTML Confluence export** (`Date: Wed, 8 Jul 2026... Message-ID:`), parseable with stdlib `email` + an HTML strip. **Zero new dependencies.** But B bundles extraction + 15 directory renames + `module.yaml` rewrites + bucket scaffolding. Amendment B-1: **B = extraction only** — parse both syllabi → provenance-carrying metadata *proposal* artifact. Amendment B-2: **application of proposals (git-mv of 15 module dirs + yaml updates) is a separate operator-gated leg**.
- **C (canonical asset contract): RIGHT-SIZED**, pure models + tests off the `collateral_spec.py` pattern. Amendment C-1: AC requiring kind-vocabulary reconciliation with `g0_enrichment_wiring.py:396-413` and `source_type.py` — no forked enums.
- **D (input bundle prototype): RIGHT-SIZED ONLY with the fence.** Amendment D-1: explicit negative AC — "diff touches none of `composition.py`, `component_selection.py`, `bundle_catalog.py`, `front_door.py`, any `block_mode_trigger_paths` entry."
- **Ordering: A → {B, C in parallel} → D.**

### 5. Dissent, risks, operator holds

- **Stale citations (errata, minor):** the SSOT §3 / party prompt cite `app/marcus/orchestrator/front_door.py` and `app/marcus/lesson_plan/component_selection.py`. Actual: `app/marcus/cli/front_door.py:136-194` and `app/models/state/component_selection.py`. Conclusions unchanged; spec author must cite the real paths.
- **Risk — guard false-positives:** any historical fixture corpus that happens to contain a `course.yaml` would now refuse to run. I found none, but the guard's RED tests must include the existing proven leaf (`studio-smoke-min` class) as a must-still-pass.
- **HOLD for operator #1 — PHS 620 module renames:** apply the §2.1 slug table only after operator review of the extraction artifact. These are his seeded folders.
- **HOLD for operator #2 — HAI 510 companion reading list:** a gap-ledger row Story A can emit, but *requesting the source* is an operator action.
- **HOLD for operator #3 — multi-SME/styleguide fields:** `state/config/gamma-style-guides.yaml:39` theme name is literally `2026 HIL APC Tejal` — single-faculty confirmed. Registry stores `sme.name` (already seeded) and nothing more.
- **Dissent (mild) vs. brief §3.3 openness:** the brief's `asset_kind: <...|...>` reads open-ended. Ship it as a **closed enum** at v0.1. Open string kinds are how the LMS-creep of §5.1 starts.

**VERDICT: GO-W-AMENDMENTS** — A-1 (fold lesson-leaf guard into Story A at `_walk_corpus_files`), B-1/B-2 (Story B = extraction-only; module-dir renames become an operator-gated application leg), C-1 (kind-vocabulary reconciled with existing registries, closed enum), D-1 (negative-AC fence keeping D off all `block_mode_trigger_paths`; no `collateral→ComponentSelection` edge). Ordering A → {B,C} → D. All four land Tier-1 under these amendments.

---

## §5 Consensus synthesis (orchestrator)

**4/4 GO-W-AMENDMENTS. No impasse; no Quinn/John escalation needed.**

### §5.1 Reconciliation ruling (unanimous)

| Filed Phase-2 item | Ruling |
|---|---|
| `lesson-plan-directs-production-collateral-to-selection-edge` | **UNTOUCHED in scope, HARDENED in binding** — stays its own arc, THE spine; Story D must end at the `ComponentSelection` boundary with a **contract test** against the real input shape (`app/models/state/component_selection.py`); the spine is **filed by name as the immediate next arc in Story D's close-out artifact** (John), not returned to the general pool. |
| `course-and-sme-registry` | **SPLIT** — trigger has FIRED (two courses/SMEs on disk). Identity core (course/SME identity, module list, source pools, runtime contract) → **Story A**. Voice/styleguide/attribution/approval-routing half stays deferred with its own trigger + the §5.5 explicit-fallback rule (blocking prerequisite before any HAI 510 production run — Murat). |
| `course-purpose-and-operator-owned-lo-inputs` | **EXPANDED by the brief** (course-level AND module-level LOs first-class). Substrate delivered by Stories B + D; the **Irene Pass-1 signature change + operator LO-ratification surface stay filed**, re-triggered "after Story D lands." |
| `collateral-projector-family` | **UNTOUCHED** — hard boundary: asset records = source EVIDENCE (input-side); projectors = generated FORMS (output-side). Story C carries an explicit exclusion AC. |

### §5.2 Ratified program shape + sequencing

**0.** Formal S7 + Irene Pass-2 close — **gates Phase-2 dev dispatch** (not spec authoring). → **1.** Story A (registry + manifest scan + gap ledger + **the broad-root refusal guard**, live-proven first). → **2.** Stories **B ∥ C** (independent; parallelizable). → **3.** Story D (input bundle, fenced). → **4.** Selection-edge spine = named next arc at D-close (with S8 prose arc interleaved per operator priority).

Ratified amendments (all folded into the spec):
- **A-1 (Amelia/Winston/Murat):** the lesson-leaf guard lands in Story A at the single chokepoint `_walk_corpus_files` (`app/composers/section_02a/composer.py:34-43`) — covers all three call sites + BOTH runner walks by construction — plus a friendly CLI-seam check at `trial.py:375-381`. Typed fail-loud refusal (container sentinels `course.yaml`/`module.yaml`/`modules/`) **before any ingestion or API-client construction**; witnessed live against real course + module roots + positive control on a proven leaf (`studio-smoke-min`-class must-still-pass).
- **B-1/B-2 (Amelia/Winston/John):** Story B = **extraction only** (both syllabi → provenance-carrying metadata *proposal* artifact; per-field `source_ref`; anti-fabrication test: missing syllabus row → `status: missing`, never an invented title). **Application of proposals (15 module-dir renames + yaml rewrites) is a separate operator-gated leg B-2.** Finding: PHS 620's "`.doc`" is a MIME/MHTML Confluence export — stdlib-parseable, zero new dependencies; HAI 510 `.docx` readable via already-shipped python-docx.
- **C-1 (Amelia/Winston/John/Murat):** Story C is a **schema-shape story** (pydantic-v2 checklist + scaffold per CLAUDE.md). Closed `asset_kind` enum at v0.1, reconciled with the existing vocabularies (`g0_enrichment_wiring._TYPE_KEYWORDS`, `source_type.py`) — no forked enums. **Unify gap-status and asset-status vocabularies** (John). Mandatory teeth: `source_grounded` with empty content-bearing `source_refs` fails validation; syllabus-row-derived records are `missing|required_gap|inferred`, never `source_grounded`. Derived lesson-level LOs enter as `inferred`/`needs_sme_review`, never silent `source_grounded` (SOURCE+LOs-are-KING). Explicit projector-family exclusion AC.
- **D-1 (Amelia/Murat/John):** Story D = bundle artifact + loader + contract test at the `ComponentSelection` boundary. **Negative AC fence:** diff touches none of `composition.py`, `component_selection.py`, `bundle_catalog.py`, `front_door.py`, or any `block_mode_trigger_paths` entry; no Irene-dispatch wiring; no `collateral → ComponentSelection` derivation. Reproducibility witness (run twice, byte-identical stable-ordered output). Murat dissents in advance against any AC that smuggles the edge into D; John's live-Irene-consumption preference is recorded as **optional color, not the close witness** (Murat's stricter reading adopted — D's close = schema-valid reproducible bundles + contract test + documented seam).

### §5.3 Answers to the brief's §6 questions (ratified)

1. **Q1 smallest shape:** scope = path position, not a modeled entity. Pydantic v2 family in NEW sibling package `app/marcus/course_source/` (`CourseRecord`, `ModuleRecord`, `SourceScope` Literal, `SourceManifestEntry`, `GapEntry`) mirroring `collateral_spec.py` idioms; YAML read-through loader validating the operator-seeded `schema_version: 0.1`; one read-only reconciling scanner (drift → gap entries). No DB, no LMS fields.
2. **Q2 committed vs generated:** split by authorship. Declarations (`course.yaml`/`module.yaml`) committed + human-owned. Source manifests generated deterministically (stable ordering + `file_content_hash`) + **committed snapshot + regenerate-and-diff drift gate** (L1-check pattern). Declared vs detected fields structurally separated. **Gap ledgers: one named divergence — see §5.4.**
3. **Q3 kinds NOW:** closed enum at v0.1: `reading`, `lecture` (incl. lecture_material), `lab`, `assignment`, `assessment`, `discussion_prompt`, plus record-kind `syllabus` and `project_artifact` where evidenced (John's 6 + Winston's syllabus/project rows; final trim at spec authoring). DEFERRED: `case`, `dataset`, `slide_seed`/`script` split, `quiz`-vs-`assessment`.
4. **Q4 gap flow:** two surfaces only — (a) `gap_ledger` section riding the lesson-planning input bundle (Irene plans around gaps); (b) reviewable per-course gap artifact surfaced **conversationally by Marcus-SPOC at the lesson-plan operator gate**, with access-coaching notes on fetchable-material gaps. No new UI.
5. **Q5 hard guard:** container-sentinel refusal at `_walk_corpus_files` (+ CLI seam) — enforced mechanism; `runtime_contract` YAML = declared policy only, explicitly NOT accepted as satisfying AC-6 alone (Murat binding).
6. **Q6 multi-SME now:** SME identity fields only (`sme_id`/name/role/attribution/owning-course). Styleguide binding/voice/approval-routing deferred to the surviving registry half. Thin exception NOW: non-Tejal SME styleguide resolution must yield marked-fallback-or-gap, never silent Tejal reuse.
7. **Q7 first live proof:** Murat's evidence shape ratified — one scanner command run per course root → `evidence/s7p2-two-course-scan-<ts>/` with per-course `manifest.yaml`/`gap-ledger.yaml`/`module-metadata.yaml` + `broad-root-refusal.log` + `negative-control.log`; deterministic assertions (15-vs-4 asymmetry, both syllabus formats honest, provenance-backed-or-gap titles, zero `source_grounded` content records, refusal-before-ingestion, no `phs`/`hai` literals in the code diff). John's fuller variant (+2 live Irene-consumed bundles) noted as the Story-D-close-time extension.

### §5.4 Named divergence (single; adjudicated provisionally, flagged to operator)

**Gap-ledger disposition.** Murat: generated-only into timestamped evidence dirs (a stale committed ledger = fabricated evidence). Amelia: generated + committed under the course container with content hashes (self-evident staleness). Winston/John: committed-snapshot-at-review-points. **Provisional ruling for the spec:** manifests = committed snapshot + drift gate (unanimous); gap ledgers = **generated-only into evidence dirs for Story A**, with a `gap_summary` block allowed inside the committed manifest snapshot (counts + ids only, no full ledger) so review surfaces exist without a stale full ledger. Cheap to flip; **flagged as an operator-notes item** if the operator wants committed full ledgers.

### §5.5 Consolidated HOLD-for-operator register

1. PHS 620 module slug renames (B-2 operator gate — propose first, mutate on confirmation, once).
2. `.doc` long-term policy: extractor vs convert-to-`.docx`-on-intake (moot-ened for PHS 620 by the MHTML finding, but the policy question stands for true legacy `.doc`s); until decided, `format_unsupported` gap.
3. HAI 510 companion reading list acquisition (gap-ledger entry either way).
4. Lesson-leaf granularity inside `modules/<slug>/lessons/`.
5. Operator LO-ratification surface (residue of filed item 3).
6. First production-target course after the close proof.
7. Gap-ledger committed-vs-evidence disposition (§5.4 provisional ruling stands unless overridden).
8. Asset-kind list beyond the evidence-grounded core.

*(Original hold "spec freeze awaits operator notes" discharged: operator indefinitely deferred the notes 2026-07-08 and directed spec completion — notes are minor workbook-content points, which land in the S8 prose arc's lane, not Phase-2.)*

### §5.6 Errata

Positioning SSOT §3 stale citations (conclusions unchanged): `front_door.py` is at `app/marcus/cli/front_door.py` (not `orchestrator/`); `component_selection.py` is at `app/models/state/component_selection.py` (not `lesson_plan/`). The Phase-2 spec cites the verified paths.
