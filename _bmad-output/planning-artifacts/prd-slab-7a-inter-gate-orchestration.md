---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoped', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
completedAt: '2026-04-28'
status: 'complete-ready-for-bmm-workflow-status-update-and-implementation-readiness-check'
polishPass2026_04_28:
  navigationAdded: ['table-of-contents', 'operator-non-negotiables-callout', 'quick-reference-anchors']
  acronymGlosses: ['JTBD', 'HIL', 'FM', 'ADR', 'K-floor']
  standingGuardrailsConsolidatedAs: ['SG-1: 11-specialist roster floor', 'SG-2: 34-row mapping checklist floor', 'SG-3: Composition Spec invariants §3.1/§3.5/§3.6/§6/§9/§10/§11']
  crossLinkFixes: ['Step 5 FM-2 → Step 6 FM-2 prefix', 'Step 8 TS-3 → Step 3 TS-3 prefix']
  scopeFloorCheck: 'verified — no specialist drop, no checklist-row drop, no Composition Spec violation across all polish edits'
guardrailsExpanded2026_04_28:
  mapping_checklist_as_guardrail:
    path: '_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md'
    rule: 'Every remaining PRD step content MUST be cross-referenced against the 34-row mapping checklist; any deliverable, requirement, or constraint that would lose essential function from a row is auto-rejected.'
    enforcement: 'Party-mode voices instructed to verify mapping-checklist coverage at draft time; assistant verifies at synthesis time before [C] menu.'
  composition_spec_as_guardrail:
    path: 'docs/dev-guide/composition-specification.md'
    rule: 'Every remaining PRD step content MUST honor Composition Spec invariants: §3.1 SHA256 output digests + append-only envelope; §3.5 gate precedence (per-specialist non-blocking by default); §3.6 manifest-declared dependencies with permanent runner fallback; §6 chain-test-per-PR; §9 Composition Smoke gate at slab-opener; §10 Decision Log additions for any composition-substrate change; §11 migration triggers tracked.'
    enforcement: 'Party-mode voices instructed to verify Composition Spec compliance at draft time; assistant flags any potential §11 trigger activation.'
metaDirective:
  partyModeForRemainingSteps: true
  consensusOrSupermajorityRequired: true
  scopeFloorGuardrails:
    specialistRoster:
      mustNotReduceBelow: 11
      named: ['Texas', 'Irene', 'Dan', 'Tracy', 'Gary', 'Kira', 'Wanda', 'Enrique', 'Compositor', 'Quinn-R', 'Vera']
      enforcement: 'Any party-mode recommendation that would drop a named specialist from Slab 7b activation roster is auto-rejected and flagged back to operator before proceeding.'
    legacyWorkflowSteps:
      mustNotDropFromMappingChecklist: 34
      checklistPath: '_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md'
      enforcement: 'Any party-mode recommendation that would drop a legacy workflow row from the mapping checklist (vs preserve essential function under different mechanism) is auto-rejected and flagged back to operator before proceeding.'
  consensusProtocol: 'Each remaining PRD step (3 through 13) opens with a 3-4 voice party-mode round; assistant synthesizes consensus or supermajority position; if consensus violates either scope-floor guardrail, assistant overrides and flags to operator; otherwise consensus position is presented as the proposed [C] content for operator final approval at step menu.'
  effectiveFromStep: 'step-03-success'
slab7bSpecialistRoster:
  count: 11
  operatorRatified: '2026-04-28'
  specialists:
    texas: { skill: 'bmad-agent-texas', appDir: 'app/specialists/texas/', sidecar: 'texas-sidecar', status: 'partial-active', slab7bShape: 'hardening-post-directive-composer' }
    irene: { skill: 'bmad-agent-content-creator', appDir: 'app/specialists/irene/', sidecar: 'irene-sidecar', status: 'pass2-done-pass1-pending', slab7bShape: 'pass1-activation' }
    dan: { skill: null, appDir: null, sidecar: 'dan-sidecar', status: 'sidecar-only', slab7bShape: 'greenfield-via-bmad-create-specialist' }
    tracy: { skill: 'bmad-agent-tracy', appDir: 'app/specialists/tracy/', sidecar: null, status: 'passthrough', slab7bShape: 'port-shape-plus-sidecar-creation' }
    gary: { skill: 'bmad-agent-gamma', appDir: 'app/specialists/gary/', sidecar: 'gary-sidecar', status: 'passthrough', slab7bShape: 'port-shape' }
    kira: { skill: 'bmad-agent-kling', appDir: 'app/specialists/kira/', sidecar: 'kira-sidecar', status: 'passthrough', slab7bShape: 'port-shape' }
    wanda: { skill: 'bmad-agent-wondercraft', appDir: 'app/specialists/wanda/', sidecar: 'wanda-sidecar', status: 'client-landed-not-on-scaffold', slab7bShape: 'port-shape-onto-scaffold' }
    enrique: { skill: 'bmad-agent-elevenlabs', appDir: 'app/specialists/enrique/', sidecar: 'enrique-sidecar', status: 'passthrough', slab7bShape: 'port-shape' }
    compositor: { skill: 'compositor', appDir: null, sidecar: null, status: 'skill-only', slab7bShape: 'greenfield-via-kind-deterministic-scaffold' }
    quinn_r: { skill: 'bmad-agent-quality-reviewer', appDir: 'app/specialists/quinn_r/', sidecar: 'quinn-r-sidecar', status: 'activated-slab-2a-era', slab7bShape: 'hardening-only-against-real-content-from-port-shape-specialists', actBodyShape: 'two-mode-precomposition-postcomposition' }
    vera: { skill: 'bmad-agent-fidelity-assessor', appDir: 'app/specialists/vera/', sidecar: 'vera-sidecar', status: 'activated-slab-2a-era', slab7bShape: 'hardening-only-against-G0-G1-G4-rubric-semantics-on-real-content', actBodyShape: 'single-mode-with-sensory-bridges-dispatch' }
  sandboxAcInventoryAdditions:
    - gamma  # forbidden in dev-agent ACs
    - kling  # forbidden in dev-agent ACs
    - elevenlabs  # forbidden in dev-agent ACs
    - wondercraft  # forbidden in dev-agent ACs (added per 9-specialist roster expansion)
    - 'dan-api-tbd'  # status TBD pending Dan's specialist-shape design
  cacheHitHarnessConfigs:
    parametric: true
    perSpecialistCount: 10  # Irene + Tracy + Gary + Kira + Enrique + Wanda + Texas + Dan + Quinn-R + Vera
    plus_one_pipeline_determinism_harness: 'compositor'
  outOfScopeNote: 'Slab 7b PRD authoring follows operator-confirmation of trial-2 critical-path subset (which of 11 must be LIVE for trial-2 reaching G3 cleanly).'
  slab7aImplications:
    - 'Vera _act body is already real (Slab 2a era); rubric semantics for terminal gates G0/G1/G4 are partially present, NOT scaffold-stubbed as the mapping checklist initially suggested.'
    - 'Quinn-R _act body is already real (two-mode pre/post-composition); G2C and G5 rubric semantics partially present.'
    - 'Slab 7a gate-fold work must acknowledge Vera + Quinn-R existing _act bodies; gate-rubric ⚠️ partial-status rows in mapping checklist need re-tier from "rubric semantics drop" to "rubric semantics partially present, need hardening for production composition path".'
classification:
  projectType: 'Internal multi-agent runtime extension (LangGraph orchestration layer)'
  domain: 'Online course content production / collaborative AI infrastructure'
  complexity: 'high'
  projectContext: 'brownfield'
  brownfieldNotes: 'Migration SHIPPED at 97842ac (2026-04-27). Slab 7a extends Slab 1-6 substrate with inter-gate conversational orchestration layer. Evidence anchor: trial 475df528-... paused-at-G1 cleanly 2026-04-28 (plumbing-PASS / content-FAIL).'
  governanceFloor:
    - 'Composition Specification (Option B / Path A-prime) — gate-precedence + dependency_map sourcing + chain-test-per-PR'
    - 'Pipeline Manifest Regime — Tier-2 minor pack-version bump (this PRD)'
    - 'Migration Story Governance JSON (frozen 2026-04-22) + sandbox-AC validator'
    - 'BMAD sprint governance (CLAUDE.md): bmad-create-prd → party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story; bmad-code-review before done'
inputDocuments:
  - _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-04-22.md
  - _bmad-output/planning-artifacts/research/technical-langchain-langgraph-migration-research-2026-04-21.md
  - _bmad-output/planning-artifacts/deferred-inventory.md
  - docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md
  - docs/project-context.md
  - docs/agent-environment.md
  - docs/dev-guide/composition-specification.md
  - docs/dev-guide/pipeline-manifest-regime.md
  - docs/dev-guide/migration-story-governance.json
  - docs/dev-guide/langgraph-migration-guide.md
  - state/config/pipeline-manifest.yaml
  - app/marcus/cli/trial.py
  - app/marcus/orchestrator/production_runner.py
  - app/manifest/compiler.py
  - app/specialists/texas/retrieval_dispatch.py
  - next-session-start-here.md
  - SESSION-HANDOFF.md
documentCounts:
  briefs: 0
  research: 1
  brainstorming: 0
  projectDocs: 6
workflowType: 'prd'
slabId: 'slab-7a'
slabName: 'Inter-Gate Conversational Orchestration (Orchestration Layer)'
parentMigrationPRD: '_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md'
siblingPRDs:
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md  # parent migration PRD
  - _bmad-output/planning-artifacts/prd.md  # legacy Wave 2B PRD (frozen reference, not relevant scope)
plannedSiblingPRDs:
  - prd-slab-7b-specialist-activation-quartet.md  # Slab 7b — Gary/Kira/Enrique port + Compositor greenfield
  - prd-doc-slab-7-prose-harvest.md  # Doc-Slab 7-D — post-trial-evidence prose harvest
---

# Product Requirements Document — Slab 7a: Inter-Gate Conversational Orchestration (Orchestration Layer)

**Author:** Juanl
**Date:** 2026-04-28
**Status:** Draft (Step 1 of 11 — workspace initialized)
**Project:** course-DEV-IDE-with-AGENTS (hybrid clone, `dev/langchain-langgraph-foundation` branch)
**Pack version target:** v4.2 (Tier-2 minor extension; additive conversational layer)
**Distinct artifact:** This PRD is sibling to `prd-langchain-langgraph-migration.md` (parent migration PRD). It is NOT an extension of legacy `prd.md` (Wave 2B summary, frozen reference).

---

## Operator Non-Negotiables (Read First)

These three guardrails are operator-ratified (2026-04-28) and bind every section, story, and dev-cycle of Slab 7a + 7b + Doc-7-D. Codex and any future reviewer parsing this PRD as plain markdown should treat these as the standing scope-floor:

- **SG-1 (Specialist roster floor):** the eleven specialists named for Slab 7b activation — **Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera** — cannot be reduced. Enforced structurally by NFR-I7 (`len(specialists) == 11` build assertion).
- **SG-2 (Legacy workflow step floor):** the **34-row mapping checklist** (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`) cannot lose rows. Essential-function preservation under different mechanism allowed; outright drops auto-rejected. Enforced structurally by NFR-I6 (CI row-count assertion blocks merge) + parity-test suite at `tests/parity/test_mapping_checklist_row_NN.py`.
- **SG-3 (Composition Spec invariants):** Composition Specification (`docs/dev-guide/composition-specification.md`) §3.1 SHA256+append-only, §3.5 gate precedence, §3.6 manifest-declared dependencies, §6 chain-test-per-PR, §9 Composition Smoke gate, §10 Decision Log, §11 migration triggers — all seven sections enforced structurally by NFR-I8 (`tests/parity/test_composition_spec_invariants.py`).

Subsequent mentions of these guardrails reference them as `(per SG-1)`, `(per SG-2)`, or `(per SG-3)` rather than re-enumerating.

## Three-Slab Trilogy at a Glance

This PRD (Slab 7a) is one of three sequenced slabs:

| PRD | Scope | Status | Sequenced |
|---|---|---|---|
| `prd-langchain-langgraph-migration.md` | Migration foundation (5 slabs, M1–M5) | SHIPPED at `97842ac` (2026-04-27) | — |
| **`prd-slab-7a-inter-gate-orchestration.md`** | **13 substrate-completeness deliverables across 5 clusters; orchestration layer; this document** | **Draft** | **First (current)** |
| `prd-slab-7b-specialist-activation-eleven.md` | Activates 11 specialists (Texas hardening, Irene Pass-1 refresh, Tracy/Gary/Kira/Enrique/Wanda port-shape, Quinn-R/Vera already-active hardening, Dan + Compositor greenfield) into the Slab 7a scaffold | Planned | Second (after 7a) |
| `prd-doc-slab-7-prose-harvest.md` | Post-trial-2 anti-pattern catalogs + worked examples + re-authored v4.2 essential-function reference (~400-line distillation) | Planned | Third (after first tracked trial post-7b) |

## Quick Reference (cold-pickup anchors)

| Question | Location |
|---|---|
| What does Slab 7a do? (JTBD) | Executive Summary §opening sentence |
| Why does it exist? (trial-475 evidence) | Executive Summary §"two trial-475 gaps" |
| What constitutes done? (trial-2 acceptance) | Success Criteria §A-1..A-7 + Project Scoping §MVP exit gate |
| 7 scope-binding commitments | Executive Summary §Scope-Binding Commitments |
| 10 frozen gates | Project-Type Specific Requirements §Gate topology |
| 11 specialists (canonical enumeration) | Functional Requirements §FR16 |
| 34-row mapping checklist | `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` |
| K-floor / target-range | NFR-T1 (canonical); NFR-CG5 cross-refs |
| Failure-mode (FM) checks | Success Criteria §Slab-7a-Shaped Failure Modes (FM-1..FM-10) |
| Innovation risks (IR) | Innovation & Novel Patterns §Risk Mitigation (IR-1..IR-7) |
| Scoping risks (SR) | Project Scoping & Phased Development §Risk-Based Scoping (SR-T1..SR-R3) |

## Glossary (acronyms used throughout)

- **JTBD** — Jobs-To-Be-Done (PM framing for user value)
- **HIL** — Human-In-Loop (operator-mediated decision points)
- **FM** — Failure Mode (Step 3 / Step 5 / Step 6 register IDs)
- **ADR** — Architecture Decision Record (D-numbered decisions in `architecture-langchain-langgraph-migration.md`)
- **K-floor / K-units** — story-cycle-efficiency discipline; see `docs/dev-guide/story-cycle-efficiency.md`
- **FR / NFR** — Functional / Non-Functional Requirement
- **SG-1/2/3** — Standing Guardrails (above)
- **CG-** — Compliance & Governance NFR / Domain Requirement ID

---

---

## Executive Summary

Slab 7a lets the operator collaborate with an eleven-specialist roster across a multi-hour course-production trial without (a) the run silently bypassing gates that should have stopped for input, or (b) the operator's attention degrading into rubber-stamp mode by slide 18 / hour 4. It does so by closing the two specific failure modes that paused the first tracked trial (`475df528-…`, 2026-04-28) cleanly at G1 — and structurally preventing the per-slide-array rubber-stamp degradation that surfaced as the load-bearing operator-friction concern in party-mode round 1.

### Position in the trilogy

Slab 7a is the orchestration half of a three-slab post-M5 effort. Slab 7b activates the eleven-specialist roster (Texas hardening, Irene Pass-1 refresh, Tracy / Gary / Kira / Enrique / Wanda port-shape, Quinn-R / Vera already-active hardening, Dan + Compositor greenfield) into the orchestration scaffold this PRD delivers. Doc-7-D harvests prose artifacts post-trial-evidence (anti-pattern catalogs, full migration-guide §12 worked examples, re-authored v4.2 essential-function reference). The migrated LangGraph runtime shipped at `97842ac` (2026-04-27); Slab 7a is post-M5 work on a stable substrate, not pre-MVP work on a moving one.

### The two trial-475 gaps Slab 7a addresses (closure demonstrated by trial-2)

**Gap 1 — silently-ignored gates.** The migrated runtime pauses on only four terminal gates (`G1`, `G2C`, `G3`, `G4` — declared as `PRODUCTION_GATE_IDS` in `app/manifest/compiler.py`). Fourteen other declared `gate_code` values in `state/config/pipeline-manifest.yaml` (G0, G0A, G0B, G1A, G1.5, G2, G2B, G2M, G2.5, G2F, G3B, G4A, G4B, G5) are silently ignored. Slab 7a expands the runner to honor all fourteen via manifest-declared fold-flags + subgraph-absorption (Composition Spec §3.5 gate precedence preserved; per-specialist non-blocking default unchanged).

**Gap 2 — missing directive composition.** Trial entry (`start_trial` in `app/marcus/cli/trial.py`) accepts `--input <corpus-path>` but no upstream code path converts that into a `directive.yaml` for Texas's `dispatch_retrieval` seam — so trial-475 invoked Texas with `directive_path=None`, which triggered the deterministic fixture stub. Slab 7a ships `app/marcus/orchestrator/directive_composer.py` (orchestration-side, per Composition Spec §3.6 manifest-declared dependency policy) to compose the directive from `--input` + §02 source-authority-map + §02A operator-directives.

### Slab 7a deliverables (substrate-completeness scope)

Closing Gap 1 (six structural items + one audit artifact):
- Checkpointer-native conversational gates (manifest-declared fold-flags; `state/config/gate_fold_manifest.yaml` audit artifact enumerating effective vs declared gates with mechanism per gate)
- Subgraph-per-specialist formalization (each specialist node compiles to its own LangGraph subgraph with own checkpoint boundary; reference scaffold for Slab 7b activations)
- `interrupt()`-per-slide subgraph for per-slide-array gates (G2B variant selection, G2F motion approval, G3B Storyboard B HIL review)
- Shared `pre-gate-marcus` LLM node (single LLM call site, single checkpoint boundary, Tier-1 additive manifest bump; emits C1 template-with-slots proposals with confidence + rationale)
- A2 single-decision shim layer for terminal gates (G1, G2C, G3, G4) with audience-layered help text
- Conversation persistence to `runs/<run_id>/conversation/<gate_id>/` sibling directory; learning-event schema additive bump v1.1→v1.2 (`kind:"operator_turn"`)
- HTML review-pack skeleton for per-slide-array gates (`runs/<run_id>/gates/<gate>-review-pack.html`; Slab 7a ships skeleton, Slab 7b populates with real specialist content)

Closing Gap 2 (one surgical patch):
- `directive_composer.py` orchestration module + tests + manifest dependency declaration

Operator-control-envelope guarantees (cross-cutting):
- Per-specialist "what I just did" summary writer (passthrough-stub in 7a; populated by real specialists in 7b)
- Unified namespaced vocabulary registry at `docs/conversational-gates/_registry/vocabulary.yaml` + auto-generated glossary script
- Operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md`, paired with a parity-test suite that fails CI if any legacy lever regresses
- Revise-loop UX with max-3 oscillation guard implemented as state-machine invariant in shared gate-runner substrate (`revise_count` field in checkpointer state; transition function enforces escalation at 3; gate-authors inherit not implement)
- C1 calibration tripwire (≥3 runs of confidence-correlation evidence before batch-approve unlocks per gate; tripwire re-locks if operator-override-rate exceeds threshold over rolling N-run window — exact threshold + N named in PRD §C-axis Implementation)

### What makes this special

Three differentiators distinguish Slab 7a from every prior migration slab:

1. **Checkpointer-native operator-control surface.** Prior slabs (1–6) consumed LangGraph as runtime; Slab 7a is the inflection point where checkpointer state becomes operator-readable evidence (trial-475's checkpoint file, with Slab 7a, becomes a versioned artifact — checkpointer state-shape acquires a format-versioning policy in this slab). CLI shims and HTML review-packs become thin renderers over LangGraph state, not the source of truth. Per-slide arrays carry via subgraph-with-`interrupt()` fan-out rather than CLI-loop-per-slide — the failure mode Quinn-R named in party-mode round 1 ("by slide 18 the operator is rubber-stamping") is structurally prevented, not policy-prevented.

2. **Essential-function preservation, not verbatim recreation.** The legacy v4.2 prompt pack is 1527 lines of operator-typed prose because the legacy runtime had no other mechanism for carrying operator decisions. Slab 7a preserves operator-decision essential function (every gate the operator needs to control is preserved) but explicitly trims legacy ceremony per Quinn-R's ruthless walk: drop §11B, merge §07D into §07F, compress §4.5 to default-accept-after-confirmation. Net: ten essential conversational gates (frozen as a PRD-output gate-inventory artifact, not a sprint-planning number). Each cut is anchored to a row in the mapping checklist (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`, 34 rows; first deliverable of Slab 7 PRD work, completed 2026-04-28).

3. **Trial-evidence-anchored design.** Every Slab 7a design decision traces to either trial-475 evidence or a named trial-2 readiness criterion: the directive-composer closes content-FAIL root cause from trial-475; subgraph-with-`interrupt()` prevents per-slide CLI collapse named in party-mode round 1; max-3 oscillation guard prevents trust-failure modes named in party-mode round 2; C1-with-calibration-tripwire prevents pre-fill-becomes-rubber-stamp degradation under multi-trial drift. Slab 7a does NOT audit the eleven specialists' `_act` bodies — that work belongs in Slab 7b. Marcus's runtime role as LLM call-site (the `pre-gate-marcus` node) resolves the Marcus-duality named in `dev-agent-anti-patterns.md`, with a defined prompt-pack contract authored as part of Slab 7a §C-axis Implementation.

The core insight: **the legacy v4.2 runtime had no checkpointer, no `interrupt()`, no subgraph composition, no LangSmith trace replay; reimplementing the prose layer would discard the most valuable thing we built.** Slab 7a keeps the operator-control envelope, replaces prose-as-mechanism with checkpointer-state-as-mechanism, and reserves prose for where it earns its weight (per-gate Markdown loaded by gate handlers, vocabulary registry, operator-control parity table).

### Scope-Binding Commitments (architectural non-negotiables)

These seven commitments BIND scope. Slab 7a stories that violate them must re-open party-mode consensus, not be relitigated at story-authoring time. Everything else in this Executive Summary is design preference and may be refined during story authoring.

1. **Subgraph-with-`interrupt()` fan-out** for per-slide-array gates — no CLI-loop-per-slide fallback, no parent-graph repeated-`interrupt()` shortcut.
2. **Max-3 oscillation guard as state-machine invariant** in shared gate-runner substrate — `revise_count` in checkpointer state, transition function enforces escalation, gate-authors inherit not implement.
3. **Frozen ten-gate essential-function inventory** — named gate list shipped as PRD artifact; an eleventh gate requires party-mode consensus + version bump.
4. **Pre-composition QA validator** as a substrate step in the gate-runner subgraph (catches the auto-fixable before reaching the operator).
5. **Decision-card vocabulary registry** as a typed substrate artifact (Pydantic schema + per-gate card type), not a style guide.
6. **C1 calibration-tripwire** with named threshold + lock-back behavior — see PRD §C-axis Implementation.
7. **Parity-test suite** that fails CI if any row in the operator-control parity table regresses (the parity-table itself is documentation; the parity-test suite is the substrate guarantee).

### Trial-2 readiness

Slab 7a + 7b + Doc-7-D are the necessary preconditions for a trial-2 attempt that targets G3 with eleven active specialists. Trial-2 itself is the verification gate, not a Slab 7a deliverable. Codex deployment is operator-blessed for parallel-authoring of port-shape Slab 7b stories (Tracy / Gary / Kira / Enrique / Wanda) and `bmad-code-review` passes on each Slab 7a + 7b story close; specific Codex parallel-authoring story assignments are scoped at PRD §Codex Deployment Plan (later in this document).

When trial-2 closes cleanly, the operator participates in roughly ten essential conversational gates (a three-gate reduction from legacy's thirteen surfaces), revise loops carry max-3 oscillation guard as substrate invariant, vocabulary registry prevents per-gate dialect drift, the operator-control parity-test suite is green, and the v4.2 1527-line pack becomes a ~400-line distillation under Doc-7-D harvest.

## Project Classification

- **Project Type:** Internal multi-agent runtime extension — an inter-gate conversational-orchestration layer over a LangGraph-based production runner, consumed by a single operator plus an eleven-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) coordinated by Marcus orchestrator. Codex is operator-blessed as a parallel dev-agent for port-shape Slab 7b activations and as a `bmad-code-review` voice on story closes.
- **Domain:** Online course content production / collaborative AI infrastructure. Domain-specific concerns: HIL tamper-evidence (FR34); audit-replay reproducibility (Composition Specification §3.1 SHA256 output digests); operator-control envelope preservation against legacy v4.2 floor; checkpointer state-shape becomes versioned artifact in Slab 7a (format-versioning policy decided at PRD §Substrate Versioning); per-trial cost discipline (~5–8× cost per tracked trial run vs trial-475 with eleven specialists active).
- **Complexity:** **High.** Loaded substrate concerns include LangGraph + Postgres checkpointer (D3); frozen-graph ceremony with Tier-1/2/3 pack-version policy (Slab 7a is Tier-2 minor); append-only `ProductionEnvelope` substrate + `ProductionDispatchAdapter` translation layer (Composition Specification Option B / Path A-prime, with named §11 migration triggers to Option C); fourteen declared gate codes with `gate_overrides` precedence rule and manifest-as-graph-config (D6); multi-pass envelope Path Z (Slab 6.1 close); sandbox-AC governance; BMAD sprint governance; four-file-lockstep model + JSON Schema + golden + shape-pin tests; A1–A17 + P1–P3 anti-pattern catalogs; K-floor / target-range / dual-gate-vs-single-gate discipline.
- **Project Context:** **Brownfield.** Migration unconditionally SHIPPED at `97842ac` (2026-04-27); first tracked trial 475df528 supplies load-bearing evidence for every Slab 7a design decision that traces to trial-evidence; ~14 working specialists across the substrate (eleven in operator-named Slab 7b roster); thirteen architectural decisions ratified in `architecture-langchain-langgraph-migration.md`; two-round party-mode consensus on the four design axes (A/B/C/D) plus four added axes (E1 essential-function audit, E2 directive-composition ownership, E3 replay-fixture strategy, E4 prose-surface registry).

---

## Meta-Directive — Remaining PRD Steps (3 through 13)

**Per operator instruction (2026-04-28):** each remaining step opens with a 3–4 voice `bmad-party-mode` round; assistant synthesizes consensus or supermajority position; consensus content is presented as proposed [C] for operator final approval at step menu.

**Hard scope-floor guardrails — auto-reject any consensus position that violates either:**
1. **Specialist roster floor:** the eleven specialists named for Slab 7b activation (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) cannot be reduced. A consensus position dropping any specialist is auto-blocked and flagged to operator before proceeding.
2. **Legacy workflow step floor:** the 34-row mapping checklist (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`) cannot lose rows. Essential-function preservation under different mechanism is allowed (e.g., merging §07D into §07F per Quinn-R's ruthless walk); outright dropping a row is auto-blocked.

---

## Success Criteria

### User Success

The user is the operator running multi-hour course-production trials with the eleven-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) against the frozen ten-gate inventory. User success is observable on the trial transcript and the LangSmith run tree, not asserted by the operator.

| ID | Outcome | How measured | Threshold |
|----|---------|--------------|-----------|
| US-1 | Operator reaches G3 (Sequencing approved) on real content without silent gate-bypass | LangSmith run tree shows ordered `interrupt(...)` events at every gate; operator `Command(resume=...)` payload at each | 100% gate transitions in trial-2 carry an operator decision-card; zero `state.gate_index += 1` writes outside `interrupt()`-resumed paths |
| US-2 | Operator participates in ~10 essential conversational gates; legacy 34-row coverage maintained | Gate-presence audit against `slab-7-legacy-migrated-mapping-checklist.md` 34-row inventory; each row maps to a present `interrupt()` site OR a documented essential-function-preserved-elsewhere annotation | All 34 legacy rows accounted for in trial-2 (10 gates fired + 24 essential-function-preserved); zero dropped rows |
| US-3 | Revise loops cannot grind — max-3 oscillation guard fires deterministically as state-machine invariant | Parity-test `test_oscillation_guard_invariant` asserts `revise_count <= 3` is a hard graph-edge condition; substrate refuses 4th revise per slide; emits `oscillation_escape_required` decision-card | Zero trial transcripts show `oscillation_count > 3`; guard-trip emits operator decision-card "escalate or accept-as-is", not silent loop |
| US-4 | No hour-4 rubber-stamping — operator engagement observably distributed across trial | Engagement-signal rate (override entered OR explicit ack-token, not blank-enter) in last quartile of trial-2 ≥ 30% of first-quartile rate; `_artifacts/trial-2/engagement_decay_report.md` auto-generated post-trial | Last-quartile engagement-rate ratio ≥ 0.30 of first-quartile; if breached, C1 calibration tripwire fires |
| US-5 | Decision-card vocabulary is closed and predictable — no per-gate dialect drift | `decision_card_registry.yaml` enumerates every directive enum value per gate; UI/CLI presents only registered values; CI test `test_no_ad_hoc_vocabulary_tokens` AST-scans gate-handler modules | 100% of trial-2 decision-cards validate against the registry; zero free-text directive fallbacks |
| US-6 | Per-slide arrays don't collapse to rubber-stamp | Compound: (a) AST grep — G2B/G2F-merged/G3B implementations contain `subgraph` + `interrupt()`; parent-graph contains zero per-slide-loop `interrupt()` calls. (b) HTML review-pack written + opened (browser-open event logged) at each per-slide-array gate. (c) ≥50% per-slide decisions show engagement signal | All three sub-checks green |

### Business Success

| ID | Outcome | How measured | Threshold |
|----|---------|--------------|-----------|
| BS-1 | Substrate-completeness claim holds — all 13 Slab 7a deliverables ship with seven scope-binding architectural commitments observable in code | Deliverable-by-deliverable closeout audit; party-mode green-light review against Executive Summary checklist | 13/13 deliverables `done`; 7/7 commitments grep-able in `app/` |
| BS-2 | Trial-2 readiness predicate satisfied (readiness, NOT Slab 7a deliverable per Mary R2 weakening): trial-2 launchable against Slab 7a substrate without further code changes | Pre-trial-2 dry-run on non-load-bearing fixture course; Marcus orchestration green | Slab 7a closeout + ≤1 week dry-run window; zero blocking defects against trial-2 launch checklist |
| BS-3 | Trial-2 cost stays within bounded-MVP envelope (~5–8× trial-475 baseline) | LangSmith cost dashboard for trial-2; reconciled against `_bmad-output/cost-ledger.md` | Trial-2 total LLM spend ≤ $3.00; per-gate spend ≤ $0.30 |
| BS-4 | No CI runaway from four new live-API surfaces (gamma, kling, elevenlabs, wondercraft, dan-api-tbd) | `.github/workflows/canary.yml` schedule audit; monthly CI cost ledger | T4 ≤ 3 end-to-end runs/night × 30 nights = 90 runs/month; monthly live-API CI spend ≤ $50 (operator-set ceiling, two orders of magnitude under the $4K runaway scenario) |
| BS-5 | Slab 7b activation feasibility unblocked — eleven-specialist roster wired and addressable from Marcus orchestration | `specialist-registry.yaml` audit; integration test `test_eleven_specialists_addressable` | 11/11 specialists return non-null handler; zero fallback-to-Marcus-stub paths in trial-2 |

### Technical Success

Tier discipline is the spine; budgets are the tripwire; K-floor is the efficiency contract; sandbox-AC inventory is the precondition for opening any Slab 7b specialist story.

**T1 — Orchestration unit tests** (substrate-only, no specialist binding)
- Count: 35–45 aggregate. Wall-clock budget <60s aggregate (stop-the-line).
- Coverage: gate-graph topology; decision-card vocabulary closure; subgraph isolation; calibration-tripwire activation paths; replay-from-fixture loader determinism.

**T2 — Replay-from-fixture orchestration tests** (substrate + recorded specialist outputs)
- Count: 25–35 aggregate. Wall-clock budget <5min aggregate (stop-the-line).
- Coverage: end-to-end gate traversal G0→Gn from fixtures; pack-hash determinism across replay; cache-hit-rate harness ≥85% across 10 specialist configs + 1 Compositor pipeline-determinism harness; cross-gate handoff invariants.

**T3 — Specialist-bound integration** (lives in Slab 7b; minimal in 7a)
- Count in 7a: 0–3 smoke shims maximum to validate bind-point contract; full T3 lives in Slab 7b. Wall-clock <2min/shim. Flakiness >2% = quarantine + follow-on, do not retry.

**T4 — End-to-end live** (capped, audited, expensive)
- Count in 7a: ≤3 end-to-end canaries (hard cap). Cost ceiling ~$0.60 aggregate (T2 + T4 fixture-record + audit-canary).
- Cadence: record-once-replay-forever with quarterly re-record cadence (operator-gated). Live-API-on-CI is dead for API specialists.

**K-floor / target-range discipline**
- Gate-shape stories: single-gate, K-floor 1.2–1.4×.
- Directive-composer story: dual-gate, K-floor 1.6× (trial-475 root-cause-class).
- Aggregate Slab 7a: ~21 K-units.
- Over-spend tripwire: any single story exceeding 1.7× K closes the dev round, escalates to party-mode.

**Sandbox-AC inventory precondition (5 entries before any Slab 7b story opens)**
gamma, kling, elevenlabs, wondercraft, dan-api-tbd — each declares forbidden-CLI-set, shipped-Python-dep substitute (httpx/SDK), `pytest.skip(...)` policy when service unreachable, and operator-gated AC split for live evidence. Inventory PR is hard precondition; Slab 7a does not close green-light without it; Slab 7b does not open without it.

**Replay-fixture strategy invariants**
Record-once-replay-forever; fixtures committed under version control with content-addressable hash. Quarterly re-record cadence. Fixture loader deterministic. Cache-hit-rate harness parametric (single binary, config-driven). Live-API-on-CI rejected for all five API specialists.

### Measurable Outcomes

| Metric | Target | Tripwire |
|---|---|---|
| Frozen gate inventory | 10 gates (operator-ratified post-Quinn-R compressions) | drift = halt |
| Declared gate-codes honored | 14 codes (10 pause-points + 4 fold-targets per `gate_fold_manifest.yaml`) | silent ignore = halt |
| Specialist activation roster | 11 (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) | <11 = scope-floor violation, halt |
| Legacy mapping checklist rows | 34 preserved | <34 = scope-floor violation, halt |
| Slab 7a code surface | ~25 files / ~530 LOC | — |
| Slab 7a test surface | ~40 tests in 7a (subset of 75–100 four-tier suite) | — |
| Slab 7a development cost (T2/T4 dev runs) | ~$0.60 total LLM spend | over-budget = halt |
| Slab 7a effort | ~21 K-units | per-story >1.7× K halts |
| Trial-2 launch window | ≤8 weeks from Slab 7a closeout | — |
| Trial-2 cost ceiling | ≤$3.00 total | BS-3 |
| T1 wall-clock | <60s aggregate | stop-the-line |
| T2 wall-clock | <5min aggregate | stop-the-line |
| T4 canary count | ≤3 | hard cap |
| Cache hit rate (warm) | ≥85% across 10 specialist + 1 Compositor harness | <80% = fixture-staleness investigation |
| Live-API-on-CI for API specialists | 0 occurrences | any occurrence = governance failure |
| Calibration-tripwire exercised in trial-2 | ≥1 fire + ≥1 quiet during trial-2 | 0 fires = "shipped but never exercised" failure |
| Parity-test suite green for trial-2 readiness | 100% pass | any red = trial-2 not ready |
| Composition Smoke evidence per slab-opener | 1 per slab-opener (Composition Spec §9) | missing = slab-opener not complete |
| Sandbox-AC inventory entries | 5 (gamma, kling, elevenlabs, wondercraft, dan-api-tbd) | <5 = Slab 7b open blocked |

### Slab 7a Acceptance (concrete clauses, artifact-backed)

| Clause | Artifact | Check |
|---|---|---|
| A-1 | All 7 scope-binding commitments landed | Executive Summary §Scope-Binding Commitments | each commitment has a story-ID reference + matching story marked done in `sprint-status.yaml` |
| A-2 | 14 declared gate_codes resolved (no silent ignore) | `state/config/gate_fold_manifest.yaml` | SM-1 metric green; zero `mechanism: ignore` or absent-mechanism entries |
| A-3 | Parity-test suite green | `tests/parity/` directory | every legacy operator-control lever from 34-row mapping checklist has reachable test; suite green; coverage report attached |
| A-4 | Calibration-tripwire mechanism exercised in trial-2 | `_artifacts/trial-2/calibration_tripwire_log.jsonl` | log contains either `fired: true` event OR `armed_check: passed` event (both count as exercised) |
| A-5 | Trial-2 closes through G3 cleanly | `_artifacts/trial-2/run_summary.yaml` | `terminal_gate: G3` AND `silent_bypass_events: 0` AND `specialist_roster_count: 11` |
| A-6 | Mapping-checklist 34-row coverage maintained | PRD §Mapping Checklist | 34 rows present; each row has `essential_function` field; legacy↔migrated mechanism cited per row |
| A-7 | Operator-friction metrics SM-1..SM-6 all green at green-light | each metric's named artifact | each metric's green-light check passes |

### Slab-7a-Shaped Failure Modes (checkable at green-light, not discovered in trial)

Each has a concrete check the green-light party-mode round can run in five minutes or less. If any returns "this matches," green-light blocks.

| FM | Description | Check |
|---|---|---|
| FM-1 | Gate-count drift (ships with 11 or 12 gates) | T1 canary asserts canonical count of 10 in `state/config/gates.yaml` |
| FM-2 | Max-3 hand-rolled per gate vs substrate inheritance | AST scan: any gate-handler module contains private `revise_count` counter or `if count > 3` branch (pass = all 10 gates inherit from `state.machine.revise_guard` only) |
| FM-3 | Subgraph degenerating to parent-graph-loop | `pytest tests/structural/test_per_slide_subgraph_pattern.py` red OR parent graph contains `interrupt()` inside per-slide `for` loop |
| FM-4 | Decision-card vocabulary fragmentation | CI test `test_no_ad_hoc_vocabulary_tokens` red OR vocabulary.yaml diff between Slab-7a-open and Slab-7a-close shows tokens added without registry update |
| FM-5 | Calibration-tripwire shipped but never exercised | `_artifacts/trial-2/calibration_tripwire_log.jsonl` missing OR contains zero entries (A-4 inverse) |
| FM-6 | Parity-test suite missing tests for any legacy lever | Coverage matrix: 34-row mapping checklist cross-referenced against `tests/parity/` test names; any unmapped row = fail |
| FM-7 | HTML review-pack skeleton ships but isn't opened in trial-2 | `_artifacts/trial-2/decision_log.jsonl` shows zero `review_pack_opened: true` events at G2B, G2F-merged, OR G3B (UX promise unverified) |
| FM-8 | Engagement-decay floor breached silently | SM-4 ratio < 0.30 AND no escalation event raised mid-trial (operator-friction analog of FM-1) |
| FM-9 | Pack-hash drift on replay-regression (Slab 6 carry-over) | T2 canary asserts identical pack-hash run-to-run on identical inputs; trial-475 root-cause-class precursor — non-negotiable |
| FM-10 | LangSmith trace-id real-binding deferred & unexercised (Slab 6 carry-over) | T2 canary exercises placeholder-binding under fixture replay; asserts placeholder is replaceable cleanly when real-binding lands |

## Product Scope

### MVP — Minimum Viable Product

Slab 7a substrate-completeness, operator-ratified 2026-04-28. All 13 deliverables ship together. **MVP threshold:** trial-2 reaches G3 cleanly with the eleven-specialist roster activated by Slab 7b. Anything that doesn't move that threshold is out of MVP.

The 13 deliverables organize into five clusters:

**Cluster A — Inter-gate orchestration substrate (closes trial-475 silent-bypass gap)**
1. Inter-Gate Conversational Orchestration runtime — typed orchestrator carrying operator/specialist exchanges between gates with structured turn-records.
2. Directive-composition contract (`app/marcus/orchestrator/directive_composer.py`) — closes trial-475's missing G1 piece; converts `--input <corpus-path>` → `directive.yaml` for Texas's `dispatch_retrieval` seam.
3. Gate-verdict envelope (typed) — verdict carries `pass | hold | fail` plus structured remediation pointer.

**Cluster B — Eleven-specialist activation surface (closes roster-readiness gap)**
4. Specialist activation contract — uniform entry/exit shape for all eleven.
5. Specialist-state persistence shape — checkpointer state-shape as versioned artifact (cross-restart resume is Slab 8; shape freezes here).
6. Specialist-roster registry (`state/config/specialist-registry.yaml`) — single source of truth for the eleven.

**Cluster C — Operator-loop guarantees (closes hour-4 rubber-stamp gap)**
7. Operator-turn structured-record format — every intervention captured as typed record; hour-4 fatigue visible in the trace.
8. Gate-bypass detection hook — runtime check fires when verdict transitions without required remediation pointer.
9. Marcus duality boundary enforcement — orchestrator-mode vs specialist-mode separation structurally enforced (resolves Marcus-duality named in `dev-agent-anti-patterns.md`).

**Cluster D — Replay and audit substrate (closes evidence-recoverability gap)**
10. Trial-run capture envelope — every trial run produces structured artifact bundle by construction.
11. Pack-hash binding in capture — replay-regression has pack-hash on every captured turn (drift remediation is Growth; binding ships now).

**Cluster E — Cross-cutting envelope guarantees**
12. Pydantic-v2 schema discipline across 1–11 — `validate_assignment=True`, tz-aware datetimes, triple-layer red-rejection on closed enums per pydantic-v2-schema-checklist.
13. Mapping-checklist 34-row Legacy↔Migrated traceability (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`) — every legacy row maps to migrated mechanism; outright drops auto-rejected. Audit floor.

**MVP exit gate:** trial-2 runs end-to-end, reaches G3 with eleven specialists, no fix-on-the-fly patches, no silent gate-bypass.

### Growth Features (Post-MVP)

**Slab 8 candidates (runtime/tooling):**
- Checkpointer state-traversal CLI (`marcus pending`, `marcus history <run-id>`, `marcus resume <run-id>`)
- `astream_events` HUD replacement of `run_hud.py`
- Replay-regression pack-hash drift remediation
- PR-TR Trial Resumption capability + trial-branch discipline (deferred-inventory entry)
- Texas best-available-medium selection (Epic 27 follow-on)

**Doc-Slab 7-D (post-trial-2 documentation harvest):**
- Anti-pattern catalogs harvested from trial-2 real evidence
- Full `langgraph-migration-guide.md` §12 worked examples per specialist (eleven examples)
- Re-authored v4.2 essential-function reference (~400-line distillation)

**Slab 6 deferred carry-overs:**
- LangSmith trace-id real-binding
- Multi-checkpoint walking / cross-restart resume / verdict-rejection branching

**Calibration-prerequisite (gates Vision):**
- C2 confidence-gated default-and-override — requires N≥30 trials calibration corpus

### Vision (Future)

**Composition Spec §11 migration triggers — Option C** (LangGraph subgraph composition with parent-graph reducers): fires when one of five named triggers becomes real production need. Currently 0 of 5 active. Slab 7a's job is to not foreclose Option C migration.

**Epic 15 chain reactivation** (gated on first tracked trial-run close + 15-1-lite-marcus close): 15-2 retrospective artifact → 15-3 upstream feedback routing → 15-4 synergy scorecard → 15-5 pattern condensation → 15-6 workflow-family ledger → 15-7 calibration harness.

**Multi-trial calibration corpus (~30+ trials) → C3 evolution** (default-on-override-by-exception). Operator stops actively gating each verdict and only intervenes on exception.

**Post-M5 greenfield specialist activations:** Mike, Eli, Mira, Sally, Kim, plus possibly Paige (if scoped as runtime specialist). Generated on-demand via `bmad-create-specialist`. **The eleven-specialist MVP roster is the floor, not the ceiling.**

**Workflow-family expansion per Epic 18** — podcasts, infographics, cases, quizzes. Each new family ships as Tier-3 pack family per Pack Versioning Policy (party-mode consensus required before dev opens).

---

## User Journeys

### Journey 1 — Primary User Happy-Path: A Saturday Morning Production Trial

**Opening Scene — 7:47 AM, Coffee Steam and a Clean Terminal**

Juan settles in. The corpus folder for *Lesson 04: Photosynthesis Foundations* is already staged at `course-content/courses/photosynthesis-foundations/` — twelve PDFs, a Notion link, three Box URLs, one Playwright-shaped page. He types one line:

```
bmad-trial start --input course-content/courses/photosynthesis-foundations/
```

**Emotion: calm, slightly braced.** The last manual trial took eleven hand-holds. He's hoping today is different.

The screen doesn't ask him eleven questions. **Marcus's pre-gate node fires the directive composer** (`directive_composer.py` — Slab 7a's Gap-2 closure deliverable), inspects the corpus directory, recognizes the disk files as corpus-shaped, recognizes the Notion + Box + Playwright entries as fetch-shaped directives, and **pre-fills a single composed directive** for Texas. Marcus shows it back: *"Here's what I'm sending Texas. Approve?"* Juan reads four lines, hits enter. **Calm becomes confident.**

**Rising Action — G0 through G2: Eleven Specialists Find Their Seats**

**G0 — Preflight + Ingestion-fold.** Texas wakes (`pre-gate-marcus` → Texas subgraph), runs source-authority validation across all four shapes, ingests via the retrieval contract, and folds what used to be the standalone ingestion gate into the same envelope write. **Vera's G0 fidelity check runs inline** — rubric scores post to the ProductionEnvelope append-only. Marcus surfaces a one-screen summary. Juan sees provenance for every source. **Confidence holds.**

**G1 — Lesson Plan Pass-1 + Plan-lock-fold.** Irene takes Pass-1 co-authoring. Tracy enriches with research-shaped intent (the connective tissue Pass-2 will lean on). Vera's G1 fidelity check stamps the plan. The old plan-lock gate folds into G1's envelope commit — no separate ceremony. Marcus presents the lesson plan in conversational form, not a wall of YAML. Juan reads it like a colleague's draft. He requests one tightening on Slide 7. The **max-3 oscillation guard** notes the revise count at 1/3. Irene revises. Approved. **A flicker of pride — the plan reads better than his manual baseline.**

**G2 — Narration Pass-2 + Storyboard-A authorization.** Irene returns for Pass-2; the narration carries Tracy's enrichment forward. Storyboard-A (the structural skeleton) authorizes. Marcus shows the storyboard side-by-side with the lesson plan. Juan approves. **Calm. The rhythm is working.**

**G2B — Per-slide Variant Selection (Gary).** Here is where the **subgraph-with-interrupt() per-slide array** earns its keep. Gary generates variants via Gamma for all 14 slides in parallel. Marcus assembles the **HTML review-pack** — one page, 14 slide cards, three variants each. Juan scrolls, clicks his picks, hits "submit." Quinn-R's G2C variant gate validates the selection set against rubric. **Anxiety that *would* have shown up on slide 9 in a manual trial — doesn't.** Confidence climbs.

**G2F-merged — Per-slide Motion Designation + Approval (Kira).** Kira proposes motion designations (Kling API) per slide. Quinn-R reviews motion gate. Marcus surfaces the merged per-slide HTML pack again — designation + preview. Juan approves twelve, asks Kira to soften two. Revise count 1/3. Kira returns. Approved. **Relief — the motion choices feel his.**

**Climax — G3: Sequencing Approved, Eleven Voices in the Envelope**

**G3 — Sequencing Approved + Storyboard-B HIL review.** This is the moment.

Marcus presents Storyboard-B: the full sequenced cut. The ProductionEnvelope, scrolled in summary, shows **eleven specialist signatures** stacked append-only:
- **Texas** (G0/G1 source authority + ingestion + retrieval)
- **Irene** (Pass-1 + Pass-2)
- **Tracy** (Pass-2 enrichment)
- **Vera** (G0, G1, and the G3 fidelity G4 check now stamping)
- **Gary** (G2B variants)
- **Kira** (G2F motion)
- **Quinn-R** (G2C + G2F gates)
- **Dan** (helper/aux contributions threaded across G1–G2 per Slab 7b activation)
- **Wanda** (podcast/audio bed scoped into the storyboard's audio track)
- **Enrique** (queued for G4 narration synthesis — pre-flight ack visible)
- **Compositor** (queued for G6 — deterministic assembly plan visible)

Juan reads Storyboard-B end to end. He approves. **G3 closes.** The terminal prints `g3.sequencing.approved`.

**Emotion: quiet pride.** Three hours forty minutes in. No relitigation. No specialist skipped. No gate snuck past him.

**Resolution — Handoff Forward**

Marcus posts the next-step ribbon: *"Ready for G4 narration (Enrique) → G5 pre-composition QA (Quinn-R) → G6 compositor assembly → G7 handoff."* Juan refills the coffee. **The trial isn't done — but the hard half is, and he wasn't a bottleneck once.** That's the journey Slab 7a buys him.

---

### Journey 2 — Primary User Edge-Case: Slide 17 Goes Sideways, but the Trial Still Lands

**Opening Scene — G2B, Slide 17 of 30**

It is the second tracked trial after Trial-475's clean pause-at-G1. The operator has cleared G1 (Texas returned a real corpus this time, not a fixture stub) and G2A (Irene Pass-1 coauthored cleanly). They are now at **G2B** — per-slide variant selection by **Gary**. Thirty slides, two variants each, served as a static HTML review-pack with checkbox columns and a free-text "delta-directive" field per row. The operator is in their pacing groove: A, A, B, A, B, B, A...

Slide 17 stops them.

The directive for slide 17 was explicit: *literal-visual leads; reference the diagram on slide 12 of the corpus PDF*. Gary has returned two **text-led** variants. Variant A is a bulleted summary; Variant B is a single-paragraph synthesis. Neither shows the diagram. Neither is what was asked for.

The operator's first reaction is mild — *Gary missed the directive on this one slide; the revise-loop is exactly for this.* They check `revise` on slide 17 and type into the delta field: **"more visual; the source asset is the diagram on slide 12 of corpus PDF."** They submit the review-pack.

**Rising Action — v2, then v3**

The substrate routes the delta-directive back into the **Gary subgraph** — not back to the parent graph (FM-3 guard holds; the subgraph-degenerating-to-parent-loop check passes). Gary regenerates slide 17 as **v2**. The HTML review-pack refreshes with v2 highlighted.

v2 is *still text-led* — Gary has bolded a phrase and added a caption referring to "the diagram," but no diagram is rendered. The operator's anxiety ticks up. They sharpen the delta: **"render the actual diagram inline; do not describe it in prose."** Submit.

**v3** arrives. v3 has a diagram — but it is the wrong diagram (slide 8 of the corpus, not slide 12). A *different* problem. The operator's frustration is now explicit; they consider just hand-editing slide 17 themselves and moving on.

**Climax — Max-3 Oscillation Guard Fires**

The operator clicks `revise` a fourth time. The substrate **refuses**. The max-3 oscillation guard — encoded as a state-machine invariant on the G2B node, not as prose guidance — fires cleanly. A **decision-card** renders in the review-pack header, drawn from the decision-card vocabulary registry: `oscillation_escape_required`. Three options, each a typed verdict:

- **(a) accept-as-is** — slide 17 freezes at v3; rationale required; logged to conversation persistence.
- **(b) reject-and-skip-slide** — slide 17 drops from the deck; downstream specialists notified.
- **(c) abort-run** — full trial halt; G2B state preserved for post-mortem.

The decision-card is the moment of **clarity**. The operator's frustration converts into a bounded choice. They pick **(a) accept-as-is**, type rationale: *"v3 diagram is wrong but acceptable; not blocking trial; flag for post-trial Gary calibration review,"* and submit.

**Resolution — Tripwire Fires; Trial Lands**

The acceptance is logged. Immediately, **C1 calibration-tripwire** fires: operator override-rate at G2B has crossed the per-trial threshold. The tripwire **re-locks batch-approve at G2B for the next 3 trials** — confidence-correlation evidence must rebuild before Gary's per-slide variants can be batch-trusted again. Operator sees the lock notification; nods. *That is the system catching what I would have forgotten to flag.*

They continue. Slides 18–30 clear at normal pace. **G2C** (Wanda, Enrique, Kira on remaining surfaces) clears clean. **G3** reaches cleanly. The trial lands.

**Emotional arc:** groove → mild concern (v1 miss) → anxiety (v2 still wrong) → frustration (v3 different problem) → **decision-clarity** (oscillation-escape card) → grounded acceptance (rationale logged) → **relief** (tripwire caught the calibration debt; G3 reached anyway).

**Essential-function preservation:** Legacy shape was prose guidance ("if Gary keeps missing, talk to him again, then escalate to the operator"). Migrated shape is a state-machine invariant with a hard counter, a typed escape verdict, and an automatic calibration consequence. Same operator-facing function (recover from a specialist miss without aborting the trial); enforcement moved from prose-discipline to substrate-invariant.

---

### Journey 3 — Admin/Ops: Operator-as-Self-Administrator (one-week-gap re-entry)

**Trigger:** Operator returns after a 7-day gap; needs to reconstitute project state without losing governance threads.

**Steps:**
1. **Hot-start ramp.** Operator opens `next-session-start-here.md`. The standing "Deferred inventory status" line (CLAUDE.md binding consultation point #2) shows current counts — backlog epics / deferred stories / follow-ons. Operator reads, registers what's queued. *Slab 7a deliverable touched:* deferred-inventory governance artifact remains the single source of truth.
2. **Deferred-inventory consultation.** Operator opens `_bmad-output/planning-artifacts/deferred-inventory.md`. Notes Slab 7b hardening entries (Wanda retry-loop from Journey 4), 15-1-lite-irene + 15-1-lite-gary follow-ons, §4.55 conditional follow-on. Cross-checks against trial-475 evidence — anything reactivatable?
3. **Sprint-status pull.** Reads `_bmad-output/implementation-artifacts/sprint-status.yaml`. Current Slab 7a story state surfaces; identifies which story is `ready-for-dev` vs `in-progress` vs `review`.
4. **Trial-475 evidence verification.** Confirms `state/config/runs/475df528-…/` checkpointer state-shape, learning-events, and pause-at-G1 artifacts are intact. *Slab 7a deliverable:* checkpointer state-shape as versioned artifact — operator must be able to inspect a closed trial's persisted state without re-running.
5. **Frontmatter guardrail audit.** Opens Slab 7a PRD; verifies the 11-specialist roster registry block and 34-row mapping-checklist reference still match the floor. Any drift = STOP signal. *Deliverables touched:* specialist-roster registry (floor-11), mapping-checklist 34-row traceability artifact.
6. **Next-action lock.** Records the chosen next-action in `next-session-start-here.md` for the *next* hot-start. Closes the loop.

---

### Journey 4 — Support/Troubleshooting: Operator + Codex investigate trial-2 cost anomaly

**Trigger:** Trial-2 reached G3 cleanly. Cost telemetry: $4.50. BS-3 budget: ≤$3.00. Variance = $1.50 (50% over). Investigation opens.

**Steps:**
1. **Anomaly capture.** Operator notes the over-budget signal at trial close. Files anomaly ticket in working notes; tags Codex for parallel investigation per Executive Summary §Codex Deployment Plan.
2. **LangSmith trace pull (Codex).** Codex queries LangSmith API for trial-2 trace_id. *Slab 7a deliverable:* LangSmith trace integration as observability primitive. Codex filters spans by specialist; spots Wanda emitting 3 LLM API calls where the cache-hit harness expected 1.
3. **Checkpointer state-traversal (Operator).** The deferred Slab-8 `marcus pending` CLI is NOT shipped. Operator falls back to direct Postgres query against the checkpointer schema (`SELECT thread_id, checkpoint_id, channel_values FROM checkpoints WHERE thread_id = …`). *Deliverable touched:* checkpointer state-shape as versioned, queryable artifact — the schema MUST be documented well enough that direct-SQL fallback works without spelunking. Specialist-state persistence shape (Wanda's _act-scope state envelope) is read directly.
4. **Root-cause identification.** Wanda's `_act` body contains a retry-loop that fires on API timeout. Trial-2 hit a transient ElevenLabs timeout; retry-loop triggered twice → 3 calls instead of 1. Cache key not consulted on retry path.
5. **Slab 7b follow-on filing.** Per CLAUDE.md binding consultation point #3, operator files "Wanda retry-loop hardening" into `deferred-inventory.md` §Named-But-Not-Filed Follow-Ons. *Deliverable:* deferred-inventory governance integrity preserved.
6. **Trial-2 evidence preservation.** Operator preserves `state/config/runs/trial-2-…/` — the over-budget run becomes the regression artifact for the Slab 7b Wanda story.

---

### Journey 5 — API/Integration: Codex authors Slab 7b Tracy port-shape activation story

**Trigger:** Slab 7b sprint opens. Per Executive Summary §Codex Deployment Plan, Codex picks up parallel-authoring for the Tracy passthrough → active-LLM port. Claude handles bmad-code-review on the parallel-authored output (mutual-handoff pattern).

**Steps:**
1. **Reference ingestion.** Codex reads, in order: Slab 7a PRD scope-binding commitments (the 11-specialist + 34-row floors); fold-flag manifest (Tracy's current passthrough flag state); mapping-checklist Tracy rows (legacy Tracy behavior vs. target migrated behavior); decision-card vocabulary registry (Tracy's emitted decision shape).
2. **Template-conformance.** Codex pulls Slab 2a.2 Irene activation as the canonical template. *Deliverable:* specialist activation contract — Irene is the reference shape; Tracy port follows it row-for-row.
3. **Story-spec authoring.** Codex drafts `slab-7b-tracy-activation` story. Includes T1 Readiness block, required readings citation, scaffold reference, K-floor target range, gate-mode designation pulled from `migration-story-governance.json` (no relitigation).
4. **Sandbox-AC validation.** Codex runs `python scripts/utilities/validate_migration_story_sandbox_acs.py <story>`. *Deliverable:* sandbox-AC inventory — spec passes; dev-agent ACs use shipped deps (httpx for any LLM-endpoint poke), no operator CLIs leaked.
5. **Implementation.** Codex implements Tracy `_act` body per Irene template. Tracy now emits decision-card-shaped output instead of passthrough echo.
6. **Canary harness.** T1 + T2 canaries run. T2 parametric cache-hit-rate harness now includes Tracy as a parameter row. *Deliverable:* cache-hit harness parametric config — adding Tracy is a config-line change, not a code change. All green.
7. **Review handoff.** Codex marks story `review`. Claude runs `bmad-code-review` (parallel-author mutual-handoff per Executive Summary). Pass. Story lands.

---

### Journey Requirements Summary

Each of the five journeys exercises a different cross-section of Slab 7a substrate. The table below maps journey → capabilities revealed → deliverable cluster(s) → scope-binding commitments touched.

| # | Journey | Capabilities Required | Slab 7a Cluster(s) | Scope-Binding Commitments Touched |
|---|---------|----------------------|--------------------|-----------------------------------|
| 1 | Primary Happy-Path | 10-gate frozen inventory, directive-composition contract, decision-card vocab registry, HTML review-pack, conversation persistence, trial-run capture | A, B, D, E | Frozen 10-gate inventory; subgraph-with-interrupt; decision-card vocab registry; pre-composition QA validator |
| 2 | Primary Edge-Case | Calibration-tripwire firing, oscillation-escape escalation, gate-verdict envelope (FAIL paths), max-3 invariant, gate-bypass detection | A, C, E | Max-3 invariant; C1 calibration tripwire; pre-composition QA validator; parity-test suite |
| 3 | Admin/Ops | Specialist roster registry (11 floor), activation contract + persistence shape, sprint-status hygiene, deferred-inventory consultation tooling, pack-hash binding | B, D, E | Frozen 10-gate inventory; parity-test suite |
| 4 | Support/Troubleshooting | Trial-run capture envelope, pack-hash binding, LangSmith trace integration, operator-turn record format, Marcus duality boundary | C, D, E | Pre-composition QA validator; parity-test suite |
| 5 | API/Integration — Codex parallel-authoring | Specialist activation port-shape pattern, activation contract, gate-verdict envelope (consumer side), Pydantic-v2 schema discipline | B, C, E | Subgraph-with-interrupt; parity-test suite |

**WHY — unique capabilities per journey.** Each journey earns its slot by revealing at least one capability no other journey touches. Journey 2 is the only one that exercises the **calibration-tripwire firing path** and the **oscillation-escape escalation** — happy-path runs never see them, and admin/support journeys observe them only after the fact. Journey 3 is the only one that touches the **specialist roster registry** as a write surface (the 11-specialist floor is enforced here, not at runtime). Journey 4 is the only one that requires **LangSmith trace integration + operator-turn record traversal** — troubleshooting is the consumer that justifies the capture envelope's depth. Journey 5 is the only one that exercises the **port-shape pattern** as an external contract, which is why Cluster B's activation contract has a public-API stance even though Slab 7a is internally-facing. If any of these four journeys were dropped, the corresponding capability would lose its named consumer and become speculative scope.

**WHY — load-bearing substrate every journey requires.** Three capabilities appear in every row: the **10-gate frozen inventory** (Cluster A), the **decision-card vocabulary registry** (Cluster A/E), and the **trial-run capture envelope** (Cluster D). This is the empirical proof that substrate-completeness scope was the right call over feature-completeness — these three deliverables are not optional in any journey, including the Codex integration journey where they show up as schema contracts the external authoring tool must conform to. Cross-cutting Cluster E (Pydantic-v2 + 34-row checklist traceability) is the silent fifth column: every capabilities-required cell above implicitly traces to the checklist's essential-function preservation row, which is how we keep the legacy↔migrated mapping honest. Drop any of these three and at least three journeys break.

---

## Domain-Specific Requirements

The domain is **online course content production / collaborative AI infrastructure**, classified HIGH complexity at Step 2. There is no external regulator (no HIPAA / PCI-DSS / GDPR / SOX), but the domain operates under an internal compliance regime — BMAD governance, Composition Spec invariants, anti-pattern catalogs, audit-trail preservation — that is, in practice, just as binding as external regulation. The trial-475 halt (paused-at-G1, plumbing-PASS / content-FAIL, 2026-04-28) is the standing reminder of what compliance failure looks like in this domain.

### Technical Constraints

**Substrate constraints.**
- **HIL tamper-evidence (FR34).** Every operator decision recorded by Slab 7a's gate-fold work persisted with a cryptographic chain: `decision_hash = SHA256(prior_envelope_digest || decision_payload || timestamp_utc || operator_id)`. Postgres checkpointer (ADR-D3) carries this as additive column on the HIL decision row; no rewrites, no in-place updates. Slab 7a deliverables touching gate-resume paths MUST round-trip the prior digest into the next envelope frame.
- **Audit-replay reproducibility.** Composition Spec §3.1 SHA256 output digests are normative. Slab 7a specialist activation contract MUST emit deterministic envelope frames given (manifest_hash, pack_hash, input_corpus_hash, gate_overrides) — no wall-clock leakage into hashed payloads, no nondeterministic dict ordering. Replay fixtures live alongside trial-2 evidence and re-execute green under FM-9 carry-over rules.
- **Append-only envelope immutability** (Option B / Path A-prime). Slab 7a deliverables MUST NOT mutate prior `ProductionEnvelope` frames. New specialist contributions append a new frame; the gate-fold reads the frame chain, never edits it. Structurally enforced by envelope schema's frozen-frame invariant.
- **Frozen-graph ceremony (Tier-2 minor).** Per `pipeline-manifest-regime.md`, Slab 7a's manifest changes (gate-fold flags, specialist activation entries) are Tier-2 minor: requires party-mode consensus BEFORE dev opens (already secured), version bump in `pipeline-manifest.yaml`, frozen-at-ship discipline post-trial. Prior pack version stays on disk for audit replay.
- **Postgres checkpointer evolution (ADR-D3).** Schema migrations are additive only — new columns nullable-with-default, no DROP, no type narrowing. In-flight runs paused at G1/G2 MUST resume cleanly against bumped schema; migration test covers a paused-trial-2 fixture replaying through the new checkpointer.
- **Multi-pass envelope Path Z (Slab 6.1).** "First contribution wins" — Slab 7a's gate-fold work MUST NOT alter dedup semantics. The 11-specialist topology preserves all eleven activation seats; gate-folds collapse flow-control edges, never specialist seats.
- **Manifest-as-graph-config (D6).** Fold-flags live as manifest fields, not as code branches. Dev agent edits `pipeline-manifest.yaml` to enable a fold; graph builder reads it. No hardcoded fold logic.

### Integration Requirements

- **Specialist activation contract.** Uniform shape all 11 specialists honor: `(envelope_in, manifest_slice, gate_overrides) → envelope_out` with §3.5 precedence-aware override read. Slab 7a delivers the contract module; specialist adapters consume it unchanged.
- **Live-API surfaces (gamma, kling, elevenlabs, wondercraft, dan-api-tbd).** All five are operator-gated AC blocks (`AC-*-B`). Dev-agent ACs verify via shipped Python deps with `pytest.skip(...)` on unreachable endpoints — `validate_migration_story_sandbox_acs.py` enforces. Per-trial cost ~5–8× a dry-run; CI MUST NOT invoke these surfaces.
- **LangSmith trace integration.** Placeholder-binding only for Slab 7a; real-binding remains a Slab 6 carry-over. Slab 7a deliverables emit trace IDs into envelope frames but do not gate on LangSmith availability.
- **Sandbox-AC inventory.** `docs/dev-guide/migration-ac-sandbox-inventory.json` is the source of truth; additions to `dev_agent_forbidden` are dev-agent authority, additions to `dev_agent_available` require party-mode consensus.

### Performance / Availability

- **Trial-2 wall-clock budget:** ~3-4h to G3, operator-attended. Not a 24/7 production SLA.
- **T1 readiness:** <60s; **T2 schema-shape pass:** <5min wall-clock.
- **Cost ceiling:** ~$3.00 per trial-2 (live-API budget envelope); CI runs dry only.

### Compliance & Governance Requirements

This domain is not subject to external regulators — but operates under internal compliance just as binding. Risk model: "we shipped a green slab that loses essential function in trial."

**CG-1. Internal-compliance gates for Slab 7a green-light** (all MUST pass before Slab 7b opens):
- **CG-1.1** Sandbox-AC inventory PR landed against `migration-ac-sandbox-inventory.json` with 5 new entries — `gamma`, `kling`, `elevenlabs`, `wondercraft`, `dan-api-tbd` — each routed to dev-agent shipped-dep verification or operator-gated AC-*-B blocks. Validator MUST return zero warnings on all Slab 7a stories.
- **CG-1.2** Composition Smoke evidence (Composition Spec §9) captured at slab-opener; missing smoke = slab does not open.
- **CG-1.3** N1-N12 substrate-inventory checklist trace attached to every slab-affecting story; checklist completion recorded in story Completion Notes.
- **CG-1.4** Four-file-lockstep enforced on every Pydantic model change: model + emitted JSON Schema + golden fixture + shape-pin tests land in same PR. Pre-commit `co-commit-invariant` hook is enforcement primitive.
- **CG-1.5** K-floor / target-range discipline: 1.2-1.4× gate-shape; 1.6× directive-composer dual-gate; 1.7× tripwire auto-escalates to party-mode.
- **CG-1.6** Gate-mode designations read from `migration-story-governance.json` (frozen 2026-04-22). No relitigation at story-authoring time; changes require party-mode consensus + JSON version bump.
- **CG-1.7** Pre-commit stack (ruff, orphan-detector, co-commit-invariant) green on every PR.

**CG-2. Audit-trail preservation:**
- **CG-2.1** Trial-475 evidence at `state/config/runs/475df528-…/` preserved for duration of Slab 7a (gitignored, local-only).
- **CG-2.2** Trial-2 evidence captured under same envelope shape; pack-hash binding in trial-run capture envelope mandatory.
- **CG-2.3** Conversation persistence written to `runs/<run_id>/conversation/<gate_id>/` sibling directory.
- **CG-2.4** LangSmith trace integration retained as audit-trail primitive (placeholder-binding acceptable for Slab 7a; real-binding deferred to Slab 7b/8 with explicit `deferred-inventory.md` entry).

**CG-3. Anti-pattern catalog enforcement** (catalog-driven, not ad-hoc):
- **CG-3.1** A1-A17 specialist anti-patterns: A12 (procedural-coupling) and A17 (substrate-designed-for-isolation-composition-assumed) are load-bearing for Slab 7a — directive-composer work MUST exercise end-to-end, not just shape-vote.
- **CG-3.2** P1-P3 cluster anti-patterns: P3 (composition-shape-vote-without-end-to-end-exercise) is the named failure mode trial-475 manifested; party-mode green-light MUST cite P3-rebuttal artifact.
- **CG-3.3** Dev-agent anti-patterns: Marcus-duality resolved by Slab 7a Cluster C #9 and MUST be referenced in Marcus-touching stories.
- **CG-3.4** Mapping-checklist 34-row Legacy↔Migrated traceability is audit floor — every row carries a verdict (migrated / deferred-with-entry / dropped-with-rationale). No row may be silently dropped.

**CG-4. Failure-mode compliance:** FM-1..FM-10 from Step 3 are green-light-checkable, not trial-discoverable.

### Risk Register

| # | Risk | Trigger | Impact | Mitigation | Address |
|---|------|---------|--------|------------|---------|
| **T1.1** | Hour-4 operator-attention breach | Trial-2 wall-clock exceeds 4h before G3 reached | Per-slide rubber-stamping; decision-card collapse; trial invalid as evidence | Time-budget telemetry per gate (<22min target); HUD shows elapsed/remaining; auto-pause at 4h with operator-confirm-to-continue | **Slab 7a (HUD + per-gate budget)** |
| **T1.2** | Specialist-roster drop below 11 | PRD step trims a specialist or merges seats "for simplicity" | Scope-floor breach; trial-2 invalidated; replay-regression baseline unusable | Hard-coded roster constant in pipeline-manifest.yaml; validator fails build if `len(specialists) != 11`; party-mode consensus required for any change | **Slab 7a (manifest validator)** |
| **T1.3** | Mapping-checklist row drop below 34 | Author "consolidates" rows or skips checklist on slab-affecting story | Substrate-trace gap; N1-N12 enforcement weakens; A12 path reopens | Checklist validator on every story touching `block_mode_trigger_paths`; row-count assertion; CLAUDE.md governance reference | **Slab 7a (checklist validator)** |
| **T1.4** | Composition Smoke skipped at slab-opener | Slab 7b or Slab 8 first-story dev rushes past smoke gate | Integration breakage caught at G6 instead of T1; cycle-time blowout | Mandatory smoke-gate hook in workflow_runner.py at slab-open; cannot be bypassed without party-mode override | **Slab 7a (workflow_runner hook)** |
| **T1.5** | Live-API cost burn 5-8× trial-475 baseline | Trial-2 runs full 11-specialist sequence with live LLM calls, no replay-cache | Operator budget shock; trial-3 funding compressed; replay-regression drifts | Replay-cache-by-default for non-decision steps; live calls only at gates where verdict matters; cost-meter in HUD | **Slab 7a (HUD cost-meter) + Slab 7b (cache plumbing)** |
| **T2.1** | Per-slide rubber-stamp collapse | Operator approves G2-G9 in <30s each without reading review-pack | Decision-quality degrades; calibration tripwire never trips; trial evidence weak | Decision-card requires one free-text reason per gate (>20 chars); HTML pack auto-opens at gate-entry | **Slab 7a (gate-card schema)** |
| **T2.2** | Decision-card vocabulary drift across gates | G2 uses "approve/reject"; G5 uses "accept/revise"; G8 uses "ship/hold" | Operator cognitive load; downstream parser breaks; verdict-rejection branching ambiguous | Frozen verdict-vocabulary enum in unified namespaced registry; lint at story-author time | **Slab 7a (vocabulary registry)** |
| **T2.3** | Subgraph degenerates to parent-graph-loop | Implementer flattens LangGraph subgraph into `for specialist in roster:` in parent | Lockstep coordination tax explodes; checkpoint granularity lost | FM-3 check at green-light; AST scan on parent graph; code-review G4 checks for flattening | **Slab 7a (FM-3 check)** |
| **T2.4** | HTML review-pack ships but operator never opens it | Pack generated to disk; gate-card doesn't link to it; operator approves blind | Review-pack effort wasted; calibration-tripwire never sees real evidence | Gate-card embeds pack URL as primary CTA; telemetry records pack-open events (FM-7 check) | **Slab 7a (gate-card UX + FM-7)** |
| **T2.5** | Greenfield Compositor opens gap downstream of attention | Compositor is novel + last-in-pipeline; operator fatigued by G6; bugs ship | Trial-2 final artifact malformed; replay-regression baseline corrupted | Compositor gets dual-gate review (not single); shape-pin tests authored before impl; T1 readiness mandatory | **Slab 7b (Compositor story spec)** |
| **T2.6** | Sandbox-AC inventory not landed before Slab 7b opens | Slab 7b stories author with operator-CLI assumptions | Validator fails at ready-for-dev; rework cycle | Sandbox-AC validator required-pass on all Slab 7a stories; inventory frozen at Slab 7a close | **Slab 7a (validator + inventory freeze)** |
| **T3.1** | Pack-hash drift on replay-regression | Tier-1 prose edit bumps pack hash silently | Replay diffs noisy; signal lost in cosmetic churn | Pack-hash separated into structural-hash vs prose-hash; only structural triggers regression-fail | **Carry-over (Slab 6 → Slab 8)** |
| **T3.2** | LangSmith trace-id real-binding deferred | Trial-2 ships with synthetic trace-ids | Cross-restart resume + multi-checkpoint walk untestable in production | Real-binding scoped into Slab 7b story; trial-3 readiness gate | **Slab 7b** |
| **T3.3** | Calibration-tripwire shipped but never exercised | Tripwire fires zero times across trial-2 | Cannot distinguish "operator well-calibrated" from "tripwire broken" | Synthetic-disagreement injection in trial-2 dry-run; verify tripwire fires at least once pre-trial | **Slab 7a (tripwire smoke-test)** |
| **T3.4** | Deferred-inventory drift | Slab 7a names follow-ons in story specs only, not in inventory | Follow-ons drop off radar at retrospective | CLAUDE.md §Deferred Inventory Governance enforced at story-close; retrospective consults inventory | **Slab 7a (governance touch)** |

**Tier distribution:** 5 BLOCKING / 6 DEGRADING / 4 MONITORING = 15 risks. Every Tier-1 has a Slab 7a deliverable owner; Tier-3 carry-overs explicitly named with downstream slab.

### Domain Patterns

- **P-D1. Operator-as-Collaborator.** The operator is a creative co-author, not a gate approver. Decisions surface explicitly with rationale and alternatives — never hidden behind silent defaults. *Operationalized by:* Inter-Gate Conversational Orchestration runtime; FM-1 (gate-count drift check enforces operator-cost-floor commitment).
- **P-D2. Specialist-as-Author.** Each of the 11 specialists holds authorial voice and judgment — proposes, justifies, revises — they do not deterministically transform inputs. *Operationalized by:* mapping checklist 34-row floor (preserves v4.2 authorial-voice idioms across all 11 specialists × 34 rows); Composition Spec §3.1 append-only trace.
- **P-D3. Multi-Hour Trial as First-Class Unit.** A trial is a 4-8 hour collaborative session with persistent state, not a request/response transaction. Hour-4 operator fatigue is a designed-for constraint. *Operationalized by:* LangGraph checkpointer durability spec; SM-4 (engagement-decay floor) and FM-8 (engagement-decay breach check).
- **P-D4. Append-Only Authorial Trace.** Every specialist contribution is an authorial commit — never overwritten, always attributed. The trace is audit substrate AND calibration evidence. *Operationalized by:* Composition Spec §3.1 binding; FM-3 (substrate-inheritance check verifies trace immutability across gate transitions).
- **P-D5. Per-Slide Array as Review Surface.** Slides are the unit of operator attention. Cross-slide pattern memory (a recurring tone tic, a slide-7 layout regression) is a first-class signal, not noise. *Operationalized by:* US-6 per-slide-arrays compound metric; subgraph-with-`interrupt()` scope-binding commitment; HTML review-pack.
- **P-D6. Revise-Loop as Dialogue.** "Specialist proposes → operator refines → specialist re-proposes" — collaborative iteration, not retry-on-failure. Oscillation-escape exists for stuck dialogue. *Operationalized by:* max-3 oscillation guard as state-machine invariant; `oscillation_escape_required` in decision-card vocabulary registry.
- **P-D7. Calibration Drift as Natural.** Specialists drift over multi-hour sessions; calibration-tripwire is a gentle re-grounding handshake, not a violation flag. *Operationalized by:* C1 calibration tripwire scope-binding commitment; tripwire smoke-test (T3.3 mitigation).

### Domain Anti-Patterns

- **AP-D1. Specialists-as-Deterministic-Transformers.** Treating Texas/Irene/Gary as pure functions of input. Erases authorial voice; produces flat artifacts. *Prevented by:* mapping checklist 34-row floor enforces voice-preservation per specialist × stage; A3 specialist-prompt-fidelity catalog entry.
- **AP-D2. Operator-as-Approver-of-Record.** Reducing operator to rubber-stamp role. Loses creative partnership; produces compliant-but-soulless content. *Prevented by:* T2.1 mitigation (free-text reason >20 chars); Inter-Gate Conversational runtime explicit-decision-surfacing.
- **AP-D3. Hiding Gates Behind Defaults (False-Confidence-in-Fold).** Auto-advancing gates with implicit "looked fine" logic — Quinn-R's 06B literal-visual concern from Round 1. *Prevented by:* every-gate-surfaces-decision binding; FM-4 (decision-card vocabulary fragmentation check); audit log must show explicit operator touch on every gate transition.
- **AP-D4. Optimizing Per-Trial Cost over Per-Trial Trust.** Cheaper specialists, fewer revise-loops, smaller models — defensible individually, corrosive collectively. False economy: trust deficit costs more than tokens saved. *Prevented by:* Trust-floor invariant before cost-ceiling; A14 trust-floor catalog entry.
- **AP-D5. Documentation Drift (v4.2 ↔ Migrated Runtime).** The 1527-line orphan risk Paige flagged: v4.2 prose says X, migrated graph does Y, neither knows. *Prevented by:* Mapping-checklist as living artifact (re-validated each Slab 7+ trial); Doc-7-D re-authored 400-line distillation closes the gap; A8 prose-runtime-parity catalog entry.
- **AP-D6. Hand-Rolled Per-Gate Invariants.** Each gate re-implements its own checks. Drift, gaps, FM-2. *Prevented by:* FM-2 substrate-inheritance enforcement; max-3 oscillation guard scope-binding commitment (state-machine invariant in shared substrate, gate-authors inherit not implement); A11 no-bespoke-invariants catalog entry.
- **AP-D7. Conflating Calibration-Tripwire with Failure.** Treating tripwire fire as "the specialist broke" rather than "we drifted, let's re-ground." Erodes specialist trust; encourages specialist replacement over recalibration. *Prevented by:* tripwire-as-handshake conversational shape; P3 tripwire-as-signal documentation; A17 drift-is-natural catalog entry.

*(Note: AP-D2 and AP-D3 are the same failure mode viewed from operator-side and gate-side respectively; both retained because the deliverables that prevent each differ.)*

---

### Standing Guardrail (operator-ratified 2026-04-28)

**Mapping Checklist** (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`, 34 rows) and **Composition Specification** (`docs/dev-guide/composition-specification.md`) are now **standing guardrails** for all remaining PRD steps and downstream Slab 7a/7b/Doc-7-D story authoring. Every party-mode round, every story spec, every dev-cycle close MUST verify:

1. **Mapping Checklist** — no row silently dropped; essential-function preservation under different mechanism is allowed (e.g., Quinn-R fold §07D into §07F) but must be explicitly cited; the 34-row floor is hard.
2. **Composition Spec invariants** — §3.1 SHA256 output digests + append-only envelope; §3.5 gate precedence; §3.6 manifest-declared dependencies; §6 chain-test-per-PR; §9 Composition Smoke gate at slab-opener; §10 Decision Log entry for any composition-substrate change; §11 migration triggers tracked.

Auto-reject + flag to operator if any party-mode consensus would violate either guardrail.

---

## Innovation & Novel Patterns

### Detected Innovation Areas

Cut to bone: most "AI orchestration" work today is plumbing dressed as innovation. Slab 7a is the inverse — **plumbing promoted to surface**.

**Three orthodoxies challenged:**

- **LangGraph-app orthodoxy:** checkpointer + `interrupt()` + subgraphs are *infrastructure*; apps render their own UI on top. Slab 7a inverts this — **checkpointer state IS the operator-facing surface**; CLI shims and HTML review-packs are renderers, not authorities. The runtime is not "instrumented for review"; the runtime IS the review.
- **Multi-agent collab orthodoxy:** the operator is an *approver* downstream of AI output. Slab 7a treats the operator as **authorial co-equal #12** in an 11-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera), with append-only commits per Composition Spec §3.1. No approver/approved hierarchy. SHA256-digested authorial commits, all the way down.
- **Legacy v4.2 orthodoxy:** prose-encoded process discipline ("operator must review each slide"). Slab 7a's answer: **structurally prevented, not policy-prevented**. The per-slide subgraph-with-`interrupt()` fan-out makes rubber-stamping topologically impossible — you cannot collapse a loop that doesn't exist.

**Novel combinations** (not just disciplined LangGraph idiom application):

1. **Subgraph fan-out + `interrupt()` + HTML review-pack as a single pattern for per-slide-array operator review under hour-4 fatigue.** Each component is known. The assembly — fatigue-as-design-constraint driving topology — is uncommon.
2. **C1 calibration-tripwire as closed-loop substrate behavior.** Override-rate over rolling-N drives gate-batch-approve auto-lock/unlock. The substrate calibrates operator trust *to itself*. Not a dashboard. A feedback controller embedded in the gate-runner.
3. **Manifest-as-graph-config + fold-flags + subgraph absorption (D6).** Topology is data. Combined with the mapping-checklist's 34-row essential-function floor, this is **traceable graph topology** — every legacy row maps to a migrated mechanism or auto-rejects.
4. **Decision-card vocabulary as typed Pydantic-v2 enum substrate**, not style guide. Closed-set red-rejection.

**Genuine novelty (narrow claims):**

- **Operator as authorial co-equal in append-only envelope** — not approver, not reviewer, *committer*. SHA256 digests treat operator commits identically to specialist commits.
- **Calibration-tripwire-driving-substrate-behavior** — self-modifying gate policy from operator-override telemetry. Not a metric. A control law.
- **Codex-as-parallel-authoring-peer for Slab 7b** while humans author Slab 7a — AI-orchestrating-AI in service of *human* creative authorship, not autonomous output.

**Honest innovation budget:** roughly **20–40% genuine recombination, 60–80% disciplined substrate completion of known LangGraph idioms.** The PRD claims "disciplined application with three load-bearing novel recombinations," not "breakthrough." The substrate is intentionally boring. The novelty lives in the assembly, the invariants, and the operator-control envelope.

### Market Context & Competitive Landscape

Slab 7a sits in well-trodden territory at the component level and on relatively fresh ground at the assembly level. An honest accounting matters here because overclaiming novelty creates downstream review risk and undersells the actual contribution.

**Adjacent prior art (boring-technology foundation):**
- **`interrupt()` + Postgres checkpointer for HIL** — textbook LangGraph for HIL workflows; documented, idiomatic, not novel.
- **Subgraph composition (Composition Spec Option C)** — first-class LangGraph idiom for fan-out / parallel / hierarchical. Slab 7a's Option B / Path A-prime is the *simpler* choice; Option C is staged behind §11 migration triggers (currently 0 of 5 active), not invented.
- **Pydantic-v2 schema discipline** — closed enums, `validate_assignment=True`, tz-aware datetimes, additive evolution. Not novel; just enforced.
- **Append-only event-sourced state** — decades-old CS pattern. Mildly novel as applied to LangGraph app state, but not Slab-7a-specific.
- **HTML-as-review-surface for HIL approvals** — well-known UX pattern.

**Genuine novelty (assembly, not components):**
1. **Multi-hour authorial-collaboration trials with an 11-specialist roster under an operator-co-author control envelope at every gate.** Most LangGraph deployments are short-running request/response or autonomous-agent loops. Multi-hour, gate-paced, operator-as-co-author with eleven named specialist seats is uncommon in the public landscape.
2. **Mapping Checklist as a standing substrate invariant** with a 34-row floor and row-count assertion enforced as a PRD/story-spec gate. Most migrations discard their legacy trace; preserving every legacy mechanism as essential-function under a migrated mechanism — and validating that mapping continuously — is unusual discipline.
3. **Calibration tripwire as closed-loop substrate behavior** — auto-locking/unlocking batch-approve based on operator-override-rate over rolling N-run window. Rare in production HIL systems, which typically treat calibration as out-of-band.
4. **Composition Spec as a living architectural artifact** with §10 Decision Log + §11 migration triggers at decision granularity. Uncommon in LangGraph application codebases.

**Competitive landscape:**
- **LangChain Agent Protocol** — adjacent but autonomous-agent-oriented; Slab 7a is operator-co-author-oriented.
- **CrewAI / AutoGen / multi-agent frameworks** — adjacent in roster shape; differ in operator-centric framing and gate cadence.
- **Cursor / Cline / Claude Code** — adjacent in operator-AI co-authoring, but oriented to dev-time code work, not multi-hour content-production trials with eleven specialist seats.
- **Lab-internal multi-agent systems** (Anthropic, OpenAI, etc.) — likely exist; undocumented publicly. Assume Slab 7a is novel against the *public* landscape only.

### Validation Approach

Innovation must be falsifiable in trial-2; otherwise this section is innovation theater. Three layers, each with primitives + thresholds + fallbacks.

**Layer 1 — Pre-trial bench validation** (before trial-2 opens):

- **Synthetic-disagreement injection** (per T3.3): fixture-driven specialist-disagreement scenarios fired against C1-tripwire offline. Threshold: 100% of injection scenarios classified correctly. Fallback if red: rollback C1 to advisory-only mode; defer closed-loop substrate to Slab 8.
- **Composition-smoke gate** (CG-1.2): manifest-as-graph-config compiles + smoke-runs end-to-end on stub corpus. Fallback: revert manifest layer to Slab 6 hand-wired graph wiring.
- **FM-1..FM-10 green-light**: each failure-mode has a corresponding pre-trial probe.
- **Replay-fixture suite green**: deterministic replay across canonical lesson fixtures. Fallback: freeze offending node (specialist-floor permitting).
- **Parity-test suite green**: legacy↔migrated parity per mapping-checklist 34 rows. Fallback: row-level rollback; never drops below 34 rows.

**Layer 2 — Trial-2 load-bearing validation** (the single experiment that proves the substrate):

| Innovation | Validation primitive | Threshold | Fallback if red |
|---|---|---|---|
| Checkpointer-native operator-control | Resume-from-checkpoint event in trial log | ≥1 successful resume across trial-2 | Rollback to Slab-6 in-memory pause |
| Per-slide subgraph + `interrupt()` | Per-slide decision-card cardinality | ≥50% slides emit engagement signal | Coarsen to per-section interrupt; defer per-slide to Slab 8 |
| Max-3 oscillation guard | Oscillation-counter state | 0 violations over trial-2 | Tighten to max-2 hard-fail; Composition Spec §11 trigger |
| C1 calibration-tripwire | Fire/quiet ratio in trial log | ≥1 fire AND ≥1 quiet | Demote to advisory; Slab 8 closed-loop |
| Manifest-as-graph-config + fold-flags | Manifest-driven boot succeeds | G0→G3 boot with zero hand-edits | Hybrid: manifest for nodes, hand-wired edges |
| Mapping-checklist living artifact | Per-row trial-2 verdict captured | 34/34 rows verdict-recorded | Freeze stale rows; never drop below 34 |
| Append-only ProductionEnvelope | Envelope diff = pure-append | 0 retroactive mutations | Composition Spec §11 migration trigger |
| Decision-card vocabulary registry | Vocabulary-violation count | 0 unregistered card types | Auto-register + flag for retro review |

Plus gestalt thresholds: G3 reached cleanly with 11 specialists active; engagement-decay ratio ≥0.30 first-vs-last quartile; cost ≤$3.00; gate-bypass events = 0.

**Layer 3 — Post-trial corpus accretion** (single-trial green is necessary, not sufficient):

- **C1 rolling-window performance**: precision/recall over rolling N=5 trial window. Threshold: precision ≥0.7 by trial-5. Fallback if not converging: redesign tripwire-feature set in Slab 8.
- **Per-specialist drift detection**: drift-score per specialist per trial. Threshold: no specialist drifts >2σ across 3 consecutive trials without retro intervention. Fallback: retro-driven recalibration; never specialist-removal.
- **Mapping-checklist re-validation**: 34 rows re-verdicted each trial. Threshold: drift-row count <5/trial. Fallback: row-author re-review; checklist stays at 34.

**No fallback path drops the specialist floor or the checklist floor.** If a candidate innovation can only be validated by dropping either floor, it is not a Slab-7a innovation — it is a Slab-8 research item, and the PRD says so out loud.

### Risk Mitigation (Innovation-Specific)

These risks exist *because* Slab 7a is novel — distinct from Step 5's general Risk Register.

| # | Tier | Risk | Early-warning signal | Fallback path | Recovery |
|---|---|---|---|---|---|
| **IR-1** | BLOCKING | Assembly pattern collapses under 11-specialist load (subgraph + `interrupt()` deadlocks, double-fires, or produces incoherent state in trial-2) | First trial-2 attempt shows >2 specialist-pair handoff failures, OR a single gate's `interrupt()` resume produces divergent state vs cold-replay | Revert failing edge to Slab 6 sequential-with-manual-resume; isolate broken handoff to single inter-gate pair; do not propagate pattern further | Party-mode root-cause within one cycle; if pattern salvageable, ship v1.1 with narrowed envelope; if not, escalate to Composition Spec §11 Trigger review |
| **IR-2** | BLOCKING | Operator-trust deficit on calibration tripwire — operator reverts to per-gate manual approval; closed loop defeated; headline value evaporates | Trial-2 telemetry shows operator overriding tripwire-green >30% of time, OR override-on-red <70% (tripwire ignored in both directions) | Ship Slab 7a with tripwire in **advisory-only** mode for one additional trial; gate batch-approve behind explicit operator opt-in per session | Tune thresholds from trial-2 evidence before promoting tripwire to authoritative |
| **IR-3** | DEGRADING | C1 false-positive rate locks out correct batch-approve (tripwire fires on benign variance; friction inflates, trust erodes — feeds IR-2) | Trial-2 shows tripwire-fired-but-operator-overrode-to-approve >20% of decisions | Widen tripwire thresholds by one stddev; re-run trial slice | Capture false-positive corpus as calibration fixture; bake into C1 regression suite |
| **IR-4** | DEGRADING | Composition Spec §11 Trigger 1 fires early — per-slide subgraph fan-out load arrives sooner than tracked; Option B no longer fits | Trial-2 shows >N concurrent subgraph instances within a single gate window (N to be set in §11 monitoring spec) | Freeze fan-out at current cardinality; queue overflow rather than parallelize | Open Slab 7b scoped specifically to Option-C migration; do not attempt in-place upgrade |
| **IR-5** | DEGRADING | Substrate-novelty vs dev-agent debugging fluency mismatch — Claude/Codex lacks mental model for subgraph/`interrupt()` bugs; bug-hunt cycles inflate K-floor 3-5× | First two Slab-7a stories trend K >3.0× target | Pair-debug with operator on first failure; capture pattern in `docs/dev-guide/` | Add subgraph-debugging anti-pattern entry to `dev-agent-anti-patterns.md` before story 3 |
| **IR-6** | MONITORING | Mapping checklist erodes under sprint pressure — A8 prose-runtime-parity drift accumulates as checklist updates lag code | Any story closes with checklist diff untouched while code touches a mapped row | Block story-done on checklist sync (validator hook) | Retro-sync at Epic close; treat as governance debt, not technical debt |
| **IR-7** | MONITORING | Innovation-elegance bias in PRD review — reviewers green-light the pattern because it reads well, not because trial-2 evidence supports it | Validation Approach lacks a falsifiable trial-2 criterion | Validation Approach must name a kill-criterion before PRD ships | N/A — pre-flight check, not runtime risk |

The fallback architecture is deliberately layered: most innovations rollback to Slab-6 substrate; closed-loop and append-only pieces escalate to Composition Spec §11 migration; truly load-bearing failures defer to Slab 8. **No fallback path drops the specialist floor or the checklist floor.**

---

## Project-Type Specific Requirements — Internal Multi-Agent Runtime Extension (LangGraph Orchestration Layer)

### Project-Type Overview

Slab 7a is a **runtime-substrate consolidation** — not a feature build. The project type is custom (not in the standard CSV: api_backend / mobile_app / saas_b2b / developer_tool); the closest analog is "internal LangGraph application extending an existing multi-agent runtime." The deep-dive organizes around four concrete surfaces: technical architecture, implementation modules, test strategy, and operator-facing contracts.

### Technical Architecture Considerations

**1. LangGraph runtime contracts (extended, not invented).** Slab 7a inherits the **append-only `ProductionEnvelope` substrate** (Composition Spec §3.1) and treats it as load-bearing: no specialist mutates a peer's contribution; multi-pass writes append under Path Z ("first contribution wins" — §3.4). The **`ProductionDispatchAdapter`** (Option B / Path A-prime) is the single translation layer between Marcus's operator-facing dispatch protocol and the LangGraph state object — the *only* sanctioned coupling point, which resolves the Marcus-duality anti-pattern at the architecture seam rather than at the persona seam.

Per-specialist `gate_decision` precedence (§3.5) and manifest-declared dependencies with permanent runner fallback (§3.6) are unchanged contracts; Slab 7a's contribution is to make `pipeline-manifest.yaml` the **graph-config source of truth** (ADR-D6) so the LangGraph compile step reads node ordering, fold targets, and dependency edges from the manifest rather than from code-resident wiring. Postgres checkpointer schema continues additive-only evolution (ADR-D3) — no destructive migration in 7a.

**2. Subgraph composition (Slab 7a's load-bearing pattern).** Each specialist node compiles to its own LangGraph subgraph with an isolated checkpoint boundary. Per-slide arrays at G2B, G2F-merged, and G3B use the subgraph-with-`interrupt()` fan-out pattern: the parent graph emits N child invocations (one per slide), each child carries an independent checkpoint thread, and the parent joins on completion. A single slide's `interrupt()` does not stall the cohort.

Subgraph absorption is governed by `fold_target` metadata in `pipeline-manifest.yaml`: all 14 declared `gate_codes` remain in the manifest (preserving auditability and the 34-row mapping-checklist floor), but the runner honors `fold_target` to absorb folded gates into their host gate's subgraph at execute time. This is the mechanism that holds "10 user-visible gates / 14 declared codes" without cheating either side of the contract.

**3. State-machine invariants (new in 7a's shared gate-runner substrate):**
- **Max-3 oscillation guard** — terminates revise-loops at depth 3 and routes to operator escalation.
- **C1 calibration tripwire** — closed-loop check that fires when calibration drift exceeds the §3 substrate threshold.
- **Gate-bypass detection hook** — refuses transitions that skip a declared gate_code (even folded ones; the fold-flag is checked, not the gate's existence).
- **Marcus duality boundary enforcement** — runtime assertion that Marcus-as-orchestrator state never mixes with Marcus-as-operator-handoff state across the dispatch adapter.

**4. Gate topology — frozen 10-gate inventory.**
G0 Preflight + Ingestion-fold (Texas + Vera G0) → G1 Plan Pass-1 + Plan-lock-fold (Irene + Tracy + Vera G1) → G2 Narration Pass-2 + Storyboard-A (Irene + Quinn-R G2C) → **G2B** per-slide variant (Gary + Quinn-R G2C, fan-out) → **G2F-merged** per-slide motion (Kira + Quinn-R G2F, fan-out) → G3 Sequencing + Storyboard-B HIL (Vera G4 + operator) → G4 Narration Synthesis (Enrique) → G5 Pre-Composition QA (Quinn-R) → G6 Compositor Assembly (deterministic, no LLM) → G7 Final Handoff (Marcus). **Wanda + Dan** thread across G1-G2 via append-only envelope contributions (Slab 7b activation) — they hold no own-gate seat but are first-class roster members, preserving the **11-specialist floor**.

### Implementation Surfaces

**New modules (orchestration spine):**

| Path | LOC | Purpose |
|---|---|---|
| `app/marcus/orchestrator/directive_composer.py` | ~150-200 | Closes trial-475 Gap 2; composes specialist directives from gate-verdict envelope + corpus state |
| `app/marcus/orchestrator/gate_runner.py` | ~80-120 | Shared substrate: max-3 oscillation guard, C1 calibration tripwire, gate-bypass detection hook |
| `app/marcus/orchestrator/pre_gate_marcus.py` | ~60-80 | Pre-gate Marcus LLM node; template-with-slots pre-fill; emits structured operator-turn record |
| `app/marcus/orchestrator/per_slide_subgraph.py` | ~150 | `interrupt()`-per-slide subgraph for G2B / G2F-merged / G3B (FM-3 guarded) |
| `app/marcus/orchestrator/conversation_persistence.py` | ~50 | Writer for `runs/<run_id>/conversation/<gate_id>/` (operator turns + verdict envelope) |
| `app/marcus/orchestrator/html_review_pack.py` | ~80-100 | HTML review-pack skeleton (deterministic; no LLM) |
| `app/marcus/orchestrator/specialist_summary_writer.py` | ~40-60 | "What I just did" summary writer (specialist→Marcus handoff record) |
| `app/marcus/cli/gate_shims/g{1,2c,3,4}_shim.py` | ~30 each | Single-decision shims for terminal gates |

**Subtotal:** ~730-880 LOC orchestration spine.

**Manifest + Compiler extensions:**
- `app/manifest/compiler.py` — extend to read `fold_target` / `fold_with` from manifest metadata; **remove** hardcoded `PRODUCTION_GATE_IDS` frozenset; derive at compile-time.
- `state/config/pipeline-manifest.yaml` — additive schema fields: `fold_with`, `fold_target` per node. Backward-compatible.
- `state/config/gate_fold_manifest.yaml` — **NEW** audit artifact; enumerates effective-gates vs declared-gates post-fold; consumed by L1 check.

**Schemas / registries (Pydantic-v2 four-file lockstep):**
- `app/models/decision_cards.py` — extend with namespaced vocabulary registry enum (`gates.*` / `specialists.*` / `shared.*`).
- `app/models/state/operator_verdict.py` — extend for revise-loop semantics + `revise_count: conint(le=3)` field.
- `app/models/state/gate_verdict_envelope.py` — **NEW** typed envelope (verdict + directives + audit fields).
- `docs/conversational-gates/_registry/vocabulary.yaml` — unified vocabulary registry.
- JSON Schema regen + golden fixtures + shape-pin tests — **lockstep on every Pydantic change** per `pydantic-v2-schema-checklist.md`.

**Codex parallel-authoring boundary:**
- **Claude authors:** orchestration-spine stories (directive_composer, gate_runner, pre_gate_marcus, manifest fold-flags, Compositor greenfield `--kind=deterministic`).
- **Codex authors:** Slab 7b port-shape stories (Tracy, Gary, Kira, Enrique, Wanda — Slab 2a.2 Irene template); sandbox-AC inventory PR (gamma, kling, elevenlabs, wondercraft, dan-api-tbd); `bmad-code-review` on every Slab 7a + 7b close.

### Test Strategy

Risk-budgeted test architecture — depth scales with blast radius. Aggregate envelope: ~75-100 canary tests, T1+T2 dominant, T3/T4 minimal-in-7a.

**T1 — Orchestration unit (35-45 tests, <60s aggregate, stop-the-line)**
- Gate-graph topology (~8): G0→G1→G2→G3 edge presence, gate-id closure, no-orphan-node assertion, Compositor adjacency invariant.
- Decision-card vocabulary closure (~6): closed-enum red-rejection (triple-layer per Pydantic checklist), unknown-verb-rejected, schema-shape pin.
- Subgraph isolation (~8): each specialist subgraph imported in isolation; no cross-specialist symbol leakage; AST-scan asserts FM-2/FM-3/FM-4 anti-patterns absent.
- Calibration-tripwire activation paths (~6): trip thresholds → escalation, no-trip → continue, double-trip → stop-the-line.
- Replay-from-fixture loader determinism (~7): sorted inputs, stable content-hash, deterministic seed propagation, fixture-version-pin matches manifest.

**T2 — Replay-from-fixture (25-35 tests, <5min aggregate, stop-the-line)**
- End-to-end gate traversal G0→Gn from LangSmith trace fixtures (~10).
- Pack-hash determinism (~4): same fixture in → same pack-hash out across 5 runs.
- Cache-hit-rate harness ≥85% (~11): parametric across 10 specialist configs + 1 Compositor pipeline-determinism harness.
- Cross-gate handoff invariants (~6): G1-output schema = G2-input schema; decision-card propagation; calibration-state hand-off integrity.

**T3 — Specialist-bound integration (0-3 in 7a):** Smoke shims only, validating bind-point contract surface. Real T3 depth lives in Slab 7b.

**T4 — End-to-end live (≤3, hard cap):** Cost ceiling ~$0.60 aggregate per full-run. Record-once-replay-forever; subsequent CI runs hit fixtures, never live APIs.

**Parametric cache-hit harness architecture:** Single module `tests/canary/cache_hit_rate_harness.py`. Per-specialist YAML configs at `tests/canary/configs/{irene,gary,kira,enrique,wanda,texas,tracy,dan,quinn_r,vera}_cache_targets.yaml` (10 configs, one per specialist in the 11-floor roster minus Compositor) — plus separate `compositor_pipeline_determinism_targets.yaml` because Compositor tests pipeline-determinism rather than cache-hit-rate. Each config declares: `target_hit_rate` (default 0.85), `fixture_corpus_path`, `essential_function_probe_set`, `allowed_miss_reasons` (closed enum: `cold-start`, `fixture-rotation`, `pack-version-bump`).

**Parity-test suite scaffolding:** `tests/parity/` mirrors the mapping-checklist 34-row structure — exactly 34 tests, one per legacy operator-control lever. `tests/parity/README.md` carries the traceability matrix (test-id → checklist-row → PRD-spec-section). CI-gated: any parity-test red = trial-2 readiness regression, blocks merge.

**Sandbox-AC inventory contract:** `python scripts/utilities/validate_migration_story_sandbox_acs.py` passes on every Slab 7a story. **5 inventory entries required** (gamma, kling, elevenlabs, wondercraft, dan-api-tbd). Inventory PR is hard precondition.

**K-floor governance:** Gate-shape stories 1.2-1.4× (single-gate); directive-composer 1.6× (dual-gate). Aggregate Slab 7a: ~21 K-units. Over-spend tripwire: any single story >1.7× K closes the dev round, escalates to party-mode. Flakiness budget: zero quarantine-skips on T1/T2; flake = critical tech debt.

### Operator-Facing Surface Contracts

This subsection registers the operator-promise side of the substrate. Each contract names the surface, the operator's expected friction, and the substrate's binding obligation.

**1. CLI entry surfaces.** Two top-level commands plus four single-decision shims. `bmad-trial start --input <corpus-path>` is the only entry that resolves Gap 2: it invokes `directive_composer.py` at pre-gate-marcus, pre-fills the Texas directive from corpus shape, and emits an operator-confirm prompt before Texas dispatch. No silent dispatch — the contract forbids fetch without confirmation. `bmad-trial resume --verdict-file <path>` is checkpointer-native and resumes from any gate. Each terminal-gate shim ships a `--help` that conforms to OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section structure; CI lint asserts the structure.

**2. HTML review-pack contract.** For per-slide-array gates (G2B, G2F-merged, G3B), the substrate writes `runs/<run_id>/gates/<gate>-review-pack.html` at gate entry and triggers a browser-open event. FM-7 verifies the open occurred (not merely that the file exists). Each slide row carries a checkbox plus a free-text delta-directive field; the decision-card header is drawn verbatim from the vocabulary registry — no inline string literals permitted. On revise, the pack regenerates with the new variant highlighted against the prior; the prior pack is retained for audit.

**3. Conversation persistence contract.** Every operator turn writes one structured-record file under `runs/<run_id>/conversation/<gate_id>/`, sibling to gate outputs (not nested). Each record carries a tamper-evident digest: `SHA256(prior_envelope_digest || decision_payload || timestamp_utc || operator_id)`. The chain is verifiable end-to-end; a broken link is a hard audit failure, not a warning.

**4. Specialist-summary contract.** Each specialist, on completion, emits `runs/<run_id>/specialist-summaries/<name>-<timestamp>.md` (15-25 lines, "received X / decided Y because Z / emitted at P"). The next gate-handler loads adjacent summaries inline so the operator never has to chase artifact paths to reconstruct context. Length is enforced at write time.

**5. Vocabulary registry contract.** `docs/conversational-gates/_registry/vocabulary.yaml` is the single source of truth for decision-card tokens, with three closed namespaces (`gates`, `specialists`, `shared`). A Pydantic-v2 enum loads it at import; a CI test scans gate-handlers and fails if any unregistered token reaches an emit site. Triple-layer red-rejection per the schema checklist.

**6. Parity-table contract.** `docs/operator/legacy-vs-langgraph-control-parity.md` lists every legacy v4.2 operator-control lever (left column) against its LangGraph equivalent path/command (right). `tests/parity/` makes the table executable — FM-6 fails the build if a row's right-column command does not produce the asserted control behavior. The table is the audit artifact; the suite is the proof.

**7. Revise-loop contract.** Per-slide oscillation cap is hard at 3; the 4th revise is refused by the substrate, not by convention. On refusal, an `oscillation_escape_required` decision-card surfaces with three options (accept-as-is / reject-and-skip / abort-run); accept-as-is requires a rationale string, logged to conversation persistence. C1 calibration tripwire watches operator-override rate; on threshold breach, batch-approve is re-locked at the affected gate for the next three trials.

**8. Calibration-tripwire transparency contract.** `_artifacts/trial-2/calibration_tripwire_log.jsonl` logs both fire and quiet events (FM-5 inverse check — silence is not assumed to mean healthy). Operator can `cat` the log at any time; a synthetic trip is exercised during Slab 7a dev (T3.3 mitigation).

**9. Engagement-decay transparency contract.** Post-trial, `_artifacts/trial-2/engagement_decay_report.md` is auto-generated with first-quartile rate, last-quartile rate, ratio, and pass/fail against SM-4 threshold (ratio ≥ 0.30). Breach fires C1.

**Friction posture:** every surface above is built so the operator's next move is one decision, one path, one command — never "go reconstruct what just happened from a tree of artifacts."

### Implementation Considerations

- **Sequenced execution.** Slab 7a stories sequence: directive_composer (closes Gap 2; first) → manifest fold-flags + compiler extension (foundation) → pre-gate-marcus shared node → per-slide subgraph + HTML review-pack skeleton → conversation persistence + specialist-summary writer → vocabulary registry + parity-table → A2 single-decision shims → integration story.
- **Codex deployment.** Codex parallel-authors port-shape Slab 7b stories + sandbox-AC inventory PR + bmad-code-review passes; Claude authors orchestration-spine + Compositor greenfield. Mutual-handoff pattern: bmad-code-review on every story close.
- **Frozen-graph ceremony (Tier-2 minor pack-version bump).** Manifest changes (gate-fold flags, specialist activation entries) require party-mode consensus BEFORE dev opens (already secured); version bump in `pipeline-manifest.yaml`; frozen-at-ship discipline post-trial.
- **Substrate-novelty learning curve.** Per IR-5: first two Slab 7a stories may trend K >3.0× target as Claude/Codex build mental model of subgraph-with-`interrupt()` patterns; pair-debug with operator on first failure; capture pattern in `docs/dev-guide/` before story 3.

---

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**Classification: Platform MVP (primary) + Problem-Solving MVP (secondary).**

Slab 7a is a **Platform MVP**. The substrate it ships — eleven specialists wired to LangGraph, the Mapping Checklist as runtime contract, Composition Spec as ordering authority, Doc-7-D as the learning-capture seam — is the *enabling layer* that downstream Slab 7b activation and every subsequent trial run on top of. That is the textbook definition: build the platform once, then iterate trials cheaply against it.

It is **secondarily a Problem-Solving MVP** because it closes two specific, evidenced failures from trial-475: silent gate-bypass (G1→G3 traversal with no surfaced state) and content-FAIL ambiguity (specialist outputs landing without composition-spec validation). Those are not hypothetical pains; they are paused-at-G1 trial evidence on disk.

It is explicitly **not** an experience MVP — legacy v4.2 *is* the experience reference — and **not** a revenue MVP — single-operator internal tool, no monetization surface.

**MVP threshold (sharp, single):** trial-2 reaches G3 cleanly with eleven specialists active, zero fix-on-the-fly patches, zero silent gate-bypass. Cited from Step 3 BS-1; restated here as the scoping-tier success line.

**Philosophy stance — why substrate-completeness, not thin-slice.** Lean-MVP orthodoxy says ship a vertical slice and grow. Slab 7a deliberately does the opposite: ship the full 13-deliverable substrate, validate once via trial-2, harvest via Doc-7-D. **Why?** Three reasons that stack: (1) trial-475 evidence shows partial substrate produces silent-bypass — a thin slice would re-encounter the same failure mode; (2) operator-locked non-negotiable on substrate-completeness (Round-2 minimum-viable cut was rejected); (3) LangGraph's platform leverage means specialist-by-specialist activation is *cheaper* on a complete substrate than incremental substrate growth on a partial one. Substrate-completeness here is not gold-plating — it is the *minimum* shape that makes trial-2 a valid signal.

**Resources.** Single operator (Juan). Two dev-agents (Claude + Codex) in mutual-handoff per Executive Summary §Codex Deployment Plan. ~21 K-units across ~8 stories. Wall-clock ≤8 weeks (Step 3 BS-2). Spend ≤$3.60 total Slab-7a-attributable (≤$0.60 dev-cycle + ≤$3.00 trial-2).

**Boundary as decision.** **IN:** the 13 deliverables across 5 clusters; the 7 scope-binding commitments; the eleven-specialist roster; the 34-row Mapping Checklist floor; Composition Spec invariants; Doc-7-D harvest. **OUT:** Slab 7b specialist activation; trial-3+; any twelfth specialist; any checklist row reduction; any experience-layer polish on Marcus surfaces. The trial-2 threshold is the gate — pass it, Slab 7a closes; fail it, Doc-7-D harvest informs the next cut, but the substrate stays.

### MVP Feature Set (Phase 1)

**Core User Journeys Supported.** Phase 1 covers all five canonical journeys end-to-end: **Journey 1** (Primary Happy-Path, G3 clean), **Journey 2** (Edge-case revise-loop oscillation), **Journey 3** (Admin/Ops one-week-gap re-entry), **Journey 4** (Support/Troubleshooting cost anomaly investigation), and **Journey 5** (API/Integration Codex parallel-authoring port). No journey is deferred to Growth/Vision — all five must be walkable by a single operator before Phase 1 closes.

**Must-Have Capabilities.** Phase 1 ships exactly the **13 substrate-completeness deliverables across the 5 clusters** cataloged in Step 3's MVP tier table. Layered on top:
- **7 scope-binding commitments** (substrate-completeness lock; 11-specialist roster floor; 34-row mapping-checklist floor; Composition Spec invariants honored; sandbox-AC dev-vs-operator split; cost-budget ceilings; G-gate audit-trail completeness).
- **5 sandbox-AC inventory entries** added under `migration-ac-sandbox-inventory.json`: `gamma`, `kling`, `elevenlabs`, `wondercraft`, `dan-api-tbd`.
- **Parity-test suite — 34 tests, 1:1 with the mapping-checklist rows** — gating the Legacy↔Migrated equivalence claim that lets Slab 7b activate specialists against migrated infrastructure.

**Phase-1 Acceptance Threshold.** All seven A-clauses from Step 3 (A-1 through A-7) satisfied; trial-2 closes through G3 cleanly with no fix-on-the-fly patches outside the recoverable-deviation envelope; calibration-tripwire exercised; 11-specialist roster active; 34-row mapping-checklist coverage maintained with zero unmapped rows at trial-2 open.

### Progressive Feature Roadmap

- **Phase 1 — Slab 7a + 7b + first tracked trial-2.** **8–12 weeks wall-clock**, **1 tracked trial**, **~$3.60 total spend** (per cost-envelope estimate; budget gate fires at $5.00). Exit criterion: trial-2 readiness verified end-to-end and the seven A-clauses green.

- **Phase 2 — Doc-7-D + Slab 8 selective items.** **~4–6 weeks post-trial-2 close**; **≥1 additional trial (trial-3)** to harvest anti-pattern evidence and verify Doc-7-D distillation against real failure modes. Slab 8 items selected **per trial-2 evidence** rather than pre-committed: if `marcus pending` CLI is painfully missed during trial-2 troubleshooting, it lifts to Phase 2; if PR-TR or Texas best-medium proves more pressing, that re-orders. Doc-7-D delivers anti-pattern catalogs, v4.2 distillation, and migration-guide §12 worked examples per specialist.

- **Phase 3 — Calibration corpus + Vision items.** **~6+ months and ≥30 trials accumulated** to reach C2 confidence-gated default-and-override evolution. Triggers: Epic 15 chain reactivation (15-2 retrospective → 15-7 calibration harness); Composition Spec §11 Option C migration evaluation; post-M5 greenfield specialist activations (Mike / Eli / Mira / Sally / Kim / possibly Paige); workflow-family expansion per Epic 18 (podcasts, infographics, cases, quizzes as Tier-3 pack families). **Specialist roster grows in Phase 3 — never drops; the 11-floor is permanent.**

### Risk-Based Scoping

Step 5 catalogs *execution* risks (15 total). Step 6 catalogs *innovation* risks (IR-1..IR-7). This subsection catalogs **scoping** risks — the probability-weighted ways MVP boundary can be set wrong. None of these proposes dropping below the operator-imposed floors. All response actions operate **above** the floor.

**Technical scoping risks:**

- **SR-T1 — Dependency-chain stall.** Trigger: any of the 13 Slab 7a deliverables slips >1 week past its in-slab milestone. Response: invoke party-mode dependency triage; deliverables on the critical path (Mapping Checklist, Composition Spec, registry) hold the line; non-critical (e.g., docs polish, second-order schema) deferred to Slab 7b without floor impact. Threshold: **>1 week slip on any one deliverable**.
- **SR-T2 — K-unit blow-out vs IR-5 learning curve.** Trigger: rolling-3-story K-actual/K-target ratio crosses 1.7×. Response: pull back **scope shape** (collapse adjacent schema-shape stories; defer cosmetic polish; preserve all 34 mapping rows + 11 specialists). Threshold: **aggregate Slab 7a K-units projected >27** (≈1.3× the ~21 baseline).
- **SR-T3 — Compositor greenfield block.** Trigger: Slab 7b Compositor story T1 readiness fails twice. Response: fall back to **inline composition inside existing orchestrator** for trial-3, defer standalone `app/specialists/compositor/` to Slab 8; specialist roster stays at 11 (Compositor still counted; implementation site moves). Threshold: **2 failed T1 readiness attempts**.
- **SR-T4 — Sandbox-AC inventory PR stall.** Trigger: inventory PR open >5 business days without merge. Response: fast-track via single-reviewer party-mode-lite; Slab 7b kickoff blocked until merge (hard precondition is hard). Threshold: **5 business days open**.

**Operator-priority risks** (domain has no external market):

- **SR-M1 — Mid-Slab 11→12 specialist addition.** Trigger: operator names a 12th specialist during Slab 7a. Response: **floor is a floor, not a ceiling** — accept via party-mode consensus + governance JSON version bump; if the 12th forces re-architecture of registry/dispatch, defer the *addition* to Slab 7b kickoff (not the existing 11). Threshold: **named specialist + party-mode quorum**.
- **SR-M2 — Trial-2 surfaces additional legacy levers.** Trigger: walkthrough identifies Nth lever beyond the 34 rows. Response: **append to checklist** (35+); 34 is a floor. Threshold: **any operator-confirmed lever**.
- **SR-M3 — Hour-4 attention failure mode unanticipated.** Trigger: trial-2 reveals a fatigue/dropout pattern the PRD did not model. Response: file as IR-8 in Step 6, schedule scope-revision party-mode within Slab 7a; do not pause execution. Threshold: **operator-confirmed novel failure mode**.

**Resource scoping risks:**

- **SR-R1 — Codex parallel-authoring throughput shortfall.** Trigger: Codex closes <50% of assigned port-shape stories on milestone. Response: reassign port-shape work to Claude; extend Slab 7a wall-clock by ≤2 weeks; defer **Slab 7b** stories (not Slab 7a) to Slab 8. Threshold: **<50% close rate at week 4**.
- **SR-R2 — Trial-2 cost ceiling breach.** Trigger: trial-2 burn projects >$5.00 (T1.5 firing). Response: halt trial; trim trial-2 scope to G1+G2 only, defer G3+ rehearsal to trial-3. Threshold: **>$5.00 projected at hour-2 checkpoint**.
- **SR-R3 — Slab 7a wall-clock overrun.** Trigger: Slab 7a runtime projects >12 weeks (BS-2 target ≤8). Response: enforce SR-T2 K-pullback; defer non-floor deliverables to Slab 7b; floor stays. Threshold: **week-8 burndown shows >4-week residual**.

### Implementation Feasibility

**Story sequence — realistic at ~8 stories / ~21 K.** The Step 7 sequencing is correct: directive_composer must land first (Gap 2 closure unblocks 6 downstream stories), and manifest fold-flags + compiler extension is the second gate. Estimated K-distribution: directive_composer ~3.5K, manifest+compiler ~2K, pre-gate-marcus shared node ~2.5K, per-slide subgraph + review-pack skeleton ~3.5K, conversation persistence + summary writer ~2.5K, vocabulary registry + parity-table ~2K, A2 single-decision shims ~2K, integration ~3K. Sum ≈ 21K. Tight but achievable if no Pydantic-lockstep surprise lands mid-story.

**Critical-path stories** (must-not-slip): directive_composer; manifest fold-flags + compiler extension; per-slide subgraph + HTML review-pack skeleton; parity-test suite. Parity-test suite must be authored **alongside** the 34-row mapping checklist, not after — the test file IS the executable form of the checklist. File path lockstep: `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` ↔ `tests/parity/test_legacy_to_migrated_parity.py` (one row → one parametrize entry).

**Floatable stories** (can slip without blocking trial-2): what-I-just-did summary writer (passthrough-stub in 7a; populated in 7b); HTML review-pack skeleton (skeleton in 7a; content in 7b); operator-control parity table (documentation parallel with parity-test suite).

**Codex parallel-authoring — feasible with named fallback.** 5 port-shape stories should run at Codex throughput ≈ Claude per-story given the pattern is fixed (Slab 2a.2 Irene template). Fallback trigger: if Codex throughput drops below 0.6× Claude on any single story, Claude picks up 2-3 serially — recovers ~1 week budget.

**Compositor greenfield — accept K-floor 2.0-2.5×.** Greenfield `--kind=deterministic` scaffold is real work; ~20-25 files at ~$0.40-0.50 dev cost is consistent with prior greenfield specialists. Slab 7b dual-gate mandatory. **Mitigation:** scaffold `--kind=deterministic` on shipped specialist scaffold (Texas pattern) rather than from-scratch — recovers ~3-5 days.

**Schema-lockstep — 6-8 cycles realistic.** Pydantic surfaces in Slab 7a: directive shape; manifest fold-flag fields; conversation-persistence record; vocabulary-registry entry; parity-row schema; A2 single-decision shim envelope. 6 lockstep cycles minimum; buffer one extra for unforeseen schema surface in integration story.

**Test-suite feasibility — pass if record-once-replay-forever honored.** 40 Slab-7a tests at T1<60s + T2<5min is fine. **Hard rule:** zero T4 in CI. Aggregate 75-100 across 7a+7b is healthy.

**Wall-clock — 7-9 weeks tight; 9-10 weeks risk flagged.** Compositor greenfield is the longest-tail. With the scaffold-on-Texas-pattern mitigation, recoverable to 7-9 weeks. **Verdict: feasible, no scope-floor breach.**

---

## Functional Requirements

This is the **capability contract** for Slab 7a. Every feature in the final product must trace to an FR below; no FR, no feature. The list integrates three drafting layers: capability-area-grouped FRs (FR1-FR38), architecture-derived substrate-invariant FRs (FR-A1-FR-A24), and operator-control surface FRs (FR-O1-FR-O25). Total: **87 FRs across 8 capability areas**.

### CA-1: Inter-Gate Conversational Orchestration

- **FR1.** *Marcus* can compose a directive for any specialist by selecting from the registered directive-shape vocabulary, without dev-author hand-writing per-specialist composition logic.
- **FR2.** *Marcus* can pre-fill the operator's pre-gate decision card with proposed values derived from upstream gate state, leaving every field operator-overridable.
- **FR3.** *Slab 7a runtime* can persist every operator turn as a structured record (timestamp, gate code, decision-card payload, free-text rationale, operator identity).
- **FR4.** *Operator* can resume a paused conversation from the last persisted turn without losing prior structured-record context.
- **FR5.** *Marcus* can produce a "what I just did" summary at every gate handoff, citing the directive shape used and the specialist invoked.
- **FR-A1.** ProductionEnvelope MUST reject mutation of any prior specialist contribution; only new entries admissible (Composition Spec §3.1).
- **FR-A2.** Every specialist contribution MUST carry a SHA256 digest computed over its declared output payload.
- **FR-A3.** ProductionDispatchAdapter MUST be the sole sanctioned interface between Marcus and LangGraph state.
- **FR-O1.** Every legacy v4.2 operator-control lever in the 34-row mapping checklist MUST be reachable in the migrated runtime; essential-function preservation under different mechanism allowed.
- **FR-O2.** Live `docs/operator/legacy-vs-langgraph-control-parity.md` MUST exist with one row per checklist entry, paired with `tests/parity/test_operator_control_parity.py` that fails CI if any row regresses.
- **FR-O3.** Operator MUST NOT be required to recall legacy v4.2 prose to participate in any gate; per-gate context loaded into decision-card at gate entry.

### CA-2: Gate Topology & Fold Management

- **FR6.** *Slab 7a runtime* can honor all 14 declared gate codes regardless of fold state, exposing each as an addressable resume target.
- **FR7.** *Slab 7a runtime* can present the 10-gate frozen inventory to the operator as the default surfaced topology, with the 4 folded gates absorbed into their declared parents.
- **FR8.** *Gate runner* can read fold-flags from the manifest and absorb a folded gate's logic into its parent subgraph without losing audit attribution.
- **FR9.** *Slab 7a runtime* can emit a `gate_fold_manifest.yaml` audit artifact per run, recording which gates were folded, into which parents, and why.
- **FR10.** *Operator* can request the unfolded 14-gate view at any time and receive the full topology including folded gates.
- **FR-A7.** `pipeline-manifest.yaml` MUST be the single source of truth for graph topology, fold targets, and dependency edges (ADR-D6).
- **FR-A8.** PRODUCTION_GATE_IDS MUST be derived from manifest at compile-time; no hardcoded frozenset survives Slab 7a.
- **FR-A9.** Manifest mutations MUST conform to Tier-1/2/3 pack-version policy per `pipeline-manifest-regime.md`.
- **FR-A10.** `gate_fold_manifest.yaml` MUST enumerate effective vs declared gates with absorption mechanism per gate.
- **FR-A23.** Transitions skipping any declared `gate_code` (folded or not) MUST be refused by the runner.
- **FR-O4.** Decision-card vocabulary MUST be drawn exclusively from the unified namespaced registry; inline string literals in gate handlers forbidden.

### CA-3: Per-Slide Array Operator Review

- **FR11.** *Gate runner* can fan out a per-slide review subgraph that pauses at each slide via a structured interrupt, blocking until operator input arrives.
- **FR12.** *Slab 7a runtime* can generate an HTML review-pack for the slide array and open it in the operator's default browser at the fan-out point.
- **FR13.** *Operator* can issue a per-slide delta-directive (accept / revise-with-text / reject) for each slide independently.
- **FR14.** *Gate runner* can re-invoke the producing specialist with the delta-directive and surface the revised slide for re-review.
- **FR15.** *Slab 7a runtime* can detect oscillation on a single slide after 3 revise cycles and escalate to the operator.
- **FR-A16.** Per-slide arrays at G2B / G2F-merged / G3B MUST use subgraph-with-`interrupt()` fan-out.
- **FR-A18.** A single slide's `interrupt()` MUST NOT stall sibling slides in the cohort.
- **FR-O5.** HTML review-pack MUST be generated to `runs/<run_id>/gates/<gate>-review-pack.html` at gate entry for every per-slide-array gate.
- **FR-O6.** A browser-open event MUST be logged (FM-7 verification — pack existence alone is insufficient); gate cannot advance without the open-event timestamp.
- **FR-O7.** Each slide row MUST carry a checkbox + free-text delta-directive field; serialization schema fixed.
- **FR-O8.** On revise, review-pack MUST regenerate with the new variant highlighted; prior packs retained under `runs/<run_id>/gates/_history/` for audit.
- **FR-O9.** Per-slide oscillation cap MUST be hard-coded at 3 as state-machine invariant; the substrate refuses a 4th revise.
- **FR-O10.** On guard-fire, an `oscillation_escape_required` decision-card MUST surface with three options: accept-as-is / reject-and-skip-slide / abort-run.
- **FR-O11.** `accept-as-is` MUST require non-empty rationale string of >20 characters; substrate rejects shorter input at the writer.
- **FR-O12.** Rationale MUST be logged to conversation persistence with tamper-evident digest.

### CA-4: Specialist Activation & Roster Management

- **FR16.** *Marcus* can activate any of the 11 registered specialists (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) through a uniform activation contract.
- **FR17.** *Slab 7a runtime* can read the specialist roster from a single registry artifact (`state/config/specialist-registry.yaml`) serving as source of truth for activation, parity, and audit.
- **FR18.** *Each specialist* can persist its working state in a declared shape so a later gate can resume it without re-activation cost.
- **FR19.** *Each specialist* can emit a "what I just did" summary on deactivation, consumable by Marcus and by the audit log.
- **FR20.** *Operator* can request a roster status snapshot at any gate and receive activation state of all 11 specialists.
- **FR-A15.** Each specialist node MUST compile to its own LangGraph subgraph with isolated checkpoint boundary.
- **FR-A19.** Repeated specialist nodes MUST honor first-contribution-wins; duplicates skipped after first (Path Z, Slab 6.1).
- **FR-A20.** Path Z skip events MUST emit a structured log record — never silent.
- **FR-O17.** Each specialist MUST emit `runs/<run_id>/specialist-summaries/<name>-<timestamp>.md` (15-25 lines: received X / decided Y because Z / emitted at P).
- **FR-O18.** Next gate-handler MUST load adjacent specialist summaries inline into the decision-card; operator never chases artifact paths.
- **FR-O19.** Summary length MUST be enforced at write time; <15 or >25 lines fails the writer's assertion.

### CA-5: Decision-Card Vocabulary & Operator-Control Surface

- **FR21.** *Slab 7a runtime* can validate every operator decision against the unified namespaced decision-card vocabulary registry.
- **FR22.** *Operator* can submit a single-decision A2 shim at terminal gates (G1, G2C, G3, G4); no multi-field card required.
- **FR23.** *Operator* can request audience-layered help (OPERATOR/INPUTS/OUTPUTS/REFERENCE structure) on any decision card.
- **FR24.** *Slab 7a runtime* can render an operator-control parity table mapping each legacy lever to its Slab 7a decision-card equivalent.
- **FR-A4.** Per-specialist gate_decision precedence MUST default to non-blocking under production composition unless manifest declares otherwise (Composition Spec §3.5).

### CA-6: Calibration & Trust Substrate

- **FR25.** *Slab 7a runtime* can run the C1 calibration tripwire as closed-loop check at every gate, blocking advance when calibration drifts past threshold.
- **FR26.** *Slab 7a runtime* can track engagement-decay across consecutive operator turns and surface decay signals to Marcus.
- **FR27.** *Slab 7a runtime* can detect operator gate-bypass attempts and record them in the tripwire log without silently allowing the bypass.
- **FR28.** *Operator* can read the tripwire transparency log at any time and see every fired tripwire with cause and outcome.
- **FR-A21.** Max-3 oscillation guard MUST live in shared gate-runner substrate as `revise_count` field with transition-function-enforced escalation; gate-authors inherit, never implement.
- **FR-A22.** C1 calibration tripwire MUST be closed-loop substrate behavior: operator-override-rate over rolling N-run window auto-locks/unlocks batch-approve per gate.
- **FR-A24.** Marcus orchestrator-mode state and operator-handoff state MUST NOT mix across the dispatch adapter; boundary runtime-asserted.
- **FR-O13.** Engagement-signal MUST be recorded per per-slide decision (override entered OR explicit ack-token, not blank-enter).
- **FR-O14.** Engagement-decay report MUST auto-generate post-trial to `_artifacts/trial-2/engagement_decay_report.md`.
- **FR-O15.** SM-4 threshold (last-quartile engagement-rate ratio ≥ 0.30) breach MUST trigger the C1 calibration-tripwire automatically.
- **FR-O16.** Each gate decision-card MUST require one free-text reason of >20 characters to deter <30s rubber-stamp transitions.
- **FR-O23.** Calibration-tripwire log MUST record BOTH fire and quiet events at `_artifacts/trial-2/calibration_tripwire_log.jsonl` (FM-5 inverse — silence not presumed healthy; quiet must be witnessed).
- **FR-O24.** Operator MUST inspect tripwire state at any time via unprivileged read path (no admin token required).
- **FR-O25.** A synthetic tripwire trip MUST be exercised during Slab 7a development (T3.3 mitigation; A-4 acceptance clause).

### CA-7: Replay, Audit & Trial Capture

- **FR29.** *Slab 7a runtime* can append every gate decision to a ProductionEnvelope as append-only record (no in-place edits).
- **FR30.** *Slab 7a runtime* can compute a SHA256 digest of every gate output artifact and bind it to the envelope record.
- **FR31.** *Slab 7a runtime* can capture a complete trial-run envelope (envelope + pack-hash binding + conversation chain) sufficient to replay the run deterministically.
- **FR32.** *Slab 7a runtime* can persist the conversation as a tamper-evident hash chain across operator turns.
- **FR33.** *Slab 7a runtime* can integrate with LangSmith such that every gate emits a trace span tagged with gate code, specialist, and decision-card payload.
- **FR-A11.** Checkpointer schema migrations MUST be additive only (no DROP, no type narrowing) (ADR-D3).
- **FR-A12.** In-flight runs paused at any gate MUST resume cleanly against bumped schema.
- **FR-A13.** Checkpointer state MUST be operator-readable as versioned artifact.
- **FR-A14.** Conversation persistence chain MUST be tamper-evident: SHA256(prior_envelope_digest || decision_payload || timestamp_utc || operator_id).

### CA-8: Substrate Governance & Mapping-Checklist Traceability

- **FR34.** *Codex* can execute the 34-row mapping checklist as automated parity-test suite, with each row producing pass/fail evidence.
- **FR35.** *Codex* can fail the parity suite if any of the 34 legacy operator-control levers lacks a Slab 7a FR-traceable equivalent.
- **FR36.** *Slab 7a runtime* can be validated against the migration sandbox-AC inventory at every dev-agent gate, blocking forbidden-CLI assumptions.
- **FR37.** *Slab 7a runtime* can be validated against Composition Spec invariants at PR-merge time.
- **FR38.** *Operator* can request a checklist-coverage report mapping every FR back to its checklist row(s) and Step-3/5/6 origin clause.
- **FR-A5.** Manifest-declared dependency edges MUST resolve before any runner-level fallback path executes (Composition Spec §3.6).
- **FR-A6.** Composition Smoke gate MUST execute at every slab-opener with PASS evidence captured (§9).
- **FR-A17.** Subgraph absorption MUST be governed by `fold_target` metadata — never code branches.
- **FR-O20.** Mapping-checklist 34-row floor MUST be enforced as row-count assertion in CI; any drop blocks merge.
- **FR-O21.** Specialist roster floor of 11 MUST be enforced as `len(specialists) == 11` assertion; any drop blocks build.
- **FR-O22.** Composition Spec invariants §3.1, §3.5, §3.6, §6, §9, §10, §11 MUST be enforced as test assertions in `tests/parity/test_composition_spec_invariants.py`.

### Functional Requirements Completeness Audit

**Capability-Area Coverage Matrix:**

| # | Capability Area | Main FRs | FR-A* | FR-O* | Total |
|---|---|---|---|---|---|
| 1 | Inter-Gate Conversational Orchestration | 5 | 3 | 3 | 11 |
| 2 | Gate Topology & Fold Management | 5 | 5 | 1 | 11 |
| 3 | Per-Slide Array Operator Review | 5 | 2 | 8 | 15 |
| 4 | Specialist Activation & Roster Management | 5 | 3 | 3 | 11 |
| 5 | Decision-Card Vocabulary & Operator-Control Surface | 4 | 1 | 0 | 5 |
| 6 | Calibration & Trust Substrate | 4 | 3 | 7 | 14 |
| 7 | Replay, Audit & Trial Capture | 5 | 4 | 0 | 9 |
| 8 | Substrate Governance & Mapping-Checklist Traceability | 5 | 3 | 3 | 11 |
| **TOTALS** | | **38** | **24** | **25** | **87** |

**Traceability binding principle:** Every FR MUST cite at least one upstream anchor from {Step 3 SC IDs, Step 4 Journeys, Step 5 Domain Reqs, Step 6 Innovation/IR, Step 7 Cluster A-E, Step 8 SR, Mapping Checklist row, Composition Spec §, ADR}. The full traceability registry lives at `_bmad-output/planning-artifacts/slab-7a/fr-traceability-registry.yaml` (machine-readable, parity-test consumes it). FRs without citation FAIL completeness audit and cannot ship.

**34-row Mapping-Checklist Coverage Assertion: 34/34.** Parity-test suite at `tests/parity/test_mapping_checklist_row_NN.py` enumerates 34 tests — one per checklist row. Each test header declares `REFERENCES_FRS = [...]`. CI fails if any row lacks a test, any referenced FR is unimplemented, or any referenced FR lacks a passing unit test. **No checklist row drops.**

**11-Specialist Roster Coverage Assertion: 11/11.** All eleven specialists — **Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera** — named as actor or subject in at least one FR (FR16-FR20 cite all eleven explicitly; CA-4 enforces `len(specialists) == 11` via FR-O21). **No specialist drops.** Roster floor of 11 honored.

**Composition Spec Invariant Coverage:** Every standing-guardrail invariant traces to ≥1 FR-A*:
- §3.1 (envelope append-only + SHA256 digests) → FR-A1, FR-A2
- §3.5 (gate precedence) → FR-A4, FR-A23
- §3.6 (manifest-declared dependencies) → FR-A5, FR-A7
- §6 (chain-test-per-PR) → FR-A6
- §9 (Composition Smoke gate) → FR-A6
- §10 (Decision Log additions) → FR-A9
- §11 (migration triggers tracked) → FR-O22

**No Composition Spec violation.** All seven invariant sections covered.

**Capability Contract Reminder.** This 87-FR list is **binding**. Any feature not listed here will not exist in Slab 7a unless explicitly added via registered scope-change (party-mode consensus + governance JSON version bump). Scope-creep at dev-time is forbidden; absent FRs become deferred-inventory entries, not silent additions.

---

## Non-Functional Requirements

73 NFRs across 13 categories. Every NFR is implementation-agnostic, measurable, and upstream-anchored.

### Performance

- **NFR-P1.** T1 orchestration unit suite completes <60s aggregate, ≤2s p95 per test. Breach blocks merge.
- **NFR-P2.** T2 replay-from-fixture suite completes <5min aggregate; per-gate replay <30s. Breach blocks merge.
- **NFR-P3.** T3 specialist-bound integration smoke <2min per shim; flakiness >2% across 20-run rolling window = automatic quarantine.
- **NFR-P4.** T4 live canaries ≤3 per nightly run; aggregate wall-clock <15min; per-canary timeout 5min hard.
- **NFR-P5.** Trial-2 wall-clock ≤4h operator-attended; auto-pause at 4:00:00 with operator-confirm-to-continue card.
- **NFR-P6.** Inter-gate transition <5s wall-clock from decision-card submit to next gate entry (excludes specialist LLM call latency; measured at orchestrator boundary).
- **NFR-P7.** HTML review-pack generation <2s for any per-slide-array gate (deterministic; no LLM in path).
- **NFR-P8.** Specialist subgraph compile <500ms (LangGraph compile-time, cold).
- **NFR-P9.** Pack-hash computation <100ms per pack-of-record (determinism harness gate).

### Cost

- **NFR-C1.** Trial-2 total LLM spend ≤$3.00; per-gate spend ≤$0.30 (BS-3 budget guard fires at $0.25 warn / $0.30 hard).
- **NFR-C2.** Slab 7a dev-cycle LLM spend (T2 + T4 across all stories) ~$0.60 aggregate; tripwire at $1.20.
- **NFR-C3.** Monthly live-API CI spend ≤$50 (operator-set ceiling); operator review at $40 burn.
- **NFR-C4.** Cache hit rate ≥85% warm across 10 specialist configs + 1 Compositor determinism harness; <80% = cache-strategy review.
- **NFR-C5.** Live-API-on-CI for the five API specialists (gamma, kling, elevenlabs, wondercraft, dan-api-tbd) = **0 occurrences**; any occurrence is a governance failure requiring party-mode review.

### Test-Budget

- **NFR-T1.** K-floors — gate-shape stories 1.2-1.4× (single-gate); directive-composer 1.6× (dual-gate); Compositor greenfield 2.0-2.5×.
- **NFR-T2.** Slab 7a aggregate ~21 K-units; per-story tripwire >1.7× K closes the dev round to party-mode triage.
- **NFR-T3.** Canary aggregate 60-100 across Slab 7a; <50 under-tested, >100 over-tested (both trigger review).
- **NFR-T4.** Replay-fixture cadence — record-once-replay-forever with quarterly re-record (operator-gated); fixture staleness >120 days warns.
- **NFR-T5.** Pack-hash determinism — same fixture → identical pack-hash across 5 consecutive T2 runs; any divergence = stop-the-line.
- **NFR-T6.** Gate-decision idempotency — replaying the same operator decision-card against the same checkpointed state yields byte-identical next-state (T2 canary).

### Reliability

- **NFR-R1.** Pause/resume across schema bump: any trial paused at G0..G7 MUST resume cleanly against a bumped Postgres checkpointer schema.
- **NFR-R2.** Subgraph isolation: a single slide's `interrupt()` MUST NOT stall sibling slides in cohort (FM-3 check).
- **NFR-R3.** Path Z first-contribution-wins: repeated specialist nodes deterministically skip after first contribution with explicit log entry — never silent.
- **NFR-R4.** Max-3 oscillation: substrate refuses 4th revise per slide as state-machine invariant, not policy.
- **NFR-R5.** Calibration tripwire determinism: synthetic-disagreement injection fires tripwire on ≥3-axis disagreement; stays quiet on consensus; 100% across injection scenarios.
- **NFR-R6.** Composition Smoke gate (Composition Spec §9) MUST PASS at every slab-opener; evidence captured in slab-opener spec.
- **NFR-R7.** Replay regression: pack-hash determinism across 5 runs over identical fixture inputs (FM-9 check).

### Integrity (audit-trail tamper-evidence)

- **NFR-I1.** ProductionEnvelope is append-only; in-place mutation raises at envelope-validator (Composition Spec §3.1).
- **NFR-I2.** Every specialist contribution carries SHA256 over canonical-JSON output (`sort_keys=True, separators=(",",":")`).
- **NFR-I3.** Conversation persistence chains as `SHA256(prior_envelope_digest || decision_payload || timestamp_utc || operator_id)`; broken link is hard audit failure, not warning.
- **NFR-I4.** Trial-475 evidence at `state/config/runs/475df528-…/` preserved for duration of Slab 7a (gitignored, local-only retention contract).
- **NFR-I5.** Trial-2 evidence captured under same envelope shape; pack-hash binding mandatory.
- **NFR-I6.** Mapping-checklist 34-row floor enforced as CI row-count assertion; any drop blocks merge (FR-O20). **Floor honored.**
- **NFR-I7.** `len(specialists) == 11` assertion; any drop blocks build (FR-O21). **Floor honored.**
- **NFR-I8.** Composition Spec invariants §3.1, §3.5, §3.6, §6, §9, §10, §11 enforced in `tests/parity/test_composition_spec_invariants.py` (FR-O22).

### Integration

- **NFR-IN1.** LangSmith trace integration: every gate emits a span tagged with gate code, specialist, decision-card payload. Placeholder-binding acceptable for Slab 7a; real-binding deferred to Slab 7b/8 with explicit `deferred-inventory.md` entry.
- **NFR-IN2.** Live-API surfaces (gamma, kling, elevenlabs, wondercraft, dan-api-tbd) accessed only via shipped Python deps (httpx + vendor SDK); operator-gated AC blocks for live evidence; sandbox-AC validator enforces.
- **NFR-IN3.** Codex parallel-authoring boundary: Codex authors port-shape Slab 7b stories (Tracy, Gary, Kira, Enrique, Wanda) + sandbox-AC inventory PR + `bmad-code-review` on every story close. Claude authors orchestration-spine + Compositor greenfield.

### Substrate-Versioning

- **NFR-V1.** Frozen-graph ceremony (Tier-2 minor): manifest changes require party-mode consensus BEFORE dev opens; version bump in `pipeline-manifest.yaml`; frozen-at-ship discipline post-trial.
- **NFR-V2.** Checkpointer schema migrations additive only (no DROP, no type narrowing) (ADR-D3); CI lints migration scripts.
- **NFR-V3.** Decision-card vocabulary registry additive only post-Slab-7a-close; modifications require party-mode + version bump.
- **NFR-V4.** Pack-version policy compliance per `pipeline-manifest-regime.md`: Slab 7a registered as Tier-2 minor extension.

### Operator-Friction

- **NFR-OX1.** Engagement-decay floor: last-quartile engagement-rate ≥ 0.30 × first-quartile in trial-2 (SM-4); breach fires C1 calibration-tripwire (FR-O15).
- **NFR-OX2.** Per-slide engagement signal: ≥50% of per-slide decisions show explicit signal (typed override OR ack-token, never blank-enter); US-6 threshold.
- **NFR-OX3.** Rationale floor: every gate transition requires non-empty rationale string >20 chars (FR-O16); <30s rubber-stamp transitions structurally impossible.
- **NFR-OX4.** Specialist-summary length envelope: 15-25 lines per summary; <15 = under-summarized; >25 = vocabulary drift (writer-assertion fail per FR-O19).
- **NFR-OX5.** Vocabulary closure: zero unregistered tokens in gate-handlers; CI test FR-O22 enforces against registered-vocabulary table.

### Operator-Trust (calibration)

- **NFR-OT1.** Tripwire dual-state proof: C1 fires ≥1 time AND stays quiet ≥1 time in trial-2; zero fires = FM-5 ("shipped but never exercised") failure.
- **NFR-OT2.** Batch-approve unlock requires ≥3 runs of confidence-correlation evidence; re-locks if override-rate exceeds threshold over rolling N-run window.
- **NFR-OT3.** Tripwire transparency: log records BOTH fire AND quiet events at `_artifacts/trial-2/calibration_tripwire_log.jsonl` (FR-O23); operator reads via unprivileged path (FR-O24).
- **NFR-OT4.** Synthetic trip during dev: tripwire exercised at least once in Slab 7a development (T3.3 mitigation; A-4 acceptance; FR-O25).

### Operator-Control envelope

- **NFR-OC1.** 34/34 parity: all mapping-checklist rows have reachable migrated equivalent; parity-test suite green (A-3 + A-6).
- **NFR-OC2.** 14/14 gate codes resolved: no silent ignore (A-2; FM-1).
- **NFR-OC3.** Subgraph-`interrupt()` discipline: per-slide arrays carry via subgraph (FM-3); zero CLI-loop-per-slide; AST scan on parent graph at green-light.
- **NFR-OC4.** Revise-loop max-3: 0 oscillation violations in trial-2; substrate refuses 4th revise (FR-O9).
- **NFR-OC5.** Zero silent gate-bypass events in trial-2 (A-5).

### Operator-Recovery

- **NFR-OR1.** Escape-card surfaces <500ms after 4th-revise refusal.
- **NFR-OR2.** Three options always: accept-as-is / reject-and-skip / abort-run (FR-O10); no two-option railroad.
- **NFR-OR3.** Accept-as-is digest <1s: tamper-evident rationale logged (FR-O12).
- **NFR-OR4.** HTML review-pack regen <2s with new variant highlighted (FR-O8).

### Operator-Documentation

- **NFR-OD1.** Parity table + CI guard: `docs/operator/legacy-vs-langgraph-control-parity.md` paired with parity-test suite that fails CI on regression (FR-O2).
- **NFR-OD2.** At-gate context loading: operator never required to recall legacy v4.2 prose; per-gate Markdown auto-loaded from `docs/conversational-gates/<gate-id>.md` (FR-O3).

### Compliance & Governance

- **NFR-CG1.** Sandbox-AC inventory PR landed against `migration-ac-sandbox-inventory.json` adding 5 new entries (gamma, kling, elevenlabs, wondercraft, dan-api-tbd) **before any Slab 7b story opens** (CG-1.1). Validator `validate_migration_story_sandbox_acs.py` must pass for every Slab 7a/7b story.
- **NFR-CG2.** Composition Smoke at slab-opener (Composition Spec §9); missing smoke = slab does not open (CG-1.2).
- **NFR-CG3.** N1-N12 substrate-inventory checklist trace attached to every slab-affecting story; completion recorded per row in story Completion Notes (CG-1.3).
- **NFR-CG4.** Four-file-lockstep on Pydantic changes: model + JSON Schema + golden + shape-pin tests in same PR; pre-commit `co-commit-invariant` hook enforces (CG-1.4).
- **NFR-CG5.** K-floor / target-range discipline (per NFR-T1, NFR-T2); story-authoring validator enforces against governance JSON (CG-1.5).
- **NFR-CG6.** Gate-mode designations read from `migration-story-governance.json` (frozen 2026-04-22); no relitigation at story-authoring; changes require party-mode + version bump (CG-1.6).
- **NFR-CG7.** Pre-commit stack (ruff + orphan-detector + co-commit-invariant) green on every PR; no `--no-verify` bypass without operator-recorded waiver (CG-1.7).
- **NFR-CG8.** Anti-pattern catalog enforcement: A12 (procedural-coupling), A17 (substrate-designed-for-isolation), P3 (composition-shape-vote-without-end-to-end-exercise) cited in code-review checklist (CG-3.1, CG-3.2).
- **NFR-CG9.** Marcus-duality boundary referenced in every Marcus-touching story (CG-3.3).
- **NFR-CG10.** BMAD sprint governance compliance: `bmad-create-prd → bmad-party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story → bmad-code-review` honored end-to-end.
- **NFR-CG11.** Deferred-inventory governance: every named-but-not-filed follow-on lands in `_bmad-output/planning-artifacts/deferred-inventory.md` at story-close per CLAUDE.md binding consultation point #3.

### NFR Coverage Audit

| Category | NFR Count | ID Range | Source Voice |
|---|---|---|---|
| Performance | 9 | NFR-P1..P9 | Murat |
| Cost | 5 | NFR-C1..C5 | Murat |
| Test-Budget | 6 | NFR-T1..T6 | Murat |
| Reliability | 7 | NFR-R1..R7 | Winston |
| Integrity | 8 | NFR-I1..I8 | Winston |
| Integration | 3 | NFR-IN1..IN3 | Winston |
| Substrate-Versioning | 4 | NFR-V1..V4 | Winston |
| Operator-Friction | 5 | NFR-OX1..OX5 | Quinn-R |
| Operator-Trust | 4 | NFR-OT1..OT4 | Quinn-R |
| Operator-Control | 5 | NFR-OC1..OC5 | Quinn-R |
| Operator-Recovery | 4 | NFR-OR1..OR4 | Quinn-R |
| Operator-Documentation | 2 | NFR-OD1..OD2 | Quinn-R |
| Compliance & Governance | 11 | NFR-CG1..CG11 | Mary |
| **TOTAL** | **73** | **13 categories** | **4 voices** |

**Coverage assertions (all four hold):**
1. **Implementation-agnostic.** Every NFR specifies HOW WELL, not HOW.
2. **Measurable.** Every NFR carries a specific threshold and cites either an acceptance clause, an FM-check, a trial metric, or a Composition Spec section reference.
3. **Upstream-anchored.** Every NFR traces back to Step 3 success criterion / Step 5 risk / Step 6 invariant / Step 8 SR / Composition Spec section.
4. **Standing-guardrail safe.** No NFR forces a specialist drop, a checklist-row drop, or a Composition Spec violation.

**Standing-guardrail structural enforcement:**
- **11-specialist roster floor:** NFR-I7 (`len(specialists) == 11` assertion blocks build).
- **34-row checklist floor:** NFR-I6 (CI row-count assertion blocks merge) + NFR-OC1 (parity-test suite).
- **Composition Spec invariants** (all 7 sections): NFR-I8 (Composition Spec conformance check at PR-merge time).

---

## Polish-Pass Notes (2026-04-28, post-Step-11)

The polish pass surfaced a set of recommendations larger than the surgical edits applied above; the navigation aids and standing-guardrail consolidation (SG-1/SG-2/SG-3) landed inline. The following recommendations from the four-voice polish round are noted but deferred to a post-trial-2 doc-pass (Doc-7-D scope) to avoid risking content regression in this PRD's structural body:

- **Move Sibling PRD context + Meta-Directive to end-of-doc Governance Appendix** (Paige + John) — top-of-doc placement currently honored for orientation; move recommended for pure-JTBD-lede preservation.
- **Section 6 (Step 3 Product Scope) trim to ≤30-line summary** with cross-ref to Section 11 (Step 8 Project Scoping & Phased Development) (Paige) — current duplication preserved as intentional design-time-vs-acceptance-time framing per Quinn-R.
- **Section-flow bridges** at Sections 7 / 9 / 12 openings (Paige) — current section transitions readable; bridges optional polish.
- **Cross-link prefixing** (Step 5 "FM-2" → "Step 6 FM-2"; Step 8 "TS-3" → "Step 3 TS-3") (Mary) — captured in frontmatter `polishPass2026_04_28.crossLinkFixes`; surgical fix in next polish pass if reader-friction surfaces.
- **Companion-document path verification:** `docs/dev-guide/sanctum-reference-conventions.md` — flagged orphan; verify or mark "(forthcoming)" before Slab 7a stories open. Mary's audit noted.

**Polish-pass scope-floor verification** (per all four voices): no specialist drop, no checklist-row drop, no Composition Spec violation introduced or implied by any polish edit. SG-1/SG-2/SG-3 enumeration in the new "Operator Non-Negotiables (Read First)" callout strengthens guardrail visibility for Codex parsing as plain markdown (frontmatter YAML may not be parsed by all readers).

---
