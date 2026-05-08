---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
status: 'complete'
completedAt: '2026-04-22'
lastStep: 8
partyModeRound1:
  date: '2026-04-22'
  participants: ['Winston', 'Murat', 'Paige', 'Amelia', 'Quinn-R']
  verdict: 'GREEN-LIGHT WITH RIDERS'
  amendments_accepted: ['A-lane-split-altitude', 'B-package-FR-traceability', 'C-canary-tests-all-4-tiers', 'D-scaffold-conformance-framework-slab-1', 'E-langgraph-state-idioms-doc', 'F-story-1-split-1a-1b-1c', 'G-CLONE-FORK-NOTICE-at-story-1b', 'H-survey-and-discard-subsection', 'I-langgraph-idiom-sanity-check']
  open_questions: ['Does Slab-1 smoke test exercise MCP, or only FastAPI localhost? — determines whether mcp_server/ is Slab 1 or Slab 2.']
decisions_locked:
  D1: 'Sanctum snapshot — Option C Hybrid (content-hash per checkpoint + trial-close snapshot; live disk canonical; warn-on-clone, fail-loud-on-CI-replay)'
  D6: 'Manifest-as-graph-config loader — Option C Hybrid (manifest declares topology: step IDs, handler names, edge kinds, gates, block-mode-trigger-paths, subgraph mounts; Python provides handlers, reducers, predicates; schema-as-boundary-not-corset)'
  D2: 'Model-cascade — SQ1-a central app/models/selector.py + SQ2-a state-embedded overrides (RunState.model_overrides) + SQ3-c both-warnings (pre-submission + DecisionCard cache-state surface) + SQ4-a per-specialist model_config.yaml; registry governance Tier-1/2/3 mirrors pack-version policy; closes readiness FR24 + T1 #7'
  D3: 'HIL tamper-evidence — signed OperatorVerdict Pydantic model (verb/operator_id/decision_card_digest/timestamp) + sole resume_api module callable only from MCP/FastAPI/CLI transports + import-linter contract against scheduler imports in app/gates/** + digest-match enforcement + ledger-based reject-rate (FR37) + gate-inventory audit at trial close (FR36); closes readiness FR34/FR36/FR37 + adds M3/M4/M5 evidence bullets for FR24/FR27/FR42/FR53. Idle-gate policy: default (i) — trial stays paused indefinitely, no notification (pure FR34 fidelity; pings are Growth phase)'
  D4: 'Graph-compile-time CI — two manifests (pipeline-manifest.yaml for Marcus + dev-graph-manifest.yaml for Cora, separate files) + compiler validation mode (no checkpointer) consumed by scripts/check_manifest_lockstep.py as library function + PR-R L1 validator (check_dispatch_registry_lockstep.py) consumed as library, not subprocess, in same hook + GitHub Actions job runs compiler in validation mode on every PR; drift surfaces as ImportError or ValidationError with named artifact + AC line. Slab 4 deliverable.'
  D5: 'Sanctum cold-read + invalidation — atomic multi-file read via pathlib glob + Pydantic SanctumContent model capturing all files (INDEX.md, PERSONA.md, L5 refs, chronology.md, access-boundaries.md); fingerprint covers exactly the files read (Slab 1 early spike picks the enumeration). Invalidation hook: watchdog-based file-watcher on `_bmad/memory/` surfaces hash-change events to running trials as NFR-O3 warnings (not fatal); emitted via ledger (Slab 4) for audit. No git-hook approach — too indirect; no periodic digest — too slow. File-watcher + hash-on-read combo: detection latency ≤200ms per NFR-P4.'
  D7: 'Operator-surface contract (Developer-tool-UX) — three-transport verdict parity (MCP gate.decide, FastAPI POST /gate/verdict, CLI app.marcus.cli gate decide) all accept identical OperatorVerdict Pydantic payload; MCP tool surface fixed at Slab 1 (trial_run.start/resume/fork/replay, specialist.invoke, gate.decide, state.inspect, model.override); FastAPI endpoints mirror 1:1 with /trial, /gate, /state, /model routes; CLI subcommands mirror. DecisionCard shape locked at Slab 3 but schema declared Slab 1 (per-gate schemas live at app/models/decision_cards/{gate_id}.py and are referenced by manifest interrupt edges per D6). Transport parity enforced by a contract test: same OperatorVerdict submitted through all three transports must produce identical graph resumption.'
  D8: 'Frozen-graph-version layout + bump ceremony — runtime/graphs/v42/ directory contains: manifest-snapshot.yaml (pipeline-manifest as shipped), dev-graph-manifest-snapshot.yaml, pack-version.txt, dispatch-registry-snapshot.yaml (post-PR-R forward-port), compiled-graph-digest.txt (SHA-256 of compiled StateGraph introspection). Tier-1 patch (prose/connective tissue) = dev-agent authority, no bump. Tier-2 (new step / new edge kind / new gate) = single-gate party-mode, minor bump v42→v42.1. Tier-3 (palette restructure / new pack family) = full party-mode + operator sign-off, major bump v42→v43 with v42/ frozen on disk. Ceremony doc: docs/dev-guide/frozen-graph-version-ceremony.md (Slab 4 deliverable).'
  D12: 'Cross-slab governance artifact ownership — at every Slab close, the closing story-spec includes three mandatory AC lines: (1) "invariant-preservation note" for each load-bearing invariant touched this slab with file/test references (feeds FR63 M5 audit matrix); (2) "anti-pattern harvest" entry if any anti-pattern encountered (feeds FR64 catalog; empty entry acceptable at Slabs 1/3/4; minimum ≥5 concrete by M5); (3) "migration-guide-section-update" naming which section(s) of docs/dev-guide/langgraph-migration-guide.md this slab revised (feeds FR65 final guide; placeholder sections exist Slab 1 onward). Enforced by bmad-code-review gate checklist at every Slab close. Does not require its own epic — lives as a protocol applied at every slab-closing story.'
  D9: 'Milestone evidence gaps closure — already accomplished in D2 (FR24 pre-submission cache-invalidation warning + DecisionCard meta surface) and D3 (FR27 Plan-and-Execute/ReAct preset bullet at M3, FR34 tamper-evidence bullet at M3, FR36 gate-inventory audit at M5, FR37 reject-rate KPI at M5, FR42 code-review trace citation at M4, FR53 state.inspect verification at M5). No separate architecture action needed; the six amendment bullets land in M1-M5 Required Evidence via PRD amendment at Step 7 (validation).'
  D10: 'Slab 2 sizing — split into 2a/2b/2c per PR-R forward-port inheritance. 2a: 3 PR-R-conformant edges migrated to 9-node scaffold (Irene Pass 2, Kira motion, Texas; low risk; ~1 week). 2b: 14 non-conformant edges retrofitted to PR-R dispatch-registry.yaml + migrated to 9-node scaffold (higher risk; ~3-4 weeks). 2c: Wondercraft pilot + anti-patterns catalog harvest + scaffold-generator (`bmad-create-specialist`) validated on a fresh non-migrated specialist (~1 week). Each sub-slab is an epic at bmad-create-epics-and-stories time.'
  D11: 'Slab 5 split — accept. 5a Acceptance (~1-1.5 weeks): trial-replay regression suite + head-to-head parity validation + cost-projection measurement + 15-invariant audit matrix + sanctum invalidation hook — M5 go/no-go gate. 5b Polish (~0.5-1 week, cuttable under pressure per PRD): fork UX CLI-to-IDE enrichment + economics dashboard beyond CLI dump + migration guide §1-11 completion if not already complete per D12 protocol. Two distinct epics at epic-authoring time.'
  D13: 'Mid-migration model-registry bump procedure — documented at app/models/ Slab 1 deliverable. Tier-1 (new model appended, no default changes): dev-agent authority in any slab; registry-version line in that slab closing-story AC. Tier-2 (default tier changes e.g., reasoning-tier switches from o3-mini to successor): single-gate party-mode; story-opening required in the current slab. Tier-3 (palette restructure): full party-mode + operator sign-off; may pause current slab. Documentation at docs/dev-guide/model-selection-guide.md (Slab 1) includes "Mid-migration bump procedure" section.'
forward_port_convergences:
  PR-R: 'Primary-repo Sprint #1 PR-R (Marcus dispatch reshaping — Pydantic input/receipt envelopes + dispatch-registry.yaml + L1 lockstep validator + Irene/Kira/Texas retrofits) is upstream proof-of-pattern for migration 9-node scaffold + FR14 conformance + FR39 graph-compile lockstep. Forward-port at M5 brings dispatch-registry.yaml as manifest companion; L1 validator consumed as library by graph-compile CI hook; migration-guide §8 lists reconciliation checklist. Implication for Slab 2 sub-structure: 2a (3 PR-R-conformant edges — Irene Pass 2, Kira motion, Texas — low risk), 2b (14 non-conformant edges — Gary, Vera, Quinn-R + 11 others — higher risk), 2c (Wondercraft + anti-patterns harvest). Cross-repo signal to operator: inject Pydantic-v2 four-file-lockstep checklist into PR-R T1 readings before primary dev-story opens, to avoid reconciliation pass at M5. Marcus-duality (Story 30-1 — Intake + Orchestrator + facade split) forward-ported into app/marcus/ package structure.'
inputDocuments:
  - _bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-04-22.md
  - _bmad-output/planning-artifacts/research/technical-langchain-langgraph-migration-research-2026-04-21.md
  - docs/project-context.md
  - docs/agent-environment.md
  - CLAUDE.md
workflowType: 'architecture'
project_name: 'course-DEV-IDE-with-AGENTS'
subject: 'LangChain + LangGraph Migration Architecture'
user_name: 'Juanl'
date: '2026-04-22'
branch: 'dev/langchain-langgraph-foundation'
upstream_prd: 'prd-langchain-langgraph-migration.md'
readiness_t1_inputs:
  - FR34 HIL invariant needs acceptance surface
  - Six FRs need milestone evidence (FR24, FR27, FR36, FR37, FR42, FR53)
  - Slab 2 sizing — split into ≥2 epics
  - Slab 5 split — 5a Acceptance / 5b Polish
  - Cross-slab ownership for FR63 / FR64 / FR65
  - Operator-surface contract (CLI + MCP + FastAPI + DecisionCard) as §Developer-tool-UX
  - Mid-migration model-registry-bump handling
provider_lock: 'OpenAI API (2026-04-22 decision); three-level model-selection cascade; Marcus locked to best reasoning; specialists default gpt-4.1 family.'
---

# Architecture Decision Document — LangChain + LangGraph Migration

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together. Target: migration of the APP orchestration pipeline onto a self-hosted LangChain + LangGraph runtime while preserving all 15 load-bearing substrate invariants._

**Anchor artifacts:**
- [PRD](prd-langchain-langgraph-migration.md) — 65 FRs / 43 NFRs / 5 slabs / 5 milestones
- [Readiness report](implementation-readiness-report-2026-04-22.md) — 5 T1 findings staged
- [Research substrate](research/technical-langchain-langgraph-migration-research-2026-04-21.md) — 12-pattern → 15-invariant mapping

## Project Context Analysis

### Requirements Overview

**Functional Requirements (65 FRs across 9 capability areas).** The FR body reads as a **platform specification**, not a feature wishlist. Two load-bearing halves:

- **Runtime platform** (FR1–FR25 + FR54–FR59): persistent LangGraph service + Postgres checkpointing + OpenAI automatic cache + MCP/FastAPI bridges + LangSmith traces + three-level model-selection cascade + economics telemetry. Describes a **self-hosted service** with specific operational shape, not a library.
- **Orchestration discipline** (FR26–FR53 + FR60–FR65): Marcus-as-SPOT + gate-as-interrupt + DecisionCard curation + Cora/Marcus lane separation + manifest-as-graph-config + frozen-graph-version + trial-run replay/fork + 15-invariant audit + anti-patterns catalog + migration guide. Describes a **governed multi-agent execution regime**, not incidental glue.

Coverage verified by readiness report (100% of FRs have slab assignment; no orphans).

**Non-Functional Requirements (43 NFRs across 7 categories).** Load-bearing inputs to architecture decisions, not post-hoc quality bars:

- **Performance (6)** — mostly operator-latency budgets (DecisionCard ≤5s, cold-start ≤10s, checkpoint ≤500ms, sanctum ≤200ms). Shapes physical deployment (local native Postgres on operator's machine; sanctum on local SSD; MCP over localhost).
- **Security (7)** — single-operator trust boundary (`.env` discipline; `127.0.0.1`-only FastAPI; local MCP; no multi-tenant). Constrains escape-hatch API surface area.
- **Integration (6) — brownfield-critical** — transient OpenAI tolerance; LangSmith non-fatal; Postgres-down → thread-pause; MCP protocol spec pinned; **Texas retrieval unmodified (NFR-I5)**; sanctum fatal-on-error.
- **Reliability (7)** — operator-presence availability; checkpoint-recoverable; `act` idempotent; `interrupt()` re-enterable; ledger idempotent; ≥48hr pause survival. Shapes state-machine discipline at every node.
- **Reproducibility (5, domain-critical, non-stock)** — byte-for-byte replay; frozen graph versions; sanctum snapshot (inline OR content-hash) into checkpoint; model selections + auto-select fallback trails preserved; documented temperature variance. **Architectural requirements, not test requirements.**
- **Maintainability (8, load-bearing here)** — scaffold-conformance mandatory; `model_config.yaml` lint-at-compile; four-layer test strategy non-excusable; K-floor 1.2–1.5×; Pydantic four-file-lockstep; living anti-patterns catalog; migration guide kept current; `docs/dev-guide/` covers every extension.
- **Observability (4)** — 100% trace coverage at single-operator volume; economics queryable without replay; sanctum-invalidation warnings; model-resolution trail in every LLM span.

### Scale & Complexity

- **Primary domain:** internal multi-agent orchestration platform (developer-tool shape; Python framework + persistent service).
- **Complexity:** high — driven by 15 load-bearing substrate invariants (drop-rate budget zero), not regulatory load.
- **Deployment:** single-operator self-hosted. Local native Postgres (operator-installed; no container runtime required); IDE+CLI clients via MCP; FastAPI localhost-only escape hatch.
- **Estimated top-level packages:** ~12 (`app/runtime/`, `app/models/`, `app/specialists/`, `app/orchestrator/marcus/`, `app/orchestrator/cora/`, `app/gates/`, `app/state/`, `app/ledger/`, `app/mcp_server/`, `app/http/`, `app/manifest/`, `app/replay/`) plus sanctum tree + `runtime/graphs/v42/` siblings + `scripts/dev/init_postgres.sql` bootstrap + test tiers.

### Technical Constraints & Dependencies

**Hard locks (cannot relitigate):**

- **Provider = OpenAI API.** `langchain-openai` + `openai` SDK. `ChatOpenAI` wrapped in `app/models/adapter.py`. Anthropic + `AnthropicPromptCachingMiddleware` out of scope. Caching = OpenAI automatic prompt cache (no middleware).
- **Runtime = self-hosted OSS LangGraph.** Not LangGraph Platform. Not LangServe.
- **Persistence = `langgraph-checkpoint-postgres`** on PostgreSQL 15+. Retention + cleanup = Slab-1 acceptance.
- **Bridge = MCP primary, FastAPI escape-hatch (localhost only).** MCP-version pinned per Slab 1; bumps are Tier-1/2/3 governance.
- **State shape = Pydantic v2** with `validate_assignment=True`, timezone-aware datetimes, UUID4 validation, triple-layer red-rejection on closed enums, `Field(exclude=True) + SkipJsonSchema` for audit fields. Four-file-lockstep inherited.
- **Language = Python 3.12+**, `uv` preferred.
- **Migration posture = bounded big-bang in clone.** Backports stop after Slab 1 opens; forward-ports batch at M5.

**Brownfield integration points (wire in, don't re-design):**

- Texas Shape 3-Disciplined retrieval contract — unmodified per NFR-I5.
- Sanctum directories (`_bmad/memory/bmad-agent-{name}/`) — identity source of truth.
- Existing specialist API wrappers (Descript / ElevenLabs / Gamma / Canvas / …) re-homed at L7 MCP tools in scaffold `act` node.
- `bmad-agent-builder` retained for non-runtime agents; new `bmad-create-specialist` generator in Slab 2.
- Pipeline manifest becomes compile-time topology source; existing L1 check scripts migrate to graph-compile-time enforcement.
- Pydantic-v2 schema-shape scaffold at `docs/dev-guide/scaffolds/schema-story/` — authoritative during migration.
- Deferred-inventory governance (CLAUDE.md) — standing register continues.
- BMAD sprint governance (party-mode green-light + bmad-code-review + consensus + stop-conditions) — migration operates under this, no exception.

**Forbidden zones (explicit out-of-scope):**
`langserve`; LangChain high-level agent abstractions; Celery/Ray/Dask; multi-tenant concurrency; remote deployment; HA clustering/failover; SOC 2 / ISO 27001 / WCAG / GDPR / HIPAA / FERPA / COPPA; sub-second LLM latency.

### Cross-Cutting Concerns Identified

**Eight PRD-native concerns requiring architectural decisions (not epic-deferrable):**

1. **Lane separation Cora dev-graph ⊥ Marcus run-graph.** FR40 + substrate invariant #15. How lanes compile (separate `StateGraph`? separate packages? separate compilation units?); how shared specialists are lane-respecting.
2. **Three-level model-selection cascade.** FR17–FR21 + FR24 + FR25. Where resolution lives; how overrides pass through subgraph boundaries; when cache-invalidation warning fires.
3. **Reproducibility / frozen-graph discipline.** NFR-X1–X5 + FR43/FR44/FR50. Sanctum snapshot strategy (inline vs. content-hash); graph-version directory layout; Tier-1/2/3 version-bump governance hook.
4. **HIL invariant preservation.** FR31–FR37 + Decision 4 + substrate invariant #4 + **readiness finding FR34**. DecisionCard schema versioning; verdict pathway parity (CLI + MCP + FastAPI); tamper-evidence that no timer can bypass operator.
5. **Sanctum cold-read discipline + cache-prefix stability.** FR11 + FR30 + NFR-I6 + FR59. Cold-read contract; invalidation hook placement; sanctum snapshot approach (A inline / B content-hash).
6. **Pipeline Lockstep elevation from pre-commit to graph-compile CI.** FR38/FR39 + Pipeline Lockstep regime. What "graph compile" means in code; how compile-time errors surface to CI; how dev-graph compiles the run-graph to check drift.
7. **Four-layer testing + K-floor discipline.** NFR-M3 + NFR-M4. Test directory layout; scaffold-conformance framework; trial-replay harness shape; how dev-graph drives story-cycle tests.
8. **Operator-surface contract.** Readiness T1 #6. `§Developer-tool-UX` section naming every operator-facing surface + transport parity.

**Five concerns from readiness T1 inputs:**

9. **Milestone evidence gaps** — Finding #2. Commit named evidence bullets closing FR24, FR27, FR34, FR36, FR37, FR42, FR53.
10. **Slab 2 sizing** — Finding #3. Commit to ≥2-epic decomposition (scaffold-generator vs. 17-specialist-tranche + Wondercraft), or reject split with rationale.
11. **Slab 5 split** — Finding #4. Commit to 5a Acceptance + 5b Polish, or reject split with rationale.
12. **Cross-slab governance artifact ownership** — Finding #5. Per-slab "governance artifact" track for FR63 invariant audit, FR64 anti-patterns catalog, FR65 migration guide.
13. **Model-registry mid-migration bump procedure** — T1 #7. Which Slab owns it; which doc; default Tier-1 handling.

These thirteen concerns form the architectural decision queue the downstream steps will close.

## Starter Template Evaluation

### Primary Technology Domain

Internal multi-agent orchestration platform (Python framework + persistent service). No conventional starter applies — the PRD pre-locks every decision a starter would normally decide (language, runtime, state modeling, checkpointing, LLM SDK, IDE bridge, package manager).

### Artifacts Surveyed and Discarded (Survey-and-Discard, Amendment H)

Documents what was evaluated and why rejected — distinguishes informed rejection from NIH reflex.

| Artifact | What it provides | Reason discarded | Anything worth importing? |
|---|---|---|---|
| `langgraph-cli new` (OSS) | Single-graph `StateGraph` + `MemorySaver` skeleton; `langgraph.json` deploy descriptor; `.env.example` with Platform keys | `langgraph.json` is the LangGraph Platform deploy descriptor — violates self-hosted OSS hard lock. Single-graph topology has no lane separation. `.env.example` presumes Platform keys. Wholesale absorption = >80% delete ratio (not a starter — a distraction). | Reference only: (a) their minimal `StateGraph` + `MemorySaver` example as a one-file idiom sanity check (Amendment I); (b) `.gitignore` patterns for `.langgraph_api/` and `langgraph.json` artifacts; (c) their pytest `conftest.py` pattern for graph-under-test fixtures *if* Platform-free. None of these are starter surface — they're cheap reference copies. |
| LangChain-AI reference apps (`open_deep_research`, supervisor-agent templates) | Full reference projects | Use forbidden high-level agent abstractions (`AgentExecutor`, `initialize_agent`). Embody the opposite of "reject the LangChain cage." Topology wrong. | Nothing — the rejection is architectural, not stylistic. |
| LangGraph templates registry (supervisor-worker template, 2026) | Per-pattern topology starter | Partial topology fit but pulls LangGraph Platform dependencies we've locked out. Also lacks sanctum pattern, manifest-as-graph-config, Cora/Marcus lane separation, DecisionCard, frozen-graph-version. | Nothing — the Platform dependency alone disqualifies it. |

**Ratio test (delete-to-keep):** `langgraph-cli new` wholesale absorption = ~80% delete. Rejection stands on evidence, not reflex.

### Selected Approach: In-Clone Scaffold (No External Starter)

Six novel patterns are load-bearing from Slab 1 and cannot be retrofitted onto any external starter:

1. Sanctum-backed L0–L8 expertise stack (file-backed Sacred Truth, cold-read on every invocation)
2. Manifest-as-graph-config (pipeline manifest as compile-time topology source)
3. Gate-as-`interrupt()` + curated DecisionCard payload
4. Frozen-graph-version (runtime-as-immutable-artifact, `runtime/graphs/v42/` siblings)
5. Two-graph lane separation (Cora dev-graph ⊥ Marcus run-graph, separate thread namespaces)
6. "Reject the LangChain cage" — 8 operating rules + 5 anti-patterns codified before specialist migration opens

PRD §Code Examples pre-names three canonical in-clone scaffolds as Slab-1/Slab-2 deliverables (`app/specialists/_scaffold/`, `app/gates/example_gate/`, `app/specialists/wondercraft/`).

### Lane Separation Altitude (Amendment A — Winston)

**FR40 + substrate invariant #15** mandate Cora dev-graph ⊥ Marcus run-graph with no lane crossover. Lane separation is **enforced by package boundary**, not by convention.

**Decision:** `app/marcus/` and `app/cora/` are **siblings under `app/`**, NOT nested under a shared `app/orchestrator/` parent. A shared parent would attract "just a small helper both lanes use" commits that the compiler happily resolves while the invariant silently degrades.

**Enforcement:** one-line `import-linter` contract — neither `app.marcus` nor `app.cora` can import from the other. Grep for `from app.cora` inside `app/marcus/` (and vice versa) trips CI.

**Rejected:** top-level `marcus/` and `cora/` outside `app/` — wrong altitude (application code should not sit peer to `tests/`, `docs/`, `scripts/`).

### Package-to-FR Traceability Table (Amendment B — Quinn-R)

Each proposed package maps to specific FR/NFR justifications and a first-use slab. **Packages that can't fill both columns are deferred to their first-use slab.** Conservative cut driven by this table is recorded in the next subsection.

| Proposed package | Justifying FR(s) / NFR(s) | First-use slab | Slab 1 scope? |
|---|---|---|---|
| `app/runtime/` | FR1, FR3, FR4, FR7 — persistent LangGraph service + Postgres checkpointing + thread resume + Python entry-point | Slab 1 | **YES** (substrate) |
| `app/models/` | FR17, FR21, FR23, FR25; NFR-M2 — three-level cascade, selector, registry, adapter, lint-at-compile | Slab 1 | **YES** (substrate) |
| `app/state/` | NFR-M3 unit layer + Pydantic v2 state base classes (FR-implicit across all slabs) | Slab 1 | **YES** (substrate) |
| `app/manifest/` | FR8, FR38, FR39 — manifest as compile-time topology source + graph-compile-time lockstep | Slab 1 (FR8) / Slab 4 (FR39 CI) | **YES** (FR8 loader substrate at Slab 1) |
| `app/http/` | FR2 FastAPI escape-hatch; NFR-S2 127.0.0.1 binding | Slab 1 | **YES** (substrate + smoke test entry) |
| `app/mcp_server/` | FR2 MCP primary bridge; NFR-I4 MCP version pinning | Slab 1 (if smoke exercises MCP) / Slab 2 (if FastAPI-only smoke) | **PENDING — operator question below** |
| `app/specialists/` | FR9–FR16 (9-node scaffold + generator + sanctum anchoring + expertise stack + conformance) | Slab 2 | NO — deferred (scaffold conformance FRAMEWORK lives in `tests/integration/scaffold_conformance/` at Slab 1 per Amendment D; `app/specialists/` itself deferred) |
| `app/marcus/` | FR26–FR30 (Marcus SPOT, Plan-and-Execute, manifest-driven routing, registry delegation, sanctum cold-read) | Slab 3 | NO — deferred |
| `app/cora/` | FR40 (Cora dev-graph sibling, separate namespace); substrate invariant #15 | Slab 4 | NO — deferred |
| `app/gates/` | FR31–FR37 (gate-as-interrupt, DecisionCard, verdict pathway, no-auto-approve, reject-rate KPI) | Slab 3 (interrupt pattern) / Slab 4 (party-mode-as-interrupt) | NO — deferred |
| `app/ledger/` | FR45, FR57, FR58; NFR-R4 idempotent ledger emission | Slab 4 | NO — deferred |
| `app/replay/` | FR49, FR50, FR51, FR52; NFR-X1 byte-for-byte replay | Slab 5 | NO — deferred |

**Result:** six packages justified at Slab 1 (pending MCP question); six packages deferred to their first-use slab. No empty-package-scaffolding at Slab 1 — each later slab scaffolds its own territory when code arrives.

**Readme-stub discipline:** every Slab-1 package directory carries a `README.md` stub naming its justifying FR and purpose. Packages deferred to later slabs have no Slab-1 presence at all.

### Slab 1 Package Scope (Confirmed)

```
app/
  runtime/        # FR1/FR3/FR4/FR7 — persistent LangGraph service + Postgres checkpointing
  models/         # FR17/FR21/FR23/FR25 — three-level cascade + selector + registry + adapter
  state/          # NFR-M3 unit + Pydantic v2 base classes
  manifest/       # FR8 — manifest-as-graph-config loader (Slab 1); FR39 compile-time CI (Slab 4)
  http/           # FR2 — FastAPI escape-hatch (127.0.0.1 only)
  mcp_server/     # FR2 — MCP primary bridge (PENDING operator question)
```

Plus siblings:
- `runtime/graphs/v42/` — frozen-graph sibling ready (Slab 5 populates)
- `_bmad/memory/bmad-agent-{name}/` — sanctum tree retained from primary repo (with CLONE-FORK-NOTICE, Amendment G)

### Test-Tier Scaffold at Slab 1 (Amendments C + D — Murat)

**Four-tier layout ships at Slab 1** with canary tests (not empty directories):

```
tests/
  unit/
  integration/
    scaffold_conformance/   # Amendment D — framework here from Slab 1, fixture specialist below
  end_to_end/
    test_harness_contract.py  # canary: asserts directory + README + naming convention
  trial_replay/
    test_harness_contract.py  # canary: pytest.skip("Slab 5 populates this directory — see NFR-M3")
    README.md                 # "Slab 5 populates this directory. Harness contract: NFR-M3 §4. Do not add tests here until Slab 5a."
  fixtures/
    specialists/
      fixture_minimal_specialist.py  # Amendment D — toy specialist the conformance framework parametrizes over
```

**Scaffold-conformance framework at Slab 1** (Murat strong opinion): build the harness before consumers exist, validate with fixture specialist. When real specialists land in Slab 2, framework picks them up via registry iteration — no framework changes needed. Same pattern as Pact contract-testing. Risk of deferring to Slab 2: ~70% probability ≥1 non-conformant specialist ships + FR14 trust erosion + Slab 2 balloons further (readiness Finding #3 already flagged oversized).

### First Implementation Stories — Slab 1 Story 1a/1b/1c (Amendment F — Amelia)

**Single-story (a) rejected** — steps 1–11 span three T1 reading sets; K ≈ 4.5–5× target fails `story-cycle-efficiency.md §K-floor`. Three-story split (b) passes K-floor on all three stories (1.3× / 1.4× / 1.6× K target). Strict serial; no parallelism (forward deps).

**Story 1a — "Runtime Substrate Environment + Dependencies"** (~0.5 dev-day; K ≈ 1.3× target)
```bash
uv venv .venv --python 3.12
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install langgraph langchain langchain-openai openai \
  langgraph-checkpoint-postgres "pydantic>=2" fastapi langsmith "psycopg[binary]"
uv pip freeze > requirements.lock
```
AC: lockfile committed; `uv run python -c "import langgraph; import langchain_openai; import pydantic; print('ok')"` succeeds.

**Story 1b — "Package Layout + Postgres + Sanctum Fork Notice"** (~1 dev-day; K ≈ 1.4× target)
```bash
# Six Slab-1 packages (per traceability table)
mkdir -p app/{runtime,models,state,manifest,http,mcp_server}
# Each with __init__.py + README.md stub naming justifying FR
# Frozen-graph sibling ready for Slab 5
mkdir -p runtime/graphs/v42
# Test-tier scaffold (all 4 dirs + canaries + fixtures per Amendment C)
mkdir -p tests/{unit,integration/scaffold_conformance,end_to_end,trial_replay,fixtures/specialists}
# Native local Postgres 15+ bootstrap (NO Docker — operator installs Postgres directly;
# Windows: EDB installer, macOS: Homebrew, Linux: distro package)
# Ship scripts/dev/init_postgres.sql (idempotent CREATE DATABASE + CREATE ROLE + GRANTs)
# and docs/dev-guide/local-postgres-setup.md (one-time operator bootstrap).
psql "$DATABASE_URL" -f scripts/dev/init_postgres.sql
psql "$DATABASE_URL" -c "SELECT version();"   # must report >= 15
# Sanctum fork discipline (Amendment G — Amelia)
# Write _bmad/memory/bmad-agent-{name}/CLONE-FORK-NOTICE.md per specialist:
#   "Sanctum authored in clone from <date>; primary sanctum frozen at commit <sha>;
#    backports stop after Slab 1 close per FR60."
```
AC: six Slab-1 packages present with READMEs; `scripts/dev/init_postgres.sql` + `docs/dev-guide/local-postgres-setup.md` authored and idempotent; `tests/integration/postgres/test_server_version.py` uses **`psycopg` (shipped dep from 1.1a lockfile) — NOT `psql`** and **skips cleanly** with a documented reason when `DATABASE_URL` is unset or unreachable (dev-agent sessions must never block on operator-side CLI availability — this is the general "verify via shipped deps, not operator CLIs" rule); canary tests green (`pytest tests/end_to_end/test_harness_contract.py tests/trial_replay/test_harness_contract.py`); CLONE-FORK-NOTICE.md exists per sanctum directory; `python -c "import app.runtime; import app.models; import app.state; import app.manifest; import app.http; import app.mcp_server"` succeeds (smoke-import shape-pin test lives in 1b AC, not a separate story). Operator-gated live `psql "$DATABASE_URL" -c "SELECT version();"` evidence is recorded once at story closure as Completion-Notes paste — it is **not** a dev-agent AC.

> 💬 Amelia concern flagged: Story 1b review exercises the psycopg-based `test_server_version.py` on the reviewer's box when Postgres is up; if Postgres is not installed on the reviewer's machine the test must skip (not error) per the "verify via shipped deps, not operator CLIs" rule. Live `psql` version smoke is operator-gated Completion-Notes evidence, not a reviewer-box gate. Flag as dual-gate candidate if Cora's block-mode hook trips.

**Story 1c — "Smoke Test + Runtime Server Entry"** (~1.5 dev-days; K ≈ 1.6× target)
```bash
uv run python -m app.models.registry_check     # model registry sanity
uv run python -m app.smoke_test                # stub graph end-to-end (full §01→§15 is M1 evidence across Slab 1, not Story 1c)
uv run python -m app.runtime_server            # persistent LangGraph + FastAPI + (MCP if Slab 1 scope)
```
AC: `registry_check` green; `smoke_test` entry-point runs stub graph; `runtime_server` boots and accepts a local connection.

**Out of Story 1 scope, distributed across Slab 1 Stories 2–N** (weeks 2–3 of Slab 1): full §01→§15 manifest-loaded smoke_test (M1 evidence), checkpoint retention + cleanup policy, LangSmith wiring + trace-per-node, model-selector cascade unit tests, `docs/dev-guide/langgraph-runtime-setup.md`, `docs/dev-guide/model-selection-guide.md`, `docs/dev-guide/langgraph-state-idioms.md` (Amendment E), LangGraph idiom sanity check throwaway (Amendment I).

### LangGraph State Idioms Doc (Amendment E — Paige)

**New Slab-1 deliverable:** `docs/dev-guide/langgraph-state-idioms.md` (six sections, diagrams/tables over prose, each with minimal working code example):

1. `TypedDict` vs `BaseModel` for graph state — decision table. PRD mandates Pydantic v2; document *how* to use BaseModel as graph state and tradeoffs (validation cost per hop vs. type safety). Most-important section because LangGraph docs push TypedDict and our mandate pushes the other way.
2. Reducer fields: `Annotated[list, operator.add]` — when needed, when not; `Field(default_factory=list)` interaction.
3. `Command(goto=..., update=...)` return types — shape, when to `goto` vs `update`, typing pattern.
4. `Send()` fan-out payloads — serialization requirement; Pydantic model rules.
5. `interrupt()` checkpoint payloads — serialization requirements; UUID4 + timezone-aware datetime discipline carries over.
6. `RetryPolicy` + Pydantic interaction — placeholder section until Slab 4 (Slab 4 deliverable per PRD); explicit "known-issue, Slab 4 deliverable" callout prevents silent gap.

**Companion references (not replacements):**
- One-paragraph cross-reference added to top of `docs/dev-guide/pydantic-v2-schema-checklist.md`: "If your schema is LangGraph graph state, ALSO read `langgraph-state-idioms.md` before T1."
- One-line pointer added to `docs/dev-guide/scaffolds/schema-story/README.md`.
- **No new scaffold folder** — existing four-file-lockstep scaffold survives unchanged; idioms overlay on top. Honors the PRD "inherit unchanged" commitment without pretending the idiom gap doesn't exist.

**Rationale for Slab 1 (not Slab 2):** if it ships with Slab 2, the first Slab 2 story produces it as emergent content *and* the drift it was meant to prevent. Doc-before-code discipline.

### LangGraph Idiom Sanity Check (Amendment I — Quinn-R)

Before Slab 1 closes, a throwaway `StateGraph` + `MemorySaver` mini-example runs against `app/runtime/` + `app/state/` abstractions. Not committed; lives in a reviewer's scratch dir during Slab-1 close. Purpose: verify our wrappers don't drift from LangGraph idiom in ways that will bite at Slab 3. Cost: half a dev-day. Value: cheap insurance against "reject-the-cage" accidentally rejecting the framework.

### Architectural Decisions Baked Into the Scaffold

- **Language + runtime:** Python 3.12+ with `uv` lock; `pyproject.toml` + `requirements.lock` as Slab-1 acceptance artifact.
- **Lane-respecting package layout:** `app/marcus/` and `app/cora/` siblings under `app/`, separated by import-linter contract. Six Slab-1 packages under `app/` (pending MCP question).
- **Frozen-graph-version sibling:** `runtime/graphs/v42/` stub ready at Slab 1; Slab 5 populates.
- **Four-tier test layout with canaries** + scaffold-conformance framework with fixture specialist, all at Slab 1.
- **Sanctum-fork discipline:** `_bmad/memory/bmad-agent-{name}/CLONE-FORK-NOTICE.md` per specialist at Story 1b AC. Codifies clone-authoritative Day 1; prevents primary/clone drift during migration window.
- **Lint / formatting:** `ruff` (inherited from primary).
- **Pre-commit → CI lockstep elevation:** Slab 4 elevates existing block-mode-trigger-path pattern to graph-compile-time CI hook.
- **Schema-shape scaffold:** `docs/dev-guide/scaffolds/schema-story/` inherited unchanged; new companion `docs/dev-guide/langgraph-state-idioms.md` added at Slab 1.

### Open Question Requiring Operator Input

> ❓ **Does the Slab-1 smoke test plan to exercise MCP, or only the FastAPI localhost entry?**
>
> - **If MCP is in Slab-1 smoke scope:** `app/mcp_server/` is Slab 1 (seventh Slab-1 package). Story 1c adds MCP bridge smoke alongside FastAPI smoke.
> - **If FastAPI-only at Slab 1:** `app/mcp_server/` defers to Slab 2. Slab 1 smoke exercises FastAPI localhost only; MCP bridge lands with first specialist migration.
>
> This determines the final Slab-1 package count (six or seven) and reshapes Story 1c AC. **Answer before Story 1b lands** (package directories are created there).

### Note

The architecture's first implementation story is **not** a `create-next-app` equivalent — it is the **in-clone scaffold grown as Slab 1 Stories 1a/1b/1c**, with six (possibly seven) packages, traceability table evidence, canary tests in all four test tiers, scaffold-conformance framework at Slab 1, CLONE-FORK-NOTICE sanctum-fork discipline Day 1, and `langgraph-state-idioms.md` companion doc as a Slab-1 deliverable.

## Core Architectural Decisions

### Decision D1 — Sanctum Snapshot Strategy: Hybrid (content-hash during run + trial-close snapshot)

**PRD Anchor:** NFR-X3 (sanctum snapshotted into checkpoint OR referenced by content hash); FR11 (cold-read discipline); FR50 (byte-for-byte replay); FR49 (fork-from-checkpoint); FR59 (sanctum invalidation hook); NFR-P3 (≤500ms Postgres write); NFR-X1 (byte-for-byte pack replay).

**Decision:** Option C Hybrid. Content-hash (SHA-256) referenced in every checkpoint during a run; one-time snapshot of all sanctum content touched during the trial, archived at trial close to `_bmad-output/trial-runs/<trial_id>/sanctum-snapshot/`. Live disk is canonical; snapshot is replay-only fallback with provenance logging.

**Rationale:** Only option that satisfies NFR-X1 byte-for-byte replay + NFR-X3 snapshot + FR59 invalidation hook + NFR-P3 write budget without compromise. Trial-close sanctum-snapshot doubles as the audit artifact the BMAD regime wants (FR63 invariant audit matrix benefits from per-trial sanctum archives). Cache-prefix stability (NFR-O4 + FR59) is directly verifiable via hash equality — C preserves this while keeping bulletproof reproducibility.

**Alternatives considered:**
- **Option A (inline bytes in checkpoint):** bulletproof reproducibility, simplest implementation, but checkpoint-size balloon (~12.5 MB sanctum-bytes per trial replicated into Postgres at 17 specialists × ~15 invocations × ~50KB avg), weak FR59 invalidation-hook fit, risks NFR-P3 (≤500ms Postgres write).
- **Option B (content-hash only):** small checkpoint, cache-prefix verifiable, but replay fails if operator deletes `_bmad/memory/bmad-agent-x/` (no fallback). B is Option C minus the safety net.

**Variance-on-replay policy:**
- **Clone-local replay:** warn-and-continue with provenance log when live-disk hash mismatches and snapshot fallback is used. Consistent with NFR-X5 temperature-variance discipline.
- **CI-enforced reproducibility tests:** fail-loud on any variance (no fallback). Trial-replay regression suite (FR51) runs in fail-loud mode. Prevents silent replay drift from masking real reproducibility regressions.

**Implementation locations:**
- `app/runtime/sanctum.py` — cold-read + fingerprint computation at every specialist invocation.
- `app/state/` — `SanctumFingerprint` Pydantic model; `NodeCheckpoint.sanctum_fingerprints: dict[str, SanctumFingerprint]`.
- `app/ledger/` — trial-close snapshot archival (Slab 4 or 5; hash infra must exist Slab 1).
- `app/replay/` — replay-time hash lookup with snapshot fallback (Slab 5).
- `app/runtime/sanctum_watcher.py` — FR59 invalidation hook; detects hash changes during live run; surfaces as warning (NFR-O3 non-fatal).

**Slab distribution:**
- **Slab 1:** Fingerprint model + cold-read integration + checkpoint-field inclusion. Enables reproducibility infrastructure from Day 1.
- **Slab 4:** Invalidation hook (surfaces warnings); trial-close snapshot archival.
- **Slab 5:** Replay-time snapshot fallback logic + CI fail-loud trial-replay regression suite.

**Open sub-decisions deferred to their slab:**
- Exact sanctum file enumeration for fingerprinting (INDEX.md + PERSONA.md + L5 references only? or all files in sanctum tree?). Slab 1 early-spike decides.
- Snapshot archive format (git-style objects? tarball? plain directory?). Slab 4 decides.
- CI fail-loud policy granularity (per-trial? per-specialist? per-file?). Slab 5 decides.

### Decision D6 — Manifest-as-Graph-Config Loader: Hybrid (topology declared, behavior in Python)

**PRD Anchor:** FR8 (manifest as compile-time topology source); FR38 (graph cannot compile without valid manifest); FR39 (Slab 4 CI drift detection); Novel Pattern #2 (manifest-as-graph-config); Substrate invariant #3 (manifest is the deterministic neck).

**Decision:** Option C Hybrid. Manifest declares topology; Python provides behavior. The manifest commits to: step IDs, handler dotted-name references, edge kinds (sequential / conditional_by_predicate / interrupt / send_fanout), gate positions + DecisionCard schema refs, block-mode-trigger-path lists, subgraph mount points, pack version, graph-version binding, state model reference. The manifest does NOT commit to: handler implementation, reducer logic, predicate code, retry policies.

**Rationale:** 
- Novel Pattern #2 promises "manifest-as-graph-config promotes Pipeline Lockstep to framework-level CI gate" — Option A (thin loader) too weak to deliver this; Option B (thick DSL) over-reaches.
- Substrate invariant #3 maps verbatim onto Option C: manifest is topology; runtime consumes, doesn't invent.
- Reject-the-LangChain-cage Rule 3 (schema-as-boundary-not-corset) fits Option C: manifest is boundary; Python interior stays free.
- FR38 architecturally enforced: `PipelineManifest` Pydantic model validates at load-time that every handler reference is importable; compiler fails fast on manifest errors before `StateGraph` is built.
- FR39 CI drift detection (Slab 4) is trivial: compare manifest handler names to Python handler inventory; verify block-mode-trigger-path coverage.
- FR40 lane separation: two manifests (one per lane) or one manifest with two top-level sections — resolve in D4. Recommend two files (`state/config/pipeline-manifest.yaml` for Marcus; `state/config/dev-graph-manifest.yaml` for Cora).

**Manifest schema (Slab 1):**
- `pack_version` + `pack_family` (inherited from primary repo's existing manifest).
- `runtime.graph_version` — FR43 frozen-graph-version linkage.
- `runtime.state_model` — dotted reference to Pydantic state class.
- `steps[]` — each with `id` (regex-validated), `handler` (dotted `module:callable`), `gate_after`, `block_mode_trigger_paths[]`, `edges[]`.
- `edges[]` per step — `kind` (enum), kind-specific fields (target for sequential; predicate + true_target + false_target for conditional_by_predicate; gate_id + decision_card_schema for interrupt; send payload shape for send_fanout).
- `subgraphs[]` — specialist mount points referenced by step handlers.
- All Pydantic models with `validate_assignment=True`, `extra="forbid"`, cross-field validators on edge-kind-specific fields, `model_validator(mode="after")` verifying every handler/predicate/state-model/subgraph reference is importable.

**Compiler (`app/manifest/compiler.py`, Slab 1):**
- Reads manifest Pydantic model.
- Iterates `steps[]` → `StateGraph.add_node(step.id, handler)`.
- Iterates edges → dispatches on `kind` to the appropriate LangGraph API (`add_edge`, `add_conditional_edges`, `interrupt()` wrapper, `Send()` fan-out).
- Returns `graph.compile(checkpointer=...)`.
- Two-lane support: `compile_run_graph(manifest)` for Marcus; `compile_dev_graph(manifest)` for Cora (both consume same `PipelineManifest` shape, different manifest files).
- Validation mode (no checkpointer): used by Slab 4 CI hook.

**Slab distribution:**
- **Slab 1:** `app/manifest/schema.py` (Pydantic manifest model) + `app/manifest/loader.py` (YAML → model) + `app/manifest/compiler.py` (model → compiled StateGraph). Empty-manifest-loaded-graph smoke test (M1 evidence) exercises this end-to-end.
- **Slab 3:** Marcus handlers registered and bound via manifest.
- **Slab 4:** CI drift hook (`scripts/check_manifest_lockstep.py`) + second manifest for Cora dev-graph.
- **Slab 5:** Manifest schema versioning discipline documented in migration guide §Frozen-graph ceremony.

**Schema governance (inherits Tier-1/2/3 from pack-version policy):**
- Tier-1 (patch): additive new optional field; dev-agent authority.
- Tier-2 (minor): new edge kind; new required field with sensible default; single-gate party-mode.
- Tier-3 (major): palette restructure; new top-level section; full party-mode + operator sign-off.

**Alternatives rejected:**
- **Option A (thin loader, YAML as data, Python as topology):** FR38 not architecturally enforced; FR39 drift detection is hard at Slab 4; Novel Pattern #2 "the manifest IS the pipeline" promise not delivered.
- **Option B (thick loader, manifest as DSL):** schema over-reach violates "schema-as-boundary-not-corset"; DSL becomes its own governance surface compounding Tier-1/2/3 complexity; dev onboarding becomes "learn the compiler's binding rules."

**Cascading implications:**
- **Handler-name registry:** Python handler inventory auto-discoverable via import (no hand-maintained catalog). Compile-time registry of `step.id → handler callable` computed by the compiler, not declared. Relates to D2 (model-cascade resolver placement at handler-entry).
- **DecisionCard schema refs at interrupt edges:** `app/models/decision_cards/` becomes a per-gate Pydantic family. Each `edge.decision_card_schema` is a dotted ref to a gate-specific DecisionCard class. Relates to D3 (HIL tamper-evidence).
- **Block-mode-trigger-path list per step:** Slab 4 CI hook compares diff against step.block_mode_trigger_paths and verifies lockstep updates. Existing `state/config/pipeline-manifest.yaml` block-mode-trigger-paths migrate into per-step `block_mode_trigger_paths[]` lists.
- **Cora dev-graph manifest:** separate file `state/config/dev-graph-manifest.yaml` (recommended). Final call resolves in D4 (graph-compile-time CI semantics).

### Decision D2 — Model-Cascade Code Location + Override Flow

**PRD Anchor:** FR17–FR25; NFR-M2; NFR-O4; readiness T1 #7 (model-registry mid-migration bump); readiness Finding #2 FR24 (cache-invalidation-warning closure).

**Four sub-decisions, all locked:**

**SQ1 (resolver location) → central `app/models/selector.py`.** Single resolution function = single LangSmith audit surface for FR22/NFR-O4 trail logging. Per-handler inline scatters cascade logic across 153+ handlers; middleware hides resolution (fights explicit-config principle). Handler pattern: `model, trail = resolve_model(node_id, state); client = adapter.for_model(model)`.

**SQ2 (override propagation) → state-embedded.** `RunState.model_overrides: dict[NodeId, ModelRef | None] = Field(default_factory=dict)`. Fork-from-checkpoint (FR49) inherits overrides naturally; NFR-X4 reproducibility preserved via Postgres checkpointing; replay reuses overrides. `None` clears override at the node. Config-threaded (loses overrides on replay) and `configurable`-thread-local (fragments state across two persistence paths) both rejected.

**SQ3 (FR24 cache-invalidation-warning timing) → both warnings.** (a) **Pre-submission warning** at override surface: operator sees "applying this override invalidates prompt cache for node X; estimated cost impact: +~50% on next invocation" before confirming — honors FR24 verbatim. (b) **Running cache-state in every DecisionCard** via `DecisionCardMeta.cache_state: Literal["healthy", "mixed", "cold"]` + `affected_nodes` + `override_trail` — operator always knows cache warmth. Pre-alone loses view after submission; post-alone fires too late to inform the decision.

**SQ4 (`model_config.yaml` location + compile-time lint) → per-specialist.** `app/specialists/{name}/model_config.yaml` + `app/marcus/model_config.yaml` + `app/cora/model_config.yaml`. NFR-M2 enforced at graph-compile: iterate every `model_config.yaml`; validate every ref against `app/models/registry.yaml`; validate `auto` cascade targets; fail graph compile on dangling reference. Matches FR14 scaffold-conformance (specialist carries own config; scaffold asserts presence + shape). Central `assignments.yaml` would weaken per-specialist autonomy; hybrid with auto-generated audit-summary deferred to Slab 5 polish.

**Model registry governance (closes readiness T1 #7):** `app/models/registry.yaml` single source of truth. Tier-1 (new model appended, no default changes) = dev-agent authority, any slab; milestone evidence includes a "registry version" line at slab close. Tier-2 (default tier changes) = single-gate party-mode. Tier-3 (palette/policy restructure) = full party-mode + operator sign-off. Mirrors pack-version Tier-1/2/3 policy. Documentation lands in `docs/dev-guide/model-selection-guide.md` (Slab 1 deliverable).

**Auto-select policy:** `app/models/selection_policy.yaml` ships Slab 1. Initial policy per PRD §Specialists tier palette: reasoning → `o3-mini`; long-context → `gpt-4.1`; fast → `gpt-4.1-mini`; boundary → `gpt-4.1-nano` or `gpt-4o-mini`; multimodal → `gpt-4o`. Deterministic — no LLM call (FR21).

**LangSmith span contract (NFR-O4):** every `resolve_model` call emits a span with tag set `{agent, node_id, node_role, resolution_level, chosen_model, policy_hit}`. Defined Slab 1 so downstream slabs' traces conform.

**Cache-state tracking:** `app/state/cache_state.py` at Slab 1. Per-node hash-based tracking reuses D1's sanctum-fingerprint hash infrastructure (unified hashing approach; not two separate hash machineries).

**Slab distribution:**
- **Slab 1:** `selector.py`, `adapter.py`, `registry.yaml`, `selection_policy.yaml`, `registry_check` entry-point (Story 1c AC per Amendment F), `CacheState` model, per-specialist `model_config.yaml` schema Pydantic model, NFR-M2 compile-time lint.
- **Slab 2:** specialist scaffold integrates `resolve_model` call at each LLM-invoking node; conformance test asserts `model_config.yaml` presence + validity.
- **Slab 3:** DecisionCard meta cache-state surface (ships with Marcus gates).
- **Slab 5:** optional auto-generated `assignments-summary.yaml` for audit.

**Forward-port convergence (PR-R):** PR-R's structured dispatch telemetry unifies with LangSmith resolution-trail span contract. No schema change here; migration-guide §8 notes convergence.

### Decision D3 — HIL Invariant Tamper-Evidence (FR34 closure)

**PRD anchor:** FR31–FR37; Decision 4 (HIL + SPOT preserved indefinitely); Substrate invariant #4 (HIL-paused gates); Readiness Finding #2 (FR34 critical — no milestone evidence today; FR36, FR37, FR42, FR53, FR24, FR27 also gap-closed here).

**Problem:** A future sprint under pressure could add a "1-hour no-response auto-reject" or "default-verdict on timeout" and **invisibly violate** the load-bearing HIL property. "Operator verdict is the sole path past a gate" must become **architecturally unavailable** to bypass, not merely conventionally avoided.

**Mechanism — "Verdict comes only from a signed `OperatorVerdict` payload; no other code path can resume a gate":**

1. **`OperatorVerdict` Pydantic model** (`app/gates/verdict.py`, Slab 1). Frozen-after-construction. Fields: `trial_id`, `gate_id`, `verb: Literal["approve", "edit", "reject"]`, `operator_id`, `timestamp` (timezone-aware), `decision_card_digest` (SHA-256 of the card that elicited the verdict — binds verdict to card), `edit_payload` (optional; present only when `verb == "edit"`). `validate_assignment=True`, `extra="forbid"`.

2. **Sole resume authority: `app/gates/resume_api.py`.** Public function `resume_from_verdict(verdict: OperatorVerdict) -> CompiledGraphHandle` is the **only code path in the entire `app/` tree** that calls LangGraph's `graph.invoke(Command(resume=...))` at a gate node. Import-linter contract restricts callers to three authorized transports: `app.mcp_server.tools.gate_decide`, `app.http.gate_endpoint`, `app.marcus.cli.gate_cli`.

3. **Three authorized verdict-submission transports populate `operator_id`.** MCP tool `gate.decide`, FastAPI `POST /gate/verdict`, CLI `app.marcus.cli gate decide`. No other code path can populate `operator_id`. Enforcement: scaffold-conformance test `tests/integration/gate_verdict_authority_test.py` greps the codebase for any construction of `OperatorVerdict` outside the three authorized call sites and fails at graph-compile.

4. **No timer / no scheduler can resume a gate.** Ruff custom check or import-linter rejects imports of `asyncio.sleep`, `threading.Timer`, `apscheduler`, `schedule` inside `app/gates/**`. Scheduler-capable dependencies not in Slab 1 lockfile. Any future slab adding one trips a graph-compile-time check that asserts `app.gates.*` doesn't import it.

5. **Digest-match enforcement.** Gate node verifies `verdict.decision_card_digest` matches the card it emitted. Synthetic verdict (replay-attack-style, card never seen) fails the digest check; gate refuses to resume.

6. **Reject-rate KPI (FR37) instrumented by construction.** Every `OperatorVerdict` emits a ledger event (`app/ledger/`, Slab 4). Dedicated query `reject_rate_per_gate(trial_id)`. Not deferrable.

7. **Gate-count audit (FR36).** Every `interrupt()` emits a ledger event with `gate_id` + `trial_id`. Trial close computes `gate_inventory = [events where kind == "interrupt"]` and asserts equality with the manifest's declared gate set for that trial's pack. Mismatch fails trial-close.

**Idle-gate policy (operator-story branch): Option (i) — do nothing.** Trial stays paused indefinitely. Operator returns whenever; card intact; verdict emits; trial resumes. Pure FR34 fidelity. Notifications / pings are explicitly Growth-phase (post-M5). No timer surface added in MVP.

**Milestone evidence bullets added (close readiness Finding #2):**

- **M3 added:** "DecisionCard acceptance test: trial run confirms every gate's resume is driven by an `OperatorVerdict` with valid `operator_id` + `decision_card_digest`; import-linter contract verified; a staged attempt to resume via `asyncio.sleep` + direct `Command(resume=...)` call is rejected at graph-compile (FR34 + substrate invariant #4)."
- **M3 added:** "Trial run under `production` preset confirms Plan-and-Execute; trial run under `explore` preset confirms ReAct (FR27)."
- **M3 added:** "Runtime model-override surface functional AND warns operator of cache-invalidation impact before applying (FR24)."
- **M4 added:** "At least one bmad-code-review gate cites a LangSmith trace link as evidence (FR42)."
- **M5 added:** "Gate-inventory audit across new tracked trial run equals manifest's declared gate set 1:1 (FR36)."
- **M5 added:** "Reject-rate KPI reported per gate alongside cache hit rate + token cost (FR37)."
- **M5 added:** "MCP `state.inspect` tool usable by operator; read-only verified (FR53)."

**Slab distribution:**
- **Slab 1:** `OperatorVerdict` model, `resume_api` module stub, import-linter contract, ledger verdict-event shape.
- **Slab 3:** all gate `interrupt()` nodes wired through `resume_api`; DecisionCard digest computation; three authorized transports populate `operator_id`.
- **Slab 4:** ledger-based reject-rate query; gate-inventory audit at trial close; graph-compile-time scheduler-import rejection.
- **Slab 5:** M5 evidence bullets verified in head-to-head parity trial run.

### Decision D4 — Graph-Compile-Time CI Semantics (FR38/FR39)

**PRD anchor:** FR38 (manifest required for compile); FR39 (CI rejects drifted PR at graph-compile); Novel Pattern #2; PR-R L1 validator convergence.

**Decision:** Two manifests (one per lane, separate files — `state/config/pipeline-manifest.yaml` for Marcus + `state/config/dev-graph-manifest.yaml` for Cora). The D6 compiler runs in **validation mode** (no checkpointer) and is callable as a library function. A CI hook `scripts/check_manifest_lockstep.py` imports the compiler + the PR-R `check_dispatch_registry_lockstep.py` validator (forward-ported at M5) as library functions — not subprocesses — and runs both against the PR diff. Drift surfaces as `ImportError` (missing handler) or `ValidationError` (manifest shape violation) or `LockstepError` (block-mode-trigger-path touched without companion update). GitHub Actions job runs this on every PR; fail = merge blocked. No new CI framework; reuses existing primary-repo CI shape.

**Rationale:** FR38 architectural ("graph won't compile without valid manifest") + FR39 architectural ("drift = compile error"). Lane separation enforced by file boundary. PR-R's L1 validator becomes the single source of truth for dispatch-registry drift — consumed in-process to avoid duplicate logic.

**Slab 4 deliverable.** Validation-mode compiler exists at Slab 1 as part of D6; CI wiring lands Slab 4.

### Decision D5 — Sanctum Cold-Read Contract + Invalidation Hook

**PRD anchor:** FR11; FR30; NFR-I6; FR59; NFR-P4 (≤200ms sanctum cold-read).

**Decision:** Atomic multi-file read via `pathlib` glob into a `SanctumContent` Pydantic model. Fingerprint (D1 shared infrastructure) computed over the exact file set read — Slab 1 early spike picks the enumeration. Default enumeration: `INDEX.md`, `PERSONA.md`, `access-boundaries.md`, `chronology.md`, plus any `L5-*.md` / `L6-*.md` references declared in `INDEX.md`.

**Invalidation hook (FR59):** `watchdog` library watches `_bmad/memory/` at runtime-server startup. File-change events publish to an async queue; running trials subscribe. When a running trial detects that a sanctum it's already used has mutated mid-trial, it surfaces an NFR-O3 warning (non-fatal) to the operator via the next DecisionCard's meta section + ledger event (Slab 4 ledger).

**Rejected:** git-hook approach (too indirect — doesn't detect uncommitted mutations); periodic digest (too slow — runtime-only check breaks detection latency). File-watcher + hash-on-read combo gives detection latency ≤200ms per NFR-P4.

**Slab distribution:** Slab 1 cold-read + fingerprint + `SanctumContent` model; Slab 5 invalidation hook (file-watcher + DecisionCard-meta surface + ledger event); Slab 4 ledger event schema.

### Decision D7 — Operator-Surface Contract (§Developer-tool-UX)

**PRD anchor:** Readiness T1 #6; FR33 (verdict via CLI / MCP / FastAPI); FR53 (state.inspect read-only); §API Surface.

**Decision:** Three-transport verdict parity. All three transports accept an identical `OperatorVerdict` Pydantic payload (D3); all three return identical graph-resumption semantics; all three pass through the single `resume_api` (D3).

**MCP tool surface (Slab 1 contract, Slab 3 DecisionCard shape):**
- `trial_run.start(bundle_path, preset)` → `{trial_id, thread_ref}`
- `trial_run.resume(trial_id)` → `{gate_id | null, decision_card | null}`
- `trial_run.fork(trial_id, from_checkpoint)` → `{forked_trial_id, thread_ref}`
- `trial_run.replay(trial_id)` → `{replay_trial_id, variance_report}`
- `specialist.invoke(name, envelope)` → `{return_payload}`
- `gate.decide(verdict: OperatorVerdict)` → `{resume_result}`
- `state.inspect(trial_id, checkpoint_id)` → `{state_read_only}` (no mutation)
- `model.override(trial_id, node_id, model_ref)` → `{cache_invalidation_warning, confirm_token}`

**FastAPI endpoints (1:1 mirror, localhost-only per NFR-S2):**
- `POST /trial/start` | `POST /trial/{id}/resume` | `POST /trial/{id}/fork` | `POST /trial/{id}/replay`
- `POST /specialist/{name}/invoke`
- `POST /gate/verdict` | `GET /gate/{trial_id}/current`
- `GET /state/{trial_id}/{checkpoint_id}` (read-only HTTP verb enforces FR53)
- `POST /model/override`

**CLI subcommands (1:1 mirror, Slab 3):** `app.marcus.cli trial start|resume|fork|replay`, `... gate decide|current`, `... state inspect`, `... model override`.

**DecisionCard schema family:** lives at `app/models/decision_cards/{gate_id}.py`; each gate has its own Pydantic `DecisionCard` model whose dotted reference is declared in the manifest's `edge.decision_card_schema` field (D6). Base `DecisionCard` class in `app/models/decision_cards/base.py` carries `meta: DecisionCardMeta` (cache-state per D2; override-trail; reject-rate context).

**Transport parity contract test:** same `OperatorVerdict` payload submitted through all three transports must produce identical graph-resumption state. Test lives in `tests/integration/transport_parity_test.py` (Slab 3).

### Decision D8 — Frozen-Graph-Version Layout + Bump Ceremony

**PRD anchor:** FR43, FR44; Novel Pattern #4 (runtime-as-immutable-artifact); frozen-at-ship pack discipline.

**Decision:** `runtime/graphs/v42/` directory contains:
- `manifest-snapshot.yaml` (copy of `pipeline-manifest.yaml` at ship time)
- `dev-graph-manifest-snapshot.yaml` (copy of Cora manifest at ship time)
- `pack-version.txt` (pack version this graph version binds to, e.g., `v4.2`)
- `dispatch-registry-snapshot.yaml` (post-PR-R forward-port; snapshot of dispatch-registry at ship time)
- `compiled-graph-digest.txt` (SHA-256 of compiled `StateGraph` introspection at ship time — byte-for-byte verification target)
- `README.md` (one paragraph: "This directory is the frozen graph v42. Do not edit. See `docs/dev-guide/frozen-graph-version-ceremony.md`.")

**Tier-1/2/3 bump policy** (mirrors pack-version policy):
- **Tier-1 patch** (prose / connective tissue / docstring edit touching no topology or dispatch shape): dev-agent authority; no version bump; v42 stays.
- **Tier-2 minor** (new step / new edge kind / new gate position / new dispatch edge): single-gate party-mode; bump v42 → v42.1; v42 stays frozen on disk.
- **Tier-3 major** (palette restructure / new pack family / manifest-schema top-level section): full party-mode + operator sign-off; bump v42 → v43; both versions on disk for audit.

**Ceremony doc:** `docs/dev-guide/frozen-graph-version-ceremony.md` (Slab 4 deliverable).

**Slab distribution:** Slab 1 creates `runtime/graphs/v42/` stub (empty at Slab 1; filled at Slab 5 ship); Slab 4 ships ceremony doc; Slab 5 first ship populates v42.

### Decision D12 — Cross-Slab Governance Artifact Ownership

**PRD anchor:** Readiness Finding #5; FR63 (15-invariant audit matrix); FR64 (anti-patterns catalog ≥5); FR65 (migration guide 11 sections); NFR-M6 (living catalog); NFR-M7 (guide kept current).

**Decision:** Not its own epic. A **protocol applied at every Slab-closing story.** Closing-story AC includes three mandatory lines:

1. **Invariant-preservation note.** For each load-bearing invariant (15 total) this slab touched, provide a one-line entry: "Invariant `<N>` preserved at `<file>:<line>` + verified by `<test>`." Feeds FR63 audit matrix incrementally. M5 rolls up into the full matrix.

2. **Anti-pattern harvest.** If this slab encountered an anti-pattern worth naming, add an entry to `docs/dev-guide/specialist-anti-patterns.md` with: anti-pattern name + example + counter-pattern + slab-of-discovery. Empty entries acceptable at Slabs 1 / 3 / 4; minimum ≥5 concrete by M5 (FR64).

3. **Migration-guide-section update.** Name which sections of `docs/dev-guide/langgraph-migration-guide.md` this slab revised. Placeholder sections ship at Slab 1 (11-section skeleton); each slab fills its owned sections; M5 ships the complete guide (FR65).

**Enforcement:** `bmad-code-review` gate checklist at every Slab close verifies the three AC lines. Missing = MUST-FIX. Adds one review item per slab-closing story.

**Slab distribution:** Slab 1 ships migration-guide skeleton (11 sections, placeholder content) + empty anti-patterns catalog. Slabs 2–5 fill per-protocol. Slab 5 rolls up the invariant audit matrix from slab-by-slab entries.

### Decision D9 — Milestone Evidence Gaps Closure (Readiness Finding #2)

Seven FRs flagged by readiness without named milestone evidence; all seven closed via D2 + D3 amendments already captured:

- **FR24** cache-invalidation warning → closed in D2 (pre-submission warning + DecisionCard meta surface). M3 evidence bullet added.
- **FR27** Plan-and-Execute / ReAct preset switching → closed in D3. M3 evidence bullet added.
- **FR34** HIL no-auto-approve → closed in D3. M3 evidence bullet added (load-bearing).
- **FR36** gate-count 1:1 audit → closed in D3. M5 evidence bullet added.
- **FR37** reject-rate KPI → closed in D3. M5 evidence bullet added.
- **FR42** code-review consumes traces → closed in D3. M4 evidence bullet added.
- **FR53** `state.inspect` read-only → closed in D7. M5 evidence bullet added.

**No separate architecture action.** The seven evidence bullets land in PRD §M1–M5 Required Evidence via the Step 7 validation pass (PRD amendment-of-record).

### Decision D10 — Slab 2 Sizing (Readiness Finding #3)

Split Slab 2 into three sub-slabs, informed by PR-R forward-port:

- **Slab 2a — Scaffold pilot on PR-R-conformant edges.** 3 specialists already Pydantic-pinned by PR-R (Irene Pass 2, Kira motion, Texas) migrate to the 9-node scaffold. Dispatch contract already known; only scaffold-wrapping + sanctum cold-read + `model_config.yaml` is new. ~1 week. Low risk. Validates the scaffold + `bmad-create-specialist` generator against known-good contracts.

- **Slab 2b — 14-specialist tranche.** Remaining 14 specialists (Gary, Vera, Quinn-R, plus 11 others from the current roster). Each needs PR-R-style dispatch contract retrofitted AND 9-node scaffold migration — two transformations stacked. ~3–4 weeks. Higher risk; parallelizable across dev-agents where specialists are independent. Anti-patterns catalog primary harvest lives here (per D12 protocol).

- **Slab 2c — Wondercraft pilot + scaffold-generator validation.** `bmad-create-specialist --name wondercraft` generates a new specialist from scratch; Wondercraft pilot produces real podcast artifact against live API; <1-dev-day claim validated. ~1 week. Validates FR13 (generator) + plug-and-play innovation claim.

**Each sub-slab becomes an epic at `bmad-create-epics-and-stories` time.** M2 acceptance closes at Slab 2c completion. **Total Slab 2 wall-clock: ~5–6 weeks** (within the 4–6 week PRD elastic range).

### Decision D11 — Slab 5 Split (Readiness Finding #4)

Split Slab 5 into two sub-slabs with distinct risk profiles:

- **Slab 5a — Acceptance (M5 go/no-go).** Trial-replay regression suite (FR51) + head-to-head parity trial run (FR52) + cost-projection measurement (FR55/FR56 ≥50% reduction bar) + 15-invariant audit matrix roll-up (FR63) + sanctum invalidation hook (FR59). ~1–1.5 weeks. Non-cuttable. M5 ship/iterate/rollback verdict anchors here.

- **Slab 5b — Polish.** Fork UX beyond CLI (IDE-integrated if time permits, PRD growth otherwise) + economics dashboard beyond CLI dump + migration guide §1–11 final pass (if not already complete per D12 protocol) + scaffold-generator polish from Slab 2c feedback. ~0.5–1 week. **Cuttable under pressure** per PRD MVP table. Ship decision at M5 uses 5a evidence; 5b may close after M5 without delaying ship.

**Each sub-slab becomes an epic at epic-authoring time.** M5 ship verdict gates on 5a only; 5b completion is a follow-up milestone.

### Decision D19 — Marcus-Writer Partition Principle (W5)

Authored 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2. Codifies the W5 partition principle that emerged during Slab 7c orchestrational tail authoring (W5 amendment to slab-7c PRD). Currently scattered across composition spec + import-linter contract comments; this entry promotes it to architecture-of-record.

**Decision:** Marcus is the SOLE author of envelope contributions. Specialists are pure functions returning `SpecialistReturn` payloads; Marcus's orchestrator owns aggregation + emission. The `production_runner.py` is the SOLE graph-execution authority. This three-way partition (specialist = pure function; Marcus = sole writer; runner = sole executor) is structurally enforced via:
- M1 import-linter contract: only `app.marcus.orchestrator.write_api` may import `app.models.state.run_state` (single-writer rule per R1 amendment 13 / Quinn)
- D3 HIL tamper-evidence (only authorized verdict-bridge modules import `app.gates.resume_api`)
- C6 `independence` contract (§section packages may not import each other; cross-§ shared content extracted to `app.gates._common`)

**Why this decision now:** Slab 7c shipped 14 §section packages each carrying a `poll_surface.py`. The §02A LLM composer pivot (7c.3a) demonstrated that §section bodies must NOT side-effect the run_state; they emit DECISIONCARD payloads, Marcus aggregates, runner persists. Without W5 codified at architecture tier, future §section authors will be tempted to duplicate write surfaces.

**Cross-references:** ADR 0001 parity-DSL; ADR 0002 eight-family gate taxonomy; M1+M3+M4 import-linter contracts; W5 amendment in `prd-slab-7c-orchestrational-tail.md`.

### Decision D18 — Eight-Family Gate Taxonomy LOCK (ADR 0002)

Authored 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2. Promotes ADR 0002 to a binding architectural decision. The eight-family taxonomy (G0/G1/G2/G2A/G2C/G3/G4/G5/G6) ratified during Slab 7c is now load-bearing for §section package layout.

**Decision:** Gate codes are partitioned into 8 family contracts; alias gates inherit family semantics via `alias_of` clause. The C6 import-linter `independence` contract enumerates the §section list; this enumeration is itself a load-bearing artifact (changes require party-mode + ADR 0002 amendment). Runtime gate IDs (currently 18) are validated against the eight-family taxonomy at compile time. `production_gate_ids(manifest)` derives the runner-pause set from manifest fold-flag metadata (currently {G1, G2C, G3, G4}; 4 of 18).

**Authoritative reference:** [`docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md`](../../docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md). D18 binds ADR 0002 to architecture-of-record currency.

### Decision D17 — Crosswalk-vs-Disk Parity Test Pattern (Murat AM-2 from post-S4)

Authored 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2. Generalizes the test pattern Murat introduced at S4 post-review when 2/6 v5 Crosswalk paths were stale.

**Decision:** Every governance map that declares disk paths (production-prompt-pack TL;DR Crosswalk; pipeline-manifest dispatch registry; coverage-manifest module_path entries; sources-of-truth.md SSOT pointers) MUST have a parity test at `tests/parity/` that:
1. Parses the governance map (markdown table OR YAML)
2. Extracts every path-string token
3. Asserts each resolves to an existing file or directory on disk
4. Excludes explicit deferred-placeholder markers per documented exclusion glob

**First instance:** `tests/parity/test_v5_crosswalk_paths_exist.py` (S4 post-review; v5 pack). **Pattern propagation:** when authoring a new governance map, file an adjacent parity test before declaring the map canonical. Filed in deferred-inventory `s5-followup-parity-test-pattern-propagation` for cross-map adoption.

### Decision D16 — v5 Canonical Prompt-Pack Discipline + Tier-1/2/3 Versioning

Authored 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2. Codifies the v5-canonical / v4.2-frozen-legacy disposition + Tier-1/2/3 versioning posture established at S4.

**Decision:** Production prompt packs follow the legacy-frozen-anchor pattern when superseded:
- New canonical version (e.g., v5) supersedes prior (v4.2 / v4.3)
- Prior canonical preserved on disk as legacy-frozen authority for the mapping checklist axis (audit reference)
- New canonical adopts Tier-1/2/3 versioning posture: Tier-1 = prose/connective tissue (dev-agent authority); Tier-2 = new pipeline step (party-mode); Tier-3 = new pack family (full party-mode + operator sign-off)
- Frozen-at-ship discipline: once a canonical pack ships + first tracked trial completes, structural edits bump version; the frozen prior-version stays on disk for audit

**First instance:** v5 supersedes v4.2 (legacy-frozen) and v4.3 (fully superseded; cluster-mode already absorbed into v4.2/v5). v4.2 retained as mapping-checklist legacy-axis anchor.

**Cross-references:** Sources-of-truth.md "Production prompt pack (canonical for production runs)" row; v5 frontmatter `versioning-posture` block; Pipeline Manifest Regime §Pack Versioning Policy.

### Decision D15 — Trial-Run Methodology Standing Operations

Authored 2026-05-07 at pre-Trial-3 cleanup S5 Tier-2. Promotes the S3 trial-run methodology to architecture-of-record.

**Decision:** Production trial runs follow the cadence + verdict framing + filing-disposition rules at [`docs/trials/methodology.md`](../../docs/trials/methodology.md). Every operator-launched full-pipeline run is a **tracked trial** producing the per-run trio (`launch.md` + `log.md` + `postmortem.md`) under `docs/trials/trial-N/`. Verdict framing: PASS / PARTIAL-PASS / STRUCTURED-STOP / FAIL. Filing-disposition: 4-question routing (anti-pattern? deferred? architecture? cross-trial?) — first YES wins; Routing Summary hygiene check at postmortem close.

**Cross-references:** `docs/trials/methodology.md`; `docs/trials/cross-trial-learnings.md`; `docs/trials/trial-N-templates/`. CLAUDE.md amendment proposed at S5 P1-32 codifies the routing rules at governance tier.

**Why D15 not D14:** D14 was used at S2 for Marcus namespace single-package discipline. S3-S6 cleanup arc decisions occupy D15+.

### Decision D14 — Marcus Namespace Single-Package Discipline (pre-Trial-3 Cleanup S2)

Authored 2026-05-07 at pre-Trial-3 cleanup S2 close. Closes deferred-inventory entry
`migration-tech-debt-app-marcus-stub-disposition` (filed 2026-04-26; reality-corrected
direction adopted at S2: legacy `marcus/` retired; canonical `app.marcus.*`).

**Decision:** the Marcus namespace lives at `app.marcus.*`. The legacy top-level `marcus/`
package — preserved as Slab-1-era migration shim — has been DELETED. Future code MUST
NOT introduce `from marcus.X` or `import marcus` references. Enforced structurally via
import-linter contract M5 (`forbidden`; `source_modules=["app"]`, `forbidden_modules=["marcus"]`).

**Story 30-1 internal duality preserved.** The Marcus-Intake / Marcus-Orchestrator
sub-package separation (R1 amendment 13 / Quinn single-writer rule) and the Maya-as-one-voice
facade (R1 amendment 17) are PRESERVED VERBATIM under the new home:
- `app.marcus.intake/` — Marcus-Intake (steps 01-04 + 4A pre-packet construction)
- `app.marcus.orchestrator/` — Marcus-Orchestrator (single-writer write API + 4A loop +
  fan-out + `NEGOTIATOR_SEAM` for 30-3a)
- `app.marcus.facade.py` — single Maya-facing voice surface
- `app.marcus.lesson_plan/` — Lesson Plan log subsystem (31-2's writer-identity discipline)
- `app.marcus.dispatch/` — dispatch contract types

**30-1 token preservation (R1 amendments 12+13+17 binding):**
- `ORCHESTRATOR_MODULE_IDENTITY = "marcus-orchestrator"` (WriterIdentity Literal value)
- `INTAKE_MODULE_IDENTITY = "marcus-intake"` (WriterIdentity Literal value)
- `NEGOTIATOR_SEAM` token `"marcus-negotiator"` (grep-discoverable sentinel)
- `MARCUS_IDENTITY = "marcus"` (programming-token; lowercase tripwire)
- `MARCUS_DISPLAY_NAME = "Marcus"` (Maya-facing render constant)

These string tokens are PRESERVED VERBATIM (not renamed to `app-marcus-*`) because they
are 31-2's WriterIdentity Literal values and Golden-Trace fixture content. Changing them
would break the single-writer log contract; the package home moved but the identity
strings stay.

**Why this decision now (not at original 30-1 ratification):** 30-1 created the duality
deliberately for Lesson Planner Epic 30. Post-brownfield-completion (Slab 7c close
2026-05-07), operator reclassified the legacy `marcus/` ↔ `app/marcus/` duality as a
bug class with production-run risk: dual-namespace ambiguity surfaces unexpected behaviors
when callers reach for one path or the other. D14 closes that duality. The 30-1 INTERNAL
duality (intake ↔ orchestrator) remains because it serves a different purpose — single-writer
discipline within one namespace, not two parallel namespaces.

**Verification:** `pytest tests/test_marcus_facade_leak_detector.py
tests/contracts/test_no_intake_orchestrator_leak_marcus_duality.py
tests/test_marcus_duality_imports.py tests/test_marcus_golden_trace_regression.py` —
17/17 GREEN at S2 close commit `195be7c` (post-Phase-7).

**Future modifications:** any future code introducing dual-namespace patterns (e.g.,
parallel `app.marcus_v2/` shim) requires party-mode ratification per the same governance
applied at S2 close. The M5 import-linter contract is the structural backstop.

### Decision D13 — Model-Registry Mid-Migration Bump Procedure (Readiness T1 #7)

Documented at `app/models/` Slab 1 deliverable + `docs/dev-guide/model-selection-guide.md` §Mid-Migration Bump:

- **Tier-1 patch** (new model appended; no default changes): dev-agent authority in any active slab. Registry-version line included in the current slab closing-story AC. Any specialist with `auto` cascade may newly resolve to the added model per policy; no forced migration.
- **Tier-2 minor** (default tier changes — e.g., reasoning tier moves from `o3-mini` to successor, or `gpt-4.1` → `gpt-4.5`): single-gate party-mode. Separate story opened in the active slab; must not derail slab scope. `model_config.yaml` files audited for specialists pinning the old default.
- **Tier-3 major** (palette restructure; new OpenAI model family; auto-select policy rewrite): full party-mode + operator sign-off. May pause the active slab if operator judges the bump is mission-critical (e.g., old model deprecated by OpenAI). Expected frequency: 0–1 times during the 12–16 week migration.

**Who owns the bump:** any active slab's dev-agent for Tier-1; the slab's spec-author for Tier-2 (story); operator + party-mode for Tier-3. Registry file (`app/models/registry.yaml`) is versioned; bumps are commits with a governance tag.

## Implementation Patterns & Consistency Rules

Scope: AI-agent conflict prevention across 153+ handlers × 17 specialists × 5 slabs × 12–16 weeks. Patterns below are load-bearing; every slab-closing bmad-code-review gate enforces them.

### 1. Naming Patterns

**Python package / module (all lowercase, snake_case):**
- `app/marcus/handlers/step_06b_gary_dispatch.py` — step handler naming matches manifest `step.id` with dashes→underscores and `_handler` suffix omitted.
- `app/specialists/{name}/graph.py` | `state.py` | `expertise/` | `sanctum/` (symlink) | `model_config.yaml` — fixed shape per FR13 scaffold.
- `app/gates/{gate_id}.py` and `app/models/decision_cards/{gate_id}.py` — gate_id matches manifest (e.g., `g2c.py`, `g4.py`).
- `app/models/state/{run_state.py|story_state.py|specialist_envelope.py|specialist_return.py}` — state base classes per FR7/NFR-M3.

**Pydantic models (PascalCase, no prefix):** `RunState`, `SpecialistEnvelope`, `SpecialistReturn`, `DecisionCard`, `OperatorVerdict`, `SanctumFingerprint`, `PipelineManifest`, `ModelRef`, `CacheState`. No `Model`/`Schema` suffix — Pydantic class IS the model.

**JSON-schema files:** `{pydantic_snake_name}.schema.json` co-located with the model module (per four-file-lockstep). Example: `run_state.py` → `run_state.schema.json`.

**Test files:** `tests/{tier}/{concern}/test_{subject}.py`. `tier ∈ {unit, integration, end_to_end, trial_replay}`. Subject matches the module under test (e.g., `tests/unit/models/test_run_state.py`). Tests are **never** co-located with source; always in `tests/` tree.

**Fixture files:** `tests/fixtures/{category}/fixture_{name}.py` — `fixture_*` prefix (not `test_*`) ensures pytest doesn't auto-collect per M-AM-4 precedent from Story 31-3.

**Manifest IDs (regex-enforced):**
- Step IDs: `^step-\d{2}[a-z]?(-[a-z-]+)?$` (matches existing primary `step-01-pre-flight`, `step-06b-gary-dispatch` shape).
- Gate IDs: `^g\d+[a-z]?$` (matches existing `g1`, `g2c`, `g3`, `g4`).
- Handler refs: `^[\w.]+:\w+$` (`module.path:callable`).
- Specialist names: `^[a-z][a-z0-9_]*$` (lowercase, underscores).

### 2. Structural Patterns

**Package boundary enforcement via `import-linter`** (`pyproject.toml::[tool.importlinter]`):
- `app.marcus` ⊥ `app.cora` — no imports either direction (D6 + D4 lane separation).
- `app.gates.resume_api` callable only from `app.mcp_server.tools.gate_decide`, `app.http.gate_endpoint`, `app.marcus.cli.gate_cli` (D3 HIL tamper-evidence).
- `app.gates.**` forbids imports of `asyncio.sleep`, `threading.Timer`, `apscheduler.*`, `schedule.*`.
- `app.specialists.*` forbids imports from `app.marcus.*` or `app.cora.*` (specialists don't know their lane).

**Four-file-lockstep locations (every Pydantic-v2 schema-shape change):**
1. Pydantic model: `app/models/{domain}/{name}.py`
2. JSON schema emission: `app/models/{domain}/{name}.schema.json`
3. Shape-pin test: `tests/unit/models/{domain}/test_{name}_shape.py`
4. Golden fixture: `tests/fixtures/models/{domain}/golden_{name}.json`

All four land in the same PR; violation = bmad-code-review MUST-FIX (inherited from primary repo discipline; see `docs/dev-guide/pydantic-v2-schema-checklist.md`).

**Config / manifest locations:**
- `state/config/pipeline-manifest.yaml` (Marcus run-graph topology; existing file extended per D6)
- `state/config/dev-graph-manifest.yaml` (Cora dev-graph topology; new at Slab 4)
- `state/config/dispatch-registry.yaml` (per-edge dispatch envelopes; PR-R forward-port at M5)
- `app/models/registry.yaml` (model catalog)
- `app/models/selection_policy.yaml` (auto-select rules)
- `app/specialists/{name}/model_config.yaml` (per-specialist model cascade)
- `scripts/dev/init_postgres.sql` (repo; idempotent bootstrap for operator's native Postgres 15+ install — **no Docker / no compose file**)

**Frozen-graph-version directory:** `runtime/graphs/v{N}/` per D8. Contents fixed (manifest-snapshot, dev-graph-manifest-snapshot, pack-version.txt, dispatch-registry-snapshot, compiled-graph-digest, README). No ad-hoc files.

**Sanctum files:** `_bmad/memory/bmad-agent-{name}/` — fixed names per D5 enumeration: `INDEX.md`, `PERSONA.md`, `access-boundaries.md`, `chronology.md`, plus L5/L6 reference files declared in `INDEX.md`. New files without `INDEX.md` declaration are ignored by cold-read (intentional — enumeration is explicit).

### 3. Pydantic Model Conventions (extends 14-idiom checklist)

All Pydantic v2 models in `app/` use:
- `model_config = ConfigDict(validate_assignment=True, extra="forbid")` unless the model is a permissive bag (rare; must name why).
- Timezone-aware datetimes: `datetime.now(UTC)` / `Annotated[datetime, AfterValidator(_require_tz_aware)]`.
- UUID4 for all identity fields: `uuid_field: UUID = Field(default_factory=uuid4)`.
- Closed enums: `Literal[...]` over `Enum` where possible; triple-layer red-rejection on closed enums (field-level + model-validator + schema-pin test).
- Audit-only fields: `audit_field: X = Field(exclude=True, json_schema_extra={"SkipJsonSchema": True})`.
- Frozen identity: `model_config = ConfigDict(frozen=True)` for value objects like `OperatorVerdict`, `SanctumFingerprint`.
- Cross-field validators: `@model_validator(mode="after")` for constraints spanning multiple fields (e.g., `edit_payload` required iff `verb == "edit"`).

**LangGraph state idioms (per Amendment E `docs/dev-guide/langgraph-state-idioms.md`):**
- Graph state is a Pydantic `BaseModel` (NOT `TypedDict`) — PRD mandate.
- Reducer fields: `Annotated[list[X], operator.add]` — explicit; don't rely on default list concatenation.
- Node return: `Command[Literal["next_node_id"]]` — typed `goto` target.
- Fan-out: `Send(node_id, payload)` where `payload` is a Pydantic model, never a dict.
- Interrupt payload: a Pydantic `DecisionCard` subclass per gate (per D7 decision-card family).
- `RetryPolicy` + Pydantic interaction: Slab 4 deliverable — placeholder section until then.

### 4. Handler Signature Conventions

Every step handler in `app/marcus/handlers/` or `app/specialists/*/graph.py` conforms to:

```python
def run(state: RunState) -> Command[Literal["...possible_next_nodes..."]]:
    # 1. Resolve model (D2)
    model, trail = resolve_model(node_id=..., state=state, agent=..., node_role=...)
    emit_resolution_trail(trail)  # LangSmith span (NFR-O4)

    # 2. Cold-read sanctum if specialist (D5)
    sanctum, fingerprint = load_sanctum(agent_name=...)
    state.sanctum_fingerprints[node_id] = fingerprint  # D1 hash

    # 3. Do work — probabilistic-first inside reason nodes; deterministic glue outside.
    #    Schema-as-boundary: Pydantic at input/output; free-text inside reason.

    # 4. Return Command with typed goto + state update
    return Command(goto="next_node_id", update={"field": value})
```

**Idempotency (NFR-R2/R3/R4):** every `act` node + gate `interrupt()` + ledger emission is idempotent by construction. Idempotency key = `(node_id, thread_id, attempt_number)`. Side effects check the key before executing; re-entry produces same output + no duplicate side effect. Scaffold-conformance test asserts idempotency contract (FR14).

### 5. Manifest-Entry Patterns (How Dev-Agents Add a New Step)

Adding a new step (e.g., `step-16-post-flight`) requires:

1. Append to `state/config/pipeline-manifest.yaml::steps[]` with all required fields (id, handler, gate_after, block_mode_trigger_paths, edges).
2. Author `app/marcus/handlers/step_16_post_flight.py` with `run(state: RunState) -> Command[...]` signature.
3. If interrupt edge: author `app/models/decision_cards/{gate_id}.py` per D7 shape.
4. If block-mode-trigger-paths listed: Slab 4 graph-compile CI will verify lockstep on next PR touching those paths.
5. Append unit test `tests/unit/handlers/test_step_16_post_flight.py` (K-floor 1.2–1.5×).
6. Append integration smoke to `tests/integration/pipeline/test_step_16_smoke.py` if the step does real work.

Scaffold-conformance (FR14) framework parametrizes over all steps automatically — no manual registry edit.

### 6. Error / Exception Taxonomy

All exceptions inherit from `app.errors.AppError` (defined Slab 1):

- `ManifestError(AppError)` — manifest parse / validation / handler-ref-not-importable. Raised by `app/manifest/loader.py`. Fails graph compile.
- `HandlerError(AppError)` — generic handler-runtime failure; includes `node_id` + `thread_id`. Surfaces to LangSmith as node-error.
- `SanctumError(AppError)` — sanctum read / fingerprint / invalidation. Fatal per NFR-I6.
- `ModelResolutionError(AppError)` — selector cascade exhausted; registry-ref not found.
- `GateError(AppError)` — DecisionCard validation / verdict digest mismatch / unauthorized verdict construction. Non-fatal at the gate; operator sees the error and retries.
- `ReplayError(AppError)` — sanctum hash mismatch in fail-loud mode (D1 CI replay policy); pack-hash drift in trial-replay regression.
- `LockstepError(AppError)` — block-mode-trigger-path drift detected at graph compile (Slab 4 CI).
- `SchedulerImportError(AppError)` — `app.gates.**` tried to import a scheduler dependency (D3 enforcement).

Ruff custom rule: no bare `except:` clauses; no `except Exception:` without re-raise or logger. `except AppError as e:` is the standard pattern.

### 7. Ledger Event Emission Patterns

Ledger events (FR45, Slab 4) follow `app/ledger/events.py` discriminated-union shape:

```python
class LedgerEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    trial_id: str
    gate_id: str | None
    node_id: str | None
    kind: Literal["interrupt", "verdict", "resolution", "sanctum_mutation", "compile", ...]
    timestamp: datetime  # UTC, timezone-aware
    payload: LedgerEventPayload  # per-kind Pydantic subclass
    idempotency_key: str  # (kind, node_id, trial_id, attempt_number)
```

Emission:
- `emit_ledger_event(event)` is the single public function in `app/ledger/`.
- Internal deduplication by `idempotency_key` (NFR-R4).
- Failure is non-fatal (NFR-I2 parallel: ledger-emit failure logs + increments a counter; doesn't fail the node).
- Persisted to Postgres `ledger_events` table (Slab 4 schema).

Queries:
- `reject_rate_per_gate(trial_id)` → FR37.
- `gate_inventory(trial_id)` → FR36.
- `sanctum_mutations(trial_id)` → FR59.

### 8. LangSmith Span Tag Contract (NFR-O4)

Every LangSmith span emitted from `app/` carries:
- `trial_id` (always)
- `node_id` (always for step handlers; null for substrate)
- `agent` (specialist name or `marcus`/`cora` for lane orchestrator)
- `lane: Literal["run", "dev"]`
- Model-resolution spans add: `resolution_level ∈ {1,2,3}`, `chosen_model`, `policy_hit` (nullable).
- Gate spans add: `gate_id`, `decision_card_digest`.
- Ledger-emit spans add: `ledger_event_kind`, `idempotency_key`.

Span-tag contract tested in `tests/integration/observability/test_langsmith_span_contract.py` (Slab 1 scaffold; populated at each slab).

### 9. Test-Authoring Patterns (K-Floor Compliance)

Inherited from primary repo (`docs/dev-guide/story-cycle-efficiency.md`):

- K-floor target: **1.2× ≤ ratio ≤ 1.5×**. Tests below 1.0× K = under-tested. Above 5× K = governance finding.
- **Single-gate by default**; dual-gate only for schema-shape stories + cross-cutting governance stories + substrate stories touching >2 concern domains.
- Per-family shape-pin tests (one per Pydantic family; not one per field).
- Parametrize aggressively — `@pytest.mark.parametrize` over data matrices, not copy-paste test bodies.
- DISMISS rubric for cosmetic NITs at G6 bmad-code-review: cosmetic preferences = DISMISS with rationale.
- Scaffold adoption: schema-shape stories inherit `docs/dev-guide/scaffolds/schema-story/` starting stubs; dev-agent extends, not re-derives.

**Canary tests** (per Amendment C + Murat): `tests/end_to_end/test_harness_contract.py` + `tests/trial_replay/test_harness_contract.py` assert directory + naming + README invariants. Run from Slab 1.

### 10. Pre-Commit / Lint Rules

`ruff.toml`:
- Line-length 100.
- Rules: `E`, `F`, `I` (imports), `UP` (pyupgrade), `B` (bugbear), `N` (pep8-naming), `S` (bandit subset).
- Custom check: reject `asyncio.sleep` / `threading.Timer` / `apscheduler` / `schedule` imports inside `app/gates/**` (D3).

`import-linter` contracts (per §2 above) — enforced in pre-commit and graph-compile CI.

Pre-commit hooks:
- `ruff check --fix` + `ruff format`.
- `import-linter` contract check.
- `check_manifest_lockstep.py` (Slab 4; until then, the existing primary-repo L1 check serves).
- `check_dispatch_registry_lockstep.py` (PR-R forward-port at M5).

### 11. Anti-Patterns (living catalog per NFR-M6 + D12)

Lives at `docs/dev-guide/specialist-anti-patterns.md`. Slab 1 ships the stub with these initial entries inherited from primary repo's existing `docs/dev-guide/dev-agent-anti-patterns.md`:

1. **Shape-separation violation.** Story author writes dispatcher wiring inside a schema-shape story. Counter: separate stories per concern.
2. **Leaky neck.** Agentic judgment enforces a deterministic constraint. Counter: push constraint to schema or deterministic glue.
3. **Cage drift.** Using `AgentExecutor` / `initialize_agent` / high-level abstractions. Counter: stick to `StateGraph` + `add_node` + typed Command returns.
4. **Pad-to-K.** Writing tests purely to hit K-floor. Counter: K-floor floor, not ceiling; shape-pin + parametrize + dismiss cosmetic.
5. **Scaffold-skip.** Dev-agent re-derives schema-shape from scratch. Counter: inherit scaffold stubs; extend, don't re-derive.

Slab 2 + Slab 3 migration will harvest additional anti-patterns empirically (FR64).

### Enforcement Summary

**Every slab-closing bmad-code-review gate checks:**
- Four-file-lockstep holds (model + schema + shape-pin + golden fixture in same PR).
- Import-linter contracts pass.
- K-floor ratio within 1.2–1.5×.
- Span-tag contract test green.
- Scaffold-conformance framework green (where specialists exist).
- Three-line D12 protocol on slab-closing story (invariant-preservation + anti-pattern harvest + migration-guide section update).
- Idempotency assertion on any new `act` node or gate.

## Project Structure & Boundaries

### FR-to-Slab Mapping (Consolidated Requirements → Components)

| FR range | Capability | Component / package | Slab of first use |
|---|---|---|---|
| FR1–FR8 | Runtime Platform | `app/runtime/`, `app/state/`, `app/manifest/`, `app/http/`, `app/mcp_server/` | Slab 1 |
| FR9–FR16 | Specialist Framework | `app/specialists/` + `_bmad/memory/bmad-agent-{name}/` sanctum + `skills/bmad-create-specialist/` generator | Slab 2 |
| FR17–FR25 | Model Selection | `app/models/` (registry, selector, adapter, selection_policy) | Slab 1 |
| FR26–FR30 | Marcus Orchestration | `app/marcus/` (intake, orchestrator, facade per Story 30-1 split) | Slab 3 |
| FR31–FR37 | Gates & HIL | `app/gates/` + `app/models/decision_cards/` + `app/gates/resume_api.py` + `app/gates/verdict.py` | Slab 3 |
| FR38–FR45 | Pipeline Lockstep & Governance | `app/manifest/compiler.py` (Slab 1) + `app/cora/` + `scripts/check_manifest_lockstep.py` + `runtime/graphs/v42/` + `app/ledger/` | Slab 4 (CI + ledger); Slab 1 (compiler) |
| FR46–FR53 | Trial-Run Discipline | `app/replay/` + `app/mcp_server/tools/trial_run.py` + `app/http/trial.py` + `app/marcus/cli/trial.py` | Slab 5 (replay/fork); Slab 1 (start/resume) |
| FR54–FR59 | Economics & Observability | `app/runtime/economics.py` + `app/runtime/sanctum_watcher.py` + LangSmith span contract | Slab 1 (measurement); Slab 5 (dashboard) |
| FR60–FR65 | Migration Hygiene & Rollback | `docs/dev-guide/langgraph-migration-guide.md` (11 sections) + `docs/dev-guide/specialist-anti-patterns.md` | Slab 1 (skeleton); Slab 5 (final) |

### Complete Project Tree

```
course-DEV-IDE-with-AGENTS/                   # hybrid clone repo root
├── app/                                       # migration target — all new Python code
│   ├── __init__.py
│   ├── errors.py                              # AppError + subclasses (§6 patterns)
│   │
│   ├── runtime/                               # Slab 1 — persistent LangGraph service substrate
│   │   ├── __init__.py
│   │   ├── server.py                          # python -m app.runtime_server entry
│   │   ├── checkpointer.py                    # langgraph-checkpoint-postgres wiring + retention/cleanup
│   │   ├── economics.py                       # FR54-FR57 cache hit rate + token cost measurement
│   │   ├── sanctum.py                         # D5 cold-read + D1 fingerprint computation
│   │   ├── sanctum_watcher.py                 # FR59 watchdog invalidation hook (Slab 5)
│   │   └── smoke_test.py                      # python -m app.smoke_test — empty-graph §01→§15
│   │
│   ├── models/                                # Slab 1 — three-level cascade + registry + adapter (D2)
│   │   ├── __init__.py
│   │   ├── adapter.py                         # thin ChatOpenAI wrapper — provider-swap point (FR25)
│   │   ├── selector.py                        # resolve_model() cascade function (FR17-FR21)
│   │   ├── registry.yaml                      # FR23 model catalog — Tier-1/2/3 governance
│   │   ├── registry.py                        # Pydantic PipelineRegistry model + loader + validator
│   │   ├── registry_check.py                  # python -m app.models.registry_check (Story 1c AC)
│   │   ├── selection_policy.yaml              # auto-select rules per tier palette
│   │   ├── selection_policy.py                # Pydantic SelectionPolicy model
│   │   ├── state/                             # Pydantic state base classes (FR-implicit across all)
│   │   │   ├── run_state.py                   # RunState for Marcus run-graph
│   │   │   ├── story_state.py                 # StoryState for Cora dev-graph
│   │   │   ├── cache_state.py                 # D2 per-node prefix warmth tracking
│   │   │   ├── specialist_envelope.py         # 9-node scaffold input shape
│   │   │   └── specialist_return.py           # 9-node scaffold output shape
│   │   └── decision_cards/                    # D7 per-gate Pydantic family
│   │       ├── __init__.py
│   │       ├── base.py                        # base DecisionCard + DecisionCardMeta (cache-state, override-trail)
│   │       ├── g1.py                          # pre-flight gate DecisionCard (Slab 3 filled)
│   │       ├── g2c.py                         # storyboard-A checkpoint (Slab 3)
│   │       ├── g3.py                          # Slab 3
│   │       └── g4.py                          # Slab 3
│   │
│   ├── manifest/                              # Slab 1 — manifest-as-graph-config per D6
│   │   ├── __init__.py
│   │   ├── schema.py                          # PipelineManifest + Step + Edge + EdgeKind Pydantic
│   │   ├── loader.py                          # YAML → PipelineManifest with handler-import validation
│   │   └── compiler.py                        # PipelineManifest → compiled StateGraph (run or dev lane)
│   │
│   ├── http/                                  # Slab 1 — FastAPI localhost-only escape hatch (FR2, NFR-S2)
│   │   ├── __init__.py
│   │   ├── server.py                          # FastAPI app factory
│   │   ├── trial.py                           # /trial/* endpoints per D7
│   │   ├── gate.py                            # /gate/verdict + /gate/{id}/current per D7
│   │   ├── state.py                           # GET /state/{trial}/{checkpoint} read-only (FR53)
│   │   └── model.py                           # POST /model/override per D2
│   │
│   ├── mcp_server/                            # Slab 1 IF smoke exercises MCP; Slab 2 otherwise (open Q)
│   │   ├── __init__.py
│   │   ├── server.py                          # MCP server; spec-pinned per NFR-I4
│   │   └── tools/                             # per D7 MCP tool surface
│   │       ├── trial_run.py                   # start/resume/fork/replay
│   │       ├── specialist.py                  # invoke
│   │       ├── gate.py                        # decide (calls app.gates.resume_api)
│   │       ├── state.py                       # inspect (read-only)
│   │       └── model.py                       # override
│   │
│   ├── gates/                                 # Slab 3 — HIL tamper-evidence per D3
│   │   ├── __init__.py
│   │   ├── verdict.py                         # OperatorVerdict Pydantic (frozen; validate_assignment)
│   │   ├── resume_api.py                      # SOLE resume authority; import-linter protected
│   │   ├── interrupt_wrapper.py               # wraps step handlers with interrupt() + DecisionCard emission
│   │   └── party_mode_as_interrupt.py         # Slab 4 — FR41 party-mode gate
│   │
│   ├── marcus/                                # Slab 3 — run-graph lane (per Amendment A sibling)
│   │   ├── __init__.py
│   │   ├── intake.py                          # Story 30-1 pre-packet extraction — forward-port surface
│   │   ├── orchestrator/                      # Story 30-1 write-API + plan-and-execute supervisor
│   │   │   ├── __init__.py
│   │   │   ├── write_api.py                   # sanctioned single-writer
│   │   │   ├── supervisor.py                  # Plan-and-Execute default, ReAct on explore preset
│   │   │   └── routing.py                     # manifest-driven specialist routing
│   │   ├── facade.py                          # get_facade() lazy accessor (Story 30-1)
│   │   ├── handlers/                          # step handlers per manifest
│   │   │   ├── step_01_pre_flight.py
│   │   │   ├── step_02_source_ingestion.py
│   │   │   ├── step_03_context_building.py
│   │   │   ├── step_04_lesson_planning.py
│   │   │   ├── step_05_irene_pass_1.py
│   │   │   ├── step_06_storyboard_a.py
│   │   │   ├── step_06b_gary_dispatch.py
│   │   │   ├── step_06c_motion_dispatch.py
│   │   │   ├── step_07_irene_pass_2.py
│   │   │   ├── step_08_storyboard_b.py
│   │   │   ├── step_09_narration_generation.py
│   │   │   ├── step_10_quinn_r_pre_composition.py
│   │   │   ├── step_11_assembly_bundle.py
│   │   │   ├── step_12_compositor_dispatch.py
│   │   │   ├── step_13_final_composition.py
│   │   │   ├── step_14_quinn_r_post_composition.py
│   │   │   └── step_15_trial_close.py
│   │   └── cli/                               # CLI transport per D7
│   │       ├── __init__.py
│   │       ├── main.py                        # app.marcus.cli entry
│   │       ├── trial.py                       # trial subcommand
│   │       ├── gate.py                        # gate subcommand (calls resume_api)
│   │       ├── state.py                       # state inspect subcommand
│   │       └── model.py                       # model override subcommand
│   │
│   ├── cora/                                  # Slab 4 — dev-graph lane (sibling to marcus, import-linter separated)
│   │   ├── __init__.py
│   │   ├── graph.py                           # story-cycle StateGraph: plan → implement → test → review → done
│   │   ├── handlers/
│   │   │   ├── plan_story.py
│   │   │   ├── implement_story.py
│   │   │   ├── test_story.py
│   │   │   ├── review_story.py
│   │   │   └── close_story.py
│   │   └── block_mode_hook.py                 # existing pre-commit → elevated to graph-compile CI per D4
│   │
│   ├── specialists/                           # Slab 2 — 9-node scaffold per specialist
│   │   ├── __init__.py
│   │   ├── _scaffold/                         # canonical reference scaffold (PRD §Code Examples)
│   │   │   ├── graph.py                       # 9-node: plan→enter_sanctum→load_expertise→reason→act→validate→emit→return→exit_sanctum
│   │   │   ├── state.py                       # reference envelope/return
│   │   │   ├── model_config.yaml              # reference model cascade
│   │   │   └── README.md                      # how to extend
│   │   ├── irene/                             # Slab 2a (PR-R-conformant)
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   ├── model_config.yaml
│   │   │   ├── expertise/                     # L5 domain references
│   │   │   └── sanctum -> ../../../_bmad/memory/bmad-agent-irene/  # symlink
│   │   ├── kira/                              # Slab 2a (PR-R-conformant)
│   │   ├── texas/                             # Slab 2a (PR-R-conformant)
│   │   ├── gary/                              # Slab 2b
│   │   ├── vera/                              # Slab 2b
│   │   ├── quinn_r/                           # Slab 2b
│   │   ├── desmond/                           # Slab 2b
│   │   ├── tracy/                             # Slab 2b
│   │   ├── paige/                             # Slab 2b
│   │   ├── winston/                           # Slab 2b (if in-scope as runtime specialist)
│   │   ├── mike/                              # Slab 2b
│   │   ├── dan/                               # Slab 2b
│   │   ├── eli/                               # Slab 2b
│   │   ├── enrique/                           # Slab 2b
│   │   ├── mira/                              # Slab 2b
│   │   ├── sally/                             # Slab 2b
│   │   ├── kim/                               # Slab 2b
│   │   └── wondercraft/                       # Slab 2c — generator-produced pilot
│   │       └── ...same 9-node shape
│   │
│   ├── ledger/                                # Slab 4 — learning-event emission (FR45, NFR-R4)
│   │   ├── __init__.py
│   │   ├── events.py                          # LedgerEvent discriminated union
│   │   ├── emitter.py                         # emit_ledger_event() idempotent API
│   │   ├── queries.py                         # reject_rate_per_gate, gate_inventory, sanctum_mutations
│   │   └── schema.sql                         # Postgres ledger_events table
│   │
│   └── replay/                                # Slab 5 — trial-replay + fork per FR49/FR50/FR51
│       ├── __init__.py
│       ├── replay.py                          # byte-for-byte replay from checkpoint
│       ├── fork.py                            # fork-from-checkpoint sibling thread
│       ├── regression.py                      # FR51 100%-of-closed-trials regression harness
│       └── parity.py                          # FR52 head-to-head parity trial validation
│
├── runtime/                                   # runtime artifacts (frozen per D8)
│   └── graphs/
│       └── v42/                               # Slab 1 stub; Slab 5 ship fills
│           ├── README.md                      # "frozen; do not edit"
│           ├── manifest-snapshot.yaml
│           ├── dev-graph-manifest-snapshot.yaml
│           ├── pack-version.txt
│           ├── dispatch-registry-snapshot.yaml
│           └── compiled-graph-digest.txt
│
├── state/                                     # existing: config + SQLite runtime
│   ├── config/
│   │   ├── pipeline-manifest.yaml             # D6 — existing extended for graph compiler
│   │   ├── dev-graph-manifest.yaml            # D4 — Slab 4 Cora manifest (new)
│   │   └── dispatch-registry.yaml             # PR-R forward-port at M5 (new)
│   └── runtime/
│       └── coordination.db                    # existing SQLite; Postgres becomes authoritative
│
├── _bmad/                                     # existing BMad Method artifacts
│   └── memory/                                # sanctum tree — retained per Amendment G
│       ├── bmad-agent-marcus/
│       │   ├── INDEX.md
│       │   ├── PERSONA.md
│       │   ├── access-boundaries.md
│       │   ├── chronology.md
│       │   └── CLONE-FORK-NOTICE.md           # Slab 1 Story 1b AC — clone-authoritative from <date>
│       ├── bmad-agent-irene/
│       ├── bmad-agent-gary/
│       └── ...one per specialist
│
├── skills/                                    # existing BMAD skill directories
│   ├── bmad-agent-marcus/                     # unchanged; coexists during migration
│   ├── bmad-create-specialist/                # NEW Slab 2 — scaffold generator
│   │   ├── SKILL.md
│   │   ├── templates/                         # 9-node scaffold templates
│   │   └── scripts/
│   └── bmad-agent-*/                          # existing specialists retained during migration
│
├── tests/                                     # four-tier layout per Amendments C + D
│   ├── unit/
│   │   ├── models/                            # Pydantic shape-pin tests
│   │   ├── selector/                          # FR17-FR21 cascade tests
│   │   ├── manifest/                          # D6 loader + compiler validation tests
│   │   └── sanctum/                           # D5 cold-read + fingerprint tests
│   ├── integration/
│   │   ├── pipeline/                          # step-handler integration
│   │   ├── gates/                             # D3 tamper-evidence + transport-parity tests
│   │   ├── scaffold_conformance/              # Amendment D — framework + fixture-specialist
│   │   └── observability/                     # LangSmith span-tag contract tests
│   ├── end_to_end/
│   │   ├── test_harness_contract.py           # canary (Amendment C)
│   │   └── test_empty_graph_15_steps.py       # M1 evidence — Slab 1
│   ├── trial_replay/
│   │   ├── test_harness_contract.py           # canary (Slab 5 populates real content)
│   │   └── README.md                          # "Slab 5 populates; harness contract NFR-M3"
│   └── fixtures/
│       ├── specialists/
│       │   └── fixture_minimal_specialist.py  # Amendment D — parametrize conformance framework
│       └── models/                            # golden-fixture JSONs per four-file-lockstep
│
├── scripts/                                   # existing primary-repo shape retained
│   └── check_manifest_lockstep.py             # Slab 4 — CI library (D4)
│
├── docs/                                      # existing + new Slab deliverables
│   └── dev-guide/
│       ├── pydantic-v2-schema-checklist.md    # existing + one-paragraph LangGraph cross-ref (Amendment E)
│       ├── scaffolds/
│       │   └── schema-story/                  # existing — unchanged per Amendment E
│       ├── langgraph-runtime-setup.md         # Slab 1 deliverable
│       ├── model-selection-guide.md           # Slab 1 deliverable + D13 mid-bump procedure
│       ├── langgraph-state-idioms.md          # NEW Slab 1 deliverable (Amendment E)
│       ├── frozen-graph-version-ceremony.md   # Slab 4 deliverable (D8)
│       ├── langgraph-migration-guide.md       # Slab 1 skeleton (11 sections); Slab 5 final (FR65)
│       └── specialist-anti-patterns.md        # Slab 1 stub; Slab 2 harvest; Slab 5 ≥5 entries (FR64)
│
├── scripts/dev/init_postgres.sql              # NEW Slab 1 — idempotent bootstrap for native local Postgres 15+ (Story 1b AC; NO Docker)
├── pyproject.toml                             # extended — ruff + import-linter contracts + dep pins
├── requirements.lock                          # NEW Slab 1 Story 1a
├── uv.lock                                    # existing
├── .env.example                               # OPENAI_API_KEY + LANGSMITH_API_KEY + DATABASE_URL
└── .gitignore                                 # + .langgraph_api/, runtime/graphs/v*/compiled-graph-digest.txt (generated)
```

### Component Boundary Map

**Who can call whom (import-linter contracts):**

- `app.marcus` ↔ `app.cora` — **NO** (lane separation, D4 + invariant #15).
- `app.specialists.*` → `app.marcus.*` or `app.cora.*` — **NO** (specialists are lane-agnostic; both lanes invoke them).
- `app.marcus.handlers.*` → `app.specialists.*` — **YES** (via routing per manifest).
- `app.cora.handlers.*` → `app.specialists.*` — **YES** (dev-graph can invoke specialists).
- `app.gates.resume_api` — called **ONLY** from `app.mcp_server.tools.gate_decide`, `app.http.gate`, `app.marcus.cli.gate` (D3).
- `app.gates.**` → `asyncio.sleep` / `threading.Timer` / `apscheduler` / `schedule` — **NO** (D3 ruff check).
- `app.runtime.*` → `app.marcus.*` / `app.cora.*` / `app.specialists.*` — **NO** (runtime is substrate; doesn't know domain).
- `app.models.*` → `app.state.*` — **YES** (models depend on state base classes).
- `app.models.adapter` → `openai` / `langchain_openai` — **YES** (thin adapter is the provider boundary).
- Anywhere in `app/` → `langgraph` / `pydantic` — **YES** (framework primitives).
- Anywhere in `app/` → `langchain.agents.*` / `AgentExecutor` / `initialize_agent` — **NO** (reject-the-cage).

**Data flow:**
- Operator ↔ MCP / FastAPI / CLI ↔ `app.gates.resume_api` ↔ compiled StateGraph ↔ Postgres checkpointer.
- Every LLM-invoking node ↔ `app.models.selector` ↔ `app.models.adapter` ↔ OpenAI API.
- Specialist `act` nodes ↔ L7 MCP tools ↔ external APIs (Gamma, ElevenLabs, Canvas, …).
- Every gate `interrupt()` ↔ `app.ledger.emit_ledger_event` ↔ Postgres `ledger_events` table.
- LangSmith receives spans from every `app/` LLM call + every node entry/exit.

### Requirements-to-Component Matrix (Spot Check)

- **FR1 persistent runtime** → `app/runtime/server.py`
- **FR3 checkpointing** → `app/runtime/checkpointer.py` + `scripts/dev/init_postgres.sql` (native local Postgres; no container runtime)
- **FR8 manifest topology** → `app/manifest/loader.py` + `app/manifest/compiler.py`
- **FR11 sanctum cold-read** → `app/runtime/sanctum.py`
- **FR14 scaffold-conformance** → `tests/integration/scaffold_conformance/` + `app/specialists/_scaffold/`
- **FR20 Marcus reasoning lock** → `app/marcus/model_config.yaml`
- **FR26 Marcus SPOT** → `app/marcus/facade.py` (operator entry) + all three transports route through facade
- **FR34 no auto-approve** → `app/gates/verdict.py` + `app/gates/resume_api.py` + import-linter contracts
- **FR40 lane separation** → `app.marcus` ⊥ `app.cora` contract + separate `StateGraph` compilation
- **FR43 frozen-graph** → `runtime/graphs/v42/`
- **FR45 learning ledger** → `app/ledger/emitter.py`
- **FR51 trial-replay regression** → `app/replay/regression.py` + `tests/trial_replay/`
- **FR63 15-invariant audit matrix** → D12 protocol → Slab 5 rolls up to `docs/dev-guide/langgraph-migration-guide.md`
- **NFR-M2 model_config lint at compile** → `app/manifest/compiler.py` validation mode iterates specialist configs
- **NFR-M5 four-file lockstep** → pre-commit hook + bmad-code-review checklist

Every FR has a component. Every component has an FR.

### Out-of-Scope Zones (Explicitly)

- No web UI code (no `ui/`, `static/`, `templates/`).
- No multi-tenant authorization (no `auth/`, no RBAC module).
- No deploy tooling. Postgres runs as a natively-installed service on the operator's machine; no Docker, no docker-compose, no container runtime is part of the architecture.
- No Celery / Ray / Dask task queues.
- No remote API gateway (FastAPI stays localhost).

## Architecture Validation

### Coherence Validation

**Decision compatibility (13 decisions cross-checked):**
- D1 (sanctum hybrid) + D5 (cold-read contract) share hashing infrastructure. ✅ Unified.
- D2 (state-embedded overrides) + D3 (OperatorVerdict state field) + D7 (transport parity) all route through `RunState`. ✅ Consistent.
- D6 (manifest-as-graph-config) + D4 (graph-compile CI) + D8 (frozen-graph-version) form one pipeline: manifest → compile → freeze. ✅ Coherent.
- D3 (no-scheduler import-linter) + D11 (no idle-gate ping) + substrate invariant #4 aligned — HIL discipline three ways. ✅ Reinforced.
- PR-R forward-port convergence + D10 (Slab 2 sub-structure) + D6 (dispatch-registry as manifest companion) form one inheritance story. ✅ Named.

**Pattern consistency:**
- Naming patterns (§1) match FR-named artifacts (FR9 9-node scaffold = `app/specialists/*/graph.py`; FR13 `bmad-create-specialist`; FR63 15-invariant audit matrix).
- Structural patterns (import-linter contracts, four-file-lockstep locations) enforce D3 + D4 + D6 + D12 at compile/pre-commit time.
- Pydantic model conventions extend the 14-idiom checklist without contradiction.

**Structure alignment:**
- 12-package tree (§Project Tree) × traceability table (D6 + Step 3 Amendment B): every package maps to an FR; packages deferred beyond Slab 1 are explicitly called out.
- Import-linter contracts enforce lane separation at compile time, matching FR40 + invariant #15.
- Test-tier layout with canaries (Amendment C) + scaffold-conformance framework (Amendment D) deliver NFR-M3 four-layer test strategy from Slab 1.

### Requirements Coverage Validation

**FR coverage — 65/65.** Full matrix in §Project Structure §Requirements-to-Component Matrix. Every FR has a component + a slab + (where applicable) a milestone acceptance bullet. Readiness Finding #2 closed via D2 + D3 + D7 amendments; seven gap FRs now have evidence bullets.

**NFR coverage — 43/43.** 
- Performance (6): operator-latency budgets shape physical deployment (local Postgres, localhost MCP, SSD sanctum).
- Security (7): single-operator trust boundary + localhost-only endpoints + `.env` discipline.
- Integration (6): brownfield-critical Texas retrieval unmodified; MCP protocol pinned; sanctum fatal-on-error.
- Reliability (7): idempotency contracts + checkpoint recovery + operator-presence availability.
- Reproducibility (5, domain-critical): D1 hybrid sanctum snapshot + D8 frozen-graph + D2 state-embedded model overrides + documented temp-variance bands.
- Maintainability (8): scaffold-conformance + four-file-lockstep + K-floor + four-tier test + living catalog + migration guide + `docs/dev-guide/` coverage.
- Observability (4): 100% LangSmith coverage + D2 span-tag contract + D5 invalidation hook + D2 resolution trail.

**Readiness Finding #1 (NFR count drift 38 vs 43):** deferred to Step 8 PRD-amendment-of-record. Architecture locks the 43-NFR count as authoritative.

**All 15 Load-Bearing Substrate Invariants have preserving implementations:**

| Invariant | Preserving pattern | Reference |
|---|---|---|
| #1 Marcus SPOT | `app/marcus/facade.py` + three-transport routing | D7 + FR26 |
| #2 Marcus stateless cold-start | FR30 cold-read on every session; sanctum is disk-authoritative | D5 + FR30 |
| #3 15-step manifest = deterministic neck | D6 manifest-as-graph-config; topology loaded, not invented | D6 |
| #4 Gates HIL-paused | D3 OperatorVerdict + resume_api + no-scheduler import-linter | D3 |
| #5 Learning events G2C/G3/G4 | `app/ledger/emitter.py` + FR45 + NFR-R4 idempotency | FR45 + D12 |
| #6 Three-layer code review | bmad-code-review gate at every slab-closing story | §6 Patterns + D12 |
| #7 K-floor test discipline | §9 Test-Authoring Patterns 1.2–1.5× ratio | §9 + NFR-M4 |
| #8 Pydantic-v2 four-file-lockstep | §2 Structural Patterns + pre-commit hook | §2 + NFR-M5 |
| #9 Learning-ledger side-effect | Ledger `act` nodes idempotent, non-fatal on emit failure | §7 + NFR-R4 |
| #10 Frozen-at-ship pack | D8 `runtime/graphs/v42/` + ceremony doc | D8 + FR43/FR44 |
| #11 K-floor story-cycle | inherited from `docs/dev-guide/story-cycle-efficiency.md` | §9 + NFR-M4 |
| #12 Marcus-first orchestration | `app/marcus/facade.py` + Marcus-first activation in CLAUDE.md | D7 + FR30 |
| #13 Specialist registry authoritative | manifest + `app/specialists/` compile-time discovery | D6 + FR14 |
| #14 Deferred-inventory continuity | CLAUDE.md §Deferred inventory governance + D12 Step 7 protocol | CLAUDE.md + D12 |
| #15 Cora/Marcus lane separation | `app.marcus` ⊥ `app.cora` import-linter + two manifest files | D4 + D6 |

**15/15 invariants covered. Zero drop budget honored.**

### Open Questions Remaining

1. **Winston's Step 3 question — MCP in Slab 1 smoke test?** Architecture commits to include `app/mcp_server/` as a Slab 1 package **IF** Slab 1 smoke exercises MCP; deferred to Slab 2 otherwise. **Default for architecture doc: MCP in Slab 1** (seven-package Slab 1 scope). Rationale: operator workflow (Journey 1: pause+resume across IDE sessions) exercises MCP from Day 1; deferring MCP to Slab 2 postpones the central value proposition. Operator can override at epic-authoring time.

2. **PR-R cross-repo coordination signal.** Flag for operator: before primary-repo opens the PR-R dev-story, inject a Pydantic-v2 four-file-lockstep checklist requirement into PR-R's T1 readings. Saves a reconciliation pass at M5. **Action:** staged in migration-guide §8 + will land in deferred-inventory at Step 8.

3. **D1 sub-decision: sanctum enumeration.** Slab 1 early spike decides exactly which files fingerprint covers. Default: `INDEX.md`, `PERSONA.md`, `access-boundaries.md`, `chronology.md` + any `L5-*.md` / `L6-*.md` declared in `INDEX.md`. Chronology.md mutates every session — may need exclusion-from-fingerprint to avoid spurious cache-prefix invalidation. Flag for Slab 1 story author.

### Readiness Findings Disposition

| # | Finding | Closure |
|---|---|---|
| 1 | NFR count drift (38 vs 43) | PRD amendment at Step 8 — architecture locks 43 as authoritative |
| 2 | Seven FRs without milestone evidence | Closed — D2 + D3 + D7 add all seven bullets; applied to PRD §M1–M5 at Step 8 |
| 3 | Slab 2 oversized | Closed — D10 splits into 2a/2b/2c; each becomes an epic |
| 4 | Slab 5 bundled | Closed — D11 splits into 5a Acceptance + 5b Polish; each becomes an epic |
| 5 | Cross-slab governance artifact ownership | Closed — D12 three-line protocol at every slab-closing story |

### Architecture Readiness Verdict

**READY** to open epic-and-story decomposition (`bmad-create-epics-and-stories`).

All 13 architectural decisions locked. All 65 FRs mapped to components + slabs. All 43 NFRs have preserving patterns. All 15 load-bearing invariants have named implementations. Five readiness findings closed. Three open questions are operator-input or Slab-1-spike level, not architecture-level.

No party-mode pass needed at this gate — party-mode Round 1 (Step 3) + autonomous decision-making per operator grant has carried the architecture to a coherent whole. Step 8 finalizes the frontmatter + PRD amendment queue + handoff artifacts.

## Architecture Completion & Handoff

### What was produced

- **8-step BMAD architecture workflow** complete (context → starter → 13 decisions → patterns → structure → validation → completion).
- **9 accepted amendments** from party-mode Round 1 (Step 3) — lane-split altitude, package-FR traceability, canary tests, scaffold-conformance framework at Slab 1, LangGraph-state-idioms doc, Story 1a/1b/1c split, CLONE-FORK-NOTICE discipline, survey-and-discard subsection, LangGraph idiom sanity check.
- **13 architectural decisions** locked (D1-D13).
- **1 PR-R forward-port convergence** staged with reconciliation plan, Slab 2 sub-structure inheritance, CI lockstep elevation, migration-guide §8 checklist.
- **43-NFR authoritative count** reconciled (PRD frontmatter update queued).
- **7 milestone evidence bullets** added (FR24, FR27, FR34, FR36, FR37, FR42, FR53 — all readiness Finding #2).
- **Full project tree + component boundary map + data flow** with import-linter contracts enforcing every invariant.
- **15/15 load-bearing invariants** have named preserving implementations with zero drop budget honored.

### PRD Amendments Queued (apply at handoff or operator-discretion)

Before epic-authoring opens, one lightweight PRD amendment pass:

1. **Update frontmatter NFR count:** 38 → 43.
2. **Add M3 evidence bullets (FR24, FR27, FR34):** see §Decision D3 + D2.
3. **Add M4 evidence bullet (FR42):** see §Decision D3.
4. **Add M5 evidence bullets (FR36, FR37, FR53):** see §Decision D3 + D7.
5. **Update §Operator-Approvable Milestones** to name Slab 2a/2b/2c + Slab 5a/5b decomposition (D10 + D11).

These amendments can be applied by the operator via a short PR, or deferred — epic-authoring can consume the architecture doc's decision record as authoritative and cite the PRD-amendment pending status in the epic headers.

### Deferred Inventory Entries to File

Three items for [_bmad-output/planning-artifacts/deferred-inventory.md](_bmad-output/planning-artifacts/deferred-inventory.md):

1. **PR-R cross-repo Pydantic-checklist injection (primary repo side).** Before primary's PR-R dev-story opens, primary must incorporate `docs/dev-guide/pydantic-v2-schema-checklist.md` into PR-R T1 readings. Saves a reconciliation pass at M5 forward-port. **Filing type:** Named-But-Not-Filed Follow-On (primary-repo scope).
2. **MCP-in-Slab-1 smoke test operator decision.** Default: MCP in Slab 1 scope (seven-package layout). Operator can override at epic-authoring time. **Filing type:** Open question pending operator input.
3. **Sanctum fingerprint enumeration spike (Slab 1 early).** Whether `chronology.md` is excluded from fingerprint (it mutates every session; including it would cause spurious cache invalidation). **Filing type:** Slab 1 story AC.

Filing to `deferred-inventory.md` deferred to Step 8 handoff — can be done at epic-authoring kickoff.

### Handoff to `bmad-create-epics-and-stories`

**Primary inputs for epic-authoring:**
- [`_bmad-output/planning-artifacts/prd-langchain-langgraph-migration.md`](prd-langchain-langgraph-migration.md) (authoritative requirements contract)
- [`_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`](architecture-langchain-langgraph-migration.md) (this document — component shape + decisions)
- [`_bmad-output/planning-artifacts/implementation-readiness-report-2026-04-22.md`](implementation-readiness-report-2026-04-22.md) (readiness findings + closure evidence)

**Recommended epic decomposition** (reflecting D10 + D11):
- **Epic M1-Slab-1 Substrate** — Stories 1a/1b/1c (per Amendment F) + ~4-6 additional stories covering selector tests, checkpoint retention, LangSmith wiring, docs (runtime-setup, model-selection-guide, langgraph-state-idioms), scaffold-conformance framework.
- **Epic M2a-Slab-2a Scaffold Pilot** (PR-R-conformant edges): scaffold-generator + Irene Pass 2 + Kira motion + Texas migrations.
- **Epic M2b-Slab-2b Specialist Tranche** (14 non-conformant edges): Gary + Vera + Quinn-R + 11 others.
- **Epic M2c-Slab-2c Wondercraft Pilot**: generator-from-scratch validation + anti-patterns catalog harvest.
- **Epic M3-Slab-3 Marcus Orchestration**: supervisor + routing + DecisionCard + three-transport verdict + override surface.
- **Epic M4-Slab-4 Lockstep + Gates + Cora**: graph-compile CI + Cora dev-graph + party-mode-as-interrupt + frozen-graph-version ceremony + ledger + Pydantic-RetryPolicy workaround.
- **Epic M5a-Slab-5a Acceptance**: trial-replay regression + head-to-head parity + cost validation + 15-invariant audit matrix + sanctum invalidation hook.
- **Epic M5b-Slab-5b Polish**: fork UX + economics dashboard + migration guide final + scaffold-generator polish.

Nine epics total. Slab 1 expected 6-8 stories; Slab 2a/2b/2c ~3+17+3; Slab 3 ~5; Slab 4 ~5; Slab 5a/5b ~4+3. Roughly 50-60 total stories across the migration — within range for a 12-16 week effort with K-floor discipline.

### Architecture Document Status

**Final. 8-step workflow complete. Ready for epic-and-story decomposition.**

Total document length: the architecture doc has grown from initial frontmatter to a 13-decision document covering substrate, invariants, patterns, structure, validation, and handoff. Every FR has a component. Every load-bearing invariant has a preserving pattern. Every readiness finding has a closure path.

The architecture-as-authored is now the governing contract for migration story authoring.





