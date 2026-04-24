# LangChain + LangGraph Migration Guide

Standing reference for the five-slab migration from the primary repo's
v4.2 orchestration pipeline to a LangChain + LangGraph-based runtime.
Owned per architecture §D12 cross-slab governance protocol; updated at
every slab-closing story.

---

## 1. Migration Overview

**Purpose:** Re-platform the Agentic Production Platform (APP) orchestration
substrate onto LangChain + LangGraph while preserving every load-bearing
substrate invariant from the primary repo. Big-bang-in-clone pattern per
PRD Decision 2 — the hybrid clone owns the migration; the primary repo
continues unchanged.

**Scope:** Five slabs (Substrate → Specialists → Marcus → Lockstep+Gates →
Trial-Run+Polish) with five operator-approvable milestones (M1–M5).
Timeline: 12–16 weeks at ~12–15 pts/week dev-agent throughput.

**Current status (2026-04-23):** **Slab 1 CLOSE.** Stories 1.1a / 1.1b / 1.1c /
1.1d / 1.2 / 1.3 / 1.4 / 1.5 / 1.6 / 1.7 all **done**. M1 acceptance evidence
pack assembled at
[`_bmad-output/implementation-artifacts/m1-acceptance-evidence-pack.md`](../../_bmad-output/implementation-artifacts/m1-acceptance-evidence-pack.md)
with one acknowledged-deferred gap (cache-hit-rate — Slab 2 first specialist
measures). Slab 2 specialist scaffold pilot (Story 2a.1) is the next story.

---

## 2. Architecture Decisions of Record (D1–D13)

Every locked-in decision from the 2026-04-22 architecture authoring. One-paragraph
summaries; the full text lives at
[`_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md`](../../_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md).

- **D1 — Sanctum Snapshot Strategy (hybrid).** Sanctum state snapshots use
  either inline payload or content-hash pointer per snapshot-size heuristic.
- **D2 — Three-Level Model-Cascade.** Per-call override → per-specialist
  `model_config.yaml` → registry default. See
  [`model-selection-guide.md`](model-selection-guide.md).
- **D3 — HIL Invariant Tamper-Evidence.** `app/gates/**` scheduler-forbidden;
  `OperatorVerdict` triple-layer red-rejection on verb enum; `resume_api`
  import-linter Contract C3.
- **D4 — Cora ⊥ Marcus Lane Separation.** Separate `StateGraph`
  instances per lane (`run_graph` vs `dev_graph`); enforced by import-linter
  Contract C1 + manifest `lane` field + per-specialist package placement.
- **D5 — Sanctum Cold-Read Discipline + Cache-Prefix Stability.** Sanctum
  reads are cold; cache-prefix hashes are deterministic across subprocesses.
- **D6 — Manifest-as-Graph-Config Loader.** `PipelineManifest` (Slab 1 Story
  1.4) is the sole source of graph topology; loader + compiler own the
  YAML→StateGraph path.
- **D7 — Operator-Surface Contract — Three-Transport Parity.** MCP + FastAPI
  + CLI expose the same minimal-node contract (FR2). M1 asserts
  two-transport parity (FastAPI↔MCP byte-equivalent); Slab 3 Story 3.4 adds
  the CLI leg.
- **D8 — Frozen-Graph-Version Ceremony.** Each graph version snapshots
  manifest + dispatch registry + compiled graph digest under
  `runtime/graphs/v{version}/`. Slab 1 creates the directory; Slab 4 Story
  4.5 wires the full ceremony.
- **D9 — Milestone Evidence Bullets.** Each slab-closing story assembles an
  evidence pack documenting milestone acceptance + acknowledged gaps.
- **D10 — Slab 2 Sub-Structure (2a/2b/2c).** Specialist migrations split
  into scaffold pilot (2a), tranche 14 (2b), Wondercraft + generator (2c).
- **D11 — Slab 5 Split (5a/5b).** Acceptance (5a) + polish (5b).
- **D12 — Cross-Slab Governance Artifact Ownership Protocol.** Closing
  stories follow a three-line commit message protocol; deferred inventory +
  anti-patterns catalog + migration guide owned cross-slab.
- **D13 — Model-Registry Mid-Migration Bump Procedure.** Three-tier
  (patch/minor/major) version bump governance. See `model-selection-guide.md §Version-bump`.

---

## 3. Substrate Inventory

Slab 1 close state of the `app/` package tree:

- **`app/manifest/`** — `PipelineManifest` / `NodeSpec` / `EdgeSpec` +
  `load()` + `compile()` + condition registry + exceptions. Architecture D6.
- **`app/models/`** — `RunState`, `StoryState`, `SpecialistEnvelope`,
  `SpecialistReturn`, `OperatorVerdict`, `SanctumFingerprint`, `CacheState`,
  `NodeCheckpoint`, `ModelResolutionEntry` (all under `app/models/state/`);
  `registry.py` / `selector.py` / `selection_policy.py` / `adapter.py` /
  `specialist_model_config.py`. Architecture D2, D3.
- **`app/gates/`** — `resume_api.resume_from_verdict()` signature stub
  (Slab 3 Story 3.3 fills body). Architecture D3 + Contract C3.
- **`app/runtime/`** — `server.py` (FastAPI), `minimal_node.py`,
  `span_tags.py`, `checkpointer.py`, `cleanup_threads.py`, `retention_policy.py`.
- **`app/mcp_server/`** — `server.py`, `protocol.py`, `tools/gate_decide.py`,
  `tools/ping.py`, `__main__.py`.
- **`app/specialists/`** — `_stub/passthrough_specialist.py` (Slab 1 target of
  every `specialist_id`); Slab 2 populates per-specialist subdirectories.
- **`app/marcus/`** + **`app/cora/`** — empty Slab-1 placeholders; Slab 3
  populates Marcus; Slab 4 populates Cora.
- **`app/smoke_test.py`** — substrate + full-manifest smoke harness.

**Frozen-graph directory:** `runtime/graphs/v0.1-stub/` (Slab 1 substrate
stub) + `runtime/graphs/v42/` (from 1.1b, anchors the migrated v4.2 manifest
from 1.6).

**Sanctum tree:** Hybrid scope lives at
`_bmad/memory/bmad-agent-{name}/` per CLAUDE.md §Custom agents; migration
work does not touch sanctum content (forward-port freeze FR60 active since
Story 1.1a).

---

## 4. State Contract Reference

Eight state models + one cascade-resolution entry:

- **`RunState`** — top-level run state (status, graph_version, temperature,
  model_resolution_trail reducer field).
- **`StoryState`** — per-story content (lesson_plan, segment_manifest,
  slides, etc.; Slab 2+ populates).
- **`OperatorVerdict`** — frozen tamper-evident HIL verdict (FR34
  triple-layer red-rejection on verb).
- **`SpecialistEnvelope`** — dispatch payload to a specialist node.
- **`SpecialistReturn`** — dispatch return from a specialist node (with
  optional `OperatorVerdict` attachment).
- **`SanctumFingerprint`** — sanctum snapshot identity (NFR-X3).
- **`CacheState`** — per-call cache-prefix state (NFR-I6).
- **`NodeCheckpoint`** — per-node persistence record.
- **`ModelResolutionEntry`** — one cascade-resolution trail entry
  (NFR-O4 spans; NFR-X4 reproducibility).

Pydantic-v2 14-idiom checklist:
[`pydantic-v2-schema-checklist.md`](pydantic-v2-schema-checklist.md). Every
state model ships with `extra="forbid"` + `validate_assignment=True` and a
schema-pin fixture for contract parity.

---

## 5. Manifest-as-Graph-Config Reference

`PipelineManifest` schema family (Slab 1 Story 1.4): `PipelineManifest` +
`NodeSpec` + `EdgeSpec` + `LearningEventsConfig` + `StepLearningEventsConfig`.
Full shape in `app/manifest/schema.py`; Pydantic-v2 idioms enforced.

Loader: `app.manifest.loader.load(path)` — YAML + Pydantic validate,
re-raises every error as `ManifestValidationError` with named-violation
message.

Compiler: `app.manifest.compiler.compile(manifest, *, repo_root=None)` —
LangGraph `StateGraph(state_schema=RunState)`, resolves `specialist_id`
via `app.specialists._stub.passthrough_specialist.make_passthrough` (Slab 1)
or per-specialist `app.specialists.{id}.graph` (Slab 2+). Validates
`frozen_graph_version` directory presence, `model_config_ref` file presence,
condition registry membership. Enforces lane separation (D4) by producing
distinct `StateGraph` instances per lane.

Migrated manifest: `state/config/pipeline-manifest.yaml` — 33 v4.2 step ids
preserved byte-equivalent; substrate stub at
`state/config/pipeline-manifest-substrate-stub.yaml` anchors the 1.1c smoke
contract.

---

## 6. Three-Transport Operator Surface

Per architecture D7 (FR2 compound contract): MCP + FastAPI + CLI expose the
same minimal-node contract. Transport-parity matrix:
[`langgraph-runtime-setup.md §Transport Parity Contract`](langgraph-runtime-setup.md).

MCP transport: `app.mcp_server` (Slab 1 Story 1.1c code substrate + 1.1d
subprocess smoke + parity assertion). 20/20 hot+cold runs at 0% flake over
2026-04-23 measurement.

FastAPI transport: `app.runtime.server` (Slab 1 Story 1.1c + 1.1d FastAPI↔MCP
parity). 127.0.0.1-only bind per NFR-S2.

CLI transport: ⏳ Slab 3 Story 3.4.

Envelope-exception table:
[`transport-parity-envelope-exceptions.md`](transport-parity-envelope-exceptions.md)
(from Story 1.1c). Enumerates the known transport-level envelope variations
that M1 parity testing tolerates (binary encoding differences, header
metadata) versus those that fail parity (semantic divergence).

---

## 7. Model Cascade + Registry Governance

Three-level cascade + registry bump procedure — full content at
[`model-selection-guide.md`](model-selection-guide.md).

Registry + policy files: `state/config/model-registry.yaml` +
`state/config/model-selection-policy.yaml`. Slab 1 ships the schema +
selector; Slab 2 populates per-specialist `model_config.yaml` files as each
specialist migrates.

D13 version-bump procedure (patch / minor / major) governs changes. Frozen
graph version ceremony snapshots registry + policy alongside compiled graph
at each frozen version (Slab 4 Story 4.5).

---

## 8. Forward-Port Convergence (PR-R)

Primary Sprint #1's PR-R Marcus dispatch reshaping landed after the hybrid
branched. The migration guide carries a forward-port reconciliation checklist
(originally authored at architecture §8) so that when Slab 3 touches Marcus
orchestration, the hybrid re-converges on the reshaped dispatch semantics.

**Reconciliation checklist (per architecture §8):**

- [ ] Pydantic-v2 four-file-lockstep applied to PR-R's new models (model +
      validator + tests + golden fixture in same commit)
- [ ] Dispatch-registry-as-manifest-companion (PR-R's dispatch registry
      ships alongside `PipelineManifest`, not as a separate top-level config)
- [ ] L1-validator-as-library-function (PR-R's L1 validator exposed as
      callable, not only CLI)
- [ ] Receipt-shape sanctum-fingerprint (receipts carry
      `SanctumFingerprint` for NFR-X3 reproducibility)

FR60 forward-port freeze (ACTIVE since Slab 1 Story 1.1a closed). `git merge
upstream/master` is off-policy; convergence goes through this checklist.

---

## 9. Reproducibility Invariants (NFR-X1–X5)

Every migration artifact preserves:

- **NFR-X1 — Byte-for-byte replay.** `RunState`/`StoryState` round-trip via
  `model_dump_json` ↔ `model_validate_json` preserves exact bytes.
- **NFR-X2 — Frozen graph version.** `RunState.graph_version` pins to
  `ALLOWED_GRAPH_VERSIONS`; compiled graph snapshot lives at
  `runtime/graphs/v{version}/`.
- **NFR-X3 — Sanctum snapshot identity.** `SanctumFingerprint` carries
  deterministic hash of sanctum payload.
- **NFR-X4 — Model selection trail.** `RunState.model_resolution_trail`
  reducer field captures every cascade resolution (span-emitted + persisted).
- **NFR-X5 — Documented temperature variance.** `RunState.temperature`
  (0.0–2.0); operator-facing span tags record the configured value.

---

## 10. Frozen-Graph-Version Ceremony

Slab 4 Story 4.5 is the forward pointer for the full ceremony. Slab 1
creates the directory structure only:

- `runtime/graphs/v0.1-stub/README.md` — substrate stub anchor (Slab 1 Story 1.4)
- `runtime/graphs/v42/README.md` — migrated v4.2 manifest anchor (Slab 1 Story 1.1b)

Slab 4's ceremony will populate each directory with:

- Manifest snapshot (byte-equivalent copy of the manifest at ship time)
- Dispatch-registry snapshot (Slab 3 adds the registry)
- Compiled-graph-digest (SHA-256 over the serialized `StateGraph`)

---

## 11. Anti-Patterns + Operational Cookbook

Pointers:

- [`specialist-anti-patterns.md`](specialist-anti-patterns.md) — living catalog
  of anti-patterns (Slab 1 seeded with 3 confirmed + ~5 primary-repo
  inherited entries)
- [`local-postgres-setup.md`](local-postgres-setup.md) — Postgres bootstrap
  + retention cookbook
- [`langgraph-runtime-setup.md`](langgraph-runtime-setup.md) — troubleshooting
  section with the two Slab-1-burned blockers (`docker` / `psql` on PATH)
  resolved via the `project_no_docker` + `verify-via-shipped-deps` memory
  entries

Per-environment troubleshooting lives in `langgraph-runtime-setup.md §Troubleshooting`.

---

## Changelog

| Version | Date | Changes | Slab |
|---|---|---|---|
| v1 | 2026-04-23 | Initial 11-section skeleton authored at Story 1.7 close. | Slab 1 close |
