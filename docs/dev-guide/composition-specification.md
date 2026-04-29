# Composition Specification — Option B (Append-Only Envelope, Path A-prime)

**Purpose:** governing reference for how multiple specialist agents compose into a single executing LangGraph in this app. Read this before evolving any specialist contract, adding a new specialist, changing a gate, modifying the production runner, or diagnosing a composition-class defect during trial production.

**Scope:** the composition substrate as it exists post-Slab-6.0 (envelope + adapter + composition-test discipline) and post-Slab-6.1 (production runner consuming substrate). Out of scope: per-specialist scaffold internals (covered by `app/specialists/_scaffold/` + `langgraph-migration-guide.md §12`), individual specialist business logic, BMAD methodology itself.

**Authorship:** drafted 2026-04-27 in operator session immediately after Slab 6.1 dispatch authored. Living document — extend as trial evidence accumulates per §10 Decision Log + §11 Migration Triggers.

**Binding:** this spec is normative for Option B evolution decisions. Any change to the composition substrate (envelope shape, adapter contract, dependency_map mechanism, gate precedence rule, composition-test discipline) requires party-mode ratification + an entry in §10 Decision Log. Any decision to escalate from Option B to Option C requires the trigger conditions in §11 to be met + party-mode ratification.

---

## 1. The Four Composition Options (canonical reference)

Any system that composes multiple agents into a single executing graph picks one of four design points. Each carries different trade-offs along five axes: contract complexity, evolution cost, runtime flexibility, audit/replay clarity, and substrate-framework alignment.

### Option A — Shared-State Mutation
- **Mechanism:** all specialists read from + write to a single shared state carrier (e.g., a mutable dict). Downstream specialists discover upstream output by inspecting whatever the upstream wrote.
- **Contract complexity:** trivial.
- **Evolution cost:** initially low; explodes after ~3-5 specialists as implicit coupling accumulates.
- **Runtime flexibility:** maximum.
- **Audit/replay clarity:** none.
- **When right:** prototypes; single-author short-lived experiments; never for production.
- **A17 fingerprint:** this is what causes A17 by construction. Avoid.

### Option B — Append-Only Envelope with Explicit Contributions  *(THIS APP — Path A-prime)*
- **Mechanism:** each specialist's output appends as a typed `SpecialistContribution` to a `ProductionEnvelope` accumulator. Downstream specialists declare dependencies via `dependency_map` + read upstream contributions by `specialist_id`. An adapter at the runner layer marshals between per-specialist scaffold contracts (`cache_prefix` scratch) and the cross-specialist envelope. Specialists themselves stay isolated.
- **Contract complexity:** moderate. Two carriers (cache_prefix + envelope); adapter holds knowledge of both.
- **Evolution cost:** moderate; pays a per-evolution tax (dependency_map declaration, gate-precedence reasoning, adapter updates for cross-cutting concerns).
- **Runtime flexibility:** good for linear chains; awkward for fan-out, parallel dispatch, mid-execution partial state, sub-specialist coordination.
- **Audit/replay clarity:** strong. Output digests + contribution accumulation + immutability invariant.
- **Substrate-framework alignment:** partial. LangGraph natively supports subgraph composition (Option C); Option B uses the framework for graph traversal but not for state composition.
- **When right:** when isolated-execution specialists already exist + cannot be redesigned cheaply; when chain composition is mostly linear; when audit + replay matter more than peak runtime flexibility.

### Option C — LangGraph Subgraph Composition (parent-graph reducers)
- **Mechanism:** each specialist is a typed LangGraph subgraph with declared state schema. The parent graph defines reducers that merge subgraph state into parent state. State channels are typed; updates flow through declared reducers, not raw mutation.
- **Contract complexity:** higher upfront (every specialist declares its subgraph state schema + reducer contract); lower over time (composition is native, not adapter-mediated).
- **Evolution cost:** higher to land initially; lower per-evolution thereafter.
- **Runtime flexibility:** maximum within LangGraph semantics; native fan-out, parallel dispatch, partial state, hierarchical gates.
- **Audit/replay clarity:** strong (LangGraph checkpointer + LangSmith trace native).
- **Substrate-framework alignment:** maximum. This is what LangGraph IS.
- **When right:** when designing fresh; when high evolution rate justifies the upfront cost; when fan-out / parallel / hierarchical-gate patterns are needed.
- **Migration target from Option B** when the triggers in §11 fire.

### Option D — Message-Passing / Event-Bus
- **Mechanism:** specialists publish typed events to a bus; downstream specialists subscribe. State is implicit in the event stream.
- **Contract complexity:** moderate (typed events + subscription contracts) but spread across many surfaces.
- **Evolution cost:** low for adding subscribers; high for changing event shapes (broadcast change).
- **Runtime flexibility:** maximum for async / concurrent / fan-out patterns.
- **Audit/replay clarity:** strong (replay the event log).
- **Substrate-framework alignment:** none with LangGraph; would require building the bus on top.
- **When right:** parallel multi-trial workflows; async producer/consumer patterns; multi-tenant trial environments. Out of scope for current bounded-MVP claim; potential Slab 7+ work if scale demands.

**This app uses Option B. The rest of this document is normative for Option B.**

---

## 2. Why this app uses Option B (decision provenance)

**The deviation from the implicitly-planned Option C happened at Slab 2 design time without anyone naming the composition trade-off.** The original LangGraph migration plan implicitly assumed Option C — that's what LangGraph IS natively. What actually happened in Slab 2:

1. **M3 deterministic harness drove the scaffold shape.** The 9-node scaffold (`receive → plan → act → verify → reflect → emit_spans → gate_decision → finalize → handoff`) was designed for *isolated* execution because that's what the M3 replay-regression harness needed.
2. **Per-specialist `gate_decision` baked in.** Each specialist owns its own gate interrupt; designed for M3 auto-verdict.
3. **`cache_prefix` as scratch.** Each specialist's `_act` writes to `RunState.cache_state.cache_prefix` as its own scratch space — never imagined as a cross-specialist accumulator.
4. **No Composition Specification step in BMAD architecture-authoring.** Per anti-pattern P3 — the composition assumption survived because it was never exercised end-to-end.

By Slab 6.1's first attempt, the substrate was 14 specialists deep into Option-B-by-default. The strict-AC HALT (2026-04-27) discovered the substrate gap structurally:
- Per-specialist gates fire before production-level G1
- `cache_prefix` overwrites instead of accumulates
- Two-phase `_plan`/`_act` shape doesn't map to single-node parent-graph execution

The 5-agent party-mode round 2026-04-27 (Winston + Murat + Amelia + Quinn-R + Mary) considered three paths:
- **Path A (Codex original):** adapter wraps M3 harness; composition stays harness-shaped
- **Path A-prime (Winston variant):** envelope state-key alongside `cache_prefix`; specialists unchanged; adapter at runner layer
- **Path B (implicit):** redesign 14 specialists as Option C subgraphs (~3-6 months restart)

Path A-prime ratified unanimously. Rationale: substrate-aware adaptation preserves 14 working specialist artifacts + M3 replay-regression baseline + deterministic harness path; adds composition substrate at runner layer only; ~8pt total cost (Slab 6.0 substrate) vs ~3-6 months of restart.

**Anti-pattern catalog entries:**
- **A17 (Substrate Designed for Isolation, Composition Assumed)** — the substrate-level defect Path A-prime addresses
- **P3 (Composition-Shape Vote Without End-to-End Exercise)** — the process-level defect Composition Smoke gate addresses

Both are filed at `docs/dev-guide/specialist-anti-patterns.md`.

---

## 3. Option B mechanics — the substrate as built

### 3.1 The accumulator: `ProductionEnvelope`

Source: `app/models/runtime/production_envelope.py`. Pydantic v2 strict.

```python
class ProductionEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    schema_version: Literal["production-envelope.v1"] = "production-envelope.v1"
    trial_id: UUID
    contributions: list[SpecialistContribution] = Field(default_factory=list)

    def get_contribution(self, specialist_id: str) -> SpecialistContribution | None: ...
    def add_contribution(self, contribution: SpecialistContribution) -> None: ...  # raises if specialist_id already present
```

**Invariants (load-bearing):**
- Append-only within a trial; immutability via `add_contribution` raising on duplicate `specialist_id`
- Closed-set `Literal` red-rejection on `schema_version`
- Each contribution's `output_digest` is SHA256 of canonical-JSON-serialized output (sort_keys=True, separators=(",",":")) — enables replay-regression reproducibility
- Tz-aware `contributed_at`; `cost_usd >= 0.0`; `model_used` non-empty

**Multi-pass / repeated-specialist node behavior (Path Z; Slab 6.1 close 2026-04-27):** the immutability invariant means if the manifest topology has multiple nodes invoking the same specialist (e.g., Irene Pass 1 + Irene Pass 2), only the FIRST contribution lands; subsequent duplicate-specialist node invocations are skipped at the runner layer with an explicit log entry. This is the agreed Slab 6.1 close shape ("first contribution wins"). Path X (node-scoped contribution identity: `<specialist>:<node_index>`) and Path Y (per-pass envelope) are filed as enhancement candidates (`slab-6-1-multi-pass-envelope-path-x-or-y`) for when actual multi-pass production need emerges. See §10 Decision Log + §12 known limitation #7.

**Four-file-lockstep:** model + `schema/production_envelope.v1.schema.json` + `tests/unit/runtime/test_production_envelope_strict.py` + `tests/fixtures/runtime/production_envelope_golden.json`. Any change to the model requires lockstep updates to all four.

### 3.2 The contribution: `SpecialistContribution`

```python
class SpecialistContribution(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True, frozen=True)
    specialist_id: str = Field(..., min_length=1)
    contributed_at: datetime  # tz-aware enforced
    output: dict[str, Any]
    cost_usd: float = Field(..., ge=0.0)
    model_used: str = Field(..., min_length=1)
    output_digest: str  # SHA256 of canonical JSON
```

**`output: dict[str, Any]` is intentional.** Specialist outputs are heterogeneous (Texas returns a retrieval bundle; Kira returns a motion plan; Wanda returns audio metadata). The downstream specialist knows its own input shape — type-checking happens at the downstream specialist's input boundary, not at envelope construction. Trade-off: less type safety at the envelope; more ergonomic for diverse specialist outputs.

### 3.3 The translation layer: `ProductionDispatchAdapter`

Source: `app/marcus/orchestrator/dispatch_adapter.py`. The ONLY surface that knows about envelope-vs-cache_prefix shape differences.

```python
class ProductionDispatchAdapter:
    def invoke_specialist(
        self,
        *,
        specialist_id: str,
        envelope: ProductionEnvelope,
        dependency_map: dict[str, str],  # downstream-input-key → upstream-specialist-id
    ) -> ProductionEnvelope:
        """Returns updated envelope with new contribution appended."""
        # 1. INPUT: read upstream contributions from envelope per dependency_map;
        #          construct specialist's RunState.cache_state.cache_prefix from them
        # 2. INVOKE: call specialist's compiled subgraph end-to-end (full 9-node scaffold,
        #            including per-specialist gate_decision)
        # 3. OUTPUT: extract specialist output from RunState.cache_state;
        #            build SpecialistContribution; append to envelope copy; return
```

**Adapter invariants:**
- Specialists never read or write `production_envelope` directly — the field exists on `RunState` but is reserved for adapter snapshot persistence, not specialist consumption
- Specialists never know about `dependency_map` — that's the adapter's job
- Adapter copies the envelope before appending; original envelope unmodified (immutability at the envelope level)
- Adapter calls the specialist's compiled subgraph (NOT `_plan` + `_act` directly) — full 9-node scaffold runs; per-specialist gate_decision fires; replay-regression path preserved
- Adapter is the single point of cross-cutting concern routing (cost tally, trace context, gate precedence)

### 3.4 The runner consumer: `production_runner.run_production_trial(...)`

Source: `app/marcus/orchestrator/production_runner.py` (post-Slab-6.1 rewire).

For each specialist node in the composed graph traversal:
1. Build `dependency_map` for the node from manifest + dispatch-registry
2. Call `adapter.invoke_specialist(specialist_id=..., envelope=current_envelope, dependency_map=...)`
3. Update `current_envelope` with returned envelope-with-new-contribution
4. Continue traversal

Production-level gates (G1/G2C/G3/G4) wrap the whole traversal; per-specialist gates fire within each `invoke_specialist` call (their interrupts auto-resolve under production composition by default — see §3.5 gate precedence).

### 3.5 Gate precedence rule

**Two layers of gates exist:**
- **Per-specialist `gate_decision`:** internal to each specialist's 9-node scaffold; designed for M3 deterministic harness auto-verdict
- **Production-level gates:** G1 (post-pipeline), G2C (compositor), G3 (audio), G4 (final) per FR34; emit `DecisionCard`; pause execution + persist checkpoint; resume via `OperatorVerdict` through `app/gates/resume_api.py`

**Precedence rule (binding; resolved by Slab 6.1 N6 work):**
1. Per-specialist gates fire first within their owning specialist's subgraph traversal
2. Per-specialist gates auto-resolve under production composition (the production runner provides a synthetic OperatorVerdict that allows continuation; per-specialist gates retain their isolated-execution semantics for M3 harness, but are non-blocking under production composition)
3. Production-level gates pause the parent traversal at the gate node + persist checkpoint + emit DecisionCard
4. Operator resumes via `resume_from_verdict` → traversal continues from checkpoint

**Operator override path (rare):** if an operator wants per-specialist gate to be load-bearing under production composition (e.g., a safety-critical specialist whose gate must block production), the production runner accepts a `gate_overrides: dict[str, GateMode]` parameter that promotes named per-specialist gates to production-blocking. Default: all per-specialist gates non-blocking under production composition.

**Why this shape:** preserves M3 replay-regression invariant (per-specialist gates still fire + still auto-verdict deterministically in M3 harness) while making production composition tractable (operator only sees production-level gates by default + explicitly opts in to per-specialist gates when safety-critical).

### 3.6 Dependency_map sourcing

**Current shape (Slab 6.2 implementation, 2026-04-27): manifest-declared dependency keys with permanent runner-layer fallback.** `state/config/pipeline-manifest.yaml` may declare per-node `dependencies: dict[str, str]`, where each key is the downstream specialist input key and each value is the upstream specialist id whose `SpecialistContribution` should be read from the envelope.

**Resolution order:** `app/marcus/orchestrator/production_runner.py::_resolve_dependency_map(...)` reads manifest-declared dependencies first. If a node omits `dependencies` or declares an empty map, the runner uses `_default_dependency_map_for(...)`. This fallback retention is permanent: the fallback is the resolution mechanism for nodes that intentionally opt out of explicit manifest declaration. It is not deprecated and not transitional.

**Fallback rule:** the permanent fallback keeps the Slab 6.1 deterministic behavior:
- `Texas → CD` maps as `source_bundle`
- All other downstream calls use the immediately previous specialist contribution as `upstream_output`

**Resolution rule for missing dependencies:** if a manifest-declared or fallback-resolved dependency names an upstream specialist contribution that is absent from the current `ProductionEnvelope`, the runner raises `MissingUpstreamContributionError` with explicit `specialist_id` and `downstream_input_key` fields. Fail loud, not silent fallback.

**Resolution rule for circular dependencies:** the manifest validator at `state/config/pipeline-manifest.yaml` schema check + `app/manifest/compiler.py` reject circular declared dependencies at compile time. Production runner trusts the manifest; circular check is a manifest-level invariant, not a runtime check.

**Evolution rule:** any new specialist added should declare its upstream dependencies in the manifest at filing time unless it intentionally opts into permanent fallback resolution. The `bmad-create-specialist` generator should emit a manifest-entry stub alongside the 9-file specialist tree (deferred as `2c-4-generator-emit-manifest-dependency-stub`, which consumes this manifest format as its emission contract).

### 3.7 Persistence shape: trial envelope + production envelope coexist

Two distinct envelopes serialize at trial close:
- `ProductionTrialEnvelope` — trial-level metadata (trial_id, evidence flag, cost report linkage, manifest version, frozen-graph version, LangSmith trace ID, start/end timestamps)
- `ProductionEnvelope` — per-specialist contribution accumulator

`ProductionTrialEnvelope.production_envelope: ProductionEnvelope` field embeds the full envelope as a **required** field (NOT a persistence pointer; NOT optional). Rationale: trial close artifact is self-contained; replay-regression reads one file; LangSmith trace + cost report + envelope all reconcilable from a single trial-close JSON. Slab 6.1 bmad-code-review patch P-2 enforces the required-field shape.

Persistence path: `state/config/runs/<trial-id>/trial_envelope.json`.

**LangSmith trace ID — known limitation (Slab 6.1 close 2026-04-27):** `ProductionTrialEnvelope.trial_trace_id` currently records a synthetic placeholder rather than the real LangSmith trace ID. The actual specialist invocations DO emit real LangSmith spans with `extra.metadata.trial_id == <trial_id>` (cost rollup works correctly because cost flows from per-call LangChain runtime objects, not from the trial-level trace ID). Operator workaround: query LangSmith manually for spans with the trial_id metadata to find the real trace tree. Filed as `slab-6-1-langsmith-runner-trace-id-real-binding` (~2-3pt). See §10 Decision Log + §12 known limitation #6.

**Lifecycle invariants — known limitation (pre-existing; not Slab 6.1):** `ProductionTrialEnvelope` lacks cross-field validators for the `completed_at` / `paused_gate` / `cost_report_path` state matrix. Impossible lifecycle states are technically constructible (e.g., `completed_at` set + `paused_gate` set simultaneously). Filed as `production-trial-envelope-lifecycle-invariants` (DFR-6.1-5). See §12 known limitation #9.

---

## 4. Contract surfaces — concrete files + tests

| Surface | File | Test pin | Change protocol |
|---|---|---|---|
| Envelope model | `app/models/runtime/production_envelope.py` | `tests/unit/runtime/test_production_envelope_strict.py` | Four-file-lockstep + party-mode for breaking changes |
| Envelope JSON Schema | `schema/production_envelope.v1.schema.json` | (above) | Lockstep with model |
| Envelope golden | `tests/fixtures/runtime/production_envelope_golden.json` | (above) | Lockstep with model |
| Adapter contract | `app/marcus/orchestrator/dispatch_adapter.py` | `tests/integration/marcus/test_dispatch_adapter.py` | Party-mode for contract changes; dev-agent for internal refactor |
| Composition fixture | `tests/composition/composed_specialist_chain_harness.py` | (used by chain tests) | Dev-agent for harness extension; party-mode for invariant changes |
| Chain test (load-bearing) | `tests/composition/test_texas_to_cd_chain.py` | self | Add new chain tests per new specialist PR (chain-test-per-PR rule, §6) |
| Isolation invariant | `tests/composition/test_specialist_isolation_preserved.py` | self | Update parametrize when specialists added/removed |
| RunState extension | `app/models/state/run_state.py` | `tests/unit/models/state/test_run_state.py` + `test_schema_pin.py` | Lockstep with envelope; party-mode |
| Trial envelope | `app/models/runtime/production_trial_envelope.py` | `tests/unit/runtime/test_production_trial_envelope_strict.py` | Four-file-lockstep |
| Production runner | `app/marcus/orchestrator/production_runner.py` | `tests/integration/marcus/test_production_runner_*.py` + `tests/live/test_production_trial_smoke.py` | Dev-agent for internal; party-mode for adapter-contract or gate-precedence changes |
| Manifest compiler | `app/manifest/compiler.py` | `tests/integration/manifest/test_compiler_real_dispatch.py` | Pipeline-lockstep regime per `pipeline-manifest-regime.md` |
| Dispatch registry | `state/config/dispatch-registry.yaml` | (registered specialists test) | Pipeline-lockstep regime |
| Pipeline manifest | `state/config/pipeline-manifest.yaml` | (manifest validator) | Pipeline-lockstep regime; pack version policy |

---

## 5. Operator playbook — common evolutions under Option B

### 5.1 Add a new specialist
1. Run `bmad-create-specialist` generator with `--from-skill <skill-name>`
2. Generator emits 9-file specialist tree + atomically appends to `pyproject.toml` C3 row (per Story 2a.5 generator auto-emit)
3. Add manifest entry to `state/config/pipeline-manifest.yaml` declaring upstream dependencies (until `2c-4-generator-emit-manifest-dependency-stub` lands, this is manual)
4. Add dispatch-registry entry to `state/config/dispatch-registry.yaml`
5. Add chain test to `tests/composition/` covering the new specialist's primary upstream specialist (per chain-test-per-PR rule, §6)
6. Run `pytest tests/composition/ -q --tb=short` → expect new chain test passing
7. Run `pytest tests/composition/test_specialist_isolation_preserved.py -q --tb=short` → confirm isolation invariant still holds (parametrize updated for new specialist)
8. Run `pytest tests/specialists/<new-specialist>/ -q --tb=short` → specialist's isolated-execution tests pass
9. Substrate Inventory Checklist N1 (referent validity) + N12 (auth model) + N4 (isolation invariant) + N5 (state-flow contract): trace through the new specialist's surface

### 5.2 Change a specialist's output shape
1. Update specialist's `_act` body and return-type model
2. Identify all downstream specialists that read this specialist's contribution (grep manifest entries for upstream reference)
3. Update each downstream specialist's input-construction logic to handle new shape
4. Update chain tests covering all affected specialist pairs
5. Run replay-regression suite (`tests/replay/`) — if regression fires, the output shape change is a breaking change requiring trial envelope schema_version bump
6. If breaking: bump `schema_version` literal (production-envelope.v1 → v2); preserve v1 read path for replay; party-mode ratify

### 5.3 Add a new gate
1. Decide layer: per-specialist (internal to specialist scaffold) or production-level (G1/G2C/G3/G4 family)
2. **Per-specialist gate:** add to specialist's `gate_decision` node logic; isolated-execution tests cover; auto-resolves under production composition by default
3. **Production-level gate:** extend `app/gates/resume_api.py` + `app/models/decision_cards.py` with new gate type; extend production runner's gate-handler dispatch; FR34 tamper-evidence path applies
4. Update gate precedence rule documentation in §3.5 if the new gate has unusual precedence
5. Substrate Inventory Checklist N6 (gate boundary scope hierarchy): trace through the new gate

### 5.4 Diagnose a composition-class defect during trial production
1. **Symptom:** downstream specialist fails with "input not found" / "expected key X" / parse error on missing upstream output
2. **Diagnostic protocol:**
   - Inspect `state/config/runs/<trial-id>/trial_envelope.json` → check `production_envelope.contributions` list
   - Verify each upstream specialist (per manifest) has a contribution in the envelope
   - If missing: which specialist failed silently? (Check LangSmith trace for that specialist's run.)
   - If present but downstream parse fails: did the upstream specialist's output shape change? (Compare contribution `output` against downstream's expected shape.)
   - If present + correctly shaped: is the downstream specialist's `dependency_map` declaring the right upstream specialist_id? (Check manifest entry.)
3. **Common cause: dependency_map mismatch** — manifest declares specialist X as upstream, but downstream code reads from specialist Y. Fix: align manifest with code.
4. **Less common cause: per-specialist gate non-blocking under production composition** — specialist gated to "needs operator review" but production composition auto-resolved + continued. Fix: promote per-specialist gate to production-level via `gate_overrides` (§3.5), OR escalate gate to production layer.
5. **Rare cause: envelope immutability violation** — same specialist_id ran twice (loop in graph?). Adapter raises; trial halts. Fix: investigate graph composition, never silently silence.

### 5.5 Decide whether an evolution requires party-mode
**Party-mode required:**
- Any change to envelope model, JSON Schema, golden, or shape-pin tests (four-file-lockstep)
- Any change to adapter contract (input/output signature)
- Any change to gate precedence rule
- Any new composition mode (fan-out, parallel dispatch, etc.) — surface as candidate Option C migration trigger
- Any change to pipeline manifest dependency structure that breaks chain tests
- Promotion of per-specialist gate to production-blocking (`gate_overrides` change)

**Dev-agent authority (no party-mode):**
- Internal refactor of adapter (no contract change)
- New chain test covering already-existing specialist pair
- Specialist-internal logic change preserving output shape
- Documentation updates
- Test additions strengthening existing invariants

---

## 6. The composition-test discipline

**Every PR that adds or modifies a specialist MUST add or update a chain test in `tests/composition/`.** The chain test exercises the specialist with at least one upstream specialist (or downstream specialist if the new specialist is itself an upstream) end-to-end through `ProductionDispatchAdapter`.

**Chain test minimum content:**
- Uses `ComposedSpecialistChainHarness` fixture
- Exercises ≥2 real specialists end-to-end
- Asserts envelope-state propagation (NOT just output equality)
- Asserts envelope contribution accumulation (both specialists' contributions present, in order)
- Asserts downstream input was constructed from upstream contribution (proves dependency_map worked)
- Uses synthetic specialist outputs at LLM-call boundary (cost ~$0)

**Coverage goal:** ≥50% of manifest-declared specialist pairs covered by chain tests by end of trial cycle 5. Full DAG coverage is a Slab 7+ aspiration; chain-test-per-PR ensures incremental progress.

**Composition Smoke gate (operationalized 2026-04-27):** every slab-opener authoring step requires a Composition Smoke check at vote time. Smoke = a 30-line throwaway script that wires the slab's primary components together end-to-end. PASS-or-FAIL records as vote-evidence. Failing smoke disposition: re-scope, defer, or explicit-composition-shape-vote with named gap.

---

## 7. Substrate Inventory Checklist application to composition decisions

The N1–N12 checklist at `docs/dev-guide/substrate-inventory-checklist.md` is the standing pre-flight for any substrate-affecting work. For composition decisions specifically:

| N-item | Composition-relevance | When it fires |
|---|---|---|
| N1 — External-provider resource ID validity | Any new specialist with new model_id / API endpoint | New specialist filing |
| N2 — Composition exercise before vote | Any slab-opener vote | Slab opener authoring |
| N3 — Live-API smoke before MVP close | Any milestone vote | M-gate ratification |
| N4 — Per-component isolation invariant preserved post-composition | Any specialist scaffold change | Scaffold modification |
| N5 — Cross-component state-flow contract | Any new specialist OR dependency_map change | New specialist OR manifest evolution |
| N6 — Gate boundary scope hierarchy | Any new gate OR gate-precedence change | Gate addition / promotion |
| N7 — Replay regression verifies execution path | Any envelope or output_digest change | Envelope evolution |
| N8 — Cost machinery integration with real trace data | Any cost-rollup change | Cost engineering evolution |
| N9 — Operator-witnessed evidence at M-gate vote | Any M-gate decision | Milestone close |
| N10 — Anti-pattern catalog read at architecture-authoring time | Any new architecture spec | Spec authoring |
| N11 — Composition mode declared alongside isolated mode | Any new specialist OR contract change | Specialist filing OR contract evolution |
| N12 — Auth model verified via probe | Any new external integration | Integration filing |

**Mandatory N-item trace section** in any bmad-code-review deliverable per Slab 6.0 governance.

---

## 8. Friction vectors — known costs of Option B

These are the per-evolution taxes Option B pays vs Option C. Track them; they inform §11 migration triggers.

### 8.1 Dependency_map tax
Every new specialist requires a manifest entry declaring upstream dependencies. Generator-emit (deferred) would help but doesn't eliminate. Cost: ~5 LOC per specialist + maintenance burden when upstream changes.

### 8.2 Adapter cross-cutting concern bottleneck
Every cross-cutting concern (cost rollup, trace binding, gate precedence, error propagation, retry semantics) routes through the adapter. Adapter grows with each cross-cutting addition. Cost: adapter LOC scales linearly with cross-cutting concerns; refactor cost grows quadratically.

### 8.3 Cache_prefix vs envelope cognitive duality
Two carriers exist; every code reader has to hold both shapes. Mistakes look like A17 (writing to wrong carrier; reading from wrong carrier). Cost: per-developer onboarding time + per-PR review attention.

### 8.4 Gate precedence reasoning
Per-specialist gates + production-level gates require explicit precedence rule. Default (per-specialist non-blocking under production) is a real choice that has to be re-justified per new gate. Cost: per-gate party-mode time.

### 8.5 New act-body category retrofit
Slab 2 established four `_act` body categories: pure-LLM, tool-dispatch-with-LLM, pure-tool-dispatch, Wondercraft-shaped tool-dispatch. A new category (e.g., fan-out specialist publishing to multiple downstream specialists) doesn't fit cleanly — would require adapter retrofit OR signal Option C migration. Cost: high (party-mode + possible substrate change).

### 8.6 Specialist split / merge
Splitting one specialist into two (or merging two into one) requires: manifest entry updates + dependency_map updates everywhere downstream + chain test updates + envelope contribution count change + replay-regression schema bump. Cost: high; Option C handles this locally to subgraph definitions.

### 8.7 Partial state mid-execution
If specialist X needs *partial* output from specialist Y mid-execution (not the complete final contribution), Option B can't express this — `add_contribution` is final-and-complete. Only workarounds: (a) split Y into Y1 + Y2 with intermediate contribution; (b) escalate to Option C. Cost: forced specialist split or Option C migration.

---

## 9. Composition Smoke gate — operationalization

**Required at every slab-opener authoring step.** Detail:

1. **Step name in slab-opener template:** "Composition Smoke"
2. **Author writes a 30-line throwaway script** that wires the slab's primary components together end-to-end. Synthetic inputs at boundaries; real components throughout.
3. **Script PASS-or-FAIL recorded** in slab-opener spec under T1 Readiness Block as vote-evidence.
4. **Failing-smoke disposition rules:**
   - **Re-scope:** bound the slab claim set to exclude composition; document explicitly
   - **Defer:** until substrate exists to admit composition; file as substrate-blocking
   - **Explicit composition-shape vote with named gap:** if the slab is itself a composition-substrate slab, vote GREEN with the substrate gap named in the verdict
5. **Anti-pattern P3 (Composition-Shape Vote Without End-to-End Exercise) is the prevention pattern.** Every vote on composition-affecting work MUST cite Composition Smoke evidence.

Template location: `skills/bmad-create-story/templates/slab-opener-template.md` (or equivalent — verify location at next slab-opener authoring).

---

## 10. Decision Log

Track every composition-substrate decision here. Update at each evolution.

| Date | Decision | Rationale | Trigger | Authority |
|---|---|---|---|---|
| 2026-04-27 | Path A-prime ratified (envelope alongside cache_prefix; specialists unchanged; adapter at runner layer) | 14 working specialists + M3 replay-regression baseline preserved; ~8pt cost vs ~3-6 months of Option C restart | Slab 6.1 strict-AC HALT discovery | 5-agent party-mode (Winston + Murat + Amelia + Quinn-R + Mary) |
| 2026-04-27 | A17 + P3 anti-pattern entries filed | Substrate-level + process-level defect classes named for prevention | Slab 6.1 strict-AC HALT | Mary harvest-gate authority |
| 2026-04-27 | Composition Smoke gate added to slab-opener template | P3 counter-discipline operationalized | Quinn-R Q3 | Operator + 5-agent party-mode |
| 2026-04-27 | Substrate Inventory Checklist N1–N12 standing | A1–A17 + P3 lessons consolidated as pre-flight checklist | Operator request post-Slab-6.0 | Operator |
| 2026-04-27 | Composition Specification authored as living document (this file) | Pre-emptive prevention vs flying blind during trial evolution | Operator request mid-Slab-6.1-dispatch | Operator |
| 2026-04-27 | Dependency_map source: deterministic fallback at runner layer (Texas → CD maps as `source_bundle`; other downstream calls use `upstream_output`); manifest promotion deferred as Slab-6.2 prerequisite story | Codex Slab 6.1 implementation surfaced manifest does not yet declare dependency input keys; operator ratified deferral to keep Slab 6.1 close tight; Slab-6.2 (~1pt) lands before Slab 6 trial-experience bundle implementation | Slab 6.1 implementation (commit `d5cfad8`) + bmad-code-review (DFR-6.1-1) | Operator ratification 2026-04-27 |
| 2026-04-27 | Dependency_map source promoted to pipeline manifest per-node `dependencies`; runner-layer fallback retained permanently for undeclared nodes | Manifest-declared dependencies reduce procedural coupling and make cross-specialist state flow visible in the manifest; permanent fallback preserves backward compatibility and remains the intentional resolution mechanism for opt-out nodes | Slab 6.2 implementation (`migration-6-2-promote-dependency-map-into-manifest`) | Codex implementation + Slab 6.2 party-mode green-light riders |
| 2026-04-27 | Gate precedence: per-specialist non-blocking by default under production composition; `gate_overrides` opt-in for safety-critical promotion | Confirmed at Slab 6.1 implementation per N6 trace; per-specialist interrupts recorded by adapter; production G1/G2C/G3/G4 remain pause boundary | Slab 6.1 implementation | Codex + N6 trace |
| 2026-04-27 | Trial envelope persistence: full embed of `ProductionEnvelope` inside `ProductionTrialEnvelope.production_envelope` (required field; not persistence-pointer alternative) | Self-contained trial close artifact; replay-regression reads one file; chosen at implementation; bmad-code-review patch P-2 made it required | Slab 6.1 implementation + bmad-code-review patch `6ca5f43` | Codex + bmad-code-review |
| 2026-04-27 | Multi-pass / repeated specialist nodes: Path Z ratified ("first contribution wins"; duplicate specialist contributions skipped after first; skip is explicit + logged + tested per bmad-code-review patch P-4) | Codex surfaced manifest topology can have repeated specialist nodes but envelope immutability invariant allows one contribution per specialist; operator ratified Path Z as Slab 6.1 contract; Path X (node-scoped contribution identity) + Path Y (per-pass envelope) filed as enhancement candidates when actual multi-pass production need emerges | Slab 6.1 implementation surfaced via bmad-code-review (EC-2 / AA-3 / DFR-6.1-2) | Operator ratification 2026-04-27 |
| 2026-04-27 | LangSmith trace/cost evidence in runner code: synthetic trace_id placeholder accepted as Slab 6.1 close shape; real LangSmith trace-id binding deferred | Cost rollup works (per-call cost from LangChain runtime is real); deficit is at runner-aggregation level (synthetic trial_trace_id placeholder); operator workaround = query LangSmith manually for spans with metadata `trial_id == <id>`; deferred as `slab-6-1-langsmith-runner-trace-id-real-binding` (~2-3pt) | Slab 6.1 bmad-code-review DN-1 (AA-5) | Operator ratification 2026-04-27 |
| 2026-04-27 | Checkpoint resume execution-continuation: PATCHED via tight-scope follow-on dispatch (`codex-handoff-slab-6-1-checkpoint-resume-patch.md`); `resume_from_verdict` re-invokes compiled graph at persisted checkpoint via LangGraph native `compiled_graph.invoke(post_gate_state, config={"thread_id": str(trial_id)})`; OUT OF SCOPE: multi-checkpoint walking, cross-restart resume, conflict resolution, verdict-rejection branching, non-gate-node resume, cross-pack-version resume | Codex bmad-code-review surfaced resume validates verdict + writes command but does not actually continue graph execution; operator ratified PATCH (not defer) because FR34 invariant is too central to bounded-MVP claim and no operator workaround makes it acceptable long-term | Slab 6.1 bmad-code-review DN-2 (EC-3 / EC-4) | Operator ratification 2026-04-27 |
| 2026-04-28 | Slab 7a fold-flag schema extension to `pipeline-manifest.yaml` (Tier-2 minor): two NEW additive optional per-node fields `fold_with: <upstream_gate_code>` and `fold_target: subgraph:<name>`; backward-compatible (existing nodes parse unchanged); pack stays v4.2; schema_version bumped to `v4.2-migration-stub-with-fold-flags` as ceremony evidence. Implementation (removing hardcoded `PRODUCTION_GATE_IDS = frozenset({"G1","G2C","G3","G4"})` from `app/manifest/compiler.py:42` and deriving from manifest at compile-time per FR-A8) lands in Slab 7a Story 7a-2 dev scope | Slab 7a needs all 14 declared gate codes honored at runtime (no silent ignore); fold-target metadata replaces the previous hardcoded frozenset gate-policy; D6 manifest-as-graph-config invariant strengthened; backward-compatible per Tier-2 minor pack-version policy | Slab 7a PRD authoring + 4-voice party-mode consensus (Winston / Murat / Amelia / Paige) on three preconditions blocking Slab 7a Epic 1 story dev | Operator ratification 2026-04-28 |
| 2026-04-29 | Story 7a.1 runner-supplied directive carrier: `ProductionDispatchAdapter.build_specialist_state(..., runner_supplied_payload=None)` accepts a runner-owned payload merged into `cache_prefix` JSON alongside `_payload_from_dependencies(...)` output. Story 7a.1 reserves top-level keys `directive_path` + `bundle_dir` for Texas only (gated at the runner call site by `specialist_id == "texas"` in `_runner_payload_for_specialist`); other specialists receive `runner_supplied_payload=None`. Runner-supplied keys win on collision with dependency_map keys (documented in adapter docstring). The kwarg is additive and backward-compatible: existing call sites that omit it preserve Slab 6.0 behavior bit-exactly | Closes trial-475 Gap 2 (silent gate-bypass when Texas's directive_path is empty → fixture-stub fallback) without (a) inventing a synthetic specialist contribution that contradicts the W-R1 "composer is orchestration" semantics, or (b) coupling Texas's specialist body to the orchestration layer. Adapter remains the sole sanctioned coupling point per §3.3; composer (`app/marcus/orchestrator/directive_composer.py`) stays a pure-function orchestration node. The runner_supplied_payload mechanism is the cleanest minimal Composition Spec §3.3 surface that admits orchestration→Texas data threading without breaking Composition Smoke, isolation, or first-contribution-wins | Story 7a.1 A-R3 Option A (Gate-1 party-mode green-light addendum 2026-04-28; ratified during dev cycle when T4 ambiguity surfaced) | Claude (dev) + Codex (bmad-code-review) + operator ratification at Story 7a.1 close 2026-04-29 |

---

## 11. Migration triggers — when to escalate Option B → Option C

**The Composition Specification is the forcing function for the B-vs-C decision. The decision is evidence-based, not speculation-based.**

**Trigger 1 — Fan-out / parallel dispatch becomes a real production need.** Symptom: a specialist needs to dispatch to ≥2 downstream specialists in parallel + merge results. Workaround: split into sequential chain (degrades latency + parallelism). Threshold: 1 confirmed production need in trial set 1-5 → file Option C migration as Slab 7+ candidate; 2 confirmed needs → start Option C brownfield.

**Trigger 2 — Partial state mid-execution becomes a real production need.** Symptom: specialist X needs partial output from specialist Y before Y completes. Workaround: forced specialist split. Threshold: 1 confirmed need → file as candidate; 2 confirmed needs → start Option C brownfield.

**Trigger 3 — Gate precedence complexity grows beyond the §3.5 default.** Symptom: ≥3 per-specialist gates promoted to production-blocking via `gate_overrides`; precedence reasoning becomes load-bearing operational concern. Threshold: 3 promoted gates → start Option C brownfield.

**Trigger 4 — Adapter LOC exceeds ~800 OR adapter refactor cost exceeds ~2pt per quarter.** Symptom: cross-cutting concern bottleneck materializes. Threshold: hit either condition → start Option C brownfield.

**Trigger 5 — New `_act` body category emerges that doesn't fit existing four (pure-LLM / tool-dispatch-with-LLM / pure-tool-dispatch / Wondercraft-shaped).** Symptom: forced retrofit to adapter or substrate change to admit new category. Threshold: 1 new category → file as Option C migration trigger candidate; 2 → start Option C brownfield.

**Trigger 6 — Composition Specification accumulates >5 entries in §10 Decision Log within 6 weeks.** Symptom: substrate-level decisions firing faster than evolution cycle. Threshold: rate exceeded → party-mode evaluate Option C migration.

**The brownfield Option C project, if triggered:**
- Designed against accumulated Composition Spec evidence (this document) + N1–N12 checklist + A1–A17 + P3 catalog
- Benefits from 14 working specialists' isolated-execution contracts as reference
- Estimated ~3-6 months
- Runs in parallel with continued Option B production trials
- Migration path: cutover after Option C parity-verifies against Option B trial set

---

## 12. Open questions (Slab 6.1 resolutions + post-6.1 known limitations)

### Resolved at Slab 6.1 close (2026-04-27)

1. ~~**Dependency_map source.**~~ **RESOLVED.** Manifest-declared per-node `dependencies` shipped in Slab 6.2, with runner-layer fallback permanently retained for nodes that omit or intentionally leave `dependencies` empty.
2. ~~**Gate precedence default.**~~ **RESOLVED.** Per-specialist non-blocking under production composition; `gate_overrides` opt-in for safety-critical promotion. Confirmed at Slab 6.1 implementation per N6 trace.
3. ~~**`ProductionTrialEnvelope.production_envelope` shape.**~~ **RESOLVED.** Full embed; required field (not optional); bmad-code-review patch P-2 enforces.
4. **Manifest entry generator-emit (`2c-4-generator-emit-manifest-dependency-stub`).** Still open — currently manual. Should be automated alongside C3 row auto-emit per A12 counter-pattern. Reactivation: when next specialist is generated AND operator wants to retire manual manifest-edit step.
5. ~~**Replay-regression with envelope.**~~ **RESOLVED-WITH-DEFERRAL.** Frozen graph/golden-trace slices PASS post-6.1; pre-existing pack-hash drift (`013b7ef → 19cde78`) is unrelated to Slab 6.1 rewire (filed as `replay-regression-pack-hash-drift-pre-slab-6.1`); replay sweep timed out at 124s during review (filed as part of same deferred entry).

### Known limitations carried forward (post-6.1; documented per operator dispositions)

6. **LangSmith trace/cost evidence in runner code: synthetic trace_id placeholder.** Cost rollup works correctly (per-call LangChain runtime emits real spans + real cost). The runner records a synthetic `trial_trace_id` placeholder rather than fetching the real LangSmith trace ID. Operator workaround: query LangSmith manually for spans where `extra.metadata.trial_id == <trial_id>`. Deferred as `slab-6-1-langsmith-runner-trace-id-real-binding` (~2-3pt). Reactivation: when first trial reveals operator-friction on the manual workaround OR when audit-trail completeness becomes load-bearing for stakeholder review.

7. **Multi-pass / repeated specialist nodes: Path Z ("first contribution wins").** Envelope immutability invariant allows one contribution per `specialist_id`; if manifest topology has repeated specialist nodes (e.g., Irene Pass 1 + Irene Pass 2), only the FIRST contribution lands; later duplicate-specialist nodes are skipped (explicitly logged per bmad-code-review patch P-4). Path X (node-scoped contribution identity: `<specialist>:<node_index>`) and Path Y (per-pass envelope) filed as enhancement candidates. Reactivation: when actual multi-pass production need emerges in trial work; deferred as `slab-6-1-multi-pass-envelope-path-x-or-y`.

8. **Runner ignores compiled graph edges; iterates manifest order.** Current v4.2 manifest is linear so this is not blocking. Required before non-linear branch/conditional production manifests. Deferred as `slab-6-1-runner-compiled-edge-traversal` (DFR-6.1-4). Reactivation: when first non-linear manifest topology lands.

9. **`ProductionTrialEnvelope` permits impossible lifecycle states.** Cross-field validators for the `completed_at` / `paused_gate` / `cost_report_path` state matrix are absent. Pre-existing issue not introduced by Slab 6.1 rewire. Deferred as `production-trial-envelope-lifecycle-invariants` (DFR-6.1-5). Reactivation: when first lifecycle-state-confusion incident surfaces in trial OR scheduled tech-debt cleanup pass.

10. **Checkpoint resume execution-continuation: PATCHED.** Resume now actually continues graph execution from the gate node post-verdict via LangGraph native `compiled_graph.invoke(post_gate_state, config={"thread_id": str(trial_id)})`. OUT OF SCOPE for the patch (deferred to follow-on stories if real production need emerges): multi-checkpoint walking; cross-restart resume; conflict resolution; verdict-rejection branching; non-gate-node resume; cross-pack-version resume.

---

## 13. Companion documents (read alongside)

- `docs/dev-guide/specialist-anti-patterns.md` — A1–A17 + P1–P3 catalog
- `docs/dev-guide/substrate-inventory-checklist.md` — N1–N12 standing pre-flight
- `docs/dev-guide/langgraph-migration-guide.md` — §12 specialist walkthrough; §"Production Envelope Substrate"; §"Production Runner"
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — four-file-lockstep contract
- `docs/dev-guide/dev-agent-anti-patterns.md` — dev-cycle-level anti-patterns
- `docs/dev-guide/story-cycle-efficiency.md` — K-floor + dual-gate + DISMISS rubric governance
- `_bmad-output/implementation-artifacts/migration-6-0-production-envelope-substrate.md` — substrate-opener spec
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` — runner-consumer spec
- `_bmad-output/implementation-artifacts/m5-decision.md` — verdict-integrity annotations + Slab 6.0 substrate-ratification waypoint
- `_bmad-output/upstream-state.md` — M5 conditions + Slab 6.0/6.1 sequence
- `_bmad-output/planning-artifacts/deferred-inventory.md` — composition-relevant deferred work

---

## 14. Maintenance protocol

This document is normative and living. Update at:

1. **Slab 6.1 close** — fill in §3 open items + §10 Decision Log post-implementation rows + §12 resolved items
2. **Each new specialist filing** — verify §5.1 protocol followed; update §5 if protocol gains a step
3. **Each composition-affecting evolution** — append §10 Decision Log entry; verify §11 triggers haven't fired
4. **Each trial production cycle** — review §8 friction vectors against trial evidence; update threshold counts
5. **Each anti-pattern harvest** — verify §7 N-item application table covers new entries
6. **Quarterly** — review §11 migration triggers against accumulated evidence; party-mode evaluate Option C escalation
7. **At Option C trigger fire** — start brownfield project; this document becomes input artifact, not output

Decisions to remove or contract this document require party-mode ratification. Decisions to extend it are dev-agent authority + party-mode for §11 trigger-rule changes.
