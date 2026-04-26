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

## 8. Forward-Port Convergence (PR-R) — HISTORICAL (see §8.1)

> **⚠️ Status note (2026-04-24):** This section documents the **pre-severance**
> convergence posture. It is retained for historical reference and for
> operators re-reading the migration chronology. **Current authoritative
> policy is §8.1 Upstream Severance below.** Do not apply the convergence
> checklist below as live governance; post-severance, there is no convergence
> path to upstream. If a defect surfaces that MIGHT call for upstream pull,
> see DR-5 in [`decision-records/DR-SLAB-1-CLOSE-2026-04-24.md`](../../_bmad-output/planning-artifacts/decision-records/DR-SLAB-1-CLOSE-2026-04-24.md).

Primary Sprint #1's PR-R Marcus dispatch reshaping landed after the hybrid
branched. The migration guide carries a forward-port reconciliation checklist
(originally authored at architecture §8) so that when Slab 3 touches Marcus
orchestration, the hybrid re-converges on the reshaped dispatch semantics.

**Reconciliation checklist (per architecture §8, historical):**

- [ ] Pydantic-v2 four-file-lockstep applied to PR-R's new models (model +
      validator + tests + golden fixture in same commit)
- [ ] Dispatch-registry-as-manifest-companion (PR-R's dispatch registry
      ships alongside `PipelineManifest`, not as a separate top-level config)
- [ ] L1-validator-as-library-function (PR-R's L1 validator exposed as
      callable, not only CLI)
- [ ] Receipt-shape sanctum-fingerprint (receipts carry
      `SanctumFingerprint` for NFR-X3 reproducibility)

FR60 forward-port freeze **was** ACTIVE from Slab 1 Story 1.1a closure until
2026-04-24. **FR60 is now RETIRED** and replaced by the severance clause at
§8.1 below. Retained here as historical policy record only.

### 8.1 Upstream Severance (Slab 2+)

**Adopted:** 2026-04-24 session, per operator directive. **Scope:** all Slab
2+ work.

**Rule:** the hybrid clone is **severed** from `upstream/master` as a live
input source. All Slab 2 specialist migrations read skill directories from
**hybrid's own working tree** (the dev branch), not from any upstream SHA.
The `upstream` remote is retained as a historical-reference-only endpoint
(`git log upstream/master` lookups are allowed; fetch + read into code is
not).

**Why severance rather than a pin protocol:** an earlier draft of this
section proposed a pinned-SHA protocol with per-story escape hatches and an
M5 reconciliation pass. That was sized for a world where upstream keeps
evolving during migration. Per 2026-04-24 operator directive, upstream is
effectively deprecated for APP development starting now — trial-run
refinements and feature enhancements all happen on hybrid post-M5. A
severance posture is strictly simpler and has identical functional
outcomes once the operator commits to "sprint to hybrid operational."

**Mechanics:**

1. **Final absorption (one-time, 2026-04-24).** The 4 upstream commits that
   landed between the FR60 freeze (`a905de0`, 2026-04-22) and severance
   (`3ed7c56`, 2026-04-24) contained net-new specialist capability (Wondercraft
   first-breath scaffold, Texas Notion/Box/Consensus providers, Irene
   Pass-2 templates, Marcus dispatch-registry) and were absorbed via
   scoped `git checkout` of specialist directories onto hybrid. Audit
   trail at
   [`_bmad-output/implementation-artifacts/upstream-severance-log.md`](../../_bmad-output/implementation-artifacts/upstream-severance-log.md).
2. **Severance cutoff (2026-04-24).** After absorption, no further `git
   show upstream/master:…`, no further `git fetch upstream` driven by
   migration work. Slab 2 2b.N T1 reads go against hybrid's working-tree
   skill directories directly.
3. **No M5 reconciliation pass.** There is nothing to reconcile — upstream
   is no longer an input surface.

**FR60 posture supersession.** FR60 "forward-port freeze" is retired and
replaced by this severance clause. The freeze permitted convergence via
§8 checklist; severance does not. If a post-severance incident surfaces
that genuinely requires re-opening the upstream channel (e.g.,
operator-initiated emergency absorption), treat it as a party-mode
governance exception with full documentation, not as a standing escape
hatch.

**See also:**
- [`upstream-severance-log.md`](../../_bmad-output/implementation-artifacts/upstream-severance-log.md)
  — absorption-and-severance audit trail
- [`slab-2-roster-reconciliation.md`](../../_bmad-output/planning-artifacts/slab-2-roster-reconciliation.md)
  — reconciled Slab 2 migratable roster (actual skill dirs vs. named-only
  roadmap entries, updated to reflect absorbed Wondercraft specialist)

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

> **⏳ STUB — Slab 4 Story 4.5 completes this section.** Slab 1 shipped the
> directory structure only (see below). The full ceremony (manifest snapshot
> byte-capture + dispatch-registry snapshot + compiled-graph SHA-256 digest
> + ship-time governance ritual) is authored at Slab 4.5. Do NOT implement
> a ceremony under pre-Slab-4.5 authority; if Slab 2+ work needs to snapshot
> a graph version, open a 4.5-forward-port story rather than extending this
> section inline.

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

> **Section type: INTENTIONAL POINTER.** This section is deliberately
> pointer-only (not a stub) — the actual catalog and cookbook content lives
> in the linked standalone docs where it can grow authoritative-in-place.
> Adding inline content here would duplicate + drift from the pointed-to
> files. Pattern matches §7 (pointer to `model-selection-guide.md`).

Pointers:

- [`specialist-anti-patterns.md`](specialist-anti-patterns.md) — living catalog
  of anti-patterns (Slab 1 seeded with 3 confirmed + ~5 primary-repo
  inherited entries; four-field format frozen)
- [`local-postgres-setup.md`](local-postgres-setup.md) — Postgres bootstrap
  + retention cookbook
- [`langgraph-runtime-setup.md`](langgraph-runtime-setup.md) — troubleshooting
  section with the two Slab-1-burned blockers (`docker` / `psql` on PATH)
  resolved via the `project_no_docker` + `verify-via-shipped-deps` memory
  entries
- [`gate-decision-binding-semantics.md`](gate-decision-binding-semantics.md) —
  Slab 2+ gate_decision node binding convention (import-but-not-invoke
  until Slab 3 Story 3.3 + LLM-live skip-fixture)

Per-environment troubleshooting lives in `langgraph-runtime-setup.md §Troubleshooting`.

---

## 12. Specialist Walkthrough

This section is the canonical operator/dev-agent flow for creating a new Slab-2+
specialist through `bmad-create-specialist`.

### 12.1 Five-step spine

1. `git pull` (or update your local branch to latest story base).
2. Run generator skill command.
3. Inspect generated file tree.
4. Run scaffold conformance + generated state-shape tests.
5. Complete manual post-edit checklist.

### 12.2 Invocation

The generator can be invoked via either of two equivalent forms — pick the one that matches your environment. **Both are first-class** per the DR-1 spec-yields-to-code rule (party-mode-ratified 2026-04-24).

**Form A — `uv` runner** (when `uv` is installed and on PATH):

```bash
uv run python -m skills.bmad_create_specialist.scripts.generate \
  --name irene \
  --mcp none \
  --expertise-tier L5-narration-pass-2 \
  --from-skill skills/bmad-agent-content-creator/
```

**Form B — venv-direct** (when `uv` is not on PATH):

```bash
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name irene \
  --mcp none \
  --expertise-tier L5-narration-pass-2 \
  --from-skill skills/bmad-agent-content-creator/
```

(Use `.venv/bin/python -m ...` on POSIX.) Flags match Form A exactly. The dev agent records which form was used in T1 Readiness for grep-able audit; no spec rewrite needed.

Optional dry-run probe (no writes — append `--dry-run` to either form):

```bash
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name irene \
  --mcp none \
  --expertise-tier L5-narration-pass-2 \
  --from-skill skills/bmad-agent-content-creator/ \
  --dry-run
```

### 12.3 Expected generated tree

```text
app/specialists/irene/
  __init__.py
  graph.py
  state.py
  model_config.yaml
  expertise/README.md
tests/specialists/irene/test_irene_state_shape.py
tests/fixtures/specialists/irene/golden_envelope.json
tests/fixtures/specialists/irene/golden_return.json
tests/integration/scaffold_conformance/test_scaffold_irene.py
```

### 12.4 Manual post-edit checklist (frozen)

1. Set `app/specialists/<name>/model_config.yaml::default_model` to a valid
   ID from `app/models/registry.yaml::entries[].model_id` (e.g., `gpt-5.4`,
   `gpt-5-haiku`, `gpt-5-codex`). Document the tier mapping rationale in inline
   comments — see [`specialist-anti-patterns.md` A10](./specialist-anti-patterns.md)
   for the epic-doc-vs-registry drift trap to avoid.
2. Populate `app/specialists/<name>/expertise/` with domain references and
   update `expertise/README.md` with an index per the
   [sanctum-reference conventions](./sanctum-reference-conventions.md).
3. **(formerly step 3 — auto-emitted as of Story 2a.5; the generator atomically appends `app.specialists.<name>.graph -> app.gates.resume_api` to `pyproject.toml`'s C3 `ignore_imports` list with a generated comment marker. Idempotent. No manual edit needed.)**
4. Replace default `act` passthrough body only when the story explicitly
   requires a real LLM invocation; otherwise keep passthrough intentionally.
   When you do replace it, **bound the act-body** to prompt-assembly + LLM
   dispatch + parse — NO procedural logic in Python (the LLM does the
   procedural work per the specialist's reference set).
5. Update graph/state reducers only if the specialist introduces custom state
   fields beyond `SpecialistEnvelope` / `SpecialistReturn`.

**Sanctum-state convention** (per [sanctum-reference-conventions.md §3](./sanctum-reference-conventions.md)):

- **Activation epoch** (Story 2a.2 only — empty sanctum for FR54 baseline measurement)
- **Steady-state epoch** (Story 2a.3 onward — populated-and-locked sanctum)

Operator runs first-breath ceremony BEFORE `bmad-dev-story` opens for steady-state stories; lock for the AC-D 10-invocation cache window.

> **§12.5–§12.11 cover four specialist-shape categories proven across Slab 2a–2b.1 (narration / LLM+tool-dispatch / pure-tool-dispatch / REST-API tool-dispatch). Pure inheritors are catalogued at §12.12; add a new §12.x only when a specialist introduces a new act-body category.**

### 12.5 Irene worked before/after (act node) — real-Irene example, post-2a.2 close

Story 2a.2 was the first **real LLM-invoking specialist migration** + the FR54 cache-hit-rate baseline activation point. The before/after below reflects what actually shipped, not a hypothetical sketch.

**Before** (generator-emitted scaffold — same shape for every Slab-2+ specialist):

```python
def _act(state: RunState) -> dict[str, Any]:
    """Canonical act slot; replace in specialist follow-up stories."""
    del state
    return {}
```

**After** (Irene Pass-2 act node, AC-B bounded ~150 LOC ceiling, `_act` itself is 64 LOC; full source at [`app/specialists/irene/graph.py`](../../app/specialists/irene/graph.py)):

```python
def _act(state: RunState) -> dict[str, Any]:
    """Pass-2 narration LLM invocation (bounded ~150 LOC across helpers — AC-B + MF4)."""
    if not state.model_resolution_trail:
        raise RuntimeError("act node invoked before plan; resolution trail empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "act node read trail entry without cache_prefix_hash; expected "
            "the final cascade resolution from `_plan` ..."
        )
    handle = make_chat_model(
        specialist_id="irene",
        temperature=state.temperature,
        tier_request="reasoning",
        system_prompt_hash=last_entry.cache_prefix_hash or "",
    )
    envelope_payload: dict[str, Any] = {}
    if state.cache_state is not None and state.cache_state.cache_prefix:
        try:
            envelope_payload = json.loads(state.cache_state.cache_prefix)
        except json.JSONDecodeError:
            envelope_payload = {}
    system_msg, user_msg = _assemble_pass_2_prompt(envelope_payload)
    response = handle.chat.invoke(
        [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
    )
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    parsed = _parse_pass_2_response(raw_text)
    output_blob = json.dumps(
        {
            "narration_script": parsed["narration_script"],
            "segment_manifest_deltas": parsed["segment_manifest_deltas"],
            "model_id": last_entry.resolved,
            "usage": getattr(response, "usage_metadata", None),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }
```

Notable design properties from the Story 2a.2 party-mode rounds (2026-04-24):

- **Helpers in graph.py** — `_read_sanctum_digest`, `_read_pass_2_references`, `_assemble_pass_2_prompt`, `_parse_pass_2_response`. All deterministic; no datetime/UUID/random in prompt body. Sorted by `as_posix()` for cross-platform stability; `json.dumps(..., sort_keys=True, ensure_ascii=True, separators=(",",":"))` for byte-identical envelope payloads (Murat MF3 binding).
- **Cache-prefix continuity** — `_act` reconstructs the chat handle with `system_prompt_hash=last_entry.cache_prefix_hash` from the `_plan` resolution trail entry. Defensive `RuntimeError` raises if `_plan` did not run, or if the last entry lacks a `cache_prefix_hash` (Winston discriminator-check binding).
- **Envelope-carrier-hack** — `state.cache_state.cache_prefix` is overloaded as a JSON-encoded payload carrier because RunState has no first-class envelope field at Slab 1. Slab 3 retires this hack via the deferred-inventory follow-on entry "Replace cache_prefix payload-carrier hack with first-class RunState envelope field."

**Where 2a.2 diverged from the hypothetical Irene plan:**

| Area | Hypothetical (pre-2a.2) | Reality (post-2a.2) |
|---|---|---|
| Output sink | `state.story_states` append | `state.cache_state.cache_prefix` JSON blob (envelope-carrier-hack receipt) |
| Prompt assembly | inline string concat | `_assemble_pass_2_prompt()` helper with sorted-keys JSON + sorted file listing |
| Sanctum read | implicit (assumed populated) | `_read_sanctum_digest()` deterministic empty-or-listed pattern (D2 SYNTHESIS: empty for 2a.2) |
| Model cascade | `gpt-4.1` per epic | `gpt-5.4` per registry (anti-pattern A10 drift) |
| Sanctum path | `_bmad/memory/bmad-agent-irene/` per epic | `_bmad/memory/bmad-agent-content-creator/` per BMB convention (anti-pattern A11) |

### 12.6 Kira worked before/after (act node) — real-Kira tool-dispatch example, post-2a.3 close

Where Irene at 2a.2 proved the **pure-LLM act-body** category, Story 2a.3 proves the **tool-dispatch act-body** category — Kira composes a Kling motion-generation instruction package via a single LLM call, then dispatches to the existing `kling-video` skill via a thin mockable wrapper. The 9-node scaffold survives the divergence; the populated-and-locked sanctum epoch is exercised end-to-end; the `motion_asset_path` field on `KiraReturn` is wired so Storyboard B's motion contract continues to work.

**Generator invocation (DR-1 venv-direct form):**

```
.venv\Scripts\python.exe -m skills.bmad_create_specialist.scripts.generate \
  --name kira --mcp kling --expertise-tier L4-video-direction \
  --from-skill skills/bmad-agent-kling
```

**Generated tree (Codex landing 2026-04-25, post-G6 patches):**

```
app/specialists/kira/
├── __init__.py
├── graph.py                # 9-node StateGraph; _act + 4 helpers + kling_dispatch invocation
├── kling_dispatch.py       # Thin mockable wrapper around skills/kling-video/scripts/run_motion_generation.py
├── state.py                # KiraEnvelope + KiraReturn (with motion_asset_path: str | None field)
├── model_config.yaml       # default_model: gpt-5-haiku; temperature_default: 0.0
└── expertise/
    └── README.md           # 6-row dotted reference table
```

**Key act-body shape (`graph.py::_act`, post-G6 patches):**

```python
def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("kira act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError("kira act expected final plan resolution entry with cache_prefix_hash")
    handle = make_chat_model(
        specialist_id="kira",
        temperature=state.temperature,
        tier_request="fast",
        system_prompt_hash=last_entry.cache_prefix_hash,
    )
    envelope_payload: dict[str, Any] = {}
    if state.cache_state is not None and state.cache_state.cache_prefix:
        try:
            decoded = json.loads(state.cache_state.cache_prefix)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, dict):
            envelope_payload = decoded
    system_message, user_message = _assemble_kira_prompt(envelope_payload)
    response = handle.chat.invoke([
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ])
    raw_text = response.content if isinstance(response.content, str) else str(response.content)
    llm_payload = _extract_kling_response(raw_text)
    dispatch_receipt = dispatch_to_kling(
        kling_prompt=llm_payload["kling_prompt"],
        model_name=llm_payload["model_name"],
        mode=llm_payload["mode"],
        duration=llm_payload["duration"],
        negative_prompt=llm_payload["negative_prompt"],
        motion_plan_path=envelope_payload.get("motion_plan_path"),
        slide_id=envelope_payload.get("slide_id"),
    )
    output_blob = json.dumps({
        "kling_prompt": llm_payload["kling_prompt"],
        "kling_choices": dispatch_receipt["kling_choices"],
        "motion_asset_path": dispatch_receipt["motion_asset_path"],
        "visual_file": envelope_payload.get("visual_file"),  # AC-L: PRESERVED unmutated
        "model_id": last_entry.resolved,
        "usage": getattr(response, "usage_metadata", None),
    }, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)
    return {"cache_state": {"cache_prefix": output_blob, "entries_count": ...}}
```

When you migrate the next specialist, expect divergences in **these eight categories**; if your specialist has a divergence outside these categories, that's a signal to update §12 itself.

**Divergences from Irene (2a.2)**

| Aspect | Irene 2a.2 (narration) | Kira 2a.3 (motion-direction) |
|---|---|---|
| Act-body category | Pure-LLM authoring | LLM-prompt-composition + tool-dispatch |
| External call after LLM | NONE — narration script returned directly | `dispatch_to_kling(...)` — mockable wrapper around `skills/kling-video/scripts/run_motion_generation.py` |
| Model tier | `tier_request: reasoning` → `gpt-5.4` | `tier_request: fast` → `gpt-5-haiku` (cheapest model that meets video-direction need per Kira's cost-aware principle) |
| Temperature | `0.3` (narration creativity) | `0.0` (structured selection JSON; cache-prefix determinism) |
| Sanctum epoch | Empty for duration (2a.2 D2 SYNTHESIS) — activation-baseline measurement | **Populated-and-locked** (steady-state from 2a.3 onward; `sanctum_context_cost = steady_state_tokens − baseline_tokens`) |
| Return shape addition | None (inherits parent `SpecialistReturn`) | `motion_asset_path: str \| None` field added on `KiraReturn` per AC-L Storyboard B |
| Live dimension | LLM-only | LLM (live-LLM-marked) + Kling API (operator-gated AC-B-OP only; never invoked by dev-agent) |
| Wrapper module | None | `kling_dispatch.py` — fixture-MP4 short-circuit when `motion_plan_path` or `slide_id` is falsy; live runner load-on-demand otherwise |

**Drifts caught at T1 (anti-pattern #3 standing protocol)**

| Drift | Epic 2a.3 text | Reality | Resolution | Harvest disposition |
|---|---|---|---|---|
| Node name "reason node" | line 620 | canonical `plan` per `SCAFFOLD_NODE_IDS` | Follow framework | A9 third example (augment) |
| Model tier "multimodal" + default `gpt-4o` | lines 619–621 | tiers are `reasoning/fast/code`; registry has `gpt-5.4/5-haiku/5-codex`; Kira maps to `tier_request: fast` → `gpt-5-haiku` | Follow framework | A10 second example (augment) |
| Sanctum path | NONE — epic correctly references `skills/bmad-agent-kling/` | matches hybrid skill-dir name | No drift | No harvest |

**G6 review patches applied at story close**

- `_act` json.loads wrapped in try/except (Irene-parity regression fix)
- `_assemble_kira_prompt` json.dumps gained `default=str` for Path/datetime envelope payloads
- `_read_sanctum_digest` normalizes `\r\n → \n` before hashing (cross-platform cache-prefix determinism)
- `_extract_kling_response` narrowed `except Exception` to `except json.JSONDecodeError` + non-dict-top-level RuntimeError (production failure paths now testable)
- `dispatch_to_kling` truthy-guard (`not motion_plan_path or not slide_id`) replaces `is None` check (closes empty-string billing-risk)
- `expertise/README.md` populated with 6-row dotted reference table; `test_kira_expertise_readme_lists_l4_references` test pin added
- `test_cache_hit_rate_kira_populated.py` skips on empty/absent sanctum (no vacuous populated-sanctum claim)

**Verification commands:**

```bash
python -m pytest tests/specialists/kira -q
python -m pytest tests/integration/scaffold_conformance/test_scaffold_kira.py -q
python -m pytest tests/end_to_end/test_cache_hit_rate_kira_populated.py -q
```

### 12.7 Texas worked before/after (act node) — real-Texas pure-tool-dispatch example, post-2a.4 close

Story 2a.4 adds the third and final Slab-2a act-body category: Texas `_act` never calls an LLM. It dispatches to the wrangler runner through a mockable subprocess seam, parses `result.yaml` + `extraction-report.yaml`, classifies the outcome on the `bundle.parsed.*` namespace, and returns canonical bundle metadata in `cache_state.cache_prefix`.

```python
def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("texas act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "texas act expected final plan resolution entry with cache_prefix_hash"
        )
    # Fail-loud guard: malformed cache_state.cache_prefix must NOT silently
    # short-circuit into the dev-mode fixture bundle. Slab-3 retires the
    # envelope-carrier-hack via a first-class RunState envelope field.
    envelope_payload = _decode_envelope_payload(state)
    dispatch_receipt = dispatch_retrieval(
        directive_path=envelope_payload.get("directive_path"),
        bundle_dir=envelope_payload.get("bundle_dir"),
    )
    bundle_path = dispatch_receipt.get("bundle_dir")
    if not bundle_path:
        raise BundleDispatchError(
            "texas dispatch receipt missing bundle_dir",
            tag="bundle.parsed.missing-key",
        )
    bundle_dir = Path(str(bundle_path))
    exit_code = int(dispatch_receipt.get("exit_code") or 0)
    if exit_code == 30:
        raise BundleDispatchError(
            "texas wrangler reported hard error (exit 30); bundle not trusted",
            tag="bundle.parsed.exit-30",
        )
    if exit_code not in (0, 10):
        raise BundleDispatchError(
            f"texas wrangler returned unexpected exit code {exit_code}",
            tag="bundle.parsed.unknown-exit",
        )
    if exit_code == 10:
        # Graceful degrade: wrangler ran cleanly but found no results.
        trail_entry = _new_dispatch_trail_entry(last_entry, tag="bundle.parsed.exit-10")
        ...  # emit no-results output_blob; append trail_entry; bump entries_count
    try:
        parsed = _load_bundle_outputs(bundle_dir)  # raises BundleParseError(tag=...)
    except BundleParseError as exc:
        # Mutate trail in-place so two-sided assertion (exception side AND
        # state side) sees the parse-failure tag — Murat M5 binding.
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "bundle_reference": str(bundle_dir),
            "status": parsed["status"],
            "overall_status": parsed["overall_status"],
            "artifacts": parsed["result"].get("artifacts", []),
            "report_schema_version": parsed["report"].get("schema_version"),
            "dispatch_exit_code": exit_code,
            "model_id": last_entry.resolved,
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (
                state.cache_state.entries_count + 1
                if state.cache_state is not None
                else 1
            ),
        },
    }
```

Texas-specific notes:
- Model cascade still resolves at `_plan` (`tier_request: fast` -> `gpt-5-haiku`) for FR16 trail consistency, but chat is not invoked.
- Sanctum exercise is the first real populated-and-locked case (`_bmad/memory/bmad-agent-texas/` lock baseline; 17-file sha256 manifest pinned as a module-level constant).
- NFR-I5 is pinned with sha256 on `skills/bmad-agent-texas/references/retrieval-contract.md`.
- Bundle-parse outcomes flow into the resolution trail under the `bundle.parsed.*` namespace (`ok` / `missing-key` / `malformed` / `wrong-type` / `empty` / `exit-10` / `exit-30` / `unknown-exit`). Tests assert two-sidedly: the parser's shape AND the trail tag — see `tests/specialists/texas/test_texas_act_node_dispatch.py` for the parametrize. Operators reading `model_resolution_trail` after a Texas run can distinguish "tool failed" from "tool succeeded with empty result" without inspecting the bundle directly.

### 12.11 Gary worked before/after (act node) — real-Gary REST-API tool-dispatch example, post-2b.1 close

Story 2b.1 introduces the fourth category: Gary `_act` is **REST-API tool-dispatch with no LLM invocation** at the specialist layer. `_plan` still resolves the model to preserve FR16 trail-shape consistency.

```python
def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("gary act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "gary act expected final plan resolution entry with cache_prefix_hash"
        )

    envelope_payload = _decode_envelope_payload(state)
    try:
        dispatch_receipt = dispatch_to_gamma(
            directive_path=envelope_payload.get("directive_path"),
            export_dir=envelope_payload.get("export_dir"),
        )
        parsed = _parse_dispatch_receipt(dispatch_receipt)
    except (GammaDispatchError, ReceiptParseError) as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "generation_id": parsed["generation_id"],
            "status": parsed["status"],
            "gary_slide_output": parsed["gary_slide_output"],
            "export_path": parsed.get("export_path"),
            "model_id": last_entry.resolved,
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return {"model_resolution_trail": [..., trail_entry], "cache_state": {...}}
```

**Divergences from Texas (§12.7):**

| Aspect | Texas pure-tool-dispatch | Gary REST-API tool-dispatch |
|---|---|---|
| Dispatch seam | subprocess wrapper (`dispatch_retrieval`) | in-process wrapper (`dispatch_to_gamma`) |
| Loader mechanism | direct Python module import under same package tree | direct package import from `skills.gamma_api_mastery.scripts.gamma_operations` |
| Error classification | `bundle.parsed.*` | `receipt.parsed.*` |
| Parse matrix | 7 cases (`ok/missing-key/malformed/wrong-type/empty/exit-10/exit-30/unknown-exit`) | 8 cases (`ok/missing-key/malformed/wrong-type/empty/export-failure/timeout/api-error`) |
| Sanctum case | populated-and-locked baseline | empty-dir/absent digest (`""`) at story close |
| Return extension | `bundle_reference` | `gary_slide_output` |

Tag namespace convention is artifact-first: `bundle.parsed.*` (Texas), `receipt.parsed.*` (Gary), future categories follow the same noun-first pattern.

Inheritors of this category are catalogued at §12.12.

### 12.12 Inheritor catalog matrix

| Specialist | Parent §12.x | Seam divergence | Sanctum case | Harvest contributions | Story |
|---|---|---|---|---|---|
| Texas | §12.7 | Subprocess dispatch wrapper + bundle parser | Populated-and-locked | A9 + A12 + NFR-I5 pin | 2a.4 |
| Gary | §12.11 | REST-API dispatch wrapper + receipt parser | Empty-dir / absent | A10 (third) + A11 (second) | 2b.1 |

### 12.13 Verification commands (Irene + Kira + Texas + Gary)

```bash
python -m pytest tests/specialists/irene -q
python -m pytest tests/integration/scaffold_conformance/test_scaffold_irene.py -q
python -m pytest tests/specialists/kira -q
python -m pytest tests/integration/scaffold_conformance/test_scaffold_kira.py -q
python -m pytest tests/specialists/texas tests/agents/bmad-agent-texas tests/contracts/test_texas_row_fungibility.py -q
python -m pytest tests/integration/scaffold_conformance/test_scaffold_texas.py -q
python -m pytest tests/specialists/gary -q
python -m pytest tests/integration/scaffold_conformance/test_scaffold_gary.py -q
```

### 12.14 Governance notes

- Generator denylist blocks Category D dissolved skills (`audra`, `cora`).
- If epic-doc text conflicts with scaffold framework contracts, framework wins
  (see scaffold T1 pre-flight protocol).
- `gate_decision` node template imports `resume_from_verdict` for C3 binding
  stability while using `interrupt()` body until Slab 3 implements resume API.

Cross-references:
- [`scaffold-conformance-framework.md`](scaffold-conformance-framework.md)
- [`specialist-anti-patterns.md`](specialist-anti-patterns.md)
- [`model-selection-guide.md`](model-selection-guide.md)

### 12.10 Slab 2a retrospective summary

Slab 2a closed with three specialist categories validated on the same 9-node scaffold: Irene (pure LLM), Kira (LLM + tool dispatch), and Texas (pure tool dispatch). This confirms scaffold survivability across divergent act-body implementations while preserving Slab-1 invariants. The strongest systemic lesson was A12 procedural coupling: three manual `pyproject.toml` C3 ignore-import edits across 2a.2/2a.3/2a.4. Sanctum protocol matured from baseline to steady state: 2a.2 measured empty-sanctum FR54 baseline, 2a.3 carried populated scaffolding with graceful degrade, and 2a.4 executed the first real populated-and-locked integrity check.

**FR54 doesn't generalize to all specialist categories.** Cache-hit-rate is narration-bound — pure-tool-dispatch specialists like Texas have no LLM prefix to cache, so the FR54 measurement category is undefined at the Texas layer (the FR54 substrate is intact and the harness stays gated; it just doesn't fire on pure-tool-dispatch). The pure-tool-dispatch substitute metric per Murat M4 is **`subprocess-dispatch-latency stability`** — the wall-clock distribution from `_act` entry to bundle-parse complete. Baseline at 2a.4 close (placeholder-key path, mocked dispatch wrapper short-circuit, single-machine warm cache): typical `_act` body completes in ≪50 ms (sub-millisecond YAML/JSON parse + dispatch-wrapper fixture short-circuit; no subprocess fork in the placeholder-key path). The live-wire baseline is owed once AC-B-OP reactivates at Slab-3 via the marcus.dispatch.contract forward-port; future Texas changes that regress p95 by >20% trigger a perf-review checkpoint. This metric feeds Slab 2b TEMPLATE design directly.

Section 12 is now structurally complete as a migration reference library for Slab 2b inheritance, with examples for narration, tool-composed motion, and retrieval subprocess dispatch. **For the full retrospective see [`_bmad-output/implementation-artifacts/slab-2a-retrospective.md`](../../_bmad-output/implementation-artifacts/slab-2a-retrospective.md); Slab 2b opens once the A12 generator auto-emit follow-on lands** (the one structural debt Slab 2a chose not to pay down before closing).

---

## Changelog

| Version | Date | Changes | Slab |
|---|---|---|---|
| v1   | 2026-04-23 | Initial 11-section skeleton authored at Story 1.7 close. | Slab 1 close |
| v1.1 | 2026-04-24 | Added §8.1 Upstream Severance (replaces FR60 forward-port freeze); STUB markers on §10 + new §12 Specialist Walkthrough placeholder; historical note on §8 + "intentional pointer" designation on §11 + "you-are-here" dev-guide cross-references landing on sibling docs. Party-mode round 3 Paige caveats. | Slab 1 close (rider hardening) |
| v1.2 | 2026-04-25 | Added §12.7 Texas pure-tool-dispatch worked example; renumbered §12.7/§12.8 -> §12.8/§12.9; added §12.10 Slab 2a retrospective summary and cross-suite verification command set. | Slab 2a close |
| v1.3 | 2026-04-25 | Added §12.11 Gary REST-API worked example + §12.12 inheritor matrix; tag-namespace noun convention (`receipt.parsed.*`); renumbered verification/governance to §12.13/§12.14 and added Gary verification commands. | Slab 2b.1 |
