---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-02-party-mode-round-a', 'step-03-create-stories', 'step-03-party-mode-round-b', 'step-03-party-mode-round-c', 'step-04-final-validation', 'step-04-party-mode-round-d-close']
status: 'complete'
completedAt: '2026-04-29'
ratificationLog:
  rounds: 4
  voicesPerRound: 4
  unanimousVerdict: 'RATIFIED-WITH-AMENDMENTS (R(a), R(b), R(c)); RATIFIED-WITH-AMENDMENTS-AND-CLOSE (R(d))'
  scopeFloorAllGreen: true  # SG-1 + SG-2 + SG-3 + SG-4 verified at R(d) close
  reOpens: 0
  amendmentsTotal: 8  # 4 R(a) + 2 R(b) + 2 R(c) + 0 R(d)
draftedAt: '2026-04-29'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-04-29-slab-7b.md
  - _bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md
  - _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md
  - _bmad-output/planning-artifacts/deferred-inventory.md
  - docs/dev-guide/composition-specification.md
  - docs/dev-guide/migration-story-governance.json
  - docs/dev-guide/migration-ac-sandbox-inventory.json
  - docs/dev-guide/bmb-sanctum-alignment-checklist.md
  - docs/dev-guide/sanctum-exception-categories.json
  - docs/dev-guide/operator-control-parity-template.md
  - docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/
  - skills/bmad-agent-cora/SKILL.md
workflowType: 'epics-and-stories'
project_name: 'Slab 7b — Specialist Activation (Eleven-Specialist Roster Body-Activation atop Slab 7a Substrate)'
subject: 'Epic and story decomposition for Slab 7b specialist body-activation'
user_name: 'Juanl'
date: '2026-04-29'
branch: 'dev/langchain-langgraph-foundation'
slabId: 'slab-7b'
parentMigrationPRD: '_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md'
siblingPRDs:
  - _bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md  # CLOSED 2026-04-29 at 95c81b0
plannedSiblingEpicsFiles:
  - epics-doc-slab-7-prose-harvest.md  # post-trial-2 prose harvest; sequenced after first tracked trial-2
fr_count: 26  # FR88-FR113
nfr_count: 24  # NFR-T9..T12 (4) + NFR-CG12..CG20 (9) + NFR-I9..I13 (5) + NFR-OD3..OD6 (4) + NFR-CG14a counted in CG block + 2 splits
adr_count: 10  # D14-D23
sg_count: 4  # SG-1..SG-4 (SG-4 NEW; SG-1/2/3 inherited from 7a)
epic_count: 1
story_count: 12  # Wave 0 + Wave 0.5 governance preconditions are NOT counted as K-units; 12 dev stories across Waves 1-6
standingGuardrails:
  - 'SG-1 (INHERITED from 7a): 11-specialist roster floor (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) — cannot be reduced; enforced via NFR-I7 carry-forward (`len(specialists) == 11` build assertion) + Slab 7b parity-test extension `tests/parity/test_eleven_specialists_addressable.py`.'
  - 'SG-2 (INHERITED from 7a): 33-row mapping checklist floor at `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` — cannot lose rows; Slab 7b targets ~28 row improvements (27 ❌ + 7 ⚠️ → toward ✅), 6 deferred rows accounted for; enforced via NFR-I6 carry-forward + extended parity-test suite + NFR-I11 mapping-checklist row-status invariant.'
  - 'SG-3 (INHERITED from 7a): Composition Spec invariants §3.1 SHA256+append-only / §3.5 gate precedence / §3.6 manifest-declared dependencies / §6 chain-test-per-PR / §9 Composition Smoke gate / §10 Decision Log / §11 migration triggers — enforced structurally by NFR-I8 carry-forward + per-specialist body chain-test PRs.'
  - 'SG-4 (NEW; party-mode-ratified Round 1): every Slab 7b body-activation story MUST either (a) align its `SKILL.md` with the standard BMB sanctum activation pattern matching the Marcus/Irene/Dan/Texas precedent, OR (b) document a structural exception drawn from the closed allowlist `docs/dev-guide/sanctum-exception-categories.json` (initial entry: `sidecar-hook` per Cora precedent), with party-mode consensus recorded in the story planning artifact. Class-D2 (Compositor) is a first-class taxonomy bin per D20 (NOT exception). Enforced via FR101 parity-test + NFR-I9 + NFR-CG18 foundational-artifacts precondition.'
foundationalArtifactsLanded:
  - 'docs/dev-guide/bmb-sanctum-alignment-checklist.md (FR108)'
  - 'docs/dev-guide/sanctum-exception-categories.json (FR109)'
  - 'docs/dev-guide/operator-control-parity-template.md (FR110)'
  - 'docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/ (FR111; path-corrected per Errata 1)'
  - 'skills/bmad-agent-cora/SKILL.md §Sanctum exception anchor (FR112)'
  - 'docs/dev-guide/migration-ac-sandbox-inventory.json +5 entries (FR107: gamma/kling/elevenlabs/wondercraft/dan-api-tbd-pending)'
prdErrataAddendumApplied:
  - 'Errata 1: FR111 path corrected to docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/ (directory; 7 files)'
  - 'Errata 2: FR101 parity-test contract — SKILL.md at skills/bmad-agent-{name}/ (NOT app/specialists/); minimal frontmatter (name + description); BMB alignment marker = sanctum-dir + 6-file pattern (NOT YAML keys)'
  - 'Errata 3: SanctumParityTestBase is a Wave-1 CREATE-task, not pre-existing'
  - 'Errata 4: tests/parity/per_specialist/ subdir does not exist; first Wave-1 parity-test author ratifies subdir-vs-flat convention'
codexDeploymentBoundary:
  claudeAuthors:
    - 'Wave 1 Class-A hardening stories (Texas / Quinn-R / Vera = 3 stories)'
    - 'Wave 2a Class-B Irene Pass-1 refresh (1 story)'
    - 'Wave 5a Class-D1 Dan greenfield (1 story)'
    - 'Wave 5b Class-D2 Compositor greenfield (1 story)'
    - 'Wave 6 integration + parity-suite + closeout (1 story; dual-gate)'
  codexAuthors:
    - 'Wave 0 sandbox-AC inventory PR (FR107; landed pre-Wave-0 atomic merge per NFR-CG17 deviation note)'
    - 'Wave 2b Class-C+ Tracy port-shape + sidecar bundle (1 story)'
    - 'Wave 3 Class-C API-bound port-shapes (Gary / Kira / Enrique = 3 stories)'
    - 'Wave 4 Class-C Wanda port-shape onto scaffold (1 story)'
  codexReviews:
    - 'Every Slab 7b story bmad-code-review (mutual-handoff pattern per Slab 7a precedent)'
metaDirective:
  partyModeRoundsScheduled: 4
  rounds:
    - 'Round (a): epic-shape green-light after Step 2 (epic title + goal + sequencing skeleton)'
    - 'Round (b): story-roster ratification after Step 3 — class-coverage + author-binding (NFR-CG17) + per-wave K-targets'
    - 'Round (c): per-story AC adversarial review after Step 4 — sandbox-AC enforcement + sanctum-alignment AC + parity-test contract + FR coverage'
    - 'Round (d): ratify-with-amendments-and-close at Step 5 — final FR coverage map + sprint-status entries + hot-start update'
---

# Slab 7b — Specialist Activation (Eleven-Specialist Roster Body-Activation): Epic Breakdown

## Overview

This document decomposes the Slab 7b PRD (`prd-slab-7b-specialist-activation-eleven.md`, 26 new FRs + 24 new NFRs + 10 new ADRs + 4 standing guardrails — SG-4 NEW) into **one epic with twelve stories** sequenced strict-serial-with-parallel-waves, plus two pre-Wave-1 governance gates (Wave 0 foundational-artifacts atomic-merge — DONE — and Wave 0.5 Codex deployment verification). The decomposition reflects:

- **Substrate-as-floor invariant** (D22): the eleven-specialist roster activates *into* the Slab 7a substrate (CLOSED 2026-04-29 at `95c81b0`); Slab 7b adds bodies, never amends substrate. Marcus duality boundary at `dispatch_adapter.py:81` (FR113) is frozen.
- **Standing guardrails SG-1/SG-2/SG-3 inherited verbatim** from Slab 7a; **SG-4 NEW** — every body-activation story carries a SKILL.md sanctum-alignment AC; Cora-sidecar precedent for option-b documented exception; Class-D2 sidecar variant (Compositor) is canonical (NOT exception) per D20.
- **Party-mode consensus** on PRD R1-R9 (9 rounds; 0 re-opens; unanimous on R9 close) + this epics-and-stories workflow's 4 rounds (a/b/c/d).
- **Codex parallel-authoring boundary** per NFR-CG17 + D21: 5 Codex-authored stories (Class-C/C+ port-shape) + sandbox-AC inventory PR; 7 Claude-authored stories (Class-A hardening + Class-B refresh + Class-D1 + Class-D2 + integration); Codex reviews every story close (mutual-handoff).
- **Sequenced execution per Phased Wave Plan**: Wave 0 (DONE) → Wave 0.5 (Codex deploy verify) → Wave 1 (3 stories parallelizable) → Wave 2a + 2b (serial) → Wave 3 (3 stories parallelizable) → Wave 4 → Wave 5a + 5b (parallelizable after Waves 1-3 *closed*) → Wave 6 (strict-last; dual-gate).
- **PRD errata addendum applied** (commit `ddcd1b1`): FR111 path correction; FR101 contract realignment; SanctumParityTestBase as Wave-1 CREATE-task; FR105 subdir-vs-flat ratified at first Wave-1 parity-test author.

**Parent migration epics file:** `epics-langchain-langgraph-migration.md` (9 epics / 56 stories at 2026-04-22).
**Sibling epics file (CLOSED):** `epics-slab-7a-inter-gate-orchestration.md` (1 Epic / 8 stories DONE at `95c81b0`).
**Successor planned:** `epics-doc-slab-7-prose-harvest.md` (post-trial-2 anti-pattern catalog + worked examples; sequenced after first tracked trial-2 post-Slab-7b).

## Requirements Inventory

### Functional Requirements (26, extracted from PRD §Functional Requirements FR88–FR113)

The PRD's Functional Requirements section is canonical. Total: **26 FRs across 7 capability sub-areas**. Numbering scheme continues from Slab 7a (FR88+ in the body-activation series). All FRs are `verified-at: 2026-04-29` per PRD errata addendum partial-application policy or T1-readiness re-verification at story-authoring time.

**Capability-Area Coverage (Slab 7b body-activation series):**

| # | Capability Sub-Area | FRs | Count |
|---|---|---|---|
| 1 | Eleven-specialist activation roster (canonical) | FR88 | 1 |
| 2 | Class-A hardening (Texas / Quinn-R / Vera) | FR89, FR90, FR91 | 3 |
| 3 | Class-B refresh (Irene Pass-1) | FR92 | 1 |
| 4 | Class-C / C+ port-shape (Tracy / Gary / Kira / Wanda / Enrique) | FR93, FR94, FR95, FR96, FR97 | 5 |
| 5 | Class-D greenfield (Dan / Compositor) | FR98, FR99 | 2 |
| 6 | SG-4 sanctum alignment per body | FR100, FR101, FR102, FR103 | 4 |
| 7 | Substrate-consumption-extended | FR104, FR105, FR106, FR107 | 4 |
| 8 | Foundational artifacts (Wave 0; DONE) | FR108, FR109, FR110, FR111, FR112 | 5 |
| 9 | Substrate boundary frozen | FR113 | 1 |
| **TOTALS** | | | **26** |

**Full FR text:**

**FR88.** Slab 7b ships eleven specialist body activations covering: Texas (Class A hardening), Irene Pass-1 (Class B activation refresh), Tracy (Class C+ port-shape + sidecar creation), Gary (Class C port-shape), Kira (Class C port-shape), Wanda (Class C port-shape onto scaffold), Enrique (Class C port-shape), Dan (Class D1 greenfield), Compositor (Class D2 greenfield), Quinn-R (Class A hardening), Vera (Class A hardening). Per-specialist Slab-7b shape designation (frontmatter `slab7bSpecialistRoster.specialists.{name}.slab7bShape`) is operator-ratified and binds.

**FR89.** Texas hardening MUST land: live-retrieval-against-real-directive-composer; six-canonical-artifacts contract enforcement (extracted.md / metadata.json / extraction-report.yaml / manifest.json / ingestion-evidence.md / result.yaml); G0 6-dim evidence-sentence rubric; word-count belt-and-suspenders check; cross-validation hint application.

**FR90.** Quinn-R hardening MUST land: two-mode (pre-composition / post-composition) rubric semantics; G2C storyboard-bound shape (`authorized-storyboard.json` write contract); G5 pre-composition QA body (WPM review + VTT monotonicity + coverage completeness + motion-vs-narration duration coherence + advisory-vs-blocking partition).

**FR91.** Vera hardening MUST land: G0 6-dim evidence-sentence rubric on real Texas output; G1 ingestion-quality 6-dim verdicts; G3 fidelity check on real Storyboard A; G4 19-criterion rubric (G4-01 through G4-19) on real Irene Pass-2 output; sensory-bridges dispatch on real motion + audio.

**FR92.** Irene Pass-1 activation refresh MUST land: 9-node scaffold mirroring Pass-2 shape (Slab 2a.2 precedent); lesson-plan coauthoring + scope-lock contract; per-plan-unit ratification surface for G1A; `irene-pass1.md` artifact write; mode-singularity hard-constraint enforcement; `scope_decision.set` + `plan.locked` learning-event emission.

**FR93.** Tracy port-shape + sidecar creation (**Class C+**) MUST land: research-shaped intent enrichment for Pass-2; sidecar greenfield at `_bmad/memory/bmad-agent-tracy/` with full 4-file BMB pattern (INDEX.md / PERSONA.md / chronology.md / access-boundaries.md); 9-node scaffold per Slab 2b.1 TEMPLATE; live LLM-only binding (no third-party API; sandbox-AC inventory entry not required for Tracy specifically); cache-hit-rate harness ≥85% post-warm-up.

**FR94.** Gary port-shape MUST land: Gamma API live invocation; per-slide variant generation (DOUBLE_DISPATCH branch when applicable); theme-handshake; PNG export normalization (`_materialize_exported_slide_paths` carry-forward); Vera G3 invocation hooks; cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR95.** Kira port-shape MUST land: Kling API live invocation; motion generation per `motion_plan.yaml`; per-slide `.progress.json` + terminal `.json` receipts; reviewer inspection pack at `[BUNDLE_PATH]/recovery/inspection/`; fail-closed budget rules; cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR96.** Wanda port-shape onto scaffold MUST land: Wondercraft API live invocation; podcast/audio bed generation scoped into storyboard's audio track; scaffold-v0.2 alignment (closes pre-Slab-2b client-landed-not-on-scaffold gap); cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR97.** Enrique port-shape MUST land: ElevenLabs API live invocation; voice-preview + voice-selection HIL contract (`voice-preview-options.json` + `voice-selection-review.md` + `voice-selection.json` artifact write); manifest-driven narration on locked package; assembly-bundle build (`assembly-bundle/audio/` + `captions/`); per-segment progress to stderr; cache-hit-rate harness ≥85% post-warm-up; live-API-on-CI strict prohibition.

**FR98.** Dan greenfield via `bmad-create-specialist` MUST land: SKILL.md (option-a sanctum-aligned); sidecar at `_bmad/memory/bmad-agent-dan/` with full BMB pattern; `app/specialists/dan/` directory with scaffold-v0.2; `_act` body shaped as narrow-lane creative-director aux contributions threaded across G1–G2; sandbox-AC `dan-api-tbd` inventory entry resolved at story-1 (LLM-only or third-party-API to be determined).

**FR99 (R6 Amelia + Winston + Mary amendment, Class-D2 sidecar variant restated).** Compositor activates per **Class-D2 sidecar variant** of the BMB regime (canonical, NOT exception): persona artifacts live as a sidecar with operational-metadata content (`contract.md`, `version.md`, `chronology.md` recording pipeline-runs, `access-boundaries.md` recording read/write directories) — sidecar carries operational metadata, not persona-shaped continuity. Class-D2 variant is recognized inside the BMB checklist as a first-class activation shape; no `# Sanctum exception` block required. MUST land: SKILL.md aligned per scaffold-v0.2-D2-pipeline contract (FR111); `app/specialists/compositor/` directory; `_act` body shaped as deterministic assembly pipeline; `sync-visuals` operation; `DESCRIPT-ASSEMBLY-GUIDE.md` regeneration; localized stills + motion under `assembly-bundle/visuals/` + `motion/`; pipeline-determinism harness ≥99% rate (bytes-identical for `sync-visuals`; field-masked-hash for `DESCRIPT-ASSEMBLY-GUIDE.md` modulo `{generated_at, run_id, build_timestamp}` per R3 Amelia-amendment).

**FR100.** Every Slab 7b body-activation story MUST carry a `# SG-4 Sanctum Alignment` AC requiring SKILL.md to either align (option-a) with the BMB pattern OR document an exception (option-b) with explicit rationale. Reviewer verifies during `bmad-code-review`.

**FR101 (R6 Winston + Mary + Amelia amendment, R1-contract restated; PRD errata Errata 2 applied).** A structural parity test `tests/parity/test_skill_md_sanctum_alignment.py` MUST exist by Slab 7b close. Test contract (errata-corrected):
- (i) enumerates the eleven-specialist roster from SG-1; asserts each name has `skills/bmad-agent-{name}/SKILL.md` present (missing dir or missing SKILL.md = FAIL, not skip) — **NOTE: SKILL.md lives at skills/bmad-agent-{name}/, NOT app/specialists/{name}/ per Errata 2**;
- (ii) parses each `SKILL.md` frontmatter as YAML; asserts MINIMAL required keys (`name` + `description`) — Errata 2: NOT `agent_name + sanctum_path + activation_order + class enum`;
- (iii) BMB alignment marker is **sanctum-directory existence** at `_bmad/memory/bmad-agent-{name}/` containing the 6-file BMB pattern (INDEX.md / PERSONA.md / CREED.md / BOND.md / MEMORY.md / CAPABILITIES.md), NOT YAML frontmatter keys (Errata 2);
- (iv) for `class: D2` (Compositor), asserts the Class-D2 sidecar variant contract per scaffold-v0.2-D2-pipeline (FR111) instead of sanctum-path-equality;
- (v) for option-b cases (rare; only allowed via party-mode-ratified closed-allowlist), asserts `# Sanctum exception: <category>` heading where `<category>` matches a row in `docs/dev-guide/sanctum-exception-categories.json` (FR109), AND a `## Rationale` subsection ≥80 chars referencing "sanctum activation" or "BMB pattern" by name;
- (vi) cold-activation smoke per A-11 (R3 Quinn FM-25 mitigation) — for each migrated specialist, simulates operator typing `talk to {name}` in fresh session; asserts SKILL.md loads + sanctum batch loads + persona activates without error.

The test references `docs/dev-guide/bmb-sanctum-alignment-checklist.md` (FR108) as canonical alignment authority.

**FR102.** The parity test MUST run at every PR merge gate. A red parity test blocks merge.

**FR103.** A documented sanctum-alignment matrix MUST live at `docs/dev-guide/specialist-sanctum-alignment-matrix.md`, listing every specialist + alignment-or-exception verdict + rationale link. Updated at every Slab 7b body-activation story close. (Operator-doc twin at `docs/operator/specialists/sanctum-alignment-matrix.md` per NFR-OD4.)

**FR104.** Operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md` MUST extend with 11 new rows (one per specialist body activation) by Slab 7b close. Each row enumerates legacy lever(s) → migrated lever(s) → back-compat shim status → end-to-end test asserting the lever changes specialist behavior. Per-specialist operator-control inventory MUST be filed (template at FR110) before that specialist's class enters dev.

**FR105 (PRD errata Errata 4 — subdir-vs-flat ratified at first Wave-1 parity-test author).** Parity-test suite for per-specialist activation contract MUST exist by Slab 7b close, with one test file per specialist following NFR-I10 naming convention `test_<specialist_name>_activation_contract.py`. Path convention ratified at first Wave-1 parity-test author per Errata 4 (recommend flat `tests/parity/test_<specialist>_activation_contract.py` matching existing convention; OR `tests/parity/per_specialist/test_<specialist>_activation_contract.py` if subdir created at Wave-1 Story 7b.1). Per-specialist test pattern is class-shaped: Class-A rubric-semantics parity; Class-B persona-continuity + sidecar-write parity; Class-C live-API + cache-hit-rate parity; Class-C+ adds sidecar-emission parity; Class-D1 first-recorded fixture set; Class-D2 pipeline-determinism parity.

**FR106.** Cache-hit-rate harness MUST be configured for ten LLM specialists (Texas / Irene-Pass1 / Irene-Pass2 / Tracy / Gary / Kira / Wanda / Enrique / Quinn-R / Vera) per T4 cadence + one Compositor pipeline-determinism harness per Class-D2 contract (NOT cache-hit-rate). Parametric configuration (single binary, config-driven). Wall-clock per harness ≈230s × N=10; runs at green-light cadence, NOT in T1/T2 dev-cycle inner loop.

**FR107 (LANDED Wave 0).** Sandbox-AC inventory at `docs/dev-guide/migration-ac-sandbox-inventory.json` extended with 5 entries (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-pending) BEFORE any **API-bound** Class-C / Class-C+ / Class-D Slab 7b story opens (per R5 Amelia-scope-amendment: Tracy + Dan-without-API exempt). Inventory PR is hard precondition for Wave-3+; LANDED in commit `9ed6fcb`.

**FR108 (LANDED Wave 0).** `docs/dev-guide/bmb-sanctum-alignment-checklist.md` exists. Canonical SG-4 alignment authority. Required TOC: §1 Purpose & audience; §2 When to use (T1 / story-close / cold-pickup); §3 Required sanctum artifacts (auto-checkable); §4 Activation-pattern verification (manual-eyeball); §5 Documented-exception pattern (option-b); §6 Worked examples (standard activation + Cora-sidecar paste-pattern); §7 Auto-check script contract (inputs/outputs/exit-code); §8 Glossary.

**FR109 (LANDED Wave 0).** `docs/dev-guide/sanctum-exception-categories.json` exists. Closed allowlist for option-b categories. Initial entry: `sidecar-hook` per Cora precedent. Reviewer + parity-test reference this allowlist to validate option-b SKILL.md exception block category claims.

**FR110 (LANDED Wave 0).** `docs/dev-guide/operator-control-parity-template.md` exists. Per-specialist operator-control inventory template with sections: legacy lever inventory; migrated lever mapping; back-compat shim status; end-to-end test pointer. Each specialist's class-entry-precondition is a filled instance of this template.

**FR111 (LANDED Wave 0; PRD errata Errata 1 applied — path corrected).** `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` exists (directory; 7 files: README.md, scaffold.yaml, field-mask.yaml, contract.md.template, version.md.template, chronology.md.template, access-boundaries.md.template, pipeline-determinism.md.template). Class-D2 pipeline-greenfield scaffold variant — defines sidecar shape (operational metadata), pipeline-determinism contract, field-mask convention. Compositor body activation consumes this scaffold. **Original PRD path `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` superseded.**

**FR112 (LANDED Wave 0).** `skills/bmad-agent-cora/SKILL.md` contains a stable §"Sanctum exception" anchor section (line 59; HTML grep marker `<!-- sanctum-exception:sidecar-hook -->`). Concrete paste-pattern target referenced by FR101 parity-test, FR108 alignment checklist §6.2 worked example, and any future Slab 7b story invoking option-b.

**FR113.** No Slab 7b body activation story amends the **Marcus duality boundary** at `app/marcus/orchestrator/dispatch_adapter.py:81` (line-pinned per R2 freeze). Activation work calls *across* the boundary using existing dispatch APIs; it does not modify the dispatch adapter itself. `bmad-code-review` MUST flag any diff hunk touching `dispatch_adapter.py` lines 70–95 as a governance escalation. Any boundary edit is a substrate amendment governed under the substrate-as-floor regime (D22), filed to `deferred-inventory.md` if needed; opens a Slab-7a-defect story.

### Non-Functional Requirements (24, extracted from PRD §Non-Functional Requirements)

Total: **24 NFRs across 4 categories**. Numbering continues from Slab 7a substrate close: T8→T9, CG11→CG12, I8→I9, OD2→OD3 (R7 Mary-amendment family-continuity anchor).

| Category | Count | ID Range | Story-Scoping |
|---|---|---|---|
| Test discipline (T) | 5 | NFR-T9, NFR-T10, NFR-T11, NFR-T11a, NFR-T11b, NFR-T12 | cross-cutting AC predicates per wave story; aggregate FR101+FR105 parity-test budget at Wave 6 |
| Compliance & Governance (CG) | 9 | NFR-CG12..CG20 (plus NFR-CG14a chain-test base) | per-wave preconditions + Wave-6 closeout aggregation |
| Integrity (I) | 5 | NFR-I9..I13 | story-scoped per-wave (NFR-I9 = FR101 parity-test; NFR-I10 = per-specialist activation contract; NFR-I11 = mapping-checklist row-status; NFR-I12 = class-shaped template conformance; NFR-I13 = substrate-frozen-paths) |
| Operator Documentation (OD) | 4 | NFR-OD3..OD6 | aggregated to Wave 6 closeout (per-specialist operator-reference docs + sanctum-alignment matrix doc + fixture-refresh dry-run + Codex-scope audit) |
| **TOTAL** | **24** (or **25** counting NFR-CG14a as separate) | **4 categories** | mixed |

**Full NFR text:**

**NFR-T9** (T1 unit/contract): wall-clock <30s aggregate per specialist parity suite, <5 min for full 11-specialist run. Enforced per-PR via `@pytest.mark.timeout` + `.github/workflows/composition-tests.yml` per-job ceiling.

**NFR-T10** (T2 fixture-replay): wall-clock <90s per specialist replay; cassettes under `tests/fixtures/specialist-replay/<name>/`. Enforced per-PR on touched specialist only.

**NFR-T11** (T3 canary live-substrate smoke): wall-clock <120s per specialist; quota-gated (operator-gated Completion-Notes evidence, not CI). One canary per specialist per merge-train day.

**NFR-T11a** (T4 cache-determinism harness): wall-clock <45s per specialist; runs nightly OR green-light cadence, NOT per-PR. Determinism-violation = block-mode.

**NFR-T11b** (T5 live canaries — Class-C/C+/D1 only): operator-gated only; no CI budget. ≤3 canaries per specialist (hard cap). Cost ceiling ~$0.40 per canary. Evidence pasted into Completion Notes.

**NFR-T12 (NEW; R7 Murat + Mary).** Parity-test wall-clock SLA: full 11-specialist FR101 parity test (YAML parse + key assertion + cold-activation smoke) MUST complete in <120s wall-clock on the standard CI runner (GitHub-hosted `ubuntu-latest`, 2 vCPU, 7GB). Aggregate budget; per-specialist budget ~10s. Regressions block merge; budget renegotiation requires party-mode.

**NFR-CG12.** Slab 7b sandbox-AC inventory PR MUST land before any API-bound Class-C/C+/D Slab 7b story opens. Story-open-before-PR-landed = governance failure. (Inventory LANDED Wave 0; precondition satisfied for Waves 3–5.)

**NFR-CG13 (R7 Amelia detection mechanism).** Slab 7b live-API-on-CI for any API-bound specialist = 0 occurrences. Detection: `scripts/utilities/detect_live_api_in_tests.py` AST-scans `tests/` for forbidden import set (live-API patterns; inventory at `docs/dev-guide/composition-test-forbidden-imports.json`); runs as pre-merge GitHub Action. Any occurrence = governance failure.

**NFR-CG14.** Slab 7b per-specialist Composition Spec §6 chain-test PR MUST land before story merge for any body activation that consumes upstream substrate APIs. Per Slab 7a chain-test-per-PR convention (Composition Spec §6).

**NFR-CG14a (chain-test base class precondition; PRD errata Errata 3).** Wave 0 / Wave 1 CREATE-task: `tests/composition/_chain_test_base.py` does not yet exist; first Wave-1 chain-test author creates the base class. Subsequent per-specialist chain-tests inherit.

**NFR-CG15.** Slab 7b per-specialist Composition Spec §10 Decision Log entry MUST land for any body activation that emits new vocabulary into the registry. Detection: `scripts/utilities/validate_specialist_composition_spec_decision_log.py` diffs the specialist's Composition Spec §6 vocabulary set against §10 entries; new vocab without a §10 row = block. Missing entry = SG-3 violation.

**NFR-CG16.** Slab 7b per-specialist BMAD code-review MUST land before story close. (Inherited from CLAUDE.md sprint governance.)

**NFR-CG17 (Codex deployment binding).** Codex authoring assignments are normative per D21: Class-C/C+ port-shape stories (Tracy/Gary/Kira/Wanda/Enrique = 5 stories) + sandbox-AC inventory PR + per-story `bmad-code-review` execute via Codex; Class-A/B/D1/D2 + Wave-6 integration story remain Claude-authored. Removing or substantially altering Codex deployment requires party-mode consensus + governance-JSON entry. Codex-authored deliverable that violates its class contract = hard-block at relevant gate.

**NFR-CG18 (foundational-artifacts precondition).** FR108-FR112 + FR107 sandbox-AC inventory entries MUST exist and pass self-test BEFORE any Wave 1 Class-A specialist story opens. Precondition gate, not parallel work item. Wave 0 authors all six; Wave 1 cannot open until §Foundational-Artifacts gate passes. Failure mode: any Wave-1 story opened before precondition is structurally void and must be reverted. (LANDED Wave 0 commit `9ed6fcb`; precondition satisfied.)

**NFR-CG19 (NEW; R7 Winston; five-API operator-side).** Credential-rotation register at `state/config/credential-rotation-register.yaml` lists each of the 5 API surfaces (gamma/kling/elevenlabs/wondercraft/dan-api-tbd) with: owner, rotation cadence, last-rotated date, next-due date, secret-store reference. Quarterly review at retrospective. Missing/expired entries fail the credentials-audit workflow.

**NFR-CG20 (NEW; R7 Winston; five-API operator-side).** Per-specialist rate-limit budget declared in each `app/specialists/<name>/config.yaml` (or sanctum equivalent) — daily token/request ceiling per upstream API. Specialist run aborts cleanly on budget exceeded; no silent-degradation. Budget changes are governance (party-mode), not dev-agent.

**NFR-I9 (NEW).** Sanctum alignment invariant: `tests/parity/test_skill_md_sanctum_alignment.py` MUST pass at every PR merge. Bound to `.github/workflows/specialist-parity.yml` as required check (job name: `parity-test`). If workflow scaffold not yet landed at FR108-FR112 merge, NFR-I9 re-classifies to "MUST pass at Slab 7b close" with Wave-0 / Wave-1 story landing the workflow.

**NFR-I10 (NEW).** Per-specialist activation contract invariant: `tests/parity/per_specialist/test_<specialist_name>_activation_contract.py` (or flat-named per Errata 4) MUST pass for every specialist by Slab 7b close. Bound to `.github/workflows/activation-contract.yml` as required check. Each test asserts the specialist body honors its per-shape contract (Class A: rubric semantics; Class B: Pass-1 mirroring Pass-2; Class C/C+: live API + cache-hit-rate; Class D1: greenfield + scaffold; Class D2: pipeline-determinism).

**NFR-I11 (NEW).** Mapping-checklist row-status invariant: `tests/parity/test_mapping_checklist_status.py` MUST pass by Slab 7b close. Bound to `.github/workflows/mapping-checklist.yml` as required check. Asserts ~28 row improvements (per A-10 R3 amendment) on rows owned by activated specialists; deferred rows (§05B, §6.2, §6.3, §7.5, §14.5, §15) retain pre-Slab-7b status legend.

**NFR-I12 (NEW; R7 Murat).** Class-shaped parity-test invariant: every specialist parity test MUST conform to exactly one of the 5 class templates (A/B/C+merged-with-C+/D1/D2) defined in the canonical alignment checklist (FR108). Template drift between classes (e.g., a fix landing in Class-A without backporting to Class-B) is a block-mode finding. Verified per-PR by `validate_parity_test_class_conformance.py` (AST-walk + import check).

**NFR-I13 (NEW; R7 Winston).** Substrate-frozen-paths invariant + Marcus boundary contract: CI workflow `.github/workflows/substrate-frozen-paths-check.yml` blocks PRs touching frozen paths (`_bmad/memory/shared/`, `app/marcus/orchestrator/dispatch_adapter.py:81`-region, conversation-persistence layer, per-slide subgraph skeleton, vocabulary registry, gate-runner substrate, SG-1..SG-4 contract files) absent `substrate-amendment:` trailer + Marcus-Winston co-sign + CODEOWNERS approval.

**NFR-OD3 (NEW; R7 Amelia path-pin).** Per-specialist operator-reference docs MUST exist at `docs/operator/specialists/<name>.md` for each of the 11 activated specialists by Slab 7b close. Each doc carries OPERATOR / INPUTS / OUTPUTS / REFERENCE four-section structure (Slab 7a Story 7a.7 audience-layered help-text precedent).

**NFR-OD4 (NEW; R7 Amelia path-pin).** Specialist-sanctum-alignment matrix doc at `docs/operator/specialists/sanctum-alignment-matrix.md` MUST exist by Slab 7b close, listing every specialist + alignment-or-exception verdict + rationale link.

**NFR-OD5 (NEW; R7 Winston).** Specialist test fixtures wrapping upstream APIs (Notion pages, Box files, Playwright captures, plus the 5-API surfaces) MUST support a fixture-refresh dry-run mode: `python scripts/utilities/refresh_fixtures.py --specialist <name> --dry-run` reports what would change without writing. Real refresh requires `--apply` + operator confirmation. Prevents silent fixture drift masking upstream behavior changes.

**NFR-OD6 (NEW; R7 Winston).** Codex agent invocation in Slab 7b is restricted to operator-machine activation flow (local `.venv` + operator-initiated). PR-level enforcement: any workflow file under `.github/workflows/` that references `codex` or invokes the Codex CLI fails the `codex-scope-audit` job. Exception requires governance JSON entry + party-mode consensus.

### Additional Requirements (extracted from Architecture + ADRs)

From `architecture-langchain-langgraph-migration.md` (D1-D13) + Slab 7b ADRs (D14-D23) + PRD §Codex Deployment Plan + PRD §Polish-Pass Notes, these implementation requirements flow into Slab 7b story ACs:

- **D14 — Five-class specialist taxonomy (six bins).** Class A (hardening — Texas/Quinn-R/Vera) / Class B (refresh — Irene Pass-1) / Class C (port-shape — Gary/Kira/Wanda/Enrique) / Class C+ (port-shape WITH sidecar emission — Tracy) / Class D1 (LLM-greenfield — Dan) / Class D2 (pipeline-greenfield, sidecar variant — Compositor). Each class has its own K-target, gate-mode designation, and reviewer-burden profile per `slab7bSpecialistRoster` frontmatter (PRD).
- **D15 — SG-4 sanctum alignment per body-activation story.** Every body story carries SKILL.md alignment-or-exception AC (FR100). Cora-sidecar precedent for option-b. Closed allowlist (FR109).
- **D16 — Sandbox-AC inventory PR as hard precondition for API-bound Class-C/C+/D opens.** Tracy + Dan-without-API exempt per R8 Amelia scope-amendment. (Inventory LANDED Wave 0.)
- **D17 — Two distinct determinism harnesses.** H-Cache (≥85%, 10 LLM specialists) + H-Pipeline (≥99%, Class-D2 Compositor). CI surfaces both metrics independently. Green H-Cache does NOT satisfy H-Pipeline and vice versa.
- **D18 — Per-specialist parity-test suite at `tests/parity/per_specialist/` (or flat per Errata 4).** Class-shaped (six templates A/B/C/C+/D1/D2). Extends Slab 7a parity suite at `tests/parity/`.
- **D19 — Mapping-checklist row-status invariant enforced per-PR** (NFR-I11).
- **D20 — Compositor as Class-D2 exemplar (NOT exception).** Sanctum alignment is REQUIRED for Classes A/B/C/C+/D1, **structurally inapplicable for Class D2**. SG-4 validator skips sanctum-presence checks for `class: D2`. No precedent citation, no waiver, no exception register entry required.
- **D21 — Codex deployment as scope-binding commitment #8.** Per-class authoring assignments normative (NFR-CG17). Wave 0.5 is deployment-verification vehicle.
- **D22 — Substrate-as-floor invariant + frozen-path immutability.** Slab 7a-frozen paths are floor; Slab 7b adds bodies, never amends substrate. CI workflow `substrate-frozen-paths-check.yml` (NFR-I13) blocks PRs touching frozen paths absent substrate-amendment ceremony.
- **D23 — Foundational-artifacts precondition gate.** Five foundational artifacts (FR108-FR112) + sandbox-AC inventory entries (FR107) MUST exist and pass self-test BEFORE any Wave 1 Class-A specialist story opens. (LANDED Wave 0.)
- **Composition Spec §3.5 gate precedence rule** — Slab 7b body activation does NOT alter; per-specialist `gate_decision` non-blocking by default under production composition.
- **Composition Spec §3.6 dependency_map sourcing** — every Slab 7b specialist body declares dependencies in manifest, not fallback.
- **ADR-D6 manifest-as-graph-config** — `pipeline-manifest.yaml` is single source of truth; Slab 7b specialist activations bind to manifest entries; PRODUCTION_GATE_IDS derived at compile-time (Slab 7a 7a.2 substrate).
- **Append-only ProductionEnvelope (Composition Spec §3.1)** — every Slab 7b specialist contribution carries SHA256 output digest; no in-place mutation; per Slab 7a 7a.5 conversation-persistence chain.
- **Sandbox-AC governance (CLAUDE.md)** — `validate_migration_story_sandbox_acs.py` passes on every Slab 7b story; dev-agent ACs MUST NOT invoke forbidden CLIs (`docker`, `psql`, `gh`, `aws`, `gcloud`, `az`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`); operator-gated AC-*-B blocks may invoke any CLI for evidence pasting.
- **BMAD sprint governance (CLAUDE.md)** — `bmad-create-prd → bmad-party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story → bmad-code-review` honored end-to-end.
- **Migration-story-governance JSON precondition** — Slab 7b story gate-mode designations (per Phased Wave Plan: Wave 1 single-gate × 3; Wave 2a single-gate; Wave 2b single-gate per Slab 2b.1 TEMPLATE; Wave 3 single-gate × 3; Wave 4 single-gate; Wave 5a single-gate; Wave 5b single-gate; Wave 6 dual-gate) MUST be added to `docs/dev-guide/migration-story-governance.json` via party-mode consensus + version bump BEFORE any Slab 7b story opens via `bmad-create-story`.
- **Composition Smoke gate (Composition Spec §9 + NFR-CG2 inherited from 7a)** — Wave 1 slab-opener (Texas, by alphabetical-by-class precedent) MUST produce Composition Smoke evidence at story-open with PASS verdict.
- **Codex parallel-authoring boundary (NFR-IN3 inherited from 7a + NFR-CG17 NEW)** — see codexDeploymentBoundary frontmatter block.

### UX Design Requirements

**Not applicable** per `bmm-workflow-status.yaml` ("Primary interface is conversational — no traditional UX design needed"). The Slab 7b PRD substitutes traditional UX deliverables with:

- **5 user journeys** (Journey 1 polyphony rewrite + scar-tissue cautious; Journey 2 substrate-remembered parable; Journey 3 dashboard reassurance + cold-session-operator primary; Journey 4 cost-arithmetic teaching + load-bearing payoff; Journey 5 cost-anomaly-pre-launch fork) — see PRD §User Journeys.
- **Operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md`** — extends with 11 new rows (FR104).
- **Per-specialist operator-reference docs at `docs/operator/specialists/<name>.md`** — 11 files (NFR-OD3).
- **Sanctum-alignment matrix at `docs/operator/specialists/sanctum-alignment-matrix.md`** — single sheet (NFR-OD4 + FR103 dev-doc twin).

UX-DR-equivalent requirements are folded into FR104 (operator-control parity) + NFR-OD3-OD6 (operator-documentation NFRs) + the per-class story ACs.

### FR Coverage Map (Epic-level; story-level populated at Step 3)

All 26 FRs (FR88–FR113) assigned to **Epic 1: Slab 7b — Specialist Body Activation**. The Epic decomposes into 12 dev stories across 7 effective waves (Waves 1, 2a, 2b, 3, 4, 5a/5b, 6) plus two pre-Wave-1 governance gates (Wave 0 LANDED + Wave 0.5 Codex-deployment verification). Six FRs (FR107–FR112) are LANDED Wave 0 governance preconditions; the remaining 20 FRs (FR88–FR106 + FR113) decompose across the 12 dev stories.

| FR | Capability | Primary owner | Cross-cuts (story-level mapping at Step 3) |
|---|---|---|---|
| FR88 | Eleven-specialist roster (canonical) | Wave 6 integration story (asserts roster floor) | All 12 dev stories cite roster member |
| FR89 | Texas hardening | Story 7b.1 (Wave 1) | — |
| FR90 | Quinn-R hardening | Story 7b.2 (Wave 1) | — |
| FR91 | Vera hardening | Story 7b.3 (Wave 1) | — |
| FR92 | Irene Pass-1 refresh | Story 7b.4 (Wave 2a) | — |
| FR93 | Tracy port-shape + sidecar (C+) | Story 7b.5 (Wave 2b) | Codex-authored per NFR-CG17 |
| FR94 | Gary port-shape | Story 7b.6 (Wave 3) | Codex-authored per NFR-CG17 |
| FR95 | Kira port-shape | Story 7b.7 (Wave 3) | Codex-authored per NFR-CG17 |
| FR96 | Wanda port-shape onto scaffold | Story 7b.9 (Wave 4) | Codex-authored per NFR-CG17 |
| FR97 | Enrique port-shape | Story 7b.8 (Wave 3) | Codex-authored per NFR-CG17 |
| FR98 | Dan greenfield (D1) | Story 7b.10 (Wave 5a) | sandbox-AC `dan-api-tbd` resolved at story-T1 |
| FR99 | Compositor greenfield (D2 sidecar variant) | Story 7b.11 (Wave 5b) | scaffold-v0.2-D2-pipeline consumed |
| FR100 | SG-4 sanctum-alignment AC per body | All 11 body stories (7b.1-7b.11) | cross-cutting; reviewer verifies |
| FR101 | Parity-test test_skill_md_sanctum_alignment.py | Story 7b.1 (creates SanctumParityTestBase per Errata 3) + Story 7b.12 (aggregates) | All body stories add their row |
| FR102 | Parity-test runs at every PR merge | Story 7b.12 (Wave 6 closeout) | Bound to .github/workflows/specialist-parity.yml |
| FR103 | Sanctum-alignment matrix doc (dev-doc twin) | Story 7b.12 (Wave 6 closeout) | All body stories update at close |
| FR104 | Operator-control parity table +11 rows | Story 7b.12 (Wave 6 aggregation) | Each body story authors its row pre-class-entry |
| FR105 | Per-specialist parity-test suite | All 11 body stories (each authors its file) + Story 7b.12 (asserts coverage) | Errata 4 subdir-vs-flat ratified at Story 7b.1 |
| FR106 | Cache-hit-rate harness (10) + pipeline-determinism harness (1) | Story 7b.6/7/8/9/10 (Class-C/C+/D1 wire harness) + Story 7b.11 (Class-D2 H-Pipeline) + Story 7b.12 (aggregation) | Parametric config |
| FR107 | Sandbox-AC inventory +5 entries | **LANDED Wave 0** (commit `9ed6fcb`; precondition for Waves 3–5) | — |
| FR108 | BMB sanctum alignment checklist | **LANDED Wave 0** (FR108 precondition for Wave 1) | — |
| FR109 | Sanctum exception categories closed allowlist | **LANDED Wave 0** | — |
| FR110 | Operator-control parity template | **LANDED Wave 0** | — |
| FR111 | Scaffold-v0.2-D2-pipeline (Errata 1 path-corrected) | **LANDED Wave 0** (precondition for Wave 5b Compositor) | — |
| FR112 | Cora SKILL.md §Sanctum exception anchor | **LANDED Wave 0** | — |
| FR113 | Marcus duality boundary frozen | All 12 dev stories (CI substrate-frozen-paths-check.yml enforces; NFR-I13) | Cross-cutting |

**Cross-check:** 26/26 FRs covered ✅. 6 FRs LANDED Wave 0; 20 FRs distributed across the 12 dev stories.

## Epic List

### Epic 1: Slab 7b — Specialist Body Activation (Eleven-Specialist Roster Body-Activation atop Slab 7a Substrate)

**Epic Goal:** Operator runs Trial-2 end-to-end against the Slab 7a substrate (CLOSED 2026-04-29 at `95c81b0`) with **real content from all eleven specialists** — Texas retrieves real corpus content (not fixture stub), Irene Pass-1 + Pass-2 author real lesson plans + narration scripts, Tracy enriches with real research (Pass-2 companion), Gary calls Gamma's API for real slide variants, Kira calls Kling's API for real motion clips, Enrique calls ElevenLabs's API for real narration audio, Wanda calls Wondercraft's API for real podcast beds, Compositor runs deterministic assembly against real assets, Quinn-R runs rubric against real upstream artifacts, Vera runs fidelity assessment on real content, Dan threads creative-director aux contributions across G1–G2 — **Trial-2 reaches G3 cleanly with no fixture-stub fallback, no silent gate-bypass, no mapping-checklist regression. SG-1 / SG-2 / SG-3 / SG-4 all green.**

**User outcome (post-epic):** the operator who paused Trial-475 cleanly at G1 (2026-04-28) because Texas returned a fixture stub now opens Trial-2, types `bmad-trial start --input course-content/courses/<lesson-slug>/`, and watches eleven specialists at a workbench. By G2 they have real Texas extractions reviewed, a real Irene Pass-1 lesson plan ratified, a real Tracy enrichment merged, real Gary slide variants chosen per slide, real Kira motion clips designated, real Enrique narration auditioned and selected, real Wanda podcast beds chosen, a real Compositor `DESCRIPT-ASSEMBLY-GUIDE.md` regenerated, real Quinn-R pre-composition QA verdicts, real Vera G0/G1/G3/G4 fidelity assessments, real Dan creative-director threads. **MVP Exit Gate (R8 amendment):** Trial-2 reaches G2 cleanly with real content from ≥9-of-11 specialists (≥3 per class) — fails fast on activation-correctness assumption. **Slab 7b Close Gate (full-scope):** Trial-2 reaches G3 cleanly with real content from all eleven specialists (cascade-reading verified for Pass-2-internal Tracy contribution per R8 Mary clarification).

**FRs covered:** all 26 (FR88–FR113). See FR Coverage Map above for per-FR Wave/Story assignment.

**NFRs covered:** all 24 (NFR-T9..T12 + NFR-CG12..CG20 + NFR-CG14a + NFR-I9..I13 + NFR-OD3..OD6). 11 story-scoped to Wave 6 (NFR-CG14, CG15, CG16; NFR-OD3, OD4, OD5, OD6; NFR-I9, I10, I11, I12); 2 governance preconditions story-scoped to Wave 0 (NFR-CG12 sandbox-AC inventory; NFR-CG18 foundational-artifacts); other 11 cross-cutting AC predicates applied across all 12 dev stories where touched code path triggers them.

**Standing-guardrail enforcement (SG-1/SG-2/SG-3/SG-4):**
- **SG-1 (11-specialist roster floor):** primary aggregation in Story 7b.12 (Wave 6 integration) parity-test extension `tests/parity/test_eleven_specialists_addressable.py`; cross-cuts every body story (each cites its specialist).
- **SG-2 (33-row mapping-checklist floor):** distributed authoring across stories per row-to-story mapping; Story 7b.12 aggregates and asserts ~28 row improvements via NFR-I11 + `tests/parity/test_mapping_checklist_status.py`; deferred rows (§05B, §6.2, §6.3, §7.5, §14.5, §15) retain pre-Slab-7b status.
- **SG-3 (Composition Spec invariants):** every body story produces Composition Spec §6 chain-test PR + §10 Decision Log entry per NFR-CG14/15; Story 7b.12 aggregates and asserts §3.1/§3.5/§3.6/§9/§11 hold; FR113 substrate-frozen-paths-check enforces §3.1/§3.6 immutability.
- **SG-4 (BMB sanctum alignment per body — NEW):** every body story (Class A/B/C/C+/D1) carries SKILL.md alignment-or-exception AC per FR100 (Class-D2 Compositor exempt per D20 — first-class taxonomy bin, not exception); Story 7b.1 creates `SanctumParityTestBase` per Errata 3; Story 7b.12 asserts FR101 parity-test green at PR-merge gate via NFR-I9.

**Standalone-epic check (per skill principle #3):** Epic 1 is **NOT** standalone in the sense that it depends on prior migration substrate (Slab 1-6 SHIPPED at `97842ac`; Slab 7a substrate CLOSED at `95c81b0`). It IS standalone in the sense that NO future epic (Doc-7-D prose harvest) is required for Epic 1 to function — Slab 7b activates specialists INTO the Slab 7a scaffold; Doc-7-D harvests anti-patterns AFTER Trial-2 runs. Trial-2 readiness with real eleven-specialist activation is Epic 1's exit gate.

**Wave structure (proposed; finalized at Step 3 story decomposition):**

| Wave | Stories | Class | Author | Gate | K-target / story | Parallelism |
|---|---|---|---|---|---|---|
| **0** (LANDED) | Foundational artifacts FR108-FR112 + sandbox-AC inventory FR107 | Governance precondition | Mixed (Wave-0 atomic-merge `9ed6fcb`) | operator-gated | NOT K-counted (per R8 Mary-amendment) | atomic merge |
| **0.5** | Codex deployment + smoke-test verification (NFR-CG17 binding) | Governance precondition | Operator (Codex deploy) | operator-gated | NOT K-counted | may fold into Wave 0 |
| **1** | 7b.1 Texas / 7b.2 Quinn-R / 7b.3 Vera | Class A hardening | Claude | single-gate | ~2K LOC + ~25 tests | parallelizable after Wave 0/0.5 |
| **2a** | 7b.4 Irene Pass-1 | Class B refresh | Claude | single-gate | ~2.5K LOC + ~30 tests | serial (precedes 2b) |
| **2b** | 7b.5 Tracy port-shape + sidecar bundle | Class C+ | Codex | single-gate (per Slab 2b.1 TEMPLATE) | ~3.3K LOC + ~36 tests | serial (after 2a) |
| **3** | 7b.6 Gary / 7b.7 Kira / 7b.8 Enrique | Class C API-bound | Codex | single-gate (per Slab 2b.1 TEMPLATE) | ~2.9K LOC + ~33 tests each | parallelizable after Wave 0+1 |
| **4** | 7b.9 Wanda port-shape onto scaffold | Class C | Codex | single-gate | ~2.9K LOC + ~33 tests | parallelizable after Wave 3 |
| **5a** | 7b.10 Dan greenfield | Class D1 | Claude | single-gate | ~3.5K LOC + ~40 tests | parallelizable after Waves 1-3 *closed* (R8 Winston) |
| **5b** | 7b.11 Compositor greenfield | Class D2 (sidecar variant) | Claude | single-gate | ~3.5K LOC + ~40 tests | parallelizable with 5a |
| **6** | 7b.12 Integration + parity-suite + closeout | Integration | Claude | **dual-gate** (mirrors Slab 7a 7a.8) | ~3K LOC + ~25 active tests | strict-last |

**Total Slab 7b:** 12 dev stories + 2 pre-Wave-1 governance gates (Wave 0 LANDED; Wave 0.5 verification). **Aggregate:** ~33–37 K-units at K-floor 1.3-1.5× per R3 amendment (target band 24-30 per R8 Mary; bias to upper band given Class-C+ + Class-D1 + Class-D2 K-bumps). Aggregate test count target: ~325-375. Wall-clock target: ~3-4 weeks per Slab 7a NEW CYCLE acceleration precedent (Slab 7a achieved 1-day vs 7-9-week plan via Codex sub-agent parallelism).

**Hard preconditions before Epic 1 Wave 1 opens:**
1. **Wave 0 atomic merge LANDED** ✅ — commit `9ed6fcb` (FR107-FR112 all green at filesystem verification; NFR-CG18 satisfied).
2. **Wave 0.5 Codex deployment verification** — Codex agent deployed + smoke-tested per NFR-CG17 binding allocation BEFORE Wave 1 opens. May fold into Wave 0 atomic merge per architect preference.
3. **Migration-story-governance JSON precondition** — Slab 7b 7b.1-7b.12 gate-mode entries (Wave 1-5: single-gate; Wave 6: dual-gate) added to `docs/dev-guide/migration-story-governance.json` via party-mode consensus + version bump BEFORE any Slab 7b story opens via `bmad-create-story`.
4. **Composition Smoke gate (Composition Spec §9 + NFR-CG2 inherited)** — Wave 1 slab-opener (Story 7b.1 Texas, by alphabetical-by-class precedent) MUST produce Composition Smoke evidence at story-open with PASS verdict.
5. **Manifest version-bump** — Slab 7b is Tier-2 minor pack-version bump per `pipeline-manifest-regime.md` (specialist-body activations extend manifest; party-mode + version bump required at Wave 1 open).

**Dependency wave structure:** strict-serial-with-parallel-waves — 7 effective execution waves:
- **Wave 0** (atomic merge; LANDED) — foundational artifacts + sandbox-AC inventory
- **Wave 0.5** (Codex deploy verify) — strict after Wave 0
- **Wave 1** (Class A × 3; parallelizable) — strict after Wave 0/0.5
- **Wave 2a** (Class B × 1) — strict after Wave 1 (Vera hardening provides G4-19 rubric Irene Pass-1 needs to mirror)
- **Wave 2b** (Class C+ × 1; Tracy) — strict after Wave 2a (Tracy is Pass-2 enrichment companion)
- **Wave 3** (Class C × 3; Gary/Kira/Enrique parallelizable) — needs Waves 0+1; Wave-1 scaffold-amortization tripwire (R8 Murat: if Tracy >2.7K LOC, escalate)
- **Wave 4** (Class C × 1; Wanda) — parallelizable with Wave 3 tail
- **Wave 5a/5b** (Class D1 + D2; parallelizable) — strict after Waves 1-3 *CLOSED* (R8 Winston-amendment, not merely in-progress)
- **Wave 6** (integration + closeout; strict-last; dual-gate) — five-API live-binding smoke runs at Wave 6 (operator-gated AC-*-B style)

**Codex deployment boundary (per PRD §Codex Deployment Plan + NFR-CG17 + D21):**
- **Codex authors:** Wave 0 sandbox-AC inventory (LANDED) + Wave 2b Tracy + Wave 3 Gary/Kira/Enrique + Wave 4 Wanda = 5 stories.
- **Claude authors:** Wave 1 Texas/Quinn-R/Vera + Wave 2a Irene Pass-1 + Wave 5a Dan + Wave 5b Compositor + Wave 6 integration = 7 stories.
- **Codex reviews:** every story `bmad-code-review` (mutual-handoff pattern per Slab 7a precedent).
- **NFR-CG17 deviation noted:** FR107 sandbox-AC inventory authored by Claude (not Codex) per R1 party-mode scoping consensus — Wave 0 is foundational scaffolding pre-Wave-1, NOT inside Codex's Class-C/C+ port-shape scope; Codex deployment activates at Wave-1 story open.

---

**End of Step 2 output (epic shape design + FR coverage map complete; party-mode Round (a) below; per-story decomposition deferred to Step 3).**

## Party-Mode Round (a) — Epic-Shape Green-Light

**Convened:** 2026-04-29 (Step 2 close pre-Step-3).
**Voices (4; per Slab 7a precedent):** John (PM/scoping/risk), Mary (analyst/scope-floor/governance), Amelia (dev-shape/K-target), Murat (test-shape/parity-test).
**Mandate:** ratify Epic 1 shape + 12-story decomposition skeleton + Wave structure + Codex/Claude per-story author binding. NOT a re-litigation of PRD R1-R9 amendments.

### Round (a) verdicts

**John (PM/scoping/risk):** GREEN.
> "Single-Epic shape inherits Slab 7a's structural precedent cleanly — sibling-coherence preserved. The MVP Exit Gate (G2 + 9-of-11) vs Slab Close Gate (G3 + 11) two-gate structure from PRD R8 is correctly reflected at the Epic level. SR-T6 cost-anomaly-pre-launch + SR-T9 Codex-availability + SR-S3 credential drift are all surfaced via Wave 0.5 + Wave 6 closeout deliverables. **One amendment:** Wave 6 should explicitly call out the **trial-2 cost-projection dry-run** as an AC-prerequisite (Journey 5 fork) — not just live-binding smoke. Filed as Wave 6 AC at Step 3."

**Mary (analyst/scope-floor/governance):** GREEN-WITH-ONE-AMENDMENT.
> "SG-1/SG-2/SG-3/SG-4 enforcement matrix is structurally correct: Story 7b.12 (Wave 6) carries the aggregate parity-test + mapping-checklist + sanctum-alignment-matrix-doc deliverables; Story 7b.1 (Texas, Wave-1 slab-opener) carries the FR101 parity-test base class creation per Errata 3. **Amendment:** the 'Codex authors 5 / Claude authors 7' ratio implies Wave 0 (sandbox-AC inventory FR107) was Codex-authored, but the NFR-CG17 deviation note clarifies it was Claude — the boundary description should match the deviation note explicitly to avoid downstream confusion. The 'Codex authors' line should read **'Wave 2b + Wave 3 + Wave 4 = 5 stories'** (drop the LANDED Wave 0 reference from the Codex-authors list since it was Claude-authored). Already worded that way in the table; just tighten the prose."

**Amelia (dev-shape/K-target):** GREEN-WITH-ONE-CONCERN.
> "K-aggregate ~33-37 trips R8 Mary's stated 24-30 band on the upper edge. The Class-D1 + D2 + integration stories carry K-bumps that push the upper bound. **Concern:** if all twelve stories land at their stated K-target ceilings without amortization, we'll exceed 30 K-aggregate. **Mitigation:** Wave-1 scaffold-amortization tripwire (R8 Murat) should fire at Tracy (Wave 2b) at >2.7K LOC, AND at Gary (Wave 3 first port-shape) at >2.7K LOC — if either fires, Class-C ports beyond the first should escalate to dual-gate. **Recommend filing this as an explicit 'K-aggregate tripwire' clause in Wave 1 close + Wave 2b open.** Otherwise GREEN."

**Murat (test-shape/parity-test):** GREEN-WITH-ONE-AMENDMENT.
> "Parity-test ownership is correctly distributed: Story 7b.1 (Texas) creates `SanctumParityTestBase` per Errata 3; Story 7b.12 (Wave 6) aggregates and asserts coverage. **Amendment:** Errata 4 (subdir-vs-flat ratification) should land at **Story 7b.1 T1-readiness check**, NOT defer to Wave 6 — first parity-test author (Texas) sets the convention; subsequent specialist authors inherit. Also: NFR-I12 class-shaped template conformance + NFR-CG14a chain-test base class creation are both Wave-1 CREATE-tasks; recommend explicitly tagging both as Story 7b.1 T1 preconditions. Otherwise GREEN. The K-floor / target-range table at the Epic level is sound — class-shaped K-bumps follow the 5-class taxonomy (D14) cleanly."

### Round (a) consensus

**Verdict:** RATIFIED-WITH-AMENDMENTS (4/4 unanimous green; 3 amendments to fold into Step 3).

**Amendments to fold at Step 3:**
- **(John A1):** Wave 6 Story 7b.12 carries explicit trial-2 cost-projection dry-run AC (Journey 5 fork; SR-T6 mitigation).
- **(Mary A2):** prose tightening — "Codex authors" list excludes Wave 0 (already correct in table; tighten paragraph wording).
- **(Amelia A3):** K-aggregate tripwire clause at Wave 1 close + Wave 2b open + Wave 3 first port-shape (Gary) — if any specialist exceeds 2.7K LOC, Class-C ports beyond the first escalate to dual-gate.
- **(Murat A4):** Story 7b.1 T1-readiness checks include (i) Errata 4 subdir-vs-flat ratification, (ii) `SanctumParityTestBase` creation per Errata 3, (iii) `_chain_test_base.py` creation per NFR-CG14a, (iv) NFR-I12 class-shaped template conformance validator scaffolding.

**Re-opens:** 0. Epic shape proceeds to Step 3 story decomposition.

---

**End of Step 2 — party-mode Round (a) closed; ratified-with-amendments; 0 re-opens.**

---

## Epic 1: Slab 7b — Specialist Body Activation (Eleven-Specialist Roster Body-Activation atop Slab 7a Substrate)

**Epic Goal:** Operator runs Trial-2 end-to-end against the Slab 7a substrate with real content from all eleven specialists; Trial-2 reaches G3 cleanly; SG-1/2/3/4 all green.

### Story 7b.1: Texas Hardening — Live Retrieval Against Real Directive Composer

As the operator,
I want Texas to execute live retrieval against the Slab 7a directive composer's output (no fixture-stub fallback) and emit the six-canonical-artifacts contract per G0 6-dim evidence-sentence rubric,
So that Trial-2 advances past G0 with real corpus extractions reviewed against the 33-row mapping checklist's G0 row, and Trial-475's pause-at-G1 fixture-stub failure mode cannot recur.

**Story metadata:** Wave 1 (slab-opener; class A hardening; Claude-authored); single-gate; ~2K LOC + ~25 tests; FR coverage 8 (FR89 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts; carries Errata 3 + Errata 4 ratifications).

**T1-readiness preconditions (Murat A4 amendment from Round (a)):**
- (i) Errata 4 subdir-vs-flat ratification — author records decision in `tests/parity/README.md` before first parity-test commit (recommend flat per "embrace boring technology")
- (ii) `SanctumParityTestBase` created at `tests/parity/_sanctum_parity_base.py` per Errata 3 — first parity-test inherits
- (iii) `_chain_test_base.py` created at `tests/composition/_chain_test_base.py` per NFR-CG14a — first chain-test inherits
- (iv) NFR-I12 class-shaped template conformance validator scaffolding — `scripts/utilities/validate_parity_test_class_conformance.py` lands with stub assertions extensible by Wave 2-5 stories

**Acceptance Criteria:**

**Given** the Slab 7a directive composer at `app/marcus/orchestrator/directive_composer.py`
**When** the operator invokes `bmad-trial start --input course-content/courses/<lesson-slug>/`
**Then** Marcus emits `state/runs/<run_id>/directive.yaml` AND Texas's `dispatch_retrieval(directive_path=<run_id>/directive.yaml, bundle_dir=<run_id>/bundle/)` is invoked against `app/specialists/texas/_act.py`
**And** Texas executes a real retrieval (NOT the fixture stub at `tests/fixtures/specialists/texas/fixture_bundle/`)
**And** the six-canonical-artifacts contract is honored: `extracted.md` / `metadata.json` / `extraction-report.yaml` / `manifest.json` / `ingestion-evidence.md` / `result.yaml` are written under `<bundle_dir>/` (FR89).

**Given** Texas's `_act` body running against real corpus
**When** Vera applies the G0 6-dim evidence-sentence rubric to `extracted.md`
**Then** every claim carries an evidence-sentence anchor traceable to corpus source-of-truth (per FR89 G0 6-dim contract)
**And** the word-count belt-and-suspenders check enforces `len(extracted.md.split()) >= floor` per directive scope (FR89)
**And** cross-validation hint application (where applicable per `RetrievalIntent`) is logged to `extraction-report.yaml §cross_validation` (FR89).

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Texas hardening changes
**Then** `skills/bmad-agent-texas/SKILL.md` is verified option-a sanctum-aligned per BMB checklist (FR108) — minimal frontmatter (`name` + `description`) per Errata 2 + sanctum dir at `_bmad/memory/bmad-agent-texas/` containing 6-file BMB pattern (INDEX.md/PERSONA.md/CREED.md/BOND.md/MEMORY.md/CAPABILITIES.md)
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Texas (FR101 + FR102 + NFR-I9)
**And** `bmad-code-review` confirms `# SG-4 Sanctum Alignment` AC verbatim in story planning artifact (FR100).

**Given** the FR105 per-specialist parity-test requirement
**When** the dev-agent authors Texas's activation-contract test
**Then** `tests/parity/test_texas_activation_contract.py` (flat per Errata 4 ratification at this story T1) lands inheriting `SanctumParityTestBase`
**And** the test asserts Class-A rubric-semantics parity per NFR-I12 class-shaped template conformance validator
**And** the test runs <30s per NFR-T9 + <120s aggregate per NFR-T12.

**Given** the sandbox-AC inventory governance requirement (CLAUDE.md)
**When** the dev-agent's ACs are validated by `scripts/utilities/validate_migration_story_sandbox_acs.py`
**Then** no forbidden CLI (`docker`, `psql`, `gh`, `aws`, `gcloud`, `az`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`) appears in dev-agent AC blocks
**And** any live-substrate verification is wrapped via shipped Python deps (e.g., `httpx`, `psycopg`) with `pytest.skip(...)` when service unreachable.

**Given** the substrate-as-floor invariant (FR113 + NFR-I13)
**When** the dev-agent's diff is reviewed
**Then** no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70–95` absent `substrate-amendment:` trailer + Marcus-Winston co-sign
**And** `.github/workflows/substrate-frozen-paths-check.yml` passes at PR merge.

**Given** the trial-475 root-cause regression test
**When** trial-475's input replays against the new Texas hardening
**Then** Texas receives a real directive AND advances past G0 with real extractions (regression evidence captured in `tests/parity/test_trial_475_texas_hardening_regression.py`).

**Standing-guardrail enforcement:** SG-1 unchanged (Texas in roster floor); SG-2 G0 row in mapping checklist preserved + status improved (one of ~28 row improvements); SG-3 Composition Spec §3.1 SHA256+append-only honored on Texas envelope contribution; **SG-4 primary enforcement here** (first body-activation story; SanctumParityTestBase created; option-a alignment verified).

**Story-scoped NFR predicates:** NFR-T9 (<30s parity test); NFR-T10 (<90s fixture-replay); NFR-T11 (T3 canary live-substrate smoke; operator-gated); NFR-T11a (T4 cache-hit-rate harness ≥85% post-warm-up); NFR-T11b (T5 live canary ≤3; cost ceiling ~$0.40); NFR-T12 (parity-test wall-clock <120s aggregate); NFR-CG14 (chain-test PR pre-merge); NFR-CG14a (chain-test base class CREATE-task); NFR-CG16 (BMAD code-review pre-close); NFR-I9 (sanctum-parity invariant); NFR-I10 (per-specialist activation contract); NFR-I12 (class-shaped template conformance); NFR-I13 (substrate-frozen-paths-check).

---

### Story 7b.2: Quinn-R Hardening — Two-Mode Rubric + G2C Storyboard-Bound + G5 Pre-Composition QA

As the operator,
I want Quinn-R to execute its two-mode (pre-composition / post-composition) rubric semantics on real upstream artifacts — G2C storyboard-bound shape + G5 pre-composition QA covering WPM review, VTT monotonicity, coverage completeness, motion-vs-narration duration coherence, and advisory-vs-blocking partition,
So that Quinn-R produces real quality verdicts (not scaffold-stubbed) at G2C/G3B/G5 gates and Trial-2's per-slide review pack carries operator-actionable findings.

**Story metadata:** Wave 1 (Class A hardening; parallelizable with 7b.1, 7b.3; Claude-authored); single-gate; ~2K LOC + ~25 tests; FR coverage 7 (FR90 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts).

**Acceptance Criteria:**

**Given** Quinn-R's two-mode body shape (pre-composition / post-composition)
**When** Marcus dispatches Quinn-R at G2C (storyboard-bound, pre-composition)
**Then** Quinn-R emits `authorized-storyboard.json` per the pre-composition write contract (FR90)
**And** the contract is structurally validated against `state/config/schemas/authorized-storyboard.schema.json` (lockstep regen via NFR-CG4 carry-forward).

**Given** Quinn-R running G5 pre-composition QA on real Enrique narration + real Kira motion
**When** the QA body executes
**Then** five sub-checks fire: (i) WPM review against `narration_profile_controls.target_wpm`; (ii) VTT monotonicity across the captions track; (iii) coverage completeness (every storyboard slide has narration); (iv) motion-vs-narration duration coherence (per-segment delta within tolerance); (v) advisory-vs-blocking partition (block-mode failures vs advisory warnings) (FR90)
**And** verdicts land in `runs/<run_id>/specialist-summaries/quinn-r-<gate>-<timestamp>.md` per Slab 7a 7a.5 conversation-persistence contract.

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Quinn-R hardening
**Then** `skills/bmad-agent-quality-reviewer/SKILL.md` is option-a sanctum-aligned + sanctum dir at `_bmad/memory/bmad-agent-quinn-r/` carries the 6-file BMB pattern
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Quinn-R.

**Given** the FR105 per-specialist parity-test requirement
**When** the dev-agent authors `tests/parity/test_quinn_r_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-A rubric-semantics parity (advisory-vs-blocking partition; structured verdict shape; storyboard-bound write contract).

**Given** the sandbox-AC inventory governance requirement
**When** the dev-agent's ACs are validated
**Then** no forbidden CLI appears in dev-agent ACs; live-substrate verification wrapped via shipped Python deps with `pytest.skip(...)`.

**Given** Quinn-R's post-composition mode
**When** Marcus dispatches Quinn-R at G3B (post-Storyboard-B HIL review)
**Then** Quinn-R produces a forensic verdict on the assembled artifacts (post-Compositor) — distinct from pre-composition mode (FR90).

**Standing-guardrail enforcement:** SG-1 unchanged (Quinn-R in roster floor); SG-2 G2C/G5 rows preserved + status improved; SG-3 Composition Spec §3.5 gate precedence honored (Quinn-R is per-specialist non-blocking by default under production composition); SG-4 option-a sanctum-aligned.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11 / T11a / T11b / T12; NFR-CG14 / CG14a / CG16; NFR-I9 / I10 / I12 / I13.

---

### Story 7b.3: Vera Hardening — G0/G1/G3/G4 Fidelity Rubrics on Real Content + Sensory Bridges Dispatch

As the operator,
I want Vera to execute fidelity assessment on real upstream artifacts — G0 6-dim evidence-sentence rubric on real Texas output, G1 ingestion-quality 6-dim verdicts, G3 fidelity check on real Storyboard A, G4 19-criterion rubric (G4-01 through G4-19) on real Irene Pass-2 narration, plus sensory-bridges dispatch on real motion + audio,
So that Vera's Fidelity Trace Reports carry forensic findings (Omissions/Inventions/Alterations) on real content, the circuit-breaker mechanism activates against real failure modes, and Quinn-R's downstream rubric runs on Vera-cleared artifacts.

**Story metadata:** Wave 1 (Class A hardening; parallelizable with 7b.1, 7b.2; Claude-authored); single-gate; ~2K LOC + ~25 tests; FR coverage 7 (FR91 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts).

**Acceptance Criteria:**

**Given** Vera's G0 6-dim evidence-sentence rubric on real Texas output
**When** Vera runs at G0
**Then** the rubric scores Texas's `extracted.md` against six dimensions (per FR91 contract) AND emits a Fidelity Trace Report under `runs/<run_id>/fidelity/g0-vera-<timestamp>.json`
**And** Omissions / Inventions / Alterations (O/I/A taxonomy) are itemized.

**Given** Vera's G4 19-criterion rubric on real Irene Pass-2 narration script
**When** Vera runs at G4
**Then** all 19 criteria (G4-01 through G4-19; codified in `g4-narration-script.yaml` per Epic 23 closure) are evaluated AND verdicts emitted with severity + description per criterion (FR91).

**Given** Vera's sensory-bridges dispatch on real motion + audio
**When** Vera runs G3 fidelity check on real Storyboard A (post-Gary slides + post-Kira motion + post-Enrique audio)
**Then** the sensory-bridges skill is invoked for image/audio/video perception (per universal perception protocol)
**And** confidence rubric scores land in the Fidelity Trace Report.

**Given** the circuit-breaker mechanism (per APP fidelity architecture)
**When** Vera detects a hard-fail O/I/A finding (per circuit-breaker rule)
**Then** the run halts at the gate with HALT-AND-REMEDIATE; control returns to operator with Vera's verdict carrying the failure reason.

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Vera hardening
**Then** `skills/bmad-agent-fidelity-assessor/SKILL.md` is option-a sanctum-aligned + sanctum dir at `_bmad/memory/bmad-agent-vera/` carries the 6-file BMB pattern
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Vera.

**Given** the FR105 per-specialist parity-test requirement
**When** the dev-agent authors `tests/parity/test_vera_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-A rubric-semantics parity (O/I/A taxonomy structural shape; circuit-breaker behavioral contract).

**Given** the sandbox-AC inventory governance requirement
**When** the dev-agent's ACs are validated
**Then** no forbidden CLI appears in dev-agent ACs.

**Standing-guardrail enforcement:** SG-1 unchanged (Vera in roster floor); SG-2 G0/G1/G3/G4 rows preserved + status improved; SG-3 Composition Spec §3.5 honored; SG-4 option-a sanctum-aligned.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11 / T11a / T11b / T12; NFR-CG14 / CG14a / CG16; NFR-I9 / I10 / I12 / I13.

**Wave-1 close gate (Amelia A3 amendment from Round (a)):** if any of 7b.1/7b.2/7b.3 lands >2.7K LOC, **K-aggregate tripwire fires**: subsequent Class-C ports beyond the first (Wave 3 second + third stories) escalate to dual-gate. Tripwire status logged in `_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md` Completion Notes.

---

### Story 7b.4: Irene Pass-1 Activation Refresh — 9-Node Scaffold Mirroring Pass-2

As the operator,
I want Irene Pass-1 to execute a 9-node scaffold mirroring the Pass-2 shape (Slab 2a.2 precedent) — lesson-plan coauthoring + scope-lock contract + per-plan-unit ratification surface for G1A + `irene-pass1.md` artifact write + mode-singularity hard-constraint enforcement + `scope_decision.set` + `plan.locked` learning-event emission,
So that Trial-2 reaches G1A with a real Pass-1 lesson plan ratified per-plan-unit (not auto-confirmed) and Pass-2 inherits a locked scope.

**Story metadata:** Wave 2a (Class B refresh; serial after Wave 1; Claude-authored); single-gate; ~2.5K LOC + ~30 tests; FR coverage 6 (FR92 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts).

**Acceptance Criteria:**

**Given** the 9-node scaffold pattern from Slab 2a.2 (Irene Pass-2)
**When** the dev-agent authors `app/specialists/irene_pass1/_act.py`
**Then** the scaffold mirrors the 9-node Pass-2 shape (per Slab 2a.2 precedent; mode-singularity hard-constraint enforced — Pass-1 cannot run in Pass-2 mode)
**And** `_act` body length is ≤150 LOC per AC-B ceiling (per Slab 2a.2 precedent).

**Given** Irene Pass-1 running against real corpus (post-Texas hardening)
**When** Marcus dispatches Irene at G1A
**Then** Irene authors a real lesson plan with per-plan-unit ratification surface (operator confirms each plan unit; not bulk auto-confirm) (FR92)
**And** the plan lands at `runs/<run_id>/irene-pass1.md` per the artifact-write contract.

**Given** the scope-lock contract
**When** the operator confirms the Pass-1 plan
**Then** `scope_decision.set` learning event is emitted AND `plan.locked` learning event fires
**And** Pass-2 inherits a locked scope (per Wave 2 sequencing — Tracy's Pass-2 enrichment runs against locked plan).

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent commits Irene Pass-1
**Then** `skills/bmad-agent-content-creator/SKILL.md` is option-a sanctum-aligned (Pass-1 + Pass-2 share the same SKILL.md per Slab 2a.2 era + 7b.4 refresh) + sanctum dir at `_bmad/memory/bmad-agent-irene/` carries 6-file BMB pattern
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Irene.

**Given** the FR105 per-specialist parity-test requirement
**When** the dev-agent authors `tests/parity/test_irene_pass1_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-B persona-continuity + sidecar-write parity (per NFR-I12 Class-B template).

**Given** the cache-hit-rate harness requirement (FR106)
**When** the dev-agent wires Irene Pass-1 into the harness
**Then** harness runs N=10 against `gpt-5.4` with `prompt_tokens >> 1024` MF2 floor; `median[2:] >= 85%` post-warm-up.

**Standing-guardrail enforcement:** SG-1 unchanged (Irene in roster floor); SG-2 G1A row preserved + status improved; SG-3 Composition Spec §3.5/§3.6 honored; SG-4 option-a sanctum-aligned.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11 / T11a / T11b / T12; NFR-CG14 / CG16; NFR-I9 / I10 / I12 / I13.

---

### Story 7b.5: Tracy Port-Shape + Sidecar Creation (Class C+) — Pass-2 Research Enrichment Companion

As the operator,
I want Tracy to execute a Class-C+ port-shape — research-shaped intent enrichment for Pass-2 + sidecar greenfield at `_bmad/memory/bmad-agent-tracy/` with full 4-file BMB pattern (INDEX.md / PERSONA.md / chronology.md / access-boundaries.md) + 9-node scaffold per Slab 2b.1 TEMPLATE + live LLM-only binding (no third-party API),
So that Pass-2 narration carries real research enrichment (not passthrough) and the BMB sidecar pattern is established for the Class C+ class.

**Story metadata:** Wave 2b (Class C+; serial after Wave 2a; **Codex-authored** per NFR-CG17 + D21); single-gate per Slab 2b.1 TEMPLATE; ~3.3K LOC + ~36 tests; FR coverage 6 (FR93 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts).

**Wave-2b open precondition (Amelia A3 amendment from Round (a)):** Wave-1 K-aggregate tripwire status check — if any Wave-1 story exceeded 2.7K LOC, this story opens with cautious K-target (per upper band 3.5K + dual-gate escalation pre-authorized).

**Acceptance Criteria:**

**Given** Tracy's pre-Slab-7b passthrough state
**When** the dev-agent (Codex) authors Tracy's port-shape
**Then** `app/specialists/tracy/_act.py` lands with a 9-node scaffold per Slab 2b.1 TEMPLATE (port-shape pattern); `_act` body ≤150 LOC per AC-B ceiling
**And** Tracy emits research-shaped intent enrichment for Pass-2 (per FR93 contract).

**Given** the Class-C+ sidecar emission requirement
**When** the dev-agent (Codex) authors Tracy's sidecar
**Then** `_bmad/memory/bmad-agent-tracy/` directory lands with 4-file BMB pattern: `INDEX.md` (essential context loaded on activation) + `PERSONA.md` (full BMB persona) + `chronology.md` (session and production-run history) + `access-boundaries.md` (read/write/deny zones) (FR93)
**And** the sidecar is wired into Tracy's SKILL.md activation order.

**Given** the live LLM-only binding (no third-party API; sandbox-AC inventory entry NOT required for Tracy specifically per R5 Amelia-scope-amendment)
**When** Tracy invokes its `_act` body
**Then** the LLM call is made against `gpt-5.4` with no live-API import (per `scripts/utilities/detect_live_api_in_tests.py` AST scan).

**Given** the SG-4 sanctum-alignment requirement (option-a required at port per `slab7bSpecialistRoster.specialists.tracy.sanctumAlignment`)
**When** the dev-agent (Codex) commits Tracy port-shape
**Then** `skills/bmad-agent-tracy/SKILL.md` is option-a sanctum-aligned + sanctum dir is the 4-file sidecar pattern (matches Class-C+ contract; reviewer verifies)
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Tracy.

**Given** the FR105 per-specialist parity-test requirement
**When** the dev-agent (Codex) authors `tests/parity/test_tracy_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-C+ live-API + cache-hit-rate parity + sidecar-emission parity (per NFR-I12 Class-C+ template).

**Given** the cache-hit-rate harness requirement (FR106)
**When** the dev-agent wires Tracy into the harness
**Then** harness runs N=10; `median[2:] >= 85%` post-warm-up.

**Given** the Codex deployment binding (NFR-CG17)
**When** the story is authored
**Then** Codex authors per Slab 2b.1 TEMPLATE pattern + Claude reviews via `bmad-code-review` mutual-handoff (NFR-CG16).

**Wave-2b close tripwire (Amelia A3 amendment from Round (a)):** if Tracy lands >2.7K LOC, K-aggregate tripwire fires → Wave 3 first port-shape (Gary) opens at upper-band K-target + Wave-3 second + third stories pre-authorized for dual-gate escalation.

**Standing-guardrail enforcement:** SG-1 unchanged (Tracy in roster floor); SG-2 Pass-2 enrichment row preserved + status improved; SG-3 Composition Spec §3.5/§3.6/§10 Decision Log entry per NFR-CG15; SG-4 option-a sanctum-aligned at port.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11 / T11a (cache-hit-rate ≥85%) / T11b / T12; NFR-CG13 (no live-API in CI; trivial since LLM-only) / CG14 / CG15 (Decision Log entry) / CG16 / CG17 (Codex authoring) / CG20 (rate-limit budget); NFR-I9 / I10 / I12 / I13.

---

### Story 7b.6: Gary Port-Shape — Gamma API Live Invocation + Per-Slide Variant Generation

As the operator,
I want Gary to execute a Class-C port-shape — Gamma API live invocation + per-slide variant generation (DOUBLE_DISPATCH branch when applicable) + theme-handshake + PNG export normalization (`_materialize_exported_slide_paths` carry-forward) + Vera G3 invocation hooks,
So that Trial-2 reaches G2B with real Gamma slide variants generated per slide and the operator can choose variants in the per-slide review pack.

**Story metadata:** Wave 3 (Class C API-bound; first port-shape; **Codex-authored** per NFR-CG17); single-gate per Slab 2b.1 TEMPLATE; ~2.9K LOC + ~33 tests; FR coverage 6 (FR94 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts; consumes FR107 sandbox-AC inventory entry `gamma`).

**Wave-3 open precondition (Amelia A3 + Mary A2 amendments):** Wave-2b K-aggregate tripwire status check — if Tracy exceeded 2.7K LOC, Gary opens at upper-band K-target; otherwise standard K-target. Sandbox-AC inventory entry for `gamma` is LANDED Wave 0 (FR107); precondition satisfied.

**Acceptance Criteria:**

**Given** Gary's pre-Slab-7b passthrough state
**When** the dev-agent (Codex) authors Gary's port-shape
**Then** `app/specialists/gary/_act.py` lands with the 9-node scaffold per Slab 2b.1 TEMPLATE
**And** Gary's `_act` body invokes the Gamma API (`GammaClient.generate_deck(...)` carry-forward from `scripts/api_clients/gamma_client.py`) per FR94 contract.

**Given** the per-slide variant generation requirement
**When** Gary runs against a per-slide directive
**Then** the DOUBLE_DISPATCH branch fires when applicable (per Gamma API mastery module)
**And** theme-handshake is performed via `GammaClient.list_themes()` (live-tested 2026-03-30 era)
**And** PNG export normalization via `_materialize_exported_slide_paths` (carry-forward from `skills/gamma-api-mastery/scripts/gamma_operations.py:1338`).

**Given** Vera's G3 fidelity check requirement (per FR91 hardening)
**When** Gary completes per-slide variant generation
**Then** Vera G3 invocation hooks fire with real Gamma artifacts as input (FR94 + FR91 cross-cut).

**Given** the live-API-on-CI strict prohibition (NFR-CG13)
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/gary/` use VCR cassettes under `tests/fixtures/specialist-replay/gary/` per NFR-T10
**And** `scripts/utilities/detect_live_api_in_tests.py` AST-scan passes (no `from gamma_client import` patterns in CI test files).

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent (Codex) commits Gary port-shape
**Then** `skills/bmad-agent-gamma/SKILL.md` is option-a sanctum-aligned + sanctum dir at `_bmad/memory/bmad-agent-gary/` carries 6-file BMB pattern
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Gary.

**Given** the FR105 per-specialist parity-test requirement
**When** the dev-agent (Codex) authors `tests/parity/test_gary_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-C live-API + cache-hit-rate parity (per NFR-I12 Class-C template).

**Given** the cache-hit-rate harness (FR106)
**When** the harness runs against Gary
**Then** `median[2:] >= 85%` post-warm-up.

**Given** the credential-rotation register (NFR-CG19)
**When** the dev-agent commits Gary port-shape
**Then** `state/config/credential-rotation-register.yaml` carries a row for Gamma API (owner / rotation cadence / last-rotated / next-due / secret-store reference)
**And** per-specialist rate-limit budget (NFR-CG20) declared in `app/specialists/gary/config.yaml`.

**Operator-gated AC-6-B (Completion Notes evidence):** operator runs T5 live canary against real Gamma API ≤3 invocations (per NFR-T11b cap); cost ≤$0.40 per canary; evidence pasted into Completion Notes once.

**Wave-3 first-port tripwire (Amelia A3):** if Gary lands >2.7K LOC, Wave-3 second + third stories (Kira + Enrique) escalate to dual-gate.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 G2B variant-generation row preserved + status improved; SG-3 Composition Spec §3.5/§3.6/§10 Decision Log per NFR-CG15; SG-4 option-a sanctum-aligned at port.

**Story-scoped NFR predicates:** NFR-T9 / T10 (VCR cassettes) / T11a (cache-hit-rate) / T11b (≤3 live canaries) / T12; NFR-CG12 (sandbox-AC inventory consumed) / CG13 (no live-API in CI) / CG14 / CG15 / CG16 / CG17 (Codex) / CG19 (credential register) / CG20 (rate-limit budget); NFR-I9 / I10 / I12 / I13.

---

### Story 7b.7: Kira Port-Shape — Kling API Live Invocation + Motion Generation

As the operator,
I want Kira to execute a Class-C port-shape — Kling API live invocation + motion generation per `motion_plan.yaml` + per-slide `.progress.json` + terminal `.json` receipts + reviewer inspection pack at `[BUNDLE_PATH]/recovery/inspection/` + fail-closed budget rules,
So that Trial-2 reaches G2F with real Kira motion clips generated per the motion plan and the operator can review motion-vs-narration coherence in the per-slide review pack.

**Story metadata:** Wave 3 (Class C API-bound; parallelizable with 7b.6, 7b.8; **Codex-authored**); single-gate per Slab 2b.1 TEMPLATE (or dual-gate if Wave-3 first-port tripwire fired); ~2.9K LOC + ~33 tests; FR coverage 6 (FR95 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts; consumes FR107 sandbox-AC `kling`).

**Acceptance Criteria:**

**Given** Kira's pre-Slab-7b passthrough state
**When** the dev-agent (Codex) authors Kira's port-shape
**Then** `app/specialists/kira/_act.py` lands with the 9-node scaffold per Slab 2b.1 TEMPLATE
**And** Kira's `_act` body invokes the Kling API per FR95 contract.

**Given** Kira running against a `motion_plan.yaml` directive
**When** Kira generates motion per slide
**Then** per-slide `.progress.json` (intermediate; live progress) AND terminal `.json` receipts (final; success/failure) land under `[BUNDLE_PATH]/motion/` (FR95)
**And** reviewer inspection pack is emitted at `[BUNDLE_PATH]/recovery/inspection/` (FR95).

**Given** the fail-closed budget rules (per FR95)
**When** Kira's per-slide motion budget is exceeded
**Then** Kira aborts cleanly with a terminal `.json` receipt carrying failure reason; no silent-degradation (NFR-CG20).

**Given** the live-API-on-CI strict prohibition (NFR-CG13)
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/kira/` use VCR cassettes; `detect_live_api_in_tests.py` passes.

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent (Codex) commits Kira port-shape
**Then** `skills/bmad-agent-kling/SKILL.md` is option-a sanctum-aligned + sanctum dir at `_bmad/memory/bmad-agent-kira/` carries 6-file BMB pattern
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Kira.

**Given** the FR105 per-specialist parity-test
**When** the dev-agent (Codex) authors `tests/parity/test_kira_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-C live-API + cache-hit-rate parity.

**Given** the cache-hit-rate harness (FR106)
**When** the harness runs against Kira
**Then** `median[2:] >= 85%` post-warm-up.

**Given** the credential-rotation register (NFR-CG19) + rate-limit budget (NFR-CG20)
**When** the dev-agent commits Kira port-shape
**Then** Kling API entries land in both registers.

**Operator-gated AC-7-B:** operator runs T5 live canary ≤3; cost ≤$0.40 per canary; evidence in Completion Notes.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 G2F row preserved + status improved; SG-3 §3.5/§3.6/§10; SG-4 option-a.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11a / T11b / T12; NFR-CG12 / CG13 / CG14 / CG15 / CG16 / CG17 / CG19 / CG20; NFR-I9 / I10 / I12 / I13.

---

### Story 7b.8: Enrique Port-Shape — ElevenLabs API + Voice-Selection HIL Contract

As the operator,
I want Enrique to execute a Class-C port-shape — ElevenLabs API live invocation + voice-preview/voice-selection HIL contract (`voice-preview-options.json` + `voice-selection-review.md` + `voice-selection.json` artifact write) + manifest-driven narration on locked package + assembly-bundle build (`assembly-bundle/audio/` + `captions/`) + per-segment progress to stderr,
So that Trial-2 reaches G2 with real Enrique narration audio + captions and the operator selects the voice via the HIL contract.

**Story metadata:** Wave 3 (Class C API-bound; parallelizable with 7b.6, 7b.7; **Codex-authored**); single-gate per Slab 2b.1 TEMPLATE; ~2.9K LOC + ~33 tests; FR coverage 7 (FR97 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts; consumes FR107 sandbox-AC `elevenlabs`).

**Acceptance Criteria:**

**Given** Enrique's pre-Slab-7b passthrough state
**When** the dev-agent (Codex) authors Enrique's port-shape
**Then** `app/specialists/enrique/_act.py` lands with the 9-node scaffold per Slab 2b.1 TEMPLATE
**And** Enrique's `_act` body invokes the ElevenLabs API per FR97 contract.

**Given** the voice-selection HIL contract
**When** Enrique runs voice-preview
**Then** `voice-preview-options.json` is emitted with N candidate voices per the run-constants
**And** the operator reviews via `voice-selection-review.md` (markdown viewer)
**And** the operator's selection lands in `voice-selection.json` per FR97 contract.

**Given** the manifest-driven narration on locked package
**When** Enrique generates narration per the storyboard's locked manifest
**Then** narration audio + captions land in `assembly-bundle/audio/` + `captions/` per FR97
**And** per-segment progress is emitted to stderr.

**Given** the live-API-on-CI strict prohibition (NFR-CG13)
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/enrique/` use VCR cassettes; `detect_live_api_in_tests.py` passes.

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent (Codex) commits Enrique port-shape
**Then** `skills/bmad-agent-elevenlabs/SKILL.md` is option-a sanctum-aligned + sanctum dir at `_bmad/memory/bmad-agent-enrique/` carries 6-file BMB pattern
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Enrique.

**Given** the FR105 per-specialist parity-test
**When** the dev-agent authors `tests/parity/test_enrique_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-C live-API + cache-hit-rate parity + voice-selection HIL contract write parity.

**Given** the cache-hit-rate harness (FR106) + credential register (CG19) + rate-limit budget (CG20)
**When** the dev-agent commits Enrique port-shape
**Then** harness runs N=10 with `median[2:] >= 85%`; ElevenLabs API entries in both registers.

**Operator-gated AC-8-B:** operator runs T5 live canary ≤3; cost ≤$0.40; evidence in Completion Notes.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 G2 narration row preserved + status improved; SG-3 §3.5/§3.6/§10; SG-4 option-a.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11a / T11b / T12; NFR-CG12 / CG13 / CG14 / CG15 / CG16 / CG17 / CG19 / CG20; NFR-I9 / I10 / I12 / I13.

---

### Story 7b.9: Wanda Port-Shape Onto Scaffold — Wondercraft API + Podcast Bed Generation

As the operator,
I want Wanda to execute a Class-C port-shape onto the scaffold-v0.2 (closes the pre-Slab-2b client-landed-not-on-scaffold gap) — Wondercraft API live invocation + podcast/audio bed generation scoped into the storyboard's audio track,
So that Trial-2 reaches G2 with real Wanda podcast beds in the storyboard's audio track and the scaffold-alignment gap closes.

**Story metadata:** Wave 4 (Class C; serial after Wave 3 OR parallelizable with Wave-3 tail; **Codex-authored**); single-gate; ~2.9K LOC + ~33 tests; FR coverage 6 (FR96 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts; consumes FR107 sandbox-AC `wondercraft`).

**Acceptance Criteria:**

**Given** Wanda's pre-Slab-2b client-landed-not-on-scaffold state
**When** the dev-agent (Codex) authors Wanda's port-shape onto scaffold
**Then** `app/specialists/wanda/_act.py` lands aligned with scaffold-v0.2 per FR96
**And** Wanda's `_act` body invokes the Wondercraft API.

**Given** the podcast/audio bed generation scope
**When** Wanda runs against a storyboard directive
**Then** podcast beds land in the storyboard's audio track scope (per FR96)
**And** beds integrate with Enrique's narration in `assembly-bundle/audio/` (downstream cohesion).

**Given** the live-API-on-CI strict prohibition (NFR-CG13)
**When** the dev-agent (Codex) authors tests
**Then** `tests/specialists/wanda/` use VCR cassettes.

**Given** the SG-4 sanctum-alignment requirement
**When** the dev-agent (Codex) commits Wanda port-shape
**Then** `skills/bmad-agent-wondercraft/SKILL.md` is option-a sanctum-aligned + sanctum dir at `_bmad/memory/bmad-agent-wanda/` carries 6-file BMB pattern.

**Given** the FR105 per-specialist parity-test
**When** the dev-agent authors `tests/parity/test_wanda_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-C live-API + cache-hit-rate parity.

**Given** the cache-hit-rate harness (FR106) + credential register (CG19) + rate-limit budget (CG20)
**When** the dev-agent commits Wanda port-shape
**Then** harness runs N=10 with `median[2:] >= 85%`; Wondercraft API entries in both registers.

**Operator-gated AC-9-B:** operator runs T5 live canary ≤3; cost ≤$0.40; evidence in Completion Notes.

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 audio-bed row preserved + status improved; SG-3 §3.5/§3.6/§10; SG-4 option-a.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11a / T11b / T12; NFR-CG12 / CG13 / CG14 / CG15 / CG16 / CG17 / CG19 / CG20; NFR-I9 / I10 / I12 / I13.

---

### Story 7b.10: Dan Greenfield (Class D1) — Creative-Director Aux Contributions

As the operator,
I want Dan to be created from scratch via `bmad-create-specialist` — SKILL.md (option-a sanctum-aligned) + sidecar at `_bmad/memory/bmad-agent-dan/` with full BMB pattern + `app/specialists/dan/` directory with scaffold-v0.2 + `_act` body shaped as narrow-lane creative-director aux contributions threaded across G1–G2,
So that Trial-2 carries real creative-director aux contributions at the G1 lesson-plan + G1A scope-lock + G2 storyboard gates and the `dan-api-tbd` inventory entry resolves at story-T1.

**Story metadata:** Wave 5a (Class D1 LLM-greenfield; parallelizable with Wave 5b after Waves 1-3 *closed* per R8 Winston-amendment; Claude-authored); single-gate; ~3.5K LOC + ~40 tests; FR coverage 6 (FR98 primary; FR100/FR101/FR102/FR105/FR113 cross-cuts).

**T1-readiness precondition:** sandbox-AC `dan-api-tbd-pending` inventory entry resolved at story-T1 — operator + dev-agent decide LLM-only vs third-party-API. If LLM-only, sandbox-AC entry retired (Tracy precedent); if third-party-API, entry promoted to active per FR107 contract.

**Acceptance Criteria:**

**Given** Dan's pre-Slab-7b sidecar-only state (no `app/specialists/dan/` directory)
**When** the dev-agent invokes `bmad-create-specialist` for Dan
**Then** the workflow produces: `skills/bmad-agent-dan/SKILL.md` + sanctum dir at `_bmad/memory/bmad-agent-dan/` (6-file BMB pattern) + `app/specialists/dan/` directory with scaffold-v0.2 (per FR98 + Errata 2).

**Given** the narrow-lane creative-director aux contributions shape
**When** Dan runs at G1 / G1A / G2
**Then** Dan emits aux contributions threaded across the gates (per FR98) — NOT a primary lesson-plan/storyboard contribution; Dan supplements Irene + Quinn-R/Vera primary roles (per `slab7bSpecialistRoster.specialists.dan.actBodyShape`).

**Given** the `dan-api-tbd` resolution at story-T1
**When** the operator + dev-agent decide
**Then** the decision is recorded in `docs/dev-guide/migration-ac-sandbox-inventory.json`: if LLM-only, `dan-api-tbd-pending` entry retired; if third-party-API, entry promoted with API name + FR98 cross-reference (FR98 + FR107)
**And (Mary C1 / B1 follow-through)** if Dan resolves to third-party-API, sandbox-AC inventory promotion requires **party-mode consensus + governance-JSON version bump pre-dev**; the dev-agent does NOT unilaterally promote (per FR107 R5 Amelia-scope-amendment — additions to `dev_agent_available` require party-mode; additions to `dev_agent_forbidden` are dev-agent authority).

**Given** the SG-4 sanctum-alignment requirement (option-a required at creation per `slab7bSpecialistRoster.specialists.dan.sanctumAlignment`)
**When** the dev-agent commits Dan greenfield
**Then** `skills/bmad-agent-dan/SKILL.md` is option-a sanctum-aligned + sanctum dir is the 6-file BMB pattern (not 4-file sidecar variant; Dan is Class D1 LLM-greenfield, not D2 pipeline-greenfield)
**And** `tests/parity/test_skill_md_sanctum_alignment.py` passes for Dan.

**Given** the FR105 per-specialist parity-test
**When** the dev-agent authors `tests/parity/test_dan_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-D1 first-recorded-fixture-set parity (per NFR-I12 Class-D1 template — first-recorded fixtures since no prior `app/specialists/dan/` existed).

**Given** the cache-hit-rate harness (FR106; ten LLM specialists incl. Dan)
**When** the dev-agent wires Dan into the harness
**Then** harness runs N=10 with `median[2:] >= 85%` post-warm-up.

**Given** the sandbox-AC inventory governance
**When** the dev-agent's ACs are validated
**Then** no forbidden CLI; if Dan resolves to third-party-API, sandbox-AC entry promoted before any API-bound dev work.

**Operator-gated AC-10-B (conditional on third-party-API resolution; John C-observation tightening):** IF Dan resolves to LLM-only at story-T1, AC-10-B is N/A and removed from Completion Notes. IF Dan resolves to third-party-API, AC-10-B activates: operator runs T5 live canary ≤3; cost ≤$0.40 per canary; evidence pasted into Completion Notes.

**Standing-guardrail enforcement:** SG-1 unchanged (Dan in roster floor; sidecar-only → fully activated); SG-2 G1/G1A/G2 aux-contribution rows added (per ~28 row improvements claim); SG-3 §3.5/§3.6/§10 Decision Log per NFR-CG15; SG-4 option-a sanctum-aligned at creation.

**Story-scoped NFR predicates:** NFR-T9 / T10 / T11a / T11b (conditional) / T12; NFR-CG12 (conditional) / CG13 (conditional) / CG14 / CG15 / CG16 / CG17 (Claude per D21) / CG19 (conditional) / CG20 (conditional); NFR-I9 / I10 / I12 / I13.

---

### Story 7b.11: Compositor Greenfield (Class D2 Sidecar Variant) — Deterministic Assembly Pipeline

As the operator,
I want Compositor to be activated per the **Class-D2 sidecar variant** of the BMB regime (canonical, NOT exception per D20) — SKILL.md aligned per scaffold-v0.2-D2-pipeline contract + `app/specialists/compositor/` directory + `_act` body shaped as deterministic assembly pipeline + `sync-visuals` operation + `DESCRIPT-ASSEMBLY-GUIDE.md` regeneration + localized stills + motion under `assembly-bundle/visuals/` + `motion/` + pipeline-determinism harness ≥99% rate,
So that Trial-2 reaches G3 with a deterministic Compositor `DESCRIPT-ASSEMBLY-GUIDE.md` regenerated against real assets and the operator can hand off to Descript without per-run drift.

**Story metadata:** Wave 5b (Class D2 pipeline-greenfield; parallelizable with Wave 5a after Waves 1-3 *closed*; Claude-authored); single-gate; ~3.5K LOC + ~40 tests; FR coverage 6 (FR99 primary; FR100/FR102/FR105/FR113 cross-cuts; **EXEMPT from FR101 sanctum-path-equality clause per D20** — Compositor uses Class-D2 sidecar variant; no `# Sanctum exception` block required).

**T1-readiness precondition:** scaffold-v0.2-D2-pipeline LANDED Wave 0 (FR111; path-corrected per Errata 1); Compositor consumes `docs/dev-guide/scaffolds/scaffold-v0.2-D2-pipeline/` 7 files: README.md, scaffold.yaml, field-mask.yaml, contract.md.template, version.md.template, chronology.md.template, access-boundaries.md.template, pipeline-determinism.md.template.

**Pre-T1 K-projection check (Amelia C2 / B2 follow-through):** dev-agent estimates LOC at story-open T1; if T1 LOC estimate **>4K**, story escalates to dual-gate per Round (b) Amelia B2 amendment (greenfield-uplift K-bump risk; pipeline-determinism harness + 7-file scaffold consumption + sidecar variant authoring may exceed 3.5K target). Tripwire status logged in `_bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md` Completion Notes.

**Acceptance Criteria:**

**Given** Compositor's pre-Slab-7b skill-only state (no `app/specialists/compositor/` directory)
**When** the dev-agent authors Compositor greenfield
**Then** `app/specialists/compositor/` directory lands with scaffold-v0.2-D2-pipeline alignment (FR99 + FR111)
**And** `_act` body is a deterministic assembly pipeline (NO LLM call per `slab7bSpecialistRoster.specialists.compositor.actBodyShape`).

**Given** the Class-D2 sidecar variant contract
**When** the dev-agent authors Compositor's sidecar
**Then** the sidecar is OPERATIONAL-METADATA-shaped (NOT persona-shaped continuity per D20): `contract.md` + `version.md` + `chronology.md` (recording pipeline-runs) + `access-boundaries.md` (recording read/write directories) (FR99)
**And** the sidecar consumes the scaffold templates rather than the 6-file BMB pattern (Compositor is the seed exemplar for Class D2).

**Given** the `sync-visuals` operation
**When** Compositor runs against an authorized storyboard
**Then** localized stills land under `assembly-bundle/visuals/` + motion under `assembly-bundle/motion/` per FR99
**And** the output is bytes-identical across runs given fixed inputs (per H-Pipeline determinism contract).

**Given** the `DESCRIPT-ASSEMBLY-GUIDE.md` regeneration
**When** Compositor runs `assembly-guide` operation
**Then** the guide regenerates with field-masked-hash determinism modulo `{generated_at, run_id, build_timestamp}` per R3 Amelia-amendment (FR99)
**And** field-mask convention defined in `field-mask.yaml` per scaffold-v0.2-D2-pipeline.

**Given** the pipeline-determinism harness (FR106 H-Pipeline; NOT cache-hit-rate)
**When** the dev-agent wires Compositor into the harness
**Then** ≥99% rate across N=10 runs (bytes-identical for `sync-visuals`; field-masked-hash for `DESCRIPT-ASSEMBLY-GUIDE.md` modulo declared-nondeterministic fields)
**And** failure is hard-block; no flake tolerance (per D17 H-Pipeline contract).

**Given** the SG-4 sanctum-alignment requirement (Class-D2 exempt from option-a sanctum-path-equality per D20)
**When** the dev-agent commits Compositor greenfield
**Then** `skills/compositor/SKILL.md` aligns per scaffold-v0.2-D2-pipeline contract (FR111) — NO `# Sanctum exception` block required (D20 first-class taxonomy bin)
**And** `tests/parity/test_skill_md_sanctum_alignment.py` for Compositor follows the D2 branch (asserts Class-D2 sidecar variant contract per FR101.iv, NOT sanctum-path-equality).

**Given** the FR105 per-specialist parity-test
**When** the dev-agent authors `tests/parity/test_compositor_activation_contract.py`
**Then** the test inherits `SanctumParityTestBase` AND asserts Class-D2 pipeline-determinism parity (per NFR-I12 Class-D2 template — H-Pipeline ≥99% rate; bytes-identical / field-masked-hash discipline).

**Given** the substrate-as-floor invariant (FR113 + NFR-I13)
**When** the dev-agent's diff is reviewed
**Then** no diff hunk touches `app/marcus/orchestrator/dispatch_adapter.py:70–95` — Compositor calls *across* the boundary using existing dispatch APIs.

**Standing-guardrail enforcement:** SG-1 unchanged (Compositor in roster floor; skill-only → fully activated); SG-2 G3 assembly + sync-visuals rows added (per ~28 row improvements claim); SG-3 §3.5/§3.6/§10 Decision Log + §11 migration triggers (Class-D2 sidecar variant is a §11 trigger); SG-4 Class-D2 first-class taxonomy bin (D20).

**Story-scoped NFR predicates:** NFR-T9 / T10 / T12; NFR-CG14 / CG15 / CG16; NFR-I9 (D2 branch) / I10 / I11 / I12 (Class-D2 template) / I13 (substrate-frozen-paths).

---

### Story 7b.12: Slab 7b Integration + Parity-Test Suite Aggregation + Closeout (Wave 6; Dual-Gate)

As the operator,
I want Slab 7b to close with an integration story that aggregates the per-specialist parity-test suite + asserts NFR coverage + lands the per-specialist operator-reference docs + sanctum-alignment matrix + ~28 mapping-checklist row improvements + 5-API live-binding smoke evidence + trial-2 cost-projection dry-run,
So that Trial-2 launches with auditable evidence that all eleven specialists are activated per their class-shaped contracts and SG-1/SG-2/SG-3/SG-4 are all green.

**Story metadata:** Wave 6 (integration; strict-last; **dual-gate** per Slab 7a 7a.8 precedent + Murat's integration-tier risk argument; Claude-authored); ~3K LOC + ~25 active tests; FR coverage 8 (FR88/FR101/FR102/FR103/FR104/FR105/FR106/FR107 aggregation + NFR-CG12-CG20 closeout block + NFR-I9-I13 closeout block + NFR-OD3-OD6 closeout block).

**Acceptance Criteria:**

**Given** the FR101 + FR102 parity-test aggregation
**When** the dev-agent authors `tests/parity/test_skill_md_sanctum_alignment.py` final form
**Then** all eleven specialists pass (Texas / Quinn-R / Vera / Irene / Tracy / Gary / Kira / Wanda / Enrique / Dan option-a; Compositor Class-D2 branch)
**And** the test runs <120s aggregate per NFR-T12 SLA on standard CI runner
**And** `.github/workflows/specialist-parity.yml` is bound as required check (NFR-I9).

**Given** the FR105 per-specialist activation-contract suite
**When** the dev-agent authors `tests/parity/test_eleven_specialists_addressable.py` (SG-1 aggregator)
**Then** all 11 individual tests pass (per Class-shaped templates per NFR-I12)
**And** `.github/workflows/activation-contract.yml` is bound as required check (NFR-I10).

**Given** the FR103 + NFR-OD4 sanctum-alignment matrix
**When** the dev-agent authors the matrix docs
**Then** `docs/dev-guide/specialist-sanctum-alignment-matrix.md` (dev-doc) AND `docs/operator/specialists/sanctum-alignment-matrix.md` (operator-doc) both exist with 11 rows (one per specialist + alignment-or-exception verdict + rationale link).

**Given** the FR104 operator-control parity table extension
**When** the dev-agent authors the +11 rows
**Then** `docs/operator/legacy-vs-langgraph-control-parity.md` carries 11 new rows (one per specialist body activation; legacy lever → migrated lever → back-compat shim status → end-to-end test pointer per FR110 template).

**Given** the NFR-OD3 per-specialist operator-reference docs
**When** the dev-agent authors the 11 docs
**Then** `docs/operator/specialists/<name>.md` exists for each of the 11 activated specialists (OPERATOR / INPUTS / OUTPUTS / REFERENCE four-section structure per Slab 7a 7a.7 precedent).

**Given** the NFR-I11 mapping-checklist row-status invariant
**When** the dev-agent authors `tests/parity/test_mapping_checklist_status.py`
**Then** the test asserts ~28 row improvements (per A-10 R3 amendment) on rows owned by activated specialists; deferred rows (§05B / §6.2 / §6.3 / §7.5 / §14.5 / §15) retain pre-Slab-7b status legend
**And** `.github/workflows/mapping-checklist.yml` is bound as required check.

**Given** the FR106 cache-hit-rate harness aggregation (10 LLM specialists + 1 Compositor pipeline-determinism)
**When** the dev-agent runs the harnesses at green-light cadence
**Then** all 10 LLM specialists report `median[2:] >= 85%` post-warm-up + Compositor reports H-Pipeline ≥99% rate
**And** harness evidence pasted into Completion Notes (operator-gated per NFR-T11a).

**Given** the trial-2 cost-projection dry-run (John A1 amendment from Round (a); SR-T6 mitigation)
**When** the dev-agent runs the cost-projection
**Then** projected Trial-2 cost ≤ BS-3 ceiling (per Journey 5 fork)
**And** if projection exceeds ceiling, the story HALTs with one of four named remediation paths (scope-cut / budget-exception / trial-redesign / Slab-7c precondition) + party-mode escalation.

**Given** the 5-API live-binding smoke (Wave 6 operator-gated)
**When** the operator runs the 5-API smoke (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-resolved)
**Then** each API responds 200-OK with valid response shape; cost per API call ≤ $0.40
**And** smoke evidence pasted into Completion Notes (operator-gated AC-12-B style).

**Given** the substrate-frozen-paths-check (FR113 + NFR-I13)
**When** the dev-agent commits the integration story
**Then** `.github/workflows/substrate-frozen-paths-check.yml` is landed + bound as required check; no diff hunk touches frozen paths absent ceremony.

**Given** the credential-rotation register (NFR-CG19) + rate-limit budgets (NFR-CG20)
**When** the dev-agent runs the closeout audit
**Then** `state/config/credential-rotation-register.yaml` carries 5 rows (gamma / kling / elevenlabs / wondercraft / dan-api-tbd-resolved); per-specialist rate-limit budget declared in each `app/specialists/<name>/config.yaml`.

**Given** the NFR-OD6 codex-scope-audit
**When** the closeout CI run executes
**Then** `.github/workflows/codex-scope-audit.yml` passes — no workflow file references `codex` or invokes Codex CLI absent governance-JSON entry.

**Given** the BMAD sprint governance (CLAUDE.md)
**When** the integration story closes
**Then** `bmad-retrospective` runs; `_bmad-output/planning-artifacts/deferred-inventory.md` updated with Slab 7b-closing follow-ons; `next-session-start-here.md` updated with Trial-2 launch hot-start; `_bmad-output/implementation-artifacts/sprint-status.yaml` reflects all 12 stories DONE.

**Dual-gate rationale (Slab 7a 7a.8 precedent + Murat integration-tier):** integration story carries cross-story failure modes that justify conservative dual-gate review; Wave 6 dual-gate flipped from single per Murat's structural-enforcement amendment.

**MVP Exit Gate verification (R8 amendment):** Trial-2 reaches **G2 cleanly with real content from ≥9-of-11 specialists (≥3 per class)**; no fixture-stub fallback; no silent gate-bypass; SG-1/SG-2/SG-3 all green (SG-4 verified at Slab close, not MVP exit).

**Slab 7b Close Gate verification (full-scope):** Trial-2 reaches **G3 cleanly with real content from all 11 specialists** (cascade-reading verified per R8 Mary clarification — visible-content surfaces from 9 standalone-row specialists PLUS Pass-2-internal contributions from Wanda + Tracy verifiable via cascade audit logs); no mapping-checklist regression; SG-1/SG-2/SG-3/SG-4 all green.

**Standing-guardrail enforcement:** **SG-1 aggregate enforcement** (`test_eleven_specialists_addressable.py`); **SG-2 aggregate enforcement** (`test_mapping_checklist_status.py` + ~28 row improvements assertion); **SG-3 aggregate enforcement** (`test_composition_spec_invariants.py` carry-forward + NFR-I8 carry-forward); **SG-4 aggregate enforcement** (FR101 parity-test + NFR-I9 + sanctum-alignment matrix doc).

**Story-scoped NFR predicates (closeout block):** NFR-T9 / T10 / T11 / T11a / T11b / T12; **NFR-CG12 / CG13 / CG14 / CG15 / CG16 / CG17 / CG18 / CG19 / CG20** (full block); **NFR-I9 / I10 / I11 / I12 / I13** (full block); **NFR-OD3 / OD4 / OD5 / OD6** (full block).

---

**End of Step 3 dev-story decomposition (12 stories authored; 4 Round (a) amendments folded; 26/26 FR coverage + 24/24 NFR coverage verified inline).**

---

## Party-Mode Round (b) — Story-Roster Ratification (Class-Coverage + Author-Binding + Per-Wave K-Targets)

**Convened:** 2026-04-29 (Step 3 mid-pre-Round-(c)).
**Voices:** John (PM), Mary (analyst/scope-floor), Amelia (dev-shape/K-target), Murat (test-shape/parity-test).
**Mandate:** ratify the 12-story roster — class-coverage parity to PRD §FR88; per-story author-binding parity to NFR-CG17 + D21; per-wave K-target distribution within R8 Mary's 24-30 band; no missing FR88 specialist.

### Round (b) verdicts

**John (PM):** GREEN.
> "All 11 specialists from FR88 named in 12 dev stories (Compositor at Wave 5b; Dan at 5a; Tracy at 2b; Wanda at 4; Gary/Kira/Enrique at Wave 3; Irene Pass-1 at 2a; Texas/Quinn-R/Vera at Wave 1; integration at Wave 6). MVP Exit Gate (G2 + 9-of-11) verifiable at Wave 6 (12 stories - integration = 11 body activations). No specialist orphaned. Story 7b.12 explicitly carries the trial-2 cost-projection dry-run AC per A1. **GREEN**."

**Mary (analyst/scope-floor):** GREEN-WITH-ONE-AMENDMENT.
> "FR coverage verification: 26/26 FRs cited across the 12 stories + 6 Wave-0 LANDED. NFR coverage: NFR-T9/T10/T11/T11a/T11b/T12 cross-cut; NFR-CG12-CG20 + NFR-I9-I13 + NFR-OD3-OD6 aggregated to 7b.12 closeout block (correct per R7 Murat NFR-binding-to-CI-workflow rule). **Amendment:** Story 7b.10 (Dan) — the `dan-api-tbd-pending` resolution at story-T1 should be **explicitly party-mode-gated** if it resolves to third-party-API (per FR107 R5 Amelia-scope-amendment — sandbox-AC inventory additions to `dev_agent_forbidden` are dev-agent authority but additions to `dev_agent_available` require party-mode consensus). Add an AC clause: 'if Dan resolves to third-party-API, sandbox-AC inventory promotion requires party-mode consensus + governance-JSON version bump pre-promotion.' Otherwise GREEN."

**Amelia (dev-shape/K-target):** GREEN-WITH-ONE-CONCERN.
> "Per-wave K-target distribution: Wave 1 (3 × 2K = 6K) + Wave 2a (2.5K) + Wave 2b (3.3K) + Wave 3 (3 × 2.9K = 8.7K) + Wave 4 (2.9K) + Wave 5a (3.5K) + Wave 5b (3.5K) + Wave 6 (3K) = **33.4K aggregate** (upper-band). Tripwire clauses (Round (a) A3 amendment) are correctly placed at Wave-1 close + Wave-2b close + Wave-3-first-port (Gary). **Concern:** Story 7b.11 (Compositor Class-D2) at 3.5K is greenfield-uplift — pipeline-determinism harness + 7-file scaffold consumption + sidecar variant authoring may push above 3.5K. **Mitigation:** add an explicit pre-T1 K-projection check at 7b.11 open — if T1 LOC estimate exceeds 4K, story escalates to dual-gate. Otherwise GREEN."

**Murat (test-shape/parity-test):** GREEN.
> "Per-story FR105 parity-test ownership distributed correctly: each body story authors its own `test_<name>_activation_contract.py`; Story 7b.12 aggregates and asserts coverage. Class-shaped templates (per NFR-I12) correctly tagged: 7b.1/7b.2/7b.3 Class-A; 7b.4 Class-B; 7b.5 Class-C+; 7b.6/7b.7/7b.8/7b.9 Class-C; 7b.10 Class-D1; 7b.11 Class-D2. **One observation, not amendment:** 7b.10 (Dan) Class-D1 'first-recorded fixture set' parity test is novel — Dan has no prior `app/specialists/dan/` directory, so 'first-recorded fixtures' need an explicit recording ceremony. The story's T1-readiness already covers `bmad-create-specialist` invocation; the recording happens during dev. Acceptable as-is. **GREEN**."

### Round (b) consensus

**Verdict:** RATIFIED-WITH-AMENDMENTS (4/4 unanimous; 2 amendments to fold at Round (c) AC review).

**Amendments to fold:**
- **(Mary B1):** Story 7b.10 (Dan) — explicit AC clause for sandbox-AC promotion requiring party-mode consensus + governance-JSON version bump if Dan resolves to third-party-API.
- **(Amelia B2):** Story 7b.11 (Compositor) — pre-T1 K-projection check; if T1 LOC estimate >4K, escalate to dual-gate.

**Re-opens:** 0. Story roster proceeds to Round (c) AC adversarial review.

---

## Party-Mode Round (c) — Per-Story AC Adversarial Review (Sandbox-AC + Sanctum-Alignment + Parity-Test + FR Coverage)

**Convened:** 2026-04-29 (Step 3 close pre-Step-4).
**Voices:** John, Mary, Amelia, Murat.
**Mandate:** adversarial review per-story ACs against (i) sandbox-AC discipline (CLAUDE.md — no forbidden CLIs in dev-agent ACs); (ii) SG-4 sanctum-alignment AC presence + class-correct shape; (iii) FR101 parity-test contract per Errata 2; (iv) FR coverage per-story; (v) NFR predicate coverage per Murat's CI-binding rule.

### Round (c) verdicts

**John (PM):** GREEN-WITH-ONE-OBSERVATION.
> "Each per-API-bound story (7b.6 Gary / 7b.7 Kira / 7b.8 Enrique / 7b.9 Wanda) carries an Operator-gated AC-N-B clause for T5 live canary evidence pasting; this matches the 'verify via shipped deps, not operator CLIs' rule from project memory. **Observation:** 7b.10 (Dan) Operator-gated AC-10-B is conditional on third-party-API resolution — if Dan resolves LLM-only, AC-10-B is skipped (no live canary needed). The phrasing 'conditional on third-party-API resolution' is correct but could be tightened — recommend explicit clause 'IF Dan resolves to LLM-only at story-T1, AC-10-B is N/A and removed; IF Dan resolves to third-party-API, AC-10-B activates'. Not a re-open. **GREEN**."

**Mary (analyst/scope-floor):** GREEN-WITH-ONE-AMENDMENT.
> "Sandbox-AC compliance: every dev-agent AC block uses shipped Python deps (`httpx`, `psycopg`, `pytest.skip(...)`); no forbidden CLI (`docker`, `psql`, `gh`, `aws`, `gcloud`, `az`, `kubectl`, `helm`, `redis-cli`, `mongo`, `mysql`, `curl`, `wget`) appears anywhere. **Amendment (B1 follow-through):** the Dan story 7b.10 sandbox-AC promotion clause from Round (b) needs to be wired explicitly — current AC reads 'if Dan resolves to third-party-API, entry promoted with API name + FR98 cross-reference'. Tighten to: 'AC-10 Sandbox-AC promotion: if Dan resolves to third-party-API at story-T1, the inventory promotion requires party-mode consensus + governance-JSON version bump pre-dev; the dev-agent does NOT unilaterally promote.' Otherwise GREEN."

**Amelia (dev-shape/K-target):** GREEN-WITH-ONE-AMENDMENT.
> "FR101 parity-test contract per Errata 2 honored: each story's SG-4 alignment AC names `skills/bmad-agent-{name}/SKILL.md` (NOT `app/specialists/{name}/SKILL.md`); minimal frontmatter (`name` + `description`); sanctum-dir 6-file pattern as alignment marker. Class-D2 Compositor exempt from sanctum-path-equality clause per D20. **Amendment (B2 follow-through):** wire 7b.11 Compositor pre-T1 K-projection check explicitly into the T1-readiness precondition list. Current text says 'scaffold-v0.2-D2-pipeline LANDED Wave 0 ... Compositor consumes ... 7 files'. Add: 'Pre-T1 K-projection check: if T1 LOC estimate >4K, story escalates to dual-gate per Round (b) Amelia B2 amendment.' Otherwise GREEN."

**Murat (test-shape/parity-test):** GREEN.
> "Per-story FR105 + NFR-I9/I10/I12 + NFR-T9/T10/T11/T11a/T11b/T12 coverage verified across all 12 stories. CI-workflow binding rule (R7 Winston/Murat) honored: each NFR with 'MUST pass at PR merge' clause names a workflow file (`.github/workflows/specialist-parity.yml` for NFR-I9; `.github/workflows/activation-contract.yml` for NFR-I10; `.github/workflows/mapping-checklist.yml` for NFR-I11; `.github/workflows/substrate-frozen-paths-check.yml` for NFR-I13; `.github/workflows/codex-scope-audit.yml` for NFR-OD6) — all aggregated to Story 7b.12 closeout. **GREEN**."

### Round (c) consensus

**Verdict:** RATIFIED-WITH-AMENDMENTS (4/4 unanimous; 2 amendments to fold immediately).

**Amendments folded inline below before Step 4 close:**
- **(Mary C1 / B1 follow-through):** Story 7b.10 — sharpened sandbox-AC promotion clause requiring party-mode + governance-JSON version bump.
- **(Amelia C2 / B2 follow-through):** Story 7b.11 — pre-T1 K-projection check wired into T1-readiness precondition list.

**Re-opens:** 0. Per-story ACs proceed to Step 4 final validation + Round (d) ratify-with-amendments-and-close.

---

## Step 4 — Final Validation

### 1. FR Coverage Validation (26/26 ✅)

Per-FR story-assignment cross-check (matches FR Coverage Map; verifies Epic 1's 26 FRs are each cited in ≥1 story):

| FR | Wave / Story | Verified |
|---|---|---|
| FR88 (eleven-specialist roster canonical) | 7b.12 (Wave 6 SG-1 aggregator) | ✅ |
| FR89 (Texas hardening) | 7b.1 (Wave 1) | ✅ |
| FR90 (Quinn-R hardening) | 7b.2 (Wave 1) | ✅ |
| FR91 (Vera hardening) | 7b.3 (Wave 1) | ✅ |
| FR92 (Irene Pass-1 refresh) | 7b.4 (Wave 2a) | ✅ |
| FR93 (Tracy port-shape + sidecar C+) | 7b.5 (Wave 2b) | ✅ |
| FR94 (Gary port-shape) | 7b.6 (Wave 3) | ✅ |
| FR95 (Kira port-shape) | 7b.7 (Wave 3) | ✅ |
| FR96 (Wanda port-shape onto scaffold) | 7b.9 (Wave 4) | ✅ |
| FR97 (Enrique port-shape) | 7b.8 (Wave 3) | ✅ |
| FR98 (Dan greenfield D1) | 7b.10 (Wave 5a) | ✅ |
| FR99 (Compositor greenfield D2 sidecar variant) | 7b.11 (Wave 5b) | ✅ |
| FR100 (SG-4 sanctum-alignment AC per body) | 7b.1 / 7b.2 / 7b.3 / 7b.4 / 7b.5 / 7b.6 / 7b.7 / 7b.8 / 7b.9 / 7b.10 / 7b.11 (all body stories) | ✅ |
| FR101 (parity-test test_skill_md_sanctum_alignment.py) | 7b.1 (creates SanctumParityTestBase per Errata 3) + 7b.12 (aggregates) | ✅ |
| FR102 (parity-test runs at every PR merge) | 7b.12 (Wave 6 closeout; binds .github/workflows/specialist-parity.yml) | ✅ |
| FR103 (sanctum-alignment matrix dev-doc) | 7b.12 (Wave 6 closeout) | ✅ |
| FR104 (operator-control parity table +11 rows) | 7b.12 (Wave 6 aggregation; per-body rows authored at each body story close) | ✅ |
| FR105 (per-specialist parity-test suite) | 7b.1-7b.11 (each body story authors its own) + 7b.12 (asserts coverage) | ✅ |
| FR106 (cache-hit-rate harness 10 + pipeline-determinism harness 1) | 7b.4-7b.10 (LLM specialists wire harness) + 7b.11 (Class-D2 H-Pipeline) + 7b.12 (aggregation) | ✅ |
| FR107 (sandbox-AC inventory +5 entries) | **LANDED Wave 0 commit `9ed6fcb`** | ✅ |
| FR108 (BMB sanctum alignment checklist) | **LANDED Wave 0** | ✅ |
| FR109 (sanctum exception categories closed allowlist) | **LANDED Wave 0** | ✅ |
| FR110 (operator-control parity template) | **LANDED Wave 0** | ✅ |
| FR111 (scaffold-v0.2-D2-pipeline; Errata 1 path-corrected) | **LANDED Wave 0** + consumed by 7b.11 | ✅ |
| FR112 (Cora SKILL.md §Sanctum exception anchor) | **LANDED Wave 0** | ✅ |
| FR113 (Marcus duality boundary frozen) | All 12 dev stories (CI substrate-frozen-paths-check enforces) | ✅ |

**Result: 26/26 FRs covered.** ✅

### 2. NFR Coverage Validation (24/24 ✅)

| NFR Block | Stories | Verified |
|---|---|---|
| NFR-T9..T12 (test discipline) | All 12 stories cross-cutting; 7b.12 aggregates wall-clock SLA | ✅ |
| NFR-CG12..CG20 + CG14a (compliance & governance) | 7b.5-7b.10 (sandbox-AC + Codex + credential register + rate-limit) + 7b.12 closeout | ✅ |
| NFR-I9..I13 (integrity invariants) | 7b.1 (creates parity-test bases) + all body stories (per-specialist tests) + 7b.12 (CI workflow binding) | ✅ |
| NFR-OD3..OD6 (operator documentation) | 7b.12 (Wave 6 closeout aggregation) | ✅ |

**Result: 24/24 NFRs covered.** ✅

### 3. Architecture Implementation Validation

**Starter template setup:** N/A — Slab 7b activates bodies *into* the Slab 7a substrate (CLOSED 2026-04-29 at `95c81b0`). No new starter template needed; specialists consume scaffold-v0.2 (Slab 2b.1 TEMPLATE; per-story scaffold consumption) + scaffold-v0.2-D2-pipeline (FR111; Compositor Class-D2). ✅

**Database/entity creation discipline:** ✅ — no upfront table creation. Per-story per-specialist sidecar dirs (`_bmad/memory/bmad-agent-{name}/`) created only by the specific story that activates that specialist (Tracy creates its sidecar at 7b.5; Dan creates at 7b.10; Wanda/Gary/Kira/Enrique consume existing sidecars). State management runs on Slab 1 Postgres checkpointer; no Slab 7b table additions.

**Substrate-as-floor invariant (D22 + FR113 + NFR-I13):** ✅ — every body story carries an explicit AC asserting `dispatch_adapter.py:70-95` is not touched; CI substrate-frozen-paths-check binds at PR merge. Slab 7b adds bodies, never amends substrate.

### 4. Story Quality Validation

Each of the 12 stories:
- ✅ Single-dev-agent-completable (K-target ≤3.5K LOC; Wave 6 dual-gate at ~3K)
- ✅ Clear acceptance criteria (Given/When/Then format; 6-9 ACs per story; cross-cutting ACs named explicitly per FR + NFR)
- ✅ References specific FRs (primary + cross-cuts called out per-story)
- ✅ Technical details present (file paths, scaffold consumption, SKILL.md location per Errata 2, sanctum-dir 6-file pattern, CI workflow names)
- ✅ No forward dependencies within Epic (verified per dependency-wave structure below)
- ✅ Implementable without waiting for future stories (each Wave's stories complete independently per Wave precedent)

### 5. Epic Structure Validation

**Epic 1 user-value focus:** ✅ — "operator runs Trial-2 end-to-end against the Slab 7a substrate with real content from all eleven specialists." MVP Exit Gate at G2 + 9-of-11 (fast-fail) and Slab Close Gate at G3 + 11 (full-scope).

**Foundation stories scope-bounded:** ✅ — Wave 0 (LANDED) deliverables are governance preconditions, not Epic 1 dev stories; Wave 0.5 Codex deployment verification is operator-gated.

**No big upfront technical work:** ✅ — Story 7b.1 (Texas) carries 4 T1-readiness preconditions (SanctumParityTestBase + chain-test base + class-conformance validator + Errata 4 ratification) that are minimal scaffolding for downstream stories, not standalone setup work.

### 6. Dependency Validation

**Epic Independence Check:** Slab 7b is one Epic; cross-Epic dependencies are upstream-only (Slab 1-6 SHIPPED + Slab 7a CLOSED). No future epic (Doc-7-D prose harvest) is required for Epic 1 to function. ✅

**Within-Epic Story Dependency Check (per Wave):**

| Wave | Story | Depends only on | ✅ |
|---|---|---|---|
| 1 | 7b.1 Texas | Wave 0 LANDED + Wave 0.5 verify | ✅ |
| 1 | 7b.2 Quinn-R | Wave 0 LANDED + Wave 0.5 verify (parallel with 7b.1) | ✅ |
| 1 | 7b.3 Vera | Wave 0 LANDED + Wave 0.5 verify (parallel with 7b.1, 7b.2) | ✅ |
| 2a | 7b.4 Irene Pass-1 | Wave 1 closed (Vera G4 rubric needed for Pass-1 mirror) | ✅ |
| 2b | 7b.5 Tracy | Wave 2a closed (Tracy is Pass-2 enrichment companion; needs locked Pass-1 plan) | ✅ |
| 3 | 7b.6 Gary | Wave 0 + Wave 1 (Vera G3 invocation hooks) | ✅ |
| 3 | 7b.7 Kira | Wave 0 + Wave 1 (parallel with 7b.6) | ✅ |
| 3 | 7b.8 Enrique | Wave 0 + Wave 1 (parallel with 7b.6, 7b.7) | ✅ |
| 4 | 7b.9 Wanda | Wave 3 (Wanda integrates with Enrique narration in assembly-bundle/audio/) | ✅ |
| 5a | 7b.10 Dan | Waves 1-3 *closed* per R8 Winston-amendment (Dan threads aux contributions across G1-G2 produced by Irene/Tracy/Gary/Kira) | ✅ |
| 5b | 7b.11 Compositor | Waves 1-3 *closed* (Compositor assembles real Gary/Kira/Enrique/Wanda outputs); parallelizable with 7b.10 | ✅ |
| 6 | 7b.12 Integration | All prior 11 body stories closed (strict-last) | ✅ |

**No forward dependencies. ✅**

### 7. Complete and Save

All Step 4 validations pass. ✅ FR coverage 26/26 ✅; NFR coverage 24/24 ✅; story quality ✅; epic structure ✅; dependencies ✅.

---

## Party-Mode Round (d) — Ratify-with-Amendments-and-Close

**Convened:** 2026-04-29 (Step 4 close).
**Voices:** John, Mary, Amelia, Murat.
**Mandate:** final ratification of the epics-and-stories artifact + closeout-deliverable verification + scope-floor confirmation across all 4 standing guardrails + re-open count assertion.

### Round (d) verdicts

**John (PM):** GREEN — RATIFIED-WITH-AMENDMENTS-AND-CLOSE.
> "MVP Exit Gate (G2 + 9-of-11) + Slab Close Gate (G3 + 11) two-gate structure preserved at story 7b.12. Trial-2 cost-projection dry-run (A1 amendment) wired into 7b.12 closeout. SR-T6/T7/T8/T9 + SR-S1/S2/S3/S4 risks all surfaced via per-wave tripwire clauses + closeout block. **Workflow close: GREEN.**"

**Mary (analyst/scope-floor):** GREEN — RATIFIED-WITH-AMENDMENTS-AND-CLOSE.
> "All four standing guardrails verified intact across Step 1-3 + Rounds (a)/(b)/(c) amendments:
> - **SG-1 (11-specialist roster floor):** intact; story 7b.12 carries `test_eleven_specialists_addressable.py` aggregator. **Floor held.**
> - **SG-2 (33-row mapping-checklist floor; ~28 improvements + 6 deferred):** intact; story 7b.12 NFR-I11 enforces; deferred rows accounted for. **Floor held.**
> - **SG-3 (Composition Spec invariants):** intact; per-body chain-test PRs (NFR-CG14) + Decision Log entries (NFR-CG15); story 7b.12 aggregates. **Floor held.**
> - **SG-4 (BMB sanctum alignment):** intact; FR101 parity-test contract correctly carries Errata 2 corrections (SKILL.md at skills/bmad-agent-{name}/; minimal frontmatter; sanctum-dir 6-file pattern); Class-D2 sidecar variant for Compositor (NOT exception per D20). **Floor held.**
> All four guardrails green. **Workflow close: GREEN.**"

**Amelia (dev-shape/K-target):** GREEN — RATIFIED-WITH-AMENDMENTS-AND-CLOSE.
> "K-aggregate ~33.4K matches the upper-band of R8 Mary's 24-30 target band, accepted as upper-band given Class-D1 + D2 + integration K-bumps. Tripwire clauses placed at three transition points (Wave-1 close + Wave-2b open + Wave-3 first port + Wave-5b pre-T1 K-projection). Per-wave parallelism preserved; Codex-authored 5 / Claude-authored 7 split honors NFR-CG17 + D21. **Workflow close: GREEN.**"

**Murat (test-shape/parity-test):** GREEN — RATIFIED-WITH-AMENDMENTS-AND-CLOSE.
> "Per-story FR105 + NFR-I9/I10/I12 coverage verified. CI-workflow binding rule (R7 Winston/Murat) honored — every NFR with 'MUST pass at PR merge' clause names a workflow file. SanctumParityTestBase creation wired to story 7b.1 T1-readiness; chain-test base + class-conformance validator scaffolding wired to 7b.1; Errata 4 subdir-vs-flat ratified at first parity-test author (7b.1). Wave 6 dual-gate flipped per Slab 7a 7a.8 precedent + integration-tier risk argument. **Workflow close: GREEN.**"

### Round (d) consensus

**Verdict:** RATIFIED-WITH-AMENDMENTS-AND-CLOSE (4/4 unanimous).

**Aggregate amendment record across Steps 2-3:** 4 amendments at Round (a) + 2 at Round (b) + 2 at Round (c) + 0 at Round (d) = **8 amendments total**, all folded inline before Step 4 close. **0 re-opens** across all 4 rounds.

**Final scope-floor confirmation (R9-style; party-mode consensus across 4 voices):**
- **SG-1 (specialist roster floor 11):** intact across Rounds (a)-(d); 11 named specialists in 12 stories. **Floor held.**
- **SG-2 (33-row mapping-checklist floor):** intact; ~28 improvements claimed + 6 deferred rows accounted for via story 7b.12 NFR-I11. **Floor held.**
- **SG-3 (Composition Spec invariants §3.1/§3.5/§3.6/§6/§9/§10/§11):** intact; foundational-artifacts cross-links REFERENCE the spec, do not redefine it; no §11 trigger activation other than Class-D2 sidecar variant (D20 first-class). **Floor held.**
- **SG-4 (BMB sanctum alignment per body):** intact; closed allowlist (FR109) + party-mode-ratified option-b prevents drift; Class-D2 sidecar variant (Compositor) is structural, not silent omission. **Floor held.**

**All four standing guardrails green across all R(a)-R(d) amendments. No scope creep observed.**

**Re-opens:** 0. Workflow CLOSED.

---

## Round-by-round amendment record

| Round | Section | Outcome | Key amendments |
|---|---|---|---|
| (a) | Epic shape green-light (Step 2) | RATIFIED-WITH-AMENDMENTS (4/4) | A1 trial-2 cost-projection AC at 7b.12; A2 Codex-authors prose tightening; A3 K-aggregate tripwire at three transition points; A4 7b.1 T1-readiness preconditions (SanctumParityTestBase + chain-test base + class-conformance validator + Errata 4) |
| (b) | Story-roster ratification (Step 3 mid) | RATIFIED-WITH-AMENDMENTS (4/4) | B1 Dan sandbox-AC promotion party-mode-gated; B2 Compositor pre-T1 K-projection check >4K → dual-gate |
| (c) | Per-story AC adversarial review (Step 3 close) | RATIFIED-WITH-AMENDMENTS (4/4) | C1/B1 follow-through wired into 7b.10; C2/B2 follow-through wired into 7b.11; John C-observation tightened 7b.10 AC-10-B conditional |
| (d) | Workflow close (Step 4) | RATIFIED-WITH-AMENDMENTS-AND-CLOSE (4/4) | 0 new amendments; final scope-floor confirmation across all 4 SGs |

**Aggregate:** 8 amendments across 4 rounds; 0 re-opens; all four standing guardrails green; workflow CLOSED 2026-04-29.

---

## Closeout deliverables (post-Round-(d))

The following downstream artifacts MUST be updated as part of this workflow's close (mirrors Slab 7a 7a.8 closeout discipline):

1. **`_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`** — add `epics_slab_7b_specialist_activation_eleven` entry (status: completed; file path; FR/NFR/ADR/SG counts; epic/story count; re-open count = 0).
2. **`_bmad-output/implementation-artifacts/sprint-status.yaml`** — queue stories 7b.1-7b.12 with class designations + author bindings + gate-mode + K-target per Phased Wave Plan.
3. **`next-session-start-here.md`** — pivot hot-start from "run bmad-create-epics-and-stories" to "run bmad-sprint-planning + open Wave-1 Story 7b.1 Texas hardening via bmad-create-story" with the appropriate readings list (Slab 7b PRD + this epics file + BMB checklist + Slab 2a.2 Irene precedent).
4. **`_bmad-output/planning-artifacts/deferred-inventory.md`** — confirm prior deferred-inventory entries from PRD errata addendum (4 entries: bmb-checklist-additional-worked-examples + fr105-tests-parity-per-specialist-subdir-decision + prd-per-fr-verified-at-annotation-policy + slab-7b-prd-domain-requirements-3-subsection-split-re-deferred) are preserved; add a note that fr105-subdir-vs-flat will be ratified at Story 7b.1 T1-readiness check (per Errata 4 + Murat A4).
5. **`docs/dev-guide/migration-story-governance.json`** — at sprint-planning time (next session), party-mode-ratify Slab 7b 7b.1-7b.12 gate-mode entries (Wave 1-5: single-gate; Wave 6: dual-gate) + version bump per migration-story-governance.json freeze policy.
6. **Commit**: stage + commit `epics-slab-7b-specialist-activation-eleven.md` + bmm-workflow-status.yaml + sprint-status.yaml + next-session-start-here.md updates as a single atomic close commit.

---

**End of Step 4 + Round (d) — workflow CLOSED 2026-04-29; 0 re-opens; ratified-with-amendments-and-close (4/4 unanimous).**
