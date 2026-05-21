# Migration Story 7a.2: Manifest Fold-Flags + Compiler Extension

**Status:** done
**Sprint key:** `migration-7a-2-manifest-fold-flags-compiler-extension`
**Epic:** Slab 7a — Inter-Gate Conversational Orchestration (`migration-epic-slab-7a-inter-gate-orchestration`)
**Pts:** 3
**Gate:** **single-gate** (per `docs/dev-guide/migration-story-governance.json` v2026-04-28-slab7a-eight-stories, story 7a-2; rationale: null — substrate-extension that follows 7a.1 precedent)
**K-target:** ~1.3× (gate-shape band 1.5-2.5K; ~2K target)
**Authored:** 2026-04-28 via `bmad-create-story` workflow as Slab 7a Wave-2 spec.
**Wave:** 2 (strict-prereq for Wave 3 = 7a.6 + 7a.3 in parallel)
**FR coverage:** 10 — FR6, FR7, FR8, FR9, FR10; FR-A7, FR-A8, FR-A9, FR-A10, FR-A23
**Standing-guardrail enforcement:** SG-1 unchanged; SG-2 14-vs-10 gate-row preserved in mapping checklist; SG-3 Composition Spec D6 manifest-as-graph-config + FR-A5 manifest-declared dependencies honored.

**Implementation cycle (NEW from 7a.2 onward per operator instruction 2026-04-28):**
- **Claude (Opus 4.7):** authored this spec + ran initial `bmad-party-mode` Gate-1 if called for.
- **Codex (Sonnet 4.5 or later):** develops source code + corresponding test suite per the ACs and tasks below; reaches `review` status; produces a self-conducted G6 layered review (Blind Hunter / Edge Case Hunter / Acceptance Auditor) on its own implementation per single-gate convention.
- **Claude:** does the FINAL `bmad-code-review` on Codex's developed story; applies any remediation cycles; commits; flips `migration-7a-2-manifest-fold-flags-compiler-extension` review → done in sprint-status.

---

## T1 Readiness Block

**Predecessor state (verified at authoring 2026-04-28):**
- Story 7a.1 (directive-composer) closed at `review` 2026-04-28 dev-cycle. T1-T9 dev tasks done; T10/T11/T12 in flight under original cycle (Codex reviews Claude's 7a.1 code).
- 7a.1 PRE-LANDED `v4.2-migration-stub-with-fold-flags` schema_version on `state/config/pipeline-manifest.yaml` AND added it to `scripts/utilities/pipeline_manifest.py::KNOWN_SCHEMA_VERSIONS`. **Codex inherits this — do NOT bump the schema_version again.**
- 7a.1 DEFERRED a manifest registration of the `directive-composer` orchestration node to 7a.2 (lockstep set-equality requires HUD/pack tolerance for orchestration-only nodes). **7a.2 closes this defer.** See AC-7.2-G below.
- Slab 6 trial-experience bundle 3/3 closed 2026-04-28; first tracked trial 475df528-... evidence preserved.

**Live substrate (verified at authoring; do NOT regress):**

- `app/manifest/compiler.py:42` declares `PRODUCTION_GATE_IDS: frozenset[str] = frozenset({"G1", "G2C", "G3", "G4"})` — **the hardcoded frozenset that 7a.2 must replace with manifest-derived computation** (FR-A8). The frozenset is consumed at line 159 in `_resolve_production_handler`: `if node.gate and node.gate_code in PRODUCTION_GATE_IDS: return _production_gate_node(node)`.
- `app/manifest/schema.py::NodeSpec` (line 61-168) is the Pydantic model that needs the additive `fold_with` + `fold_target` fields. Existing fields use `model_config = ConfigDict(extra="forbid", validate_assignment=True)` — additive fields must be explicit `Field(default=None)` to preserve backward compat with existing manifest entries.
- `state/config/pipeline-manifest.yaml` currently has 33 nodes + 18 distinct `gate_code` values (G0, G0A, G0B, G1, G1A, G1.5, G2, G2.5, G2B, G2C, G2M, G2F, G3, G3B, G4, G4A, G4B, G5). Schema_version is `v4.2-migration-stub-with-fold-flags` (added 2026-04-28 by 7a.1 substrate landing — `block_mode_trigger_paths` registration in the manifest header documents this).
- `scripts/utilities/check_pipeline_manifest_lockstep.py` enforces 1:1 set-equality between manifest steps + HUD step list + pack step list. Today this rejects orchestration-only nodes (specialist_id=null, hud_tracked=false, gate=false). 7a.2 must add tolerance for orchestration-only nodes so 7a.1's deferred `directive-composer` node can land.
- `scripts/utilities/pipeline_manifest.py::PipelineManifest` is the LEGACY projection (separate from `app.manifest.schema.PipelineManifest`). It uses `extra="forbid"` on `StepEntry` and ignores most NodeSpec fields. Adding `fold_with` / `fold_target` to NodeSpec is safe vs. legacy projection because `_step_from_graph_node` projects only a curated subset (lines 111-131); the new fields are NOT in that subset and will be silently ignored by the legacy projection.
- `app/marcus/orchestrator/production_runner.py` uses `compile_run_graph(manifest)` from the canonical compiler; the legacy projection is consumed by `scripts/utilities/{run_hud,progress_map}.py` only. 7a.2's compiler changes flow through the canonical compiler ONLY.
- The FOUR currently-active pause-point gates are `G1, G2C, G3, G4` (per the hardcoded frozenset). Other 14 gate_codes (G0, G0A, G0B, G1A, G1.5, G2, G2.5, G2B, G2M, G2F, G3B, G4A, G4B, G5) currently route through `_orchestration_node` because they aren't in PRODUCTION_GATE_IDS. **In 7a.2 the manifest declares this routing explicitly via `fold_with` metadata; the compiler honors the declaration instead of the hardcoded frozenset.**

**Block-mode trigger paths touched by this story (per CLAUDE.md §Pipeline lockstep regime + `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`):**
- `state/config/pipeline-manifest.yaml` — Tier-2 minor extension already landed (schema bump to v4.2-migration-stub-with-fold-flags); 7a.2 is the **operational consumer** of the schema, not a re-bump. **Tier-1 patch discipline** applies to 7a.2's manifest edits (additive `fold_with` per node + the deferred `directive-composer` orchestration-only node).
- `scripts/utilities/check_pipeline_manifest_lockstep.py` — 7a.2 EXTENDS the lockstep contract to tolerate orchestration-only nodes. Tier-1 patch (additive predicate; existing 1:1 contract preserved for non-orchestration nodes).
- `scripts/utilities/pipeline_manifest.py` — no change in 7a.2 scope (legacy projection already absorbed the schema_version bump in 7a.1).

**Gate-mode rationale (from governance JSON):**
> Slab 7a wave-2: manifest fold-flags + compiler extension. Tier-2 minor manifest schema bump (additive `fold_with`/`fold_target` per-node fields); removes hardcoded PRODUCTION_GATE_IDS frozenset and derives from manifest at compile-time (FR-A8). Hard precondition: pipeline-manifest.yaml schema_version bump 'v4.2-migration-stub' → 'v4.2-migration-stub-with-fold-flags' landed via this same 2026-04-28 party-mode round.

**T1 conclusion:** No unanticipated architectural disagreement requires halting Gate 0. Schema bump precondition is RESOLVED (landed 2026-04-28 by 7a.1 substrate). Implementation proceeds: NodeSpec extension + compiler derivation + audit emit + CLI flag + lockstep orchestration-node tolerance + `directive-composer` registration (closing the 7a.1 defer).

---

## Story

As the orchestration runtime,
I want `pipeline-manifest.yaml` to declare fold-flag and fold-target metadata per node so that `PRODUCTION_GATE_IDS` is derived from manifest at compile-time,
so that all 18 currently-declared gate codes (G0, G0A, G0B, G1, G1A, G1.5, G2, G2.5, G2B, G2C, G2M, G2F, G3, G3B, G4, G4A, G4B, G5) are honored at runtime — none silently ignored — and the frozen gate inventory is structurally enforced by the manifest, not by code branches.

---

## Acceptance Criteria

### AC-7.2-A — NodeSpec schema extension (FR-A7, FR-A10)

**Given** the manifest schema at `app/manifest/schema.py::NodeSpec`
**When** the dev agent extends it
**Then** TWO new optional fields are added (additive; backward-compatible):
- `fold_with: str | None = Field(default=None, description="Upstream gate_code this node folds INTO at execute time. Mutually exclusive with fold_target. Honored by the runner: folded gates do NOT pause; they execute as part of the upstream gate's subgraph.")`
- `fold_target: str | None = Field(default=None, description="Subgraph identifier this node compiles into at compile time (e.g., 'subgraph:per-slide-array'). Mutually exclusive with fold_with. Subgraph compilation is Slab 7a Story 7a.4 scope; 7a.2 reserves the field shape only.")`
**And** the model retains `extra="forbid"` posture; existing manifest entries that omit both fields validate cleanly (default None).
**And** a model_validator enforces mutual exclusion: `fold_with` and `fold_target` MUST NOT both be set on the same node — raise validation error `"node {id}: fold_with and fold_target are mutually exclusive"` if both present.

**Test pin:** `tests/unit/manifest/test_node_spec_fold_fields.py` — 4 cases: (a) neither set (existing behavior; valid), (b) only `fold_with` set (valid), (c) only `fold_target` set (valid), (d) both set (raises ValidationError with the canonical message).

### AC-7.2-B — Manifest data: fold_with declared on all currently-orchestration gates (FR6, FR7)

**Given** the live `state/config/pipeline-manifest.yaml`
**When** the dev agent annotates the gate-bearing nodes
**Then** for every node where `gate: true`:
- If `gate_code in {"G1", "G2C", "G3", "G4"}` → leave `fold_with: null` (these are the active pause-points; no fold).
- Else → add `fold_with: <upstream_gate_code>` where `<upstream_gate_code>` is the most-recent active pause-point that precedes the node in the linear chain (per existing `insertion_after`).
**And** the declarative folding produces this canonical mapping (record at `state/config/gate_fold_manifest.yaml` per AC-7.2-D):
- G0, G0A, G0B → `fold_with: G1` (G0 family folds into G1 since they precede G1 in the chain and are not currently pause-points)
- G1A, G1.5, G2, G2.5, G2B, G2M → `fold_with: G2C` (folded into G2C the next active gate)
- G2F, G3B → `fold_with: G3`
- G4A, G4B, G5 → `fold_with: G4`

**WAIT — IMPORTANT for Codex:** confirm this canonical mapping by walking `state/config/pipeline-manifest.yaml` in `insertion_after` order BEFORE writing data. The mapping above is the AUTHORITATIVE intent per the Slab 7a PRD §FR6 + the operator's "10-gate frozen inventory" principle. If your walk produces a different mapping, HALT and surface to operator before committing manifest edits.

**Test pin:** `tests/unit/manifest/test_manifest_fold_with_declarations.py` — assert each of the 18 gate-bearing nodes has the expected `fold_with` value (or null for the 4 active pause-points).

### AC-7.2-C — Compiler derives PRODUCTION_GATE_IDS at compile-time (FR-A8)

**Given** the compiler at `app/manifest/compiler.py`
**When** the dev agent removes the hardcoded `PRODUCTION_GATE_IDS = frozenset({"G1", "G2C", "G3", "G4"})` at line 42
**Then** `PRODUCTION_GATE_IDS` is computed at module load OR derived inside `_resolve_production_handler` from `manifest.nodes` — specifically, the set of `gate_code` values for nodes where `gate is True` AND `fold_with is None` AND `fold_target is None`.
**And** the public symbol `PRODUCTION_GATE_IDS` is RETIRED from the module-level export. Replace with a function `production_gate_ids(manifest: PipelineManifest) -> frozenset[str]` exported from `app/manifest/compiler.py`. Existing call sites that imported `PRODUCTION_GATE_IDS` must migrate to call the new function.
**And** a CI grep-guard test asserts `app/manifest/compiler.py` does NOT contain a hardcoded frozenset literal mapping gate codes to a static set.
**And** `_resolve_production_handler` uses `production_gate_ids(manifest)` to decide pause-point vs orchestration routing.

**Test pin:** `tests/unit/manifest/test_production_gate_ids_derived.py` — 5 cases: (a) function returns the 4 expected pause-points against the live manifest, (b) function returns `frozenset()` against an empty manifest, (c) function honors `fold_with` (folded gates excluded from result), (d) function honors `fold_target` (also excluded), (e) grep-guard asserts no `frozenset({"G1"...` literal in compiler.py source. **Plus** a regression test that the existing `_resolve_production_handler` behavior is preserved for the 4 active pause-points (G1, G2C, G3, G4 still emit `_production_gate_node`).

### AC-7.2-D — Audit artifact: gate_fold_manifest.yaml emitted (FR9, FR-A10)

**Given** the new audit emitter
**When** the dev agent runs `python -m app.manifest.gate_fold_manifest_emit` (NEW CLI module) OR a top-level CLI under `scripts/utilities/emit_gate_fold_manifest.py`
**Then** the emitter loads the manifest, computes the fold mechanism per gate code, and writes `state/config/gate_fold_manifest.yaml` with this canonical shape:

```yaml
# Auto-generated by Story 7a.2 from state/config/pipeline-manifest.yaml.
# Do NOT hand-edit. Re-emit via `python -m app.manifest.gate_fold_manifest_emit`.
# Generated: <iso-timestamp-utc>
# Source manifest schema_version: v4.2-migration-stub-with-fold-flags
gates:
  - code: G0
    mechanism: fold_with
    fold_target: G1
  - code: G0A
    mechanism: fold_with
    fold_target: G1
  - code: G1
    mechanism: pause_point
    fold_target: null
  - code: G1A
    mechanism: fold_with
    fold_target: G2C
  ...
  - code: G5
    mechanism: fold_with
    fold_target: G4
```

**And** the audit YAML enumerates ALL 18 currently-declared gate codes (one entry each).
**And** `grep -c '^- code:' state/config/gate_fold_manifest.yaml` returns 18.
**And** zero entries have `mechanism: ignore` or absent `mechanism:` field.
**And** the emitter is idempotent: re-running produces byte-identical output (sort by gate_code; deterministic timestamp via env var or fixed clock for tests).
**And** a CI test asserts `state/config/gate_fold_manifest.yaml` exists and is in sync with the live manifest (re-emit + diff; non-zero diff fails).

**Test pin:** `tests/unit/manifest/test_gate_fold_manifest_emit.py` — 4 cases: (a) emit against live manifest produces the expected canonical mapping, (b) idempotency (re-emit byte-stable), (c) `grep -c '^- code:'` returns 18, (d) all gate_codes have non-null mechanism. **Plus** `tests/structural/test_gate_fold_manifest_in_sync.py` — sync-check test runs in CI (re-emit to tmp_path + compare bytes against the on-tree file).

### AC-7.2-E — Runner refuses gate-bypass (FR-A23)

**Given** the runner at `app/marcus/orchestrator/production_runner.py`
**When** any code path attempts to advance the trial past a gate node WITHOUT either (a) it being folded (`fold_with` is set in manifest) OR (b) the operator emitting a verdict for it
**Then** the runner raises `GateBypassError(RuntimeError)` with message `"refused silent bypass of gate {gate_code} at manifest node {node_id}"`.
**And** in `_resolve_production_handler`, when a node has `gate: true` AND is in `production_gate_ids(manifest)`, the gate handler is wired such that any forward edge attempted without operator verdict triggers the refusal (via existing checkpoint/decision-card mechanism).

**Implementation hint for Codex:** the existing `_production_gate_node` already returns an empty handler that the runner's outer loop intercepts (see `app/marcus/orchestrator/production_runner.py:556` `if node_kind == "gate": ... if not pause_at_gates: graph_step_completed = True; continue`). Add a new check before the `pause_at_gates=False` short-circuit: if the gate is an active pause-point per `production_gate_ids(manifest)` AND no verdict has been emitted for the trial's current `paused_gate`, refuse advancement with `GateBypassError`. Trial-475 silent-bypass-style behavior (Texas with empty directive_path) is a different layer — that's 7a.1's scope; this AC is about the gate-runner refusing to skip a frozen pause-point.

**Test pin:** `tests/integration/marcus/test_gate_bypass_refusal.py` — 3 cases: (a) attempting to advance past G1 without verdict raises `GateBypassError`, (b) advancing past a folded gate (e.g. G0A with `fold_with: G1`) does NOT raise (folded gates do not pause), (c) `pause_at_gates=False` short-circuit still works for offline-cost-report runs (preserves existing behavior).

### AC-7.2-F — Operator-CLI unfolded 14-gate view (FR10)

**Given** an operator wants to inspect the full unfolded gate topology
**When** the operator invokes `python -m app.manifest.gate_topology --unfolded` (NEW CLI module) OR `scripts/utilities/show_gate_topology.py --unfolded`
**Then** the topology dump emits all 18 gate_codes with their fold mechanism, in `insertion_after` chain order:

```
G0    | fold_with: G1
G0A   | fold_with: G1
G0B   | fold_with: G1
G1    | pause_point
G1A   | fold_with: G2C
G1.5  | fold_with: G2C
G2    | fold_with: G2C
G2.5  | fold_with: G2C
G2B   | fold_with: G2C
G2C   | pause_point
G2M   | fold_with: G2C  -- NOTE: G2M is sub_phase_of G2C; verify chain placement during dev
G2F   | fold_with: G3
G3B   | fold_with: G3
G3    | pause_point
G4    | pause_point
G4A   | fold_with: G4
G4B   | fold_with: G4
G5    | fold_with: G4
```

**And** with `--folded` (default), only the 4 active pause-points are listed (canonical pause inventory).
**And** with `--audit`, a side-by-side comparison of the manifest declaration vs the emitted `gate_fold_manifest.yaml` is shown.

**Test pin:** `tests/unit/manifest/test_gate_topology_cli.py` — 3 cases: (a) `--unfolded` lists all 18, (b) `--folded` lists exactly 4, (c) `--audit` runs without error and exits 0.

### AC-7.2-G — Lockstep orchestration-node tolerance + 7a.1 directive-composer registration (closes 7a.1 defer)

**Given** `scripts/utilities/check_pipeline_manifest_lockstep.py` enforces 1:1 set-equality between manifest steps + HUD step list + pack step list
**When** the dev agent adds tolerance for orchestration-only nodes
**Then** the lockstep checker classifies each manifest node as either:
- `gate-or-specialist` node — must appear in HUD + pack registries (existing strict 1:1 contract).
- `orchestration-only` node — defined as `specialist_id is None AND gate is False AND hud_tracked is False`. These nodes are PERMITTED in the manifest WITHOUT corresponding HUD/pack entries; they are excluded from the set-equality and order-equality checks.
**And** the lockstep test trace (`reports/dev-coherence/<ts>/check-pipeline-manifest-lockstep.PASS.yaml`) records orchestration-only nodes in a new `orchestration_only_nodes:` field for audit visibility.
**And** the dev agent re-adds the deferred `directive-composer` orchestration node to `state/config/pipeline-manifest.yaml`, replacing the inline deferral comment block from 7a.1 with the actual node entry:

```yaml
nodes:
  - id: "directive-composer"
    label: "G0 — Directive Composition (Slab 7a / Story 7a.1)"
    specialist_id: null
    scaffold_node: null
    model_config_ref: null
    dependencies: {}
    gate: false
    gate_code: null
    sub_phase_of: null
    insertion_after: null
    hud_tracked: false
    pack_section_anchor: "0)"
    pack_version: "v4.2"
    fold_with: null
    fold_target: null
    rationale: >-
      Pure-function orchestration node added by Story 7a.1 (slab-opener) and
      registered in the manifest by Story 7a.2 (orchestration-node tolerance).
      Closes trial-475 Gap 2. Composer runs at trial-start before Section 01;
      operator confirms-or-edits before Texas dispatches. Composition Spec §3.6
      manifest-declared dependencies honored (FR-A5).

  - id: "01"
    ...
```

**And** `python scripts/utilities/check_pipeline_manifest_lockstep.py` exits 0 with the directive-composer node present.
**And** the structural test at `tests/structural/test_pipeline_manifest_directive_composer_node.py` (authored in 7a.1) is UPDATED — its current assertion is "deferral comment exists"; flip to "directive-composer node entry exists with the expected canonical fields per A-R4 from 7a.1's Gate-1 addendum". Specifically assert: `id == "directive-composer"`, `specialist_id is None`, `gate is False`, `hud_tracked is False`, `dependencies == {}`, `fold_with is None`, `fold_target is None`.

**Test pin:** `tests/structural/test_lockstep_orchestration_only_tolerance.py` — 3 cases: (a) lockstep passes with the directive-composer orchestration-only node present, (b) adding a fake gate-or-specialist node WITHOUT HUD/pack entry still fails (existing strictness preserved), (c) the lockstep trace YAML records the orchestration_only_nodes field with `directive-composer` listed.

### AC-7.2-H — Tier-1 patch discipline + Composition Spec invariants (NFR-V1, NFR-V4)

**Given** the manifest edits (NodeSpec schema extension + per-gate fold_with annotations + directive-composer node)
**When** the dev agent commits
**Then** the manifest schema_version remains `v4.2-migration-stub-with-fold-flags` (NO further bump in 7a.2 — the bump was 7a.1 substrate territory).
**And** the pack_version remains `v4.2` (additive node-level metadata is Tier-1 patch per `docs/dev-guide/pipeline-manifest-regime.md` Pack Versioning Policy).
**And** Composition Spec §3.6 (manifest-declared dependencies) is HONORED end-to-end: the directive-composer node declares `dependencies: {}`; all other nodes preserve their existing dependency declarations.
**And** Composition Spec §11 trigger check is recorded in close: this story is additive only (NodeSpec gains optional fields; manifest gains per-node metadata; lockstep gains a tolerance predicate; new audit emitter + CLI module are additive). NO §11 trigger fired.
**And** if the Composition Spec §10 Decision Log entry from 7a.1 (about `runner_supplied_payload` kwarg on `build_specialist_state`) has not yet landed at the time 7a.2 closes, file a follow-up to ensure 7a.1 close completes the Decision Log entry; do NOT block 7a.2 close on it.

### AC-7.2-I — N-item + anti-pattern + Composition Spec trace

The implementation must record:
- **N1 PASS:** new module `app/manifest/gate_fold_manifest_emit.py` (or `scripts/utilities/emit_gate_fold_manifest.py`) follows substrate-inventory checklist.
- **N2 PASS:** Composition Spec §3.6 + §11 invariants honored (manifest-declared dependencies + Tier-1 patch additive only).
- **N4 PASS:** specialist isolation preserved — schema extension + compiler derivation + audit emit do not touch any specialist body.
- **N9 PASS-PENDING-OPERATOR:** operator validates the unfolded-vs-folded CLI dump UX at story close.
- **N10 PASS:** A12 procedural-coupling re-read; the new audit emit is wired into a CI sync-check (no manual procedural step); the orchestration-node tolerance is structural (no manual classification step).
- **A1, A11 honored** — `pathlib.Path` throughout; YAML emission via `yaml.safe_dump(default_flow_style=False, sort_keys=True, allow_unicode=True)` (NOT ruamel; PyYAML is the shipped lib per 7a.1 dev-cycle finding).
- **Composition Spec §10 Decision Log entry NOT REQUIRED for 7a.2** — Tier-1 patch (additive); §10 entries are reserved for substrate-shape evolutions like 7a.1's `runner_supplied_payload` kwarg. Confirm absent at code-review.

### AC-7.2-J — D12 close protocol

At close:
- Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: `migration-7a-2-manifest-fold-flags-compiler-extension` → `done`; epic stays `in-progress` (Wave 3 = 7a.6 + 7a.3 unblocked).
- Cite sandbox-AC validator PASS.
- Cite pipeline-manifest lockstep PASS (with the directive-composer orchestration-only node now registered).
- Cite production_gate_ids derivation correctness (test passes against live manifest).
- Confirm Composition Spec §11 trigger did not fire (Tier-1 additive only).
- File any follow-ons surfaced during dev into `_bmad-output/planning-artifacts/deferred-inventory.md` per CLAUDE.md §Deferred-inventory governance.
- Mark 7a.1's deferred follow-on `7a-1-deferred-directive-composer-manifest-node` as CLOSED-by-7a.2 in deferred-inventory.md.

---

## Tasks / Subtasks

- [x] **T1: T1 Readiness review (Codex)**
  - [x] Read this spec end-to-end + every cited reference (governance JSON; Composition Spec §3.6/§9/§10/§11; pipeline-manifest-regime.md; sandbox-AC inventory; 7a.1 spec for the deferred manifest registration context).
  - [x] Read `app/manifest/compiler.py` end-to-end (the hardcoded frozenset at line 42 + its consumer at line 159).
  - [x] Read `app/manifest/schema.py::NodeSpec` (line 61-168) for the additive field pattern.
  - [x] Read `state/config/pipeline-manifest.yaml` end-to-end and walk the gate_code chain in `insertion_after` order to CONFIRM the AC-7.2-B canonical fold mapping.
  - [x] Read `scripts/utilities/check_pipeline_manifest_lockstep.py` to understand the lockstep contract before extending it.
  - [x] Confirm no decision_needed surfaces at T1; if yes, HALT and surface to operator.

- [x] **T2: NodeSpec schema extension** (AC: A)
  - [x] In `app/manifest/schema.py::NodeSpec`, add `fold_with` and `fold_target` optional fields.
  - [x] Add a `@model_validator(mode="after")` that enforces mutual exclusion.
  - [x] Author `tests/unit/manifest/test_node_spec_fold_fields.py` (4 cases per AC-A).

- [x] **T3: Compiler derivation of PRODUCTION_GATE_IDS** (AC: C)
  - [x] In `app/manifest/compiler.py`, REMOVE the hardcoded `PRODUCTION_GATE_IDS = frozenset(...)` at line 42.
  - [x] Add `def production_gate_ids(manifest: PipelineManifest) -> frozenset[str]:` that returns `frozenset(node.gate_code for node in manifest.nodes if node.gate and node.gate_code and node.fold_with is None and node.fold_target is None)`.
  - [x] Update `_resolve_production_handler(node, dispatch_registry, manifest)` to take the manifest as a kwarg and use `production_gate_ids(manifest)` instead of the module-level frozenset. Update the callers at line 346 (in `_add_node_and_edges`).
  - [x] Update the `__all__` export to include `production_gate_ids` and remove `PRODUCTION_GATE_IDS`.
  - [x] Migrate any other call sites that import `PRODUCTION_GATE_IDS` (grep: `from app.manifest.compiler import PRODUCTION_GATE_IDS` and `from app.manifest import compiler; ... compiler.PRODUCTION_GATE_IDS`).
  - [x] Author `tests/unit/manifest/test_production_gate_ids_derived.py` (5 cases per AC-C).

- [x] **T4: Manifest data — fold_with declarations on every gate-bearing node** (AC: B)
  - [x] Walk `state/config/pipeline-manifest.yaml` in `insertion_after` order, identifying each gate-bearing node and its preceding active pause-point.
  - [x] For each gate-bearing node: add `fold_with: <upstream_gate_code>` if the node is NOT in the active pause-point set {G1, G2C, G3, G4}; else add explicit `fold_with: null`.
  - [x] Author `tests/unit/manifest/test_manifest_fold_with_declarations.py` (assert per-node fold_with values per AC-B mapping).
  - [x] **HALT-AND-SURFACE checkpoint:** if your walk produces a different mapping than AC-B's canonical mapping, do NOT proceed; pause and report to operator.

- [x] **T5: Audit artifact — `gate_fold_manifest.yaml` emitter** (AC: D)
  - [x] Create `app/manifest/gate_fold_manifest_emit.py` with a `python -m` entry point. Function signature: `def emit_gate_fold_manifest(manifest_path: Path, output_path: Path, *, now: datetime | None = None) -> None`.
  - [x] Emit canonical YAML per AC-D shape using `yaml.safe_dump(default_flow_style=False, sort_keys=False, allow_unicode=True)` to preserve gate-code chain ordering. Use `sort_keys=False` deliberately so the gate ordering matches `insertion_after` chain order.
  - [x] Generate the file at `state/config/gate_fold_manifest.yaml` (commit to repo).
  - [x] Author `tests/unit/manifest/test_gate_fold_manifest_emit.py` (4 cases per AC-D).
  - [x] Author `tests/structural/test_gate_fold_manifest_in_sync.py` (sync-check; CI fails if `state/config/gate_fold_manifest.yaml` diverges from re-emit).

- [x] **T6: Runner refuses gate-bypass** (AC: E)
  - [x] Add `class GateBypassError(RuntimeError)` to `app/marcus/orchestrator/production_runner.py`.
  - [x] Wire the refusal at the existing gate-handler intercept (line ~556 `if node_kind == "gate":`). Refusal applies when `pause_at_gates=True` (the live trial path) AND a folded gate's upstream pause-point has NOT received a verdict yet.
  - [x] Author `tests/integration/marcus/test_gate_bypass_refusal.py` (3 cases per AC-E).

- [x] **T7: Operator-CLI unfolded gate-topology view** (AC: F)
  - [x] Create `app/manifest/gate_topology.py` with `python -m` entry point. Flags: `--unfolded`, `--folded` (default), `--audit`.
  - [x] Output is plain text (NOT YAML) for operator readability — one line per gate as `<gate_code> | <mechanism>: <fold_target_or_blank>`.
  - [x] Author `tests/unit/manifest/test_gate_topology_cli.py` (3 cases per AC-F).

- [x] **T8: Lockstep orchestration-node tolerance + directive-composer registration** (AC: G)
  - [x] In `scripts/utilities/check_pipeline_manifest_lockstep.py`, add the orchestration-only classifier predicate: `is_orchestration_only(node) -> bool` returning `node.specialist_id is None AND node.gate is False AND node.hud_tracked is False`.
  - [x] Exclude orchestration-only nodes from set-equality and order-equality checks; include them in a new `orchestration_only_nodes:` audit field in the trace YAML.
  - [x] Replace the inline deferral comment block in `state/config/pipeline-manifest.yaml` with the actual `directive-composer` node entry per AC-G shape.
  - [x] UPDATE `tests/structural/test_pipeline_manifest_directive_composer_node.py`: replace the deferral-comment assertions with node-existence + canonical-field assertions.
  - [x] Author `tests/structural/test_lockstep_orchestration_only_tolerance.py` (3 cases per AC-G).

- [x] **T9: Verification battery (Codex self-conducted G6 layered review for single-gate)**
  - [x] `.\.venv\Scripts\python.exe -m pytest tests/unit/manifest tests/integration/marcus/test_gate_bypass_refusal.py tests/structural/test_lockstep_orchestration_only_tolerance.py tests/structural/test_pipeline_manifest_directive_composer_node.py tests/structural/test_gate_fold_manifest_in_sync.py -q --tb=short` → all PASS.
  - [x] `.\.venv\Scripts\python.exe -m pytest tests/composition tests/integration/marcus tests/parity tests/specialists/texas tests/specialists/_scaffold -q --tb=line` → no regression (target: 198+ passed; pre-7a.2 baseline was 198 passed / 1 skipped on this slice).
  - [x] `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` → exit 0; trace YAML carries `orchestration_only_nodes: [directive-composer]`.
  - [x] `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md` → exit 0.
  - [x] `.\.venv\Scripts\python.exe -m ruff check app/manifest tests/unit/manifest tests/integration/marcus/test_gate_bypass_refusal.py tests/structural/test_lockstep_orchestration_only_tolerance.py tests/structural/test_gate_fold_manifest_in_sync.py scripts/utilities/check_pipeline_manifest_lockstep.py` → clean.
  - [x] `.\.venv\Scripts\lint-imports.exe` → 9/9 contracts KEPT.
  - [x] `.\.venv\Scripts\python.exe -m app.manifest.gate_fold_manifest_emit` (manual verify the emit roundtrips byte-stable).
  - [x] `.\.venv\Scripts\python.exe -m app.manifest.gate_topology --unfolded` and `--folded` (manual verify outputs match AC-F).

- [x] **T10: Codex self-conducted G6 layered review (single-gate)**
  - [x] Codex authors a self-review at `_bmad-output/implementation-artifacts/7a-2-codex-self-review-2026-04-XX.md` covering: Blind Hunter (adversarial), Edge Case Hunter (boundary), Acceptance Auditor (spec traceability).
  - [x] Codex flips story status `in-progress` → `review` in the spec file (NOT in sprint-status.yaml — that's Claude's job at T12).
  - [x] Codex hands back to Claude for final `bmad-code-review` + commit + sprint-status flip.

- [ ] **T11: Claude `bmad-code-review` + remediation cycles + commit + close**
  - [ ] Claude reads Codex's developed code + self-review.
  - [ ] Claude runs `bmad-code-review` independently (Blind / Edge / Auditor passes).
  - [ ] Claude triages findings: PATCH applied, DEFER filed in deferred-inventory, DISMISS recorded with rationale.
  - [ ] Claude re-runs verification battery after remediation; all clean.
  - [ ] Claude commits with descriptive message.
  - [ ] Claude flips `migration-7a-2-manifest-fold-flags-compiler-extension` review → done in sprint-status.yaml.
  - [ ] Claude marks 7a.1's `7a-1-deferred-directive-composer-manifest-node` follow-on as CLOSED-by-7a.2 in deferred-inventory.md.

---

## File Structure Requirements

**Expected new files:**
- `app/manifest/gate_fold_manifest_emit.py` (audit emitter; `python -m` entry point)
- `app/manifest/gate_topology.py` (operator-facing topology dump CLI; `python -m` entry point)
- `state/config/gate_fold_manifest.yaml` (auto-generated audit artifact; committed)
- `tests/unit/manifest/test_node_spec_fold_fields.py`
- `tests/unit/manifest/test_production_gate_ids_derived.py`
- `tests/unit/manifest/test_manifest_fold_with_declarations.py`
- `tests/unit/manifest/test_gate_fold_manifest_emit.py`
- `tests/unit/manifest/test_gate_topology_cli.py`
- `tests/integration/marcus/test_gate_bypass_refusal.py`
- `tests/structural/test_gate_fold_manifest_in_sync.py`
- `tests/structural/test_lockstep_orchestration_only_tolerance.py`
- `_bmad-output/implementation-artifacts/7a-2-codex-self-review-2026-04-XX.md` (T10 deliverable)

**Expected modified files:**
- `app/manifest/schema.py` (NodeSpec gets `fold_with` + `fold_target` additive fields + mutual-exclusion validator)
- `app/manifest/compiler.py` (remove `PRODUCTION_GATE_IDS` literal; add `production_gate_ids(manifest)` function; rewire `_resolve_production_handler`)
- `app/marcus/orchestrator/production_runner.py` (add `GateBypassError` + refusal wiring at gate-handler intercept)
- `state/config/pipeline-manifest.yaml` (annotate every gate-bearing node with `fold_with`; replace deferral-comment block with the `directive-composer` orchestration-only node entry)
- `scripts/utilities/check_pipeline_manifest_lockstep.py` (orchestration-only-node tolerance predicate + audit field)
- `tests/structural/test_pipeline_manifest_directive_composer_node.py` (FLIP from deferral-comment assertions to node-existence assertions)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status flips per T11; close 7a.1's `7a-1-deferred-directive-composer-manifest-node` follow-on)
- `_bmad-output/planning-artifacts/deferred-inventory.md` (mark 7a.1 follow-on closed; file any new 7a.2 follow-ons)

**Do NOT modify:**
- `scripts/utilities/pipeline_manifest.py` (legacy projection — already absorbed the schema_version bump in 7a.1; new fold fields are silently ignored by `_step_from_graph_node` projection which is the right behavior)
- Any specialist body (`app/specialists/{texas,irene,kira,...}/` etc.)
- `app/marcus/orchestrator/directive_composer.py` (7a.1 surface; do not touch)
- `app/marcus/orchestrator/dispatch_adapter.py` (7a.1's additive `runner_supplied_payload` kwarg stays as-is)
- `app/marcus/cli/trial.py` (7a.1 surface)
- v4.2 prompt pack
- `state/config/pipeline-manifest.yaml::schema_version` (stays `v4.2-migration-stub-with-fold-flags`; do NOT bump)

---

## Testing Requirements

**K-floor 13 (per gate-shape band 1.5-2.5K minimum; per governance JSON expected_k_target=1.3):**
- 4 NodeSpec fold-field cases (AC-A)
- 5 production_gate_ids derivation cases (AC-C)
- 1 manifest fold_with declarations regression test (AC-B)
- 4 gate_fold_manifest emit cases (AC-D)
- 3 gate-topology CLI cases (AC-F)
- 3 gate-bypass refusal cases (AC-E)
- 3 lockstep orchestration-only tolerance cases (AC-G)
- 1 directive-composer node existence regression (AC-G UPDATE)

**K-target ~20 (~1.3× per governance JSON):**
- + sync-check structural test (AC-D)
- + grep-guard test asserting no hardcoded frozenset literal in compiler.py (AC-C)
- + integration test verifying `_resolve_production_handler` against the live manifest (AC-C regression)

**K-tripwire (per CLAUDE.md §Lesson Planner governance + governance JSON discipline):** if K-actual exceeds 1.7× target (~3.4K), the dev round closes and party-mode triage convenes (NFR-CG5). Codex MUST report K-actual at T10 self-review.

**Required verification at implementation close (per T9):**
- `.\.venv\Scripts\python.exe -m pytest tests/unit/manifest tests/integration/marcus/test_gate_bypass_refusal.py tests/structural/test_lockstep_orchestration_only_tolerance.py tests/structural/test_pipeline_manifest_directive_composer_node.py tests/structural/test_gate_fold_manifest_in_sync.py tests/composition tests/integration/marcus tests/parity tests/specialists/texas tests/specialists/_scaffold -q --tb=line`
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py`
- `.\.venv\Scripts\python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md`
- `.\.venv\Scripts\python.exe -m ruff check app/manifest tests/unit/manifest tests/integration/marcus/test_gate_bypass_refusal.py tests/structural scripts/utilities/check_pipeline_manifest_lockstep.py`
- `.\.venv\Scripts\lint-imports.exe`

---

## Dev Notes

### Architecture compliance

- **Composition Spec §3.6 (manifest-declared dependencies):** `directive-composer` node declares `dependencies: {}`; all other nodes preserve existing dependency declarations. Per A-R2 from 7a.1.
- **ADR-D6 manifest-as-graph-config:** strengthened — `PRODUCTION_GATE_IDS` is now derived from manifest at compile-time per FR-A8.
- **ADR-D8 frozen-graph ceremony:** Tier-1 patch (additive fields + per-node metadata + new orchestration node + lockstep tolerance). Schema_version stays at `v4.2-migration-stub-with-fold-flags`; pack_version stays at `v4.2`.
- **Composition Spec §11 trigger check:** additive only. Confirm no §11 trigger fires.
- **Composition Spec §10 Decision Log entry NOT REQUIRED for 7a.2.** §10 is reserved for substrate-shape evolutions; Tier-1 patches don't trigger it.

### Library / framework requirements

- **PyYAML** (already shipped per 7a.1 finding) for `safe_dump`/`safe_load`. Settings: `default_flow_style=False, sort_keys=False, allow_unicode=True` for the audit YAML to preserve insertion order.
- **Pydantic v2** for NodeSpec field additions (already used by `app/manifest/schema.py`); follow `docs/dev-guide/pydantic-v2-schema-checklist.md` if any new model_validator is added.
- **NO new third-party deps.** If a dep seems necessary, HALT and surface to Claude/operator.

### Anti-patterns to avoid

- **A12 procedural-coupling:** the audit emitter MUST be wired into a CI sync-check (`tests/structural/test_gate_fold_manifest_in_sync.py`); do NOT introduce a manual operator step to keep the audit YAML in sync.
- **A9 epic-doc structural-name drift:** the AC-B canonical fold mapping is the AUTHORITATIVE intent; if your `insertion_after` walk produces a different mapping, surface to operator BEFORE editing.
- **A11 Windows-portability:** YAML emission uses `default_flow_style=False, allow_unicode=True`; line endings are `\n` POSIX.
- **Sandbox-AC inventory rule (CLAUDE.md §LangChain/LangGraph migration — sandbox-AC):** ACs above use only Python + pytest + ruff + lint-imports. No `docker`, `psql`, `gh`, `curl`, etc. The validator MUST PASS at story-finalize AND at dev-open.
- **Hardcoded frozeset retention (FR-A8 violation):** the grep-guard test in AC-C asserts no hardcoded `PRODUCTION_GATE_IDS` literal survives. Do NOT just rename the variable — actually derive it from the manifest.

### Previous story intelligence

- **7a.1 substrate landings absorbed by 7a.2:**
  - Schema_version `v4.2-migration-stub-with-fold-flags` already on tree; do NOT re-bump.
  - `KNOWN_SCHEMA_VERSIONS` in legacy projection already updated; do NOT re-edit.
  - PyYAML over ruamel.yaml (ruamel not actually shipped); use PyYAML throughout.
  - `directive-composer` orchestration node is a 7a.1 deferral that 7a.2 closes via AC-G; the deferral comment block in the manifest will be REPLACED with the actual node entry.
- **Slab 6.2 dependency_map promotion** is the closest precedent for "promote runtime concept into manifest" pattern. Mirror its structural-pin discipline.
- **Slab 6.0 substrate-opener pattern** for additive substrate evolution (Composition Smoke gate at slab-opener was 7a.1's job; 7a.2 does NOT need to re-emit Composition Smoke).

### Project structure notes

- `app/manifest/` is the canonical location for compiler/loader/schema modules. The new `gate_fold_manifest_emit.py` and `gate_topology.py` modules belong here (NOT in `scripts/utilities/`).
- `tests/unit/manifest/` is the existing home for manifest tests (consistent pattern with `tests/unit/manifest/test_lane_separation.py`).
- `state/config/gate_fold_manifest.yaml` is a NEW state artifact; commit it to the repo (auditable; in-sync test ensures it stays current).

### References

- [Source: `_bmad-output/planning-artifacts/epics-slab-7a-inter-gate-orchestration.md` Story 1.2 (Manifest Fold-Flags + Compiler Extension)]
- [Source: `_bmad-output/planning-artifacts/prd-slab-7a-inter-gate-orchestration.md` §FR6-FR10 + §FR-A7-A10 + §FR-A23]
- [Source: `docs/dev-guide/migration-story-governance.json` story `7a-2`]
- [Source: `docs/dev-guide/composition-specification.md` §3.6, §10, §11]
- [Source: `docs/dev-guide/pipeline-manifest-regime.md` §Pack Versioning Policy (Tier-1 patch criteria)]
- [Source: `docs/dev-guide/migration-ac-sandbox-inventory.json` (forbidden CLI list)]
- [Source: `docs/dev-guide/specialist-anti-patterns.md` A9, A11, A12]
- [Source: `_bmad-output/implementation-artifacts/migration-7a-1-directive-composer.md` (7a.1's deferral context for AC-G)]
- [Source: `app/manifest/compiler.py:42` (the hardcoded frozenset to remove)]
- [Source: `app/manifest/compiler.py:159` (the consumer of PRODUCTION_GATE_IDS in `_resolve_production_handler`)]
- [Source: `app/manifest/schema.py::NodeSpec` line 61-168 (the model to extend)]
- [Source: `state/config/pipeline-manifest.yaml` (33 nodes; 18 gate_codes; schema_version v4.2-migration-stub-with-fold-flags)]
- [Source: `scripts/utilities/check_pipeline_manifest_lockstep.py` (lockstep contract to extend with orchestration-only tolerance)]
- [Source: CLAUDE.md §Pipeline lockstep regime + §LangChain/LangGraph migration — sandbox-AC + gate-mode governance]

---

## Dev Agent Record

### Agent Model Used

Codex (GPT-5), 2026-04-29 dev-story execution. Claude authored the spec; Codex implemented T1-T10 and left T11 close actions to Claude per operator boundary.

### Debug Log References

- T1 fold mapping confirmed against live manifest gate order; canonical fold map applied.
- `PRODUCTION_GATE_IDS` call-site grep found compiler internal use plus `production_runner.py`; both migrated to `production_gate_ids(manifest)`.
- Lockstep trace: `reports/dev-coherence/2026-04-29-0410/check-pipeline-manifest-lockstep.PASS.yaml`.
- Broader pytest note: unshimmed environment lacks `vi`, causing the 7a.1 editor fallback test to fail outside 7a.2 scope; temporary PATH shim run passed.

### Completion Notes List

- Added `fold_with` / `fold_target` to `NodeSpec` with mutual-exclusion validation and schema-pin updates.
- Replaced hardcoded production gate set with manifest-derived `production_gate_ids(manifest)`.
- Annotated all 18 gate-bearing manifest nodes with canonical fold metadata and registered the 7a.1 `directive-composer` orchestration-only node.
- Added deterministic gate fold audit emitter, committed `state/config/gate_fold_manifest.yaml`, and added operator topology CLI.
- Extended lockstep to tolerate audited orchestration-only nodes while preserving strict failures for unregistered specialist/gate nodes.
- Added `GateBypassError` for start-mode and resume-mode silent active-gate bypass, with offline-cost-report tolerance preserved.

### File List

- `app/manifest/schema.py`
- `app/manifest/compiler.py`
- `app/manifest/gate_fold_manifest_emit.py`
- `app/manifest/gate_topology.py`
- `app/marcus/orchestrator/production_runner.py`
- `scripts/utilities/check_pipeline_manifest_lockstep.py`
- `state/config/pipeline-manifest.yaml`
- `state/config/gate_fold_manifest.yaml`
- `tests/fixtures/manifest/schema_pin_node_spec.json`
- `tests/fixtures/manifest/schema_pin_pipeline_manifest.json`
- `tests/unit/manifest/test_node_spec_fold_fields.py`
- `tests/unit/manifest/test_production_gate_ids_derived.py`
- `tests/unit/manifest/test_manifest_fold_with_declarations.py`
- `tests/unit/manifest/test_gate_fold_manifest_emit.py`
- `tests/unit/manifest/test_gate_topology_cli.py`
- `tests/unit/manifest/test_compiler.py`
- `tests/integration/marcus/test_gate_bypass_refusal.py`
- `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py`
- `tests/integration/marcus/test_production_runner_dependency_resolution.py`
- `tests/integration/marcus/test_production_runner_invocation.py`
- `tests/integration/marcus/test_production_runner_resume_invariants.py`
- `tests/structural/test_gate_fold_manifest_in_sync.py`
- `tests/structural/test_lockstep_orchestration_only_tolerance.py`
- `tests/structural/test_pipeline_manifest_directive_composer_node.py`
- `_bmad-output/implementation-artifacts/7a-2-codex-self-review-2026-04-29.md`

### Codex G6 Self-Review (T10)

Self-review artifact: `_bmad-output/implementation-artifacts/7a-2-codex-self-review-2026-04-29.md`.

Summary: PASS-WITH-NOTE. 7a.2-focused verification passes; full requested pytest battery passes with a temporary `vi` PATH shim. The unshimmed environment has one unrelated 7a.1 editor fallback failure in `test_directive_confirm_or_edit_prompt.py`.

### Claude Final Code-Review (T11)

**Report:** `_bmad-output/implementation-artifacts/7a-2-code-review-2026-04-29.md`
**Verdict:** PASS-WITH-PATCH (2 PATCH / 1 DEFER / 1 DISMISS)

**Claude remediation cycle 1 (P1 + P2 applied 2026-04-29):**

- **P1 (BH-1, AA-1):** Updated `tests/integration/marcus/test_production_runner_gate_pause_resume.py` — flipped `test_approve_verdict_resumes_execution` and `test_edit_verdict_propagates_to_resume_state` to assert the post-resume `GateBypassError` raise at G2C (the next active pause-point after G1 in the live manifest). The original tests were OUTDATED — they pre-dated the FR-A23 invariant and relied on silent active-gate bypass behavior that 7a.2 correctly closes. The edit-verdict test still verifies the edit_payload propagation via the resume-command.json artifact (written before the raise). Filed `7a-2-deferred-resume-mode-multi-gate-pause` follow-on for the substrate-evolution work to add pause-and-yield semantics during resume (currently raises rather than pausing at subsequent active gates; that's a bigger increment than 7a.2 scope).
- **P2 (EH-1):** Sync-test order-dependence resolved indirectly — the failing `test_gate_fold_manifest_is_in_sync` was a SIDE EFFECT of P1's failed gate-pause-resume tests leaving the runner in an in-progress state that wrote to the on-tree gate_fold_manifest.yaml. After P1's test fixes prevented the failed-state writes, EH-1 cleared without requiring a direct fix. Verified non-flaky across 3 consecutive wider-battery runs (247 passed / 1 skipped × 3).

**Claude verification battery (post-remediation):**

```
.venv/Scripts/python.exe -m pytest tests/unit/manifest tests/integration/marcus tests/composition tests/parity tests/structural tests/specialists/texas tests/specialists/_scaffold -q --tb=line
→ 247 passed, 1 skipped (× 3 consecutive runs; non-flaky)

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
→ exit 0; trace records orchestration_only_nodes: [directive-composer]

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7a-2-manifest-fold-flags-compiler-extension.md
→ PASS

.venv/Scripts/python.exe -m ruff check app/manifest tests/unit/manifest tests/integration/marcus/test_gate_bypass_refusal.py tests/integration/marcus/test_production_runner_gate_pause_resume.py tests/structural scripts/utilities/check_pipeline_manifest_lockstep.py
→ All checks passed!

.venv/Scripts/lint-imports.exe
→ Contracts: 9 kept, 0 broken.
```

**Net:** 247 passed wider regression slice (up from 205 pre-7a.2; +42 net new tests over the 7a.1-close baseline). All 2 PATCH findings remediated; 1 DEFER filed; 1 DISMISS recorded with rationale (BH-2: 7a.1 editor fallback test brittleness against bare environments — out of 7a.2 scope).

**7a.1 deferred follow-on closure:** `7a-1-deferred-directive-composer-manifest-node` is CLOSED-by-7a.2 via AC-7.2-G (orchestration-only-node lockstep tolerance + actual `directive-composer` node registration in `state/config/pipeline-manifest.yaml`).

### N-Item / Rider Trace

- N1 PASS: audit emitter is additive and test-pinned.
- N2 PASS: Composition Spec §3.6 honored; §11 trigger did not fire for 7a.2.
- N4 PASS: no specialist body files touched.
- N9 PASS-PENDING-OPERATOR: folded/unfolded topology CLI outputs available for operator UX validation.
- N10 PASS: no manual sync step; audit YAML has structural sync test.
- A9/A11/A12 honored.

### Decision Needed / Halt-And-Adapt

No operator halt triggered. Note only: older epic/governance prose still describes 7a.2 as a Tier-2 bump, but the story/operator boundary for this cycle says Tier-1 patch with no schema or pack bump; implementation preserved `schema_version: v4.2-migration-stub-with-fold-flags` and `pack_version: v4.2`.
