# Migration Story 1.4: Manifest-as-Graph-Config Loader + Compiler

**Status:** done
**Sprint key:** 1-4-manifest-loader-compiler
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — manifest is the source of truth for graph topology.
**Pts:** 5 | **Gate:** dual (schema-shape PipelineManifest + compile-time topology contract) | **K-target:** ~1.5×

## Story

As a **dev agent landing the manifest-as-graph-config substrate**,
I want **the full `PipelineManifest` Pydantic schema + `app.manifest.loader` + `app.manifest.compiler` that loads a YAML manifest, validates it against the schema + import-linter contracts + model_config.yaml lint rules (NFR-M2), and compiles it into one or two `StateGraph` instances (Marcus run-graph + optionally Cora dev-graph per D4 lane separation)**,
So that **D6 (manifest as graph topology source) is realized, FR8 is satisfied, FR25 model_config-at-compile-time is enforced, and downstream stories (1.6 manifest migration, 4.1 compile-time CI hook) have a real loader+compiler to extend**.

## Acceptance Criteria

All ACs dev-agent-executable. Schema-shape + compile-time-contract story; uses [schema-story scaffold](../../docs/dev-guide/scaffolds/schema-story/).

### AC-1.4-A — `PipelineManifest` schema (full shape, including v4.2 inventory)

- **Given** 1.1c shipped a stub manifest at `state/config/pipeline-manifest.yaml` (1-step no-op) and 1.6 will migrate the real v4.2 manifest; **per Winston/Amelia amendment 2026-04-22**, the v4.2 schema-delta inventory is performed at THIS story's T1, NOT deferred to 1.6's mid-implementation discovery
- **When** the dev agent:
  1. **At T1, before any schema implementation:** reads the primary repo's `state/config/pipeline-manifest.yaml` (v4.2 source) + the frozen v42 pack content via the pipeline-manifest-regime pointer chain. Inventories every field present. If the architecture-canonical field set below is missing any v4.2-required field (e.g., step ordinal, motion-mode metadata, cluster-arc anchors), the dev agent ESCALATES to party-mode amendment BEFORE schema implementation begins (NOT silently extends in 1.6 — that punt is what this amendment closes).
  2. Authors `app/manifest/schema.py` defining `PipelineManifest` Pydantic v2 with the full union of (a) the architecture-canonical field set + (b) v4.2 inventory deltas: `version: str`, `lane: Literal["run_graph", "dev_graph"]`, `nodes: list[NodeSpec]`, `edges: list[EdgeSpec]`, `entrypoint: str`, `frozen_graph_version: str` + any v4.2-required additions discovered at T1, with `NodeSpec` = `{id, specialist_id, scaffold_node, model_config_ref, ...}` and `EdgeSpec` = `{from, to, condition?, dispatch_envelope?, ...}`
- **Then** four-file-lockstep complete; the schema accommodates the entire v4.2 manifest at 1.4 close (1.6 will load it without surgery); the stub manifest from 1.1c is updated to satisfy the real schema; golden fixture covers a 3-node manifest with one conditional edge AND a v4.2-shaped fixture (subset of the 15-step manifest) demonstrating the v4.2 deltas resolve.

### AC-1.4-B — `app.manifest.loader`

- **Given** `state/config/pipeline-manifest.yaml` exists
- **When** the dev agent authors `app/manifest/loader.py` exporting `load(path: Path | str) -> PipelineManifest`
- **Then** loader uses `yaml.safe_load` + Pydantic validation; raises `ManifestValidationError` (subclass of `pydantic.ValidationError`) with named-violation path on bad input; exits gracefully on file-not-found with named exception.

### AC-1.4-C — `app.manifest.compiler`

- **Given** the loader produces a validated `PipelineManifest`
- **When** the dev agent authors `app/manifest/compiler.py` exporting `compile(manifest: PipelineManifest) -> StateGraph` that:
  - Instantiates a LangGraph `StateGraph` with state schema = `RunState` (from 1.2)
  - Adds each node from `manifest.nodes`, resolving `specialist_id` to a callable (1.4 uses a stub callable `lambda state: state` — full specialist resolution is Slab 2 scope)
  - Adds each edge per `EdgeSpec`; conditional edges use `add_conditional_edges`
  - Sets `entrypoint`
  - Validates frozen-graph-version exists at `runtime/graphs/v{version}/` (stub check; full ceremony at Slab 4 Story 4.5)
  - Validates each `model_config_ref` resolves against shipped `model_config.yaml` files (NFR-M2 / FR25 model_config-at-compile-time lint)
- **Then** compiler returns a compiled `StateGraph` ready for `.compile().invoke(...)`; lint failures surface as `CompileError` with named violation; `lint-imports` continues to pass on `app.manifest.*`.

### AC-1.4-D — Two-lane support (D4)

- **Given** D4 mandates Cora ⊥ Marcus lane separation as separate `StateGraph` compilation units
- **When** the dev agent confirms compiler accepts `lane: "run_graph"` (Marcus) and `lane: "dev_graph"` (Cora) and produces topology consistent with `app.marcus` ⊥ `app.cora` import-linter contract C1
- **Then** a unit test `tests/unit/manifest/test_lane_separation.py` instantiates a manifest with `lane: "run_graph"` and a manifest with `lane: "dev_graph"`, compiles both, and asserts the resulting `StateGraph` instances do not share node references; fails if a node bridges lanes.

### AC-1.4-E1 — `app/gates/resume_api.py` stub + import-linter contract C3 (architecture §D3, FR34 tamper-evidence)

- **Given** architecture §D3 places the gate-verdict substrate (`OperatorVerdict` model + `resume_api` module stub + import-linter contract + ledger verdict-event shape) in Slab 1; `OperatorVerdict` lands in Story 1.2; this story (1.4) lands the `resume_api` stub + the import-linter contract C3 because 1.4 is the compile-time-contract story
- **When** the dev agent authors:
  - `app/gates/resume_api.py` with named-exception-body stubs only: `def resume_from_verdict(verdict: OperatorVerdict) -> NoReturn: raise NotImplementedError("Slab 3 Story 3.3 wires the resume path")`. Keep the function signature stable (Slab 3 will replace the body, not the signature) so import-linter C3 has a real symbol to constrain.
  - `app/gates/__init__.py` (already exists from 1.1a as empty stub — extend to export `resume_api`)
  - `pyproject.toml` `[tool.importlinter]` section adds **Contract C3** with `type = "forbidden"`, `name = "app.gates.resume_api may only be imported by the three authorized verdict-bridge modules (D3 tamper-evidence)"`, `source_modules = ["app.gates.resume_api"]`, plus an inverse-style assertion via a new contract block of `type = "layers"` declaring `app.gates.resume_api` as a leaf with allowed importers limited to `app.mcp_server.tools.gate_decide`, `app.http.gate_endpoint`, `app.marcus.cli.gate_cli`. (NOTE: import-linter's `forbidden` type is one-directional caller-restriction; if `layers` doesn't fit, the dev agent uses `forbidden` from `app.runtime`, `app.specialists`, `app.cora`, `app.models`, `app.manifest` per the explicit non-caller list — pick the contract type that gives the right semantics; the architecture intent is "only the three named bridge modules may import `resume_api.resume_from_verdict`," and the implementation choice is dev-agent authority within that intent. None of the three bridge modules exist yet — they're created in Slab 3 — so C3 trivially passes at Slab 1 close, exactly like C1/C2 did at 1.1a.)
- **Then** `app/gates/resume_api.py` exists with the signature stub; `lint-imports --config pyproject.toml` continues to exit 0 (C1, C2, C3 all trivially pass against the still-mostly-empty Slab-1 tree); a test under `tests/unit/gates/test_resume_api_stub.py` asserts that calling `resume_from_verdict(any_valid_verdict)` raises `NotImplementedError` with the named-exception body, confirming the substrate is honestly stubbed (not silently dispatching).

### AC-1.4-E2 — Compile-time `model_config.yaml` lint pass (FR25 + NFR-M2)

- **Given** each specialist has a `model_config.yaml` (1.3 landed the schema; full per-specialist files arrive in Slab 2)
- **When** the compiler iterates the manifest's `nodes` and resolves each `model_config_ref`
- **Then** missing/malformed `model_config.yaml` raises `CompileError` with the offending node id; valid configs pass through; the lint pass runs at compile time, not at runtime — runtime invocation cannot be reached if compile lint failed.

### AC-1.4-F — End-to-end loader+compiler+invoke smoke

- **Given** AC-1.4-A through AC-1.4-E are green
- **When** the dev agent runs `pytest tests/integration/manifest/test_loader_compile_invoke.py` which loads the stub manifest, compiles, invokes one node, and asserts the output
- **Then** the test passes; the stub manifest from 1.1c continues to work after this story's schema tightening (no breaking change to 1.1c's smoke).

## Tasks / Subtasks

- [x] **T1 — Read T1 Bundle** §1 (D3 HIL tamper-evidence + Slab-1 substrate distribution; D4, D6, D8), §2 (FR8, FR25, FR31 verdict, FR34 no auto-approve, NFR-M2), §3 (Pydantic + LangGraph state idioms #2 reducer fields, #3 Command goto/update). T1 also includes verifying that 1.2 closed with `OperatorVerdict` model present (1.4 imports it for the `resume_from_verdict` signature stub per AC-1.4-E1).
- [x] **T2 — Use schema-story scaffold** for `PipelineManifest` + `NodeSpec` + `EdgeSpec`.
- [x] **T3 — Author schemas** per AC-1.4-A.
- [x] **T4 — Author loader** per AC-1.4-B.
- [x] **T4.5 — Author `app/gates/resume_api.py` stub + C3 contract + stub test** per AC-1.4-E1. Land BEFORE compiler implementation so C3 is in `pyproject.toml` when `lint-imports` runs at T8.
- [x] **T5 — Author compiler** per AC-1.4-C, AC-1.4-D, AC-1.4-E2 (single module, three responsibilities).
- [x] **T6 — Update 1.1c stub manifest** to satisfy the new schema (no behavioral change; just adds `version`, `lane`, etc.).
- [x] **T7 — End-to-end test** per AC-1.4-F.
- [x] **T8 — Run validators + tests.** Sandbox-AC validator + ruff + lint-imports + pytest.
- [x] **T9 — Commit.** `feat(migration): Slab 1 Story 1.4 — manifest-as-graph-config loader + compiler`

## Dev Notes

### Stub specialist callables in 1.4 — full resolution is Slab 2

1.4's compiler resolves `specialist_id` to a stub callable (`lambda state: state` or `passthrough_node`). Full specialist resolution (loading `app.specialists.{name}.graph` and instantiating the 9-node scaffold) is Epic 2a Story 2a.1 scope. **Do not pull in specialist instantiation here** — the compiler shape must accept any callable that conforms to the LangGraph node signature, and Slab 2 wires the real callables.

### `add_conditional_edges` vs `add_edge`

EdgeSpec with `condition` field → `add_conditional_edges`. Without → `add_edge`. The `condition` value is a callable name resolved at compile time from a registered condition-function registry (stub: just allow `"always_true"` and `"always_false"` in 1.4; full registry is Slab 3 dispatch territory).

### Frozen-graph-version stub check

Compiler asserts `runtime/graphs/v{version}/README.md` exists (this directory was created in 1.1b). Full ceremony (manifest snapshot, dispatch-registry snapshot, compiled-graph-digest) lands at Slab 4 Story 4.5. 1.4 does the existence check only.

### `RunState` is the state schema

LangGraph `StateGraph(state_schema=RunState)`. `RunState` from 1.2. If 1.2 + 1.3 cross-tightening hasn't fully landed, this story may need to coordinate timing — but per the dependency graph (1.2 → 1.3 → 1.4), this should be linear.

### Project Structure Notes

**New files:**
- `app/manifest/schema.py` (PipelineManifest, NodeSpec, EdgeSpec)
- `app/manifest/loader.py`
- `app/manifest/compiler.py`
- `app/manifest/exceptions.py` (ManifestValidationError, CompileError)
- `app/manifest/__init__.py`
- `app/gates/resume_api.py` (per AC-1.4-E1 — signature stub with named-exception body, NotImplementedError)
- Four-file-lockstep tests + fixtures for the three schemas
- `tests/unit/manifest/test_lane_separation.py`
- `tests/unit/gates/test_resume_api_stub.py` (per AC-1.4-E1)
- `tests/integration/manifest/test_loader_compile_invoke.py`

**Modified:**
- `state/config/pipeline-manifest.yaml` (stub from 1.1c — add `version`, `lane`, `frozen_graph_version`)
- `app/gates/__init__.py` (extend to export resume_api)
- `pyproject.toml` `[tool.importlinter]` section — add Contract C3 per AC-1.4-E1

## References

- Bundle: [Set-A T1 Context Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md)
- Architecture D3, D4, D6, D8
- PRD FR8, FR25, NFR-M2

## Dev Agent Record

### Model used

claude-opus-4-7 (1M context) — bmad-dev-story on 2026-04-23.

### T1 — v4.2 inventory (Winston/Amelia amendment 2026-04-22)

Primary-repo v4.2 manifest (`git show upstream/master:state/config/pipeline-manifest.yaml`, 379 lines) inventoried before any schema code. Field deltas vs architecture-canonical AC-1.4-A set:

**Top-level v4.2 fields that ride `PipelineManifest` as first-class:**
- `schema_version: str` (equivalent to architecture-canonical `version`; rename accepted)
- `pack_version: str` — new; prompt-pack identifier (`"v4.2"`, etc.), distinct from `frozen_graph_version` (LangGraph compiled-graph identity)
- `generator_ref: str | None` — new; generator script path (pipeline-manifest regime)
- `learning_events: LearningEventsConfig | None` — new; top-level `schema_ref` for learning-event substrate (Epic 33)
- `block_mode_trigger_paths: list[str]` — new; Epic 33 pipeline-manifest regime block-mode surface

**Per-step v4.2 fields that ride `NodeSpec` under AC-1.4-A's trailing `...` extensibility clause:**
- `label`, `gate`, `gate_code`, `sub_phase_of`, `insertion_after`, `hud_tracked`, `pack_section_anchor`, `pack_version`, `rationale`, nested `learning_events`

**Gaps flagged for 1.6 migration (NOT schema gaps — migration-time synthesis responsibilities):**
- v4.2 has no explicit `edges` list; topology is linear via per-step `insertion_after`. 1.6 will synthesize `EdgeSpec` list from `insertion_after` during manifest migration.
- v4.2 carries no `lane` / `entrypoint` / `frozen_graph_version` top-level; 1.6 will inject `lane: "run_graph"`, `entrypoint: "01"`, `frozen_graph_version: "v42"` at migration.
- v4.2 NodeSpec carries no `specialist_id` / `scaffold_node` / `model_config_ref`; 1.6 will add these per-step when mapping to specialists (Slab 2 wires the real callables).

**Inventory VERDICT: CLEAN.** All v4.2 fields fit within AC-1.4-A's explicit union formula. Party-mode amendment NOT required. Proceeding to T2-T5 schema authoring.

### T1 — `OperatorVerdict` verification

1.2's `app.models.state.operator_verdict.OperatorVerdict` confirmed present with the full FR34 triple-layer red-rejection shape (verb `Literal["approve", "edit", "reject"]` + `_check_invariants` model_validator + schema-pin emission). 1.4's `resume_api.resume_from_verdict` signature imports this type directly.

### Debug log

- **T6 refactor detail:** `app/smoke_test.py` updated to route manifest loading through `app.manifest.loader.load()` (the production entrypoint this story introduces). Local `_StubManifest` / `_StubManifestGraph` / `_StubManifestNode` / `_StubManifestEdge` Pydantic classes removed. `_SmokeState` TypedDict + direct `minimal_node` wiring preserved so the 1.1c payload contract (`{"smoke": "ok", "node": "noop"}`) lands byte-equivalent — the production compiler targets `RunState` + passthrough stubs which would change the stub smoke's payload shape if used here.
- **Contract C3 scope decision:** pyproject.toml's pre-existing C3 block scoped to `app.mcp_server` only; rewritten to list every non-bridge Slab-1 source package (`app.runtime/specialists/cora/models/manifest/mcp_server`) as forbidden-importers of `app.gates.resume_api` with a single ignore for `app.mcp_server.tools.gate_decide`. The two future bridge modules (`app.http.gate_endpoint`, `app.marcus.cli.gate_cli`) are documented in the contract comment; Slab 3 Story 3.3 adds their `ignore_imports` entries when the modules materialize (import-linter rejects unused ignores, so pre-seeding fails).
- **Stub-manifest schema migration:** `state/config/pipeline-manifest.yaml` rewritten from the 1.1c nested `graph.{nodes,edges}` shape to the flat `PipelineManifest` shape (top-level `nodes`/`edges` + `lane` + `entrypoint` + `frozen_graph_version`). Added `runtime/graphs/v0.1-stub/README.md` to anchor the compiler's frozen-graph-version directory-existence check.
- **G6-P1 patch:** compiler was adding an implicit `START → entrypoint` edge even when the manifest's edges list already declared an explicit `__start__ → entrypoint` edge. Fixed via `has_explicit_start_edge` guard. LangGraph's current version accepts the double-add, but semantic uniqueness is the contract. Two new regression tests: `test_compile_does_not_duplicate_start_edge_when_explicit` + `test_compile_adds_implicit_start_edge_when_absent`.

### Completion notes

**T8 validator sweep (post-G6-P1):**
- Sandbox-AC validator: **PASS** — zero violations in Story 1.4 spec.
- Ruff (app/ + 1.4 test files + pyproject.toml): **All checks passed!**
- Import-linter: **3/3 KEPT** — C1 (lane-isolation) + C2 (scheduler-forbidden on gates) + C3 (only bridge modules may import resume_api). 80 files / 180 dependencies analyzed.
- Pytest (1.4-scoped): **52/52 passing** in `tests/unit/manifest/` + `tests/unit/gates/` + `tests/integration/manifest/`.
- Pytest (migration-suite regression): **260 passed / 1 deselected** across `tests/unit/` + `tests/integration/manifest/runtime/models/sanctum/transport_parity/`. +52 new nodes from 1.4, zero regressions on 1.1a/1.1b/1.1c/1.1d/1.2/1.3 scope.
- 1.1c smoke contract preserved: `python -m app.smoke_test` prints `smoke ok (nodes=1, payload={'input': 'ping', 'smoke': 'ok', 'node': 'noop', 'echo': 'ping'})` byte-equivalent to 1.1c baseline.

**G6 layered code-review triage (self-conducted, 1.2/1.3 precedent):**
- **Blind Hunter** — 0 MUST-FIX + 1 SHOULD-FIX + minor style NITs. Applied: G6-P1 double-edge guard.
- **Edge Case Hunter** — 0 MUST-FIX + 0 SHOULD-FIX + 1 DEFER (G6-D1: NodeSpec.id accepts `__start__` / `__end__` sentinel strings — low practical risk, Slab 2 tightens when specialist_id resolution lands).
- **Acceptance Auditor** — all 7 ACs (A, B, C, D, E1, E2, F) covered by at least one test with assertions tight to the AC's Then-clause.
- **DUAL-GATE audit (ci_or_compile_shape):** compile-time topology contract + schema-shape parity both green. Schema-pin fixtures exist for all three schemas with bidirectional round-trip + `additionalProperties: false` + `extra="forbid"` propagation assertions.

Net: **1 PATCH applied (G6-P1), 1 DEFER (G6-D1), ~8 DISMISS** per aggressive G6 rubric (verbose error messages, pragma-on-OSError, `__name__` assignment on stub handlers).

**Unblocks:** Story 1.5 (checkpoint retention — single-gate, parallel-eligible), Story 1.6 (pipeline-manifest migration stub + smoke — consumes this schema directly), Story 2a.1 (Slab 2 specialist scaffold pilot — compiler's passthrough stub is the extension point for real specialist resolution), Story 3.3 (Slab 3 resume_api body + bridge modules honoring C3 signature).

### File list

**New files:**
- `app/manifest/schema.py` — PipelineManifest + NodeSpec + EdgeSpec + LearningEventsConfig + StepLearningEventsConfig
- `app/manifest/exceptions.py` — ManifestValidationError + CompileError
- `app/manifest/loader.py` — `load(path) -> PipelineManifest`
- `app/manifest/compiler.py` — `compile(manifest) -> StateGraph`
- `app/manifest/conditions.py` — Slab 1 stub condition registry (`always_true` / `always_false`)
- `runtime/graphs/v0.1-stub/README.md` — anchors `frozen_graph_version: "v0.1-stub"` directory-existence check
- `tests/unit/manifest/test_schema.py` — 20 shape + round-trip + cross-field + rejection tests
- `tests/unit/manifest/test_schema_pin.py` — 6 schema-pin parity tests (3 models × parametrize + 3 `additionalProperties: false` assertions)
- `tests/unit/manifest/test_loader.py` — 7 loader tests (happy path + 5 error paths + string-path acceptance)
- `tests/unit/manifest/test_compiler.py` — 10 compiler tests (compile + invoke + model_config_ref lint + conditions + frozen-graph-dir + G6-P1 double-edge guard)
- `tests/unit/manifest/test_lane_separation.py` — 3 lane-separation tests (AC-1.4-D)
- `tests/unit/gates/test_resume_api_stub.py` — 3 stub tests (NotImplementedError + echo + signature-stability)
- `tests/integration/manifest/test_loader_compile_invoke.py` — 3 e2e tests (compile+invoke + 1.1c smoke contract + CompileError surface)
- `tests/fixtures/manifest/schema_pin_pipeline_manifest.json` + `schema_pin_node_spec.json` + `schema_pin_edge_spec.json`
- `tests/fixtures/manifest/golden_pipeline_manifest_3node.json` + `golden_pipeline_manifest_v42_subset.json`

**Modified:**
- `app/manifest/__init__.py` — extended exports for the new schema + loader + compiler + exceptions
- `app/gates/__init__.py` — extended to re-export `resume_api`
- `app/gates/resume_api.py` — replaced scaffold docstring with signature-stable `resume_from_verdict(verdict: OperatorVerdict) -> NoReturn` raising named NotImplementedError
- `app/smoke_test.py` — routed manifest loading through `app.manifest.loader.load()`; removed local `_StubManifest` / `_StubManifestGraph` / `_StubManifestNode` / `_StubManifestEdge` classes; payload contract byte-equivalent
- `pyproject.toml` — rewrote Contract C3 block to list non-bridge source_modules explicitly with a single ignore for `gate_decide` (the only currently-extant bridge module)
- `state/config/pipeline-manifest.yaml` — flat `PipelineManifest` shape with `lane: run_graph` + `entrypoint: noop` + `frozen_graph_version: v0.1-stub` + `block_mode_trigger_paths` + v4.2 inventory deltas where relevant
- `_bmad-output/implementation-artifacts/migration-1-4-manifest-loader-compiler.md` — this file (Dev Agent Record populated)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — `migration-1-4-manifest-loader-compiler: ready-for-dev → in-progress → done`

### Change log

| Date | Change | Commit |
|---|---|---|
| 2026-04-23 | Story 1.4 — `PipelineManifest` schema family + loader + compiler (with two-lane support, compile-time `model_config_ref` + `frozen_graph_version` lint, stub condition registry) + `app/gates/resume_api.py` signature-stable stub + Contract C3 restructure + 1.1c stub manifest + smoke_test migrated to production loader. 52 new test nodes. G6 layered-review triage: 1 PATCH (G6-P1 double-START-edge guard), 1 DEFER, ~8 DISMISS. | _(pending)_ |
