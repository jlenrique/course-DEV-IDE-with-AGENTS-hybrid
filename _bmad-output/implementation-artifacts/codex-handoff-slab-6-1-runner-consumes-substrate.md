# Codex dispatch: Slab 6.1 runner-consumes-substrate (rewire production runner against Slab 6.0 envelope + adapter)

**Session:** 2026-04-27 (operator-authorized post-Slab-6.0-formal-close)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.0 (`migration-6-0-production-envelope-substrate.md`) CLOSED 2026-04-27 after bmad-code-review triage cleared (review report at `_bmad-output/implementation-artifacts/6-0-code-review-2026-04-27.md`; patch commit `072724c` landed; substrate inventory checklist N1–N12 trace recorded)
- Operator dual-gate gate-2: `pytest tests/composition/ -q --tb=short` → 17 passed in 1.21s (Texas → cd chain test PASS — the EXACT scenario that surfaced A17 in the prior Slab 6.1 strict-AC HALT)
- New substrate available for import: `app.models.runtime.production_envelope.ProductionEnvelope` + `SpecialistContribution`; `app.marcus.orchestrator.dispatch_adapter.ProductionDispatchAdapter`
- New standing checklist: `docs/dev-guide/substrate-inventory-checklist.md` (N1–N12; binding for all slab dispatches per Slab 6.0 review-dispatch governance)
- Slab 6.1 spec: `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` (already re-scoped per Slab 6.0 AC-J — line 14 rescope note: "imports and consumes `ProductionEnvelope` + `ProductionDispatchAdapter` from Slab 6.0")

**Mission:** rewire the existing Slab 6.1 production runner to actually consume the Slab 6.0 substrate. The pre-HALT first-attempt implementation in `app/marcus/orchestrator/production_runner.py` (596 LOC) currently invokes specialists via `_invoke_specialist_probe(...)` — a one-shot `handle.chat.invoke(...)` call that bypasses the specialist's 9-node scaffold. This is the compose-without-invoke vestige that bmad-code-review caught originally. With Slab 6.0's substrate in place, replace it with `ProductionDispatchAdapter.invoke_specialist(...)` calls that exercise each specialist's full subgraph and accumulate outputs in a `ProductionEnvelope` carried alongside the existing `ProductionTrialEnvelope`.

## Why this dispatch exists

The Slab 6.1 spec was re-scoped on 2026-04-27 from "build composition substrate + runner" (~13pt) to "runner consumes substrate" (~5pt) after Slab 6.0 absorbed the substrate work. The implementation that landed pre-HALT predates Slab 6.0 — it has the runner skeleton (graph composition, gate pause/resume, evidence discipline, trial envelope) but uses a probe-shaped specialist invocation that does NOT exercise the per-specialist 9-node scaffold. The Texas → cd chain test in `tests/composition/` proves the substrate-correct path works; this dispatch wires that same path into the live runner.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 + A17 + Slab 6.0 instances.

## Scope (rewire, not rewrite)

**KEEP from existing Slab 6.1 implementation (do NOT rewrite):**
- `app/manifest/compiler.py::compile_run_graph(...)` — real-handler resolution per AC-A (Slab 6.0 review confirmed this is correct as-is)
- `ProductionTrialEnvelope` Pydantic v2 model + four-file-lockstep — trial-level metadata (trial_id, evidence flag, cost report linkage, etc.); orthogonal to per-specialist accumulator
- HIL gate pause/resume per FR34 — `register_decision_card` + `resume_from_verdict` flow stays intact
- LangSmith trace binding (AC-E) — trace context wraps the whole trial; specialist node calls become child runs
- `production_clone_launch_evidence` boolean discipline (AC-F) — flips `True` ONLY after ≥1 real specialist call completes via the adapter
- Trial CLI wiring at `app/marcus/cli/trial.py`
- Existing test files: `test_production_runner_invocation.py` + `test_production_runner_gate_pause_resume.py` + `test_production_clone_launch_evidence_discipline.py` + `test_production_trial_smoke.py` (operator live smoke)

**REPLACE in existing Slab 6.1 implementation:**
- `_invoke_specialist_probe(specialist_id, ...)` at `production_runner.py:189` → use `ProductionDispatchAdapter.invoke_specialist(specialist_id=..., envelope=..., dependency_map=...)`. The probe was a one-shot `handle.chat.invoke(...)` call that does NOT run the specialist's `_plan` / `_act` nodes; it just confirms the cascade resolves to a real handle and the model accepts a token. Replace with adapter call so the full scaffold runs.
- The specialist-call loop around `production_runner.py:477-496` (`if node_kind == "specialist" and specialist_calls < max_specialist_calls: ...`) → for each specialist node, call `adapter.invoke_specialist(...)`; the returned envelope-with-new-contribution becomes the input to the next specialist node.
- `cache_state.cache_prefix` JSON serialization at `production_runner.py:360-361` — cache_prefix stays per-specialist scratch (Path A-prime); the new accumulator is the envelope. Add `production_envelope: ProductionEnvelope = ProductionEnvelope(trial_id=trial_id)` as a separate carrier through the graph.

**ADD to Slab 6.1 implementation:**
- `ProductionEnvelope` instance carried through the graph alongside `RunState.cache_state`. Each specialist node's adapter call appends a `SpecialistContribution`; downstream specialists' inputs are constructed from the envelope's prior contributions via `dependency_map`.
- `dependency_map` declaration: per-specialist-node mapping `downstream-input-key → upstream-specialist-id`. Source the map from the manifest (each manifest node already declares its upstream dependencies in the v4.2 33-step pack); if the manifest doesn't carry it explicitly, derive from the dispatch-registry topology. (Acceptance Auditor: verify dependency_map source is deterministic + reproducible across runs — surface as `decision_needed` if neither manifest nor registry carries it cleanly.)
- `ProductionTrialEnvelope.production_envelope: ProductionEnvelope` field (or a JSON-serialized snapshot reference; operator-judgement-call on persistence shape — surface as `decision_needed` if the right shape isn't obvious). The trial envelope persisted to `state/config/runs/<trial-id>/` should let replay-regression reconstruct the full per-specialist contribution chain.

## Specific files to modify

- `app/marcus/orchestrator/production_runner.py` — primary rewire surface
- `app/models/runtime/production_trial_envelope.py` — extend with optional `production_envelope` field (or persistence pointer; surface as decision_needed if shape unclear)
- `schema/production_trial_envelope.v1.schema.json` — emit updated schema
- `tests/fixtures/runtime/production_trial_envelope_golden.json` — regenerate golden
- `tests/integration/marcus/test_production_runner_invocation.py` — update assertions: specialist invocation happens via adapter; envelope accumulates contributions; second specialist's input was constructed from first specialist's envelope contribution (mirror the Texas → cd chain test discipline)
- `tests/integration/marcus/test_production_runner_gate_pause_resume.py` — verify per-specialist gate semantics under the new dispatch (per-specialist `gate_decision` interrupts may now fire before production-level G1; confirm production runner handles both gate scopes correctly OR document the precedence rule explicitly)
- `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py` — update tests so the live-mode case actually runs through the adapter (not the probe); offline-mode case unchanged
- `tests/live/test_production_trial_smoke.py` — update to assert envelope contributions present at trial close + LangSmith trace shows child runs from adapter invocations

## Files to NOT modify (per Path A-prime + Slab 6.0 invariants)

- 14 × `app/specialists/<name>/graph.py` — specialists unchanged (Slab 6.0 AC-E)
- `marcus/orchestrator/m3_trial.py` — deterministic harness preserved (replay-regression baseline)
- `app/models/runtime/production_envelope.py` — Slab 6.0 substrate; do not modify
- `app/marcus/orchestrator/dispatch_adapter.py` — Slab 6.0 substrate; do not modify
- `app/models/state/run_state.py` — `production_envelope` field already added in Slab 6.0; no further changes needed for this story (envelope flows alongside the run state, not as a `RunState` field; the field added in 6.0 is for cases where someone wants to attach a snapshot)
- Anti-pattern catalog (`docs/dev-guide/specialist-anti-patterns.md`) — A17 + P3 already filed; no new entries expected from this rewire (if a NEW pattern emerges, file via Mary harvest-gate)

## Substrate Inventory Checklist application (BINDING per Slab 6.0 governance)

Read `docs/dev-guide/substrate-inventory-checklist.md` at T1. Items with non-N/A applicability for this dispatch:

- **N2 (Composition exercise before vote):** the Slab 6.1 live smoke is the composition-exercise check; verify it runs through adapter, not probe. PASS criterion: `tests/live/test_production_trial_smoke.py -m live` passes with envelope-contribution assertions.
- **N3 (Live-API smoke before MVP close):** operator dual-gate gate-2 is the live smoke; closes M5 condition #3.
- **N4 (Per-component isolation invariant preserved post-composition):** specialists must remain runnable in isolation post-rewire (re-run `tests/composition/test_specialist_isolation_preserved.py` post-implementation; PASS = unchanged).
- **N5 (Cross-component state-flow contract):** dependency_map mechanism. Verify missing-dependency / circular-dependency cases handled.
- **N6 (Gate boundary scope hierarchy):** per-specialist `gate_decision` interrupts coexist with production-level G1/G2C/G3/G4. Either (a) hierarchical handling (per-specialist auto-resolve unless production-level operator verdict overrides), or (b) document the precedence rule explicitly + test it. Surface as `decision_needed` if not obvious.
- **N7 (Replay regression verifies execution path):** re-run 5a.1 replay-regression suite post-implementation; PASS = unchanged. Verify `output_digest` from envelope contributions reproduces deterministically.
- **N8 (Cost machinery integration with real trace data):** `measure_trial_cost(trial_id)` filter still finds spans correctly under the adapter dispatch path (LangSmith metadata propagates through adapter calls).
- **N9 (Operator-witnessed evidence at M-gate vote):** operator runs the live smoke for the formal Slab 6.1 close; same shape as Slab 6.0 dual-gate.
- **N11 (Composition mode declared alongside isolated mode):** confirmed at Slab 6.0 close; this dispatch consumes that declaration.

N1, N10, N12 are N/A for this story (no new external resource IDs introduced; anti-pattern catalog read at architecture-authoring time was already done at Slab 6.0; auth model is not introduced — existing `OPENAI_API_KEY` + `LANGSMITH_API_KEY` paths unchanged).

## AC traceability (against re-scoped Slab 6.1 spec)

Trace each existing AC against the new substrate-aware approach:
- AC-A (compiler real-handler resolution) — UNCHANGED; already correct per Slab 6.0 review
- AC-B (production_runner.py composition + invocation) — REWIRED to use `ProductionDispatchAdapter`; tests must assert adapter invocation path, not probe path
- AC-C (`ProductionTrialEnvelope` four-file-lockstep) — extend with `production_envelope` field (or persistence pointer); regenerate JSON Schema + golden fixture; preserve all existing shape pins
- AC-D (HIL gate pause/resume per FR34) — verify per-specialist gate interactions don't break the production gate flow (N6 substrate concern)
- AC-E (LangSmith trace binding) — verify adapter-level invocations show as child runs of the trial root span
- AC-F (`production_clone_launch_evidence` discipline) — flips `True` only after ≥1 adapter invocation completes (NOT after a probe); offline-mode unchanged
- AC-G (live smoke) — the load-bearing operator-witnessed smoke for formal close
- AC-H (A16 counter-pattern compliance) — FR52 head-to-head parity flips from PARTIAL to TRACED at story close
- AC-I (anti-pattern harvest) — no new entries expected
- AC-J (TEMPLATE compliance R1, R6, R8) — honored
- AC-K (D12 close protocol — DUAL-GATE FIVE-line) — operator runs `pytest tests/live/test_production_trial_smoke.py -m live -q` with real keys; cost cap ~$0.10–$2 (whatever the spec's cap is); evidence pasted into Dev Agent Record §"Operator dual-gate gate-2 evidence"
- AC-L (sprint-status state-flips at filing AND close) — at close: `migration-6-1-production-graph-runner: done`; M5 condition #3 in `_bmad-output/upstream-state.md` flips from REFRAMED-AS-SLAB-6.0-SUBSTRATE-+-SLAB-6.1-RUNNER to RESOLVED-2026-XX-XX; deferred-inventory `5a-2-production-graph-entrypoint-substrate-gap` flips to RESOLVED

## Implementation phasing

Suggested phases (operator-judgement-call; halt-and-adapt budget built in):
- **Phase 1 (~4-6 hr):** Read Slab 6.0 substrate (envelope + adapter + Texas → cd chain test) at T1; map dependency_map source decision (manifest? registry? both?); refresh `ProductionTrialEnvelope` shape decision; surface `decision_needed` items if any.
- **Phase 2 (~4-6 hr):** Rewire `production_runner.py` specialist invocation loop; replace probe with adapter calls; add envelope carrier through graph traversal.
- **Phase 3 (~3-4 hr):** Update test files (invocation + gate-pause-resume + evidence discipline); regenerate envelope golden; verify all integration tests pass with adapter path.
- **Phase 4 (~3-4 hr):** Re-run live smoke (Codex-side first, operator-side at formal close); update migration-guide §"Production Runner" to reference adapter; verify N-item trace passes for N4 (isolation), N5 (state-flow), N7 (replay-regression).
- **Phase 5 (~2-3 hr):** D12 close protocol artifacts; sprint-status / upstream-state / deferred-inventory updates; bmad-code-review dispatch authored at the end of implementation (separate dispatch fired after this one's deliverable lands).

Total: ~16-23 hr Codex time. Halt-and-adapt cycles expected at Phase 1 (dependency_map source) and Phase 4 (per-specialist gate semantics under composition).

## Disposition rules

Standard halt-and-surface discipline:
- **Substrate disagreement:** if Slab 6.0's adapter contract doesn't admit the production runner's needs as written, HALT and surface — do NOT modify Slab 6.0 substrate without operator party-mode ratification.
- **`decision_needed` items:** name each option + tradeoff; do not silently choose. Particularly likely surfaces: (a) dependency_map source; (b) per-specialist gate precedence; (c) `ProductionTrialEnvelope.production_envelope` shape (full embedded vs persistence pointer).
- **N-item FAIL during dev:** auto-promote to `patch` work in this dispatch; do not defer N-item failures.

## Deliverable

When implementation lands and all tests pass:
1. Codex commits the rewire as themed commit(s); follow `feat(slab-6.1): rewire production runner to consume Slab 6.0 substrate` convention.
2. Codex sets `migration-6-1-production-graph-runner` line annotation in `sprint-status.yaml` to "Implementation rewired against Slab 6.0 substrate; awaiting bmad-code-review + operator dual-gate"; story status remains `review`.
3. Codex final report names: tests passing (Codex-side), Codex-side live smoke result (cost), N-item trace summary, `decision_needed` items surfaced, files changed.
4. **Next dispatch (separate, fires after this lands):** bmad-code-review on Slab 6.1 rewire diff, with the same N-item trace deliverable section as the Slab 6.0 review (substrate inventory checklist trace section is BINDING for all reviews from this point forward per Slab 6.0 governance).
5. **Formal close (after bmad-code-review triage clears + operator runs live smoke):** operator runs `pytest tests/live/test_production_trial_smoke.py -m live -q`; pastes evidence into Dev Agent Record; `review → done` flip; M5 condition #3 RESOLVED; the migration's central architectural-equivalence claim now has end-to-end live-trial proof.

This dispatch closes the M5 conditional that has carried since 2026-04-26. After this, the bounded-MVP scope can drop the "bounded" qualifier — production-graph-runner becomes the demonstrated path, not a deferred slab opener.
