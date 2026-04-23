# Migration Story 1.4: Manifest-as-Graph-Config Loader + Compiler

**Status:** ready-for-dev
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

- [ ] **T1 — Read T1 Bundle** §1 (D3 HIL tamper-evidence + Slab-1 substrate distribution; D4, D6, D8), §2 (FR8, FR25, FR31 verdict, FR34 no auto-approve, NFR-M2), §3 (Pydantic + LangGraph state idioms #2 reducer fields, #3 Command goto/update). T1 also includes verifying that 1.2 closed with `OperatorVerdict` model present (1.4 imports it for the `resume_from_verdict` signature stub per AC-1.4-E1).
- [ ] **T2 — Use schema-story scaffold** for `PipelineManifest` + `NodeSpec` + `EdgeSpec`.
- [ ] **T3 — Author schemas** per AC-1.4-A.
- [ ] **T4 — Author loader** per AC-1.4-B.
- [ ] **T4.5 — Author `app/gates/resume_api.py` stub + C3 contract + stub test** per AC-1.4-E1. Land BEFORE compiler implementation so C3 is in `pyproject.toml` when `lint-imports` runs at T8.
- [ ] **T5 — Author compiler** per AC-1.4-C, AC-1.4-D, AC-1.4-E2 (single module, three responsibilities).
- [ ] **T6 — Update 1.1c stub manifest** to satisfy the new schema (no behavioral change; just adds `version`, `lane`, etc.).
- [ ] **T7 — End-to-end test** per AC-1.4-F.
- [ ] **T8 — Run validators + tests.** Sandbox-AC validator + ruff + lint-imports + pytest.
- [ ] **T9 — Commit.** `feat(migration): Slab 1 Story 1.4 — manifest-as-graph-config loader + compiler`

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

_(placeholder)_
