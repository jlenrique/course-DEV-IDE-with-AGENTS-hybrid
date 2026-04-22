---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
status: 'complete'
completed: '2026-04-22'
provider_decision: 'OpenAI API (not Anthropic) — locked 2026-04-22 per operator directive. AnthropicPromptCachingMiddleware out of scope. Caching via OpenAI automatic prompt cache (~50% discount on cached input tokens, ≥1024-token prefix eligible). Marcus locked to best reasoning model; specialists default to gpt-4.1 family (1M context, cost-efficient); three-level resolution cascade (runtime override > per-agent config > auto-select).'
classification:
  projectType: developer_tool
  domain: edtech
  complexity: high
  projectContext: brownfield
  notes: 'True shape is internal multi-agent orchestration platform (Marcus + specialist subgraphs). Migration target is re-platform of the orchestration spine onto LangChain + LangGraph. Complexity is high from invariant surface (Pipeline Lockstep, HIL gates, Pydantic-v2 schema-shape discipline, party-mode/code-review gates, deferred-inventory governance, Marcus-first SPOT), not regulatory load.'
inputDocuments:
  - _bmad-output/planning-artifacts/research/technical-langchain-langgraph-migration-research-2026-04-21.md
  - docs/project-context.md
workflowType: 'prd'
outputFile: _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md
project_name: course-DEV-IDE-with-AGENTS
subject: 'LangChain + LangGraph migration of APP orchestration pipeline'
primary_research: _bmad-output/planning-artifacts/research/technical-langchain-langgraph-migration-research-2026-04-21.md
user_name: 'Juanl'
date: '2026-04-22'
documentCounts:
  briefs: 0
  research: 1
  brainstorming: 0
  projectDocs: 1
scope_directives:
  - Lock the five decisions from the research doc as assumptions
  - Formalize the five-slab structure
  - Scope the LangChain/LangGraph migration
  - Define operator-approvable milestones
  - Produce cost/risk projections needed for go/no-go
---

# Product Requirements Document - course-DEV-IDE-with-AGENTS

**Subject:** LangChain + LangGraph Migration of the APP Orchestration Pipeline
**Author:** Juanl
**Date:** 2026-04-22
**Primary Input:** `_bmad-output/planning-artifacts/research/technical-langchain-langgraph-migration-research-2026-04-21.md`

## Table of Contents

1. [Executive Summary](#executive-summary) — vision, differentiator, five locked decisions
2. [Project Classification](#project-classification) — type, domain, complexity, context
3. [Success Criteria](#success-criteria) — user / business / technical success measures + go/no-go outcomes
4. [Product Scope (MVP / Growth / Vision)](#product-scope) — five-slab MVP structure and post-MVP roadmap
5. [User Journeys](#user-journeys) — operator, specialist developer, BMAD reviewer, CI governance
6. [Domain-Specific Requirements](#domain-specific-requirements) — 15 load-bearing invariants + governance inheritance
7. [Innovation & Novel Patterns](#innovation--novel-patterns) — six novel architectural patterns + validation approach
8. [Developer Tool / Internal Orchestration Platform — Specific Requirements](#developer-tool--internal-orchestration-platform--specific-requirements) — OpenAI provider, three-level model selection, language/framework matrix, API surface
9. [Project Scoping & Phased Development](#project-scoping--phased-development) — operator-approvable milestones (M1–M5), timeline + cost projections for go/no-go
10. [Functional Requirements](#functional-requirements) — 65 FRs across nine capability areas (binding contract)
11. [Non-Functional Requirements](#non-functional-requirements) — performance, security, integration, reliability, reproducibility, maintainability, observability

## Executive Summary

This PRD scopes the re-platform migration of the **course-DEV-IDE-with-AGENTS APP** — a Marcus-orchestrated 15-step production pipeline with 17 specialist agents, Pipeline Lockstep regime, HIL operator gates, and Pydantic-v2 schema-shape discipline — onto a **self-hosted LangChain + LangGraph** runtime. The APP just completed its first end-to-end tracked trial run (`C1-M1-PRES-20260419B §01→§15`, closed 2026-04-19). Its current shape is empirically validated; its current operating constraint is that the Claude Code conversation **is** the runtime. The migration exists to relieve that constraint without softening any of the load-bearing invariants that make the APP work.

The migration follows a **bounded big-bang** shape over **12–16 weeks** in the `dev/langchain-langgraph-foundation` clone while the primary repo carries production and stays the frozen reference. The clone is "broken end-to-end" as a managed state; backports stop early; forward-ports happen at migration close. Five architectural slabs are delivered strictly in sequence: (1) Substrate — runtime, Postgres checkpointing, OpenAI automatic prompt caching, LangSmith, FastAPI+MCP bridge, `app/models/` (registry + adapter + three-level selector), empty manifest-loaded graph end-to-end; (2) Specialists — a 9-node scaffold plus `bmad-create-specialist` generator drives 17 specialist migrations and a Wondercraft pilot; (3) Marcus Supervisor + Routing + DecisionCards; (4) Pipeline Lockstep CI enforcement, Cora dev-graph, party-mode-as-`interrupt()`, frozen-graph-version ceremony, learning-event ledger; (5) Trial-Run Discipline + Replay UX + observability polish, closing with a new tracked trial run at parity-or-better against the primary repo.

Five foundational decisions are **locked as PRD assumptions, not open questions**: Stage-2 runtime independence as the architectural target (persistent local LangGraph service, IDE as client); bounded big-bang in the clone; reject-the-LangChain-cage operating principles (eight rules + five anti-patterns codified to protect agent intelligence from graph determinism); HIL operator + Marcus-as-SPOT preserved indefinitely (gate-payload curation reduces operator burden over time, never operator authority); specialist scaffold + sanctum-backed expertise stack as plug-and-play architecture. The 12 architectural patterns mapped in research map 1:1 onto the 15 load-bearing substrate invariants; no invariant is dropped.

### What Makes This Special

**Plug-and-play specialist architecture as a permanent capability, not a migration artifact.** The 9-node scaffold, the L0–L8 sanctum-backed expertise stack, and the `bmad-create-specialist` generator together compress new-specialist time-to-deploy from *weeks* under the current approach to **<1 dev-day** once the scaffold hardens. New media/service specialists (Wondercraft, Canvas, Qualtrics, and whatever comes next) drop in at the speed of API contracts changing.

**"Reject the LangChain cage" is an architectural principle enforced at the node level.** Eight operating rules — probabilistic-first nodes, routing-edges-decide-who-not-what, schema-as-boundary-not-corset, long-context-over-compression, specialists-as-subgraphs, narrow-deterministic-glue, model-tier-follows-reasoning, replay-enables-exploration — plus five named anti-patterns keep probabilistic intelligence intact inside each specialist's `reason` node while the graph absorbs structure only at boundaries.

**Operator authority is preserved and amplified, not traded away.** Every gate becomes a checkpointed `interrupt()` node consuming a curated **DecisionCard** (drafted specialist proposal + evidence + risks + approve/edit/reject verbs). HIL+SPOT stays indefinite. Fork-from-checkpoint enables what-if exploration that doesn't exist today. Gate-payload curation reduces cognitive load per decision without removing decision authority.

**Reproducibility becomes architectural, not procedural.** Frozen-graph-version + checkpointed trial runs + replay-from-checkpoint mean every closed trial is byte-for-byte reproducible. `runtime/graphs/v42/`, `v43/` siblings preserve audit reproducibility across pack-version bumps — a direct mapping of the existing frozen-at-ship pack discipline onto the new runtime.

**Token economics that scale through compound levers.** The APP is powered by the OpenAI API (locked decision, 2026-04-22). OpenAI automatic prompt caching on the stable sanctum/persona/references prefix delivers ~50% discount on cached input tokens; composed with three-level model-tier routing (Marcus locked to best OpenAI reasoning model; most specialists default to `gpt-4.1` / `gpt-4.1-mini` on the 1M-context cost-efficient tier), the projected total token-cost reduction per trial run is **≥50% vs. an all-flagship baseline**. Sanctum cold-start is deterministic and cache-friendly by construction.

**Manifest-as-graph-config promotes Pipeline Lockstep to a framework-level CI gate.** The existing 15-step pipeline manifest becomes compile-time topology source; block-mode-trigger-paths become graph-compilation-time checks; drift between manifest and runtime becomes impossible rather than rare.

## Project Classification

- **Project Type:** `developer_tool` — internal multi-agent orchestration platform. The true shape is a Python framework + runtime (LangGraph subgraphs, Pydantic-v2 state, MCP bridge, Postgres checkpointing, LangSmith traces) that backs an operator-facing APP. Not a SaaS, not a web app, not a CLI-only tool. Developer-tool signals (framework, library, pip) match the stack; user-facing shape is operator + specialist agents.
- **Domain:** `edtech` — output is online course content production. Complexity driver is *infrastructure re-platform of a live system*, not classroom-privacy regulatory load (no COPPA/FERPA surface in scope). Secondary domain flavor is developer-tool infrastructure.
- **Complexity:** **High**. Invariant surface is large and load-bearing: Marcus-first orchestration semantics, Pipeline Lockstep regime (7-component), block-mode-trigger-paths, HIL operator gates, Pydantic-v2 four-file-lockstep schema discipline, party-mode + code-review gates before `done`, deferred-inventory governance, K-floor story-cycle discipline, 17 specialist agents with sanctum-backed identity, ~1100 tests green, first tracked trial run just closed. Migrating a working system onto a new runtime *without* softening any of those invariants is where the complexity lives.
- **Project Context:** **Brownfield.** Epics 1–14 + SB complete (75 stories); Epics 19–21 + 23 complete; Epic 20c in-progress (Wave 2B Creative Director + parameter registry); Epic 27 just closed 27-0 Retrieval Foundation + 27-1 DOCX provider; Epics 28–32 Lesson Planner MVP in flight; ~1100 tests passing. Primary repo carries production during migration.

## Success Criteria

### User Success (Operator)

The APP's primary user is the **operator** (solo human partnering with Marcus). The migration succeeds for the operator when:

1. **Runtime independence: IDE closure no longer aborts a production run.** A tracked trial run can be started, paused at a gate, resumed hours later from a different IDE session, forked for what-if exploration, and replayed from any checkpoint — all without requiring continuous Claude Code conversation. Measured by: a new tracked trial run (`C1-M1-PRES-20260501B` or later) completes §01→§15 with ≥1 mid-run IDE close/reopen and ≥1 intentional replay-from-checkpoint.
2. **HIL authority preserved at every consequential gate.** Operator receives a curated DecisionCard (drafted specialist proposal + evidence + risks + approve/edit/reject verbs) at every `interrupt()` gate. Gate count per trial run is unchanged from the manifest (Decision 3a — no gate silently removed or auto-approved). Measured by: gate inventory audit across the new tracked trial run matches the manifest 1:1.
3. **DecisionCard curation reduces cognitive load without removing authority.** Per-gate subjective cognitive-load self-report improves vs. the current (C1-M1-PRES-20260419B) baseline while reject-rate stays non-zero (proving decisions are real, not rubber-stamp). Measured by: pre-migration vs. post-migration operator diary entries on gate review time and perceived difficulty.
4. **Specialist spin-up is a same-day activity.** Operator can greenlight a new specialist (e.g., Wondercraft, Canvas, Qualtrics) and see it invocable from CLI/CI/MCP against a live API within **<1 dev-day** after the scaffold hardens (end of Slab 2). Measured by: Wondercraft pilot time-from-story-open to first-real-artifact-produced.

### Business Success (Migration ROI)

The migration succeeds economically when:

5. **Token cost per trial run drops ≥50%** vs. the current IDE-Marcus baseline, driven by compound levers: OpenAI automatic prompt caching on the stable sanctum/persona/references prefix (~50% cache discount on eligible input tokens) **plus** three-level model-tier routing (Marcus on best OpenAI reasoning model; specialists default to `gpt-4.1` / `gpt-4.1-mini` cost-efficient tier). Baseline measured during Slab 1; target validated during Slab 5.
6. **Cache hit rate on production preset reaches ≥80% (median)** by end of Slab 5. Slab 1 acceptance is ≥60%. Lower targets than the Anthropic-middleware baseline because OpenAI caching is automatic (not operator-tuned via explicit `cache_control` breakpoints) — hit rate reflects prefix stability, not operator tuning.
7. **Timeline honored: 12–16 weeks wall-clock** from Slab 1 kickoff to Slab 5 close. Deviation >20% triggers replan; deviation >50% triggers migration go/no-go re-evaluation with operator.
8. **Primary repo production continuity.** During the 12–16 week migration window, the primary repo continues to produce tracked trial runs on demand. Zero production outages attributable to migration-driven backport conflicts (because backports stop early — see Decision 2).
9. **Post-migration new-specialist cost structure.** Median dev-days per new specialist drops from *weeks* (current) to **<1 dev-day** — validated on 2+ new specialists after Slab 2 (Wondercraft in Slab 2; one additional in Slab 5 polish or post-migration).

### Technical Success (Runtime Properties)

The migration succeeds as a system when:

10. **Trial-run reproducibility is 100%.** Replay from any closed trial run's final checkpoint produces the same pack hash, byte-for-byte. Measured by: trial-replay regression test suite covering 100% of closed tracked trial runs at Slab 5 close (and every closed trial thereafter).
11. **Pipeline Lockstep is CI-enforced at graph-compile time.** A PR touching any `block_mode_trigger_path` without the required multi-file updates fails graph compilation — not just a pre-commit hook. Measured by: Slab 4 acceptance test where an intentionally drifted PR is rejected at CI.
12. **All 15 load-bearing substrate invariants preserved.** Audit at Slab 5 close confirms each invariant (Marcus SPOT, sanctum cold-read, 15-gate manifest topology, HIL-paused gates, 3-layer code review, event-ledger emission at G2C/G3/G4, frozen-at-ship pack discipline, K-floor test discipline, deferred-inventory continuity, Cora/Marcus lane separation, etc.) has a preserving pattern implementation.
13. **Specialist scaffold integrity.** All 17 specialists (plus Wondercraft pilot) use the same 9-node scaffold + typed envelope/return contracts + L0–L8 sanctum-backed expertise stack. Measured by: scaffold conformance test at Slab 2 close; zero ad-hoc specialist shapes permitted.
14. **Observability: LangSmith trace per gate decision.** Every DecisionCard emitted at a gate links to a LangSmith trace; party-mode and code-review gates consume traces (not just diffs) as evidence.
15. **Four-layer testing strategy green.** Unit (Pydantic state) + integration (subgraph) + end-to-end (graph replay) + trial-run regression layers all pass at Slab 5 close. No layer excused for migration convenience.

### Measurable Outcomes

| Outcome | Slab-1 baseline | Slab-5 target |
|---|---|---|
| End-to-end empty/full graph run completes §01→§15 | TRUE (empty) | TRUE (full, parity-or-better) |
| Specialist time-to-deploy (Wondercraft-class stub) | N/A | **< 1 dev-day** |
| Cache hit rate on production preset (median) | ≥ 80% | **≥ 90%** |
| Token cost per trial run (vs. current IDE-Marcus baseline) | measured | **≥ 60% reduction** |
| Trial-run reproducibility (replay produces same pack hash) | N/A | **100%** |
| Operator decisions per trial run (gate count) | manifest-defined | **unchanged** |
| Operator cognitive load at gates (1–5 self-report) | pre-migration baseline | **improved** via DecisionCard curation |
| BMAD code-review MUST-FIX rate per specialist story | current | **declining** (scaffold + anti-patterns catalog) |
| Trial-replay regression test coverage | 0 closed runs | **100%** of closed tracked trial runs |
| Migration timeline | T+0 | **T+12 to T+16 weeks** |

## Product Scope

### MVP — Minimum Viable Product (Slabs 1–5, end of 12–16 week window)

The **MVP of the migration** is the completion of all five slabs with a new tracked trial run reaching parity-or-better against the primary repo. Concretely:

- **Slab 1 — Substrate.** Runtime skeleton: self-hosted LangGraph + Pydantic v2 state base classes + `langgraph-checkpoint-postgres` with cleanup + retention policy + OpenAI automatic prompt caching + LangSmith tracing + FastAPI + MCP bridge + `app/models/` (registry + adapter + three-level selector). Empty manifest-loaded graph runs end-to-end through 15 steps with operator-driven gate decisions. Cache hit rate ≥60% on second invocation.
- **Slab 2 — Specialists.** 9-node scaffold hardened. `bmad-create-specialist` generator shipped. 17 existing specialists migrated (two-axis: scaffold conformance + sanctum cold-load integrity). Wondercraft pilot produces a real podcast against the live API. Specialist-anti-patterns catalog captured from the migration.
- **Slab 3 — Marcus Supervisor + Routing.** Marcus runs Plan-and-Execute (default) / ReAct (explore preset). DecisionCards curated at every gate. End-to-end APP run §01→§15 completes with operator approve/edit/reject at every gate.
- **Slab 4 — Pipeline Lockstep + Gates + Dev-Graph.** CI block-mode hook at graph-compile time. Cora dev-graph compiled as sibling (separate thread namespace). Party-mode-as-`interrupt()` operationalized. Frozen-graph-version ceremony codified. Learning-event ledger captures events at G2C/G3/G4. Pydantic + RetryPolicy workaround documented.
- **Slab 5 — Trial-Run + Polish.** Trial-replay regression test suite. Replay/fork UX usable by the operator. Economics dashboard (cache hit rate + token cost + per-specialist cost). Sanctum invalidation hook. Cold-storage archival policy. **Head-to-head parity validation** — a new tracked trial run reaches parity-or-better against the primary repo for the same input content.

MVP exit bar: all measurable outcomes above hit their Slab-5 targets, **and** the operator signs off on a new tracked trial run (`C1-M1-PRES-<date>` or equivalent) as parity-or-better.

### Growth Features (Post-MVP / Post-Migration enablement)

Capabilities unlocked by the MVP architecture; expected to land in the 3–6 months after Slab 5:

- **New specialist fleet at API-contract speed.** Canvas, Qualtrics, additional media/service specialists spun up in <1 dev-day each.
- **Schedulable/headless trial runs.** Cron-triggered runs; overnight replay/regression sweeps; batch cohort production without operator being present.
- **Party-mode review at scale.** Trace-first review workflow for party-mode and code-review gates; reviewers consume LangSmith traces as primary evidence alongside diffs.
- **Fork-from-checkpoint as a standard operator tool.** What-if exploration — fork a trial at G4 to explore alternate narration profiles without losing the canonical branch.
- **Cross-run learning-ledger analytics.** Patterns extracted across closed trial runs inform specialist prompt tuning and scaffold evolution.
- **Primary repo retirement ceremony.** Backport window closes; primary repo goes read-only as the frozen reference; clone becomes canonical.

### Vision (Future)

Longer-horizon capabilities beyond the immediate migration window:

- **Multi-operator collaboration.** Checkpointed state + DecisionCard curation naturally supports multiple operators reviewing different gates of the same trial run asynchronously.
- **Specialist marketplace pattern.** Sanctum-backed specialist identity + scaffold conformance means specialists become portable across BMAD projects.
- **LangGraph runtime upgrades as governance tickets.** Tier-1/2/3 version-bump policy (mirroring pack-version policy) makes LangGraph upgrades a party-mode decision, not a surprise.
- **Learning-ledger-driven scaffold evolution.** Empirical evidence from closed trial runs drives scaffold changes (Tier-3 pack-version bumps) — the system learns from its own production history.
- **Multi-pipeline topology.** The manifest-as-graph-config pattern generalizes — future pipelines (non-course, different domains) can reuse the substrate + scaffold + sanctum pattern without re-platforming.

## User Journeys

### User Types Covered

1. **The Operator** (primary, solo) — Juanl, running tracked production trial runs with Marcus as SPOT.
2. **The Specialist Developer** (could be Juanl wearing dev hat, or BMAD Amelia/Diego dev agents) — extends the specialist fleet using the scaffold + `bmad-create-specialist` generator.
3. **The BMAD Reviewer** (party-mode persona + bmad-code-review agent) — gate-reviewer consuming traces and diffs as evidence.
4. **The Governance/CI System** (Cora dev-graph + block-mode hook) — enforces Pipeline Lockstep regime at graph-compile time.
5. **The Future Operator** (asynchronous / headless user) — triggers, forks, and replays runs without a continuous IDE conversation.

---

### Journey 1 — The Operator Runs a Tracked Trial, IDE Closes Mid-Run, Run Survives

**Persona:** Juanl. **Situation:** Running `C1-M1-PRES-20260501B` on a Tuesday evening. Currently at G4 (post-narration-script review). The operator's laptop battery is at 9%, and Slack is lighting up with an unrelated production issue that needs triage.

**Opening Scene (Before migration — current reality):** Under the IDE-resident runtime, closing the laptop means the Claude Code conversation ends. The trial is in an ambiguous state — some files written, checkpoint-of-sorts in `_bmad-output/trial-runs/`, but the *reasoning thread* (what Marcus was about to do next, which specialist was mid-draft, what DecisionCard the operator was about to receive) is stuck in a conversation that cannot reliably be resumed. The operator's only safe move today is to **wait** — keep the IDE open, finish G4 manually — at cost to the unrelated triage.

**Rising Action (Post-migration reality):** The operator sees the G4 DecisionCard waiting in the IDE, confirms the specialist proposal is in a good interim state, clicks a *pause* action that serializes the current thread state into Postgres via `PostgresSaver`. Closes the IDE. Handles the production incident on a different machine. Four hours later, opens the IDE on the *same* or a *different* machine.

**Climax:** The IDE reconnects to the self-hosted LangGraph runtime (it was never down — it's a persistent local service). The active thread is still at the G4 `interrupt()` with the DecisionCard intact. The operator reviews, approves with one edit, and Marcus resumes the trial at G5. No re-feeding of prior context, no conversation-history rehydration, no drift.

**Resolution:** Trial run closes at §15 the next morning. `runtime/graphs/v42/` produced byte-for-byte reproducible checkpoints. The trial is indexed in LangSmith with traces for every specialist and every gate. The operator's perceived cost of "pausing a run" has dropped from *hours of re-work* to *zero*.

**Capabilities this journey reveals:**
- Self-hosted persistent LangGraph runtime (not IDE-resident) — **Slab 1**
- `PostgresSaver` checkpointing with pause/resume semantics — **Slab 1**
- Gates as `interrupt()` nodes with durable DecisionCard payloads — **Slab 3**
- IDE ↔ runtime bridge (MCP primary + FastAPI escape hatch) — **Slab 1**
- LangSmith trace per trial run — **Slabs 1–5**

---

### Journey 2 — The Operator Forks a Closed Trial to Explore an Alternate Narration Profile

**Persona:** Juanl. **Situation:** Trial `C1-M1-PRES-20260501B` closed clean with Text-Led profile. Operator wants to know what would have happened with Visual-Led for comparison — but doesn't want to re-burn the whole pipeline.

**Opening Scene (Before migration):** Today the answer is "run a second full trial from scratch and diff the outputs." That's ~30 minutes of operator time, full token spend, 15 gates to re-decide. In practice this exploration almost never happens; operators ship a single profile and move on.

**Rising Action (Post-migration):** The operator opens the replay UX, navigates to the closed `C1-M1-PRES-20260501B` checkpoint at G3 (pre-narration-profile resolution), and clicks *fork*. A sibling thread is created from that checkpoint. The operator edits the `experience_profile` parameter in the forked thread's state and resumes.

**Climax:** Only the downstream nodes that depend on `experience_profile` re-execute (narration expansion, assembly-time parameter resolution, cluster-aware refinement). Cached-prefix token cost stays low (prompt-caching middleware already has the sanctum/persona/references layer warm). Operator decides 8 gates in the fork instead of 15 (upstream gates reused from canonical thread).

**Resolution:** Fork closes in ~15 minutes. Operator diffs canonical vs. fork artifacts. Chooses to ship canonical, but captures the fork in the deferred-inventory as a Wave-3 comparison artifact. What-if exploration is now a standard operator tool, not a forbidden cost.

**Capabilities this journey reveals:**
- Checkpointed thread state with time-travel + fork semantics — **Slab 5**
- Replay UX / fork UX usable by operator — **Slab 5**
- Prompt-caching middleware warmth across forked threads — **Slabs 1, 5**
- Only-dependent-nodes-re-execute (graph-aware partial replay) — **Slab 5**
- Deferred-inventory continuity across forked runs — **Slab 4**

---

### Journey 3 — The Specialist Developer Adds Wondercraft in Under a Day

**Persona:** Dev-agent Amelia (or Juanl wearing dev hat). **Situation:** Operator has signed off on adding Wondercraft (podcast-production specialist) to the fleet. Story `NN-1` opens: "Implement Wondercraft specialist".

**Opening Scene (Before migration — current reality):** Adding a new specialist today means hand-crafting a `skills/bmad-agent-wondercraft/` directory, writing a SKILL.md, populating sanctum files from scratch, wiring scripts, writing integration tests, patching Marcus's specialist registry, iterating through party-mode and code-review on a custom shape. This has historically taken **weeks** — multiple stories, multiple gates, with each specialist having subtly different internal structure.

**Rising Action (Post-migration):** Amelia runs `bmad-create-specialist --name wondercraft --mcp wondercraft-api --expertise-tier L5-podcast-production`. The generator emits: a 9-node scaffold pre-wired to the manifest, a sanctum stub under `_bmad/memory/bmad-agent-wondercraft/` (INDEX.md + PERSONA.md + empty access-boundaries.md + chronology.md), L0–L8 expertise-stack skeleton with L5/L6 placeholders, typed envelope/return Pydantic models, integration-test scaffold with scaffold-conformance assertions, and a scaffold-entry in Marcus's specialist registry. Amelia fills in the L5 references (podcast-production knowledge) and L6 Wondercraft-specific operational context, hooks the L7 MCP tool to the real Wondercraft API, and writes one happy-path integration test.

**Climax:** Amelia runs the scaffold-conformance test — passes. Runs the sanctum cold-load integrity test — passes. Runs the end-to-end integration test against the live Wondercraft API — produces a real podcast artifact on first full wire-up. Total elapsed clock time from story-open to first-real-artifact: **~6 hours**.

**Resolution:** Story closes through party-mode (green) and bmad-code-review (MUST-FIX count minimal because scaffold enforces shape). Wondercraft is now invocable from CLI, CI, and Marcus. The operator can call on Wondercraft in the next trial run. Specialist time-to-deploy has collapsed from weeks to <1 dev-day — as designed.

**Capabilities this journey reveals:**
- `bmad-create-specialist` generator — **Slab 2**
- 9-node scaffold + typed envelope/return contracts — **Slab 2**
- Sanctum-backed L0–L8 expertise-stack taxonomy — **Slab 2**
- Scaffold-conformance test + sanctum-cold-load integrity test — **Slab 2**
- MCP tool integration pattern at L7 — **Slab 2**
- Specialist-anti-patterns catalog harvested during migration — **Slab 2**
- Specialist registry as graph-config, not hand-patched — **Slab 2, 3**

---

### Journey 4 — The BMAD Reviewer Consumes a Trace as Gate Evidence

**Persona:** BMAD party-mode reviewer (e.g., Dr. Quinn, Tracy, Winston) and/or bmad-code-review gate. **Situation:** Story 33-5 (a hypothetical Slab-2 scaffold-hardening story) is at gate. Dev agent claims the scaffold passes all 17 specialist migrations.

**Opening Scene (Before migration — current reality):** Reviewers consume diffs plus dev-notes narrative. If the reviewer wants evidence that "Marcus routed correctly to all 17 specialists across a trial," they rely on written descriptions and spot-check artifacts in `_bmad-output/trial-runs/<run-id>/`. There is no unified way to *see* the orchestration unfold.

**Rising Action (Post-migration):** The story spec links to a LangSmith trace of a tracked trial run that exercised all 17 specialists. The reviewer opens the trace in LangSmith UI. Sees the full graph execution: every specialist subgraph invocation, every routing edge taken by Marcus, every gate `interrupt()` firing, every DecisionCard payload, every prompt-cache hit/miss, every token count per node.

**Climax:** The reviewer notices one specialist's `reason` node returned unusually high token usage on one trial. Drills in. Sees the prompt — finds a references-layer file that was re-included instead of cache-referenced. Flags a MUST-FIX with the specific node + trace link as evidence. Dev agent fixes in ~10 minutes because the issue is precisely localized.

**Resolution:** Gate closes. Story moves to done. The party-mode + bmad-code-review gates now have a **trace-first evidence standard**: reviewers consume traces alongside diffs, not just narrative. MUST-FIX precision goes up; MUST-FIX count-per-story goes down (scaffold + anti-patterns catalog + trace evidence together).

**Capabilities this journey reveals:**
- LangSmith tracing at node granularity — **Slab 1**
- Party-mode + code-review gates as evidence-first workflow — **Slab 4**
- Per-node prompt-cache hit/miss telemetry — **Slabs 1, 5**
- Learning-event ledger emission at G2C/G3/G4 — **Slab 4**
- MUST-FIX localization via trace-link citation — **Slab 4**

---

### Journey 5 — The Governance CI System Rejects a Drifted PR at Graph-Compile Time

**Persona:** Cora dev-graph + block-mode hook, consuming a PR that touches `scripts/utilities/workflow_runner.py` (a `block_mode_trigger_path`) but does NOT update the pipeline manifest, the L1 check script, and the v4.2 pack.

**Opening Scene (Before migration — current reality):** Today this drift is caught by a pre-commit hook + a story-level discipline rule + human reviewer vigilance. It sometimes slips — the story-level rule relies on the dev agent reading CLAUDE.md and the Pipeline Lockstep Regime doc before T1. Drift has been caught pre-ship but has also been a near-miss source for Wave 2B.

**Rising Action (Post-migration):** The PR hits CI. The Cora dev-graph compilation step loads the manifest as graph config, then loads the modified `workflow_runner.py`, attempts to compile the runtime graph against it. Compilation fails: the runner signature changed but the manifest's `run_lifecycle.steps[]` contract did not update to match. Graph compilation error is precise: "Node `run_workflow_step` expects `(state: RunState, step_id: str) -> RunState` but workflow_runner.run_step signature is `(state, step_id, ctx) -> RunState`."

**Climax:** CI blocks the merge. The dev agent sees the graph-compile-time error (not a "pre-commit hook failed" — a *framework-level semantic violation*). Updates the manifest contract, the L1 check, and the v4.2 pack in the same PR. Re-runs CI. Graph compiles. Merge unblocks.

**Resolution:** Pipeline Lockstep regime is now CI-enforced at graph-compile time. Block-mode-trigger-paths become compile-time checks, not just pre-commit hygiene. Drift has moved from "usually caught" to "impossible to merge."

**Capabilities this journey reveals:**
- Manifest-as-graph-config — **Slab 4**
- Cora dev-graph compiled as sibling, separate thread namespace — **Slab 4**
- Graph-compile-time Pipeline Lockstep enforcement — **Slab 4**
- Block-mode hook elevated from pre-commit to CI — **Slab 4**
- Cora/Marcus lane separation preserved (Cora owns dev-graph; Marcus owns run-graph) — **Slab 4**

---

### Journey Requirements Summary

Capability areas revealed across the five journeys, mapped to slabs:

| Capability Area | Journey(s) | Primary Slab |
|---|---|---|
| Persistent self-hosted LangGraph runtime | 1, 2 | **Slab 1** |
| Postgres checkpointing + pause/resume | 1 | **Slab 1** |
| IDE ↔ runtime bridge (MCP primary) | 1, 2 | **Slab 1** |
| Prompt-caching middleware | 2, 4 | **Slab 1** |
| LangSmith tracing at node granularity | 1, 4 | **Slab 1** |
| 9-node specialist scaffold + envelope contracts | 3 | **Slab 2** |
| Sanctum-backed L0–L8 expertise stack | 3 | **Slab 2** |
| `bmad-create-specialist` generator | 3 | **Slab 2** |
| Specialist-anti-patterns catalog | 3, 4 | **Slab 2** |
| Marcus Plan-and-Execute supervisor | 1, 4 | **Slab 3** |
| Gates as `interrupt()` nodes + DecisionCards | 1, 2, 4 | **Slab 3** |
| Manifest-as-graph-config | 5 | **Slab 4** |
| Cora dev-graph + block-mode CI enforcement | 5 | **Slab 4** |
| Learning-event ledger at G2C/G3/G4 | 4 | **Slab 4** |
| Party-mode-as-`interrupt()` + trace-first review | 4 | **Slab 4** |
| Time-travel + fork (replay/fork UX) | 2 | **Slab 5** |
| Trial-replay regression test suite | 2 | **Slab 5** |
| Economics dashboard (cache hit + token + per-specialist) | 2, 4 | **Slab 5** |
| Sanctum invalidation hook | 3 | **Slab 5** |
| Head-to-head parity validation vs. primary repo | (implicit, all) | **Slab 5** |

Every capability area ties to a slab; every slab has journey-validated capabilities. No capability is orphaned; no journey lacks capability backing.

## Domain-Specific Requirements

The domain here is **brownfield re-platform of a live, governed multi-agent production system**. The constraint surface that follows is inherited from the current APP and the BMAD governance regime — not from edtech regulation. No edtech-specific privacy requirements apply (no student PII in the pipeline).

### Load-Bearing Substrate Invariants (15 total — none droppable)

Every one of these must have a preserving implementation pattern in the target architecture. Drop-rate budget: **zero**. Source: research doc §Current APP State — Substrate Digest.

1. **Marcus is SPOT (Sacred Truth, Single Point of Contact).** Operator talks to Marcus; Marcus delegates to specialists. No specialist is operator-facing except through Marcus.
2. **Marcus is stateless-cold-start on every invocation.** Sanctum is re-read from disk on every session open. There is no persistent Marcus in-memory state between sessions; the sanctum files on disk are the only identity source.
3. **The 15-step pipeline manifest is the deterministic neck.** Topology is manifest-driven (`state/config/pipeline-manifest.yaml`). Runtime code does not invent topology; it consumes it.
4. **Gates are HIL-paused by construction.** Every gate point in the manifest has operator authority (approve / edit / reject). No gate auto-progresses without an explicit operator decision.
5. **Learning events are emitted at G2C, G3, G4.** Structured records that feed downstream learning-ledger analytics; idempotent side-effect; must not be skipped or duplicated.
6. **Three-layer code review discipline (blind-hunter + edge-case-hunter + acceptance-auditor) precedes every story `done`.** The `bmad-code-review` skill embodies this. MUST-FIX findings block `done`.
7. **K-floor test discipline** (target 1.2–1.5× K, not 5× — see `docs/dev-guide/story-cycle-efficiency.md`). Test counts that balloon to 5× K are a governance finding, not a virtue.
8. **Pydantic-v2 four-file-lockstep schema discipline** (model module + JSON-schema emission + shape-pin test + golden fixture — all four updated in one PR; violation is a drift bug, not a style quibble). See `docs/dev-guide/pydantic-v2-schema-checklist.md`.
9. **Structured learning-ledger emission** at G2C/G3/G4 is a *side-effect* node, not part of the primary reasoning flow. Removing it does not change trial artifacts; adding it does not change trial artifacts beyond the ledger itself.
10. **Frozen-at-ship pack discipline.** Once a pack ships + a tracked trial-run completes, subsequent structural edits bump the version; the frozen prior-version pack stays on disk for audit. `runtime/graphs/v42/`, `v43/` siblings preserve this.
11. **K-floor story-cycle discipline** intersects with Slab-2 mass specialist migration — 17 specialists × disciplined story-cycle means Slab 2 must use the scaffold to hit K-floor targets, not inflate story counts.
12. **Marcus-first orchestration semantics.** Operator says "Marcus" → cold-start activation reads skills then sanctum. No specialist is jumped to ad-hoc without operator naming them.
13. **Specialist registry is authoritative and discoverable.** Marcus's registry (e.g., `skills/bmad-agent-marcus/references/specialist-registry.yaml`) is the single source of truth for "who can Marcus call." Registry drift is a bug.
14. **Deferred-inventory continuity across runs.** `_bmad-output/planning-artifacts/deferred-inventory.md` is the standing register; consulted at every Epic retrospective, every session hot-start, every new story that names a follow-on.
15. **Cora/Marcus lane separation.** Cora owns the dev-graph lane (story-cycle, story-authoring, dev-agent orchestration). Marcus owns the run-graph lane (production trial orchestration). Two compiled graphs, two thread namespaces, no crossover.

### Compliance & Regulatory (Non-Edtech)

- **No student PII, no classroom data, no COPPA/FERPA surface.** The APP produces *course content assets* (narration scripts, visual designs, assembly bundles). It does not ingest or store student data. This is a strict scope boundary the migration preserves.
- **Operator data sovereignty.** All state (Postgres checkpoints, sanctum files, trial artifacts, LangSmith traces) lives on operator-controlled infrastructure. Self-hosted LangGraph was chosen partially to preserve this (Decision — LangGraph Platform rejected).
- **LangSmith as observability, not decision-of-record.** Traces are evidentiary substrate for reviewers; the decision-of-record remains the operator's DecisionCard verdict + BMAD artifacts in `_bmad-output/`. LangSmith loss does not invalidate a closed trial.

### Technical Constraints

- **Self-hosted runtime.** Self-hosted OSS LangGraph is the decision (not LangGraph Platform). Sanctum-file-backed memory, hybrid IDE↔runtime bridge architecture, single-operator scale, and bounded-big-bang control needs all favor self-host. See research §Technology Stack.
- **Persistence layer = Postgres via `langgraph-checkpoint-postgres`.** Checkpoint cleanup + retention + audit policy is a Slab-1 acceptance criterion, not a Slab-5 afterthought.
- **LLM provider = OpenAI API** (locked 2026-04-22). `langchain-openai` + `openai` SDK. Anthropic / `AnthropicPromptCachingMiddleware` out of scope. Provider adapter (`app/models/adapter.py`) isolates `ChatOpenAI` so a future multi-provider or Anthropic re-introduction is a contained change.
- **Caching = OpenAI automatic prompt caching** (no middleware required; stable prefix ≥1024 tokens cache-eligible automatically; ~5–10 min TTL; ~50% discount on cached input tokens). Cache hit rate ≥60% is a Slab-1 acceptance bar; ≥80% is a Slab-5 target.
- **IDE bridge protocol = MCP primary, FastAPI escape hatch.** Reuses existing IDE↔MCP infrastructure. LangServe explicitly rejected (deprecated direction in 2026).
- **State shape = Pydantic v2** with `validate_assignment=True`, timezone-aware datetimes, UUID4 validation, triple-layer red-rejection on closed enums, `Field(exclude=True) + SkipJsonSchema` for internal audit fields. Inherited idioms — see Pydantic-v2 checklist.
- **Schema-shape stories default to the scaffold at `docs/dev-guide/scaffolds/schema-story/`.** Migration does not abandon scaffold adoption; the migration *extends* the scaffold pattern to specialists.
- **Model-tier routing via three-level resolution cascade:** (1) runtime override (operator sets per-node model at trial-run start / gate resume / fork) > (2) per-agent configured default in `app/specialists/{name}/model_config.yaml` > (3) auto-select via deterministic `app/models/selector.py` (when configured default is `auto`). Marcus's plan/supervisor nodes are locked to the best available OpenAI reasoning model (default target: `o3-mini` or successor); runtime override permitted for debug but production trials default to reasoning tier. Specialist palette: reasoning (`o3-mini` for rare multi-hop cases), long-context balanced (`gpt-4.1` / 1M context), fast workhorse (`gpt-4.1-mini`), boundary/structured-output (`gpt-4.1-nano` / `gpt-4o-mini`), multimodal (`gpt-4o` for image/audio specialists). Model registry (`app/models/registry.yaml`) is versioned; updates follow Tier-1/2/3 governance (mirrors pack-versioning policy).
- **Structured output at boundaries, free-text inside specialists' `reason` nodes.** Schema-as-boundary-not-corset. Free-text default prevents the LangChain cage.

### Integration Requirements

- **MCP server as IDE↔runtime bridge** — reuses existing `.mcp.json` and `.cursor/mcp.json` entries; adds a new runtime-server entry for the LangGraph service.
- **Existing retrieval substrate (Texas Shape 3-Disciplined retrieval contract)** — must integrate as-is; the retrieval contract lives at `skills/bmad-agent-texas/references/retrieval-contract.md` and is authoritative. Migration does not re-design retrieval; it wires it into the specialist scaffold's L7 (MCP tool access) layer.
- **Existing sanctum directories** (`_bmad/memory/bmad-agent-{name}/`) — remain the identity source of truth; are read on every cold-start and are cache-friendly prefix material.
- **Existing `bmad-agent-builder` skill** — remains for non-runtime agent creation (party-mode agents, BMAD stock personas). A *new* skill `bmad-create-specialist` is introduced in Slab 2 for runtime specialists with scaffold conformance.
- **Existing Descript/ElevenLabs/Gamma specialist APIs** — integrated via L7 MCP tools in the new scaffold; the current `skills/bmad-agent-{desmond,dex,gamma,...}/scripts/` layers get re-homed into specialist subgraph `act` nodes.
- **Existing four-file-lockstep schema discipline** — integrated as a CI check against the Pydantic-v2 checklist; violations block merge at graph-compile time (Slab 4).

### Risk Mitigations (Domain-Specific — See Slab-Level Risk Register for Full Surface)

- **Risk: LangChain cage creeps in over Slabs 2–3** as specialists are migrated under time pressure. **Mitigation:** Decision 3's eight operating rules + five anti-patterns are codified *before* Slab 2 opens. A specialist-anti-patterns catalog is a Slab-2 deliverable that harvests real examples from the migration itself.
- **Risk: Invariant drift** — an invariant is silently dropped under a plausible-sounding refactor ("we don't need event-ledger emission in the new runtime since LangSmith has traces"). **Mitigation:** Slab-5 acceptance includes a 15-invariant audit matrix; each invariant must name its preserving implementation pattern with a file/test reference. No invariant can be marked preserved with a narrative claim alone.
- **Risk: Sanctum drift between primary and clone** during the 12–16 week divergence window. **Mitigation:** Sanctum files are authored in the clone going forward; primary repo sanctum becomes frozen reference. Backports stop early (Decision 2).
- **Risk: Pipeline Lockstep regime weakens** during migration because CI runs against the primary repo's manifest discipline, not the clone's emerging graph-config discipline. **Mitigation:** Slab 4 delivers graph-compile-time Lockstep enforcement before Slab 5 head-to-head parity; block-mode-trigger-paths migrate to graph-compile-time checks.
- **Risk: HIL operator authority erodes** because DecisionCard curation is mistaken for decision auto-advance. **Mitigation:** Decision 3a is explicit: curation reduces re-feeding burden, never operator authority. DecisionCards include an explicit `reject` verb; reject-rate is a tracked KPI in Slab 5.
- **Risk: Team ramp-up cost on LangGraph + Pydantic-v2 LangGraph state + Postgres ops** consumes Slab-1 timeline. **Mitigation:** Slab 1 is deliberately scoped as "runtime skeleton + team learning slab." Concept-work is Slab 1's primary deliverable alongside artifacts.
- **Risk: Clone divergence drifts forward too fast** — primary repo ships Epic 33/34 features during migration that clone cannot forward-port cheaply. **Mitigation:** Backports stop after Slab 1 opens. Forward-ports batch at Slab-5 close. Operator coordinates epic-open/close cadence to avoid mid-migration primary-repo feature ships.

### BMAD Sprint Governance Inheritance

The migration operates **under existing BMAD sprint governance** (see CLAUDE.md §BMAD sprint governance):
- Every story authored via `bmad-create-story` / `bmad-create-prd` / `bmad-quick-dev` (no ad-hoc stories).
- Green-lighting + initial review via `bmad-party-mode` (not a single improvised persona).
- `bmad-code-review` precedes every story `done`.
- BMAD team consensus drives decisions; impasse is a pause, not an override.
- Stop only on sprint complete or documented impasse.

All migration stories conform to this. The migration does not grant itself a governance exception.

### Lesson Planner MVP Intersection (Concurrent Epic — Migration Does Not Block)

Epics 28–32 (Lesson Planner MVP) are in flight in the primary repo. The migration **does not pause Lesson Planner MVP**:
- Lesson Planner MVP stories continue in the primary repo with full schema-shape discipline (per CLAUDE.md §Lesson Planner MVP — dev-agent references).
- The migration clone does not attempt to forward-port Lesson Planner MVP stories mid-migration; they forward-port at Slab-5 close along with any other primary-repo progress.
- Lesson Planner schema-shape patterns (31-1, 31-2, 31-3 and beyond) are inherited into the target runtime at forward-port time; the scaffolds at `docs/dev-guide/scaffolds/schema-story/` remain authoritative during migration.

## Innovation & Novel Patterns

### Detected Innovation Areas

The migration is not a routine LangGraph adoption. Six architectural patterns in it are genuinely novel relative to the mainstream LangGraph/LangChain community patterns circa early 2026:

#### 1. Sanctum-Backed L0–L8 Expertise Stack as a First-Class Specialist Primitive

**What it is:** Every specialist is instantiated against a 9-node scaffold whose identity is anchored in a sanctum directory (`_bmad/memory/bmad-agent-{name}/`) containing INDEX.md, PERSONA.md, chronology.md, access-boundaries.md. The sanctum is read cold on every invocation (no in-memory continuity). Around the sanctum sit 9 layered expertise tiers (L0 LLM training → L1–L4 sanctum identity → L5 domain references → L6 operational context → L7 MCP tools → L8 envelope/runtime context).

**Why novel:** LangGraph community patterns treat agent identity as prompt-inline or as a RAG retrieval surface. This pattern treats identity as a **file-backed Sacred Truth** that is deterministic, cache-friendly by construction, auditable (files are in git), and cold-startable without session memory. The 9-layer taxonomy imposes a vocabulary on "what an agent knows" that doesn't exist in the LangChain literature.

**Differentiation:** File-backed identity + layered expertise stack + mandatory cold-read discipline is a coherent pattern that makes specialist creation a **plug-and-play activity** rather than bespoke engineering. Generic LangGraph specialists require hand-crafting identity, memory, and tool access per specialist.

#### 2. Manifest-as-Graph-Config (compile-time topology source)

**What it is:** The existing 15-step pipeline manifest (`state/config/pipeline-manifest.yaml`) becomes the compile-time topology source. The runtime doesn't build topology in Python; it compiles it from the manifest. Block-mode-trigger-paths become compile-time checks. Manifest drift vs. runtime becomes impossible-to-merge (graph-compile fails).

**Why novel:** Most LangGraph examples build topology in Python with explicit `add_node` / `add_edge` calls at import time. Few promote a declarative manifest to the compile-time topology source; fewer still enforce manifest conformance as a CI check at graph-compile time. The pattern is closer to Terraform's plan/apply discipline than to typical LangGraph code.

**Differentiation:** Turns Pipeline Lockstep from a process discipline into an architectural invariant. Makes "the manifest IS the pipeline" a load-bearing truth, not an aspiration.

#### 3. Gate-as-`interrupt()` + Curated DecisionCard Payload

**What it is:** Every gate in the manifest becomes a checkpointed `interrupt()` node whose payload is a curated DecisionCard — drafted specialist proposal + evidence + risks + explicit approve/edit/reject verbs. Operator consumes the card, emits a verdict, the graph resumes.

**Why novel:** `interrupt()` in LangGraph is widely used for HIL, but the pattern of treating the interrupt *payload* as a first-class curated artifact (not just a prompt-for-input) is uncommon. DecisionCards are structured payloads that evolve over time — curation reduces operator cognitive load per decision without reducing operator authority. Reject-rate becomes a measurable KPI.

**Differentiation:** Makes HIL *scalable* — operator spends mental budget on decision quality, not on reconstituting state. Most HIL flows today re-feed context at every gate.

#### 4. Frozen-Graph-Version Pattern (runtime-as-immutable-artifact)

**What it is:** `runtime/graphs/v42/`, `v43/` etc. are siblings on disk. A completed trial run binds to the graph version it ran against; that version is immutable after first tracked trial closes. Subsequent structural changes bump the version; the frozen prior-version graph stays on disk for audit/replay.

**Why novel:** LangGraph community typically treats the graph definition as code-evolves-freely. This pattern treats graphs like database migrations or pack versions — versioned, frozen on ship, coexistent for audit. Tier-1/2/3 version-bump policy mirrors pack versioning, and graph upgrades become governance tickets, not silent refactors.

**Differentiation:** Byte-for-byte reproducibility of closed trial runs becomes architectural, not procedural. Audit guarantees are code-enforced, not process-enforced.

#### 5. Two-Graph Lane Separation (Cora Dev-Graph ⊥ Marcus Run-Graph)

**What it is:** Two compiled graphs coexist in the same repo, compiled separately, run on separate thread namespaces in Postgres. Cora owns the dev-graph lane (story-cycle: plan → implement → test → review → done). Marcus owns the run-graph lane (production trial: §01 → §15). No node crosses lanes; no thread crosses lanes.

**Why novel:** Most LangGraph applications have a single graph. Few maintain two graphs with explicit lane-separation discipline. The pattern corresponds to the BMAD operational reality that **dev-work and production-work are different lanes with different governance** (K-floor tests for dev; frozen-at-ship packs for prod).

**Differentiation:** Governance regimes stay separated at the graph level, not just the process level. Attempts to blur the lanes (e.g., Cora invoking Marcus) get caught at compile-time via thread-namespace checks.

#### 6. "Reject the LangChain Cage" as Codified Architectural Discipline

**What it is:** Eight operating rules (probabilistic-first nodes, routing-edges-decide-who-not-what, schema-as-boundary-not-corset, long-context-over-compression, specialists-as-subgraphs, narrow-deterministic-glue, model-tier-follows-reasoning, replay-enables-exploration) + five named anti-patterns, codified as the explicit operating doctrine for the migration and captured in a living specialist-anti-patterns catalog.

**Why novel:** Most LangGraph adoptions silently trade agent intelligence for graph determinism (the "cage"). This migration **names** that trade-off, rejects it as an architectural principle, and codifies the rules that prevent it — before a single specialist is migrated. The catalog is harvested from the migration itself during Slab 2 and becomes a permanent reference.

**Differentiation:** Architectural discipline as doctrine, not as tacit knowledge. New specialist developers read the rules + anti-patterns catalog before T1 — same as the Pydantic-v2 checklist and dev-agent anti-patterns already in CLAUDE.md.

### Market Context & Competitive Landscape

- **LangGraph ecosystem maturity (as of 2026-Q1):** Plan-and-Execute and ReAct are mature. OpenAI automatic prompt caching is production-ready at the API layer (no middleware required); `AnthropicPromptCachingMiddleware` also production-ready (not used — OpenAI provider decision). Pydantic v2 state + Postgres checkpointing is production-ready. MCP as bridge protocol is production-ready (deprecating LangServe). Time-travel + fork is in preview but usable.
- **Comparable systems:** LangGraph reference implementations (supervisor-worker patterns, multi-agent graphs) exist — but none of the reference projects combines: file-backed agent identity, manifest-as-graph-config, DecisionCard-curated HIL, frozen-graph-versioning, and lane-separated dev/run graphs. Each of these patterns exists individually in academic papers or isolated repos; the combination is novel.
- **Operator-facing AI frameworks (Claude Desktop, Cursor MCP, etc.):** These treat the IDE-as-runtime as the model. Relieving that constraint while keeping operator-first interaction is the migration's central bet. Few comparable systems have made the jump from "chat-is-runtime" to "persistent-runtime + chat-client"; those that have (e.g., some agentic research platforms) typically sacrifice operator authority.
- **What doesn't exist in the literature:** Applied academic literature on multi-agent HIL pipelines with gate-curation + lane-separation + manifest-driven topology. The research doc's 12-pattern → 15-invariant mapping is itself an original contribution; the PRD and subsequent architecture doc should capture it as a reference.

### Validation Approach

Innovation claims require validation — not theory. Validation methodology:

1. **Sanctum-backed specialist pattern:** Validated in Slab 2 by producing the Wondercraft specialist end-to-end in **<1 dev-day** using `bmad-create-specialist`. One specialist suffices to prove the pattern; a second new specialist in post-Slab-5 polish confirms generalization.
2. **Manifest-as-graph-config:** Validated in Slab 4 by an acceptance test that intentionally drifts a `block_mode_trigger_path` file without updating the manifest — graph compilation must fail at CI, not just at pre-commit.
3. **Gate-as-`interrupt()` + DecisionCard:** Validated across Slabs 3 + 5 by running a new tracked trial run §01→§15 with DecisionCards at every gate. Reject-rate must be non-zero (proving decisions are real); operator cognitive-load self-report must improve vs. pre-migration baseline.
4. **Frozen-graph-version:** Validated in Slab 5 by closing a tracked trial run against `v42`, then bumping to `v43` for a structural change, then replaying the `v42`-bound trial — must produce byte-for-byte identical pack hash.
5. **Two-graph lane separation:** Validated in Slab 4 by attempting to compile a node that crosses lanes (a Cora node invoking Marcus's specialist registry) — must fail at compile time with a clear lane-violation error.
6. **"Reject the LangChain cage" doctrine:** Validated by Slab-2 harvest of the specialist-anti-patterns catalog. Catalog must include at least 5 concrete anti-patterns encountered and corrected during migration (not invented retrospectively). BMAD code-review MUST-FIX rate per specialist story declining over Slab 2 is the quantitative proxy.

### Risk Mitigation

- **Risk: Innovation over-engineering.** The temptation to elaborate the scaffold, expertise stack, or DecisionCard curation beyond what the APP actually needs. **Mitigation:** Each innovation pattern is gated by Slab acceptance criteria with measurable outcomes, not by theoretical elegance. If a pattern has no acceptance bar, it is not in scope.
- **Risk: "Novel" patterns that don't generalize.** A pattern that works for Marcus+17-specialists may not generalize to future use cases. **Mitigation:** Validation #1 (Wondercraft pilot) and the post-Slab-5 second new specialist are explicitly generalization tests.
- **Risk: Innovation doctrine becomes dogma.** Eight operating rules + five anti-patterns, rigidly applied, could become the new cage. **Mitigation:** The specialist-anti-patterns catalog is **harvested from the migration**, not pre-declared. Rules are empirical, not aspirational. Rules that don't prevent real anti-patterns in Slab 2 get revised, not defended.
- **Risk: Framework lock-in to LangGraph's current idioms.** LangGraph evolves; patterns that depend on current API shape may break. **Mitigation:** Tier-1/2/3 version-bump policy (mirroring pack-version policy) surfaces LangGraph upgrades as governance decisions. Frozen-graph-version isolates impact of runtime upgrades per-graph.

## Developer Tool / Internal Orchestration Platform — Specific Requirements

### Project-Type Overview

This is an **internal multi-agent orchestration platform** — a Python framework + persistent runtime that backs the operator-facing APP. It is not an SDK shipped to external developers; its consumers are (a) the operator (via Marcus + IDE), (b) BMAD dev agents (Amelia, Diego), (c) BMAD reviewer agents (party-mode + code-review), (d) CI systems (Cora dev-graph + block-mode hooks). The platform's developer-tool shape is real: specialists are authored as scaffold-conforming subgraphs, extensions are built via MCP tools and Pydantic state extensions, and migration is consumed as a developer guide.

### LLM Provider — OpenAI API

The APP is powered by **OpenAI models via `langchain-openai`**, using a single `OPENAI_API_KEY`. Anthropic models and the `AnthropicPromptCachingMiddleware` are **out of scope** for this migration. Implications:

- **Caching**: OpenAI automatic prompt caching (prompts ≥1024 tokens, ~50% discount on cached input tokens, ~5-10 min TTL, no middleware required). Strategy is unchanged (stable sanctum/persona/references prefix), but the economic magnitude is lower than Anthropic's cache discount.
- **Tool / function calling**: OpenAI function-calling + `response_format={"type": "json_schema", ...}` structured-outputs used at schema boundaries — replaces Anthropic tool-use surface.
- **Provider lock-in risk**: mitigated architecturally via `ChatOpenAI` wrapped in a thin adapter (`app/models/adapter.py`) so a future multi-provider or Anthropic re-introduction is a contained change, not a scaffold rewrite.

### Model-Selection Mechanism (first-class, three-level)

Every node that invokes an LLM (every specialist `reason` and `act` node, every Marcus plan/supervisor node, every DecisionCard-curation node) resolves its model through a **three-level selection cascade**:

1. **Runtime override** (highest priority). Operator passes a per-invocation override at trial-run start, at gate resume, or at fork-from-checkpoint. Shape: `model_override: Dict[NodeId, ModelRef]`. Stored in thread state; cleared on trial close.
2. **Agent-configured default** (second priority). Per-specialist, per-node config in `app/specialists/{agent_name}/model_config.yaml`. Can be a specific model ref (e.g., `gpt-4.1`) or the literal string `auto` to defer to level 3.
3. **System-recommended auto-select** (fallback when configured default is `auto`). Deterministic selection function — **not an LLM itself** — that picks a model given `(agent, node_role, context_tokens, quality_tier, budget_tier)`. Encoded in `app/models/selector.py`. Rules expressed as YAML in `app/models/selection_policy.yaml`.

The three levels form a pure resolution cascade: resolution is deterministic, auditable, and logged per-node in LangSmith traces (which model ran, under which level, with what fallback trail). Model-selection decisions are **side-effect-free configuration logic**, not agentic reasoning; no cage-risk.

#### Marcus — locked to best available reasoning model

Marcus's plan/supervisor nodes are **not subject to `auto`**. Marcus's `model_config.yaml` pins the best available OpenAI reasoning model (target default: `o3-mini` or whatever supersedes it at migration close). Runtime override remains permitted for debugging — e.g., operator can force `gpt-4o` for a fast-iteration dev session — but production trial runs default Marcus to the reasoning tier. Rationale: Decision 1+2+3a all rest on Marcus's orchestration quality; downgrading Marcus to a fast/cheap model is a category mistake.

#### Specialists — tier palette

Most specialists default to cost-effective, large-context, fast tiers. Palette (defaults subject to registry updates):

| Tier | Primary Use | Default Model (2026-Q2) | Context | Relative Cost |
|---|---|---|---|---|
| **Reasoning** | Marcus plan, supervisor, deep multi-step reasoning | `o3-mini` (or successor) | 200K | high |
| **Long-context balanced** | Specialist `reason` nodes with large reference loads (Irene planning, Texas retrieval synthesis) | `gpt-4.1` | 1M | medium |
| **Fast & cheap workhorse** | Specialist `reason` nodes for routine work (most specialists), DecisionCard drafting | `gpt-4.1-mini` | 1M | low |
| **Boundary / structured output** | Schema-extraction nodes, validators, learning-event emitter payloads | `gpt-4.1-nano` or `gpt-4o-mini` | variable | lowest |
| **Multimodal** | Specialists needing image/audio (Eli for ElevenLabs QA, visual-pack specialists) | `gpt-4o` | 128K | medium |

GPT-4.1 family is the migration's workhorse tier (1M context + low cost + fast). Specialists with genuine multimodal needs fall to GPT-4o. The reasoning tier is reserved for Marcus and (rarely) specialists that explicitly need multi-hop reasoning.

#### Model registry — authoritative and versioned

`app/models/registry.yaml` is the single source of truth for available models:
- Model ID, tier, context window, input/output cost per 1M tokens, capabilities (tool-use, structured-output, multimodal, reasoning-mode), deprecation status
- Updated as OpenAI releases new models — registry bumps follow the Tier-1/2/3 pack-versioning analog: Tier-1 (new model added, no default changes) = dev-agent authority; Tier-2 (a default tier changes, e.g., reasoning-tier switches from `o3-mini` to `o4`) = single-gate party-mode; Tier-3 (palette or policy restructure) = full party-mode + operator sign-off.

#### Model-selection interactions with caching

Worth explicit mention: **OpenAI prompt cache is per-model**. Switching models at runtime via override invalidates the cache on first call with the new model. Runtime overrides are therefore explicitly a **cost trade-off** for the operator — flagged in the runtime-override UX so the operator sees the cache-invalidation implication before forcing a model switch mid-trial.

### Technical Architecture Considerations

The architecture lives at the intersection of **three concurrent lanes**:

- **Run-graph lane (Marcus).** 15-step production pipeline compiled from the manifest. Thread namespace: `run/{trial_id}`. Checkpointed in Postgres. Specialist subgraphs invoked via routing edges. Gates are `interrupt()` nodes with DecisionCard payloads.
- **Dev-graph lane (Cora).** Story-cycle as a compiled graph: plan → implement → test → review → done. Thread namespace: `dev/{story_id}`. Same Postgres. Separate compilation unit. Block-mode hooks live here.
- **Specialist fleet.** 17 specialists + growth (Wondercraft, Canvas, Qualtrics). Each is a 9-node scaffold subgraph invocable from either lane (via lane-respecting routing). Identity anchored in sanctum (`_bmad/memory/bmad-agent-{name}/`). Model resolution runs at each node entry via the three-level cascade.

Shared across lanes: one Postgres instance (with thread-namespace isolation), one LangSmith workspace (with run-tagging per lane), one OpenAI client pool (with cache-warmth shared implicitly at the OpenAI side per-model).

### Language & Framework Matrix

| Layer | Selection | Version Pin (Slab 1) | Rationale |
|---|---|---|---|
| Language | Python | **3.12+** | LangGraph runtime baseline; matches existing APP |
| Runtime orchestrator | `langgraph` (OSS, self-hosted) | pinned per Slab 1 | Decision — not LangGraph Platform |
| Graph primitives | `langchain` (just what LangGraph depends on) | pinned transitive | Core-only; avoid LangChain agent abstractions |
| LLM provider SDK | `langchain-openai` + `openai` | pinned per Slab 1 | OpenAI API across the fleet |
| State modeling | `pydantic` v2 | **v2.x**, latest minor | Inherited discipline; `validate_assignment=True` standard |
| Checkpointing | `langgraph-checkpoint-postgres` | pinned per Slab 1 | Selected over SQLite/memory; persistence + retention |
| Caching | OpenAI automatic prompt caching (no middleware) | N/A (API feature) | Stable sanctum/persona/references prefix cacheable; ~50% discount on cached input tokens |
| Observability | `langsmith` (client) | pinned per Slab 1 | LangSmith trace emission per node |
| IDE bridge | MCP (Model Context Protocol) | spec-pinned | Existing `.mcp.json`/`.cursor/mcp.json` infrastructure reused |
| Escape-hatch API | `fastapi` | pinned per Slab 1 | Local-only endpoints for non-MCP clients (rare) |
| Persistence DB | PostgreSQL | **15+** | Cleanup + retention policy queries require modern Postgres |
| Dependency manager | `uv` (preferred) / `pip` | per Slab 1 lock | `uv` for speed; `pip` accepted for legacy scripts |

Lock files (`uv.lock` or `pip-tools` output) committed in clone. Dependency upgrades = governance tickets (Tier-1/2/3 per pack-version-analog policy).

Frameworks explicitly **out of scope** (Decision — research doc):
- `langserve` (deprecating direction in 2026)
- LangGraph Platform (managed service) — self-hosted chosen for sovereignty + hybrid bridge architecture
- LangChain high-level agent abstractions (`AgentExecutor`, `initialize_agent`) — cage-risk
- `AnthropicPromptCachingMiddleware` + `langchain-anthropic` — provider superseded by OpenAI decision
- Celery / Ray / Dask for distribution — single-operator scale

### Installation Methods (Dev Ramp-Up)

The clone is a fully working repo. Dev ramp on the clone:

1. **Clone + branch.** `git clone <repo>; git checkout dev/langchain-langgraph-foundation`
2. **Python env.** `uv venv .venv --python 3.12; source .venv/bin/activate` (or `python -m venv`)
3. **Dependencies.** `uv pip install -r requirements.lock` (or `pip install -r`). Slab 1 ships the lockfile.
4. **Postgres (local).** `docker compose up -d postgres` (docker-compose included in clone; Postgres 15+ image). Slab 1 ships the compose file + init SQL.
5. **LangSmith (optional but recommended).** `export LANGSMITH_API_KEY=…; export LANGSMITH_PROJECT=course-dev-ide-migration`
6. **OpenAI API key.** `export OPENAI_API_KEY=…`
7. **Model registry check.** `uv run python -m app.models.registry_check` — verifies all models in `app/models/registry.yaml` are reachable; fails loudly if a model ID has been deprecated.
8. **Run the empty-graph smoke test.** `uv run python -m app.smoke_test` — runs the empty manifest-loaded graph through 15 steps; operator decides every gate via CLI prompts; Marcus runs on its default reasoning model.
9. **Bring up the IDE bridge.** `uv run python -m app.runtime_server` — starts the persistent LangGraph runtime + FastAPI + MCP server. The IDE connects via `.mcp.json`.
10. **Smoke test from IDE.** Marcus's "hello, trial run" flow works against the empty graph.

This ramp is a **Slab 1 acceptance artifact** (the run-through, plus the docs: `docs/dev-guide/langgraph-runtime-setup.md` and `docs/dev-guide/model-selection-guide.md`).

### API Surface (What Extensions Touch)

For dev agents and specialist authors, the runtime exposes a narrow surface:

1. **Specialist extension surface (`app/specialists/`).** Each specialist is a subdirectory with: `graph.py` (9-node scaffold instantiation), `state.py` (Pydantic envelope/return), `expertise/` (L5 references), `sanctum/` (symlink to `_bmad/memory/bmad-agent-{name}/`), `model_config.yaml` (three-level selection defaults per node). Generator `bmad-create-specialist` emits this shape.
2. **MCP tool surface (`app/mcp_server/tools/`).** Tools exposed to the IDE: `trial_run.start`, `trial_run.resume`, `trial_run.fork`, `trial_run.replay`, `specialist.invoke`, `gate.decide`, `state.inspect`, `model.override`. Plus per-thread resources: `thread://run/{trial_id}`, `thread://dev/{story_id}`.
3. **FastAPI escape-hatch surface (`app/http/`).** Local-only endpoints for non-MCP scenarios (CI invocation, headless scripts). Not exposed beyond localhost by default.
4. **DecisionCard schema (`app/gates/decision_card.py`).** Pydantic model. Every gate produces a DecisionCard; every operator verdict conforms to approve/edit/reject. Schema versioned; bumps are governance tickets.
5. **State base classes (`app/state/base.py`).** `RunState`, `StoryState`, `SpecialistEnvelope`, `SpecialistReturn`. Specialists and gate nodes consume and emit these.
6. **Model selection surface (`app/models/`).** `registry.yaml` (available models), `selection_policy.yaml` (auto-select rules), `selector.py` (resolution cascade logic), `adapter.py` (thin wrapper over `ChatOpenAI`). Specialists do not talk to OpenAI directly — they resolve through the adapter.
7. **Learning-event ledger emitter (`app/ledger/`).** Idempotent side-effect node. Emits at G2C/G3/G4. Failure to emit does not fail the gate; drift is detected by the ledger's own audit.

Extension authors read `docs/dev-guide/runtime-extension-surface.md` + `docs/dev-guide/model-selection-guide.md` (both Slab 1 deliverables) before writing against these APIs.

### Code Examples (Canonical Scaffolds)

Three canonical examples ship with the migration for new developers to learn against:

1. **The 9-node specialist scaffold (`app/specialists/_scaffold/`).** Reference implementation: `plan → enter_sanctum → load_expertise → reason → act → validate → emit → return → exit_sanctum`. Includes a reference `model_config.yaml` showing all three resolution levels. New specialists extend or adapt (not rewrite) this.
2. **The DecisionCard gate example (`app/gates/example_gate/`).** A reference `interrupt()` node producing a canonical DecisionCard, showing: evidence inclusion, risk articulation, approve/edit/reject handling, state mutation on verdict, and cache-invalidation warning on runtime model override.
3. **The Wondercraft specialist (`app/specialists/wondercraft/`).** The first non-migrated specialist — built end-to-end using the scaffold + generator. Doubles as the generalization test for the innovation pattern. Uses the `gpt-4.1-mini` fast-and-cheap tier by default. Ships by Slab 2 close.

All three are linked from `docs/dev-guide/runtime-extension-surface.md` with explicit annotations about which parts must remain invariant and which parts are extension points.

### Migration Guide (Primary Repo → Clone)

This is the load-bearing developer-facing artifact. It lives at `docs/dev-guide/langgraph-migration-guide.md` and is a **Slab 5 deliverable** (because it captures the realized migration, not the plan).

**Structure:**

1. **Conceptual map** — old shape → new shape. For every load-bearing invariant, "where it lived in primary repo" vs "where it lives in clone."
2. **Specialist migration walkthrough** — pick one real specialist (e.g., Irene) and show the before (`skills/bmad-agent-irene/`) vs after (`app/specialists/irene/`) — full side-by-side, including model-config evolution.
3. **Manifest → graph-config translation** — how `state/config/pipeline-manifest.yaml` becomes compile-time graph topology. Show the compiler.
4. **Gate migration** — how existing gate points (G1, G2C, G3, G4, §14, etc.) became `interrupt()` nodes. DecisionCard curation before/after.
5. **Schema migration** — existing Pydantic v2 schemas integrated into LangGraph state. Where `validate_assignment=True` and the four-file-lockstep discipline attach.
6. **Pipeline Lockstep regime → graph-compile-time CI** — how block-mode-trigger-paths migrated from pre-commit hook to CI graph-compile failure.
7. **Frozen-graph-version ceremony** — how to bump v42 → v43 properly. Who decides (governance).
8. **Forward-port playbook** — how to forward-port primary-repo changes (Epic 33/34 features, Lesson Planner MVP patterns, etc.) into the clone at Slab-5 close.
9. **Model-selection cutover notes** — how each specialist's `model_config.yaml` was chosen, cache-hit-rate measurements by tier, rationale for tier defaults.
10. **Rollback plan** — if the migration is rejected at go/no-go (see PRD §Go/No-Go Gates, later step), how to return to the primary-repo-only world. Not expected, but documented.
11. **Appendix: Anti-patterns catalog** — harvested during Slab 2. Five named anti-patterns + their counter-patterns. Explicit examples from the migration.

### Implementation Considerations

- **Dev-lockstep with pack-version-analog policy.** Runtime graph versions, manifest versions, pack versions, and **model registry** versions move in lockstep with the existing Tier-1/2/3 policy. Tier-3 changes require party-mode consensus + operator sign-off; Tier-2 require single-gate party-mode; Tier-1 proceed under dev-agent authority.
- **Test-layer discipline per slab.** Slab 1 ships unit (Pydantic state + model selector) + integration (empty-graph-through-15-steps). Slab 2 ships specialist-scaffold-conformance tests + model-selection-cascade tests. Slab 3 adds graph-replay tests. Slab 4 adds CI graph-compile-failure tests. Slab 5 adds trial-replay regression suite + model-cost-projection acceptance. Four-layer strategy green at Slab 5 close.
- **Idempotency at the node level.** Specialist `act` nodes are idempotent by construction (retries don't double-side-effect). Learning-ledger emission is idempotent. Gate `interrupt()` nodes are idempotent on re-enter. Node idempotency is a scaffold-conformance assertion.
- **Subgraph composition pattern: isolated state with `Send` fan-out.** Default is isolated state per specialist subgraph. `Send` is used for fan-out patterns (e.g., parallel specialist queries). No shared mutable state across subgraphs.
- **Pydantic + LangGraph RetryPolicy workaround.** A known interaction issue — Pydantic-validated state can interact poorly with LangGraph retry wrappers. Slab 4 ships the documented workaround pattern.
- **LangGraph Issue #2581 (fan-out/subgraph aggregation).** Known open issue at time of research. Slab 2 captures the current workaround in the scaffold.
- **Single-operator scale.** The system is sized for one concurrent operator, one primary production stream, periodic dev-graph runs. No multi-tenant concerns. Postgres sizing: small (10s of MB of checkpoint state per month). LangSmith usage: well within free-tier / low-tier pricing for a single operator.

### Sections Intentionally Skipped

Per the `developer_tool` CSV guidance (and confirmed against the APP's true shape), these are out of scope for this PRD:

- **Visual design / brand styling** — the APP's output *artifacts* (narration, visuals) are produced by specialists against Storyboard B + prompt packs. The *runtime platform* has no UI beyond the IDE (which is Claude Code's UI, not something we design). Store/app compliance also N/A.
- **Store compliance** — no app store, no extension marketplace, no SaaS compliance regime.
- **User journeys for end-users-of-the-SDK** — already covered in §User Journeys at the operator + specialist-developer + BMAD-reviewer + CI granularities. No external SDK users to journey-map.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach: Platform MVP (not experience MVP).** The operator-facing experience of running a trial already exists and works in the primary repo. What doesn't exist is the *platform* — the persistent runtime that makes runs pausable, forkable, replayable, and reproducible. The MVP therefore delivers a working **platform substrate** that achieves parity-or-better with the current experience, not a new experience.

**Resource Requirements:** Single operator (Juanl) + BMAD dev agents (Amelia, Diego) + specialist subagents invoked per-story. No additional humans required. External dependencies: OpenAI API account (billing visible to operator), Postgres 15+ (local Docker), LangSmith account (free tier sufficient at single-operator scale).

**Philosophical commitment:** MVP ≠ "minimal viable product" here. MVP = **minimum viable platform for parity-or-better**. Cutting below parity is not an option — it invalidates the migration's core premise (preserve invariants while changing the substrate). Cutting *scope beyond parity* (e.g., fork UX polish, economics dashboard richness) is on the table under pressure; cutting *invariants* is not.

### MVP Feature Set (Phase 1) — The Five Slabs

**Core user journeys supported by end of MVP (Slab 5 close):**
- Journey 1 (run survives IDE close) — **load-bearing, non-cuttable**
- Journey 2 (fork from checkpoint) — **load-bearing, non-cuttable** at functional level; fork UX polish is cuttable to a CLI-only interface if time-pressured
- Journey 3 (specialist in <1 dev-day) — **load-bearing, non-cuttable** (proves the plug-and-play claim)
- Journey 4 (trace-first gate review) — **load-bearing, non-cuttable** functionally; reviewer workflow richness is cuttable
- Journey 5 (CI rejects drifted PR at graph-compile) — **load-bearing, non-cuttable**

**Must-have capabilities (the MVP bar):**

| Slab | Must-Have (non-cuttable under pressure) | Cut-candidate (under pressure, deferred to Growth) |
|---|---|---|
| **1 — Substrate** | Persistent LangGraph runtime, Postgres checkpointing, OpenAI automatic cache, MCP bridge, empty-graph-through-15-steps, Pydantic state base classes, `app/models/` (registry + adapter + selector), LangSmith tracing | Rich economics dashboard (can ship as CLI-only metric dump; web UI deferred) |
| **2 — Specialists** | 9-node scaffold, `bmad-create-specialist` generator, 17 specialist migrations, Wondercraft pilot producing real artifact, sanctum cold-load integrity tests, scaffold-conformance tests, **model_config.yaml per specialist** | Specialist-anti-patterns catalog depth (5 anti-patterns minimum; 8-10 is "nice") |
| **3 — Marcus** | Plan-and-Execute supervisor, routing, DecisionCard at every gate, runtime model-override surface, §01→§15 end-to-end | DecisionCard UX richness (operator can approve/edit/reject via CLI; IDE-side rich-text rendering deferred) |
| **4 — Gates & Lockstep** | CI graph-compile-time lockstep enforcement, Cora dev-graph, party-mode-as-`interrupt()`, frozen-graph-version ceremony, learning-event ledger | Learning-ledger analytics richness (schema emission is non-cuttable; cross-run analytics deferred) |
| **5 — Trial-Run & Polish** | Trial-replay regression test suite, head-to-head parity validation with new tracked trial, cost-projection acceptance measurement, sanctum invalidation hook | Fork UX polish (MVP is CLI; IDE-integrated fork UX deferred to Growth) |

### Operator-Approvable Milestones (Inter-Slab Gates)

Five inter-slab gates, each requires **explicit operator approval** before the next slab opens. These are the migration's version of the existing HIL gate pattern — applied at the slab level, not the step level.

**Milestone M1 — Slab 1 Close: "Runtime substrate is real"**
- **Required evidence (dev delivers; operator reviews):**
  - Empty manifest-loaded graph completes §01→§15 end-to-end via CLI (recording of the run + log output)
  - `uv run python -m app.smoke_test` passes on fresh clone
  - Postgres checkpoint retention + cleanup policy demonstrable
  - OpenAI prompt-cache hit rate **≥60%** on a second run (measured, not asserted)
  - LangSmith trace shows per-node execution + token cost
  - Model registry + adapter + selector unit tests green
  - `docs/dev-guide/langgraph-runtime-setup.md` + `docs/dev-guide/model-selection-guide.md` complete and usable by a hypothetical new dev
- **Operator decision:** *Go* (open Slab 2) / *Revise* (iterate on Slab 1 with specific findings) / *Halt* (migration go/no-go re-evaluation)

**Milestone M2 — Slab 2 Close: "Plug-and-play specialist claim validated"**
- **Required evidence:**
  - All 17 existing specialists migrated + scaffold-conformance tests green
  - `bmad-create-specialist` generator works end-to-end on a fresh specialist
  - **Wondercraft pilot produces a real podcast artifact** against live Wondercraft API (the proof of the plug-and-play claim)
  - Wondercraft story time-from-open to first-real-artifact **< 1 dev-day** (or documented variance with root cause)
  - Specialist-anti-patterns catalog: ≥5 concrete anti-patterns harvested from migration (not invented)
  - BMAD code-review MUST-FIX rate per specialist story **declining trend** visible over Slab 2
- **Operator decision:** *Go* / *Revise* / *Halt*

**Milestone M3 — Slab 3 Close: "Marcus orchestrates end-to-end"**
- **Required evidence:**
  - New tracked trial run §01→§15 completes with Marcus as supervisor (specialist quality may lag primary; parity is not the bar yet)
  - DecisionCard produced at every gate, consumable by operator
  - Operator can approve/edit/reject at every gate via CLI (IDE integration optional at this milestone)
  - Runtime model-override surface functional: operator can force a specific model per node
  - Marcus locked to reasoning tier in production config; override works for debug
- **Operator decision:** *Go* / *Revise* / *Halt*

**Milestone M4 — Slab 4 Close: "Governance regime is architectural"**
- **Required evidence:**
  - CI graph-compile-time lockstep enforcement: an intentionally drifted PR is **rejected at CI**, not just pre-commit (demo'd)
  - Cora dev-graph compiles as sibling with separate thread namespace
  - Party-mode-as-`interrupt()` works for at least one real story gate (captured in LangSmith trace)
  - Frozen-graph-version ceremony codified in `docs/dev-guide/frozen-graph-version-ceremony.md`
  - Learning-event ledger captures events at G2C/G3/G4 in a tracked run
  - Pydantic + RetryPolicy workaround documented and tested
- **Operator decision:** *Go* / *Revise* / *Halt*

**Milestone M5 — Slab 5 Close: "Migration ships" (this is the go/no-go gate)**
- **Required evidence (the full acceptance surface):**
  - Trial-replay regression test suite covering 100% of closed tracked trial runs
  - **Head-to-head parity validation:** a new tracked trial run (`C1-M1-PRES-<date>`) reaches parity-or-better against primary repo for the same input content (operator signs off)
  - Cost-projection measurement: **≥50% total token-cost reduction** per trial run vs. current IDE-Marcus baseline (measured, with tier-routing + cache-hit breakdown)
  - Cache hit rate **≥80% median** on production preset
  - Fork UX usable (CLI minimum; IDE integration if possible)
  - Sanctum invalidation hook functional
  - 15-invariant audit matrix: every load-bearing invariant has named preserving implementation pattern with file/test reference
  - Migration guide (`docs/dev-guide/langgraph-migration-guide.md`) complete with all 11 sections
  - Specialist-anti-patterns catalog at ≥5 concrete entries (min); harvested from migration, not invented
- **Operator decision:** *Ship* (declare migration complete; backports close; forward-ports batched; primary repo becomes frozen reference) / *Iterate* (specific-finding remediation, new M5 target date) / *Rollback* (decline the migration; primary repo continues; clone archived)

### Post-MVP Features

**Phase 2 (Growth — 3–6 months post-M5):**
- Rich economics dashboard (web UI; beyond the Slab-5 CLI metric dump)
- IDE-integrated fork UX (beyond CLI fork tooling)
- Schedulable/headless trial runs (cron-triggered; overnight replay sweeps)
- Trace-first review workflow UX refinement (beyond "reviewer opens LangSmith trace by hand")
- New specialist fleet: Canvas, Qualtrics, other media/service specialists at API-contract speed
- Cross-run learning-ledger analytics (patterns extracted across closed runs)
- Primary repo retirement ceremony (when operator is ready — no fixed date)
- Specialist-anti-patterns catalog depth expansion beyond Slab-2 minimum of 5

**Phase 3 (Expansion — 6–12 months post-M5):**
- Multi-operator collaboration (checkpointed state + DecisionCards asynchronously reviewable)
- Specialist marketplace pattern (cross-project portability)
- LangGraph runtime upgrade governance tickets (Tier-1/2/3 for framework itself)
- Learning-ledger-driven scaffold evolution (empirical scaffold changes from closed-trial patterns)
- Multi-pipeline topology (non-course domains reusing substrate + scaffold + sanctum pattern)
- Optional provider expansion (Anthropic re-introduction via adapter, or Google/Mistral) — contained change via `app/models/adapter.py`

### Timeline Projection (Go/No-Go Inputs)

| Slab | Wall-Clock (weeks) | Cumulative | Elastic Range |
|---|---|---|---|
| 1 — Substrate | 2–3 | 2–3 | +1 week on Postgres ops complexity; -0 (no cut below full stack) |
| 2 — Specialists | 4–6 | 6–9 | +2 weeks if scaffold iteration is more than expected; -1 week if parallel dev capacity > planned |
| 3 — Marcus | 2 | 8–11 | +1 week on DecisionCard schema iteration; -0 |
| 4 — Lockstep & Gates | 2–3 | 10–14 | +1 week on CI integration complexity; -0 |
| 5 — Trial & Polish | 2 | 12–16 | +1 week if head-to-head parity iteration needed; -0 |

**Planned range: 12–16 weeks total.** Slab 2 is the pivot — that's where parallelism matters.

**Deviation triggers:**
- **>20% cumulative slip (≥3 weeks):** Replan required. Slab-level scope re-evaluation with operator. Use BMAD party-mode if root cause is unclear.
- **>50% cumulative slip (≥8 weeks):** Migration go/no-go re-evaluation with operator. On the table: defer, reduce scope, or halt.

### Cost Projection (Go/No-Go Inputs)

**Token-cost model assumptions:**
- Baseline: current IDE-Marcus all-flagship estimated trial-run cost (measured during Slab 1; placeholder until then: call it `$B` per trial run).
- Post-migration: compound of two levers applied on top of `$B`.

**Lever 1 — OpenAI prompt cache discount on stable prefix:**
- Cached input tokens cost ~50% of non-cached input tokens.
- Sanctum/persona/references prefix estimated at ~60–70% of each specialist's input context per invocation (inherited from sanctum cold-start discipline).
- At Slab-5-target cache hit rate (≥80% median), realized discount on input-token cost: ~25–30%.

**Lever 2 — Model-tier routing:**
- Marcus on reasoning tier (expensive); most specialists on `gpt-4.1` / `gpt-4.1-mini`; boundary nodes on `gpt-4.1-nano` or `gpt-4o-mini`.
- Aggregate token-cost reduction vs. all-flagship baseline: ~30–40% (driven primarily by specialist workhorse tier being ~4–5× cheaper than flagship on comparable tasks).

**Compound projection (conservative):**
- Total token-cost reduction per trial run: **≥50%** of baseline `$B`.
- Concrete acceptance target at M5: measured reduction ≥50% on a head-to-head parity trial.
- Stretch target: ≥60% if cache hit rate exceeds 80% and tier routing is aggressive.

**Non-token costs:**
- Postgres local: $0 (Docker on operator's machine).
- LangSmith: $0–$39/month at single-operator volume (free tier or Plus tier).
- LangGraph OSS: $0.
- **Dev labor:** the full cost. 12–16 weeks × (operator orchestration + BMAD dev agent invocations + party-mode + code-review). Dominant cost; outside token economics.

**Go/no-go financial bar:**
- If measured token-cost reduction at M5 is <30%, operator declares *revise* or *rollback*. (Below 30% reduction, the token-cost argument alone doesn't justify migration; value has to come entirely from platform properties — defensible if operator chooses, but not the premise.)
- If measured token-cost reduction at M5 is ≥50%, the cost argument is validated and *ship* is the expected decision barring other findings.

### Risk Mitigation Strategy (Scope-Level)

**Technical Risks**
- **Risk: OpenAI prompt-cache hit rate falls below ≥60% at Slab-1 acceptance** (automatic caching less tuneable than Anthropic middleware). **Mitigation:** Prefix-stability audit in Slab 1 — identify sources of prefix variation (e.g., timestamp injection, sanctum mutation). Sanctum invalidation hook (Slab 5) prevents unintentional cache breaks. If <60% persists after audit, operator can choose: (a) accept lower target + higher cost, (b) fall back to an Anthropic-middleware evaluation as a mitigation option (scope-expansion — triggers Tier-3 governance).
- **Risk: Three-level model-selection cascade complexity creates debug drag.** **Mitigation:** Selector is deterministic (not LLM-based); every resolution logs (node, level, chosen, fallback trail) in LangSmith trace. Runtime override visible in DecisionCard UX so operator sees current model at every gate.
- **Risk: Specialist-migration time blows past 4–6 weeks for Slab 2.** **Mitigation:** The scaffold + generator IS the mitigation. If time still blows past, parallelize across dev agents (Amelia + Diego + specialist subagents); defer Wondercraft pilot to Slab 5 polish if necessary (but the "plug-and-play" claim then validates in Slab 5, not Slab 2).

**Market Risks (for the APP, not external market)**
- **Risk: Primary repo ships a significant feature mid-migration (e.g., Epic 33/34 major) that blocks forward-port at M5.** **Mitigation:** Backports close after Slab 1 opens. Forward-ports batch at M5. Operator coordinates primary-repo epic cadence — avoid major structural changes during Slabs 2–4. If unavoidable, specific forward-port work becomes a named Slab-5 item with scope impact.
- **Risk: Lesson Planner MVP evolution in primary repo creates schema-shape drift that complicates forward-port.** **Mitigation:** Lesson Planner schema-shape patterns (scaffolds under `docs/dev-guide/scaffolds/schema-story/`) remain authoritative during migration. Clone does not modify those patterns unilaterally; forward-ports inherit them as-is.

**Resource Risks (single operator, no surge capacity)**
- **Risk: Operator unavailable mid-migration** (medical, family, other obligation). **Mitigation:** Checkpointed state in Postgres means work pauses cleanly. The clone does not rot during operator absence. Backports remain closed; forward-port window simply extends.
- **Risk: BMAD dev agent capacity (Amelia + Diego) is shared with primary-repo production.** **Mitigation:** Explicit slab-level scheduling — Slab 2 is the capacity-heavy slab; operator coordinates primary-repo story-cadence to free Amelia/Diego for Slab 2 weeks. Slabs 1, 3, 4 are lower-capacity and can run alongside primary-repo work.
- **Risk: Contingency scope-cut if resources drop.** **Mitigation:** The MVP table above already names cut-candidates per slab. Non-cuttable items are the invariants + parity surface; cut-candidates are UX polish, dashboard richness, catalog depth.

## Functional Requirements

The capability contract for this migration. Every downstream artifact (architecture, epic, story, story-cycle test, PR) must trace to at least one FR. Capabilities not listed here will not exist in the migrated runtime unless explicitly added via PRD revision.

### 1. Runtime Platform

- **FR1:** The runtime can host a compiled LangGraph application as a persistent local service, independent of any IDE session.
- **FR2:** The runtime can accept client connections from the IDE (via MCP) and from local CLI/scripts (via FastAPI), both concurrently.
- **FR3:** The runtime can checkpoint every graph-node state transition to PostgreSQL via `langgraph-checkpoint-postgres`.
- **FR4:** The runtime can resume any thread from its last checkpoint after runtime restart, operator absence, or IDE disconnection.
- **FR5:** The runtime can enforce a configurable checkpoint retention policy (cleanup + archive + audit-preservation).
- **FR6:** The runtime can emit per-node execution traces to LangSmith, including model selected, token counts, cache hit/miss, and execution duration.
- **FR7:** The runtime can be started, stopped, and health-checked via a Python entry-point (`python -m app.runtime_server`) without external orchestration tooling.
- **FR8:** The runtime can load its graph topology from the pipeline manifest (`state/config/pipeline-manifest.yaml`) at compile time, not at invocation time.

### 2. Specialist Framework

- **FR9:** A specialist can be instantiated from a fixed 9-node scaffold: `plan → enter_sanctum → load_expertise → reason → act → validate → emit → return → exit_sanctum`.
- **FR10:** A specialist can anchor its identity in a sanctum directory (`_bmad/memory/bmad-agent-{name}/`) containing INDEX.md, PERSONA.md, chronology.md, and access-boundaries.md.
- **FR11:** A specialist can load its sanctum from disk on every cold invocation without carrying in-memory continuity between invocations (Sacred-Truth cold-read).
- **FR12:** A specialist can declare its expertise across a 9-layer stack (L0 LLM training → L1–L4 sanctum identity → L5 domain references → L6 operational context → L7 MCP tools → L8 runtime envelope).
- **FR13:** A specialist can be generated from scratch via `bmad-create-specialist` with scaffold, sanctum stub, typed envelope/return models, scaffold-conformance test, and specialist-registry entry emitted together.
- **FR14:** A specialist can pass a scaffold-conformance test that asserts node count, node shape, envelope contract, sanctum cold-read integrity, and node idempotency.
- **FR15:** A specialist can be invoked as a subgraph with isolated state from any parent graph (Marcus run-graph, Cora dev-graph, or test harness).
- **FR16:** A specialist can expose its capabilities to external systems via MCP tools registered at L7 of its expertise stack.

### 3. Model Selection

- **FR17:** Every LLM-invoking node can resolve its model via a three-level cascade: runtime override → per-agent configured default → auto-select (system recommended).
- **FR18:** Every specialist can declare a `model_config.yaml` specifying default model per node, or the literal `auto` to defer to auto-select.
- **FR19:** The operator can pass a runtime model override per node at trial-run start, at gate resume, or at fork-from-checkpoint.
- **FR20:** Marcus's plan/supervisor nodes can be locked to the best available OpenAI reasoning model in production config, with operator-override permitted for debugging.
- **FR21:** The auto-select function can pick a model deterministically given `(agent, node_role, context_tokens, quality_tier, budget_tier)` inputs, with no LLM call involved.
- **FR22:** Every model resolution can be logged to LangSmith with node, resolution level, chosen model, and fallback trail.
- **FR23:** The model registry (`app/models/registry.yaml`) can be versioned and updates can be governed by Tier-1/2/3 policy (mirroring pack-versioning).
- **FR24:** The runtime can warn the operator of cache-invalidation impact before applying a mid-run runtime model override.
- **FR25:** A provider adapter (`app/models/adapter.py`) can isolate `ChatOpenAI` so provider swaps are contained changes, not scaffold rewrites.

### 4. Marcus Orchestration

- **FR26:** Marcus can operate as the Single Point of Contact (SPOT) for the operator — no specialist is operator-facing except via Marcus delegation.
- **FR27:** Marcus can run a Plan-and-Execute reasoning loop by default, switching to ReAct only when the `explore` quality preset is selected.
- **FR28:** Marcus can route work to specialists based on the manifest-defined step topology, not inline reasoning.
- **FR29:** Marcus can delegate to any specialist in the active specialist registry via a routing-edge decision, not via code-embedded selection.
- **FR30:** Marcus can cold-read its own sanctum on every session open, per the Marcus-first activation protocol.

### 5. Gates and Human-in-the-Loop

- **FR31:** Every gate in the manifest can be realized as a `langgraph.interrupt()` node with a checkpointed payload.
- **FR32:** Every gate can produce a DecisionCard containing drafted specialist proposal, evidence, risks, and explicit approve/edit/reject verbs.
- **FR33:** The operator can consume a DecisionCard and emit a verdict (approve / edit / reject) via CLI, IDE (MCP), or FastAPI escape-hatch.
- **FR34:** A gate can block the graph until an operator verdict is received — there is no auto-approve, no auto-advance, no timeout-based override.
- **FR35:** A gate can resume the graph on verdict receipt, propagating the verdict payload into downstream state.
- **FR36:** The gate count per trial run can match the manifest 1:1, auditable at trial close.
- **FR37:** Reject-rate per gate can be tracked as a measurable KPI across trial runs.

### 6. Pipeline Lockstep and Governance

- **FR38:** The pipeline manifest can serve as the compile-time topology source — the runtime graph cannot be compiled without a valid manifest.
- **FR39:** A PR touching any `block_mode_trigger_path` can fail graph compilation at CI if the manifest, L1 check script, or pack contract are not updated in lockstep.
- **FR40:** Cora's dev-graph can be compiled as a sibling graph with a separate thread namespace (`dev/{story_id}`) and no lane crossover with Marcus's run-graph (`run/{trial_id}`).
- **FR41:** A party-mode gate can be realized as a `langgraph.interrupt()` node where multiple personas contribute via structured payload before operator verdict.
- **FR42:** A code-review gate can consume LangSmith traces as primary evidence alongside git diffs.
- **FR43:** The graph version (`runtime/graphs/v42/`, `v43/`, …) can be frozen on ship — once a tracked trial closes against a version, that version is immutable.
- **FR44:** Graph version bumps can be governed by Tier-1/2/3 policy: Tier-1 (patch) by dev-agent authority; Tier-2 (minor) by single-gate party-mode; Tier-3 (major) by full party-mode + operator sign-off.
- **FR45:** A learning-event ledger can emit structured events at gates G2C, G3, and G4 as idempotent side-effects that do not alter trial artifacts.

### 7. Trial-Run Discipline

- **FR46:** The operator can start a new trial run with a specified input content bundle and quality preset.
- **FR47:** The operator can pause a running trial by serializing thread state to Postgres; the runtime persists this state without IDE presence.
- **FR48:** The operator can resume a paused trial from any closed checkpoint, from the same or a different IDE session.
- **FR49:** The operator can fork a closed trial from any checkpoint, producing a sibling thread that inherits upstream state and re-executes only downstream dependent nodes.
- **FR50:** The operator can replay a closed trial from its final checkpoint, producing a byte-for-byte identical pack hash.
- **FR51:** A trial-replay regression test suite can cover 100% of closed tracked trial runs and fail on pack-hash drift.
- **FR52:** A new tracked trial run can be validated head-to-head against the primary-repo trial output for the same input content, with operator sign-off.
- **FR53:** The operator can inspect any thread's current state at any checkpoint without altering it (read-only inspection via MCP `state.inspect`).

### 8. Economics and Observability

- **FR54:** The runtime can measure and report the OpenAI prompt-cache hit rate per trial run, broken down by node and tier.
- **FR55:** The runtime can measure and report token cost per trial run, broken down by specialist, tier, and cache hit/miss.
- **FR56:** The runtime can compare post-migration per-trial cost against a recorded baseline and report the realized reduction percentage.
- **FR57:** The runtime can emit structured economics telemetry (cache hit rate + token cost + model tier distribution) consumable via CLI dump at Slab 5 minimum; via dashboard UI post-MVP.
- **FR58:** Every LLM invocation can be traceable in LangSmith to a specific node, specialist, and model.
- **FR59:** A sanctum invalidation hook can detect and log sanctum mutations that break prefix stability.

### 9. Migration Hygiene and Rollback

- **FR60:** Backports from clone to primary repo can be suspended after Slab 1 opens and can resume only at Slab 5 close (as forward-ports in the opposite direction).
- **FR61:** A forward-port playbook (`docs/dev-guide/langgraph-migration-guide.md` §8) can specify how primary-repo changes are integrated into the clone at Slab 5 close.
- **FR62:** A rollback plan (`docs/dev-guide/langgraph-migration-guide.md` §10) can specify how to return to the primary-repo-only operating model if M5 results in *rollback* instead of *ship*.
- **FR63:** A 15-invariant audit matrix can be produced at M5 naming the preserving implementation pattern for each invariant with file/test references.
- **FR64:** A specialist-anti-patterns catalog can harvest ≥5 concrete anti-patterns from the migration and publish them in `docs/dev-guide/specialist-anti-patterns.md`.
- **FR65:** The migration guide (`docs/dev-guide/langgraph-migration-guide.md`) can include 11 documented sections covering conceptual map, specialist walkthrough, manifest translation, gate migration, schema migration, lockstep CI, frozen-graph ceremony, forward-port playbook, model-selection cutover, rollback plan, and anti-patterns appendix.

### Capability-to-Slab Mapping (Summary)

| Capability Area | Primary Slab | FRs |
|---|---|---|
| Runtime Platform | Slab 1 | FR1–FR8 |
| Specialist Framework | Slab 2 | FR9–FR16 |
| Model Selection | Slabs 1–2 | FR17–FR25 |
| Marcus Orchestration | Slab 3 | FR26–FR30 |
| Gates and HIL | Slab 3 | FR31–FR37 |
| Pipeline Lockstep & Governance | Slab 4 | FR38–FR45 |
| Trial-Run Discipline | Slab 5 | FR46–FR53 |
| Economics & Observability | Slabs 1, 5 | FR54–FR59 |
| Migration Hygiene & Rollback | Slab 5 | FR60–FR65 |

**65 functional requirements, nine capability areas.** Every FR is testable. Every FR maps to at least one user journey, success criterion, or domain requirement. No FR prescribes HOW — only WHAT. This is the binding capability contract; downstream artifacts (architecture, epic breakdown, story specs) will trace to these FRs.

## Non-Functional Requirements

NFRs define *how well* the runtime must perform, not *what* it must do. Only categories relevant to this migration are listed. Accessibility is N/A (no end-user UI; operator interacts via Claude Code CLI + MCP). Scalability has a narrow single-operator scope and is folded into Reliability + Performance where relevant.

### Performance

- **NFR-P1:** A gate `interrupt()` node can present its DecisionCard to the operator within **5 seconds** of specialist proposal completion (DecisionCard curation + serialization + MCP transport budget).
- **NFR-P2:** The runtime can cold-start (process launch → accept-connection) in **under 10 seconds** on the operator's laptop-class hardware (target: Apple M-series or equivalent).
- **NFR-P3:** A checkpoint write to Postgres can complete in **under 500 ms** per node transition at the single-operator scale (trial-run state ~1–10 MB).
- **NFR-P4:** Sanctum cold-read per specialist invocation can complete in **under 200 ms** on local-disk (SSD) storage.
- **NFR-P5:** A full tracked trial run (§01→§15) can complete in **no more than 2× the current IDE-Marcus wall-clock time** for the same input content and quality preset. Parity-or-better is the Slab-5 bar; this NFR is the loosest acceptable upper bound under pressure.
- **NFR-P6:** Graph compilation at CI can complete in **under 60 seconds** for the current 15-step manifest + 17 specialists. Faster is better (keeps the block-mode CI check lightweight).

### Security

Single-operator local deployment. Security surface is narrow but non-zero:

- **NFR-S1:** API keys (`OPENAI_API_KEY`, `LANGSMITH_API_KEY`) can be loaded only from environment variables or `.env` files (never from committed source). `.env` files must not be tracked in git.
- **NFR-S2:** The FastAPI escape-hatch endpoint can bind only to `127.0.0.1` by default — no public network exposure without explicit configuration.
- **NFR-S3:** The MCP server can accept connections only from local processes by default.
- **NFR-S4:** Postgres can authenticate via password or local-trust in dev; production-equivalent deployments (if any future operator needs remote access) must use password + TLS — documented but not implemented during migration.
- **NFR-S5:** LangSmith traces can redact sensitive payload content on opt-in basis (per-node config). Default: no redaction (single-operator trust boundary). Operator can flip redaction on for a specific node if sensitive content enters the trace.
- **NFR-S6:** Trial artifacts and sanctum content can remain on operator-controlled storage. No third-party storage by default. LangSmith stores traces; operator can purge on request.
- **NFR-S7:** No multi-tenant concerns. The runtime does not perform cross-user authentication or authorization — it trusts the local operator.

### Integration

- **NFR-I1:** The runtime can tolerate transient OpenAI API errors (rate limits, 5xx responses) with exponential-backoff retry on a per-node basis, up to a configurable max-retry count. A fully failed LLM call surfaces as a node error, not a silent failure.
- **NFR-I2:** The runtime can tolerate LangSmith unavailability without blocking graph execution — trace-emission failures are logged but non-fatal.
- **NFR-I3:** The runtime can tolerate Postgres unavailability only by pausing the thread and surfacing the outage to the operator — graph execution must not continue without checkpointing.
- **NFR-I4:** MCP protocol compatibility can be pinned to a specific spec version in Slab 1; MCP-version bumps follow Tier-1/2/3 governance.
- **NFR-I5:** The retrieval substrate (Texas Shape 3-Disciplined retrieval contract) can integrate without modification — its contract is authoritative, and the runtime wires it into L7 MCP tools.
- **NFR-I6:** Sanctum file-system reliability — sanctum reads are treated as fatal-on-error (no specialist invocation proceeds without a complete sanctum cold-read). Missing or corrupt sanctum files fail fast.

### Reliability

- **NFR-R1:** Any node transition can be recovered from a checkpoint. The runtime can resume from the last successful checkpoint after crash, restart, or power loss.
- **NFR-R2:** All specialist `act` nodes can be idempotent — re-execution produces the same side-effects and the same output state.
- **NFR-R3:** All gate `interrupt()` nodes can be re-enterable — re-entering a gate after runtime restart produces the same DecisionCard payload.
- **NFR-R4:** Learning-event ledger emission can be idempotent — re-emission at the same node-thread-attempt key is a no-op.
- **NFR-R5:** The runtime's availability target is **operator-presence availability** — available when the operator is present. No 24/7 uptime requirement. Planned stops for upgrades are acceptable.
- **NFR-R6:** A trial run can survive ≥48 hours of pause (IDE closed, runtime potentially restarted) and still resume correctly from its last checkpoint.
- **NFR-R7:** The runtime can tolerate a clone-local corruption event (lost `.venv`, corrupted Postgres volume, lost LangSmith connection) without losing trial state — Postgres is the durable source; other layers are restorable.

### Reproducibility (domain-critical; non-stock NFR)

- **NFR-X1:** A closed tracked trial run's pack output can be byte-for-byte reproducible from its final checkpoint — `hash(replay(checkpoint)) == hash(original_output)`.
- **NFR-X2:** Graph versions can be frozen on first tracked-trial close. A frozen graph version cannot be edited; subsequent structural changes bump the version.
- **NFR-X3:** Sanctum content at trial-run time can be snapshotted into the checkpoint (or referenced by content hash) so that replay reproduces identical specialist behavior even if sanctum is later mutated.
- **NFR-X4:** Model selections made at trial-run time can be preserved in the checkpoint (including runtime overrides and auto-select fallback trails) — replay uses the same models to produce the same outputs.
- **NFR-X5:** OpenAI API non-determinism (temperature > 0 nodes) can be a known source of replay variance; trial-replay regression tests tolerate documented variance bands per node and fail on any un-documented drift.

### Maintainability (developer-tool category; load-bearing here)

- **NFR-M1:** Every specialist can pass a scaffold-conformance test — no specialist ships with a divergent internal shape.
- **NFR-M2:** Every specialist's `model_config.yaml` can be linted/validated at graph-compile time (valid model IDs, valid tier references, no dangling references).
- **NFR-M3:** The test-layer strategy can remain four-layer (unit / integration / end-to-end / trial-replay regression) through the migration. No layer can be excused for migration convenience.
- **NFR-M4:** K-floor story-cycle discipline can hold during migration — target 1.2–1.5× K test coverage per story, not 5×.
- **NFR-M5:** Pydantic-v2 four-file-lockstep discipline can hold for every schema-shape change in the migration (model module + JSON-schema emission + shape-pin test + golden fixture).
- **NFR-M6:** The specialist-anti-patterns catalog can be updated during Slab 2 as anti-patterns are encountered — the catalog is living, not retrospective.
- **NFR-M7:** The migration guide can be kept current during migration — each slab's closeout updates the guide's relevant sections before Milestone-approval.
- **NFR-M8:** Documentation under `docs/dev-guide/` can cover every extension point that a future dev or dev-agent will need (runtime setup, model selection, specialist creation, gate curation, frozen-graph ceremony).

### Observability (folded under existing FRs; quality bar called out here)

- **NFR-O1:** LangSmith tracing can capture every node execution with no sampling gap at single-operator volume — 100% trace coverage (cost is acceptable at this scale).
- **NFR-O2:** Economics telemetry (cache hit rate + token cost + model distribution) can be queryable per trial run without requiring a trace-replay pass.
- **NFR-O3:** Sanctum invalidation events can be surfaced to the operator as warnings (not failures) with a link to the suspected invalidating commit.
- **NFR-O4:** Model-selection resolution trails can be present in every LLM-invoking node's LangSmith span.

### Explicitly Out of Scope (for this migration; may reappear post-MVP)

- **Multi-operator concurrency** — single operator by design (Scalability scope).
- **Remote deployment** — local-only by design.
- **High-availability clustering / failover** — operator-presence availability is sufficient.
- **SOC 2 / ISO 27001 / similar compliance regimes** — no external data handling mandates.
- **WCAG / Section 508** — no end-user UI within scope.
- **GDPR / HIPAA / FERPA / COPPA** — no regulated data surfaces in the pipeline.
- **Sub-second latency targets for LLM invocations** — LLM response times are provider-bound and outside the runtime's control.
