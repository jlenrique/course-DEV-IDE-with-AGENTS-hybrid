# Migration Story 6.1: Production-Graph Runner — composition layer that turns substrate into a runnable trial

**Status:** review (implementation landed 2026-04-27; operator acceptance ratification pending)
**Sprint key:** `migration-6-1-production-graph-runner`
**Epic:** Slab 6 — Post-MVP Production Capability (NEW; opens with this story).
**Pts:** 13 (3-week-shaped story; substantial new orchestration integration across 5+ surfaces).
**Gate:** dual-gate (rationale: `substrate_shape` + `operator_acceptance_gate` — composition layer + first-trial verification both load-bearing).
**K-target:** ~1.4× (target ~30 / floor ~22; estimated honest K-floor will land per implementation phasing).

**Predecessors:** Slab 5a closed as **bounded-MVP unconditional SHIP** (2026-04-27 ratification). M5 conditions #1 (M2 Wondercraft), #2 (M3 Texas), #4 (Plausible-Token live verification) close via operator-presence; condition #3 was reframed as this Slab 6 opener per party-mode round 2026-04-27 (Winston + Murat + Quinn-R unanimous GREEN-WITH-CONCERNS).

**Authorship provenance:** authored 2026-04-27 in operator session immediately after 3-agent party-mode reframe. Cite Codex Phase A investigation as primary substrate evidence: `_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-27.md`.

---

## Why this story exists

The migration's Slab 5a M5 SHIP-CONDITIONAL verdict was reached without anyone surfacing that the migrated runtime had no callable live production-graph entry point. The 15-invariant audit matrix verified each substrate component's correctness in isolation; no audit step exercised the composition end-to-end. Codex's Phase A investigation on 2026-04-27 (Path c HALT) characterized the gap precisely: 6 missing integration points across manifest compiler, frozen graph artifacts, HIL gate pause/resume, LangSmith trace scoping, and trial lifecycle persistence.

This story is the load-bearing close for the gap. Done well, the migrated runtime can produce a real production trial through a real production graph against live OpenAI, registered in `state/config/runs/<trial-id>/` with `production_clone_launch_evidence=true` and a real LangSmith trace bound to the trial. Done poorly (silently inventing the production path, fabricating evidence), it would un-do the discipline that anti-pattern A16 (Composition-vs-Component Audit Gap) was filed to address.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Substrate-aware adaptation is the discipline; halt-and-surface is the right move when substrate disagrees with spec. Same pattern as 3.1 substrate adaptation, 5a.3 cost-engineering amendment, A15 + A16 remediation cycles.

---

## T1 Readiness Block

1. **Governance:** dual-gate per `substrate_shape` (composition layer is new substrate) + `operator_acceptance_gate` (first real production trial is operator-verified). Add to `docs/dev-guide/migration-story-governance.json` as Slab 6 inaugural entry.

2. **Substrate inheritance (BINDING):**
   - `_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-27.md` — Codex Phase A investigation; primary substrate evidence; the 6 missing integration points listed there are the deliverable scope.
   - `_bmad-output/upstream-state.md` condition #3 reframed as this story.
   - `_bmad-output/implementation-artifacts/m5-decision.md` Scope Clarification (2026-04-27) bounds the MVP claim and points at this story.
   - `docs/dev-guide/specialist-anti-patterns.md` A15 + A16 entries — the pattern this story addresses.
   - `_bmad-output/planning-artifacts/deferred-inventory.md` `5a-2-production-graph-entrypoint-substrate-gap` — RESOLVES on this story's close.

3. **Reusable substrate (existing pieces this story COMPOSES):**
   - Specialist LangGraph builders at `app/specialists/<name>/graph.py` (14 of them; all live-OpenAI-capable via `app.models.adapter.make_chat_model` per per-specialist `model_config.yaml`).
   - Dispatch registry at `state/config/dispatch-registry.yaml` (`_status: production` per Codex Batch 1 B9).
   - Pipeline manifest at `state/config/pipeline-manifest.yaml` (33-step v4.2).
   - Frozen graph artifacts at `runtime/graphs/v42/` (`compiled-graph-digest.txt` + `manifest-snapshot.yaml` + `dispatch-registry-snapshot.yaml` + `pack-version.txt`).
   - Cascade YAML at `runtime/config/model_cascade.yaml` (real OpenAI catalog IDs per A15 remediation).
   - Pricing YAML at `runtime/config/openai_pricing.yaml`.
   - HIL gate machinery at `app/gates/resume_api.py` (FR34 tamper-evidence path).
   - Cost machinery at `app/runtime/economics.py` (per-trial cost report per 5a.3).
   - LangSmith integration: trace upload happens automatically when `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` set.
   - Lint guard at `tests/test_no_fictitious_model_ids.py` + catalog-membership test at `tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` — must remain GREEN.
   - Live-OpenAI smoke at `tests/live/test_openai_cascade_tiers_smoke.py` — must remain skip-clean by default + green when keys set.

4. **NOT-existing substrate (the gap this story closes; per Codex Phase A):**
   - **Manifest compiler integration:** `app/manifest/compiler.py` currently produces `_passthrough_node` handlers per node. Real compilation must resolve each manifest node to its dispatch-registry-backed specialist graph builder.
   - **Invokable graph artifact:** `runtime/graphs/v42/` has metadata but no serialized invokable graph or loader. Either build a runtime composer that recomposes the graph from manifest + registry on each trial start, OR persist a serialized invokable graph at frozen-pack-build time. (Operator decision needed at T1; recommend recomposer for flexibility.)
   - **HIL gate pause/resume runtime semantics:** the M3 harness auto-verdicts deterministically at gates. Production runner must pause execution at gate nodes, persist trial state, accept `OperatorVerdict` via the existing `app/gates/resume_api.py` FR34 path, and resume from the persisted checkpoint.
   - **LangSmith trace scoping with trial_id:** specialist invocation must be wrapped in a LangSmith trace context that binds `trial_id` as metadata so `app/runtime/economics.py::measure_trial_cost(trial_id)` can find the trace's spans.
   - **Production TrialEnvelope schema:** distinct from `marcus.orchestrator.m3_trial.TrialEnvelope` (which is a deterministic local-test envelope). Production envelope records `production_clone_launch_evidence=true` only after a real graph invocation completes; persists artifacts to `state/config/runs/<trial-id>/`.
   - **Trial lifecycle persistence:** trial registration → in-flight state → gate-pause checkpoint → gate-resume → completion record. The shape exists in pieces (registration in `app/marcus/cli/trial.py` shim; resume API at `app/gates/resume_api.py`); the lifecycle composition does not.

5. **Severance posture:** primary repo at `upstream/master @ 3ed7c56` remains frozen reference; FR60 backport stays closed.

---

## TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1):** This story builds the production-graph runner ONLY. NOT in scope:
- Operator-experience polish (ad-hoc CLI mode → Batch 3 B-adhoc; HUD modernization → Batch 3 B-hud)
- Cost-optimization (5a.3 deferred Layer-1/Layer-2 cascade collapse, etc.)
- Any specialist refactor (specialists are scaffold-conformant per Slab 2; do not modify)
- Any new gate semantics (use existing G1/G2C/G3/G4 + resume_api per FR34)
- Any new manifest version (v4.2 stays canonical; production runner consumes existing manifest)

**Decision #2 — Recomposer vs serialized graph:** the production runner RECOMPOSES the LangGraph from manifest + dispatch registry on each trial start (rather than persisting a serialized invokable graph at frozen-pack-build time). Rationale: operator-editable cascade YAML + dispatch registry remain authoritative; recomposition picks up registry promotion / cascade rebalance without requiring frozen-pack rebuild ceremony. Performance impact: graph composition is O(33-node) traversal at trial start (~milliseconds), negligible vs trial duration (~30-60 min). The `runtime/graphs/v42/dispatch-registry-snapshot.yaml` and `runtime/graphs/v42/manifest-snapshot.yaml` remain frozen artifacts for replay-regression purposes; the recomposer reads the LIVE registry/manifest by default and the snapshot only when explicitly invoked for replay (FR51).

**Decision #3 — Production TrialEnvelope schema (Pydantic v2 strict, four-file-lockstep per Pydantic checklist):**

```python
# app/models/runtime/production_trial_envelope.py
class ProductionTrialEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    schema_version: Literal["production-trial-envelope.v1"] = "production-trial-envelope.v1"
    trial_id: UUID
    preset: Literal["production", "explore"]
    corpus_path: str
    operator_id: str
    started_at: datetime  # tz-aware
    completed_at: datetime | None = None  # None while in-flight
    status: Literal["registered", "in-flight", "paused-at-gate", "completed", "failed"]
    paused_gate: Literal["G1", "G2C", "G3", "G4"] | None = None
    langsmith_trace_id: str | None = None  # populated when first specialist fires
    production_clone_launch_evidence: bool  # MUST be True only after a real graph invocation completes a step
    cost_report_path: Path | None = None  # populated at completion
    artifact_paths: list[Path] = Field(default_factory=list)
```

Four-file-lockstep:
- Model: `app/models/runtime/production_trial_envelope.py`
- JSON Schema: `schema/production_trial_envelope.v1.schema.json`
- Shape-pin tests: `tests/unit/runtime/test_production_trial_envelope_strict.py`
- Golden fixture: `tests/fixtures/runtime/production_trial_envelope_golden.json`

**Decision #4 — HIL gate pause/resume mechanism:** at gate nodes, the production runner:
1. Persists the LangGraph state checkpoint (uses LangGraph's checkpointer API per Slab 1 substrate).
2. Emits the appropriate DecisionCard (G1/G2C/G3/G4 per gate kind) via existing `app/models/decision_cards/` machinery.
3. Updates `ProductionTrialEnvelope.status` → `paused-at-gate` + `paused_gate` set.
4. Returns control to the operator (via CLI / HTTP / MCP transport surface).
5. On resume: reads `OperatorVerdict` via `app/gates/resume_api.py::resume_from_verdict`, restores LangGraph state from checkpoint, continues execution from the gate node onward.

The mechanism MUST honor FR34 tamper-evidence (decision-card-digest binding + anti-replay tuple per Story 3.3 W-R1-3.3-2). NO bypass paths.

**Decision #5 — LangSmith trace binding:** wrap the entire trial invocation in a LangSmith trace context with metadata `{"trial_id": str, "preset": str, "operator_id": str}`. Each specialist node invocation becomes a child run within this trace. `app.runtime.economics.measure_trial_cost(trial_id)` filters trace spans by `extra.metadata.trial_id == trial_id`.

---

## Story

As a **migration operator running the first real production trial against the migrated runtime per FR52 + the production-graph-runner gap closure (post-MVP-SHIP)**,
I want **a real production-graph runner at `app/marcus/orchestrator/production_runner.py` that composes the LangGraph from manifest + dispatch registry, dispatches specialist work to live OpenAI per cascade YAML, pauses at HIL gates per FR34, captures LangSmith trace bound to trial_id, persists per-trial cost report per 5a.3, registers the trial with `production_clone_launch_evidence=true`, and is invokable via `python -m app.marcus.cli trial start --preset production --input <corpus-path>`**,
So that **the migration's actual production capability is demonstrably real (not deterministic-harness-wrapped), the 5a.2 production-clone-launch rider closes properly, and post-MVP Slab 6 establishes the composition-verification dimension that A16 (Composition-vs-Component Audit Gap) flagged as a structural prevention**.

---

## Acceptance Criteria

### AC-6.1-A — `app/manifest/compiler.py` real-handler resolution

- **Given** the manifest compiler currently produces `_passthrough_node` handlers per Codex Phase A
- **When** dev replaces passthrough handlers with dispatch-registry-backed specialist graph builders for the run lane
- **Then** `compile_run_graph(...)` returns an invokable LangGraph where each node dispatches to its specialist's real `_act` node (or to a HIL gate node where applicable).
- **Test pin (DUAL-GATE acceptance gate-1 — composition):** `tests/integration/manifest/test_compiler_real_dispatch.py` — N tests (one per active specialist + one per gate node) asserting the compiled graph node references resolve to the specialist's graph builder (or gate emitter), NOT to a passthrough placeholder.

### AC-6.1-B — `app/marcus/orchestrator/production_runner.py` composition + invocation

- **Given** the real-handler compiler from AC-A + dispatch registry + cascade YAML
- **When** dev authors `run_production_trial(corpus_path: Path, preset: Literal["production","explore"], operator_id: str, trial_id: UUID | None = None) -> ProductionTrialEnvelope`
- **Then** function (a) registers the trial via existing `app/marcus/cli/trial.py` registration ceremony, (b) composes the LangGraph from manifest + registry, (c) opens LangSmith trace context with trial_id metadata, (d) invokes the graph against the input bundle, (e) routes specialist calls through cascade YAML to real OpenAI via `app.models.adapter.make_chat_model`, (f) pauses at HIL gate nodes per Decision #4, (g) at completion writes per-trial cost report per 5a.3 contract.
- **Test pin:** `tests/integration/marcus/test_production_runner_invocation.py` — 3 tests: (a) trial registers with `status="registered"` then transitions to `in-flight`; (b) at least one specialist node fires (synthetic LangSmith trace fixture proving graph composed not passthrough); (c) at gate node, runner pauses (status=`paused-at-gate`) and accepts an `OperatorVerdict` to resume.

### AC-6.1-C — `ProductionTrialEnvelope` Pydantic v2 strict (four-file-lockstep per checklist)

- **Given** Decision #3 schema
- **When** dev authors model + JSON Schema + shape-pin tests + golden fixture
- **Then** four-file-lockstep present; tz-aware datetime enforced; closed-set Literals red-rejected; `production_clone_launch_evidence` required boolean (no default; explicit set required).
- **Test pin:** `tests/unit/runtime/test_production_trial_envelope_strict.py` — 4 tests: strict_config + tz-aware + Literal-red-rejection + production_clone_launch_evidence-explicit-required.

### AC-6.1-D — HIL gate pause/resume per Decision #4 + FR34

- **Given** the production runner reaches a gate node
- **When** runner persists LangGraph checkpoint + emits DecisionCard + transitions status to `paused-at-gate`
- **Then** operator can submit verdict via existing CLI / HTTP / MCP transport; runner resumes from checkpoint via `resume_from_verdict`; FR34 tamper-evidence intact (decision-card-digest binding + anti-replay tuple).
- **Test pin (DUAL-GATE acceptance gate-2 — operator acceptance):** `tests/integration/marcus/test_production_runner_gate_pause_resume.py` — 4 tests: (a) approve verdict resumes execution; (b) edit verdict propagates via RunState to downstream nodes; (c) reject verdict halts (per gate semantics); (d) digest-mismatch verdict raises GateError("digest_mismatch") and refuses resume.

### AC-6.1-E — LangSmith trace binding with trial_id (Decision #5)

- **Given** the production runner wraps invocation in trace context
- **When** trial completes and `app.runtime.economics.measure_trial_cost(trial_id)` is called
- **Then** trace spans filter correctly by `extra.metadata.trial_id == trial_id`; per-agent + per-model + total cost computed from real spans.
- **Test pin:** `tests/integration/runtime/test_production_runner_trace_binding.py` — 2 tests: (a) trace metadata contains trial_id (synthetic-trace fixture); (b) `measure_trial_cost(trial_id)` returns non-None cost report from production-runner trace.

### AC-6.1-F — `production_clone_launch_evidence` boolean discipline

- **Given** the runner has an honest discipline boundary per the B-extra-shim precedent (Codex 2026-04-27)
- **When** runner completes a real graph invocation that involved at least one live OpenAI specialist call
- **Then** `ProductionTrialEnvelope.production_clone_launch_evidence` is set to `True`. If the runner falls back to offline mode (no OPENAI_API_KEY OR `--allow-offline-cost-report` flag), evidence stays `False`.
- **Test pin:** `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py` — 3 tests: (a) live mode (mocked OpenAI client) → evidence=True; (b) offline mode → evidence=False; (c) live mode with zero specialist calls fired → evidence=False with explicit reason in envelope.

### AC-6.1-G — End-to-end live smoke (NEW; Quinn-R Q3 / A16 counter-pattern requirement)

- **Given** `OPENAI_API_KEY` set + `LANGSMITH_API_KEY` set
- **When** operator runs `pytest tests/live/test_production_trial_smoke.py -m live -q` against a tiny synthetic corpus (cost cap: ~$0.10)
- **Then** ONE real trial runs end-to-end: graph composes; at least one specialist node fires against real OpenAI; trial reaches a HIL gate (or completes if no gates in tiny-corpus path); LangSmith trace uploads; cost report writes correctly; `production_clone_launch_evidence=True`.
- **Test pin:** `tests/live/test_production_trial_smoke.py` — 1 parametrized test (`pytest -m live` gated; skips when key absent; explicit cost cap assertion).

### AC-6.1-H — A16 counter-pattern compliance (composition-exercise audit)

- **Given** A16 (Composition-vs-Component Audit Gap) names integration-exercise AC as required dimension
- **When** this story lands
- **Then** AC-G provides the integration-exercise verification; the `bmad-testarch-trace` traceability matrix entry for FR52 (head-to-head parity) flips from PARTIAL to TRACED (live-trial verification path now exists); future M-gate audits cite this story as the precedent for "composition-exercise audit" as a required dimension alongside referent-validity audit.
- **Test pin:** absorbed in AC-G + the FR-trace matrix update at story close (no new test).

### AC-6.1-I — Anti-pattern catalog harvest

NO new entries expected at this story; A16 is the precipitating entry. If a composition-defect-class anti-pattern surfaces during dev (e.g., "subgraph state-isolation breaks parent-graph reducer"), file as candidate per harvest-gate.

### AC-6.1-J — TEMPLATE compliance

R1, R6, R8 honored. Slab 6 inaugural — establishes the post-MVP TEMPLATE precedent for stories that compose existing substrate rather than build new substrate.

### AC-6.1-K — D12 close protocol (DUAL-GATE; FIVE-line)

1. **Invariant preservation:** all 15 invariants from 5a.4 matrix REMAIN preserved (this story composes them; does not modify any). FR34 HIL tamper-evidence honored throughout. FR43 frozen-graph-version-ceremony respected (production runner reads live registry/manifest by default; replay-regression mode reads frozen snapshot per FR51).
2. **Anti-pattern harvest:** A16 counter-pattern compliance per AC-H; future M-gate audits gain composition-exercise audit dimension.
3. **Migration-guide update:** §"Production Runner" added — composition mechanism + recomposer rationale + HIL gate pause/resume + LangSmith trace binding + production_clone_launch_evidence discipline.
4. **TEMPLATE compliance:** R1, R6, R8.
5. **Dual-gate gate-2 (operator acceptance):** operator runs `pytest tests/live/test_production_trial_smoke.py -m live -q` with real keys + ratifies that one real production trial completes through the production runner (~$1-2 cost; closes M5 condition #3 for real, no longer reframed-as-Slab-6-opener).

### AC-6.1-L — Sprint-status state-flips at filing AND close

At filing: `migration-6-1-production-graph-runner: ready-for-dev` (NEW Slab 6 epic block opens). At close: `migration-6-1-production-graph-runner: done`; `migration-epic-6-post-mvp-production: in-progress` (new epic; further Slab 6 stories pending). M5 condition #3 in `_bmad-output/upstream-state.md` flips from REFRAMED-AS-SLAB-6-OPENER to RESOLVED-2026-XX-XX. `_bmad-output/planning-artifacts/deferred-inventory.md` `5a-2-production-graph-entrypoint-substrate-gap` flips from DEFERRED-CONTINUES to RESOLVED.

---

## File Structure Requirements

### NEW files

- `app/marcus/orchestrator/production_runner.py` — composition + invocation (~300-500 LOC est.)
- `app/models/runtime/production_trial_envelope.py` — Pydantic v2 strict envelope
- `schema/production_trial_envelope.v1.schema.json` — emitted JSON Schema
- `tests/fixtures/runtime/production_trial_envelope_golden.json`
- `tests/integration/manifest/test_compiler_real_dispatch.py` (AC-A)
- `tests/integration/marcus/test_production_runner_invocation.py` (AC-B)
- `tests/unit/runtime/test_production_trial_envelope_strict.py` (AC-C)
- `tests/integration/marcus/test_production_runner_gate_pause_resume.py` (AC-D)
- `tests/integration/runtime/test_production_runner_trace_binding.py` (AC-E)
- `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py` (AC-F)
- `tests/live/test_production_trial_smoke.py` (AC-G; `pytest -m live` gated)

### MODIFIED files

- `app/manifest/compiler.py` — replace `_passthrough_node` with dispatch-registry-backed specialist graph builder resolution for the run lane (AC-A).
- `app/marcus/cli/trial.py` — wire to `production_runner.run_production_trial(...)` in production mode; preserve existing offline-mode discipline (`--allow-offline-cost-report` flag + `production_clone_launch_evidence=false` when offline).
- `marcus/orchestrator/m3_trial.py` — UNCHANGED. The deterministic harness stays as Slab 3 close artifact + replay-regression baseline. The trial CLI just stops wrapping it as the production path.
- `docs/dev-guide/migration-story-governance.json` — add Slab 6 inaugural entry for `6-1`; bump version.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Production Runner" added per D12.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-L.
- `_bmad-output/upstream-state.md` — condition #3 flip per AC-L.
- `_bmad-output/planning-artifacts/deferred-inventory.md` — `5a-2-production-graph-entrypoint-substrate-gap` flip per AC-L.

---

## Testing Requirements

**K-target ~1.4× (target ~30 / floor ~22).** AC-A: N tests (parametrize-collapsible to ~3 K-floor units per Murat M-R18 same-property collapse) + AC-B: 3 + AC-C: 4 + AC-D: 4 + AC-E: 2 + AC-F: 3 + AC-G: 1 = honest **~20 K-floor**. RIDER additions during dev: AC-D digest-mismatch raises (+1); AC-F live-mode-with-zero-specialist-calls edge (+1) = **~22 K-floor (meets floor)**.

**Sandbox-AC:** PASS expected (uses shipped `langsmith` + `openai` Python deps + `pytest.skip` on missing service). Live smoke gated by `pytest -m live` per A15 + A16 counter-pattern discipline.

---

## Effort estimate

**~20-40 hours total Codex time** per Codex Phase A investigation report. Phasing recommendation:
- Phase 1 (~6-8 hr): Decision #2 ratification (recomposer vs serialized) + AC-A (compiler real-handler resolution) + AC-C (envelope schema four-file-lockstep)
- Phase 2 (~6-8 hr): AC-B (production_runner.py composition + invocation) + AC-D (HIL gate pause/resume per FR34) + AC-F (evidence discipline)
- Phase 3 (~4-6 hr): AC-E (LangSmith trace binding) + AC-G (live smoke; build only, operator runs)
- Phase 4 (~4-6 hr): D12 close + AC-H counter-pattern compliance + sprint-status / upstream-state / deferred-inventory updates + migration-guide §

Halt-and-adapt budget built in: any phase that hits substrate disagreement HALTS and surfaces (3.1 + 5a.3 + A15 + A16 precedent). Total wall-clock with halt-allowance: 3-week-shaped story; expect at least one halt-and-ratify cycle.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness + substrate verification

Confirmed the Phase A finding that `app/manifest/compiler.py` still used
`_passthrough_node` for manifest nodes. Additional live-tree drift found:
`state/config/dispatch-registry.yaml` omitted migrated `texas` and `kira`
builders even though the manifest routes production steps to both. The story
implementation added those registry rows and treats remaining non-registry
manifest nodes as explicit orchestration nodes, not passthrough evidence.

### Decision #2 ratification (recomposer vs serialized graph)

Implemented the default recomposer path. `compile_run_graph(...)` reads the live
manifest and dispatch registry at trial start; frozen v42 artifacts remain
replay references.

### Implementation summary

- Added strict `ProductionTrialEnvelope` plus JSON Schema, golden fixture, and
  shape-pin tests.
- Added `compile_run_graph(...)` production handler resolution. Active migrated
  specialist nodes resolve to registry-backed graph builders; `G1/G2C/G3/G4`
  resolve to gate emitters; structural/unmigrated nodes are explicit
  orchestration handlers.
- Added `app/marcus/orchestrator/production_runner.py` with registration,
  in-flight persistence, live specialist probe dispatch, LangSmith-compatible
  trace metadata fixture, cost-report persistence, DecisionCard pause,
  checkpoint persistence, and FR34 resume validation.
- Rewired `app.marcus.cli trial start` to use the production runner while
  preserving offline cost-report discipline.

### Live-trial evidence (per AC-G + dual-gate gate-2)

Codex-side live smoke passed on 2026-04-27:
`pytest tests/live/test_production_trial_smoke.py -m live -q` -> `1 passed`.
Formal dual-gate operator ratification remains pending before this story should
be flipped from `review` to `done`.

### Verification

Targeted verification:
- `pytest tests/unit/runtime/test_production_trial_envelope_strict.py tests/integration/manifest/test_compiler_real_dispatch.py tests/integration/marcus/test_production_runner_invocation.py tests/integration/marcus/test_production_runner_gate_pause_resume.py tests/integration/marcus/test_production_clone_launch_evidence_discipline.py tests/integration/runtime/test_production_runner_trace_binding.py tests/unit/manifest/test_compiler.py tests/integration/manifest/test_loader_compile_invoke.py tests/integration/marcus/test_trial_cli.py -q` -> `38 passed`.
- `pytest tests/live/test_production_trial_smoke.py -m live -q` -> `1 passed`.
- `ruff check` on touched app/test files -> pass.

### File List

- `app/manifest/__init__.py`
- `app/manifest/compiler.py`
- `app/manifest/lanes.py`
- `app/marcus/cli/trial.py`
- `app/marcus/orchestrator/production_runner.py`
- `app/models/runtime/__init__.py`
- `app/models/runtime/production_trial_envelope.py`
- `app/models/state/run_state.py`
- `pyproject.toml`
- `schema/production_trial_envelope.v1.schema.json`
- `state/config/dispatch-registry.yaml`
- `tests/fixtures/runtime/production_trial_envelope_golden.json`
- `tests/integration/manifest/test_compiler_real_dispatch.py`
- `tests/integration/marcus/test_production_runner_gate_pause_resume.py`
- `tests/integration/marcus/test_production_runner_invocation.py`
- `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py`
- `tests/integration/marcus/test_trial_cli.py`
- `tests/integration/runtime/test_production_runner_trace_binding.py`
- `tests/live/test_production_trial_smoke.py`
- `tests/unit/runtime/test_production_trial_envelope_strict.py`
- `docs/dev-guide/langgraph-migration-guide.md`
- `docs/dev-guide/migration-story-governance.json`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md`
