# Migration Story 4.2: Cora Dev-Graph + Separate Thread Namespace

**Status:** ready-for-dev
**Sprint key:** `migration-4-2-cora-dev-graph-and-thread-namespace`
**Epic:** Slab 4 — Lockstep + Gates + Cora + Ledger + Frozen-Graph; M4 gate.
**Pts:** 5 | **Gate:** dual (per governance JSON `4-2.expected_gate_mode = "dual-gate"`, rationale: `lane_or_package_boundary`). **K-target:** ~1.4× (target 14 / floor 10).

**Predecessor:** 4.1 done (compile_dev_graph callable surface inherited; 4.2 implements it). Drafted-for-queue.

---

## T1 Readiness Block

### Standing Pre-Flight items

1. Governance: `4-2.expected_gate_mode = "dual-gate"` (rationale: `lane_or_package_boundary`).
2. **Substrate truth: `app/cora/` does NOT exist** at hybrid (verify; epic 4.2 says "empty at Slab 4 open"). Also verify `state/config/dev-graph-manifest.yaml` does NOT exist.
3. **Cora skill substrate** — `skills/bmad-agent-cora/scripts/preclosure_hook.py` per `docs/dev-guide/pipeline-manifest-regime.md:28`. Existing block-mode hook gets elevated to a node in the Cora dev-graph per epic AC.
4. Architecture FR40 lane separation; invariant #15 (dev-lane vs run-lane separation).
5. Marcus runtime canonical at `marcus/` (per Slab-3 substrate-aware adaptation); Cora MUST NOT import from marcus.* (architectural enforcement via import-linter).
6. RunState canonical at `app/models/state/run_state.py`; StoryState at `app/models/state/story_state.py` (verified per 3.5 cascade). Cora's dev-graph state likely consumes `StoryState` (story-cycle as graph).
7. Severance posture.

### Slab 4.2 artifact-existence sweep

- A `app/cora/` does NOT exist; T1 verifies.
- B `state/config/dev-graph-manifest.yaml` does NOT exist.
- C `app/models/state/story_state.py` exists per Slab-1+Slab-3 substrate (rich story-state for Cora consumption).
- D `skills/bmad-agent-cora/scripts/preclosure_hook.py` exists per Epic 33 substrate.
- E `compile_dev_graph` callable per 4.1 (verify shipped).

### Epic-doc-vs-architecture cross-check

(a) **Drift:** epic 4.2 references `app/cora/graph.py` + handlers (plan_story, implement_story, test_story, review_story, close_story) + `dev-graph-manifest.yaml`. Verify against Cora skill at `skills/bmad-agent-cora/` for any pre-existing handler logic that lifts to the graph. (b) **Decisions** below.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/cora/{__init__, graph}.py` + handlers `{plan_story, implement_story, test_story, review_story, close_story}.py`; (b) `state/config/dev-graph-manifest.yaml` per Slab-1 manifest precedent shape (NOT pipeline-manifest.yaml shape — separate dev-graph manifest); (c) Cora's `block_mode_hook.py` lifted from skill substrate (preclosure_hook.py) into the Cora graph as a node; (d) thread namespace `dev/{story_id}` distinct from Marcus's `run/{trial_id}`; (e) import-linter contract `app.cora ⊥ app.marcus` (forbidden contract, both directions). NOT in scope: ledger (4.4); party-mode-as-interrupt (4.3); frozen-graph (4.5).

**Decision #2 — Thread namespace per FR40:** Cora's checkpoint thread namespace is `dev/{story_id}`; Marcus's is `run/{trial_id}`. Architectural separation prevents cross-namespace checkpoint pollution.

**Decision #3 — Cora ⊥ Marcus import-linter (BIDIRECTIONAL):** `app.cora.*` MUST NOT import `app.marcus.*` OR `marcus.*` (canonical). `app.marcus.*` MUST NOT import `app.cora.*`. Pre-commit + CI enforce.

**Decision #4 — Block-mode hook elevation:** existing `skills/bmad-agent-cora/scripts/preclosure_hook.py` runs as a NODE in the Cora dev-graph (NOT just as pre-commit hook). Surfaces violations as `GateError` at a dev-graph gate. Pre-commit hook continues to fire as the OUTER guard; in-graph node fires within story-cycle as the INNER guard.

---

## Story

As a **governance system running story-cycle as a graph per FR40**,
I want **`app/cora/` with its own manifest + sibling StateGraph compilation + separate thread namespace `dev/{story_id}` + Cora's block_mode_hook elevated to in-graph node + import-linter `app.cora ⊥ app.marcus` (bidirectional)**,
So that **FR40 lane separation is architecturally enforced + invariant #15 preserved + dev-cycle becomes a first-class graph alongside Marcus's run-graph**.

---

## Acceptance Criteria

### AC-4.2-A — `app/cora/` package + `graph.py` + 5 handlers

- **Given** `app/cora/` does NOT exist
- **When** the dev agent authors:
  ```
  app/cora/
  ├── __init__.py
  ├── graph.py                          # StateGraph compilation entry
  ├── handlers/
  │   ├── __init__.py
  │   ├── plan_story.py
  │   ├── implement_story.py
  │   ├── test_story.py
  │   ├── review_story.py
  │   └── close_story.py
  └── block_mode_node.py                # Decision #4 elevation of preclosure_hook to in-graph node
  ```
- **Then** `compile_dev_graph(dev_manifest)` successfully compiles; thread namespace is `dev/{story_id}`.
- **Test pin:** `tests/integration/cora/test_cora_graph_compiles.py` — 1 test asserting compile_dev_graph returns CompiledGraphHandle + thread namespace prefix matches `dev/`.

### AC-4.2-B — `state/config/dev-graph-manifest.yaml` per Slab-1 manifest shape

- **Given** dev-graph-manifest.yaml does NOT exist
- **When** the dev agent authors with shape `{schema_version, nodes: [{id, label, handler}], edges: [{from, to}], thread_namespace: "dev/{story_id}"}`
- **Then** manifest validates per a `DevGraphManifest` Pydantic v2 strict model (parallel to PipelineManifest); compile_dev_graph consumes it.
- **Test pins:** `tests/unit/cora/test_dev_graph_manifest_shape.py` — 2 tests (parametrize-collapsible to 1 K-floor): valid manifest parses + invalid manifest raises.

### AC-4.2-C — Import-linter `app.cora ⊥ app.marcus` BIDIRECTIONAL (DUAL-GATE gate-1)

- **Given** Slab 3 import-linter contracts at 7/7 KEPT (post-3.4 facade-reachability)
- **When** the dev agent extends `pyproject.toml [tool.importlinter]` with TWO new forbidden contracts:
  - `app.cora.*` forbids `app.marcus.*` AND top-level `marcus.*` (per Slab 3 canonical home)
  - `app.marcus.*` AND `marcus.*` forbid `app.cora.*`
- **Then** `lint-imports --config pyproject.toml` returns N/N KEPT (8/8 or 9/9 depending on Slab-3 close state); negative tests construct synthetic violations.
- **Test pin:** `tests/integration/cora/test_cora_marcus_import_linter_bidirectional.py` — 2 tests (one per direction).

### AC-4.2-D — Block-mode hook elevation per Decision #4

- **Given** `skills/bmad-agent-cora/scripts/preclosure_hook.py` exists
- **When** the dev agent authors `app/cora/block_mode_node.py` that wraps the preclosure_hook logic as a graph node
- **Then** dev-graph run exercises it; non-zero exit surfaces as `GateError` at a dev-graph gate; pre-commit hook continues firing as outer guard.
- **Test pin:** `tests/integration/cora/test_block_mode_node.py` — 2 tests: (a) clean PR diff → node passes; (b) drifted PR diff → GateError at gate.

### AC-4.2-E — Anti-pattern catalog harvest (per R6)

NO new entries expected.

### AC-4.2-F — TEMPLATE compliance

R1, R6, R8 honored.

### AC-4.2-G — D12 close protocol (DUAL-gate; lane_or_package_boundary; FIVE-line)

1. Invariant preservation: FR40 lane separation; invariant #15; thread namespace separation.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §"Cora Dev-Graph" added; documents bidirectional ⊥ enforcement.
4. TEMPLATE compliance: R1, R6, R8.
5. Dual-gate gate-2 (operator package-boundary review).

### AC-4.2-H — Sprint-status state-flips

At close: `migration-4-2-...: done`; epic stays `in-progress`.

---

## File Structure Requirements

### NEW files

```
app/cora/{__init__, graph, block_mode_node}.py + handlers/{__init__, plan_story, implement_story, test_story, review_story, close_story}.py
state/config/dev-graph-manifest.yaml
tests/integration/cora/{__init__, test_cora_graph_compiles, test_cora_marcus_import_linter_bidirectional, test_block_mode_node}.py
tests/unit/cora/{__init__, test_dev_graph_manifest_shape}.py
```

### MODIFIED files

- `pyproject.toml` — 2 NEW import-linter contracts per AC-C.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-H.

---

## Testing Requirements

**K-target ~1.4× (target 14 / floor 10).** AC-A:1 + AC-B:1 + AC-C:2 + AC-D:2 = **6 K-floor**. RIDER: AC-A adds `test_thread_namespace_distinct_from_marcus` (orthogonal property); AC-B adds `test_dev_graph_manifest_pydantic_strict` (shape-pin per 31-1 schema-shape precedent); AC-D adds `test_block_mode_node_logs_classify_change_window` (orthogonal property); AC-C adds `test_marcus_to_canonical_marcus_import_forbidden` (canonical-home enforcement) = **honest 10 K-floor**. Within band.

Sandbox-AC PASS (no live API; all import-linter + compile validation).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
