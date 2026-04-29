---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
status: 'complete'
completedAt: '2026-04-28'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md
  - _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-04-28.md
  - _bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md
  - docs/dev-guide/composition-specification.md
  - docs/dev-guide/pipeline-manifest-regime.md
  - docs/dev-guide/migration-story-governance.json
  - docs/dev-guide/migration-ac-sandbox-inventory.json
workflowType: 'epics-and-stories'
project_name: 'Slab 7a — Inter-Gate Conversational Orchestration (Orchestration Layer)'
subject: 'Epic and story decomposition for Slab 7a inter-gate orchestration substrate'
user_name: 'Juanl'
date: '2026-04-28'
branch: 'dev/langchain-langgraph-foundation'
fr_count: 87
nfr_count: 73
epic_count: 1
story_count: 8
parentMigrationEpics: '_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md'
siblingPRD: '_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md'
plannedSiblingEpicsFiles:
  - epics-slab-7b-specialist-activation-eleven.md
  - epics-doc-slab-7-prose-harvest.md
standingGuardrails:
  - 'SG-1: 11-specialist roster floor (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) — cannot be reduced; enforced via NFR-I7 / FR-O21 (`len(specialists) == 11` build assertion)'
  - 'SG-2: 34-row mapping checklist floor at `_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md` — cannot lose rows; enforced via NFR-I6 / FR-O20 (CI row-count assertion blocks merge)'
  - 'SG-3: Composition Spec invariants §3.1/§3.5/§3.6/§6/§9/§10/§11 — cannot be violated; enforced via NFR-I8 / FR-O22 (`tests/parity/test_composition_spec_invariants.py`)'
ratifiedAdjustmentsBatch_2026_04_28:
  reSequencing: '7a.1 → 7a.2 → 7a.6 → 7a.3 → 7a.4 → 7a.5 → 7a.7 → 7a.8 (vocabulary registry promoted from slot 6 to slot 3 — registry must precede stories that emit vocabulary into it)'
  kFloorAdjustments:
    7a.4: 'K-contract explicitly bounds HTML review-pack to skeleton-only; full styling deferred to post-Slab-7a polish; K stays at 3.5K against gate-shape 1.2-1.4× target'
    7a.8: 'flipped to dual-gate (integration story; cross-story failure modes justify conservative review)'
  governanceJSONPrecondition: 'add Slab 7a 7a.1-7a.8 gate-mode entries to docs/dev-guide/migration-story-governance.json via party-mode consensus + version bump before any Slab 7a story opens via bmad-create-story'
  manifestVersionBumpPrecondition: '7a.2 manifest fold-flags + compiler extension is Tier-2 minor pack-version bump per pipeline-manifest-regime.md; party-mode consensus + version bump required before 7a.2 dev opens'
  parityTestOwnership: 'distributed per-row across stories per row-to-story mapping (Mary); 7a.8 aggregates and asserts 34-row floor as single coverage gate'
  nfrFraming: 'NFR-CG1-CG11 (11) + NFR-I8 (1) story-scoped to 7a.8; other 61 NFRs (NFR-P*, NFR-C*, NFR-T*, NFR-R*, NFR-I1-I7, NFR-IN*, NFR-V*, NFR-OX*, NFR-OT*, NFR-OC*, NFR-OR*, NFR-OD*) are cross-cutting AC predicates applied across all 8 stories where touched code path triggers them'
  goldenTraceFixtures: '7a.8 close deliverable = record-once golden-trace fixtures from trial-2 (if trial-2 has run); else fixtures land in Slab 7b kickoff; Slab 7b inherits as input, does NOT block on them'
  scopeFloorComplianceVerified: 'all four party-mode voices (John, Mary, Amelia, Murat) explicit no SG-1/SG-2/SG-3 violations in any adjustment'
codexDeploymentBoundary:
  claudeAuthors: 'Slab 7a orchestration spine (7a.1-7a.8) + Slab 7b Compositor greenfield (separate PRD)'
  codexAuthors: 'Slab 7b port-shape stories (Tracy, Gary, Kira, Enrique, Wanda) + sandbox-AC inventory PR + bmad-code-review on every Slab 7a + 7b story close'
---

# Slab 7a — Inter-Gate Conversational Orchestration: Epic Breakdown

## Overview

This document decomposes the Slab 7a PRD (`prd-slab-7a-inter-gate-orchestration.md`, 87 FRs + 73 NFRs + 5 user journeys + 32 named risks + 10 named failure modes + 7 scope-binding commitments + 3 standing guardrails) into **one epic with eight stories** sequenced strict-serial-with-parallel-waves. Decomposition reflects:

- Substrate-completeness MVP (operator-locked; minimum-viable cut rejected at PRD Round 2)
- Standing guardrails SG-1 (11-specialist roster floor) + SG-2 (34-row mapping checklist floor) + SG-3 (Composition Spec invariants) enforced structurally via NFR-I6/I7/I8 + FR-O20/O21/O22
- Party-mode consensus on all design decisions (PRD Step-by-Step) + Step 1 batch-approved adjustments (re-sequenced 7a.6 to slot 3; 7a.8 flipped to dual-gate; 7a.4 K-contract bounds HTML to skeleton-only)
- Codex parallel-authoring boundary: all 8 Slab 7a stories Claude-authored; Codex bmad-code-review on every story close
- Sequenced execution: 7a.1 (closes trial-475 Gap 2) → 7a.2 (manifest foundation) → 7a.6 (vocabulary registry foundation) → 7a.3 → 7a.4 → 7a.5 → 7a.7 → 7a.8

**Parent migration epics file:** `epics-langchain-langgraph-migration.md` (9 epics / 56 stories at 2026-04-22; Slab 7a sibling-extends).

## Requirements Inventory

### Functional Requirements (87, extracted from PRD §Functional Requirements)

The PRD's Functional Requirements section is canonical. Total: **87 FRs across 8 capability areas**. Numbering scheme:

- **FR1–FR38** (38) — main capability-area FRs
- **FR-A1–FR-A24** (24) — architecture-derived substrate-invariant FRs
- **FR-O1–FR-O25** (25) — operator-control surface FRs

**Capability-Area Coverage Matrix:**

| # | Capability Area | Main | FR-A* | FR-O* | Total |
|---|---|---|---|---|---|
| 1 | Inter-Gate Conversational Orchestration | 5 (FR1-FR5) | 3 (FR-A1, A2, A3) | 3 (FR-O1, O2, O3) | 11 |
| 2 | Gate Topology & Fold Management | 5 (FR6-FR10) | 5 (FR-A7, A8, A9, A10, A23) | 1 (FR-O4) | 11 |
| 3 | Per-Slide Array Operator Review | 5 (FR11-FR15) | 2 (FR-A16, A18) | 8 (FR-O5, O6, O7, O8, O9, O10, O11, O12) | 15 |
| 4 | Specialist Activation & Roster Management | 5 (FR16-FR20) | 3 (FR-A15, A19, A20) | 3 (FR-O17, O18, O19) | 11 |
| 5 | Decision-Card Vocabulary & Operator-Control Surface | 4 (FR21-FR24) | 1 (FR-A4) | 0 | 5 |
| 6 | Calibration & Trust Substrate | 4 (FR25-FR28) | 3 (FR-A21, A22, A24) | 7 (FR-O13, O14, O15, O16, O23, O24, O25) | 14 |
| 7 | Replay, Audit & Trial Capture | 5 (FR29-FR33) | 4 (FR-A11, A12, A13, A14) | 0 | 9 |
| 8 | Substrate Governance & Mapping-Checklist Traceability | 5 (FR34-FR38) | 3 (FR-A5, A6, A17) | 3 (FR-O20, O21, O22) | 11 |
| **TOTALS** | | **38** | **24** | **25** | **87** |

Full FR text in PRD §Functional Requirements §CA-1..CA-8. Traceability binding principle (per PRD §FR Completeness Audit): every FR cites at least one upstream anchor from {Step 3 SC IDs, Step 4 Journeys, Step 5 Domain Reqs, Step 6 IR, Step 7 Cluster A-E, Step 8 SR, Mapping Checklist row, Composition Spec §, ADR}.

### Non-Functional Requirements (73, extracted from PRD §Non-Functional Requirements)

Total: **73 NFRs across 13 categories**.

| Category | Count | ID Range | Story-Scoping |
|---|---|---|---|
| Performance | 9 | NFR-P1..P9 | cross-cutting AC predicates (all 8 stories) |
| Cost | 5 | NFR-C1..C5 | cross-cutting |
| Test-Budget | 6 | NFR-T1..T6 | cross-cutting |
| Reliability | 7 | NFR-R1..R7 | cross-cutting |
| Integrity | 8 | NFR-I1..I8 | NFR-I1-I7 cross-cutting; **NFR-I8 story-scoped to 7a.8** (Composition Spec invariant test suite) |
| Integration | 3 | NFR-IN1..IN3 | cross-cutting |
| Substrate-Versioning | 4 | NFR-V1..V4 | cross-cutting (NFR-V1 governance precondition for 7a.2; NFR-V2 governance precondition for 7a.6) |
| Operator-Friction | 5 | NFR-OX1..OX5 | cross-cutting |
| Operator-Trust | 4 | NFR-OT1..OT4 | cross-cutting |
| Operator-Control | 5 | NFR-OC1..OC5 | cross-cutting |
| Operator-Recovery | 4 | NFR-OR1..OR4 | cross-cutting |
| Operator-Documentation | 2 | NFR-OD1..OD2 | cross-cutting |
| Compliance & Governance | 11 | NFR-CG1..CG11 | **all story-scoped to 7a.8** (closeout governance gate) |
| **TOTAL** | **73** | **13 categories** | **62 cross-cutting + 11 story-scoped + 1 (NFR-I8) story-scoped** |

Full NFR text in PRD §Non-Functional Requirements + §NFR Coverage Audit.

### Additional Requirements (extracted from Architecture)

From `architecture-langchain-langgraph-migration.md` and the 13 ratified ADRs (D1-D13), these implementation requirements flow into Slab 7a story ACs:

- **Composition Spec §3.5 gate precedence rule** (per-specialist non-blocking by default under production composition) — enforced by FR-A4; Slab 7a does NOT alter this rule.
- **Composition Spec §3.6 dependency_map sourcing** (manifest-declared dependencies first, runner-layer fallback for opt-out nodes) — Slab 7a's `directive_composer.py` (7a.1) declares its dependencies in manifest, not fallback.
- **ADR-D3 Postgres checkpointer** — additive-only schema migrations (NFR-V2); in-flight runs paused at any gate must resume cleanly against bumped schema (NFR-R1).
- **ADR-D6 manifest-as-graph-config** — `pipeline-manifest.yaml` is single source of truth for graph topology (FR-A7); PRODUCTION_GATE_IDS derived at compile-time (FR-A8); 7a.2 makes this structural (no hardcoded frozenset).
- **ADR-D8 frozen-graph ceremony** — Tier-1/2/3 pack-version policy per `pipeline-manifest-regime.md`; Slab 7a is Tier-2 minor extension; 7a.2 manifest fold-flags requires party-mode consensus + version bump BEFORE dev opens.
- **Multi-pass envelope Path Z** (Slab 6.1 close) — "first contribution wins"; repeated specialist nodes deterministically skip after first contribution (FR-A19); Slab 7a does NOT alter dedup semantics.
- **Append-only ProductionEnvelope (Composition Spec §3.1)** — every specialist contribution carries SHA256 output digest; no in-place mutation; 7a.5 conversation-persistence chain extends this contract (FR-A14).
- **Sandbox-AC inventory governance** — `validate_migration_story_sandbox_acs.py` passes on every Slab 7a story (NFR-CG1); Slab 7a is orchestration-only (no live-API surfaces) so validator passes trivially; 5 inventory entries (gamma/kling/elevenlabs/wondercraft/dan-api-tbd) are Slab 7b precondition.
- **BMAD sprint governance compliance** — `bmad-create-prd → bmad-party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story → bmad-code-review` honored end-to-end (NFR-CG10).
- **Migration-story-governance JSON precondition** — Slab 7a story gate-mode designations (7a.1 dual-gate; 7a.2-7a.7 single-gate; 7a.8 dual-gate) MUST be added to `docs/dev-guide/migration-story-governance.json` via party-mode consensus + version bump BEFORE any Slab 7a story opens via `bmad-create-story`.
- **Composition Smoke gate (Composition Spec §9 + NFR-CG2)** — slab-opener story (7a.1) MUST produce Composition Smoke evidence at story-open with PASS verdict.
- **Codex parallel-authoring boundary** — all 8 Slab 7a stories Claude-authored; Codex authors `bmad-code-review` on every story close + Slab 7b port-shape stories + sandbox-AC inventory PR (NFR-IN3).

### UX Design Requirements

**Not applicable** per `bmm-workflow-status.yaml` ("Primary interface is conversational — no traditional UX design needed"). The Slab 7a PRD substitutes traditional UX deliverables with:

- **5 user journeys** (Journey 1 Primary Happy-Path / Journey 2 Edge-Case / Journey 3 Admin/Ops / Journey 4 Support/Troubleshooting / Journey 5 API/Integration via Codex) — see PRD §User Journeys.
- **7 operator-facing surface contracts** (CLI entry / HTML review-pack / conversation persistence / specialist-summary / vocabulary registry / parity-table / revise-loop / calibration-tripwire transparency / engagement-decay transparency) — see PRD §Operator-Facing Surface Contracts.
- **3 domain patterns + 3 anti-patterns** related to operator-experience — see PRD §Domain Patterns + §Domain Anti-Patterns.

UX-DR-equivalent requirements are folded into FR-O1-FR-O25 (operator-control surface FRs) + NFR-OX1-OX5 (operator-friction NFRs) + NFR-OT1-OT4 (operator-trust NFRs) + NFR-OC1-OC5 (operator-control NFRs) + NFR-OR1-OR4 (operator-recovery NFRs) + NFR-OD1-OD2 (operator-documentation NFRs).

### FR Coverage Map

All 87 FRs assigned to ≥1 of 8 stories (verified 87/87). Cross-cutting FRs (FR2, FR3, FR5, FR21, FR24) route through the directive-composer ↔ pre-gate-marcus spine.

| Story | Primary CA | FRs owned (primary + cross-cuts) | Count |
|---|---|---|---|
| **7a.1** directive_composer.py | CA-1 | FR1, FR2 (xc with 7a.3), FR4, FR5 (xc with 7a.5); FR-A1, FR-A2, FR-A3; FR-O3 | 8 |
| **7a.2** manifest fold-flags + compiler ext | CA-2 | FR6, FR7, FR8, FR9, FR10; FR-A7, FR-A8, FR-A9, FR-A10, FR-A23 | 10 |
| **7a.6** vocabulary registry + parity-table | CA-5 + CA-8 | FR21 (xc with 7a.3), FR24 (xc with 7a.3), FR34, FR35, FR38; FR-A5, FR-A6 (xc with 7a.7), FR-A17; FR-O1, FR-O2, FR-O4, FR-O20, FR-O21, FR-O22 | 14 |
| **7a.3** pre-gate-marcus shared LLM node | CA-1 + CA-5 | FR2 (xc), FR3 (xc with 7a.5), FR21 (xc), FR22-prep, FR23-prep, FR24 (xc); FR-A4 | 7 |
| **7a.4** per-slide subgraph + HTML review-pack | CA-3 | FR11, FR12, FR13, FR14, FR15; FR-A15, FR-A16, FR-A18; FR-O5, FR-O6, FR-O7, FR-O8, FR-O10, FR-O11, FR-O12 | 15 |
| **7a.5** conversation persistence + summary writer | CA-1 + CA-4 + CA-7 | FR3 (xc), FR5 (xc), FR16, FR17, FR18, FR19, FR20, FR29, FR30, FR31, FR32, FR33; FR-A11, FR-A12, FR-A13, FR-A14, FR-A19, FR-A20; FR-O17, FR-O18, FR-O19 | 20 (ceiling — flag rebalance only if breach) |
| **7a.7** A2 single-decision shims | CA-5 | FR22, FR23; FR-A6 (xc); NFR-OD1, NFR-OD2 (story-scoped operator-documentation surface) | 5 |
| **7a.8** integration + parity-test + closeout | CA-6 + CA-8 + integration | FR25, FR26, FR27, FR28, FR36, FR37; FR-A21, FR-A22, FR-A24; FR-O9, FR-O13, FR-O14, FR-O15, FR-O16, FR-O23, FR-O24, FR-O25; NFR-CG1..CG11 (block); NFR-I8 | 17 FR-line + NFR-CG block + NFR-I8 |

**Cross-check totals (per Mary's audit):**
- FR1–FR38: 38/38 covered ✅
- FR-A1–FR-A24: 24/24 covered ✅
- FR-O1–FR-O25: 25/25 covered ✅
- **Total: 87/87 cited** ✅

**Story-load distribution:** Range 5-20 FRs per story (within band). Median ~10. No story over-loaded; 7a.5 at ceiling but acyclic ownership graph holds.

**Standing-guardrail enforcement (SG-1/SG-2/SG-3):**
- **SG-1 (11-specialist roster):** primary enforcement in 7a.6 (vocabulary registry hard-codes 11 names + emits canonical list via FR-O21 `len(specialists) == 11` build assertion); aggregated assertion in 7a.8 parity suite.
- **SG-2 (34-row mapping checklist):** distributed authoring across stories per row-to-story mapping; 7a.6 (vocabulary registry) authors registry-related parity tests; 7a.8 aggregates and asserts 34-row floor as single coverage gate via FR-O20 (CI row-count assertion blocks merge).
- **SG-3 (Composition Spec invariants):** FR-A1/A2/A3 in 7a.1 (envelope append-only + SHA256 + dispatch adapter); FR-A4 in 7a.3 (gate precedence); FR-A5 in 7a.6 (manifest-declared dependencies); FR-A6 in 7a.6 + 7a.7 (Composition Smoke gate at slab-opener evidence); FR-A11-A14 in 7a.5 (Postgres checkpointer additive evolution); FR-A21/A22/A24 in 7a.8; FR-O22 in 7a.6 + NFR-I8 in 7a.8 author `tests/parity/test_composition_spec_invariants.py`.

## Epic List

### Epic 1: Slab 7a — Inter-Gate Conversational + Per-Slide Operator-Review Substrate

**Epic Goal:** Operator can run a multi-hour course-production trial collaborating with the eleven-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) without (a) the run silently bypassing gates that should have stopped for input, or (b) the operator's attention degrading into rubber-stamp mode by slide 18 / hour 4. Trial-2 reaches G3 cleanly with all 11 specialists active; calibration-tripwire exercised; 34-row mapping-checklist coverage maintained; no fix-on-the-fly patches.

**User outcome (post-epic):** post-Epic-1 + Slab 7b specialist activation, the operator participates in ~10 essential conversational gates (3-gate reduction from legacy 13 surfaces), per-slide arrays at G2B/G2F-merged/G3B carry via subgraph-with-`interrupt()` fan-out, revise-loops carry max-3 oscillation guard as state-machine invariant, and the operator-control parity table earns operator trust that the legacy v4.2 floor is honored.

**FRs covered:** all 87 (FR1-FR38 + FR-A1-FR-A24 + FR-O1-FR-O25). See FR Coverage Map above.

**NFRs covered:** all 73 (NFR-P1-P9, NFR-C1-C5, NFR-T1-T6, NFR-R1-R7, NFR-I1-I8, NFR-IN1-IN3, NFR-V1-V4, NFR-OX1-OX5, NFR-OT1-OT4, NFR-OC1-OC5, NFR-OR1-OR4, NFR-OD1-OD2, NFR-CG1-CG11). 11 story-scoped to 7a.8 (NFR-CG1-CG11) + 1 story-scoped to 7a.8 (NFR-I8) + 2 story-scoped to 7a.7 (NFR-OD1, NFR-OD2); other 59 cross-cutting AC predicates applied across all 8 stories where touched code path triggers them.

**Story sequence (post-Step-1 batch-approved adjustments):**

1. **Story 7a.1** — Directive Composer (Gap 2 closure) — dual-gate, ~3.5K
2. **Story 7a.2** — Manifest Fold-Flags + Compiler Extension — single-gate, ~2K *(Tier-2 manifest version bump precondition)*
3. **Story 7a.6** — Vocabulary Registry + Parity-Table — single-gate, ~2K *(promoted from slot 6 — registry must precede stories that emit vocabulary into it)*
4. **Story 7a.3** — Pre-Gate-Marcus Shared LLM Node — single-gate, ~2.5K
5. **Story 7a.4** — Per-Slide Subgraph + HTML Review-Pack Skeleton — single-gate, ~3.5K *(K-contract bounds HTML to skeleton-only; full styling deferred to post-Slab-7a polish)*
6. **Story 7a.5** — Conversation Persistence + Specialist-Summary Writer — single-gate, ~2.5K
7. **Story 7a.7** — A2 Single-Decision Shims for Terminal Gates — single-gate, ~2K *(carries NFR-OD1, NFR-OD2 operator-documentation surface as story-scoped deliverables + FR-A6 cross-cite for Composition Smoke at A2 boundary)*
8. **Story 7a.8** — Integration + Parity-Test Suite + Slab 7a Closeout — **dual-gate** (flipped from single per Murat's integration-tier risk argument), ~3K *(close deliverable = record-once golden-trace fixtures from trial-2 OR fixtures land in Slab 7b kickoff if trial-2 hasn't run)*

**Total K-units:** ~21 (matches NFR-T2 aggregate budget). Aggregate test count target: ~74 (NFR-T3 band 60-100).

**Dependency wave structure (per Amelia, Step 1):** strict-serial-with-parallel-waves — 5 effective waves:
- Wave 1: 7a.1 (composer)
- Wave 2: 7a.2 (manifest+compiler) — strict after 7a.1
- Wave 3: 7a.6 (registry) — parallel with 7a.3 (pre-gate-marcus); 7a.6 needs 7a.2; 7a.3 independent of 7a.6
- Wave 4: 7a.4 (subgraph+HTML) — needs 7a.3 + 7a.6; parallel with 7a.5 (conversation persistence)
- Wave 5: 7a.7 (shims) parallel with start of 7a.8 (integration); 7a.8 strict-last close

**Hard preconditions before Epic 1 opens:**
1. **Governance JSON precondition:** Slab 7a 7a.1-7a.8 gate-mode entries (7a.1 dual; 7a.2-7a.7 single; 7a.8 dual) added to `docs/dev-guide/migration-story-governance.json` via party-mode consensus + version bump.
2. **Manifest version bump precondition:** 7a.2 fold-flags is Tier-2 minor; party-mode + `pipeline-manifest.yaml` version bump required before 7a.2 dev opens.
3. **Companion-document orphan verification:** `docs/dev-guide/sanctum-reference-conventions.md` path verification (Mary's polish-pass audit); verify or mark "(forthcoming, Slab 7b)" before 7a.5 dev opens.
4. **Composition Smoke gate** (Composition Spec §9 + NFR-CG2): 7a.1 slab-opener produces Composition Smoke evidence with PASS verdict at story-open.

**Standalone-epic check (per skill principle #3):** Epic 1 is **NOT** standalone in the sense that it depends on prior migration substrate (Slab 1-6 SHIPPED at `97842ac`); but it IS standalone in the sense that NO future epic (Slab 7b, Doc-7-D) is required for Epic 1 to function — Slab 7b activates specialists INTO Epic 1's scaffold, but Epic 1 ships with passthrough specialists (carry-over from Slab 1) where Slab 7b would later activate. Trial-2 readiness is Epic 1's exit gate.

**Codex deployment boundary (per PRD §Codex Deployment Plan + NFR-IN3):**
- All 8 Slab 7a stories Claude-authored.
- Codex authors `bmad-code-review` on every Slab 7a + 7b story close (mutual-handoff pattern).
- Codex authors Slab 7b port-shape stories (Tracy, Gary, Kira, Enrique, Wanda) + sandbox-AC inventory PR (separate workflow; not in Epic 1 scope).

## Epic 1: Slab 7a — Inter-Gate Conversational + Per-Slide Operator-Review Substrate

**Epic Goal:** Operator can run a multi-hour course-production trial collaborating with the eleven-specialist roster (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) without (a) the run silently bypassing gates that should have stopped for input, or (b) the operator's attention degrading into rubber-stamp mode by slide 18 / hour 4.

### Story 1.1: Directive Composer (Gap 2 closure)

As the operator,
I want Marcus to compose a `directive.yaml` automatically from my `--input <corpus-path>` invocation,
So that Texas receives a real directive (not a fixture stub) and trial-2 can advance past G0 with real corpus content.

**Story metadata:** Wave 1 (slab-opener); dual-gate; ~3.5K; FR coverage 8.

**Acceptance Criteria:**

**Given** an operator invokes `bmad-trial start --input <corpus-path>`
**When** the trial start handler executes
**Then** Marcus's pre-gate-marcus node calls `app/marcus/orchestrator/directive_composer.py::compose_directive(corpus_path, source_authority_map, operator_directives)`
**And** the composed directive is written to `state/runs/<run_id>/directive.yaml`
**And** the operator sees the composed directive with an explicit confirm-or-edit prompt before Texas dispatch.

**Given** the operator confirms the composed directive
**When** Texas's `dispatch_retrieval(directive_path=<run_id>/directive.yaml, bundle_dir=<run_id>/bundle/)` is invoked
**Then** Texas executes a real retrieval (not the fixture stub at `tests/fixtures/specialists/texas/fixture_bundle/`)
**And** Texas's contribution lands in the `ProductionEnvelope` with SHA256 output digest (FR-A2)
**And** the envelope is append-only (no in-place mutation; FR-A1)
**And** the dispatch goes through `ProductionDispatchAdapter` as the sole sanctioned coupling point (FR-A3).

**Given** Slab 7a story 7a.1 is opened as the slab-opener
**When** the dev-agent runs the Composition Smoke gate per Composition Spec §9
**Then** the smoke fixture writes a 30-line throwaway script wiring composer → Texas-stub → envelope-append end-to-end
**And** the smoke evidence captures PASS verdict (FR-A6) and pastes into `_bmad-output/implementation-artifacts/migration-7-1-directive-composer.md` Completion Notes once.

**Given** the directive composer executes against real corpus
**When** the operator inspects the trial outputs
**Then** the operator never recalls legacy v4.2 prose to participate in directive composition (FR-O3 — at-gate context loaded into decision-card from `docs/conversational-gates/g0-directive-composition.md`).

**Given** the trial-475 root-cause regression test
**When** trial-475's `--input course-content/courses/tejal-APC-C1/` is replayed against the new composer
**Then** Texas receives a real directive (not the fixture stub) and the trial advances past G0 (regression evidence captured in `tests/parity/test_trial_475_directive_composition_regression.py`).

**Standing-guardrail enforcement:** SG-1 unchanged (composer is orchestration, not specialist); SG-2 directive composition row in mapping checklist preserved; SG-3 Composition Spec §3.1/§3.5/§3.6 honored.

**Story-scoped NFR predicates:** NFR-P6 (<5s gate transition); NFR-R1 (pause/resume across schema bump); NFR-R6 (Composition Smoke gate PASS); NFR-I1 (envelope append-only); NFR-I2 (SHA256 canonical-JSON); NFR-IN3 (Codex bmad-code-review on close).

---

### Story 1.2: Manifest Fold-Flags + Compiler Extension

As the orchestration runtime,
I want `pipeline-manifest.yaml` to declare fold-flag and fold-target metadata per node so that `PRODUCTION_GATE_IDS` is derived from manifest at compile-time,
So that all 14 declared gate codes (G0, G0A, G0B, G1, G1A, G1.5, G2, G2B, G2C, G2M, G2.5, G2F, G3, G3B, G4, G4A, G4B, G5) are honored at runtime — none silently ignored — and the 10-gate frozen inventory is structurally enforced by the manifest, not by code branches.

**Story metadata:** Wave 2 (strict after 7a.1); single-gate; ~2K; FR coverage 10.

**Hard precondition:** Tier-2 minor pack-version bump per `pipeline-manifest-regime.md` requires party-mode consensus + `pipeline-manifest.yaml` version bump BEFORE 7a.2 dev opens (NFR-V1; NFR-CG6 governance JSON entries already landed per Epic 1 hard precondition #1).

**Acceptance Criteria:**

**Given** the manifest schema extension
**When** a node entry is authored in `state/config/pipeline-manifest.yaml`
**Then** the entry can declare optional `fold_with: <upstream_gate_code>` OR `fold_target: subgraph:<name>` metadata (FR-A7 manifest-as-graph-config; FR-A10 fold-target audit).

**Given** the compiler extension at `app/manifest/compiler.py`
**When** the manifest is compiled
**Then** `PRODUCTION_GATE_IDS` is derived from manifest fold_target metadata at compile-time (FR-A8 — no hardcoded frozenset survives Slab 7a; CI grep-guard rule + import-time assertion enforce).

**Given** the manifest contains all 14 declared gate codes
**When** the runner executes a trial
**Then** every declared gate code resolves to either `mechanism: pause_point` (mapped to one of the 10 frozen gates) OR `mechanism: fold_with: <upstream_gate_code>` (folded into upstream) (FR6, FR7, FR-A23 gate-bypass refusal).

**Given** the audit artifact `state/config/gate_fold_manifest.yaml`
**When** the runner produces an effective-vs-declared gates report
**Then** all 14 codes are enumerated with mechanism per code; `grep -c '^- code:' gate_fold_manifest.yaml` returns 14; zero entries have `mechanism: ignore` or absent `mechanism:` field (FR9, FR-A10).

**Given** the operator requests the unfolded 14-gate view via CLI flag
**When** the runner emits the topology
**Then** the full 14-gate topology is returned including folded gates (FR10).

**Given** Tier-2 minor manifest version bump
**When** the dev-agent opens 7a.2
**Then** party-mode consensus is recorded + `pipeline-manifest.yaml` version field bumped + frozen-at-ship discipline applies post-trial (NFR-V1, NFR-V4).

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 14-vs-10 gate row in mapping checklist preserved; SG-3 Composition Spec D6 manifest-as-graph-config honored.

**Story-scoped NFR predicates:** NFR-P8 (<500ms compile); NFR-V1, NFR-V4 (Tier-2 minor); NFR-T2 (K-floor 1.2-1.4× single-gate; ~2K target); NFR-CG6 governance JSON entries pre-landed.

---

### Story 1.3: Vocabulary Registry + Parity-Table

As the orchestration runtime + dev-agents (Claude/Codex),
I want a unified namespaced decision-card vocabulary registry at `docs/conversational-gates/_registry/vocabulary.yaml` and an operator-control parity table at `docs/operator/legacy-vs-langgraph-control-parity.md`,
So that downstream stories (7a.3-7a.5, 7a.7) emit decision-card vocabulary that's pre-registered (FR-O4 no-inline-string-literals; closed-set red-rejection) and so that the 34-row mapping-checklist legacy↔migrated trace is operator-readable + CI-enforceable.

**Story metadata:** Wave 3 (parallel with 7a.3; needs 7a.2 manifest foundation); single-gate; ~2K; FR coverage 14. **Promoted from slot 6 to slot 3 per Step 1 batch-approved adjustment** — registry must precede stories that emit vocabulary into it.

**Acceptance Criteria:**

**Given** the vocabulary registry artifact
**When** a dev-agent edits `docs/conversational-gates/_registry/vocabulary.yaml`
**Then** the registry uses three top-level namespaces (`gates`, `specialists`, `shared`) with closed-enum value sets per namespace (FR21).

**Given** a Pydantic-v2 enum loader at `app/models/decision_cards.py`
**When** the runtime imports the registry at startup
**Then** the loader emits a closed-enum schema with triple-layer red-rejection per `pydantic-v2-schema-checklist.md` (FR-A6 four-file-lockstep: model + JSON Schema + golden + shape-pin tests).

**Given** the parity table at `docs/operator/legacy-vs-langgraph-control-parity.md`
**When** the dev-agent authors the table
**Then** it has one row per legacy v4.2 operator-control lever in the 34-row mapping checklist (left column = legacy lever, right column = LangGraph equivalent path/command); 34 rows total (FR-O2 + SG-2 floor).

**Given** the parity-test suite at `tests/parity/test_operator_control_parity.py`
**When** CI runs
**Then** the suite fails if any row's right-column command does not produce the asserted control behavior; row-count assertion `len(rows) == 34` blocks merge if violated (FR-O2 + FR-O20 + NFR-I6).

**Given** the canonical specialist roster
**When** the registry is built
**Then** the registry hard-codes the 11 specialist names (Texas, Irene, Dan, Tracy, Gary, Kira, Wanda, Enrique, Compositor, Quinn-R, Vera) as a closed list; `len(specialists) == 11` build assertion blocks build if violated (FR-O21 + NFR-I7 + SG-1 floor).

**Given** the auto-generated glossary script
**When** the script runs
**Then** it emits `docs/conversational-gates/_registry/glossary.md` (one source of truth for both registry + glossary surfaces; auto-sync via CI).

**Given** the manifest fold-flag artifact from 7a.2
**When** 7a.3 imports vocabulary at runtime
**Then** all decision-card emit sites pull from the registry; CI test `test_no_ad_hoc_vocabulary_tokens` AST-scans gate-handler modules and fails on any unregistered token (FR-O4).

**Given** Composition Spec §9 Composition Smoke gate evidence at slab-opener (already captured in 7a.1)
**When** 7a.3-7a.5 build atop the registry
**Then** the registry FR-A5 (manifest-declared dependencies) and FR-A17 (subgraph-absorption-via-fold-target) invariants are enforced per Composition Spec §3.6.

**Standing-guardrail enforcement:** **SG-1 primary enforcement here** (FR-O21 hard-codes 11-specialist roster; build assertion blocks drop). **SG-2 primary enforcement here** (FR-O2 + FR-O20 — parity table + parity-test suite + 34-row CI assertion). SG-3 Composition Spec §3.6 + §10 Decision Log entries honored (FR-A5).

**Story-scoped NFR predicates:** NFR-V3 (registry additive only post-Slab-7a-close); NFR-CG2 Composition Smoke evidence already captured at 7a.1 referenced; NFR-T2 (K-floor 1.2-1.4× single-gate; ~2K target).

---

### Story 1.4: Pre-Gate-Marcus Shared LLM Node

As the orchestration runtime,
I want a single shared `pre-gate-marcus` LangGraph node at `app/marcus/orchestrator/pre_gate_marcus.py` that pre-fills C1 template-with-slots decision-card proposals with confidence + rationale before each conversational gate,
So that all 10 essential conversational gates inherit a uniform pre-fill mechanism (no per-gate hand-rolling), single LLM call site, single checkpoint boundary, and Tier-1 additive manifest bump (vs Tier-2 if added per-gate).

**Story metadata:** Wave 3 (parallel with 7a.6; needs 7a.2 manifest foundation; independent of 7a.6); single-gate; ~2.5K; FR coverage 7.

**Acceptance Criteria:**

**Given** the new shared `pre-gate-marcus` node in `pipeline-manifest.yaml`
**When** the manifest compiles
**Then** the node fires before every gate code in the 10-gate frozen inventory (FR2 — pre-fill with confidence + rationale).

**Given** the C1 template-with-slots renderer (Jinja2 templates at `docs/conversational-gates/<gate-id>.j2`)
**When** the pre-gate-marcus node executes for gate G_n
**Then** the renderer loads `docs/conversational-gates/g{n}.j2`, fills slots from upstream gate state + specialist contributions, and emits a structured pre-fill proposal with `decision`, `directive`, `rationale`, `confidence`, `confidence_signals` fields (FR2 + FR3 — operator-turn structured-record format).

**Given** the per-specialist `gate_decision` precedence rule (Composition Spec §3.5)
**When** the pre-gate-marcus node runs under production composition
**Then** per-specialist gates are non-blocking by default; pre-gate-marcus does NOT alter the precedence rule (FR-A4).

**Given** the decision-card vocabulary registry from 7a.6
**When** pre-gate-marcus emits proposals
**Then** every emitted token is registered in the vocabulary registry; CI test `test_pre_gate_marcus_vocabulary_closure` fails on any ad-hoc token (FR21, FR-O4 cross-cite).

**Given** the operator confirms or edits the pre-fill proposal
**When** the operator-turn is recorded
**Then** the structured-record format includes operator decision + override-or-accept + rationale + timestamp + tamper-evident digest (FR2, FR3, FR21, FR22-prep, FR23-prep, FR24).

**Given** a single LLM call site (pre-gate-marcus is the only LLM-invoking node before any conversational gate)
**When** the runner traces the trial
**Then** LangSmith spans show one `pre-gate-marcus` invocation per gate transition; downstream gate handlers do NOT invoke LLM directly (FR2 + NFR-IN1).

**Standing-guardrail enforcement:** SG-1 unchanged (Marcus is orchestrator, not specialist roster member); SG-2 multiple checklist rows preserved (every gate has corresponding pre-fill mechanism); SG-3 Composition Spec §3.5 gate precedence honored.

**Story-scoped NFR predicates:** NFR-P6 (<5s gate transition excluding LLM call); NFR-OX3 (rationale floor >20 chars enforced at writer); NFR-CG4 four-file-lockstep on Pydantic changes; NFR-T2 (K-floor 1.2-1.4×; ~2.5K target).

---

### Story 1.5: Per-Slide Subgraph + HTML Review-Pack Skeleton

As the operator,
I want per-slide arrays at G2B (variant selection by Gary), G2F-merged (motion designation+approval by Kira), and G3B (Storyboard B HIL review by Quinn-R) to surface as a generated HTML review-pack at `runs/<run_id>/gates/<gate>-review-pack.html` opened in my browser at gate entry, with each slide carrying a checkbox + free-text delta-directive field, backed structurally by a LangGraph subgraph-with-`interrupt()` fan-out pattern,
So that I can review and decide on 30 slides without the per-slide CLI-loop collapse failure mode, and substrate (not policy) prevents rubber-stamping by structurally fanning out per-slide decision boundaries.

**Story metadata:** Wave 4 (needs 7a.3 pre-gate-marcus + 7a.6 vocabulary registry; parallel with 7a.5); single-gate; ~3.5K; FR coverage 15. **K-contract bounds HTML to skeleton-only per Step 1 batch-approved adjustment** — full styling deferred to post-Slab-7a polish; if HTML review-pack scope grows beyond skeleton during dev, the K tripwire fires and 7a.4 escalates to dual-gate.

**Acceptance Criteria:**

**Given** the per-slide subgraph at `app/marcus/orchestrator/per_slide_subgraph.py`
**When** Gary/Kira/Quinn-R produce per-slide outputs
**Then** the parent graph fans out one subgraph instance per slide, each with isolated checkpoint boundary; each instance emits `interrupt()` per slide; parent joins on completion (FR-A15 + FR-A16 + FR-A18).

**Given** the FM-3 AST scan at `tests/structural/test_per_slide_subgraph_pattern.py`
**When** CI runs
**Then** the test fails if any parent graph contains repeated `interrupt()` inside a per-slide `for` loop (FM-3 — subgraph-degenerating-to-parent-graph-loop check).

**Given** the HTML review-pack generator at `app/marcus/orchestrator/html_review_pack.py`
**When** a per-slide-array gate fires
**Then** the generator writes `runs/<run_id>/gates/<gate>-review-pack.html` with one row per slide, each row carrying checkbox + free-text delta-directive field; serialization schema fixed (FR-O5 + FR-O7).

**Given** a browser-open event hook
**When** the review-pack file is generated
**Then** the operator's default browser is invoked AND a browser-open event is logged at `runs/<run_id>/gates/<gate>-pack-open.log`; the gate cannot advance without an open-event timestamp (FR-O6 — FM-7 verification).

**Given** the operator submits a delta-directive for slide N as `revise`
**When** the substrate routes the delta back to the producing specialist subgraph
**Then** the specialist regenerates slide N as v2; the HTML review-pack regenerates with v2 highlighted; prior pack retained at `runs/<run_id>/gates/_history/<gate>-v1.html` for audit (FR-O8).

**Given** the operator clicks `revise` a 4th time on the same slide
**When** the substrate evaluates the revise count
**Then** the substrate refuses (state-machine invariant `revise_count <= 3` per `app/models/state/operator_verdict.py` extension; FR-A21 enforces); an `oscillation_escape_required` decision-card surfaces with three options (accept-as-is / reject-and-skip-slide / abort-run); accept-as-is requires non-empty rationale string >20 chars (FR-O11 — substrate rejects shorter input at the writer).

**Given** the four-file-lockstep on `operator_verdict.py` extension
**When** the dev-agent commits the model change
**Then** the same PR includes the model + JSON Schema regen + golden fixture refresh + shape-pin tests (NFR-CG4).

**Given** the K-contract for 7a.4
**When** the dev-agent opens the story
**Then** the AC explicitly bounds HTML review-pack to skeleton-only (semantic HTML structure; checkbox + delta-field; no full styling); full styling deferred to post-Slab-7a polish; if scope grows beyond skeleton, K-tripwire (>1.7×) fires and 7a.4 escalates to dual-gate (per Step 1 batch-approved adjustment).

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 G2B/G2F-merged/G3B per-slide rows preserved with subgraph-mechanism citation; SG-3 Composition Spec §3.5 (per-specialist non-blocking) honored — each per-slide subgraph has isolated checkpoint boundary.

**Story-scoped NFR predicates:** NFR-P7 (<2s HTML pack generation); NFR-OR1 (escape-card surfaces <500ms); NFR-OR4 (HTML regen <2s); NFR-OX2 (engagement signal); NFR-OC3 (subgraph-`interrupt()` discipline; AST scan); NFR-OC4 (revise-loop max-3 invariant).

---

### Story 1.6: Conversation Persistence + Specialist-Summary Writer

As the operator + the audit-trail substrate,
I want every operator turn persisted as a structured record under `runs/<run_id>/conversation/<gate_id>/` with tamper-evident SHA256 chain, and every specialist to emit a "what I just did" summary at `runs/<run_id>/specialist-summaries/<name>-<timestamp>.md` (15-25 lines) loaded inline by the next gate-handler,
So that I have hot-pickup context at every gate (no chasing artifact paths) and the trial trace is replay-deterministic + audit-recoverable.

**Story metadata:** Wave 4 (parallel with 7a.4; needs 7a.3 pre-gate-marcus); single-gate; ~2.5K; FR coverage 20 (at ceiling — no preemptive split per Mary's audit; rebalance only if breach occurs at gate-closeout).

**Acceptance Criteria:**

**Given** the conversation persistence module at `app/marcus/orchestrator/conversation_persistence.py`
**When** the operator submits a turn (decision-card payload)
**Then** the writer creates `runs/<run_id>/conversation/<gate_id>/<turn_n>.json` with the structured-record format (timestamp, gate code, decision-card payload, free-text rationale, operator identity) (FR3 + FR-O17-prep).

**Given** the tamper-evident chain
**When** the writer computes the digest for turn N
**Then** the digest is `SHA256(prior_envelope_digest || decision_payload || timestamp_utc || operator_id)`; the chain is verifiable end-to-end; broken link is hard audit failure, not warning (FR-A14 + NFR-I3).

**Given** the specialist-summary writer at `app/marcus/orchestrator/specialist_summary_writer.py`
**When** any of the 11 specialists completes its `_act` body
**Then** the writer emits `runs/<run_id>/specialist-summaries/<name>-<timestamp>.md` with the format: header (specialist name, gate, timestamp) + "received X" + "decided Y because Z" + "emitted artifacts at paths P" (FR-O17).

**Given** the length envelope enforced at write time
**When** the writer is invoked
**Then** summary length is enforced as 15-25 lines; <15 or >25 fails the writer's assertion (not a lint warning) (FR-O19 — NFR-OX4 envelope).

**Given** the next gate-handler imports adjacent specialist summaries
**When** the gate handler renders the decision card
**Then** the immediately-prior specialist summary is loaded inline into the decision card; operator never chases artifact paths (FR-O18).

**Given** the 11-specialist roster
**When** any specialist completes
**Then** that specialist's summary writer is wired into its emit-node; specialist persistence shape conforms to the declared schema in `app/models/state/specialist_state.py` (FR16-FR20 specialist activation contract; FR-A11 Postgres checkpointer additive).

**Given** the multi-pass envelope Path Z (Slab 6.1)
**When** a specialist node fires repeatedly (e.g., Irene Pass-1 + Pass-2)
**Then** only the first contribution lands; duplicates are skipped after first with explicit log entry; conversation persistence chain accommodates the skip (FR-A19 + FR-A20 + NFR-R3).

**Given** the trial-run capture envelope
**When** the trial closes
**Then** `_artifacts/trial-2/run_summary.yaml` captures `terminal_gate`, `silent_bypass_events: 0`, `specialist_roster_count: 11`, pack-hash binding, conversation chain digest, LangSmith trace_id (FR29-FR33).

**Given** Postgres checkpointer schema migrations
**When** any 7a story extends the schema
**Then** migrations are additive only (no DROP, no type narrowing); in-flight runs paused at any gate resume cleanly against bumped schema (FR-A11 + FR-A12 + NFR-V2).

**Standing-guardrail enforcement:** SG-1 enforced (FR16 enumerates all 11 specialists explicitly; specialist-summary writer wired for all 11); SG-2 conversation persistence rows + specialist-state persistence rows preserved; SG-3 Composition Spec §3.1 append-only envelope + SHA256 invariants honored (FR-A11-A14).

**Story-scoped NFR predicates:** NFR-I3 (tamper-evident chain); NFR-I4 (Trial-475 evidence retention); NFR-I5 (Trial-2 envelope parity); NFR-OX4 (summary length envelope 15-25); NFR-V2 (additive-only schema migrations); NFR-T2 (~2.5K K-target; ceiling at 20 FRs).

---

### Story 1.7: A2 Single-Decision Shims for Terminal Gates (G1, G2C, G3, G4)

As the operator,
I want gate-scoped CLI shims at `app/marcus/cli/gate_shims/g{1,2c,3,4}_shim.py` for the four terminal gates that already pause cleanly today (G1, G2C, G3, G4), each with audience-layered help text following the OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section structure,
So that I have a uniform single-decision CLI surface for terminal gates (no multi-field card required) and I can hand the PRD to Codex for parallel-authoring of similar shims in Slab 7b without reauthoring the help-text contract.

**Story metadata:** Wave 5 (parallel with start of 7a.8; independent of 7a.4/7a.5/7a.6); single-gate; ~2K; FR coverage 5 (post-augment per Mary's Step 2 finding — added FR-A6 cross-cite + NFR-OD1/OD2 first-class scope to bring count above 5-floor).

**Acceptance Criteria:**

**Given** four shim modules (one per terminal gate)
**When** the operator invokes `bmad-trial gate G_n --verdict-file <path>` for gate G_n in {G1, G2C, G3, G4}
**Then** the shim accepts a single-decision verdict (no multi-field card); structured payload conforms to `app/models/state/operator_verdict.py` (FR22).

**Given** each shim's `--help` output
**When** the operator runs `bmad-trial gate G_n --help`
**Then** the help text follows the OPERATOR/INPUTS/OUTPUTS/REFERENCE four-section structure (FR23 + NFR-OD1 + NFR-OD2 — operator-documentation surface as story-scoped deliverable).

**Given** the CI lint at `tests/cli/test_shim_help_structure.py`
**When** CI runs
**Then** the lint asserts each of the 4 shims has all four sections present and ordered (OPERATOR → INPUTS → OUTPUTS → REFERENCE) (FR23 + NFR-OD1).

**Given** the Composition Smoke gate evidence at A2 boundary
**When** the dev-agent opens 7a.7
**Then** the shim layer is exercised in Composition Smoke (each terminal-gate shim accepts a stub verdict + advances the runner) (FR-A6 cross-cite from 7a.6).

**Given** the decision-card vocabulary registry from 7a.6
**When** the shim emits a verdict
**Then** the verdict tokens are drawn exclusively from the registry; no inline string literals (FR-O4 cross-cite).

**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 four terminal-gate rows preserved (G1, G2C, G3, G4 already in mapping checklist); SG-3 Composition Spec §3.5 gate precedence honored.

**Story-scoped NFR predicates:** **NFR-OD1 + NFR-OD2 first-class story-scoped here** (operator-documentation surface assertions for shim help text); NFR-T2 (K-floor 1.2-1.4×; ~2K target).

---

### Story 1.8: Integration + Parity-Test Suite + Slab 7a Closeout

As the operator + the substrate-completeness gate,
I want a parity-test suite at `tests/parity/` mirroring the 34-row mapping checklist (one test per legacy operator-control lever), Composition Spec invariant test suite at `tests/parity/test_composition_spec_invariants.py`, calibration-tripwire substrate behavior wired into the gate-runner, gate-bypass detection hook, max-3 oscillation guard as state-machine invariant, engagement-decay reporting, sandbox-AC validator pass on every Slab 7a story, and Slab 7a closeout artifacts (sprint-status update, deferred-inventory entries, retrospective evidence),
So that all seven scope-binding commitments (Subgraph-with-`interrupt()` / Max-3 / Frozen 10-gate inventory / Pre-composition QA validator / Decision-card vocabulary registry / C1 calibration-tripwire / Parity-test suite) are landed and tested, and trial-2 closes through G3 cleanly with all 11 specialists active.

**Story metadata:** Wave 5 (strict-last); **dual-gate** (flipped from single per Step 1 batch-approved adjustment — integration story; cross-story failure modes justify conservative review); ~3K; FR coverage 17 FR-line + NFR-CG block + NFR-I8.

**Acceptance Criteria:**

**Given** the 34-row mapping-checklist (`_bmad-output/planning-artifacts/slab-7-legacy-migrated-mapping-checklist.md`)
**When** the parity-test suite at `tests/parity/test_mapping_checklist_row_NN.py` is executed
**Then** the suite enumerates 34 tests (one per row); each test header declares `REFERENCES_FRS = [...]` + `MAPPING_CHECKLIST_ROW = NN`; CI fails if any row lacks a test, any referenced FR is unimplemented, or any referenced FR lacks a passing unit test (FR34 + FR35 + FR-O20 + NFR-I6 + SG-2 floor structurally enforced).

**Given** the Composition Spec invariant test suite at `tests/parity/test_composition_spec_invariants.py`
**When** CI runs
**Then** all seven Composition Spec invariant sections are tested (§3.1 envelope append-only + SHA256; §3.5 gate precedence; §3.6 manifest-declared dependencies; §6 chain-test-per-PR; §9 Composition Smoke gate; §10 Decision Log; §11 migration triggers tracked) (FR-O22 + NFR-I8 + SG-3 floor structurally enforced).

**Given** the calibration-tripwire substrate at `app/marcus/orchestrator/gate_runner.py` (or shared substrate module)
**When** the operator-override-rate at any gate exceeds threshold over rolling N-run window
**Then** batch-approve auto-locks at the affected gate for the next 3 trials; tripwire log records BOTH fire and quiet events at `_artifacts/trial-2/calibration_tripwire_log.jsonl`; FM-5 inverse — silence is not assumed healthy; quiet must be witnessed (FR-A22 + FR-O23 + FR-O24).

**Given** the synthetic tripwire trip during dev
**When** 7a.8 executes the synthetic-disagreement injection fixture
**Then** the tripwire fires on ≥3-axis disagreement, stays quiet on consensus; ≥1 fire + ≥1 quiet captured in trial-2 (FR-O25 + NFR-OT1 + NFR-OT4 + A-4 acceptance clause).

**Given** the gate-bypass detection hook
**When** the runner attempts a transition that skips a declared gate_code
**Then** the runner refuses the transition (FR-A23 + FR27 + NFR-OC5); in trial-2, `silent_bypass_events: 0` is asserted in `_artifacts/trial-2/run_summary.yaml` (FR36).

**Given** the engagement-decay report generator
**When** trial-2 closes
**Then** `_artifacts/trial-2/engagement_decay_report.md` is auto-generated reporting first-quartile rate, last-quartile rate, ratio, pass/fail; SM-4 threshold (last-quartile ratio ≥ 0.30 × first-quartile) breach triggers C1 calibration-tripwire (FR-O14 + FR-O15 + NFR-OX1 + NFR-OT3).

**Given** the gate-runner shared substrate
**When** any gate executes
**Then** max-3 oscillation guard is implemented as state-machine invariant (`revise_count` field in checkpointer state; transition function enforces escalation at 3; gate-authors inherit not implement) (FR-A21 + FR-O9 + NFR-R4 + NFR-OC4 — across all gates, not per-gate hand-rolling).

**Given** the Marcus-duality boundary
**When** the dispatch adapter executes any Marcus-touching transition
**Then** orchestrator-mode state never mixes with operator-handoff state (FR-A24 + NFR-CG9 — runtime-asserted boundary; reviewer confirms in code review).

**Given** the sandbox-AC validator
**When** every Slab 7a story closes
**Then** `python scripts/utilities/validate_migration_story_sandbox_acs.py <story-file>` returns zero warnings (NFR-CG1 — Slab 7a is orchestration-only; trivially passes).

**Given** the BMAD sprint governance
**When** Slab 7a stories are authored + reviewed + closed
**Then** the workflow chain is honored: `bmad-create-prd → bmad-party-mode → bmad-create-epics-and-stories → per-story bmad-dev-story → bmad-code-review` end-to-end; no improvised single-persona substitution at green-light or initial-review gates (NFR-CG10).

**Given** the deferred-inventory governance
**When** Slab 7a stories close
**Then** every named-but-not-filed follow-on lands in `_bmad-output/planning-artifacts/deferred-inventory.md` per CLAUDE.md binding consultation point #3; retrospective + session hot-start reads the inventory (NFR-CG11).

**Given** the four-file-lockstep on every Pydantic touch in Slab 7a
**When** any story closes
**Then** the model + emitted JSON Schema + golden + shape-pin tests landed in the same PR; pre-commit `co-commit-invariant` hook enforces; PR cannot merge if any of the four is missing or stale (NFR-CG4).

**Given** the K-floor / target-range discipline
**When** any Slab 7a story exceeds 1.7× its K-target
**Then** the over-spend tripwire fires; the dev round closes; the story escalates to party-mode triage (NFR-CG5).

**Given** the gate-mode designations
**When** any Slab 7a story opens via `bmad-create-story`
**Then** gate-mode is read from `docs/dev-guide/migration-story-governance.json` (frozen 2026-04-22 with Slab 7a entries added per Epic 1 hard precondition #1); no relitigation at story-authoring time (NFR-CG6).

**Given** the pre-commit stack
**When** any Slab 7a story PR is submitted
**Then** ruff + orphan-detector + co-commit-invariant are green; no `--no-verify` bypass without operator-recorded waiver (NFR-CG7).

**Given** the anti-pattern catalog enforcement
**When** any Slab 7a code-review checklist is executed
**Then** A12 (procedural-coupling), A17 (substrate-designed-for-isolation), P3 (composition-shape-vote-without-end-to-end-exercise) are explicitly cited (NFR-CG8).

**Given** the Composition Smoke gate at slab-opener
**When** 7a.8 closes
**Then** the slab-opener evidence (originally captured at 7a.1) is referenced in 7a.8 closeout artifact; Composition Smoke pre-PASS is mandatory for slab close (NFR-CG2).

**Given** the trial-2 readiness predicate (BS-2)
**When** all 8 Slab 7a stories close + Slab 7b activations complete
**Then** trial-2 is launchable against Slab 7a substrate without further code changes; all 7 acceptance clauses A-1..A-7 from PRD §Success Criteria green at 7a.8 close.

**Given** golden-trace fixtures
**When** trial-2 has run by 7a.8 close
**Then** record-once-replay-forever fixtures are committed under `_bmad-output/trial-fixtures/<trial-2-id>/`; quarterly re-record cadence calendar-tracked (operator-gated) (NFR-T4); IF trial-2 hasn't run by 7a.8 close, fixtures land in Slab 7b kickoff (Slab 7b inherits as input, does NOT block on them) (per Murat's Step 1 finding).

**Standing-guardrail enforcement:** **SG-1 aggregated assertion here** (parity suite asserts `len(roster) == 11` + name-set equality); **SG-2 aggregated assertion here** (parity suite enumerates 34 tests; row-count CI assertion blocks merge); **SG-3 aggregated assertion here** (Composition Spec invariant test suite enforces all 7 sections).

**Story-scoped NFR predicates (all NFR-CG1-CG11 + NFR-I8 here):**
- NFR-CG1 sandbox-AC inventory PR landed (Slab 7b precondition; not a 7a deliverable but referenced)
- NFR-CG2 Composition Smoke evidence pre-captured at 7a.1; referenced at 7a.8 close
- NFR-CG3 N1-N12 substrate-inventory checklist trace per Slab 7a story
- NFR-CG4 four-file-lockstep on every Pydantic change
- NFR-CG5 K-floor / target-range discipline
- NFR-CG6 gate-mode designations from frozen JSON
- NFR-CG7 pre-commit stack green
- NFR-CG8 anti-pattern catalog enforcement
- NFR-CG9 Marcus-duality boundary
- NFR-CG10 BMAD sprint governance compliance
- NFR-CG11 deferred-inventory governance
- NFR-I8 Composition Spec invariant test suite

**Plus cross-cutting NFRs converged here:** NFR-OT1 (tripwire dual-state proof); NFR-OT4 (synthetic trip during dev); NFR-OC5 (zero silent gate-bypass); NFR-OX1 (engagement-decay floor); NFR-V1 (frozen-graph ceremony close); NFR-V4 (pack-version policy compliance).

**Closeout deliverables (post-AC):**
- Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: Slab 7a stories closed; Slab 7b queued.
- Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`: Slab 7a PRD entry done; Slab 7a epic entry done.
- Update `next-session-start-here.md`: immediate-next-action = Slab 7b PRD authoring OR trial-2 dry-run.
- Update `_bmad-output/planning-artifacts/deferred-inventory.md`: Slab 7a-named follow-ons filed (Doc-7-D harvest items, structural polish-pass deferrals, sanctum-reference-conventions verification).
- Author Slab 7a retrospective per `bmad-retrospective` skill.

---

**Epic 1 closeout:** all 8 stories complete; 87/87 FRs implemented + tested; 73/73 NFRs satisfied (62 cross-cutting AC predicates + 11 NFR-CG block + 1 NFR-I8 + 2 NFR-OD); 34/34 mapping-checklist rows have parity tests; 3/3 standing guardrails (SG-1/SG-2/SG-3) structurally enforced via CI assertions; trial-2 readiness predicate green.

---

**Step 1 status:** Requirements extracted; party-mode consensus achieved on 8-story decomposition with batch-approved adjustments (re-sequence 7a.6 to slot 3; 7a.4 K-contract bounds HTML to skeleton-only; 7a.8 dual-gate; governance JSON entries as precondition; manifest version bump as 7a.2 precondition; parity-test ownership distributed per-row; NFR framing 11 story-scoped + 1 (NFR-I8) story-scoped + 61 cross-cutting; golden-trace fixtures as 7a.8 close deliverable). All four voices verified no SG-1/SG-2/SG-3 violations.
