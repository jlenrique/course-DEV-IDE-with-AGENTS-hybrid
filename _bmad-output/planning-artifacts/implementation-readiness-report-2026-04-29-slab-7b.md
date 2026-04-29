---
stepsCompleted: ['step-01-document-discovery', 'step-02-prd-analysis', 'step-03-epic-coverage-validation']
stepsDeferred: ['step-04-ux-alignment', 'step-05-epic-quality-review', 'step-06-final-assessment']
deferralRationale: |
  Per Slab 7a precedent (`implementation-readiness-report-2026-04-28.md`):
  - Step 4 (UX alignment): UX is not applicable for body-activation runtime work; no operator-facing UI surface introduced beyond Slab 7a HTML review-pack skeleton (already shipped).
  - Step 5 (Epic Quality Review): cannot run until `bmad-create-epics-and-stories` produces actual epic/story file. Reframed Step-3 epic-coverage-validation against PROPOSED stories (12 from Wave plan) substitutes for now.
  - Step 6 (Final Assessment): re-runs after Step 5; deferred jointly.
status: 'READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS'
verdict: 'READY for `bmad-create-epics-and-stories` next workflow, contingent on 3 named preconditions landing in Wave 0 (foundational artifacts FR108-FR112 + sandbox-AC inventory FR107 + scaffold-v0.2-D2-pipeline FR111)'
draftedAt: '2026-04-29'
draftedBy: 'Claude Opus 4.7 (per operator directive: bmad-check-implementation-readiness Steps 1-3 against Slab 7b PRD)'
inputDocuments:
  primary: '_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md'  # Slab 7b PRD (just-ratified, 9 party-mode rounds R1-R9)
  inherited:
    - '_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md'  # parent migration architecture; 13 ADRs D1-D13 inherited
    - '_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md'  # sibling baseline PRD; substrate-completeness CLOSED 2026-04-29
    - '_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md'  # sibling Epic decomposition (8 stories; reference precedent for Slab 7b)
    - '_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md'  # 34-atomic-row inventory; SG-2 floor
    - 'docs/dev-guide/composition-specification.md'  # SG-3 invariants
    - 'docs/dev-guide/migration-story-governance.json'  # gate-mode governance
  notYetAuthored:
    - '_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md'  # next-workflow output of bmad-create-epics-and-stories
slabId: 'slab-7b'
slabName: 'Specialist Activation — Eleven-Specialist Roster Body-Activation atop Slab 7a Orchestration Substrate'
---

# Implementation Readiness Assessment Report — Slab 7b

**Date:** 2026-04-29
**Project:** course-DEV-IDE-with-AGENTS (hybrid clone, `dev/langchain-langgraph-foundation` branch)
**Slab:** Slab 7b — Specialist Activation (Eleven-Specialist Roster Body-Activation)
**Verdict:** **READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS**

---

## Executive Verdict

Slab 7b PRD is **ready for `bmad-create-epics-and-stories` next workflow**, contingent on three named preconditions landing in Wave 0 before Wave 1 Class-A stories open:
1. **Foundational artifacts (FR108-FR112)** — five docs/configs not yet authored.
2. **Sandbox-AC inventory PR (FR107 + NFR-CG12)** — 5-entry inventory (gamma/kling/elevenlabs/wondercraft/dan-api-tbd-if-API) not yet landed.
3. **scaffold-v0.2-D2-pipeline.yaml (FR111)** — Class-D2 pipeline-greenfield scaffold variant for Compositor not yet authored.

These preconditions are explicitly named in the PRD as Wave-0 deliverables; their pre-merge state at PRD ratification is expected. Implementation-readiness is conditional but not blocked.

**FR coverage:** 26/26 FRs (FR88-FR113) anchored to ≥1 story or governance deliverable across the proposed 12-story + Wave-0 + Wave-0.5 decomposition.
**NFR coverage:** 24 NFRs spanning T (test discipline), CG (compliance & governance), I (invariants), OD (operator documentation); each enforced via named CI workflow OR validator script OR per-specialist AC.
**Standing-guardrail audit:** SG-1/SG-2/SG-3/SG-4 all green across PRD; no implicit-violation surface detected.

Slab 7a precedent: closed at `95c81b0` (2026-04-29; 696 passed/19 skipped baseline). Slab 7b inherits substrate-completeness; body-activation is the next layer. NEW CYCLE proven 6× end-to-end on Slab 7a; same dev-cycle pattern inherits.

---

## Step 1 — Document Discovery

### A. PRD Documents

**Primary Slab 7b PRD (just-ratified, 9 party-mode rounds R1-R9):**
- `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` (1,153 lines, 2026-04-29; status `complete-ready-for-bmm-workflow-status-update-and-implementation-readiness-check`)

**Sibling baseline PRDs (inherited reference):**
- `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md` (1,325 lines; CLOSED 2026-04-28)
- `_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md` (parent migration PRD; SHIPPED at `97842ac` 2026-04-27)
- `_bmad-output/planning-artifacts/prd.md` (legacy Wave 2B; frozen reference, NOT in scope)

**No duplicates** (whole vs sharded) detected.

### B. Architecture Documents

- `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` (parent migration architecture; 13 ADRs D1-D13 inherited; ratified 2026-04-22)
- `_bmad-output/planning-artifacts/architecture.md` (legacy Wave 2B reference; frozen)

Slab 7b adds D14-D23 (10 new ADRs) within its own PRD §Architectural Decisions. No standalone Slab 7b architecture document; Slab 7a precedent did the same (architecture inheritance + ADR addendum in PRD).

### C. Epics & Stories Documents

**Sibling/inherited:**
- `_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md` (parent migration; 9 epics / 56 stories)
- `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` (sibling Epic; 1 epic / 8 stories CLOSED)
- `_bmad-output/planning-artifacts/epics.md` (legacy 22-epic frozen reference)
- `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` (Wave 2B frozen reference)

**Not yet authored (expected — output of next workflow `bmad-create-epics-and-stories`):**
- `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md`

Reframed Step 3 (epic-coverage-validation) below validates FR coverage against PROPOSED 12-story decomposition from PRD Wave plan rather than against not-yet-existing epics file.

### D. UX Design Documents

**Not applicable** for Slab 7b (body-activation runtime work; no operator-facing UI surface introduced beyond Slab 7a HTML review-pack skeleton already shipped). Step 4 (UX alignment) deferred per Slab 7a precedent.

### Document Discovery — Issues + Resolution

- ✅ No duplicate-format conflicts.
- ⚠️ Step 5 epic-coverage-validation reframed (proposed stories, not authored epics) — **expected and pre-acknowledged** per Slab 7a precedent.
- ✅ Steps 4-6 deferral rationale documented in frontmatter.

---

## Step 2 — PRD Analysis

### Functional Requirements Extracted (26 FRs: FR88-FR113)

**FR-7b-roster (1 FR):**
- **FR88.** Slab 7b ships eleven specialist body activations covering: Texas (Class A hardening), Irene Pass-1 (Class B activation refresh), Tracy (Class C+ port-shape + sidecar creation), Gary (Class C port-shape), Kira (Class C port-shape), Wanda (Class C port-shape onto scaffold), Enrique (Class C port-shape), Dan (Class D1 LLM-greenfield), Compositor (Class D2 pipeline-greenfield), Quinn-R (Class A hardening), Vera (Class A hardening). Per-specialist Slab-7b shape designation operator-ratified; binds.

**FR-7b-class-A-hardening (3 FRs):**
- **FR89.** Texas hardening: live-retrieval-against-real-directive-composer; six-canonical-artifacts contract; G0 6-dim evidence-sentence rubric; word-count belt-and-suspenders; cross-validation hint application.
- **FR90.** Quinn-R hardening: two-mode rubric (pre-composition / post-composition); G2C storyboard-bound shape; G5 pre-composition QA body.
- **FR91.** Vera hardening: G0 6-dim rubric on real Texas output; G1 ingestion-quality 6-dim verdicts; G3 fidelity check on real Storyboard A; G4 19-criterion rubric (G4-01..G4-19) on real Irene Pass-2 output; sensory-bridges dispatch on real motion + audio.

**FR-7b-class-B-refresh (1 FR):**
- **FR92.** Irene Pass-1 refresh: 9-node scaffold mirroring Pass-2 shape; lesson-plan coauthoring + scope-lock contract; per-plan-unit ratification surface for G1A; `irene-pass1.md` artifact write; mode-singularity hard-constraint enforcement; `scope_decision.set` + `plan.locked` learning-event emission.

**FR-7b-class-C-port-shape (5 FRs; Tracy = C+ class designation per R8):**
- **FR93.** Tracy Class-C+ port-shape + sidecar creation: research-shaped intent enrichment for Pass-2; sidecar greenfield at `_bmad/memory/bmad-agent-tracy/` with full 4-file BMB pattern; 9-node scaffold per Slab 2b.1 TEMPLATE; LLM-only; cache-hit-rate harness ≥85% post-warm-up.
- **FR94.** Gary Class-C port-shape: Gamma API live; per-slide variant generation (DOUBLE_DISPATCH); theme-handshake; PNG export normalization; Vera G3 invocation hooks; cache-hit-rate ≥85%; live-API-on-CI prohibition.
- **FR95.** Kira Class-C port-shape: Kling API live; motion generation per `motion_plan.yaml`; per-slide receipts; reviewer inspection pack; fail-closed budget rules; cache-hit-rate ≥85%; live-API-on-CI prohibition.
- **FR96.** Wanda Class-C port-shape onto scaffold: Wondercraft API live; podcast/audio bed; scaffold-v0.2 alignment; cache-hit-rate ≥85%; live-API-on-CI prohibition.
- **FR97.** Enrique Class-C port-shape: ElevenLabs API live; voice-preview + voice-selection HIL contract; manifest-driven narration; assembly-bundle build; cache-hit-rate ≥85%; live-API-on-CI prohibition.

**FR-7b-class-D-greenfield (2 FRs):**
- **FR98.** Dan Class-D1 LLM-greenfield via `bmad-create-specialist`: SKILL.md (option-a sanctum-aligned); sidecar with full BMB pattern; `app/specialists/dan/` with scaffold-v0.2; narrow-lane CD aux contributions across G1-G2; sandbox-AC `dan-api-tbd` resolved at story-1.
- **FR99.** Compositor Class-D2 pipeline-greenfield (sidecar variant CANONICAL not exception per R5/R6): scaffold-v0.2-D2-pipeline; sidecar with operational metadata (contract / version / chronology / access-boundaries); deterministic assembly pipeline; pipeline-determinism harness ≥99% (bytes-identical sync-visuals + field-masked-hash assembly-guide).

**FR-7b-sanctum (4 FRs):**
- **FR100.** Per-story `# SG-4 Sanctum Alignment` AC requiring SKILL.md option-a OR option-b.
- **FR101.** Structural parity test `tests/parity/test_skill_md_sanctum_alignment.py` MUST exist; 5-clause test contract (enumerate roster; YAML parse + required keys + sanctum_path derivation; Class-D2 sidecar variant branch; option-b closed-allowlist + ≥80 chars rationale; cold-activation smoke per FM-25).
- **FR102.** Parity test runs at every PR merge gate; red blocks merge.
- **FR103.** Sanctum-alignment matrix at `docs/dev-guide/specialist-sanctum-alignment-matrix.md` MUST exist; updated at every body-activation story close.

**FR-7b-substrate-consumption-extended (4 FRs):**
- **FR104.** Operator-control parity table extended with 11 new rows (legacy lever → migrated lever → shim → end-to-end test); per-specialist operator-control inventory MUST be filed before that specialist's class enters dev.
- **FR105.** Parity-test suite at `tests/parity/per_specialist/test_<specialist_name>_activation_contract.py`; class-shaped (5 templates).
- **FR106.** Cache-hit-rate harness configured for 10 LLM specialists + 1 Compositor pipeline-determinism harness; parametric.
- **FR107.** Sandbox-AC inventory MUST extend with up to 5 entries before any API-bound Class-C/C+/D opens; Tracy + Dan-without-API exempt.

**FR-7b-foundational-artifacts (5 FRs):**
- **FR108.** `docs/dev-guide/bmb-sanctum-alignment-checklist.md` MUST exist before Wave 1; canonical SG-4 alignment authority; required TOC §1-§8.
- **FR109.** `docs/dev-guide/sanctum-exception-categories.json` MUST exist before Wave 1; closed allowlist for option-b (initial entry: `sidecar-hook` per Cora precedent).
- **FR110.** `docs/dev-guide/operator-control-parity-template.md` MUST exist before Wave 1; per-specialist inventory template.
- **FR111.** `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` MUST exist before Wave 5 (Class-D Compositor opens).
- **FR112.** `skills/bmad-agent-cora/SKILL.md` MUST contain stable §"Sanctum exception" anchor before any option-b invocation.

**FR-7b-substrate-boundary-frozen (1 FR):**
- **FR113.** No Slab 7b body activation amends `app/marcus/orchestrator/dispatch_adapter.py:81` (line-pinned per R2 freeze; ±line range 70-95 governance escalation flag in code-review).

**Total FRs: 26**

### Non-Functional Requirements Extracted (24 NFRs)

**NFR-T (test discipline; 6 NFRs):**
- NFR-T9 (T1 unit/contract; <30s aggregate; <5min full 11-specialist run)
- NFR-T10 (T2 fixture-replay; <90s/specialist)
- NFR-T11 (T3 canary live-substrate smoke; <120s/specialist)
- NFR-T11a (T4 cache-determinism harness; <45s/specialist; nightly OR green-light cadence; ≥85% median[2:])
- NFR-T11b (T5 live canaries Class-C/C+/D1; ≤3 canaries/specialist; ~$0.40/canary; operator-gated)
- NFR-T12 (parity-test wall-clock SLA; <120s on ubuntu-latest; ~10s/specialist budget)

**NFR-CG (compliance & governance; 9 NFRs incl. CG14a):**
- NFR-CG12 (sandbox-AC inventory PR before any API-bound Class-C/C+/D opens)
- NFR-CG13 (live-API-on-CI = 0; AST-scan validator at `scripts/utilities/detect_live_api_in_tests.py` + pre-merge GitHub Action)
- NFR-CG14 (per-specialist Composition Spec §6 chain-test PR per body activation)
- NFR-CG14a (chain-test base class at `tests/composition/_chain_test_base.py` MUST land BEFORE Wave 1)
- NFR-CG15 (per-specialist Composition Spec §10 Decision Log entry; validator at `scripts/utilities/validate_specialist_composition_spec_decision_log.py`)
- NFR-CG16 (per-specialist `bmad-code-review` before story close)
- NFR-CG17 (Codex parallel-authoring scope-binding commitment #8; 5 Class-C/C+ stories + sandbox-AC inventory PR + per-story bmad-code-review)
- NFR-CG18 (foundational-artifacts precondition discipline; Wave 1 cannot open until FR108-FR112 merge)
- NFR-CG19 (credential-rotation register at `state/config/credential-rotation-register.yaml`; 5 API surfaces)
- NFR-CG20 (per-specialist rate-limit budget in `app/specialists/<name>/config.yaml`)

**NFR-I (invariants; 5 NFRs):**
- NFR-I9 (sanctum alignment invariant; bound to `.github/workflows/specialist-parity.yml`)
- NFR-I10 (per-specialist activation contract invariant; bound to `.github/workflows/activation-contract.yml`)
- NFR-I11 (mapping-checklist row-status invariant; bound to `.github/workflows/mapping-checklist.yml`)
- NFR-I12 (class-shaped parity-test invariant; 5 templates A/B/C+merged/D1/D2; validator `validate_parity_test_class_conformance.py`)
- NFR-I13 (substrate-as-floor invariant; CODEOWNERS + `.github/workflows/substrate-frozen.yml`)

**NFR-OD (operator documentation; 4 NFRs):**
- NFR-OD3 (per-specialist operator-reference docs at `docs/operator/specialists/<name>.md`)
- NFR-OD4 (sanctum-alignment matrix at `docs/operator/specialists/sanctum-alignment-matrix.md`)
- NFR-OD5 (fixture-refresh dry-run mode at `scripts/utilities/refresh_fixtures.py`)
- NFR-OD6 (Codex scope-audit; `codex-scope-audit` job)

**Total NFRs: 24** (NFR-CG14a counted as sub-rule of NFR-CG14; aggregate 24 distinct NFR identifiers).

### Additional Requirements (Constraints + Standing Guardrails)

- **SG-1** (Specialist roster floor): 11 specialists named; cannot reduce.
- **SG-2** (Legacy workflow step floor): 34-atomic-row mapping-checklist (33 prompt sections + sub-step §05.5); cannot lose rows.
- **SG-3** (Composition Spec invariants): §3.1/§3.5/§3.6/§6/§9/§10/§11; structurally enforced.
- **SG-4** (BMB sanctum alignment per body): NEW for Slab 7b; option-a (BMB pattern) OR option-b (closed allowlist + party-mode consensus); silent omission = HALT-AND-REMEDIATE.

**Eight scope-binding commitments** (Exec Summary): substrate-as-floor; subgraph-with-`interrupt()`; max-3 oscillation guard substrate; pre-composition QA validator substrate-step; decision-card vocabulary registry honored; C1 calibration-tripwire honored; parity-test suite honored; SG-4 sanctum alignment per body; Codex parallel-authoring binding (R7 amendment).

### PRD Completeness Assessment

- ✅ **FR coverage** complete: 26 FRs spanning roster + 5-class taxonomy + sanctum + substrate-extension + foundational + boundary-frozen.
- ✅ **NFR coverage** complete: 24 NFRs across all four NFR families (T/CG/I/OD); each enforced via named CI workflow OR validator script.
- ✅ **Standing-guardrails** explicit: 4 SGs operator-non-negotiable; structural enforcement.
- ✅ **Scope-binding commitments** explicit: 8 SBCs architectural non-negotiables.
- ✅ **Acceptance clauses** complete: A-8..A-14 (7 clauses; A-9 with per-specialist file-path table).
- ✅ **Failure modes** complete: FM-11..FM-26 (16 modes; A-11 cold-activation smoke; FM-23/24/25/26 added per R3 Quinn).
- ✅ **Innovation register**: IR-1..IR-9 (9 risk patterns; cross-referenced to NFRs per R8 amendments).
- ✅ **Scoping risk register**: SR-T1..SR-S4 (18 risks; expanded 12→18 per R8).
- ✅ **Cross-section consistency**: verified across R1-R9 party-mode rounds (4/4 unanimous on close).

**No requirement gaps detected at PRD analysis.**

---

## Step 3 — Epic Coverage Validation (Reframed: Proposed-Story FR Coverage)

Per Slab 7a precedent: epics file not yet authored (next-workflow `bmad-create-epics-and-stories` output). Reframed validation against PROPOSED 12-story + Wave-0 + Wave-0.5 decomposition from PRD Wave plan §Phased Wave Plan.

### Proposed Story Decomposition (from PRD Wave plan)

| Wave | Story-ID (proposed) | Class | Specialist | Gate-mode | K-target |
|---|---|---|---|---|---|
| Wave 0 | 7b.0-foundational-artifacts | (governance) | — | (operator-gated; not K-counted) | governance-budgeted |
| Wave 0.5 | 7b.0.5-codex-deployment | (governance) | — | (verification gate) | governance-budgeted |
| Wave 1 | 7b.1-texas-hardening | A | Texas | single-gate | ~2K + ~25 tests |
| Wave 1 | 7b.2-quinn-r-hardening | A | Quinn-R | single-gate | ~2K + ~25 tests |
| Wave 1 | 7b.3-vera-hardening | A | Vera | single-gate | ~2K + ~25 tests |
| Wave 2 | 7b.4-irene-pass1 | B | Irene Pass-1 | single-gate | ~2.5K + ~30 tests |
| Wave 2 | 7b.5-tracy-port-shape-and-sidecar | C+ | Tracy | single-gate (bundle per R8 Mary) | ~3.3K + ~36 tests |
| Wave 3 | 7b.6-gary-port-shape | C | Gary | single-gate | ~2.9K + ~33 tests |
| Wave 3 | 7b.7-kira-port-shape | C | Kira | single-gate | ~2.9K + ~33 tests |
| Wave 3 | 7b.8-enrique-port-shape | C | Enrique | single-gate | ~2.9K + ~33 tests |
| Wave 4 | 7b.9-wanda-port-shape | C | Wanda | single-gate | ~2.9K + ~33 tests |
| Wave 5 | 7b.10-dan-greenfield | D1 | Dan | single-gate | ~3.5K + ~40 tests |
| Wave 5 | 7b.11-compositor-greenfield | D2 | Compositor | single-gate | ~3.5K + ~40 tests |
| Wave 6 | 7b.12-integration-parity-suite-closeout | (integration) | — | dual-gate | ~3K + ~25 active tests |

**Total: 12 dev stories + Wave-0 governance deliverable + Wave-0.5 governance deliverable = 14 deliverables.**

**K-aggregate:** ~36K LOC + ~378 tests; ~24-30 K-units at K-floor 1.3-1.5× per R3 amendment.

### FR Coverage Matrix (FR88-FR113 → proposed stories)

| FR # | Requirement Summary | Proposed Story Coverage | Status |
|---|---|---|---|
| FR88 | Eleven-specialist roster (canonical) | Story 7b.12 integration parity-test asserts roster=11; cross-cuts all 12 stories | ✅ Covered |
| FR89 | Texas hardening | Story 7b.1-texas-hardening | ✅ Covered |
| FR90 | Quinn-R hardening | Story 7b.2-quinn-r-hardening | ✅ Covered |
| FR91 | Vera hardening | Story 7b.3-vera-hardening | ✅ Covered |
| FR92 | Irene Pass-1 refresh | Story 7b.4-irene-pass1 | ✅ Covered |
| FR93 | Tracy Class-C+ port-shape + sidecar | Story 7b.5-tracy-port-shape-and-sidecar | ✅ Covered |
| FR94 | Gary Class-C port-shape | Story 7b.6-gary-port-shape | ✅ Covered |
| FR95 | Kira Class-C port-shape | Story 7b.7-kira-port-shape | ✅ Covered |
| FR96 | Wanda Class-C port-shape onto scaffold | Story 7b.9-wanda-port-shape | ✅ Covered |
| FR97 | Enrique Class-C port-shape | Story 7b.8-enrique-port-shape | ✅ Covered |
| FR98 | Dan Class-D1 LLM-greenfield | Story 7b.10-dan-greenfield | ✅ Covered |
| FR99 | Compositor Class-D2 pipeline-greenfield | Story 7b.11-compositor-greenfield | ✅ Covered |
| FR100 | Per-story SG-4 sanctum AC | Cross-cuts all 11 specialist stories (7b.1-7b.11) as per-story AC | ✅ Covered |
| FR101 | Structural parity test contract | Story 7b.12 integration parity-suite | ✅ Covered |
| FR102 | Parity test per-PR enforcement | Story 7b.12 + NFR-I9 CI workflow | ✅ Covered |
| FR103 | Sanctum-alignment matrix doc | Story 7b.12 closeout deliverable + per-story update | ✅ Covered |
| FR104 | Operator-control parity table extension (11 rows) | Story 7b.12 + per-specialist filed at story open | ✅ Covered |
| FR105 | Parity-test suite class-shaped | Story 7b.12 + per-specialist test landed at each story | ✅ Covered |
| FR106 | Cache-hit-rate harness + Compositor pipeline-determinism | Story 7b.12 + per-Class-C/C+/D1 story landing harness config | ✅ Covered |
| FR107 | Sandbox-AC inventory PR | Story 7b.0-foundational-artifacts (Wave 0) — Codex authors per NFR-CG17 | ✅ Covered |
| FR108 | bmb-sanctum-alignment-checklist.md | Story 7b.0 (Wave 0) | ✅ Covered |
| FR109 | sanctum-exception-categories.json | Story 7b.0 (Wave 0) | ✅ Covered |
| FR110 | operator-control-parity-template.md | Story 7b.0 (Wave 0) | ✅ Covered |
| FR111 | scaffold-v0.2-D2-pipeline.yaml | Story 7b.0 (Wave 0; precondition for Wave 5 Compositor) | ✅ Covered |
| FR112 | Cora SKILL.md §"Sanctum exception" anchor | Story 7b.0 (Wave 0) | ✅ Covered |
| FR113 | Marcus boundary frozen | Cross-cuts all stories as governance gate (NFR-I13 + CODEOWNERS); no dedicated story | ✅ Covered (governance) |

**Coverage Statistics:**
- Total PRD FRs: **26**
- FRs covered by ≥1 proposed story or governance gate: **26**
- Coverage percentage: **100%**

### Missing FR Coverage

**None.** All 26 FRs have a story-anchored or governance-gated coverage path.

### NFR Coverage Spot-Check (24 NFRs)

| NFR Family | Count | Coverage Mechanism |
|---|---|---|
| NFR-T9..T12 (test discipline) | 6 | Cross-cuts all stories as per-tier wall-clock budgets; enforced via `@pytest.mark.timeout` + CI-job timeout |
| NFR-CG12..CG20 (compliance & governance) | 9 (incl. CG14a) | CG12+CG18 = Wave 0 precondition; CG13/14a/15 = validator scripts (Story 7b.0); CG14/16/17 = per-specialist + per-story; CG19/CG20 = operator-side (config files + register) |
| NFR-I9..I13 (invariants) | 5 | All bound to named `.github/workflows/*.yml` files; per-PR enforcement |
| NFR-OD3..OD6 (operator documentation) | 4 | OD3 = 11 per-specialist files (one per Wave 1-5 story); OD4 = Story 7b.12 closeout; OD5 = `scripts/utilities/refresh_fixtures.py`; OD6 = `codex-scope-audit` job |

**Spot-check result:** All 24 NFRs anchor to ≥1 enforcement mechanism. No orphan NFRs.

---

## Standing-Guardrail Implicit-Violation Audit (SG-1/2/3/4)

### SG-1 — 11-Specialist Roster Floor

**Status:** ✅ GREEN.
- PRD canonical roster (FR88 + frontmatter `slab7bSpecialistRoster`): Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera = **11**.
- Wave plan: 11 specialist stories (7b.1-7b.11) + governance (7b.0, 7b.0.5) + integration (7b.12) = 14 deliverables; specialist count = 11.
- Codex deployment Wave-0.5: additive verification, NOT roster expansion.
- Implicit violations: NONE detected.

### SG-2 — 33-Row Mapping Checklist Floor

**Status:** ✅ GREEN.
- 34-atomic-row inventory (33 prompt sections + sub-step §05.5); ~28 row improvements + 6 explicitly deferred (4 conditional cluster paths §05B/§6.2/§6.3/§7.5 + §14.5 Desmond + §15 Operator Handoff).
- A-10 acceptance clause (R3 Mary amendment): "≤28 inheritance rows transition ❌→✅ or ⚠️→✅ on rows owned by activated specialists; the 6 explicitly deferred rows remain ❌/⚠️ as-tracked and are out of scope."
- NFR-I11 per-PR enforcement: `tests/parity/test_mapping_checklist_status.py` bound to `.github/workflows/mapping-checklist.yml`.
- Domain Requirements activation matrix maps each row to owning specialist OR conditional/deferred status.
- Implicit violations: NONE detected.

### SG-3 — Composition Spec Invariants (§3.1/§3.5/§3.6/§6/§9/§10/§11)

**Status:** ✅ GREEN.
- §3.1 SHA256+append-only: inherited via Slab 7a substrate (gate_runner.py); per-specialist body activations preserve.
- §3.5 gate precedence: per-specialist non-blocking default unchanged.
- §3.6 manifest-declared dependencies: per-specialist body activation declares deps in manifest (via Slab 7a fold-flags substrate).
- §6 chain-test-per-PR: NFR-CG14 per-specialist; NFR-CG14a base class precondition.
- §9 Composition Smoke gate: at slab-opener (Wave 0 / Wave 1 transition).
- §10 Decision Log: NFR-CG15 per-specialist for new vocabulary.
- §11 Migration triggers: monitored; 0 of 5 active.
- Implicit violations: NONE detected.

### SG-4 — BMB Sanctum Alignment per Body (NEW)

**Status:** ✅ GREEN.
- Per-story SG-4 AC (FR100): every body-activation story carries SKILL.md option-a OR option-b AC.
- Closed allowlist (FR109): option-b limited to `docs/dev-guide/sanctum-exception-categories.json` rows; party-mode consensus required.
- Structural parity-test (FR101 + NFR-I9): YAML parse + required keys + sanctum_path derivation + Class-D2 sidecar variant branch + option-b allowlist + cold-activation smoke.
- Class-D2 Compositor: structural variant (D20 amendment), NOT silent omission.
- Reviewer is belt-and-suspenders (R7 Murat amendment); parity-test IS the gate.
- Implicit violations: NONE detected.

**SG audit aggregate:** 4/4 standing guardrails green. No implicit-violation surface detected.

---

## Named Preconditions (Wave 0 Hard Gate Before Wave 1 Opens)

These three preconditions are explicitly named in the PRD and MUST land before any Wave 1 Class-A specialist story opens for dev. Their current pre-PRD-ratification state is expected; flagging here for visibility at story-authoring time.

### Precondition 1 — Foundational Artifacts (FR108-FR112; 5 documents)

**Status:** Not yet authored. Wave 0 deliverable.

| FR | Artifact | Path | Audience |
|---|---|---|---|
| FR108 | BMB sanctum alignment checklist | `docs/dev-guide/bmb-sanctum-alignment-checklist.md` | Reviewer + parity-test + dev agent |
| FR109 | Sanctum exception categories | `docs/dev-guide/sanctum-exception-categories.json` | Closed allowlist for option-b |
| FR110 | Operator-control parity template | `docs/dev-guide/operator-control-parity-template.md` | Per-specialist inventory authoring |
| FR111 | scaffold-v0.2-D2-pipeline.yaml | `_bmad/_cfg/scaffolds/scaffold-v0.2-D2-pipeline.yaml` | Compositor body activation (Wave 5) |
| FR112 | Cora SKILL.md §"Sanctum exception" anchor | `skills/bmad-agent-cora/SKILL.md` (edit) | Concrete paste-pattern target for option-b |

**Recommendation:** Author all 5 in Story 7b.0-foundational-artifacts (Wave 0). Per Winston R9 amendment: atomic merge required (single load-bearing commit) so Wave 1 has unambiguous green-light commit to branch from.

### Precondition 2 — Sandbox-AC Inventory PR (FR107 + NFR-CG12)

**Status:** Not yet landed. Wave 0 / Wave 0.5 deliverable.

5-entry inventory at `docs/dev-guide/migration-ac-sandbox-inventory.json`:
- gamma (forbidden in dev-agent ACs; httpx + SDK alternative)
- kling (forbidden in dev-agent ACs; httpx + SDK alternative)
- elevenlabs (forbidden in dev-agent ACs; httpx + SDK alternative)
- wondercraft (forbidden in dev-agent ACs; httpx + SDK alternative)
- dan-api-tbd (status TBD pending Story 7b.10 resolution; if LLM-only, exempt; if third-party, finalized)

**Recommendation:** Codex authors per NFR-CG17 (scope-binding commitment #8). Party-mode-ratified before Wave 3 (API-bound Class-C stories) opens.

### Precondition 3 — Tracy + Dan-without-API Sandbox Exemption Confirmed

**Status:** Pending Story 7b.5 (Tracy port-shape) + Story 7b.10 (Dan greenfield).
- Tracy: LLM-only (no third-party API binding); sandbox-AC inventory entry NOT required (R5 Amelia scope-amendment confirmed).
- Dan: API binding TBD at story-1; if LLM-only, also exempt; if third-party, sandbox-AC inventory entry finalized.

**Recommendation:** Resolution at Story 7b.5 / Story 7b.10 T1 readiness; document in Completion Notes; update NFR-CG12 inventory state if Dan goes third-party.

---

## Verdict

**READY-WITH-MINOR-AMENDMENTS-AND-NAMED-PRECONDITIONS.**

Slab 7b PRD is **ready for `bmad-create-epics-and-stories` next workflow** subject to:

1. **Hard preconditions (block Wave 1 open until landed):** FR108-FR112 foundational artifacts authored in Wave 0; sandbox-AC inventory PR landed before Wave 3; scaffold-v0.2-D2-pipeline.yaml authored before Wave 5.
2. **Minor amendments deferred to story-authoring time** (`bmad-create-epics-and-stories`):
   - Per-FR `verified-at: 2026-04-29` annotations on FRs citing file paths/symbols (R6 Mary deferred).
   - Path verification spot-checks: `dispatch_retrieval(directive_path, bundle_dir)` signature (FR89), `_materialize_exported_slide_paths` symbol existence (FR94), `assembly-bundle/audio/` convention (FR97). Each story's T1 readiness audits these against current repo state.
   - K-floor citation audit: PRD says 1.3-1.5×; story-cycle-efficiency.md may say 1.2-1.5×. Reconcile at sprint planning.
   - §Domain Requirements 3-subsection split (R5 Paige): re-deferred to post-MVP polish PR (filed in deferred-inventory).
3. **No critical gaps detected.**

Per Slab 7a precedent: **Steps 4 (UX), 5 (Epic Quality Review), 6 (Final Assessment) deferred** — UX N/A for body-activation; Steps 5-6 re-run after `bmad-create-epics-and-stories` produces the epic/story file.

### Recommended next workflow

**`bmad-create-epics-and-stories`** with the following as input:
- This implementation-readiness report
- `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md` (just-ratified)
- `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` (sibling Epic precedent)
- Per-class allocation table from PRD §Codex Deployment Plan (Wave-0/0.5/1/2/3/4/5/6 + per-story Codex/Claude assignment)

Expected output: `_bmad-output/planning-artifacts/epics-slab-7b-specialist-activation-eleven.md` with 1 Epic + 12 stories (or 13-14 if Tracy split per Amelia option-B; bundle preferred per Mary R8).

---

## References

- **Slab 7a sibling readiness report:** `_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-28.md`
- **Slab 7b PRD (just-ratified):** `_bmad-output/planning-artifacts/prd-slab-7b-specialist-activation-eleven.md`
- **Slab 7a Epic + 8 stories:** `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md`
- **Slab 7a retrospective:** `_bmad-output/implementation-artifacts/slab-7a-retrospective.md`
- **Mapping checklist (34-atomic-row):** `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`
- **Sprint status:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
- **Deferred inventory:** `_bmad-output/planning-artifacts/deferred-inventory.md`
- **CLAUDE.md governance:** sandbox-AC + gate-mode governance + sprint governance
