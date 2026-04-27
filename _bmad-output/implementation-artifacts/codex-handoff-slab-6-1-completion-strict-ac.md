# Codex dispatch: Slab 6.1 completion (strict-AC path; close the 20% gap)

**Session:** 2026-04-27 (operator-authorized post-bmad-code-review-finding-gap)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.1 implementation landed (Codex 2026-04-27): composition layer + probe + 38 tests + 1 live smoke pass
- bmad-code-review (Codex 2026-04-27): three-layer convergence on substantive blocker
- Code review file: `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md`
- Two preserved-state commits: `c7d6447 fix(review-6.1)` + `7421f66 docs(review-6.1)`
- Story status: `review` (Codex correctly held; do NOT flip)
- Operator chose Option 1 (strict-AC path) per Codex's recommendation

**Mission:** complete the load-bearing 20% gap that bmad-code-review identified. Make `app.marcus.cli trial start` actually invoke the manifest-composed LangGraph through the registry-backed specialist handlers — NOT a direct OpenAI probe. Real production-graph execution end-to-end so that `production_clone_launch_evidence=True` honestly reflects production-graph completion, not probe completion.

## Why this dispatch exists

bmad-code-review's three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) independently converged on the same finding: Slab 6.1's runner composes the graph but does NOT execute the production graph or registry-backed specialist handlers. The runner performs a direct OpenAI probe; the live smoke proves a live API call happens, NOT that the manifest-composed-LangGraph-with-registry-specialists path is exercised.

This is **A16 (Composition-vs-Component Audit Gap) instance #4 today.** The composition layer landed (per AC-A); the invocation against the composition did not (per AC-B which required BOTH compose AND invoke).

Operator decision (2026-04-27): Option 1 strict-AC path. Same "do it right" preference that has held since the top of this migration. No band-aids; close the substrate gap properly.

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 instances.

## What is preserved from prior 6.1 implementation (DO NOT REVERT)

Codex's 80% from yesterday's implementation stays as starting state:

- `app/marcus/orchestrator/production_runner.py` (composition layer + probe)
- `app/manifest/compiler.py` (real-handler resolution per AC-A; the `compile_run_graph(...)` change that replaced `_passthrough_node` with dispatch-registry-backed specialist resolution)
- `app/marcus/cli/trial.py` (rewired to invoke `production_runner` instead of M3 harness wrapper)
- `app/models/runtime/production_trial_envelope.py` (Pydantic v2 strict envelope)
- `schema/production_trial_envelope.v1.schema.json`
- `tests/fixtures/runtime/production_trial_envelope_golden.json`
- 7 unit/integration test files
- `tests/live/test_production_trial_smoke.py` (live smoke; will be UPDATED per below, not removed)
- Governance JSON updates (Slab 6 inaugural entry; version 2026-04-27-slab6)
- Migration guide §"Production Runner" addition
- Sprint-status updates
- Story Dev Agent Record

These represent real value (the composition layer is correctly built; the test surface is correctly authored at the unit/integration level). The gap is in INVOCATION, not in COMPOSITION.

## What this dispatch must implement

### Phase 1 — Real graph execution (the load-bearing change)

Replace the direct OpenAI probe in `production_runner.py` with **actual invocation of the composed LangGraph**. Specifically:

1. The runner must compose the graph from manifest + dispatch registry per the existing `compile_run_graph(...)` call (preserved).
2. The runner must INVOKE the composed graph via LangGraph's standard execution path: `compiled_graph.invoke(initial_state)` or `compiled_graph.astream(initial_state)` (operator-decision on sync vs streaming; prefer streaming for HIL gate pause/resume per Phase 2).
3. The invocation must route through the registry-backed specialist handlers (NOT bypass to a direct OpenAI client call). Each manifest node that maps to a specialist must execute that specialist's `_act` node which calls `app.models.adapter.make_chat_model(...)` per the cascade YAML.
4. The trial-state initial conditions must be derived from the operator-supplied input bundle (corpus path); the LangGraph state passes through specialist nodes accumulating outputs.

**Verify:** add an integration test that asserts the production runner's invocation path passes through at least 2 specialist nodes (proves real composition execution, not single-node probe). Mock the OpenAI client at the adapter layer (NOT at the runner layer) to confirm the invocation reaches `make_chat_model`.

### Phase 2 — Real LangGraph checkpoint/resume (HIL gate pause/resume per FR34)

The current implementation likely either bypasses HIL gates or uses CLI-orchestrated re-launch. The strict-AC path requires real LangGraph checkpoint/resume:

1. Configure the LangGraph compilation with a checkpointer (PostgresCheckpointer per Slab 1 substrate, or SqliteCheckpointer for development).
2. At gate nodes (G1/G2C/G3/G4): runner persists checkpoint, emits DecisionCard via existing `app/models/decision_cards/` machinery, transitions `ProductionTrialEnvelope.status` to `paused-at-gate` + `paused_gate` set.
3. Trial CLI returns control to operator (via stdout indicating pause + trial_id).
4. On resume: `app.marcus.cli gate decide ...` (or HTTP/MCP transport) submits `OperatorVerdict` via `app/gates/resume_api.py::resume_from_verdict`; the runner resumes graph execution from the persisted checkpoint at the gate node onward.
5. Anti-replay binding intact (decision-card-digest + `(card_content + trial_run_id + issuance_timestamp + server_nonce)` per Story 3.3 W-R1-3.3-2).

**Verify:** the existing `tests/integration/marcus/test_production_runner_gate_pause_resume.py` (4 tests per AC-D) must exercise the REAL checkpointer path, not a mocked-around shortcut. After this phase, those tests must verify checkpoint persistence + resume from persisted state, not just transition-to-paused-status.

### Phase 3 — Real LangSmith trace binding (per AC-E)

The trace context must wrap the GRAPH INVOCATION, not the probe. Specifically:

1. `production_runner.run_production_trial(...)` opens a LangSmith trace with metadata `{"trial_id": str, "preset": str, "operator_id": str}`.
2. The graph invocation (Phase 1) executes within that trace context.
3. Each specialist node's `_act` LLM call becomes a CHILD RUN within the parent trace (LangChain/LangGraph automatically captures these when LANGSMITH_TRACING=true).
4. `app/runtime/economics.py::measure_trial_cost(trial_id)` filter must successfully find spans by `extra.metadata.trial_id == trial_id`.

**Verify:** the existing `tests/integration/runtime/test_production_runner_trace_binding.py` (2 tests per AC-E) must verify the trace's child runs include specialist node invocations, not just a single probe call. Use synthetic LangSmith trace fixtures or a real LangSmith capture for this.

### Phase 4 — Evidence discipline correction (per AC-F)

Update `production_clone_launch_evidence` flip logic:

1. `production_clone_launch_evidence=True` ONLY after the production graph completes at least one real specialist node invocation through `make_chat_model` (live OpenAI call), AND the graph execution reaches a terminal state (completion or operator-rejected).
2. Probe-only execution (no graph composition + no specialist invocation) MUST set evidence=False.
3. Offline mode (no OPENAI_API_KEY OR `--allow-offline-cost-report` flag) MUST set evidence=False.
4. Mid-graph failure (e.g., graph compiles + first specialist call fails with API error) MUST set evidence=False with explicit reason in envelope (e.g., `evidence_reason="graph_invocation_failed_at_node_05"`).

**Verify:** the existing `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py` (3 tests per AC-F) must verify the evidence flip ONLY happens for real graph completion, not for probe completion. Add a new test: probe-only path → evidence=False (negative assertion).

### Phase 5 — Live smoke updated to fail on probe-only build (per AC-G + A16)

The current `tests/live/test_production_trial_smoke.py` passed because it tested probe success, not graph execution success. Update it to fail on the current probe-only build:

1. The live smoke must invoke through the production runner end-to-end against a tiny real corpus.
2. The test must assert: (a) the trace's child-run count is ≥ 1 specialist invocation (proves graph execution); (b) `production_clone_launch_evidence=True`; (c) the trial registry record at `state/config/runs/<trial-id>/` includes specialist node attribution in cost report.
3. The test must FAIL when run against the current probe-only build (confirms it actually verifies the graph path).
4. Cost cap: ~$0.10 (per existing spec; specialist invocations may push slightly higher; raise to ~$0.20 if needed).

**Verify:** run live smoke against the new implementation; PASS expected. Run against the current probe-only HEAD before any fix lands; FAIL expected (this is the discriminator that proves Phase 1 actually works).

### Phase 6 — Re-verify all existing tests + lint gates

After Phases 1-5 land:
- `pytest tests/integration/manifest/test_compiler_real_dispatch.py tests/integration/marcus/test_production_runner_invocation.py tests/integration/marcus/test_production_runner_gate_pause_resume.py tests/integration/runtime/test_production_runner_trace_binding.py tests/integration/marcus/test_production_clone_launch_evidence_discipline.py tests/integration/marcus/test_trial_cli.py tests/unit/runtime/test_production_trial_envelope_strict.py` — all PASS
- `pytest tests/live/test_production_trial_smoke.py -m live -q` (with OPENAI_API_KEY + LANGSMITH_API_KEY set) — PASS
- `pytest tests/test_no_fictitious_model_ids.py tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py` — both PASS (no new fictitious IDs introduced)
- `ruff check app/manifest app/marcus/orchestrator app/marcus/cli app/models/runtime app/replay tests/integration/manifest tests/integration/marcus tests/integration/runtime tests/unit/runtime tests/live` — clean
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if new contract added)
- `pytest tests/migration/test_compiled_graph_digest_stable.py` — PASS

## Disposition rules (unchanged from prior dispatches)

- **`patch` items in Codex's own work mid-implementation:** address in commits as you go.
- **`defer` items (genuinely out of scope):** file as deferred-inventory entries with explicit reactivation gates.
- **`decision_needed` items (substrate disagrees with spec; can't proceed without operator):** HALT and surface. Do not silently choose. Same pattern as today's bmad-code-review finding — the right move is to surface, not push through.

**Specific halt-points likely:** if checkpointer integration reveals a substantive substrate gap (e.g., LangGraph's PostgresCheckpointer schema doesn't match Slab 1's Postgres setup), halt and surface. Operator authorizes path forward.

## What this dispatch does NOT do

- Does NOT formally close Slab 6.1. After Phases 1-6 land, second bmad-code-review pass is required (operator dispatches separately) before formal close.
- Does NOT modify the M3 deterministic harness at `marcus/orchestrator/m3_trial.py`. That stays as Slab 3 close artifact + replay-regression baseline.
- Does NOT modify any specialist code in `app/specialists/<name>/graph.py`. Specialists are scaffold-conformant; the runner's job is to compose + invoke them, not to alter them.
- Does NOT add new gate semantics. Use existing G1/G2C/G3/G4 + `resume_api` per FR34.
- Does NOT touch SciteProvider / WondercraftClient / NotionClient. Those are separate concerns.

## Effort estimate

~8-15 hours focused Codex time across the 5 implementation phases. Likely 1-2 substrate-aware halts (LangGraph checkpointer integration is the most likely surface to surface a gap; trace binding is also non-trivial against real LangSmith).

## Verification gates at dispatch close

Per Phase 6 above. Plus:
- Story status remains `review` (do NOT flip to `done`; second code-review pass is required first)
- Code-review file at `6-1-code-review-2026-04-27.md` updated with a "follow-up" section noting the strict-AC implementation landed
- All `decision_needed` items surfaced to operator (do not silently choose)
- Operator-witnessed re-run of live smoke deferred until operator dispatches the second bmad-code-review pass
- Updated commits land cleanly with descriptive messages referencing the Phase 1-5 structure

## Operator-presence work after this dispatch closes

When Codex completes Phases 1-6:

1. **Operator runs the updated live smoke** locally to confirm real graph execution end-to-end. Should fail-fast against the OLD build, pass against the NEW build.
2. **Operator dispatches second bmad-code-review pass** on the new diff (via a new dispatch artifact; same disposition rules; specifically focused on whether the strict-AC implementation actually closed the gap).
3. **If second review clears clean:** formal Slab 6.1 close orchestrates (story `review → done`; deferred-inventory `5a-2-production-graph-entrypoint-substrate-gap` flips to RESOLVED; sprint-status flip; m5-decision.md amendment with Slab 6.1 close annotation; upstream-state.md condition #3 promotes from REFRAMED-AS-SLAB-6-OPENER to RESOLVED).
4. **If second review surfaces another gap:** repeat Option 1 cycle. The discipline holds.

## Carry-forward notes

- This is the FOURTH A16 (Composition-vs-Component Audit Gap) instance discovered today (smoke test max_completion_tokens; WondercraftClient payload+endpoint; SciteProvider OAuth+tool-count; Slab 6.1 compose-without-invoke). The pattern's been remarkably persistent. The A16 prevention discipline (specifically bmad-code-review's Acceptance Auditor layer) is what catches these. Honor the discipline; don't shortcut around it.
- Codex's preserved-state commits (`c7d6447` + `7421f66`) retain the composition-layer work + the code-review findings. Build on top; do not revert.
- Cost-engineering machinery (5a.3) is in place; verify the production runner's cost report at `state/config/runs/<trial-id>/cost-report.{json,md}` actually reflects the real graph execution's spend, not the probe's spend.
- LangGraph checkpointer requires DATABASE_URL configured; verify Slab 1 Postgres setup is honored.

## Final notes

The migration's substantive product capability — operator-driven trial production through real Marcus orchestration → real specialists → real OpenAI → real artifacts — is what this dispatch finally closes. Slab 6.1's first attempt got the composition layer right but missed the invocation path; bmad-code-review caught that; this completion dispatch closes the gap.

After Phases 1-6 land + second code review clears + formal close orchestrates: the migration is genuinely shipped. Bounded-MVP scope from Slab 5a + post-MVP production capability from Slab 6.1 (real, not probe). That ship state is honest.
