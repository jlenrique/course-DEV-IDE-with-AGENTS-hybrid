---
stepsCompleted: ['step-01-document-discovery', 'step-02-prd-analysis', 'step-03-coverage-validation', 'step-04-ux-alignment', 'step-05-slab-quality-review', 'step-06-final-assessment']
overallReadiness: 'READY-WITH-MINOR-AMENDMENTS'
findingsCount: 5
findingCategories: ['NFR-count-drift', 'milestone-evidence-gaps', 'slab-sizing', 'slab-bundling', 'cross-slab-ownership']
assessmentTarget: 'prd-langchain-langgraph-migration.md'
assessmentScope: 'PRD-only pre-architecture gate (hybrid migration track)'
filesIncluded:
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md
filesExcluded:
  - _bmad-output/planning-artifacts/prd.md (legacy APP PRD, production-repo scope, not migration)
  - _bmad-output/planning-artifacts/architecture.md (legacy APP architecture, pre-migration)
  - _bmad-output/planning-artifacts/epics.md (legacy epic roster, production-repo scope)
  - _bmad-output/planning-artifacts/epics-interstitial-clusters.md (cluster-wave shard, production-repo scope)
---

# Implementation Readiness Assessment Report

**Date:** 2026-04-22
**Project:** course-DEV-IDE-with-AGENTS (hybrid clone)
**Branch:** `dev/langchain-langgraph-foundation`
**Assessment Target:** LangChain + LangGraph migration PRD
**Scope:** PRD-only pre-architecture gate (migration architecture + epics not yet authored; this is the readiness check *before* they open)

## Step 1 — Document Inventory

### PRD Documents

**Whole Documents:**
- `_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md` — **IN SCOPE** (migration PRD, 2026-04-22, 65 FRs + 43 NFRs enumerated in body vs. 38 in frontmatter — see drift finding #1 below)
- `_bmad-output/planning-artifacts/prd.md` — **OUT OF SCOPE** (legacy Wave-2B APP PRD, production-repo frozen reference)

**Sharded Documents:** none

### Architecture Documents

**Whole Documents:**
- `_bmad-output/planning-artifacts/architecture.md` — **OUT OF SCOPE** (legacy APP architecture, pre-migration)

**Sharded Documents:** none

**Migration-scope architecture:** NOT YET AUTHORED. Pending next workflow (`bmad-create-architecture`).

### Epics & Stories Documents

**Whole Documents:**
- `_bmad-output/planning-artifacts/epics.md` — **OUT OF SCOPE** (legacy epic roster, production-repo scope)
- `_bmad-output/planning-artifacts/epics-interstitial-clusters.md` — **OUT OF SCOPE** (cluster-wave shard, production-repo scope)

**Sharded Documents:** none

**Migration-scope epics:** NOT YET AUTHORED. Pending post-architecture workflow (`bmad-create-epics-and-stories`).

### UX Design Documents

None found. **Not required** — migration PRD confirms `workflowType: prd`; `bmm-workflow-status.yaml::ux_design.status = not-applicable` (conversational interface / developer tool).

## Critical Issues

### Duplicate format (CRITICAL)

None. `prd.md` and `prd-langchain-langgraph-migration.md` are **distinct PRDs by design**, not two versions of the same document:
- `prd.md` = legacy APP PRD (production repo's frozen Wave-2B state)
- `prd-langchain-langgraph-migration.md` = migration PRD (hybrid clone's re-platform scope)

Both are tracked in `bmm-workflow-status.yaml` under separate keys.

### Missing documents (EXPECTED — not a blocker for this assessment)

- Migration-scope **architecture** — expected missing; readiness runs *before* architecture authoring per [next-session-start-here.md:32-36](next-session-start-here.md#L32-L36).
- Migration-scope **epics + stories** — expected missing; follows architecture.

### Assessment-scope implication

Standard readiness checks traceability across PRD ↔ architecture ↔ epics/stories. For this migration session that traceability layer does not exist yet by design. This assessment will therefore be **a PRD-only pre-architecture gate**: validates PRD completeness, internal consistency, FR/NFR coverage of the locked decisions + five-slab structure, and surfaces gaps that architecture authoring would otherwise inherit as latent defects.

## Step 2 — PRD Analysis

**Source:** [_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md](_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md) (996 lines, 12-step `bmad-create-prd` authoring complete 2026-04-22)

### Functional Requirements Extracted (65 total)

**Capability Area 1 — Runtime Platform (Slab 1)**

- **FR1:** The runtime can host a compiled LangGraph application as a persistent local service, independent of any IDE session.
- **FR2:** The runtime can accept client connections from the IDE (via MCP) and from local CLI/scripts (via FastAPI), both concurrently.
- **FR3:** The runtime can checkpoint every graph-node state transition to PostgreSQL via `langgraph-checkpoint-postgres`.
- **FR4:** The runtime can resume any thread from its last checkpoint after runtime restart, operator absence, or IDE disconnection.
- **FR5:** The runtime can enforce a configurable checkpoint retention policy (cleanup + archive + audit-preservation).
- **FR6:** The runtime can emit per-node execution traces to LangSmith, including model selected, token counts, cache hit/miss, and execution duration.
- **FR7:** The runtime can be started, stopped, and health-checked via a Python entry-point (`python -m app.runtime_server`) without external orchestration tooling.
- **FR8:** The runtime can load its graph topology from the pipeline manifest (`state/config/pipeline-manifest.yaml`) at compile time, not at invocation time.

**Capability Area 2 — Specialist Framework (Slab 2)**

- **FR9:** A specialist can be instantiated from a fixed 9-node scaffold: plan → enter_sanctum → load_expertise → reason → act → validate → emit → return → exit_sanctum.
- **FR10:** A specialist can anchor its identity in a sanctum directory (`_bmad/memory/bmad-agent-{name}/`) containing INDEX.md, PERSONA.md, chronology.md, access-boundaries.md.
- **FR11:** A specialist can load its sanctum from disk on every cold invocation without carrying in-memory continuity between invocations (Sacred-Truth cold-read).
- **FR12:** A specialist can declare its expertise across a 9-layer stack (L0 LLM training → L1–L4 sanctum identity → L5 domain references → L6 operational context → L7 MCP tools → L8 runtime envelope).
- **FR13:** A specialist can be generated from scratch via `bmad-create-specialist` with scaffold, sanctum stub, typed envelope/return models, scaffold-conformance test, and specialist-registry entry emitted together.
- **FR14:** A specialist can pass a scaffold-conformance test that asserts node count, node shape, envelope contract, sanctum cold-read integrity, and node idempotency.
- **FR15:** A specialist can be invoked as a subgraph with isolated state from any parent graph (Marcus run-graph, Cora dev-graph, or test harness).
- **FR16:** A specialist can expose its capabilities to external systems via MCP tools registered at L7 of its expertise stack.

**Capability Area 3 — Model Selection (Slabs 1–2)**

- **FR17:** Every LLM-invoking node can resolve its model via a three-level cascade: runtime override → per-agent configured default → auto-select.
- **FR18:** Every specialist can declare a `model_config.yaml` specifying default model per node, or the literal `auto` to defer to auto-select.
- **FR19:** The operator can pass a runtime model override per node at trial-run start, at gate resume, or at fork-from-checkpoint.
- **FR20:** Marcus's plan/supervisor nodes can be locked to the best available OpenAI reasoning model in production config, with operator-override permitted for debugging.
- **FR21:** The auto-select function can pick a model deterministically given (agent, node_role, context_tokens, quality_tier, budget_tier) inputs, with no LLM call involved.
- **FR22:** Every model resolution can be logged to LangSmith with node, resolution level, chosen model, and fallback trail.
- **FR23:** The model registry (`app/models/registry.yaml`) can be versioned; updates governed by Tier-1/2/3 policy.
- **FR24:** The runtime can warn the operator of cache-invalidation impact before applying a mid-run runtime model override.
- **FR25:** A provider adapter (`app/models/adapter.py`) can isolate `ChatOpenAI` so provider swaps are contained changes.

**Capability Area 4 — Marcus Orchestration (Slab 3)**

- **FR26:** Marcus can operate as the Single Point of Contact (SPOT) for the operator — no specialist is operator-facing except via Marcus delegation.
- **FR27:** Marcus can run a Plan-and-Execute reasoning loop by default, switching to ReAct only when the `explore` quality preset is selected.
- **FR28:** Marcus can route work to specialists based on the manifest-defined step topology, not inline reasoning.
- **FR29:** Marcus can delegate to any specialist in the active specialist registry via a routing-edge decision, not via code-embedded selection.
- **FR30:** Marcus can cold-read its own sanctum on every session open, per the Marcus-first activation protocol.

**Capability Area 5 — Gates and HIL (Slab 3)**

- **FR31:** Every gate in the manifest can be realized as a `langgraph.interrupt()` node with a checkpointed payload.
- **FR32:** Every gate can produce a DecisionCard containing drafted specialist proposal, evidence, risks, and explicit approve/edit/reject verbs.
- **FR33:** The operator can consume a DecisionCard and emit a verdict via CLI, IDE (MCP), or FastAPI escape-hatch.
- **FR34:** A gate can block the graph until an operator verdict is received — no auto-approve, no auto-advance, no timeout-based override.
- **FR35:** A gate can resume the graph on verdict receipt, propagating the verdict payload into downstream state.
- **FR36:** The gate count per trial run can match the manifest 1:1, auditable at trial close.
- **FR37:** Reject-rate per gate can be tracked as a measurable KPI across trial runs.

**Capability Area 6 — Pipeline Lockstep & Governance (Slab 4)**

- **FR38:** The pipeline manifest can serve as the compile-time topology source.
- **FR39:** A PR touching any `block_mode_trigger_path` can fail graph compilation at CI if manifest, L1 check script, or pack contract are not updated in lockstep.
- **FR40:** Cora's dev-graph can be compiled as a sibling graph with a separate thread namespace and no lane crossover with Marcus's run-graph.
- **FR41:** A party-mode gate can be realized as a `langgraph.interrupt()` node with multiple personas contributing via structured payload before operator verdict.
- **FR42:** A code-review gate can consume LangSmith traces as primary evidence alongside git diffs.
- **FR43:** The graph version (`runtime/graphs/v42/`, `v43/`, ...) can be frozen on ship.
- **FR44:** Graph version bumps can be governed by Tier-1/2/3 policy.
- **FR45:** A learning-event ledger can emit structured events at G2C, G3, G4 as idempotent side-effects.

**Capability Area 7 — Trial-Run Discipline (Slab 5)**

- **FR46:** The operator can start a new trial run with a specified input content bundle and quality preset.
- **FR47:** The operator can pause a running trial by serializing thread state to Postgres.
- **FR48:** The operator can resume a paused trial from any closed checkpoint, from the same or a different IDE session.
- **FR49:** The operator can fork a closed trial from any checkpoint, re-executing only downstream dependent nodes.
- **FR50:** The operator can replay a closed trial from its final checkpoint, producing a byte-for-byte identical pack hash.
- **FR51:** A trial-replay regression test suite can cover 100% of closed tracked trial runs and fail on pack-hash drift.
- **FR52:** A new tracked trial run can be validated head-to-head against primary-repo trial output for the same input content.
- **FR53:** The operator can inspect any thread's current state at any checkpoint without altering it (read-only MCP `state.inspect`).

**Capability Area 8 — Economics and Observability (Slabs 1, 5)**

- **FR54:** The runtime can measure and report OpenAI prompt-cache hit rate per trial run, broken down by node and tier.
- **FR55:** The runtime can measure and report token cost per trial run, broken down by specialist, tier, cache hit/miss.
- **FR56:** The runtime can compare post-migration per-trial cost against a recorded baseline and report realized reduction percentage.
- **FR57:** The runtime can emit structured economics telemetry consumable via CLI dump at Slab 5 minimum; dashboard UI post-MVP.
- **FR58:** Every LLM invocation can be traceable in LangSmith to a specific node, specialist, and model.
- **FR59:** A sanctum invalidation hook can detect and log sanctum mutations that break prefix stability.

**Capability Area 9 — Migration Hygiene and Rollback (Slab 5)**

- **FR60:** Backports from clone to primary repo can be suspended after Slab 1 opens and resume only at Slab 5 close (as forward-ports).
- **FR61:** A forward-port playbook can specify how primary-repo changes are integrated into the clone at Slab 5 close.
- **FR62:** A rollback plan can specify how to return to the primary-repo-only operating model if M5 results in *rollback*.
- **FR63:** A 15-invariant audit matrix can be produced at M5 naming the preserving implementation pattern for each invariant with file/test references.
- **FR64:** A specialist-anti-patterns catalog can harvest ≥5 concrete anti-patterns from the migration.
- **FR65:** The migration guide can include 11 documented sections (conceptual map, specialist walkthrough, manifest translation, gate migration, schema migration, lockstep CI, frozen-graph ceremony, forward-port playbook, model-selection cutover, rollback plan, anti-patterns appendix).

**Total FRs: 65** across 9 capability areas. Count confirmed by grep of PRD source.

### Non-Functional Requirements Extracted (43 total)

**Performance (6)**

- **NFR-P1:** Gate `interrupt()` presents DecisionCard to operator within **5 seconds** of specialist proposal completion.
- **NFR-P2:** Runtime cold-start in **under 10 seconds** on laptop-class hardware.
- **NFR-P3:** Checkpoint write to Postgres in **under 500 ms** per node transition (state ~1–10 MB).
- **NFR-P4:** Sanctum cold-read per specialist invocation in **under 200 ms** on local SSD.
- **NFR-P5:** Full trial run §01→§15 in **no more than 2× current IDE-Marcus wall-clock** for same input/preset.
- **NFR-P6:** Graph compilation at CI in **under 60 seconds** for 15-step manifest + 17 specialists.

**Security (7)**

- **NFR-S1:** API keys loaded only from environment variables or `.env`; `.env` never tracked in git.
- **NFR-S2:** FastAPI escape-hatch binds only to `127.0.0.1` by default.
- **NFR-S3:** MCP server accepts connections only from local processes by default.
- **NFR-S4:** Postgres authenticates via password or local-trust in dev; production-equivalent uses password + TLS (documented, not implemented).
- **NFR-S5:** LangSmith traces can redact sensitive payload content on opt-in; default no redaction.
- **NFR-S6:** Trial artifacts and sanctum content remain on operator-controlled storage.
- **NFR-S7:** No multi-tenant concerns; runtime trusts the local operator.

**Integration (6)**

- **NFR-I1:** Tolerate transient OpenAI API errors with exponential-backoff retry per-node.
- **NFR-I2:** Tolerate LangSmith unavailability without blocking graph execution; emission failures logged non-fatal.
- **NFR-I3:** Tolerate Postgres unavailability only by pausing the thread — graph execution cannot continue without checkpointing.
- **NFR-I4:** MCP protocol compatibility pinned to specific spec version in Slab 1; bumps follow Tier-1/2/3 governance.
- **NFR-I5:** Retrieval substrate (Texas Shape 3-Disciplined contract) integrates without modification.
- **NFR-I6:** Sanctum reads treated as fatal-on-error; missing or corrupt sanctum fails fast.

**Reliability (7)**

- **NFR-R1:** Any node transition recoverable from checkpoint after crash, restart, power loss.
- **NFR-R2:** All specialist `act` nodes are idempotent.
- **NFR-R3:** All gate `interrupt()` nodes are re-enterable — same DecisionCard payload on re-entry.
- **NFR-R4:** Learning-event ledger emission is idempotent — re-emission at same node-thread-attempt key is a no-op.
- **NFR-R5:** Availability target is **operator-presence availability**. No 24/7 uptime.
- **NFR-R6:** A trial run can survive ≥48 hours of pause and resume correctly from last checkpoint.
- **NFR-R7:** Tolerate clone-local corruption without losing trial state — Postgres is durable source.

**Reproducibility (5, domain-critical)**

- **NFR-X1:** Closed trial run's pack output is byte-for-byte reproducible from final checkpoint.
- **NFR-X2:** Graph versions frozen on first tracked-trial close; structural changes bump version.
- **NFR-X3:** Sanctum content at trial-run time snapshotted into checkpoint (or referenced by content hash) so replay reproduces identical specialist behavior.
- **NFR-X4:** Model selections preserved in checkpoint (including runtime overrides and auto-select fallback trails).
- **NFR-X5:** OpenAI temperature > 0 non-determinism is a known variance source; replay regression tolerates documented variance bands per node.

**Maintainability (8, load-bearing for developer-tool)**

- **NFR-M1:** Every specialist passes scaffold-conformance test — no specialist ships with divergent internal shape.
- **NFR-M2:** Every specialist's `model_config.yaml` lintable at graph-compile time.
- **NFR-M3:** Four-layer test strategy (unit / integration / end-to-end / trial-replay regression) holds through migration.
- **NFR-M4:** K-floor story-cycle discipline holds — target 1.2–1.5× K test coverage per story, not 5×.
- **NFR-M5:** Pydantic-v2 four-file-lockstep discipline holds for every schema-shape change.
- **NFR-M6:** Specialist-anti-patterns catalog updated during Slab 2 as anti-patterns are encountered (living, not retrospective).
- **NFR-M7:** Migration guide kept current — each slab closeout updates relevant sections before Milestone-approval.
- **NFR-M8:** `docs/dev-guide/` covers every extension point a future dev/dev-agent will need.

**Observability (4)**

- **NFR-O1:** LangSmith captures every node execution with 100% trace coverage at single-operator volume.
- **NFR-O2:** Economics telemetry queryable per trial run without trace-replay.
- **NFR-O3:** Sanctum invalidation events surfaced as warnings (not failures) with link to suspected invalidating commit.
- **NFR-O4:** Model-selection resolution trails present in every LLM-invoking node's LangSmith span.

**Total NFRs: 43** (P:6 + S:7 + I:6 + R:7 + X:5 + M:8 + O:4). Count confirmed by grep of PRD source.

> ⚠️ **DRIFT FINDING #1 — NFR count mismatch.** PRD frontmatter and session notes report **"38 NFRs"** (see `next-session-start-here.md:10`, `bmm-workflow-status.yaml::nonfunctional_requirements: 38`). The body enumerates **43**. Reconciliation needed before architecture opens — either correct the frontmatter/session notes to 43, or explicitly mark which 5 NFRs are aspirational vs. binding.

### Additional Requirements

**Locked Decisions (assumptions, not open questions):**

1. Stage-2 runtime independence — persistent local LangGraph service; IDE as client.
2. Bounded big-bang in clone — `dev/langchain-langgraph-foundation`; primary carries production; backports stop after Slab 1 opens.
3. Reject-the-LangChain-cage — 8 operating rules + 5 anti-patterns codified before Slab 2 opens.
4. HIL operator + Marcus-as-SPOT preserved indefinitely — gate-payload curation reduces burden, never authority.
5. Specialist scaffold + sanctum-backed expertise stack as plug-and-play architecture.

**Provider Lock (2026-04-22):** OpenAI API. Anthropic middleware out of scope. `ChatOpenAI` wrapped in thin adapter for future provider swap as contained change.

**15 Load-Bearing Substrate Invariants (drop-rate budget zero):** Marcus SPOT; Marcus stateless-cold-start; 15-step manifest as deterministic neck; HIL-paused gates; learning events at G2C/G3/G4; three-layer code review; K-floor test discipline; Pydantic-v2 four-file-lockstep; learning-ledger as side-effect; frozen-at-ship pack discipline; K-floor story-cycle discipline; Marcus-first orchestration semantics; specialist registry authoritative; deferred-inventory continuity; Cora/Marcus lane separation.

**Constraints:** Self-hosted OSS LangGraph; Postgres 15+; Python 3.12+; Pydantic v2; `uv` preferred. MCP primary bridge; FastAPI localhost-only escape hatch. `langserve`, LangChain high-level agents, Celery/Ray/Dask explicitly out of scope.

**Out-of-Scope (explicit):** Multi-operator concurrency; remote deployment; HA clustering/failover; SOC 2 / ISO 27001; WCAG / Section 508; GDPR/HIPAA/FERPA/COPPA; sub-second LLM latency.

### PRD Completeness Assessment (Initial — full findings in Step 5)

**Strengths:**
- Every FR has a slab assignment (capability-to-slab matrix closes the topology).
- Every FR is testable and WHAT-not-HOW.
- Five measurable milestones M1–M5 with explicit Go / Revise / Halt verdicts and evidence requirements.
- Six innovation patterns each have validation approach + risk mitigation.
- 15 substrate invariants explicitly enumerated with drop-rate budget = 0.
- Provider decision fully scoped; tier palette specified; auto-select cascade deterministic + auditable.
- Timeline + cost projections include deviation triggers (>20% replan, >50% go/no-go).

**Concerns to validate in Step 5:**
- **NFR count drift** (38 declared vs. 43 enumerated) — see finding #1.
- **FR8 ↔ FR38 overlap** — "manifest as compile-time topology source" appears twice (Runtime vs. Lockstep). Acceptance may differ by slab — verify.
- **FR45 ↔ invariant #5 ↔ invariant #9** — three references to "ledger emit at G2C/G3/G4" — verify test-ability split.
- **FR13 ↔ FR14** — generator vs. conformance test — distinct acceptance needed.
- **Invariant #7 (K-floor test discipline) ↔ invariant #11 (K-floor story-cycle discipline)** — named similarly; confirm no downstream traceability duplication.
- **Epic seed:** PRD does not pre-shape epics. For a 65-FR / 9-capability / 5-slab scope, downstream epic breakdown must decide: capability-areas or slabs as primary epic partition? Architecture doc should take a position before epics can be authored.

## Step 3 — Coverage Validation (adapted for pre-architecture scope)

**Adaptation rationale:** migration epics do not exist yet. Instead of FR ↔ epic traceability, this step validates two coverage surfaces the PRD itself carries:

1. **Slab coverage** — PRD §Capability-to-Slab Mapping table.
2. **Milestone evidence coverage** — M1–M5 evidence requirements (which FRs land as named acceptance criteria at an operator-approvable gate).

Gaps in surface (1) = FRs with no implementation lane — architectural orphans.
Gaps in surface (2) = FRs nominally slab-mapped but with no named acceptance evidence — latent under-delivery risk.

### Coverage Matrix — Slab Mapping (PRD §Capability-to-Slab Mapping)

| FR Range | Capability Area | Primary Slab(s) | Slab-Mapped? |
|---|---|---|---|
| FR1–FR8 | Runtime Platform | Slab 1 | ✓ |
| FR9–FR16 | Specialist Framework | Slab 2 | ✓ |
| FR17–FR25 | Model Selection | Slabs 1–2 | ✓ |
| FR26–FR30 | Marcus Orchestration | Slab 3 | ✓ |
| FR31–FR37 | Gates & HIL | Slab 3 | ✓ |
| FR38–FR45 | Pipeline Lockstep & Governance | Slab 4 | ✓ |
| FR46–FR53 | Trial-Run Discipline | Slab 5 | ✓ |
| FR54–FR59 | Economics & Observability | Slabs 1, 5 | ✓ |
| FR60–FR65 | Migration Hygiene & Rollback | Slab 5 | ✓ |

**Slab-coverage result: 65 / 65 FRs have a slab assignment (100%).** No FR is orphaned at the Slab level.

### Coverage Matrix — M1–M5 Milestone Evidence

For each FR, checked whether any M1–M5 "Required evidence" bullet explicitly names the capability or a proxy artifact that would unambiguously validate it.

| FR | Capability (abbrev.) | Milestone | Explicit? |
|---|---|---|---|
| FR1 | LangGraph persistent service | M1 | ✓ (empty graph §01→§15 via CLI) |
| FR2 | Concurrent MCP + FastAPI clients | — | **⚠ implicit only** |
| FR3 | Postgres checkpointing | M1 | ✓ (retention/cleanup demonstrable) |
| FR4 | Thread resume after IDE disconnect | M1 | ⚠ implicit (Journey 1 validates; no M-bullet names it) |
| FR5 | Checkpoint retention policy | M1 | ✓ |
| FR6 | LangSmith per-node traces | M1 | ✓ (trace shows per-node execution + token cost) |
| FR7 | Python entry-point (`app.runtime_server`) | M1 | ✓ (smoke_test passes) |
| FR8 | Manifest as compile-time topology | M1 | ✓ (empty manifest-loaded graph) |
| FR9 | 9-node scaffold | M2 | ✓ (scaffold-conformance tests green) |
| FR10 | Sanctum directory structure | M2 | ⚠ implicit via FR14 conformance test |
| FR11 | Sacred-Truth cold-read discipline | M2 | ⚠ implicit via FR14 |
| FR12 | 9-layer expertise stack | M2 | ⚠ implicit via FR14 |
| FR13 | `bmad-create-specialist` generator | M2 | ✓ (generator works end-to-end + Wondercraft) |
| FR14 | Scaffold-conformance test | M2 | ✓ (all 17 migrated + tests green) |
| FR15 | Subgraph isolated state | M2 | ⚠ implicit via FR14 |
| FR16 | MCP tool exposure at L7 | M2 | ⚠ implicit via Wondercraft |
| FR17 | Three-level model cascade | M1 | ✓ (selector unit tests green) |
| FR18 | `model_config.yaml` declaration | M1/M2 | ✓ (NFR-M2 lintable at compile time) |
| FR19 | Runtime model override | M3 | ✓ (runtime model-override surface functional) |
| FR20 | Marcus locked to reasoning tier | M3 | ✓ (explicit M3 bullet) |
| FR21 | Deterministic auto-select function | M1 | ✓ (selector unit tests) |
| FR22 | LangSmith resolution trail logging | M1 | ⚠ partially explicit (FR22 not named in M evidence; NFR-O4 names it) |
| FR23 | Model registry versioning | M1 | ⚠ implicit via "model registry + adapter + selector" bullet |
| FR24 | Cache-invalidation warning UX | — | **⚠ NO MILESTONE EVIDENCE** |
| FR25 | Provider adapter isolation | M1 | ⚠ implicit via adapter bullet |
| FR26 | Marcus SPOT | M3 | ✓ (Marcus supervisor end-to-end) |
| FR27 | Plan-and-Execute / ReAct preset switching | — | **⚠ NO MILESTONE EVIDENCE** |
| FR28 | Manifest-driven routing (not inline reasoning) | M3 | ⚠ implicit |
| FR29 | Registry-driven delegation | M3 | ⚠ implicit |
| FR30 | Marcus sanctum cold-read on session open | M3 | ⚠ implicit |
| FR31 | Gates as `interrupt()` nodes | M3 | ✓ (DecisionCard at every gate) |
| FR32 | DecisionCard payload structure | M3 | ✓ (consumable by operator) |
| FR33 | Verdict emission via CLI/MCP/FastAPI | M3 | ✓ (approve/edit/reject via CLI) |
| FR34 | No auto-approve / no timeout override | — | **⚠ NO MILESTONE EVIDENCE — CRITICAL HIL INVARIANT** |
| FR35 | Resume with verdict payload propagation | M3 | ⚠ implicit |
| FR36 | Gate count 1:1 with manifest (auditable) | — | **⚠ NO MILESTONE EVIDENCE — audit capability not acceptance-gated** |
| FR37 | Reject-rate KPI tracking | — | **⚠ NO MILESTONE EVIDENCE — KPI promised but not gated** |
| FR38 | Manifest as compile-time topology source | M4 | ✓ (graph-compile-time lockstep demo) |
| FR39 | CI graph-compile-time lockstep failure | M4 | ✓ (drifted PR rejected at CI) |
| FR40 | Cora dev-graph sibling + namespace isolation | M4 | ✓ |
| FR41 | Party-mode-as-`interrupt()` | M4 | ✓ (≥1 real story gate) |
| FR42 | Code-review consumes LangSmith traces | — | **⚠ NO MILESTONE EVIDENCE** |
| FR43 | Frozen graph versions | M4 | ✓ (ceremony codified) |
| FR44 | Tier-1/2/3 graph version bumps | M4 | ⚠ implicit via ceremony doc |
| FR45 | Learning-event ledger at G2C/G3/G4 | M4 | ✓ (events captured in tracked run) |
| FR46 | Trial start with bundle + preset | M3/M5 | ⚠ implicit via §01→§15 bullet |
| FR47 | Pause via state serialization | M5 | ⚠ implicit (Journey 1; no M-bullet names it) |
| FR48 | Resume from different IDE | M5 | ⚠ implicit (Journey 1) |
| FR49 | Fork from checkpoint | M5 | ✓ (Fork UX usable CLI minimum) |
| FR50 | Byte-for-byte replay | M5 | ✓ (trial-replay regression) |
| FR51 | Trial-replay regression test suite | M5 | ✓ (100% coverage of closed runs) |
| FR52 | Head-to-head parity with primary repo | M5 | ✓ (explicit M5 bullet + operator sign-off) |
| FR53 | Read-only state.inspect | — | **⚠ NO MILESTONE EVIDENCE** |
| FR54 | Cache hit rate measurement | M1/M5 | ✓ (≥60% M1, ≥80% M5) |
| FR55 | Token cost per-trial breakdown | M5 | ✓ (cost-projection with tier + cache breakdown) |
| FR56 | Post-migration vs. baseline comparison | M5 | ✓ (≥50% reduction bar) |
| FR57 | Telemetry CLI (MVP) + dashboard (post-MVP) | M5 | ⚠ partial — CLI only; dashboard deferred is consistent with scope |
| FR58 | LangSmith traceability per LLM invocation | M1 | ✓ (LangSmith trace evidence) |
| FR59 | Sanctum invalidation hook | M5 | ✓ (hook functional) |
| FR60 | Backport suspension policy | — | process/policy item, not code acceptance |
| FR61 | Forward-port playbook | M5 | ✓ (migration guide §8) |
| FR62 | Rollback plan | M5 | ✓ (migration guide §10) |
| FR63 | 15-invariant audit matrix | M5 | ✓ (named preserving pattern per invariant) |
| FR64 | Specialist-anti-patterns catalog ≥5 | M2/M5 | ✓ (both milestones reference) |
| FR65 | Migration guide 11 sections | M5 | ✓ |

### Coverage Statistics

- **Total PRD FRs:** 65
- **Slab-mapped (100% coverage):** 65 / 65
- **Explicit milestone evidence:** 35 / 65 (53.8%)
- **Implicit milestone coverage (⚠, reasonable inference but no named bullet):** 23 / 65 (35.4%)
- **No milestone evidence at all (⚠⚠, gap):** 7 / 65 (10.8%)

### Missing / Weak Coverage (Gap Finding #2)

> ⚠️ **DRIFT FINDING #2 — FRs slab-mapped but without named M1–M5 evidence criteria.** These seven FRs risk silent under-delivery because no operator-approvable gate explicitly tests them. Architecture must either (a) add named acceptance criteria when architecture opens, (b) fold these into their containing Slab's milestone evidence via PRD amendment, or (c) mark them as validated-by-proxy (naming the specific proxy criterion and rationale).

**Critical**

- **FR24 — Cache-invalidation warning on runtime override.** No milestone names this UX. Risk: operator flips a model mid-trial, tanks cache hit rate, discovers it only in the economics dashboard. Recommend: add to M3 evidence ("runtime model-override surface functional AND warns operator of cache-invalidation impact before applying").
- **FR34 — No auto-approve / no timeout override.** **CRITICAL HIL INVARIANT** (derives from locked decision 4 + substrate invariant #4). No milestone evidence names this. Risk: a future sprint under pressure adds a "1-hour no-response auto-reject" and violates the invariant invisibly. Recommend: add to M3 evidence ("DecisionCard acceptance includes assertion that no gate auto-progresses on any timer / default-verdict condition").
- **FR36 — Gate count 1:1 with manifest, auditable.** No milestone evidence. The PRD Journey 1 says "gate inventory audit across the new tracked trial run matches the manifest 1:1" but M3/M5 doesn't codify it. Recommend: add to M3 or M5 ("gate inventory audit report in trial-close artifacts").
- **FR37 — Reject-rate per gate as measurable KPI.** PRD Success Criterion 3 promises this KPI; no M evidence gates it. Recommend: add to M5 economics surface ("reject-rate per gate reported alongside cache hit rate + token cost").

**Important**

- **FR27 — Plan-and-Execute / ReAct preset switching.** PRD names both but M3 evidence only says "Marcus as supervisor" without preset-switching validation. Recommend: add to M3 ("trial run under `production` preset confirms Plan-and-Execute; trial run under `explore` preset confirms ReAct").
- **FR42 — Code-review consumes traces alongside diffs.** M4 names party-mode-as-interrupt but not the trace-first review workflow Journey 4 validates. Recommend: add to M4 ("at least one bmad-code-review gate review cites a LangSmith trace link as evidence").
- **FR53 — Read-only `state.inspect`.** No milestone names it. Used in the fork / debug workflows. Recommend: add to M5 ("MCP `state.inspect` tool operator-usable; read-only verified").

### Reverse Check — M Evidence Without FR Backing

Every M1–M5 evidence bullet maps to ≥1 FR (or to an NFR, e.g., NFR-M3 four-layer test strategy, NFR-M5 four-file-lockstep). **No orphan M-evidence found.** Reverse-traceability clean.

## Step 4 — UX Alignment Assessment

### UX Document Status

**Not found** — and **correctly marked not-applicable** in `bmm-workflow-status.yaml::ux_design` with note *"Primary interface is conversational — no traditional UX design needed."*

The PRD explicitly classifies the project as `developer_tool` and names the "Sections Intentionally Skipped" list as including "Visual design / brand styling" and "User journeys for end-users-of-the-SDK" (§Developer Tool — Specific Requirements).

### UX-Adjacent Decisions Embedded in FRs (implied-UX check)

Even with no separate UX doc, the PRD does carry UX-surface decisions that architecture must realize. These are **correctly embedded as FRs**, not orphaned:

| UX Surface | FR | PRD Treatment |
|---|---|---|
| **DecisionCard rendering & verdict capture** | FR32, FR33 | CLI primary, IDE (MCP) integration, FastAPI escape-hatch — all three transports required |
| **Cache-invalidation warning** | FR24 | Explicit UX bullet; no milestone evidence (see Drift Finding #2) |
| **Fork UX** | FR49 | CLI minimum (MVP); IDE-integrated deferred to Growth |
| **Replay / pause / resume UX** | FR47, FR48, FR50 | Operator-facing via IDE + CLI; Journey 1 & 2 validate |
| **Economics dashboard** | FR57 | CLI dump (MVP); web UI post-MVP |
| **State inspection** | FR53 | Read-only MCP tool; no milestone evidence (see Drift Finding #2) |
| **Runtime model-override UX** | FR19, FR24 | Operator-visible at trial-run start / gate resume / fork; cache-impact warning embedded |

### Alignment Issues

**None at the PRD level** — UX-surface decisions are scoped, embedded in FRs, and ranged across MVP vs. post-MVP. No hidden UI commitment.

**⚠ ALIGNMENT CONCERN FOR ARCHITECTURE:** Because UX is not a separate artifact, architecture must not silently introduce UX surface the PRD didn't scope. Architecture should either:
- State explicitly which UX-surface FRs it implements vs. defers, or
- Produce a small "operator-surface contract" addendum (CLI commands + MCP tool surface + FastAPI endpoints + DecisionCard shape) as a §Developer-tool-UX section.

This is not a gap in the PRD; it's a reminder for the downstream architecture workflow. Capturing here so it lands on the architecture author's desk at T1.

### Warnings

- No true UX-doc warning. Project type justifies absence.
- UX-surface FRs (FR24, FR53) also carry gap-finding #2 overlap (no milestone evidence). Double-flagged — fixing milestone evidence also closes the UX-validation-path gap for these.

## Step 5 — Slab Quality Review (adapted for pre-epic scope)

**Adaptation rationale:** migration epics don't exist. Applied the same best-practice heuristics (user value / independence / no-forward-deps / brownfield fit / dev-ramp-first / timing / sizing) against the **five slabs as proto-epic containers**. Findings feed architecture authoring and downstream epic decomposition.

### Compliance Checklist (per slab)

| Heuristic | Slab 1 | Slab 2 | Slab 3 | Slab 4 | Slab 5 |
|---|---|---|---|---|---|
| Delivers user-visible value | 🟡 borderline | ✓ | ✓ | 🟡 governance-visible | ✓ |
| Independence (no forward-dep on N+1) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Brownfield integration named | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dev-ramp / setup scoped | ✓ (Slab 1 owns it) | n/a | n/a | n/a | n/a |
| Infrastructure-timing appropriate | ✓ | ✓ | ✓ | ✓ | ✓ |
| Sizing reasonable for one epic | ✓ (2–3 wk) | ⚠ oversized | ✓ (2 wk) | ✓ (2–3 wk) | ⚠ bundled |
| FR → milestone evidence named | ✓ mostly | ✓ mostly | ⚠ gaps | ⚠ gaps | ✓ mostly |

Aggregate: **no 🔴 critical violations** at the slab level. Four 🟡 concerns worth surfacing to architecture; none block readiness.

### 🟠 Major Concerns (feed architecture T1 queue)

> ⚠️ **FINDING #3 — Slab 2 is oversized for one-epic decomposition.**
>
> Slab 2 is the capacity-heavy pivot (4–6 weeks wall-clock, PRD §Timeline Projection). It bundles: scaffold hardening + `bmad-create-specialist` generator + 17 specialist migrations + Wondercraft pilot + anti-patterns catalog harvest. A one-slab-per-epic decomposition will produce an oversized epic that violates BMAD sizing discipline (target epic ≈ 2–4 weeks, not 4–6).
>
> **Recommendation for downstream `bmad-create-epics-and-stories`:** decompose Slab 2 into at minimum two epics:
> - (a) *Scaffold + Generator + Anti-Patterns* — the substrate for plug-and-play (weeks 1–2 of Slab 2).
> - (b) *17-specialist migration tranche + Wondercraft pilot* — the mass-migration + validation (weeks 3–6).
> - Optionally (c) *Anti-Patterns Catalog Publication* as a closing story that harvests the catalog across both (a) and (b).

> ⚠️ **FINDING #4 — Slab 5 bundles parity acceptance and polish; split advised.**
>
> Slab 5 mixes: (a) the **go/no-go acceptance bar** — trial-replay regression, head-to-head parity, cost validation, 15-invariant audit — and (b) **polish** — fork UX, dashboard CLI, sanctum invalidation hook, migration guide authorship. These are distinct risk profiles.
>
> **Recommendation:** Architecture and epic breakdown should split into Slab 5a (Acceptance) and Slab 5b (Polish). Slab 5a is the true gate; Slab 5b is cuttable under pressure (per PRD's own MVP cut-candidates table) but cannot be cut before Slab 5a closes.

> ⚠️ **FINDING #5 — Cross-slab deliverables have no named per-slab owner.**
>
> Three load-bearing deliverables span all five slabs but are only gated at M5:
> - **FR63 — 15-invariant audit matrix.** Every slab must produce its invariant-preservation artifacts, but the audit matrix itself is shipped only at M5. Risk: an invariant is silently dropped in Slab 2 or 3 and only surfaces at M5 audit.
> - **FR64 — Specialist anti-patterns catalog.** Harvested during Slab 2 (per M2 evidence), but PRD commits to "living catalog" (NFR-M6). Who owns updates during Slabs 3–5?
> - **FR65 — Migration guide.** NFR-M7 commits to "kept current — each slab closeout updates relevant sections." But M1/M2/M3/M4 evidence doesn't name migration-guide updates. Only M5 ships the finished 11-section guide.
>
> **Recommendation:** Architecture names a per-slab "governance artifact" sub-epic (or lightweight story) that updates these three cross-slab deliverables at each Slab close. Prevents end-of-migration scramble and drift.

### 🟡 Minor Concerns

- **Slab 1 user-value framing is technical-milestone-shaped.** "Empty manifest-loaded graph completes §01→§15" is real operator-exercisable capability, but the slab name "Substrate" reads as a classic "setup infrastructure" epic. This is a framing concern only — the acceptance evidence IS user-exercisable. No action needed.

- **Slab 4 governance-value is indirect.** CI-enforced Pipeline Lockstep is operator-value ("drift-impossible-to-merge") but requires the operator to value governance guarantees. Confirm with operator that governance delivery counts as a Slab-sized unit of work (recommend: party-mode the Slab-4 scope pre-architecture).

- **Wondercraft pilot double-duty risk.** The Wondercraft pilot validates (i) the `bmad-create-specialist` generator and (ii) the <1-dev-day innovation claim simultaneously. If the scaffold isn't stable when Wondercraft begins, the <1-dev-day measurement becomes noisy. **Recommendation:** architecture should explicitly gate Wondercraft behind scaffold-stability (e.g., "scaffold-conformance green on ≥5 migrated specialists" before Wondercraft opens).

- **Model-registry mid-migration bump.** FR23 says Tier-1 registry updates proceed under dev-agent authority. Over 12–16 weeks, ≥1 OpenAI model release is likely. PRD doesn't name which slab or artifact owns a mid-migration registry bump. Minor today; flag for architecture.

### Dependency Analysis (proto-epic graph)

Slab ordering is content-driven, not artificial:
- Slab 2 depends on Slab 1 (scaffold uses runtime + Postgres + OpenAI adapter)
- Slab 3 depends on Slab 2 (Marcus routes to scaffold-conformant specialists)
- Slab 4 depends on Slab 3 (party-mode-as-`interrupt()` uses the interrupt pattern Slab 3 establishes)
- Slab 5 depends on Slab 4 (frozen-graph-version + learning-ledger are needed for replay + economics)

**No forward dependencies.** No circular dependencies. Sequencing is justified.

### Brownfield Fit

PRD explicitly integrates with existing systems: Texas Shape 3-Disciplined retrieval contract (NFR-I5), sanctum directories, specialist APIs (Descript/ElevenLabs/Gamma), Pydantic four-file-lockstep discipline, deferred-inventory governance, BMAD sprint governance, existing `bmad-agent-builder` (retained for non-runtime agents). **Brownfield fit strong.** Migration does not re-design those surfaces; it wires them in.

### Starter-Template / Dev-Ramp

Slab 1 owns the dev-ramp (Installation Methods §1-10 + `docs/dev-guide/langgraph-runtime-setup.md`). Empty-manifest-loaded-graph smoke test is the canonical Slab 1 "day one" exercise. Architecture should explicitly name the "Slab 1 Story 1: runtime setup + empty-graph smoke" as the first story when epic decomposition opens.

## Step 6 — Summary and Recommendations

### Overall Readiness Status

**READY-WITH-MINOR-AMENDMENTS** to open architecture (`bmad-create-architecture`).

The PRD is structurally complete, internally self-consistent on all load-bearing surfaces, and carries enough scope discipline (locked decisions, slab-to-FR mapping, milestone evidence, invariant audit, timeline + cost deviation triggers) to anchor architecture authoring. The five findings below are **pre-architecture amendments**, not blockers — architecture can start with them staged; they become architecture's T1-input queue.

### Findings Summary (5 total across 5 categories)

| # | Severity | Category | Finding | Remediation |
|---|---|---|---|---|
| 1 | 🟡 Minor | NFR count drift | Frontmatter declares 38 NFRs; body enumerates 43 | Update frontmatter + `bmm-workflow-status.yaml` to 43, or explicitly scope 5 NFRs as aspirational |
| 2 | 🟠 Major | Milestone evidence gaps | 7 FRs slab-mapped but no M1–M5 evidence (FR24, FR27, FR34, FR36, FR37, FR42, FR53); FR34 is a CRITICAL HIL invariant | Add named evidence bullets to M3/M4/M5 per Drift Finding #2 rec list |
| 3 | 🟠 Major | Slab 2 oversized | 4–6 week Slab 2 bundles scaffold + generator + 17 migrations + Wondercraft + catalog — oversized for one epic | Downstream epic decomposition splits Slab 2 into ≥2 epics (scaffold-generator vs. 17-specialist-tranche + Wondercraft) |
| 4 | 🟠 Major | Slab 5 bundled | Slab 5 mixes go/no-go acceptance with polish — distinct risk profiles | Split into Slab 5a (Acceptance) + Slab 5b (Polish); 5a gates the ship decision, 5b is cuttable |
| 5 | 🟠 Major | Cross-slab ownership | FR63 invariant-audit, FR64 anti-patterns catalog, FR65 migration guide span all slabs but only gate at M5 | Architecture names per-slab "governance artifact" sub-epic/story that updates the three cross-slab deliverables at each Slab close |

### Critical Issues Requiring Immediate Action (before architecture opens)

**Only Finding #2-FR34 rises to "critical"**: the HIL invariant "no auto-approve / no timeout override" has no milestone evidence. This is a load-bearing property of Decision 4 (HIL + SPOT preserved) and Invariant #4 (HIL-paused gates). It could be silently compromised in a future sprint without tripping a gate.

**Recommended amendment before architecture opens:** append to PRD §M3 Required evidence:
> "DecisionCard acceptance test: a trial run at a gate confirms that no verdict is auto-generated by any timer, default-verdict, or idle-timeout condition — operator verdict is the sole path past the gate. Assertion verified in integration test + in a tracked trial run log."

All other findings (#1, #3, #4, #5, and the rest of #2) are **non-blocking** — architecture can proceed and absorb these as T1 considerations.

### Recommended Next Steps

1. **Lightweight PRD amendment** (≈30 min) — add FR34 acceptance bullet to M3 (see above). Optionally add the six other milestone-evidence bullets from Drift Finding #2. Optionally reconcile NFR count to 43 in frontmatter + `bmm-workflow-status.yaml`. Alternative: skip the amendment and treat these as architecture-author input at T1.

2. **Stage architecture-author T1 brief** (the finding list above) — either inline in this readiness report (already here) or as a separate `architecture-author-t1-inputs.md` for the architect to read cold.

3. **Open architecture** — run `bmad-create-architecture` anchored to the 65 FRs + 43 NFRs. Architecture should explicitly:
   - Address the slab sizing question (Finding #3) — confirm or revise the one-slab-one-epic assumption
   - Address the Slab 5 split (Finding #4) — commit architecture to a 5a/5b division or reject the split with rationale
   - Name cross-slab deliverable owners (Finding #5) — produce a per-slab governance-artifact plan
   - Produce an "operator-surface contract" §Developer-tool-UX (per Step 4 alignment concern)
   - Name a mid-migration model-registry-bump handling procedure (Step 5 minor concern)

4. **Optional: party-mode review of PRD-post-amendment** (path c from `next-session-start-here.md`) — if architecture author wants a second pass before T1. Recommended for the Slab 2 oversized-epic and Slab 5 bundling questions; BMAD personas (Winston, Murat, Paige) can stress-test the decomposition before architecture commits.

### Final Note

This assessment identified **5 findings across 5 categories** in the migration PRD. None block architecture from opening. One (Finding #2 FR34) warrants a ≈30-min PRD amendment before architecture opens; the others are architecture-author T1 inputs.

**Overall:** PRD is well-anchored, brownfield integration is strong, invariants are explicit, and scope discipline holds. Architecture can proceed.

**Assessor:** Claude (Opus 4.7, 1M context), operating under BMAD implementation-readiness workflow (`.claude/skills/bmad-check-implementation-readiness/`).
**Date:** 2026-04-22
**Workflow:** 6 steps executed; all findings documented; no step skipped.
