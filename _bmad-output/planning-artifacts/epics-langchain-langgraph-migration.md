---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2026-04-22'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-04-22.md
workflowType: 'epics-and-stories'
project_name: 'course-DEV-IDE-with-AGENTS — LangChain + LangGraph Migration'
subject: 'Epic and story decomposition for the LangChain+LangGraph migration of the APP orchestration pipeline'
user_name: 'Juanl'
date: '2026-04-22'
branch: 'dev/langchain-langgraph-foundation'
fr_count: 65
nfr_count: 43
epic_count: 9
---

# course-DEV-IDE-with-AGENTS — LangChain + LangGraph Migration Epic Breakdown

## Overview

This document decomposes the migration PRD (65 FRs + 43 NFRs) and migration architecture (13 decisions + 15 invariants + full project tree) into nine epics and ~55 stories across five slabs with five operator-approvable milestones (M1–M5). Decomposition reflects:

- Architecture D10 — Slab 2 split into 2a (PR-R-conformant scaffold pilot) / 2b (14-specialist tranche) / 2c (Wondercraft + generator validation)
- Architecture D11 — Slab 5 split into 5a (Acceptance) / 5b (Polish)
- PR-R forward-port convergence from primary repo Sprint #1
- BMAD sprint governance inheritance (party-mode green-light + bmad-code-review + K-floor discipline + single-vs-dual-gate policy)

## Requirements Inventory

### Functional Requirements (65, extracted from PRD §Functional Requirements)

**Runtime Platform (FR1–FR8):** persistent LangGraph service, MCP+FastAPI concurrent clients, Postgres checkpointing, thread resume, retention policy, LangSmith traces, Python entry-point, manifest-as-compile-time-topology.

**Specialist Framework (FR9–FR16):** 9-node scaffold, sanctum directory anchoring, cold-read discipline, 9-layer expertise stack, `bmad-create-specialist` generator, scaffold-conformance test, subgraph isolated state, L7 MCP tool exposure.

**Model Selection (FR17–FR25):** three-level cascade (override → per-agent default → auto-select), per-specialist `model_config.yaml`, runtime override surface, Marcus locked to reasoning tier, deterministic auto-select, LangSmith resolution logging, registry Tier-1/2/3 governance, cache-invalidation warning on override (FR24), provider adapter isolation.

**Marcus Orchestration (FR26–FR30):** SPOT preservation, Plan-and-Execute/ReAct preset switching, manifest-driven routing, registry-driven delegation, sanctum cold-read on session open.

**Gates and HIL (FR31–FR37):** gates as interrupt() nodes, curated DecisionCard payloads, verdict via CLI/MCP/FastAPI, no-auto-approve (FR34), verdict resume + downstream propagation, gate count 1:1 with manifest (FR36), reject-rate KPI (FR37).

**Pipeline Lockstep & Governance (FR38–FR45):** manifest as compile-time topology source, CI graph-compile rejection on drift (FR39), Cora dev-graph sibling with separate thread namespace, party-mode-as-interrupt, code-review consumes traces (FR42), frozen graph versions, Tier-1/2/3 version governance, learning ledger at G2C/G3/G4.

**Trial-Run Discipline (FR46–FR53):** trial start with bundle + preset, pause via state serialization, resume from any checkpoint, fork-from-checkpoint, byte-for-byte replay, trial-replay regression suite (FR51), head-to-head parity with primary (FR52), read-only state.inspect (FR53).

**Economics & Observability (FR54–FR59):** cache hit rate per trial, token cost per trial, post-migration vs. baseline comparison, economics telemetry CLI (MVP) + dashboard (post-MVP), LangSmith per-LLM-invocation traceability, sanctum invalidation hook.

**Migration Hygiene & Rollback (FR60–FR65):** backport suspension after Slab 1 opens, forward-port playbook, rollback plan, 15-invariant audit matrix (FR63), specialist anti-patterns catalog ≥5 entries (FR64), migration guide 11 sections (FR65).

### Non-Functional Requirements (43, extracted from PRD §Non-Functional Requirements)

**Performance (6):** NFR-P1 DecisionCard ≤5s, NFR-P2 runtime cold-start ≤10s, NFR-P3 Postgres write ≤500ms, NFR-P4 sanctum cold-read ≤200ms, NFR-P5 trial ≤2× current wall-clock, NFR-P6 graph compile ≤60s.

**Security (7):** NFR-S1 `.env` discipline, NFR-S2 FastAPI 127.0.0.1 only, NFR-S3 MCP local-only, NFR-S4 Postgres password/TLS (dev/prod documented), NFR-S5 LangSmith redaction opt-in, NFR-S6 operator-controlled storage, NFR-S7 no multi-tenant.

**Integration (6):** NFR-I1 OpenAI transient retry, NFR-I2 LangSmith non-fatal, NFR-I3 Postgres-down → thread pause, NFR-I4 MCP pinned, NFR-I5 Texas retrieval unmodified, NFR-I6 sanctum fatal-on-error.

**Reliability (7):** NFR-R1 checkpoint recovery, NFR-R2 `act` idempotent, NFR-R3 `interrupt()` re-enterable, NFR-R4 ledger idempotent, NFR-R5 operator-presence availability, NFR-R6 ≥48hr pause survival, NFR-R7 clone-local corruption tolerance.

**Reproducibility (5, domain-critical):** NFR-X1 byte-for-byte replay, NFR-X2 frozen graph versions, NFR-X3 sanctum snapshot in checkpoint, NFR-X4 model selections preserved, NFR-X5 documented temp-variance bands.

**Maintainability (8, load-bearing):** NFR-M1 scaffold-conformance mandatory, NFR-M2 `model_config.yaml` lint-at-compile, NFR-M3 four-layer test strategy non-excusable, NFR-M4 K-floor 1.2–1.5×, NFR-M5 Pydantic four-file-lockstep, NFR-M6 living anti-patterns catalog, NFR-M7 migration guide kept current, NFR-M8 `docs/dev-guide/` comprehensive.

**Observability (4):** NFR-O1 100% LangSmith coverage, NFR-O2 economics queryable without replay, NFR-O3 sanctum invalidation warnings, NFR-O4 model-resolution trails in every LLM span.

### Additional Requirements (from Architecture)

From architecture D1–D13 + amendments A–I, these concrete implementation requirements flow into story ACs:

- **A1 — Lane separation via import-linter** (architecture D6 + Amendment A). `pyproject.toml::[tool.importlinter]` contract enforces `app.marcus` ⊥ `app.cora` with no direct or indirect import paths; CI fails on violation.
- **A2 — Package-to-FR traceability maintained as living doc** (Amendment B). Architecture §Requirements-to-Component Matrix is the authoritative table; every new package MUST add a row citing justifying FR(s) + first-use slab.
- **A3 — Canary tests in all four test tiers at Slab 1** (Amendment C). `tests/end_to_end/test_harness_contract.py` + `tests/trial_replay/test_harness_contract.py` pass from Slab 1; `trial_replay/README.md` pins harness contract.
- **A4 — Scaffold-conformance framework at Slab 1 with fixture specialist** (Amendment D). `tests/integration/scaffold_conformance/` harness + `tests/fixtures/specialists/fixture_minimal_specialist.py` green before any real specialist exists.
- **A5 — `docs/dev-guide/langgraph-state-idioms.md` as Slab 1 deliverable** (Amendment E). Six sections per Paige's outline; companion cross-refs from `pydantic-v2-schema-checklist.md` and schema-story scaffold README.
- **A6 — Story 1 split 1a/1b/1c** (Amendment F). Strict serial; no parallelism.
- **A7 — CLONE-FORK-NOTICE.md in every sanctum directory** (Amendment G). Slab 1 Story 1b AC — primary sanctum frozen at commit `<sha>`; no backport after Slab 1 close.
- **A8 — Survey-and-discard subsection** (Amendment H). Architecture doc contains explicit rejection rationale for langgraph-cli new, LangChain-AI reference apps, and LangGraph templates registry.
- **A9 — LangGraph idiom sanity check** (Amendment I). Half-dev-day throwaway `StateGraph + MemorySaver` mini-example against `app/runtime/` + `app/state/` abstractions before Slab 1 closes. Not committed.
- **A10 — Sanctum fingerprint snapshot** (D1 Hybrid). `SanctumFingerprint` model + `NodeCheckpoint.sanctum_fingerprints` + trial-close snapshot archival. Live disk canonical; replay fallback with provenance logging.
- **A11 — Three-transport verdict parity** (D3 + D7). Identical `OperatorVerdict` accepted via MCP `gate.decide`, FastAPI `POST /gate/verdict`, CLI `app.marcus.cli gate decide`. Contract test green.
- **A12 — No-scheduler-import contract** (D3). Ruff custom check + import-linter reject `asyncio.sleep`, `threading.Timer`, `apscheduler.*`, `schedule.*` inside `app/gates/**`.
- **A13 — `app/models/selector.py` as sole cascade resolver** (D2). Single audit surface for LangSmith resolution trails (NFR-O4).
- **A14 — Per-specialist `model_config.yaml` lintable at graph-compile** (D2 + NFR-M2). Invalid model refs or `auto` targets fail graph compile.
- **A15 — Two manifests, one per lane** (D4). `state/config/pipeline-manifest.yaml` (Marcus) + `state/config/dev-graph-manifest.yaml` (Cora, Slab 4).
- **A16 — Manifest schema Tier-1/2/3 governance** (D6 + D8 + D13). Mirrors pack-version policy; registry + manifest + graph-version bumps inherit same discipline.
- **A17 — Reject-rate KPI + gate-inventory audit ledger queries** (D3 + FR36 + FR37). `app/ledger/queries.py` implements `reject_rate_per_gate` + `gate_inventory`.
- **A18 — Transport parity contract test** (D7). `tests/integration/transport_parity_test.py` submits identical `OperatorVerdict` through all three transports; asserts identical resumption state.
- **A19 — Sanctum watchdog invalidation hook** (D5 + FR59). `app/runtime/sanctum_watcher.py`, Slab 5; emits NFR-O3 warnings via ledger.
- **A20 — Frozen-graph v42/ stub at Slab 1; Slab 5 ship populates** (D8). Directory exists from Slab 1 Story 1b; filled at M5 ship.
- **A21 — Cross-slab governance protocol three-line AC on every slab-closing story** (D12). Invariant-preservation note + anti-pattern harvest + migration-guide-section update. Enforced at bmad-code-review gate.
- **A22 — PR-R forward-port reconciliation checklist in migration-guide §8** (PR-R convergence). Dispatch-registry schema, L1 validator as library function, receipt-shape sanctum-fingerprint field.
- **A23 — MCP in Slab 1 scope by default** (architecture open question resolved). Seven-package Slab 1 layout: `app/runtime/`, `app/models/`, `app/state/`, `app/manifest/`, `app/http/`, `app/mcp_server/`, and a Marcus stub sufficient for smoke test routing. Operator can override at epic-kickoff.

### UX Design Requirements

**Not applicable.** PRD classifies project as `developer_tool`; no traditional UX surface. UX-adjacent decisions (DecisionCard rendering, fork UX, economics dashboard, state inspection, model-override UX, cache-invalidation warning) are all captured as FRs or within architecture D7 (operator-surface contract / §Developer-tool-UX) — not as a separate UX document. See architecture §Decision D7 for the full operator-surface contract.

### FR Coverage Map

See architecture §Requirements-to-Component Matrix for full FR→component map (spot-checked; every FR has a component + a slab). Epic-level coverage below:

| Epic | FR Range | NFR Focus |
|---|---|---|
| 1 — Slab 1 Substrate | FR1–FR8 + FR17–FR25 + FR54 + FR58 + FR59 (stub) + partial FR60 | NFR-P2/P3/P4/P6, NFR-S1/S2/S3, NFR-R1/R7, NFR-X2 (stub), NFR-M1/M2/M3/M5/M8, NFR-O1/O4 |
| 2a — Scaffold Pilot (3 PR-R-conformant edges) | FR9–FR16 applied to 3 specialists (Irene Pass 2, Kira motion, Texas) | NFR-M1 + NFR-I5 (Texas) + NFR-M6 (harvest begins) |
| 2b — Specialist Tranche (14 specialists) | FR9–FR16 applied to remaining 14 | NFR-M1 + NFR-M4 + NFR-M6 primary harvest |
| 2c — Wondercraft Pilot | FR13 + FR14 + FR16 (generator validation) | NFR-M6 + FR64 ≥5 catalog entries |
| 3 — Marcus Orchestration | FR26–FR30 + FR31–FR37 + FR19 + FR24 | NFR-P1 + NFR-R3 + NFR-R5 + NFR-M7 |
| 4 — Lockstep + Gates + Cora | FR38–FR45 + FR42 + FR22 (policy) + FR59 (Slab 4 portion) | NFR-I4 + NFR-R4 + NFR-X2 + NFR-M7 |
| 5a — Acceptance | FR49–FR52 + FR55–FR57 + FR63 + FR64 | NFR-X1 + NFR-X3 + NFR-X4 + NFR-X5 |
| 5b — Polish | FR65 + FR57 (dashboard) + fork-UX polish + generator-polish | NFR-M7 + NFR-M8 |

## Epic List

1. **Epic 1 — Slab 1 Substrate: Runtime + Models + Manifest + Bridges + Docs** — M1 go/no-go gate
2. **Epic 2a — Slab 2a Scaffold Pilot: PR-R-Conformant Specialists** (Irene Pass 2 + Kira motion + Texas)
3. **Epic 2b — Slab 2b Specialist Tranche: 14 Non-Conformant Specialists** (Gary, Vera, Quinn-R + 11)
4. **Epic 2c — Slab 2c Wondercraft Pilot + Generator Validation + Anti-Patterns Catalog** — M2 go/no-go gate
5. **Epic 3 — Slab 3 Marcus Orchestration: Supervisor + Gates + DecisionCards + Three-Transport Verdict** — M3 go/no-go gate
6. **Epic 4 — Slab 4 Lockstep + Gates + Cora Dev-Graph + Ledger + Frozen-Graph Ceremony** — M4 go/no-go gate
7. **Epic 5a — Slab 5a Acceptance: Trial-Replay Regression + Head-to-Head Parity + Invariant Audit** — M5 ship/iterate/rollback gate
8. **Epic 5b — Slab 5b Polish: Fork UX + Economics Dashboard + Migration Guide Final + Generator Polish**
9. **Epic X — Cross-Cutting Governance Artifacts** (living throughout; owned by protocol at every slab close per D12)

Nine epics. ~55 stories expected total (~7 Epic 1, 3 Epic 2a, 17 Epic 2b, 4 Epic 2c, 6 Epic 3, 7 Epic 4, 5 Epic 5a, 4 Epic 5b, 2 Epic X). Single-gate default per story; dual-gate designated at story authoring per `docs/dev-guide/lesson-planner-story-governance.json` analog policy.

## Epics and Stories

Legend: **Pts** = rough story-point estimate; **Gate** = single/dual-gate per `docs/dev-guide/lesson-planner-story-governance.json` analog; **K** = approximate K-floor target (1.2–1.5× per NFR-M4).

---

## Epic 1: Slab 1 Substrate — Runtime + Models + Manifest + Bridges + Docs

**Milestone:** M1 go/no-go — "Runtime substrate is real."

**Goal:** Stand up a persistent local LangGraph service with Postgres checkpointing, three-level model-selection cascade, manifest-as-graph-config loader, MCP + FastAPI bridges, LangSmith tracing, and the test-tier + scaffold-conformance frameworks from Day 1. Empty-manifest-loaded graph runs end-to-end §01→§15 via CLI with operator-driven gates and ≥60% cache hit rate on second invocation.

**FR coverage:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8, FR17, FR18, FR19, FR20, FR21, FR22, FR23, FR24 (pre-submission portion), FR25, FR54 (baseline measurement), FR58, FR59 (stub), FR60 (backport policy commit).

**Stories:** 1.1a, 1.1b, 1.1c, 1.1d, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 (10 stories — Story 1.1d added 2026-04-22 via party-mode middle-path consensus on MCP-in-Slab-1 scope).

---

### Story 1.1a: Runtime Substrate Environment + Dependencies (Story 1a per Amendment F)

As a **dev agent onboarding the hybrid clone**,
I want **a locked Python 3.12+ venv with the migration's core dependencies installed and pinned**,
So that **every subsequent Slab 1 story starts from an identical, reproducible baseline**.

**Pts:** 1 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** a fresh clone of the `dev/langchain-langgraph-foundation` branch
**When** the dev agent runs `uv venv .venv --python 3.12 && uv pip install langgraph langchain langchain-openai openai langgraph-checkpoint-postgres "pydantic>=2" fastapi langsmith "psycopg[binary]"`
**Then** the venv activates, all nine core packages install without conflict, and `uv pip freeze > requirements.lock` emits a committed lockfile.

**Given** the lockfile is committed
**When** the dev agent runs `uv run python -c "import langgraph, langchain_openai, pydantic, fastapi, langsmith; print('ok')"`
**Then** the import succeeds with `ok` on stdout; no import errors or version conflicts.

**Given** `pyproject.toml` is extended
**When** the dev agent runs `ruff check .` and `lint-imports --config pyproject.toml`
**Then** both tools report clean on the minimal contract-stub `app/` tree required by import-linter; the contract stubs for `app.marcus ⊥ app.cora` and `app.gates.**` scheduler-forbidden are declared and pass without violations.

**Given** no `.env` exists yet
**When** the dev agent creates `.env.example` with placeholder `OPENAI_API_KEY=<placeholder>`, `LANGSMITH_API_KEY=<placeholder>`, `LANGSMITH_PROJECT=course-dev-ide-migration`, `DATABASE_URL=postgresql://...`
**Then** `.env.example` is committed; `.env` is in `.gitignore` per NFR-S1.

---

### Story 1.1b: Package Layout + Postgres + Sanctum Fork Notice (Story 1b per Amendment F)

As a **dev agent completing Slab 1 substrate scaffolding**,
I want **the seven Slab-1 packages created with READMEs citing justifying FRs, a locally-installed Postgres 15+ reachable via `DATABASE_URL`, four test tiers with canaries, and CLONE-FORK-NOTICE in every sanctum directory**,
So that **the substrate shape is in place before any handler code is written, clone-fork discipline is codified Day 1, and the test harness is real from the first story**.

**Pts:** 3 | **Gate:** dual (substrate-shape story) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `app/` contains only the empty contract-stub packages seeded in Story 1.1a (`app/`, `app/marcus/`, `app/cora/`, `app/gates/`)
**When** the dev agent creates the seven Slab-1 packages (`app/runtime/`, `app/models/`, `app/models/state/`, `app/models/decision_cards/`, `app/manifest/`, `app/http/`, `app/mcp_server/`)
**Then** each package has `__init__.py` + `README.md` stub naming the justifying FR(s) per architecture §Project Structure §Requirements-to-Component Matrix; `python -c "import app.runtime, app.models, app.manifest, app.http, app.mcp_server"` succeeds.

**AC-Postgres-A (dev-agent-executable — code + artifact correctness, verified via shipped deps):**

**Given** no Postgres bootstrap artifacts exist yet and the dev agent cannot assume operator-side CLIs (`psql`, `docker`, etc.) are on the session `PATH`
**When** the dev agent authors (a) `scripts/dev/init_postgres.sql` creating the migration database + role + initial schema grants consumed later by the checkpointer (the init script must be idempotent — re-running is a no-op); (b) `docs/dev-guide/local-postgres-setup.md` documenting the one-time operator install (Windows: EDB installer; macOS: Homebrew; Linux: distro package — **no Docker / no container runtime**) + the `psql -f scripts/dev/init_postgres.sql` bootstrap; (c) a SQL parse-only syntax check that the dev agent runs against `init_postgres.sql` using a pure-Python parser already resolvable via `uv` (e.g., `sqlparse`) — no live DB required; (d) `tests/integration/postgres/test_server_version.py` that connects via **`psycopg`** (already in the 1.1a lockfile — NOT `psql`) to `DATABASE_URL`, asserts `server_version >= 150000`, and **calls `pytest.skip(...)` with a clear reason when `DATABASE_URL` is unset or the connection is refused** so the dev agent's sandbox never blocks on operator-side Postgres availability
**Then** the three artifacts exist; the SQL parse-only check exits 0; `pytest tests/integration/postgres/test_server_version.py` either passes (if a local Postgres is reachable) or skips with the documented reason (never errors/fails due to missing CLI tooling); `DATABASE_URL` is sourced from `.env` per NFR-S1; the test relies only on `psycopg` + `pytest` — no external CLI is invoked.

**AC-Postgres-B (operator-gated — one-time runtime smoke on operator's machine, recorded as Completion-Notes evidence):**

**Given** AC-Postgres-A artifacts have landed and the operator has completed the one-time native Postgres 15+ install per `docs/dev-guide/local-postgres-setup.md`
**When** the **operator** (not the dev agent) runs `psql "$DATABASE_URL" -f scripts/dev/init_postgres.sql` once, then `psql "$DATABASE_URL" -c "SELECT version();"`
**Then** the version output reports Postgres ≥ 15; the operator pastes that output into the story's Completion Notes / Dev Agent Record as evidence; this AC is recorded once at story closure and is **never** rerun per-session — it is not a dev-agent AC and must not block the dev agent if `psql` is absent from the session `PATH`.

**Given** `tests/` is empty
**When** the dev agent creates `tests/{unit,integration/scaffold_conformance,end_to_end,trial_replay,fixtures/specialists}/`
**Then** `tests/end_to_end/test_harness_contract.py` + `tests/trial_replay/test_harness_contract.py` exist with canary tests per Amendment C; `tests/trial_replay/README.md` declares "Slab 5 populates; harness contract NFR-M3"; `pytest tests/end_to_end tests/trial_replay` is green.

**Given** `runtime/graphs/` does not exist
**When** the dev agent creates `runtime/graphs/v42/README.md` declaring "frozen; do not edit; ceremony see Slab 4"
**Then** the directory and README are committed; directory is empty otherwise (Slab 5 populates).

**Given** the sanctum tree (`_bmad/memory/bmad-agent-*/`) was inherited from primary
**When** the dev agent writes `_bmad/memory/bmad-agent-{name}/CLONE-FORK-NOTICE.md` per specialist, containing: fork commit SHA, fork date, "backports stop after Slab 1 close per FR60", "sanctum authored in clone going forward"
**Then** every sanctum directory in `_bmad/memory/` has the notice; a test in `tests/integration/sanctum/test_clone_fork_notice_present.py` asserts all are present.

**Given** the import-linter contracts are declared
**When** CI runs `lint-imports --config pyproject.toml`
**Then** the contracts validate: `app.marcus ⊥ app.cora` (both remain empty at this slab; trivially passes), `app.gates.**` forbids scheduler imports (still empty; trivially passes), `app.mcp_server.tools.gate_decide`-only access to `app.gates.resume_api` (both empty; trivially passes once Story 1.1b adds that third contract).

---

### Story 1.1c: Smoke Test + Runtime Server Entry + MCP Code Substrate (Story 1c per Amendment F, middle-path-revised 2026-04-22)

As a **dev agent bringing the runtime substrate online**,
I want **working `app.smoke_test` + `app.runtime_server` entry points + `app.models.registry_check` that prove the FastAPI transport boots end-to-end, PLUS the MCP code substrate (protocol-version pin + one real tool handler + stdio wire-up in `app/mcp_server/`) landed but NOT yet exercised by the per-PR smoke gate**,
So that **M1 acceptance evidence can begin accruing, the empty-manifest-loaded graph exercise is demonstrable via FastAPI, and FR2's compound MCP+FastAPI+CLI contract has the MCP code present in Slab 1 substrate (smoke + parity-test cadence lives in Story 1.1d)**.

**Pts:** 3 | **Gate:** single | **K:** ~1.5×

> **Authoring note (party-mode consensus 2026-04-22):** This story was re-scoped via a two-round party-mode consensus (5/5 MIDDLE PATH) from the pre-split architecture version. The MCP smoke test + FastAPI↔MCP parity assertions that originally lived here were moved to new Story 1.1d to keep MCP transport off the per-PR critical path (Murat's flake-vector concern) while preserving FR2 substrate presence in Slab 1 (Mary's compound-contract concern) and D7 three-transport architecture commitment (Winston). 1.1c code scope grew (+1 Pt for MCP code substrate); smoke scope stayed narrow (FastAPI-only per-PR).

**Acceptance Criteria:**

**AC-1.1c-A — Registry check (dev-agent-executable)**

**Given** `app/models/registry.yaml` and `app/specialists/_scaffold/model_config.yaml` exist (stub content)
**When** the dev agent runs `uv run python -m app.models.registry_check`
**Then** the script loads the registry, validates every referenced model ID against the Pydantic `PipelineRegistry` model, and exits 0; invalid refs exit 1 with named violation.

**AC-1.1c-B — Smoke test via stub manifest (dev-agent-executable)**

**Given** a minimal stub manifest at `state/config/pipeline-manifest.yaml` (1-step no-op graph)
**When** the dev agent runs `uv run python -m app.smoke_test`
**Then** the manifest loads, the compiler produces a compiled StateGraph, one node executes, the graph returns, and stdout shows "smoke ok" + node count.

**AC-1.1c-C — FastAPI runtime server + /health + /invoke (dev-agent-executable)**

**Given** the smoke test passes and `app.runtime_server` is importable
**When** the dev agent runs `uv run python -m app.runtime_server` in a subprocess and probes it via `httpx` from a pytest (NOT `curl`, per sandbox-AC rule "verify via shipped deps not operator CLIs")
**Then** a FastAPI server binds to `127.0.0.1:<port>` per NFR-S2; `GET /health` returns `200` with body `{"status": "ok", "postgres": "connected"}` (when Postgres reachable) or `{"status": "ok", "postgres": "skipped"}` (when Postgres unreachable — same skip-not-fail discipline as AC-Postgres-A); `POST /invoke` with the minimal-graph input invokes the shared minimal LangGraph node and returns its output; `SIGTERM` (or equivalent clean-shutdown signal) terminates the server within 2 seconds with no orphaned threads.

**AC-1.1c-D — LangSmith span-tag contract (dev-agent-executable)**

**Given** `LANGSMITH_API_KEY` is set (skip if unset per sandbox-AC discipline)
**When** the smoke test or `/invoke` runs
**Then** a LangSmith trace is created and visible in the configured project; the trace has ≥1 span per node with the contract tag set `{trial_id, node_id, agent, lane}` (per architecture §8 span-tag contract).

**AC-1.1c-E — MCP code substrate present (dev-agent-executable; NO smoke yet — smoke is 1.1d scope)**

**Given** `app/mcp_server/` is an empty-stub package (README-only from 1.1b)
**When** the dev agent authors (a) `app/mcp_server/protocol.py` with `MCP_PROTOCOL_VERSION: str = "<pinned version>"` (FR2 protocol-version pin, exact value per architecture §MCP Protocol Pin — Slab 1 decides); (b) `app/mcp_server/server.py` with a stdio transport wire-up using `mcp.server.stdio` (shipped SDK per 2026 maturity confirmed by team); (c) `app/mcp_server/tools/ping.py` (or `trial_run_start.py` if architecture prefers) — one real `@server.tool()` handler that invokes the SAME minimal LangGraph node used by FastAPI `/invoke` so parity can be asserted in 1.1d; (d) `app/mcp_server/__main__.py` entry point (`uv run python -m app.mcp_server`) so the server can be spawned as a subprocess in 1.1d
**Then** `uv run python -c "from app.mcp_server import server; from app.mcp_server.protocol import MCP_PROTOCOL_VERSION; print(MCP_PROTOCOL_VERSION)"` prints the pinned version; the import-linter contracts continue to pass (`lint-imports --config pyproject.toml` exits 0); **no subprocess MCP round-trip is exercised in this story** — per-PR smoke stays FastAPI-only.

**AC-1.1c-F — Forward-pointer to 1.1d in docs stub (dev-agent-executable)**

**Given** `docs/dev-guide/langgraph-runtime-setup.md` stub exists (Slab 1 deliverable; final polish in 1.7)
**When** the dev agent authors the stub with the inverted **transport-parity matrix** (3 columns FastAPI / MCP / CLI × 3 rows code-present / smoke-test / parity-test) showing 1.1c lights the FastAPI column rows code+smoke, the MCP column row code-only, and 1.1d pointer callouts on the MCP smoke/parity cells; PLUS an explicit "MCP acceptance gated on Story 1.1d — handler present but not production-ready until 1.1d closes" callout in the MCP section per Paige's Round 2 doc-shape recommendation
**Then** the stub exists, the matrix is present (Mermaid table or markdown table acceptable; Paige to finalize shape in 1.7), and the 1.1d reference is grep-able.

---

### Story 1.1d: MCP Transport Smoke + Two-Transport Parity (NEW — party-mode consensus 2026-04-22)

As a **dev agent closing the FR2 compound-contract evidence at M1 acceptance**,
I want **a dedicated MCP stdio smoke test + FastAPI↔MCP byte-equivalent parity assertion that runs nightly / on-merge (NOT per-PR) against the same minimal LangGraph node 1.1c wires to both transports**,
So that **the MCP transport is proven substrate at M1 without putting subprocess stdio flake vectors on every Slab 1 PR's critical path (Murat's concern), the D7 three-transport parity claim is falsifiable not aspirational (Winston/Mary's concern), and Slab 3 Story 3.4 three-transport verdict inherits a pre-proven two-transport baseline**.

**Pts:** 3 | **Gate:** single | **K:** ~1.5× (floor 1.2, ceiling 1.8; subprocess fixture is the K risk — budget absorbs it per Amelia's Round 2 math)

**Origin:** Middle-path consensus from party-mode round on MCP-in-Slab-1 (transcript in session memory; 5/5 MIDDLE PATH vote). Pulls the MCP smoke + parity matrix out of 1.1c's per-PR critical path while keeping MCP code substrate in Slab 1 per FR2 and D7.

**Dependencies:** 1.1c (provides MCP code + shared minimal LangGraph node), 1.1b (provides test-tier scaffold at `tests/integration/`), 1.1a (provides `mcp` SDK via lockfile — verify in story T1).

**Acceptance Criteria:**

**AC-1.1d-A — Shared-fixture contract (dev-agent-executable)**

**Given** 1.1c shipped the MCP code substrate + the same minimal LangGraph node wired to both FastAPI `/invoke` and the MCP `ping` (or `trial_run_start`) tool
**When** 1.1d authors `tests/integration/transport_parity/conftest.py` with a fixture that imports the literal same minimal-node module (not a re-implementation) and parametrizes it across both transports
**Then** the fixture is the single source of truth for the node-under-test; any drift between transports is caught by import-site changes, not test-site duplication.

**AC-1.1d-B — MCP stdio subprocess smoke (dev-agent-executable)**

**Given** the shipped `mcp` PyPI SDK provides `mcp.client.stdio.stdio_client` + `ClientSession` primitives (verified at T1 against the locked version in `requirements.lock`)
**When** 1.1d authors `tests/integration/transport_parity/test_mcp_stdio_smoke.py` that spawns `uv run python -m app.mcp_server` as a real subprocess, connects via `stdio_client`, runs `await session.initialize()` → `await session.list_tools()` → `await session.call_tool("ping", {...})` → graceful shutdown via `SIGTERM` (or equivalent on Windows) within N seconds (target ≤3s; hard-fail ≥10s)
**Then** `list_tools` returns the one registered tool (plus protocol-version metadata); `call_tool` returns the minimal node's output; subprocess exits cleanly; no orphaned pipes or threads; pytest passes with `pytest.skip(...)` when `mcp` SDK import fails (sandbox-AC discipline).

**AC-1.1d-C — FastAPI↔MCP byte-equivalent parity (dev-agent-executable)**

**Given** AC-1.1d-A + AC-1.1d-B are green
**When** 1.1d authors `tests/integration/transport_parity/test_fastapi_mcp_parity.py` that drives the SAME input through both transports and compares response payloads
**Then** response payloads are **byte-equivalent modulo a documented transport-envelope exceptions table** (request-id, timestamps, transport-name, per-transport framing — full list authored in `docs/dev-guide/transport-parity-envelope-exceptions.md`); any drift outside the exceptions table = test failure; CLI/SSE parity legs explicitly **deferred** with visible-roadmap pointer to Slab 3 Story 3.4.

**AC-1.1d-D — Cadence + flakiness budget (dev-agent-executable)**

**Given** AC-1.1d-B + AC-1.1d-C are the high-flake-risk tests per Round 2 test-architect analysis
**When** 1.1d authors CI lane configuration placing these tests in a nightly / on-merge-to-main lane, NOT the per-PR Slab 1 smoke lane; plus a reopen-trigger note: "if subprocess smoke or parity test flakes >2% across its first 20 runs, reopen the MCP-in-Slab-1 deferral conversation"
**Then** the CI configuration exists (skeleton — full CI wiring lands in Slab 4 Story 4.1 graph-compile-time hook); per-PR Slab 1 smoke remains the FastAPI-only gate from 1.1c; the flakiness budget is grep-able in the story spec and the transport-parity test module docstring.

**AC-1.1d-E — M1 acceptance gate (dev-agent-executable)**

**Given** all above ACs are green
**When** the M1 acceptance evidence is compiled (Slab 1 close)
**Then** 1.1d's transport-parity test run is part of the M1 evidence pack; if it is red, M1 is not met; the FR2 compound-contract claim is satisfied by this story's closure, not by 1.1c's closure.

---

### Story 1.2: Pydantic State Base Classes + Shape-Pin Tests

As a **dev agent authoring LangGraph state modules**,
I want **`RunState`, `StoryState`, `SpecialistEnvelope`, `SpecialistReturn`, `SanctumFingerprint`, `CacheState`, and `NodeCheckpoint` Pydantic v2 models with four-file-lockstep compliance and exhaustive shape-pin tests**,
So that **every downstream handler has a validated state contract from Day 1 and reproducibility invariants (NFR-X1–X5) are enforceable**.

**Pts:** 3 | **Gate:** dual (schema-shape story) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** no state modules exist
**When** the dev agent authors `app/models/state/run_state.py`, `story_state.py`, `specialist_envelope.py`, `specialist_return.py`, `sanctum_fingerprint.py`, `cache_state.py`, `node_checkpoint.py` following the Pydantic-v2 checklist (validate_assignment=True, extra=forbid, timezone-aware datetimes, UUID4, closed enums with triple-layer red-rejection)
**Then** each module has a companion `*.schema.json` emission, a `tests/unit/models/state/test_*_shape.py` shape-pin test, and a `tests/fixtures/models/state/golden_*.json` golden fixture per four-file-lockstep (NFR-M5).

**Given** `RunState` has `model_overrides: dict[NodeId, ModelRef | None]` per D2
**When** the shape-pin test runs
**Then** the test asserts the field exists, allows None values, allows valid `ModelRef` values, rejects unregistered model IDs at assignment time.

**Given** `NodeCheckpoint` has `sanctum_fingerprints: dict[str, SanctumFingerprint]` per D1
**When** the shape-pin test runs
**Then** the test asserts field presence, default-empty, and that adding a fingerprint is persistable to Postgres without serialization errors.

**Given** all seven state modules are authored
**When** CI runs `ruff check app/models/state/` and `pytest tests/unit/models/state/`
**Then** both are green with zero MUST-FIX findings; test count ≥ 18 (3 per module minimum: round-trip + boundary + error-path).

---

### Story 1.3: Three-Level Model Selector + Registry + Adapter + Selection Policy

As a **dev agent implementing the model cascade**,
I want **a deterministic `resolve_model()` function, a governed `registry.yaml`, a thin `ChatOpenAI` adapter, and a declarative `selection_policy.yaml` that together resolve every LLM invocation to a model with full LangSmith audit trail**,
So that **FR17–FR25 are architecturally enforced, NFR-O4 resolution trails are captured, and D13 mid-migration bumps have a governed path**.

**Pts:** 3 | **Gate:** dual (schema-shape in PipelineRegistry) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** no `app/models/selector.py` exists
**When** the dev agent authors `selector.py::resolve_model(node_id, state, *, agent, node_role) -> tuple[ModelRef, ResolutionTrail]` implementing the three-level cascade (override → per-agent `model_config.yaml` → auto-select via `selection_policy.yaml`)
**Then** a parametrized unit test in `tests/unit/selector/test_cascade.py` covers: override wins over config, config wins over auto-select, auto-select deterministic with same inputs, unknown model raises `ModelResolutionError`, `ResolutionTrail.level ∈ {1,2,3}` with correct value per case.

**Given** `app/models/registry.yaml` lists initial OpenAI models per PRD §Specialists tier palette
**When** the dev agent authors `registry.py::PipelineRegistry` Pydantic model and `registry_check.py` validator
**Then** a test asserts every model entry has valid `tier`, `context_window`, `cost_per_1m_input`, `cost_per_1m_output`, `capabilities`, `deprecation_status`; invalid entries fail graph compile.

**Given** `adapter.py::adapter_for_model(model_ref) -> BaseChatModel` is a thin wrapper over `ChatOpenAI`
**When** tests run with mocked OpenAI responses
**Then** the adapter correctly applies model, temperature, and config; no high-level LangChain agent abstractions (`AgentExecutor`, `initialize_agent`) appear in imports; `ruff check` green.

**Given** `selection_policy.yaml` declares auto-select rules per (agent, node_role, context_tokens, quality_tier, budget_tier)
**When** the dev agent runs `pytest tests/unit/selector/test_auto_select_deterministic.py`
**Then** the same inputs always produce the same model choice; no LLM call occurs during auto-select; policy-hit reasons are logged in `ResolutionTrail.policy_hit`.

**Given** LangSmith is wired
**When** any handler calls `resolve_model()` and emits the trail via `emit_resolution_trail()`
**Then** the LangSmith span tag set includes `resolution_level`, `chosen_model`, `policy_hit`; contract test in `tests/integration/observability/test_langsmith_span_contract.py` green.

---

### Story 1.4: Manifest-as-Graph-Config Loader + Compiler

As a **dev agent standing up the manifest-driven compilation pipeline**,
I want **`app/manifest/schema.py`, `app/manifest/loader.py`, and `app/manifest/compiler.py` that together parse `state/config/pipeline-manifest.yaml` into a compiled LangGraph `StateGraph` with cross-field validation at load time**,
So that **FR8 + FR38 are architecturally enforced (topology cannot compile without a valid manifest) and D6 + D4 compile-time CI has its library substrate**.

**Pts:** 5 | **Gate:** dual (schema-shape in PipelineManifest + compile-time topology) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** no manifest modules exist
**When** the dev agent authors `schema.py` with `PipelineManifest`, `Step`, `Edge`, `EdgeKind` (sequential / conditional_by_predicate / interrupt / send_fanout), `Subgraph`, `RuntimeSection` Pydantic models per architecture D6 sketch
**Then** four-file-lockstep applies: schema.py + schema.json + test_manifest_shape.py + golden_manifest.json; regex validators enforce step-ID + gate-ID + handler-ref patterns per architecture §1 patterns.

**Given** `loader.py::load_manifest(path) -> PipelineManifest` is authored
**When** a test manifest with an unimportable handler is loaded
**Then** loader raises `ManifestError` with the handler ref named; fail-fast per architecture §error taxonomy.

**Given** `compiler.py::compile_run_graph(manifest, checkpointer) -> CompiledGraph` is authored
**When** a stub 1-step manifest is compiled with Postgres checkpointer
**Then** the compiled graph accepts `.invoke()` calls; all four edge kinds (sequential, conditional_by_predicate, interrupt, send_fanout) have dispatch branches.

**Given** `compile_run_graph()` supports a validation mode (no checkpointer)
**When** called with validation_mode=True
**Then** the graph compiles without attempting Postgres connection; suitable for CI graph-compile hook per D4.

**Given** compiler validation iterates every specialist's `model_config.yaml`
**When** a specialist declares an unregistered model ID
**Then** `compile_run_graph()` raises `ManifestError` at validation time; NFR-M2 enforced.

**Given** a test manifest has an invalid handler reference shape (`app.foo.bar` instead of `app.foo:bar`)
**When** loader runs
**Then** Pydantic validation raises before import is attempted; pattern mismatch surfaced with field path.

---

### Story 1.5: Checkpoint Retention + Cleanup Policy

As an **operator managing long-running trial-run history**,
I want **a configurable Postgres checkpoint retention + cleanup + audit-preservation policy that trims old threads without losing in-flight or referenced trials**,
So that **FR5 is implemented, NFR-R7 (clone-local corruption tolerance) is preserved, and Postgres storage doesn't balloon over 12–16 weeks**.

**Pts:** 2 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** Postgres has `checkpoint` and `checkpoint_writes` tables from `langgraph-checkpoint-postgres`
**When** the dev agent authors `app/runtime/checkpointer.py::RetentionPolicy` Pydantic model with `retain_days: int`, `preserve_trial_close: bool`, `preserve_forked_parents: bool`
**Then** unit tests cover: age-based cleanup, preserve-trial-close exception, preserve-forked-parents exception, dry-run mode.

**Given** the retention policy is configured via `state/config/retention-policy.yaml`
**When** the dev agent runs `uv run python -m app.runtime.checkpointer --prune` in dry-run mode
**Then** the CLI lists thread IDs that would be deleted with reasons; no deletion occurs.

**Given** a trial run is closed and its final checkpoint is marked preserve
**When** cleanup runs
**Then** the preserved checkpoints remain; only unreferenced checkpoints older than `retain_days` are removed.

**Given** an integration test creates 3 trials (1 active, 1 closed-preserved, 1 closed-unpreserved)
**When** cleanup runs with `retain_days=0`
**Then** only the closed-unpreserved trial's checkpoints are removed; active and preserved remain.

---

### Story 1.6: Pipeline Manifest Migration from Primary + Stub Empty-Graph Smoke

As a **dev agent bridging primary's existing manifest into the clone's new compile pipeline**,
I want **the existing `state/config/pipeline-manifest.yaml` extended to match D6 schema + a stub 15-step empty-graph manifest that the smoke test can execute**,
So that **M1 acceptance evidence (empty-manifest-loaded graph §01→§15) is buildable and primary's manifest continuity is preserved**.

**Pts:** 3 | **Gate:** dual (manifest schema change) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `state/config/pipeline-manifest.yaml` exists from primary repo
**When** the dev agent extends it with D6-schema fields (`runtime.graph_version: v42`, `runtime.state_model: app.models.state.run_state:RunState`, per-step `handler`, per-step `edges[]`, per-step `block_mode_trigger_paths[]`)
**Then** the extension is additive (existing primary-consumed fields preserved); `load_manifest()` parses it into a valid `PipelineManifest`.

**Given** 15 handler stubs at `app/marcus/handlers/step_*.py` each implementing a no-op `run(state) -> Command[...]` returning the next step
**When** the compiler builds the graph
**Then** a 15-node sequential graph compiles; `uv run python -m app.smoke_test` executes §01→§15 end-to-end with operator-driven CLI gates at the manifest-declared gate positions.

**Given** the smoke test runs twice back-to-back with the same input bundle
**When** the second run completes
**Then** LangSmith reports prompt-cache hit rate ≥ 60% on the second run (M1 Required Evidence bar).

**Given** the pipeline manifest declares block-mode-trigger-paths per step
**When** `lint-imports --config pyproject.toml` runs
**Then** no violations; block-mode-trigger-paths are declared (Slab-4 CI hook consumes them later).

---

### Story 1.7: Slab 1 Docs + Scaffold-Conformance Framework + Anti-Patterns Stub + Migration Guide Skeleton

As a **dev agent closing Slab 1 and preparing Slab 2 consumers**,
I want **`langgraph-runtime-setup.md`, `model-selection-guide.md`, `langgraph-state-idioms.md`, the scaffold-conformance framework with fixture specialist, the anti-patterns catalog stub, and the migration-guide 11-section skeleton**,
So that **M1 acceptance closes with all documentation deliverables landed, Amendment D + E are honored, and Slab 2 has a working conformance harness before any real specialist exists**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** `docs/dev-guide/` exists from primary
**When** the dev agent authors `langgraph-runtime-setup.md` (clone→venv→deps→postgres→smoke→runtime_server, usable by fresh dev), `model-selection-guide.md` (three-level cascade + tier palette + D13 mid-migration bump procedure), `langgraph-state-idioms.md` (six sections per Amendment E Paige outline: BaseModel-vs-TypedDict, reducers, Command, Send, interrupt payloads, RetryPolicy placeholder)
**Then** each doc is ≥80% of outline; one-paragraph cross-reference is added to `pydantic-v2-schema-checklist.md` pointing at `langgraph-state-idioms.md`; one-line pointer is added to `docs/dev-guide/scaffolds/schema-story/README.md`.

**Given** `tests/fixtures/specialists/fixture_minimal_specialist.py` does not exist
**When** the dev agent authors a minimal-but-9-node-conformant fixture specialist + the scaffold-conformance framework at `tests/integration/scaffold_conformance/`
**Then** the framework parametrizes over `app/specialists/_scaffold/` + `fixture_minimal_specialist.py`; asserts node count = 9, sanctum cold-read integrity, envelope/return typing, node idempotency; `pytest tests/integration/scaffold_conformance/` green (FR14 proven against fixture before real specialists land).

**Given** `docs/dev-guide/specialist-anti-patterns.md` does not exist
**When** the dev agent authors the stub file with the five initial entries from architecture §11 (shape-separation violation, leaky neck, cage drift, pad-to-K, scaffold-skip)
**Then** the file is committed; Slab 2+ stories add entries per D12 protocol.

**Given** `docs/dev-guide/langgraph-migration-guide.md` does not exist
**When** the dev agent authors the 11-section skeleton (Conceptual Map / Specialist Walkthrough / Manifest Translation / Gate Migration / Schema Migration / Lockstep CI / Frozen-Graph Ceremony / Forward-Port Playbook / Model-Selection Cutover / Rollback Plan / Anti-Patterns Appendix) with placeholder content
**Then** the file is committed; each section has a "Status: placeholder — filled in Slab N" line citing the slab that owns that section's final content per D12.

**Given** Amendment I (LangGraph idiom sanity check)
**When** the dev agent runs a throwaway `StateGraph + MemorySaver` mini-example against `app/runtime/` + `app/state/` abstractions
**Then** the example compiles and runs; the dev agent confirms no drift from LangGraph idiom; the example is NOT committed (scratch only); a one-line Dev-Agent-Record entry logs "idiom sanity check: OK."

**Given** Slab 1 closing story per D12 protocol
**When** the dev agent adds the three-line slab-closing governance AC (invariant-preservation note + anti-pattern-harvest entry + migration-guide-section-update)
**Then** the Dev Agent Record names: (1) invariants touched in Slab 1 (#3 manifest neck, #8 four-file-lockstep, #10 frozen-at-ship stub, #15 lane separation enforced) with file/test refs, (2) anti-pattern harvest empty at Slab 1 (five seed entries already present), (3) migration-guide sections "Conceptual Map" + "Manifest Translation" + "Model-Selection Cutover" placeholder content deepened.

---

## Epic 2 Reconciliation Banner (2026-04-24)

> **Slab 2 roster reconciled 2026-04-24** against actual skill directories on
> hybrid post-severance absorption. The named 14-specialist Epic 2b roster
> (*Gary, Vera, Quinn-R, Desmond, Tracy, Paige, Mike, Dan, Eli, Enrique,
> Mira, Sally, Kim, CD*) resolved to **9 migratable (Category A+B, including
> absorbed Wondercraft) + 5 Tier-4 thin nodes (Category C) + 2 dissolved
> (Audra, Cora — replaced by LangGraph CI + BMAD session protocols) + 7
> roadmap-only names with no skill directory (Category E — deferred to
> post-M5 greenfield mini-epic).** Full reconciliation at
> [`slab-2-roster-reconciliation.md`](slab-2-roster-reconciliation.md).
>
> **Upstream severance** per [`langgraph-migration-guide.md §8.1`](../../docs/dev-guide/langgraph-migration-guide.md#81-upstream-severance-slab-2)
> replaces FR60 forward-port freeze. 2b.N T1 reads go against hybrid's
> working-tree skill directories directly; no more `upstream/master` reads.
> Absorption + severance audit trail at [`upstream-severance-log.md`](../implementation-artifacts/upstream-severance-log.md).
>
> **Wondercraft decision** flagged for Slab 2 kickoff party-mode: absorbed
> as a real skill directory, Wondercraft can migrate as 2b.N (Path A) or
> remain as 2c.1 generator-validation target (Path B). See reconciliation
> doc §Wondercraft Decision. Default pending kickoff: Path A.

---

## Epic 2a: Slab 2a Scaffold Pilot — PR-R-Conformant Specialists

**Milestone:** Intermediate (feeds M2).

**Goal:** Validate the 9-node specialist scaffold + `bmad-create-specialist` generator against three specialists already Pydantic-pinned by primary's PR-R work (Irene Pass 2, Kira motion, Texas). Low risk because dispatch contracts are already known; scaffold wrapping + sanctum cold-read + `model_config.yaml` is the new work.

**FR coverage:** FR9–FR16 applied to 3 specialists; FR13 generator validated.

**Stories:** 2a.1, 2a.2, 2a.3, 2a.4 (4 stories).

---

### Story 2a.1: `bmad-create-specialist` Generator + 9-Node Scaffold Reference

As a **dev agent bootstrapping the specialist fleet**,
I want **`skills/bmad-create-specialist/` with SKILL.md + templates + scripts emitting a scaffold-conformant 9-node specialist from a fresh command**,
So that **FR13 is proven and the three PR-R-conformant specialists (Irene Pass 2, Kira motion, Texas) have a consistent creation path**.

**Pts:** 5 | **Gate:** dual (generator emits schema-shape + test scaffolds) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** `skills/bmad-create-specialist/` does not exist
**When** the dev agent authors SKILL.md + `templates/` (9-node graph.py template, state.py envelope/return, model_config.yaml, expertise/README.md, sanctum-symlink target) + `scripts/generate.py`
**Then** running `uv run python -m skills.bmad_create_specialist.scripts.generate --name toytest --mcp none --expertise-tier L5-toy` emits `app/specialists/toytest/` with all required files; scaffold-conformance framework (from Story 1.7) validates the new specialist; test passes.

**Given** `app/specialists/_scaffold/` was created in Story 1.7
**When** the dev agent populates it with the canonical 9-node reference (`plan → enter_sanctum → load_expertise → reason → act → validate → emit → return → exit_sanctum`) + reference `model_config.yaml` showing all three cascade levels
**Then** the scaffold is the generator's template source; doc reference added to `docs/dev-guide/langgraph-migration-guide.md` §Specialist Walkthrough.

**Given** a generated specialist's `model_config.yaml` has an invalid model ref
**When** the compiler runs NFR-M2 validation
**Then** graph compile fails with the specialist name + the invalid ref surfaced.

**Given** `toytest` was generated for this AC
**When** the story closes
**Then** `toytest` is DELETED (no empty specialist in the tree) or moved to `tests/fixtures/specialists/fixture_generated_specialist_for_acceptance_test.py` as a fixture specialist used in generator regression tests.

---

### Story 2a.2: Migrate Irene Pass 2 to 9-Node Scaffold

As a **migration dev agent**,
I want **the existing Irene Pass 2 dispatch (already Pydantic-pinned by PR-R) rehomed into `app/specialists/irene/` with 9-node scaffold, sanctum symlink, `model_config.yaml`, and scaffold-conformance test green**,
So that **the first real specialist migration validates the scaffold pattern end-to-end with a known-good contract shape**.

**Pts:** 3 | **Gate:** single | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `skills/bmad-agent-content-creator/` (Irene's current home in the clone) has working scripts
**When** the dev agent runs `bmad-create-specialist --name irene --mcp none --expertise-tier L5-narration-pass-2` and migrates the existing logic into the 9-node shape
**Then** `app/specialists/irene/graph.py` compiles; `tests/integration/scaffold_conformance/test_irene_conforms.py` green; `_bmad/memory/bmad-agent-irene/` sanctum symlink present.

**Given** PR-R's dispatch envelope for Irene Pass 2 was forward-ported (placeholder for M5 forward-port; Slab 2a uses the migration-version-of-record at time of authoring)
**When** Irene's subgraph is invoked from a test harness
**Then** input envelope is validated, `reason` node runs, `act` node produces narration artifact, `validate` node checks G4 criteria, `emit` sends typed receipt, `return` yields `SpecialistReturn` matching shape-pin test.

**Given** Irene uses model tier "long-context balanced"
**When** `resolve_model()` runs at her `reason` node
**Then** default resolves to `gpt-4.1` (per `app/models/selection_policy.yaml`); runtime override correctly propagates via `RunState.model_overrides`.

**Given** Irene's sanctum contains L5 references (narration-pass-2 rules, G4 criteria, cluster-aware refinement patterns)
**When** `load_expertise` node runs
**Then** the expertise payload includes L5 references by dotted reference from `INDEX.md`; fingerprint is computed per D1.

**Given** the slab-closing governance protocol
**When** the story closes
**Then** Dev Agent Record includes D12 three-line AC: invariant #13 (specialist registry) preserved, anti-pattern harvest entry (if any), migration-guide §Specialist Walkthrough updated with Irene before/after.

---

### Story 2a.3: Migrate Kira Motion to 9-Node Scaffold

As a **migration dev agent**,
I want **Kira motion (Kling dispatch for motion segments) migrated to `app/specialists/kira/` with the 9-node scaffold pattern and motion-specific L5 references**,
So that **the motion pathway is scaffold-conformant and Storyboard B motion contract continues to work**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** `skills/bmad-agent-kling/` has working scripts
**When** the dev agent migrates Kira into `app/specialists/kira/` with scaffold conformance
**Then** `tests/integration/scaffold_conformance/test_kira_conforms.py` green; sanctum + model_config + expertise layers present.

**Given** Kira's `act` node dispatches to Kling API via L7 MCP tool
**When** the motion segment produces an artifact
**Then** `SpecialistReturn.motion_asset_path` is populated; Storyboard B motion contract (still in `visual_file` + MP4 in `motion_asset_path`) is preserved.

**Given** Kira's model tier is "multimodal"
**When** `resolve_model()` runs at reason node
**Then** default resolves to `gpt-4o` per selection policy.

**Given** D12 protocol at slab-closing story
**When** close AC runs
**Then** three-line protocol satisfied (invariant, anti-pattern, guide-section).

---

### Story 2a.4: Migrate Texas (Source Wrangler) to 9-Node Scaffold

As a **migration dev agent**,
I want **Texas (Shape 3-Disciplined retrieval) migrated to `app/specialists/texas/` with the 9-node scaffold, preserving the retrieval-contract-at-references unchanged per NFR-I5**,
So that **retrieval substrate remains authoritative across migration and `app/specialists/texas/expertise/` references the existing `skills/bmad-agent-texas/references/retrieval-contract.md` verbatim**.

**Pts:** 3 | **Gate:** single | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `skills/bmad-agent-texas/` contains the retrieval substrate (27-0 + 27-1 + pending 27-2/27-2.5)
**When** the dev agent migrates Texas into `app/specialists/texas/`
**Then** the existing retrieval contract at `skills/bmad-agent-texas/references/retrieval-contract.md` is NOT modified (NFR-I5); `app/specialists/texas/expertise/retrieval-contract-ref.md` is a symlink or pointer file referencing the existing doc.

**Given** Texas's scaffold is conformance-green
**When** a smoke-test dispatch with a minimal `RetrievalIntent` arrives at Texas's subgraph
**Then** the envelope validates, Texas's retrieval dispatcher (`skills/bmad-agent-texas/scripts/run_wrangler.py`) is invoked via L7 MCP tool, result normalizes to the six-artifact bundle per schema v1.1, `SpecialistReturn` carries the bundle reference.

**Given** Texas's current tests (`tests/bmad-agent-texas/...`) exist from primary
**When** the migration adds `tests/integration/specialists/test_texas_scaffold.py`
**Then** both test suites pass (existing + new); no regression of retrieval behavior.

**Given** D12 protocol at slab-closing story
**When** close AC runs
**Then** invariant preservation note cites NFR-I5 (Texas contract unmodified) + invariant #13 (specialist registry); anti-pattern harvest if any; migration-guide §Specialist Walkthrough updated with Texas case.

---

## Epic 2b: Slab 2b Specialist Tranche — 14 Non-Conformant Specialists

**Milestone:** Intermediate (feeds M2).

**Goal:** Migrate the remaining 14 specialists (Gary, Vera, Quinn-R, Desmond, Tracy, Paige, Mike, Dan, Eli, Enrique, Mira, Sally, Kim, CD — actual final list reconciled at kickoff per roster at time of Slab 2b open). Each gets PR-R-style dispatch contract retrofitted AND 9-node scaffold migration. Anti-patterns catalog primary harvest lives here.

**FR coverage:** FR9–FR16 applied to 14 specialists; FR64 primary harvest.

**Stories:** 17 (one per specialist migration; +3 cross-cutting stories for dispatch contract hardening + anti-patterns catalog harvest + scaffold-conformance framework hardening).

**Structure:** stories 2b.1–2b.14 are per-specialist migrations (template repeated); stories 2b.15, 2b.16, 2b.17 are cross-cutting. Full ACs are given for the template (2b.1) and the cross-cutting stories; 2b.2–2b.14 follow the template with specialist-specific adaptations.

---

### Story 2b.1: Migrate Gary (Gamma Slide Generation) to 9-Node Scaffold (TEMPLATE)

As a **migration dev agent**,
I want **Gary migrated to `app/specialists/gary/` with PR-R-style dispatch contract retrofitted + 9-node scaffold compliance + sanctum retention**,
So that **slide generation (Gamma API dispatch) is scaffold-conformant and the "reject the cage" discipline holds at the act node**.

**Pts:** 4 | **Gate:** single (non-schema-shape specialist migration; dual only if dispatch contract adds a new edge kind) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `skills/bmad-agent-gamma/` contains Gary's working Gamma dispatch
**When** the dev agent migrates Gary into `app/specialists/gary/` with PR-R-style dispatch envelope (Pydantic input + receipt + error taxonomy)
**Then** scaffold-conformance test green; envelope + receipt + error models follow PR-R shape (pending forward-port reconciliation at M5); `act` node calls Gamma REST API via L7 MCP tool.

**Given** Gary's `reason` node uses free-text (cage-rule: schema-as-boundary, not corset)
**When** Gary drafts slide content
**Then** the draft is free-text; structured output only at the envelope boundary.

**Given** Gary's model tier is "fast & cheap workhorse"
**When** `resolve_model()` runs
**Then** default resolves to `gpt-4.1-mini` per selection policy.

**Given** anti-patterns encountered during Gary migration
**When** the story closes
**Then** any new anti-pattern is added to `docs/dev-guide/specialist-anti-patterns.md` per D12 protocol with: name + example + counter-pattern + slab-of-discovery.

**Given** D12 close protocol
**When** close AC runs
**Then** invariant-preservation note + anti-pattern harvest + migration-guide §Specialist Walkthrough entry for Gary.

---

### Stories 2b.2–2b.14: Per-Specialist Migrations (Template Applied)

Each of the 13 remaining stories (Vera, Quinn-R, Desmond, Tracy, Paige-as-runtime-specialist-if-scoped, Mike, Dan, Eli, Enrique, Mira, Sally, Kim, CD) follows the Story 2b.1 template with specialist-specific adaptations:

- **Points:** 3–4 each (Quinn-R 5 due to fidelity-assessor composition with Vera); total ~50 pts across the 13.
- **Gate:** single default; dual if the migration surfaces a new edge kind or schema-shape change.
- **K:** ~1.3–1.4× each.
- **Model tier** resolved per specialist: Quinn-R reasoning or long-context (review depth); Vera fast-and-cheap (fidelity assessment is pattern-match, not reasoning-heavy); Desmond fast-and-cheap; Tracy long-context-balanced (research intent shaping); CD long-context-balanced (creative direction); etc.

Anti-patterns catalog harvest is the cross-slab deliverable driven per D12 — each story adds 0–1 entries. Target ≥5 catalog entries by Slab 2c close.

---

### Story 2b.15: Dispatch Contract Hardening (PR-R Alignment Placeholder)

As a **dev agent bridging primary's PR-R dispatch discipline into the migration**,
I want **a `app/models/dispatch/` Pydantic family declaring per-edge input/receipt/error shapes for all 17 specialists + an interim dispatch-registry schema**,
So that **the migration's dispatch surface is PR-R-compatible at M5 forward-port with zero reconciliation churn**.

**Pts:** 5 | **Gate:** dual (schema-shape) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** PR-R artifacts in primary (expected post-Sprint #1: `state/config/dispatch-registry.yaml`, per-edge Pydantic models, `check_dispatch_registry_lockstep.py` L1 validator)
**When** the dev agent authors `app/models/dispatch/{input,receipt,error}.py` per specialist Pydantic family
**Then** each of the 17 specialists has input/receipt/error classes following four-file-lockstep.

**Given** `state/config/dispatch-registry.yaml` does not yet exist in the clone (inherited at M5 from primary)
**When** the dev agent writes an interim clone-local `state/config/dispatch-registry.yaml` mirroring the structure expected from PR-R
**Then** the interim file is marked `# INTERIM — reconciled with primary at M5 forward-port` at the top; M5 forward-port playbook consumes it for merge.

**Given** migration-guide §8 (Forward-Port Playbook)
**When** the story closes
**Then** §8 has a "PR-R reconciliation checklist" listing: (1) replace interim dispatch-registry.yaml with primary's at M5, (2) wire L1 validator as library call from graph-compile CI per D4, (3) verify receipt-shape has `sanctum_fingerprint` field per D1 or amend at forward-port, (4) verify Pydantic schemas pass `pydantic-v2-schema-checklist.md` per A22.

---

### Story 2b.16: Scaffold-Conformance Framework Hardening + Per-Specialist Test Generation

As a **dev agent ensuring zero-drift on the 9-node scaffold across 17 specialists**,
I want **the conformance framework (from Story 1.7) extended to parametrize over the specialist registry automatically + per-specialist test generation**,
So that **adding a specialist requires no framework changes (FR14 architecturally enforced)**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** `tests/integration/scaffold_conformance/` contains the framework
**When** the dev agent extends it to auto-discover all `app/specialists/*/` directories and parametrize
**Then** `pytest tests/integration/scaffold_conformance/` runs the 14 conformance rules (FR14 assertions) against every non-`_scaffold` specialist; a fresh generated specialist is picked up with zero framework changes.

**Given** scaffold-conformance finds a specialist missing `sanctum/` symlink
**When** the test runs
**Then** the test fails with a specific error naming the missing file and the FR14 rule violated.

**Given** the `_scaffold/` reference specialist must ALSO pass conformance
**When** the test runs
**Then** `_scaffold/` is treated as a specialist for the purposes of conformance (self-consistency check).

---

### Story 2b.17: Anti-Patterns Catalog Consolidation + First 5 Confirmed Entries

As a **dev agent closing Slab 2b**,
I want **the anti-patterns catalog consolidated with ≥5 concrete entries harvested from the 2b migration (no invented retrospectively)**,
So that **FR64 is met before Slab 2c opens and the scaffold-generator (Slab 2c) can reference real anti-patterns**.

**Pts:** 2 | **Gate:** single | **K:** ~1.2×

**Acceptance Criteria:**

**Given** `docs/dev-guide/specialist-anti-patterns.md` contains the seed entries from Story 1.7
**When** the dev agent reviews entries harvested during 2b.1–2b.14
**Then** the catalog has ≥5 entries harvested from real migration work (not the seed entries); each entry has name + example + counter-pattern + slab-of-discovery.

**Given** Slab 2b closes
**When** migration-guide §Anti-Patterns Appendix updates
**Then** the appendix cites the catalog; migration-guide §4 (Gate Migration) and §2 (Specialist Walkthrough) cross-reference anti-pattern entries where relevant.

---

## Epic 2c: Slab 2c Wondercraft Pilot + Generator Validation

**Milestone:** M2 go/no-go gate — "Plug-and-play specialist claim validated."

**Goal:** Use `bmad-create-specialist` to generate Wondercraft (podcast production) from scratch and produce a real podcast artifact against the live Wondercraft API in <1 dev-day. Validates FR13 + the <1-dev-day innovation claim.

**FR coverage:** FR13, FR14, FR16.

**Stories:** 2c.1, 2c.2, 2c.3, 2c.4 (4 stories).

---

### Story 2c.1: Generate Wondercraft Specialist from Scratch

As a **dev agent (or operator wearing dev hat) validating the plug-and-play innovation claim**,
I want **`bmad-create-specialist --name wondercraft --mcp wondercraft-api --expertise-tier L5-podcast-production` to emit a fully-conformant specialist with sanctum stub + L5/L6 placeholders + scaffold-conformance test + registry entry**,
So that **FR13 is demonstrated on a fresh specialist and the <1-dev-day time-to-deploy claim has its first measurement**.

**Pts:** 2 | **Gate:** single | **K:** ~1.3× | **Time-to-deploy target: ≤1 dev-day from story open to first real artifact**

**Acceptance Criteria:**

**Given** Slab 2a + 2b complete; generator hardened; scaffold-conformance framework green on all migrated specialists
**When** the dev agent runs `bmad-create-specialist --name wondercraft --mcp wondercraft-api --expertise-tier L5-podcast-production` at T0
**Then** within 30 seconds the command emits: `app/specialists/wondercraft/{graph.py,state.py,model_config.yaml,expertise/README.md,sanctum-> ../../../_bmad/memory/bmad-agent-wondercraft/}`, `_bmad/memory/bmad-agent-wondercraft/{INDEX.md,PERSONA.md,chronology.md,access-boundaries.md,CLONE-FORK-NOTICE.md}` with L5/L6 placeholders, `tests/integration/specialists/test_wondercraft_conforms.py`, and a specialist-registry entry.

**Given** scaffold-conformance framework is running
**When** the framework auto-picks up `app/specialists/wondercraft/`
**Then** the new specialist passes all 14 conformance rules without modification; T_elapsed = T0 + ≤5 minutes.

**Given** timing is tracked
**When** the story closes
**Then** Dev Agent Record notes time-to-deploy for generator step (≤30 sec) + time-to-conformance-green (≤5 min).

---

### Story 2c.2: Wondercraft L5 + L6 Expertise Population + Live API Wire-Up

As a **dev agent populating Wondercraft expertise stack**,
I want **L5 podcast-production references + L6 operational Wondercraft-specific context + L7 MCP tool wire-up against the live Wondercraft API**,
So that **Wondercraft has genuine expertise beyond the generator stub and can produce real podcast artifacts**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** `_bmad/memory/bmad-agent-wondercraft/` has L5 placeholder content
**When** the dev agent populates L5 with ≥3 podcast-production reference files (storytelling framework, audio-production patterns, narration-length-vs-engagement patterns)
**Then** the `INDEX.md` references all L5 files; `load_expertise` node reads them at specialist invocation; fingerprint per D1.

**Given** Wondercraft API credentials are in `.env`
**When** the dev agent adds `.mcp.json` entry for wondercraft-api + authors `app/specialists/wondercraft/act.py` calling the MCP tool
**Then** an integration test with real API credentials (marked `@pytest.mark.live_api`) produces a real podcast artifact (MP3 or similar) and stores it in a fixture directory.

**Given** the live API produces an artifact
**When** Wondercraft's `return` node yields `SpecialistReturn`
**Then** the return includes the artifact path, duration, and any Wondercraft metadata needed for downstream assembly.

---

### Story 2c.3: Time-to-Deploy Measurement + Party-Mode Validation

As an **operator validating the <1-dev-day plug-and-play claim**,
I want **end-to-end time-to-deploy measured (story open → first real artifact) + party-mode validation of the migration path**,
So that **M2 Required Evidence "Wondercraft time-from-open to first-real-artifact < 1 dev-day" has a defensible measurement**.

**Pts:** 1 | **Gate:** single | **K:** ~1.2×

**Acceptance Criteria:**

**Given** Stories 2c.1 + 2c.2 closed
**When** the dev agent logs total elapsed clock time from 2c.1 T0 → 2c.2 first-real-artifact
**Then** elapsed time is ≤ 1 dev-day (≤ 8 clock hours of active dev work; can span calendar days); if > 1 dev-day, root cause is documented.

**Given** M2 acceptance requires operator sign-off
**When** party-mode convenes (Winston + Murat + Paige + Quinn-R + Amelia)
**Then** consensus verdict GREEN-LIGHT with any riders documented; verdict recorded in `_bmad-output/implementation-artifacts/<slab-2c-close-artifact>`.

**Given** the innovation claim is measured
**When** M2 closes
**Then** the 15-invariant audit matrix adds Wondercraft entries (FR63 incremental roll-up per D12).

---

### Story 2c.4: Scaffold-Generator Polish + Specialist-Anti-Patterns Catalog Final 2b+2c Harvest

As a **dev agent closing Slab 2c**,
I want **generator polish from 2c.1 feedback + final anti-patterns catalog with ≥5 concrete entries (validated as harvested-not-invented)**,
So that **FR64 is met and the generator is production-ready for the optional second new specialist in Slab 5b**.

**Pts:** 2 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** Wondercraft generation in 2c.1 produced feedback
**When** the dev agent polishes the generator (bug fixes, clearer error messages, template improvements)
**Then** a regression test generates + conformance-validates a second throwaway specialist without issues; the throwaway is deleted.

**Given** the anti-patterns catalog had 5 entries at Slab 2b close
**When** the dev agent reviews 2b + 2c migration logs for any additional anti-patterns
**Then** the catalog is final with ≥5 entries (≥7 preferred); every entry names slab-of-discovery + example.

**Given** D12 protocol at slab-closing story
**When** close AC runs
**Then** invariant audit matrix entries for Slab 2c + anti-patterns catalog final + migration-guide §Anti-Patterns Appendix cross-refs added.

---

## Epic 3: Slab 3 Marcus Orchestration — Supervisor + Gates + DecisionCards + Verdict Flow

**Milestone:** M3 go/no-go — "Marcus orchestrates end-to-end."

**Goal:** Marcus runs Plan-and-Execute by default (ReAct on `explore` preset), routes to specialists via manifest, produces DecisionCards at every gate, operator verdict via CLI/MCP/FastAPI transports. HIL tamper-evidence enforced. New tracked trial run §01→§15 completes with operator approve/edit/reject at every gate.

**FR coverage:** FR19, FR20, FR24 (operator-facing UX), FR26–FR37, FR41 (party-mode-as-interrupt hook point).

**Stories:** 3.1, 3.2, 3.3, 3.4, 3.5, 3.6 (6 stories).

---

### Story 3.1: Marcus Intake + Orchestrator + Facade Split

As a **dev agent implementing Marcus per Story 30-1 duality split (forward-ported)**,
I want **`app/marcus/intake.py`, `app/marcus/orchestrator/{write_api.py, supervisor.py, routing.py}`, `app/marcus/facade.py` with Marcus-first activation discipline and sanctioned single-writer pattern**,
So that **FR26 + FR30 are enforced and Marcus is the SPOT operator-facing surface via `app.marcus.facade.get_facade()`**.

**Pts:** 5 | **Gate:** dual (package boundary + duality split) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** `app/marcus/` is empty at Slab 3 open
**When** the dev agent authors `intake.py` (pre-packet extraction per Story 30-1 lift), `orchestrator/write_api.py` (single-writer), `orchestrator/supervisor.py` (Plan-and-Execute default, ReAct on explore preset), `orchestrator/routing.py` (manifest-driven), `facade.py` (`get_facade()` lazy accessor)
**Then** import-linter contract green (`app.marcus.facade` reachable only from authorized transports; `app.marcus.orchestrator.write_api` is sanctioned single-writer; no `app.cora.*` imports).

**Given** Marcus's `supervisor.py` is authored
**When** a trial is started with `preset: production`
**Then** Plan-and-Execute reasoning loop runs; each step is routed per manifest via `routing.py`; no inline specialist selection.

**Given** the same trial is started with `preset: explore`
**When** the supervisor enters
**Then** ReAct mode runs instead; switching is deterministic via preset; unit test `tests/unit/marcus/test_preset_switching.py` covers both paths (FR27).

**Given** Marcus's sanctum cold-read discipline (FR30)
**When** a new session opens and Marcus is instantiated
**Then** `_bmad/memory/bmad-agent-marcus/` is read fresh; fingerprint recorded; no in-memory continuity from prior sessions.

---

### Story 3.2: DecisionCard Schema Family + Per-Gate Models

As a **dev agent implementing HIL gates**,
I want **`app/models/decision_cards/{base,g1,g2c,g3,g4}.py` with per-gate Pydantic DecisionCard subclasses + `DecisionCardMeta` carrying cache-state + override-trail + reject-rate context**,
So that **FR32 + D7 per-gate schema family is in place and gate schema drift is compile-time detectable**.

**Pts:** 4 | **Gate:** dual (schema-shape) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** no `app/models/decision_cards/` content exists beyond the Slab 1 stub directory
**When** the dev agent authors `base.py::DecisionCard` + `DecisionCardMeta` + per-gate subclasses for G1, G2C, G3, G4 following four-file-lockstep
**Then** each gate has model + schema.json + shape-pin test + golden fixture; `DecisionCardMeta.cache_state: Literal["healthy","mixed","cold"]` + `affected_nodes: list[str]` + `override_trail: list[OverrideEvent]` per D2.

**Given** the manifest's `edge.decision_card_schema` field is `app.models.decision_cards.g2c:G2CDecisionCard`
**When** the compiler validates the manifest
**Then** the dotted reference is importable; compile fails if not (per D6 validation).

**Given** each DecisionCard subclass has drafted_proposal + evidence + risks + approve/edit/reject verbs
**When** a test constructs a G4 DecisionCard
**Then** all fields are typed, validate_assignment=True enforces immutability-after-construction, `verb: Literal["approve","edit","reject"]` constrains verb set.

---

### Story 3.3: OperatorVerdict + ResumeApi + Import-Linter Tamper-Evidence

As an **architect of HIL invariant preservation (FR34)**,
I want **`app/gates/verdict.py::OperatorVerdict` + `app/gates/resume_api.py::resume_from_verdict()` + import-linter contract making resume_api callable only from three authorized transports + scheduler-import-forbidden contract for `app/gates/**`**,
So that **FR34 is architecturally unavailable to bypass (not merely conventionally avoided)**.

**Pts:** 5 | **Gate:** dual (invariant-preservation story) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** no `app/gates/verdict.py` exists
**When** the dev agent authors `OperatorVerdict` Pydantic model (frozen, validate_assignment, extra=forbid) with fields `trial_id, gate_id, verb, operator_id, timestamp, decision_card_digest, edit_payload | None`
**Then** four-file-lockstep green; cross-field validator enforces `edit_payload` required iff `verb == "edit"`.

**Given** `resume_api.py::resume_from_verdict(verdict) -> CompiledGraphHandle` is authored
**When** the import-linter contract runs
**Then** the only authorized callers are `app.mcp_server.tools.gate_decide`, `app.http.gate_endpoint`, `app.marcus.cli.gate_cli`; a test `tests/integration/gate_verdict_authority_test.py` greps the `app/` tree for unauthorized `OperatorVerdict` constructions + unauthorized `resume_from_verdict` callers and fails at compile if any found.

**Given** scheduler-import-forbidden ruff + import-linter rules
**When** the dev agent attempts to add `import asyncio` + `asyncio.sleep` to any file in `app/gates/**`
**Then** pre-commit + CI both reject with `SchedulerImportError`; test `tests/integration/gates/test_no_scheduler_import.py` asserts all four scheduler modules (`asyncio.sleep`, `threading.Timer`, `apscheduler`, `schedule`) are forbidden.

**Given** digest-match enforcement
**When** a synthetic `OperatorVerdict` is constructed with a `decision_card_digest` that doesn't match the emitted card
**Then** `resume_from_verdict` raises `GateError` + refuses to resume; test covers.

**Given** M3 Required Evidence
**When** a trial run confirms every gate's resume is driven by a valid `OperatorVerdict`
**Then** a staged attempt to bypass via `asyncio.sleep + direct Command(resume=...)` is rejected at graph-compile (M3 evidence bullet per D3).

---

### Story 3.4: Three-Transport Verdict Parity (MCP + FastAPI + CLI)

As an **operator with transport freedom**,
I want **identical `OperatorVerdict` submission via MCP `gate.decide`, FastAPI `POST /gate/verdict`, CLI `app.marcus.cli gate decide`, all routing through `resume_api`**,
So that **FR33 + D7 transport parity is operator-verified and no transport shortcut exists around tamper-evidence**.

**Pts:** 3 | **Gate:** single | **K:** ~1.4×

**Acceptance Criteria:**

**Given** three transports are implemented at `app/mcp_server/tools/gate.py`, `app/http/gate.py`, `app/marcus/cli/gate.py`
**When** the same `OperatorVerdict` payload is submitted through each transport
**Then** all three produce identical graph-resumption state; contract test `tests/integration/transport_parity_test.py` asserts state equality + identical ledger events + identical LangSmith traces.

**Given** each transport populates `operator_id`
**When** `OperatorVerdict.__init__` runs via any transport
**Then** `operator_id` is a real operator identifier (not null, not a scheduler name); scaffold-conformance test greps for unauthorized `operator_id` values.

**Given** DecisionCard cache-state surface (FR24)
**When** operator views any gate's DecisionCard via any transport
**Then** `DecisionCardMeta.cache_state` is populated with current prefix warmth; `override_trail` shows applied overrides; D2 warning fires before override applies.

---

### Story 3.5: Runtime Model-Override + Cache-Invalidation Warning (FR24 closure)

As an **operator choosing to override a specialist's model mid-trial**,
I want **a submission surface that warns me of cache-invalidation impact BEFORE I confirm the override + a running cache-state surface in every DecisionCard**,
So that **FR24 is met verbatim + D2 pre-submission + post-application dual warning is operator-visible**.

**Pts:** 3 | **Gate:** single | **K:** ~1.4×

**Acceptance Criteria:**

**Given** operator submits an override via any transport
**When** `submit_override(trial_id, node_id, new_model)` runs
**Then** `compute_cache_impact()` returns an `OverrideWarning` with: estimated cost impact, affected nodes, cache-state delta; operator sees warning; explicit `confirm_token` required to proceed.

**Given** operator confirms
**When** override is applied
**Then** `RunState.model_overrides[node_id]` is set; `CacheState` is updated; ledger event emitted (`kind: "override"`).

**Given** next gate fires
**When** DecisionCard is emitted
**Then** `DecisionCardMeta.cache_state` reflects current state ("mixed" if any overrides in flight; "healthy" if all nodes on default).

**Given** M3 Required Evidence
**When** the trial run closes
**Then** runtime model-override surface is functional AND warns of cache-invalidation impact (M3 bullet per D3).

---

### Story 3.6: End-to-End Trial Run with Marcus Supervisor + M3 Acceptance

As an **operator closing M3**,
I want **a new tracked trial run §01→§15 completes with Marcus as supervisor, DecisionCards at every gate, operator verdict via CLI (MCP + FastAPI optional at this milestone per PRD)**,
So that **M3 Required Evidence is accrued and Slab 3 closes to done**.

**Pts:** 5 | **Gate:** dual (slab-closing story + operator acceptance) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** Slab 3 stories 3.1–3.5 complete
**When** operator starts a trial run with a real input content bundle and `preset: production`
**Then** §01 through §15 executes; Marcus routes per manifest; every gate emits a DecisionCard; operator emits verdict at each gate via CLI; run closes cleanly.

**Given** operator exercises at least one `edit` verdict
**When** the edit propagates
**Then** downstream nodes consume the edit via `RunState` payload; reject-rate KPI tracks the decision distribution.

**Given** M3 operator decision
**When** party-mode convenes (Winston + Murat + Paige + Quinn-R + Amelia) with the trial evidence
**Then** consensus verdict Go/Revise/Halt recorded; if Go, Slab 4 opens.

**Given** D12 close protocol
**When** story closes
**Then** three-line AC: invariants #1 (Marcus SPOT), #2 (cold-start), #4 (HIL-paused), #12 (Marcus-first), #13 (specialist registry) preserved; anti-pattern entries if any; migration-guide §4 (Gate Migration) + §2 (Specialist Walkthrough — Marcus updated) deepened.

---

## Epic 4: Slab 4 Lockstep + Gates + Cora Dev-Graph + Ledger + Frozen-Graph Ceremony

**Milestone:** M4 go/no-go — "Governance regime is architectural."

**Goal:** Pipeline Lockstep becomes a CI graph-compile-time gate. Cora dev-graph compiles as sibling with separate thread namespace. Party-mode-as-`interrupt()` operationalized. Frozen-graph-version ceremony codified. Learning ledger captures events at G2C/G3/G4.

**FR coverage:** FR22 (policy logging), FR38–FR45, FR41, FR42, FR59 (invalidation-hook Slab-4 portion).

**Stories:** 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7 (7 stories).

---

### Story 4.1: Graph-Compile-Time CI Hook + Lockstep Enforcement

As a **CI governance system enforcing Pipeline Lockstep**,
I want **`scripts/check_manifest_lockstep.py` consuming the D6 compiler (validation mode) + PR-R's `check_dispatch_registry_lockstep.py` (when forward-ported) as library functions, running on every PR**,
So that **FR38 + FR39 are architecturally enforced + drift-impossible-to-merge**.

**Pts:** 5 | **Gate:** dual (CI-shape) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `scripts/check_manifest_lockstep.py` does not exist
**When** the dev agent authors it to call `compile_run_graph(manifest, validation_mode=True)` + `compile_dev_graph(dev_manifest, validation_mode=True)`
**Then** the script iterates the PR diff; for each block-mode-trigger-path in the diff, asserts companion updates in manifest + L1 script + pack; fails with `LockstepError` on drift.

**Given** a test PR intentionally touches a block-mode-trigger-path without companion updates
**When** CI runs the script
**Then** CI fails with `LockstepError` naming the drifted file + missing companion; merge blocked (M4 Required Evidence — "intentionally drifted PR rejected at CI").

**Given** GitHub Actions workflow is authored
**When** the workflow runs
**Then** the job runs the script in-process (not subprocess) for performance; completes in ≤60 sec per NFR-P6.

---

### Story 4.2: Cora Dev-Graph + Separate Thread Namespace

As a **governance system running story-cycle as a graph**,
I want **`app/cora/` with its own manifest (`state/config/dev-graph-manifest.yaml`) + sibling `StateGraph` compilation + separate thread namespace `dev/{story_id}`**,
So that **FR40 lane separation is architecturally enforced + invariant #15 preserved**.

**Pts:** 5 | **Gate:** dual (package + manifest shape) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `app/cora/` is empty
**When** the dev agent authors `app/cora/graph.py` + handlers for the story-cycle (plan_story, implement_story, test_story, review_story, close_story) + `state/config/dev-graph-manifest.yaml`
**Then** `compile_dev_graph(dev_manifest)` compiles; thread namespace is `dev/{story_id}` (distinct from Marcus's `run/{trial_id}`); import-linter confirms `app.cora` ⊥ `app.marcus`.

**Given** a test attempts to import from `app.marcus.*` inside `app/cora/**`
**When** import-linter runs
**Then** the contract fails; pre-commit blocks.

**Given** Cora's `block_mode_hook.py` (existing pre-commit behavior elevated per D4)
**When** a story-cycle run exercises it
**Then** the hook runs as a node in the Cora graph; surfaces violations as `GateError` at a dev-graph gate.

---

### Story 4.3: Party-Mode-as-`interrupt()` + Trace-First Review

As a **BMAD reviewer consuming gate evidence**,
I want **`app/gates/party_mode_as_interrupt.py` wrapping a party-mode gate as a checkpointed `interrupt()` node where multiple personas contribute via structured payload before operator verdict + code-review gates that cite LangSmith trace links as evidence**,
So that **FR41 + FR42 are met and M4 "at least one code-review gate cites a LangSmith trace link" is demonstrable**.

**Pts:** 4 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** party-mode-as-interrupt does not exist
**When** the dev agent authors the wrapper that accepts a list of `PartyModeContribution` payloads + emits a consolidated DecisionCard before operator verdict
**Then** a test in `tests/integration/gates/test_party_mode_as_interrupt.py` simulates a multi-persona contribution + verdict flow.

**Given** a real story review at M4
**When** a bmad-code-review gate cites a LangSmith trace link as evidence in its finding record
**Then** M4 Required Evidence is satisfied (FR42 closure per D3).

---

### Story 4.4: Learning Ledger + G2C/G3/G4 Events + Reject-Rate + Gate-Inventory Queries

As a **governance observer of HIL decisions**,
I want **`app/ledger/{events,emitter,queries}.py` + `schema.sql` Postgres table + G2C/G3/G4 event emission + `reject_rate_per_gate(trial_id)` + `gate_inventory(trial_id)` queries**,
So that **FR37, FR36, FR45 are met and NFR-R4 (idempotent emission) is enforced**.

**Pts:** 4 | **Gate:** dual (ledger event schema) | **K:** ~1.4×

**Acceptance Criteria:**

**Given** `app/ledger/` is empty
**When** the dev agent authors `events.py::LedgerEvent` discriminated union + `emitter.py::emit_ledger_event()` + `queries.py::reject_rate_per_gate + gate_inventory + sanctum_mutations`
**Then** four-file-lockstep for `LedgerEvent`; Postgres `ledger_events` table created via `schema.sql`; idempotent deduplication by `idempotency_key`.

**Given** G2C, G3, G4 gates fire in a trial run
**When** emission runs
**Then** ledger contains events for each gate; re-emission at same `idempotency_key` is a no-op (NFR-R4).

**Given** emission fails (Postgres unavailable)
**When** the handler proceeds
**Then** the node does not fail; log entry + counter increment (NFR-I2 parallel).

**Given** reject-rate query
**When** `reject_rate_per_gate(trial_id="...")` runs
**Then** returns dict mapping gate_id to reject-rate per KPI tracking (FR37).

**Given** gate-inventory query
**When** `gate_inventory(trial_id)` runs at trial close
**Then** returns the list of gate_ids fired; asserts equality with manifest-declared gate set for that trial's pack (FR36).

---

### Story 4.5: Frozen-Graph-Version Ceremony Doc + v42 Populate + Bump Policy

As a **governance author of reproducibility discipline**,
I want **`docs/dev-guide/frozen-graph-version-ceremony.md` codifying Tier-1/2/3 bump policy + `runtime/graphs/v42/` populated with manifest-snapshot + pack-version + compiled-graph-digest**,
So that **FR43 + FR44 are met and D8 ceremony is first-class documentation**.

**Pts:** 3 | **Gate:** single | **K:** ~1.2×

**Acceptance Criteria:**

**Given** `docs/dev-guide/frozen-graph-version-ceremony.md` does not exist
**When** the dev agent authors it with Tier-1/2/3 policy per D8 + worked example of a v42→v42.1 bump + worked example of v42→v43 bump + rollback procedure
**Then** doc ≥80% of outline; cross-references from migration-guide §7 added.

**Given** `runtime/graphs/v42/` is empty (Slab 1 stub only)
**When** the dev agent populates manifest-snapshot + dev-graph-manifest-snapshot + pack-version + dispatch-registry-snapshot (interim; M5 reconciles) + compiled-graph-digest
**Then** digest is SHA-256 of compiled StateGraph introspection; test asserts stability across runs.

---

### Story 4.6: Sanctum Invalidation Hook (FR59) + NFR-O3 Warnings

As an **operator wanting visibility into prefix-stability risk**,
I want **`app/runtime/sanctum_watcher.py` with watchdog file-watcher + NFR-O3 non-fatal warnings surfaced via ledger + DecisionCard meta section**,
So that **FR59 is met + D5 invalidation hook is operator-visible**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** runtime server is running
**When** operator modifies a sanctum file during an active trial
**Then** watchdog detects the change; hash-delta is computed; ledger event `kind: "sanctum_mutation"` is emitted; next DecisionCard's meta section includes a warning citing the mutated file + suggested invalidating commit.

**Given** sanctum mutation happens BEFORE an invocation
**When** specialist cold-reads
**Then** fingerprint reflects the mutated state; no spurious warning fires.

**Given** mutation happens DURING invocation
**When** the running trial continues (non-fatal)
**Then** warning logs + surfaces at next gate; trial does not fail (NFR-O3).

---

### Story 4.7: Pydantic + RetryPolicy Workaround + Slab 4 Close

As a **dev agent closing Slab 4**,
I want **the documented Pydantic + LangGraph RetryPolicy interaction workaround implemented and tested + Slab 4 close D12 protocol satisfied**,
So that **Slab 5 inherits a stable substrate for the replay + parity work**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** Pydantic + RetryPolicy interaction has a known gotcha (PRD §Implementation Considerations)
**When** the dev agent implements the workaround at `app/runtime/retry_policy.py`
**Then** a test in `tests/integration/runtime/test_retry_policy_pydantic.py` demonstrates the workaround working; `docs/dev-guide/langgraph-state-idioms.md` §6 (RetryPolicy + Pydantic) is updated from placeholder to final content.

**Given** M4 Required Evidence
**When** party-mode convenes with evidence from 4.1–4.6
**Then** verdict Go/Revise/Halt; if Go, Slab 5 opens.

**Given** D12 close protocol
**When** story closes
**Then** three-line AC: invariants #3 (deterministic neck — manifest CI), #5 (learning events), #9 (ledger side-effect), #15 (lane separation via Cora compilation) preserved; anti-pattern entries; migration-guide §6 (Lockstep CI), §7 (Frozen-Graph Ceremony) deepened.

---

## Epic 5a: Slab 5a Acceptance — Trial-Replay Regression + Head-to-Head Parity + Invariant Audit

**Milestone:** M5 go/no-go — "Migration ships."

**Goal:** Trial-replay regression suite covers 100% of closed trials. Head-to-head parity validation against primary-repo output. Cost-projection measurement ≥50% reduction. 15-invariant audit matrix rolls up. Sanctum invalidation hook production-ready.

**FR coverage:** FR49, FR50, FR51, FR52, FR55, FR56, FR57 (CLI portion), FR63, FR64 (catalog ≥5 confirmed).

**Stories:** 5a.1, 5a.2, 5a.3, 5a.4, 5a.5 (5 stories).

---

### Story 5a.1: Trial-Replay Regression Suite + CI Fail-Loud Mode

As a **governance system enforcing byte-for-byte reproducibility**,
I want **`app/replay/regression.py` + `tests/trial_replay/` populated with 100% coverage of closed tracked trial runs + CI fail-loud on pack-hash drift + D1-sanctum-fingerprint variance policy**,
So that **FR51 + NFR-X1 + NFR-X3 + NFR-X4 + NFR-X5 are met**.

**Pts:** 5 | **Gate:** dual (acceptance-shape) | **K:** ~1.5×

**Acceptance Criteria:**

**Given** closed trial runs exist in the clone (Slab 2/3/4 trials)
**When** `app/replay/regression.py::replay_all_closed_trials()` runs
**Then** every closed trial replays from final checkpoint; pack-hash is compared; drift raises `ReplayError` in CI fail-loud mode.

**Given** replay encounters a sanctum-hash mismatch
**When** CI mode is `fail-loud`
**Then** replay fails + names the fingerprint delta; in `warn-on-clone` mode, replay continues with snapshot fallback + provenance log (per D1).

**Given** the full regression suite runs
**When** GitHub Actions completes
**Then** 100% of closed trials replay green (or document variance bands per NFR-X5); total wall-clock ≤15 min per trial.

---

### Story 5a.2: Head-to-Head Parity Trial vs Primary

As an **operator validating migration MVP bar**,
I want **a new tracked trial run `C1-M1-PRES-<date>` produced in the clone against the same input content as a primary-repo trial + side-by-side artifact comparison**,
So that **FR52 is met + M5 operator sign-off has evidence base**.

**Pts:** 5 | **Gate:** dual (acceptance gate) | **K:** ~1.3×

**Acceptance Criteria:**

**Given** a primary-repo trial (e.g., `C1-M1-PRES-20260419B`) exists with closed artifacts
**When** the operator runs the same input content through the clone
**Then** the clone produces a new tracked trial `C1-M1-PRES-<clone-date>`; artifacts produced at §01→§15; LangSmith trace captures every node.

**Given** the two trials have completed
**When** the operator compares artifacts side-by-side
**Then** parity-or-better judgment recorded; where parity differs, rationale is captured in the M5 Required Evidence artifact.

**Given** party-mode convenes
**When** multi-persona review of the parity trial runs
**Then** consensus GREEN/YELLOW/RED recorded; rider findings documented.

---

### Story 5a.3: Economics Measurement + ≥50% Cost-Reduction Bar

As an **operator validating the migration economic argument**,
I want **`app/runtime/economics.py` measuring cache hit rate, token cost, per-specialist cost + comparison against a recorded baseline + ≥50% reduction target confirmed**,
So that **FR55 + FR56 + M5 cost-projection bar is met (≥50% reduction)**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** baseline cost of primary-repo trial is measured + stored at `_bmad-output/economics-baselines/primary-repo-baseline-<date>.json`
**When** the clone's head-to-head parity trial runs (Story 5a.2)
**Then** per-trial cost is measured with breakdown by specialist, tier, cache hit/miss.

**Given** comparison runs
**When** `app.runtime.economics::compute_reduction_percentage(baseline, new)` executes
**Then** reduction percentage is ≥50% per M5 acceptance bar; if <30%, M5 operator decision defaults to Revise or Rollback per PRD §Cost Projection.

**Given** cache hit rate ≥80% median is required at M5
**When** economics dashboard CLI runs
**Then** reported median is ≥80% across all nodes; if lower, prefix-stability audit is triggered.

---

### Story 5a.4: 15-Invariant Audit Matrix Roll-Up + FR64 Catalog Final

As an **operator closing M5 ship verdict**,
I want **the 15-invariant audit matrix rolled up from slab-by-slab entries (per D12 protocol) + anti-patterns catalog finalized with ≥5 concrete entries (validated harvested-not-invented)**,
So that **FR63 + FR64 are met and M5 acceptance has full invariant-preservation evidence**.

**Pts:** 3 | **Gate:** single | **K:** ~1.2×

**Acceptance Criteria:**

**Given** D12 per-slab-closing-story entries accumulated across Slabs 1–5a
**When** the dev agent rolls them up into the migration guide's 15-invariant audit matrix
**Then** each of 15 invariants has named file/test references proving preservation; matrix goes into migration-guide §1 or a dedicated §12 "Invariant Audit" appendix.

**Given** anti-patterns catalog has ≥5 entries from prior slabs
**When** the dev agent reviews final state
**Then** catalog has ≥5 entries, each with slab-of-discovery + real example + counter-pattern; migration-guide §Anti-Patterns Appendix cross-references.

---

### Story 5a.5: M5 Ship Decision + Party-Mode Green-Light

As an **operator making the ship/iterate/rollback decision at M5**,
I want **party-mode convening with full Slab-5a evidence (replay regression + parity + economics + invariant audit) + documented verdict**,
So that **the migration's central go/no-go gate has a defensible decision record**.

**Pts:** 2 | **Gate:** dual (operator decision) | **K:** ~1.2×

**Acceptance Criteria:**

**Given** Slab 5a stories 5a.1–5a.4 closed
**When** party-mode convenes (Winston + Murat + Paige + Quinn-R + Amelia + Dr. Quinn for strategic framing)
**Then** verdict Ship / Iterate / Rollback recorded in `_bmad-output/implementation-artifacts/m5-decision.md`.

**Given** verdict is "Ship"
**When** operator confirms
**Then** backport channel remains closed (per FR60); forward-port from primary starts per FR61 playbook; primary repo is marked as frozen-reference.

**Given** verdict is "Iterate"
**When** operator names specific findings
**Then** remediation stories open as Slab 5a extensions; M5 target date renamed; Slab 5b may defer.

**Given** verdict is "Rollback"
**When** operator names rollback reason
**Then** FR62 rollback plan activates: migration clone archived, primary repo continues production, learnings captured in retrospective.

---

## Epic 5b: Slab 5b Polish — Fork UX + Economics Dashboard + Guide Final + Generator Polish

**Milestone:** Follows M5 ship decision (non-blocking for M5 Ship verdict; cuttable per PRD MVP table).

**Goal:** Operator-visible polish + documentation final. Cuttable under pressure.

**FR coverage:** FR57 (dashboard portion), FR65 (migration guide final), fork UX polish, generator polish from 2c.1 feedback.

**Stories:** 5b.1, 5b.2, 5b.3, 5b.4 (4 stories).

---

### Story 5b.1: Fork UX Polish (CLI → IDE-Integrated)

As an **operator exploring what-if branches of a closed trial**,
I want **fork-from-checkpoint UX beyond the Slab 5a CLI baseline, with optional IDE integration via MCP `trial_run.fork`**,
So that **FR49 meets the Journey 2 operator experience beyond baseline**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** CLI-only fork works from Slab 5a
**When** the dev agent enriches the MCP `trial_run.fork` tool with a more informative return payload (fork preview, expected re-execution nodes)
**Then** an IDE client can offer a fork-preview UX; tests cover the richer return payload.

---

### Story 5b.2: Economics Dashboard Beyond CLI Dump

As an **operator monitoring migration economics**,
I want **an economics dashboard that goes beyond the Slab 5a CLI dump (web UI optional; queryable structured JSON minimum)**,
So that **FR57 meets Slab-5 polish bar + per-trial cost is queryable without trace-replay**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** CLI dump from Slab 5a
**When** the dev agent authors a `app/runtime/economics.py::query_dashboard()` returning structured JSON
**Then** per-trial cost + cache hit + tier distribution is queryable per NFR-O2 (without trace-replay).

---

### Story 5b.3: Migration Guide 11-Section Final

As a **dev team consuming migration context**,
I want **`docs/dev-guide/langgraph-migration-guide.md` with all 11 sections fully populated (not placeholder)**,
So that **FR65 is met (11 documented sections)**.

**Pts:** 3 | **Gate:** single | **K:** ~1.2×

**Acceptance Criteria:**

**Given** slab closings fed per-section content via D12 protocol
**When** the dev agent consolidates all 11 sections
**Then** Conceptual Map + Specialist Walkthrough + Manifest Translation + Gate Migration + Schema Migration + Lockstep CI + Frozen-Graph Ceremony + Forward-Port Playbook + Model-Selection Cutover + Rollback Plan + Anti-Patterns Appendix are all complete (no "placeholder — filled in Slab N" tags remaining).

**Given** forward-port playbook (§8) must include PR-R reconciliation checklist
**When** the section is finalized
**Then** the checklist lists the four reconciliation steps per A22 (dispatch-registry + L1-validator + sanctum-fingerprint + Pydantic-checklist compliance).

---

### Story 5b.4: Generator Polish + Second New Specialist Pilot

As a **governance check on plug-and-play generalization**,
I want **`bmad-create-specialist` polish from Slab 2c + 5b feedback + a second new specialist generated as generalization test**,
So that **innovation claim generalization is validated (Slab 2c Wondercraft was first; a second specialist beyond Wondercraft confirms pattern)**.

**Pts:** 3 | **Gate:** single | **K:** ~1.3×

**Acceptance Criteria:**

**Given** generator had feedback from Wondercraft generation
**When** the dev agent polishes + generates a second new specialist (operator picks; e.g., Canvas LMS or Qualtrics)
**Then** time-to-deploy ≤1 dev-day again; confirms generalization.

**Given** Slab 5b closes
**When** D12 close protocol runs
**Then** migration guide final rolls forward; anti-patterns catalog final; invariant audit final.

---

## Epic X: Cross-Cutting Governance Artifacts (Living Protocol)

**Goal:** Not its own epic in the traditional sense — a **protocol** applied at every slab-closing story. No discrete stories; instead, every slab-closing story (1.7, 2a.4, 2b.17, 2c.4, 3.6, 4.7, 5a.5, 5b.3) includes D12 three-line AC per architecture §Decision D12.

**FR coverage:** FR63 (incremental build-up), FR64 (incremental catalog), FR65 (incremental guide).

**Story count:** 0 discrete; 8 closing-story-embedded per slab.

**Enforcement:** `bmad-code-review` gate at every slab-closing story verifies the three-line AC. Missing = MUST-FIX.

---

## Story Count Summary

| Epic | Story Count | Points Estimate |
|---|---|---|
| 1 Slab 1 Substrate | 9 | ~25 pts |
| 2a Scaffold Pilot | 4 | ~14 pts |
| 2b Specialist Tranche | 17 | ~55 pts |
| 2c Wondercraft | 4 | ~8 pts |
| 3 Marcus Orchestration | 6 | ~25 pts |
| 4 Lockstep + Gates + Cora | 7 | ~27 pts |
| 5a Acceptance | 5 | ~18 pts |
| 5b Polish | 4 | ~12 pts |
| X Cross-Cutting | 0 discrete (embedded) | — |
| **Total** | **56 stories** | **~184 points** |

Aligns with PRD §Timeline (12–16 weeks wall-clock) at typical BMAD dev-agent story throughput (~12–15 points/week).

## Final Validation (Step 4)

### FR Coverage Verification

All 65 FRs map to at least one story's AC:

| FR | Covered by |
|---|---|
| FR1 | 1.1c (runtime_server), 1.6 (manifest-loaded graph) |
| FR2 | 1.1c (FastAPI runtime + MCP code substrate per middle-path consensus), 1.1d (MCP stdio smoke + FastAPI↔MCP byte-equivalent parity, M1 acceptance gate), 3.4 (3-transport verdict parity inheriting 1.1d baseline), 1.1b (mcp_server stub) |
| FR3 | 1.1b (native local postgres + init SQL), 1.5 (checkpointer retention) |
| FR4 | 1.6 (empty-graph + resume implicit), 3.6 (trial with resume) |
| FR5 | 1.5 |
| FR6 | 1.1c (LangSmith wiring), 1.3 (resolution trail spans) |
| FR7 | 1.1c |
| FR8 | 1.4 (loader + compiler), 1.6 (15-step stub manifest) |
| FR9 | 2a.1 (scaffold reference), all 2a/2b/2c migrations |
| FR10 | 1.1b (sanctum retention), all 2a/2b/2c migrations |
| FR11 | all 2a/2b/2c migrations; architecture D5 |
| FR12 | 2a.1 (scaffold reference), 2c.2 (L5+L6 wire-up) |
| FR13 | 2a.1 (generator), 2c.1 (Wondercraft generated), 5b.4 (second specialist) |
| FR14 | 1.7 (framework), 2b.16 (hardening), all 2a/2b migrations |
| FR15 | 1.4 (compiler subgraph support), all specialist migrations |
| FR16 | 2c.2 (MCP tool at L7), all specialist migrations with L7 |
| FR17 | 1.3 (cascade), 3.5 (override) |
| FR18 | 1.3, 2a.1 (model_config emission), all 2a/2b/2c migrations |
| FR19 | 3.5 |
| FR20 | 1.3 (registry), 3.1 (Marcus reasoning lock) |
| FR21 | 1.3 (auto-select deterministic) |
| FR22 | 1.3 (LangSmith trail), 1.7 (span-tag contract test) |
| FR23 | 1.3 (registry versioning), D13 procedure |
| FR24 | 3.5 (pre-submission warning), 3.4 (DecisionCard cache surface) |
| FR25 | 1.3 (adapter) |
| FR26 | 3.1 (facade + SPOT) |
| FR27 | 3.1 (preset switching) |
| FR28 | 3.1 (routing) |
| FR29 | 3.1 (registry delegation) |
| FR30 | 3.1 (Marcus cold-read on session) |
| FR31 | 3.2 (DecisionCard per-gate), 3.3 (interrupt wrapper) |
| FR32 | 3.2 |
| FR33 | 3.4 (three-transport parity) |
| FR34 | 3.3 (OperatorVerdict + resume_api + import-linter) |
| FR35 | 3.3 (resume path) |
| FR36 | 4.4 (gate_inventory query) |
| FR37 | 4.4 (reject_rate_per_gate query) |
| FR38 | 1.4 (compiler validation), 4.1 (CI hook) |
| FR39 | 4.1 (CI graph-compile-time drift detection) |
| FR40 | 4.2 (Cora dev-graph + import-linter) |
| FR41 | 4.3 (party-mode-as-interrupt) |
| FR42 | 4.3 (code-review cites traces) |
| FR43 | 4.5 (ceremony doc + v42 populate) |
| FR44 | 4.5 (Tier-1/2/3 policy) |
| FR45 | 4.4 (ledger emission at G2C/G3/G4) |
| FR46 | 3.6 (trial start), 5a.2 (parity trial) |
| FR47 | 3.6 (pause implicit via checkpoint), 5a.2 |
| FR48 | 3.6 (resume implicit via checkpoint) |
| FR49 | 5a.1 (replay), 5b.1 (fork UX) |
| FR50 | 5a.1 (byte-for-byte replay regression) |
| FR51 | 5a.1 |
| FR52 | 5a.2 (head-to-head parity) |
| FR53 | 3.4 (state.inspect via MCP), transport parity test |
| FR54 | 5a.3 (cache hit rate measurement) |
| FR55 | 5a.3 |
| FR56 | 5a.3 |
| FR57 | 5a.3 (CLI), 5b.2 (dashboard) |
| FR58 | 1.1c (LangSmith tracing at LLM call) |
| FR59 | 4.6 (invalidation hook) |
| FR60 | 1.1a (.env/gitignore discipline), all slab-closing stories per D12 |
| FR61 | 5b.3 (migration-guide §8 final), 2b.15 (interim reconciliation plan) |
| FR62 | 5b.3 (migration-guide §10 final), 5a.5 (rollback decision path) |
| FR63 | 5a.4 (audit matrix roll-up), D12 protocol every slab |
| FR64 | 2b.17 (first 5), 2c.4 (final ≥5 catalog), D12 protocol every slab |
| FR65 | 1.7 (skeleton), 5b.3 (final 11 sections) |

**All 65 FRs covered.**

### NFR Coverage Verification

All 43 NFRs have preserving stories:

- **Performance (6):** NFR-P1 (3.2 DecisionCard latency), NFR-P2 (1.1c runtime cold-start), NFR-P3 (1.5 Postgres retention write-budget), NFR-P4 (1.2 sanctum cold-read), NFR-P5 (5a.2 trial wall-clock comparison), NFR-P6 (4.1 graph compile <60s).
- **Security (7):** NFR-S1 (1.1a .env discipline), NFR-S2 (1.1c FastAPI 127.0.0.1), NFR-S3 (1.1b MCP local-only), NFR-S4 (1.1b Postgres auth), NFR-S5 (implicit via LangSmith client config), NFR-S6 (implicit, operator storage), NFR-S7 (implicit, no multi-tenant code).
- **Integration (6):** NFR-I1 (1.3 adapter retry behavior), NFR-I2 (4.4 ledger non-fatal on emit failure), NFR-I3 (1.5 Postgres-down pause), NFR-I4 (1.1b MCP version pin), NFR-I5 (2a.4 Texas unmodified), NFR-I6 (1.2 sanctum fatal-on-error).
- **Reliability (7):** NFR-R1 (1.5 retention + 3.6 resume), NFR-R2 (scaffold-conformance asserts idempotency per FR14 tests across 2a/2b/2c), NFR-R3 (3.3 gate re-entry), NFR-R4 (4.4 ledger idempotency), NFR-R5 (implicit via operator-presence design), NFR-R6 (implicit via Postgres checkpoint durability, 3.6), NFR-R7 (1.5 retention + checkpointer recovery).
- **Reproducibility (5):** NFR-X1 (5a.1 byte-for-byte replay), NFR-X2 (4.5 frozen-graph ceremony), NFR-X3 (1.2 fingerprint + 5a.1 snapshot fallback), NFR-X4 (1.2 model_overrides in RunState checkpointed), NFR-X5 (5a.1 documented variance bands).
- **Maintainability (8):** NFR-M1 (all 2a/2b/2c scaffold-conformance), NFR-M2 (1.4 compile-time lint), NFR-M3 (1.1b four-tier layout + all slabs populate), NFR-M4 (K-floor discipline on every story), NFR-M5 (four-file-lockstep on every schema-shape story 1.2/1.4/2b.15/3.2/4.4), NFR-M6 (D12 protocol every slab), NFR-M7 (D12 protocol every slab + 5b.3 final), NFR-M8 (1.7 + 4.5 + 5b.3 docs).
- **Observability (4):** NFR-O1 (1.1c LangSmith wiring), NFR-O2 (5b.2 queryable-without-replay), NFR-O3 (4.6 warnings non-fatal), NFR-O4 (1.3 resolution trail in every LLM span).

**All 43 NFRs covered.**

### Architecture T1 Findings Closure

| # | Finding | Closed by |
|---|---|---|
| Readiness #1 | NFR count drift 38→43 | Document-of-record lock in this epics file (43 canonical) |
| Readiness #2 | 7 FRs without milestone evidence | Per-FR stories listed above; evidence bullets embedded in ACs |
| Readiness #3 | Slab 2 oversized | Epics 2a/2b/2c per D10 |
| Readiness #4 | Slab 5 bundled | Epics 5a/5b per D11 |
| Readiness #5 | Cross-slab governance | Epic X protocol + D12 on every slab-closing story |

### Dependency Verification

- Every story within an epic is independently completable in sequence (no forward dependency within epic).
- Cross-epic dependencies are slab-boundary-aligned: Epic 1 must close before Epic 2a opens; 2a closes before 2b; 2b closes before 2c; 2c + M2 gate before 3; 3 + M3 gate before 4; 4 + M4 gate before 5a; 5a + M5 ship verdict before 5b (or 5b cut).
- No forward dependency across stories within a single epic (Amelia's Story 1a→1b→1c is the exception: strict serial per Amendment F, intentional).

### Stories Ready For `bmad-create-story`

All 56 stories have sufficient AC + context + K-floor + gate-type designation to feed `bmad-create-story` at Slab 1 open. Authorship cadence:

- **Now (Slab 1 opens):** Stories 1.1a, 1.1b, 1.1c authored first; other Slab 1 stories follow.
- **Deferred to owning slab:** Stories for Epics 2–5 remain in this document as specs until their slab opens. Each slab's kickoff will promote the epic's stories to `ready-for-dev` via `bmad-create-story` on each.

### Risks + Open Items (For Operator Visibility)

1. **Winston's MCP-in-Slab-1 question** — default committed (seven-package Slab 1 scope with `app/mcp_server/` included). Operator can override at Slab 1 kickoff.
2. **Wondercraft <1-dev-day measurement** — ambitious; if elapsed > 1 dev-day on first attempt, Story 2c.3 documents root cause rather than failing the epic outright.
3. **PR-R forward-port timing** — if primary's PR-R closes before M5, reconciliation pass is lightweight; if after, forward-port playbook §8 handles it. Either way, interim clone-local dispatch-registry.yaml (Story 2b.15) keeps the clone self-sufficient.
4. **Slab 2b specialist roster finalization** — the 14 non-conformant specialists need a final roster confirmation at Slab 2b open (who are the 14 — Gary, Vera, Quinn-R + 11 others — depending on Slab 2a outcome and any deferrals).
5. **Tier-2/3 model-registry bumps during migration** — if a mid-migration bump is needed (e.g., OpenAI deprecates `o3-mini`), D13 procedure activates; may open a named story in the active slab.

### Deferred Inventory Entries Queued

Per architecture Step 8 handoff:

1. PR-R cross-repo Pydantic-checklist injection (primary-repo scope; Named-But-Not-Filed follow-on).
2. MCP-in-Slab-1 operator decision (default: in; operator can override).
3. Sanctum fingerprint enumeration spike (Slab 1 Story 1.2 AC — chronology.md exclusion from fingerprint decided during story).

These land in `_bmad-output/planning-artifacts/deferred-inventory.md` at Slab 1 kickoff or at operator convenience.

---

## Completion

**Epic + story decomposition for the LangChain + LangGraph migration is complete.**

- 65/65 FRs covered across 9 epics + Epic X protocol.
- 43/43 NFRs preserved across stories.
- 5/5 readiness findings closed.
- 56 stories authored with AC + gate-type + K-floor estimates.
- All 15 load-bearing invariants have preserving stories.
- PR-R forward-port convergence staged with reconciliation plan.
- M1–M5 acceptance bars expressed as concrete story-level ACs.

**Ready for Slab 1 kickoff** — Stories 1.1a, 1.1b, 1.1c queue first per Amelia's strict-serial pattern. Remaining Slab 1 stories (1.2–1.7) open in parallel-allowed order once 1.1c closes.
