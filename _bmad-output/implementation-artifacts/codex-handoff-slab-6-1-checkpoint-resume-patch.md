# Codex dispatch: Slab 6.1 patch — checkpoint resume execution-continuation (decision_needed Item 2 from review triage)

**Session:** 2026-04-27 (operator-authorized post-bmad-code-review-6.1)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.1 implementation landed (commit `d5cfad8`)
- bmad-code-review-6.1 completed; report at `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md`
- Patch commits already applied: `6ca5f43` (review fixes) + `0f91e95` (review-record docs)
- Codex-side verification: focused review suite → 54 passed; ruff clean on touched files
- Operator-side live smoke (prior): 1 passed in 31.75s; envelope contributions `['texas', 'irene']`; cost $0.0325215
- Substrate inventory checklist trace recorded: 0 FAIL / 2 decision_needed
- Story status: `review` (correctly held pending decision_needed resolution + formal close)

**Operator dispositions on the two decision_needed items (BINDING):**

1. **Decision_needed Item 1 — synthetic LangSmith trace/cost evidence in runner code → DEFER.** Real specialist invocations DO emit real LangSmith spans (cost rollup works correctly; $0.0325215 was real OpenAI spend). The deficit is at the runner-aggregation level: `ProductionTrialEnvelope.production_envelope` records a synthetic `trial_trace_id` placeholder rather than fetching the real LangSmith trace ID. Operator workaround acceptable for bounded-MVP: query LangSmith manually for spans where `extra.metadata.trial_id == <trial_id>`. File as deferred-inventory entry `slab-6-1-langsmith-runner-trace-id-real-binding` (~2-3pt; reactivate when first trial reveals operator-friction on the manual workaround OR when audit-trail completeness becomes load-bearing for stakeholder review).

2. **Decision_needed Item 2 — resume validates verdict + writes command but does not continue graph execution → PATCH NOW (this dispatch).** Structural bounded-MVP hole: FR34 HIL tamper-evidence is listed as a 5a.4 invariant; shipping without working resume means FR34 is verified at unit-test level but not at runtime end-to-end. First tracked trial WILL hit gates if the corpus is real. No operator workaround makes shipping-without-resume acceptable long-term.

**Mission:** patch the production runner so `resume_from_verdict(...)` actually continues graph execution from the checkpoint state at the gate node post-verdict. Tight scope: don't try to handle every checkpoint edge case; just enable the happy-path resume from gate-pause to trial-completion.

## Why this dispatch exists

Per the bmad-code-review-6.1 finding (Item 2 in the report's decision_needed section), the production runner currently:
- PAUSES correctly at gate nodes (G1/G2C/G3/G4)
- PERSISTS LangGraph checkpoint state at pause
- EMITS DecisionCard correctly (kind, digest binding, anti-replay tuple per Story 3.3 W-R1-3.3-2)
- ACCEPTS OperatorVerdict via `app/gates/resume_api.py::resume_from_verdict`
- VALIDATES the verdict (signature, anti-replay, tamper-evidence)
- WRITES a "resume command" record

But it does NOT:
- Re-enter the LangGraph at the checkpoint state to continue execution
- Drive the manifest traversal forward from the gate node
- Marshal the verdict into the production envelope (or wherever the post-gate state path expects it)
- Complete the trial through subsequent specialist invocations + remaining gates

The trial APPEARS to resume from operator's perspective — verdict accepted, command written — but no further specialist work happens. This breaks the FR34 contract under production composition.

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 + A17 + Slab 6.0 + Slab 6.1 instances.

## Scope (TIGHT)

**IN SCOPE:**
1. Wire `resume_from_verdict` to actually re-invoke the production runner at the persisted checkpoint state — LangGraph natively supports this via `compiled_graph.invoke(state=None, config={"configurable": {"thread_id": <trial_id>}})` which resumes from the persisted checkpoint
2. Marshal the OperatorVerdict into the post-gate state correctly so the next manifest step picks up the verdict's payload (e.g., edit_payload for G2C; promote_to_next for G1; etc.)
3. Continue manifest traversal from the gate node forward — adapter invocations for downstream specialists fire normally; envelope accumulates correctly
4. Trial reaches terminal state (final node; trial envelope persisted; cost rollup completes; production_clone_launch_evidence reflects post-gate specialist invocations correctly)
5. Add at least ONE integration test exercising end-to-end pause → checkpoint → verdict-submit → execution-continues → trial-completes
6. Add at least ONE live smoke test that exercises the resume path (or augment existing smoke to include a gate-firing path; corpus may need to be sized to trigger at least one gate within cost cap)

**OUT OF SCOPE (explicitly defer if surfaced):**
- Multi-checkpoint walking (resume from arbitrary historical checkpoint vs latest)
- Resume across thread restarts (resume after process restart, not just within-process)
- Resume conflict resolution (what if two operators submit conflicting verdicts simultaneously)
- Verdict-rejection branching (operator submits verdict that says "halt"; current happy-path is verdict says "continue")
- Resume into a non-gate node (resume from arbitrary checkpoint, not just from a known gate)
- Resume across pack-version changes (resume a trial after manifest version bumped)

If any of these surface during implementation as blocking the happy-path, HALT and surface to operator.

**FAIL-LOUD invariants (preserve from existing code):**
- Verdict signature/anti-replay validation must still happen before any state change
- Tamper-evidence (decision-card-digest binding per Story 3.3 W-R1-3.3-2) preserved
- No bypass paths that allow verdict submission without checkpoint persistence happening first
- DecisionCard kind correctly matches the gate node that paused

## Specific implementation guidance

### Resume mechanism (LangGraph native)

LangGraph's `MemorySaver` / `PostgresSaver` checkpointer persists state at each interrupt. To resume, the compiled graph is invoked with the same `thread_id` and a state that includes the verdict's resolution. Conceptually:

```python
# In resume_from_verdict (or wherever verdict-acceptance lands):
def resume_from_verdict(verdict: OperatorVerdict, *, trial_id: UUID) -> ProductionTrialEnvelope:
    # 1. Validate verdict (existing code; preserve)
    _validate_verdict_signature(verdict)
    _validate_anti_replay_tuple(verdict, trial_id)
    _validate_decision_card_digest_binding(verdict)

    # 2. Load production runner state for the trial (NEW)
    runner_context = _load_runner_context_for_trial(trial_id)
    # runner_context carries: compiled_graph, envelope, manifest, dispatch_adapter,
    # langsmith_trace_context, cost_machinery, etc.

    # 3. Marshal verdict into post-gate state (NEW)
    post_gate_state = _apply_verdict_to_state(runner_context.last_checkpoint_state, verdict)

    # 4. Re-invoke compiled graph from checkpoint with verdict-resolved state (NEW)
    config = {"configurable": {"thread_id": str(trial_id)}}
    final_state = runner_context.compiled_graph.invoke(post_gate_state, config=config)

    # 5. Continue trial close path (existing code; reuse from production_runner)
    return _finalize_trial(trial_id, runner_context, final_state)
```

### Key implementation surfaces

- `app/marcus/orchestrator/production_runner.py` — likely needs a new `resume_production_trial(trial_id, verdict)` entry point that the resume_api can call; OR refactor existing `run_production_trial(...)` into compose-able phases (`_setup` + `_traverse_until_pause` + `_finalize`) that resume can reuse
- `app/gates/resume_api.py::resume_from_verdict` — call into the new entry point after verdict validation
- Runner context persistence — the runner must persist enough state at gate-pause (compiled_graph reference, envelope snapshot, manifest version, dispatch adapter config) for resume to reconstruct. Likely a small new `RunnerCheckpointMetadata` Pydantic model alongside the existing LangGraph checkpointer
- Trial CLI surface (`app/marcus/cli/trial.py`) — add a `resume` subcommand for operator-side testing: `python -m app.marcus.cli trial resume --trial-id <uuid> --verdict-file <path>`

### Composition Spec invariants to preserve

Per `docs/dev-guide/composition-specification.md`:
- §3.1 envelope immutability: the envelope at resume time must be the SAME envelope that was persisted at pause; any specialist contribution that fired pre-pause stays in the envelope; specialists that fire post-resume append normally
- §3.5 gate precedence: per-specialist gates that fired pre-pause stay non-blocking under production; production-level G1/G2C/G3/G4 are the resume targets; per-specialist gates within post-resume specialists fire normally as composition continues
- §3.7 persistence: trial envelope at trial close (post-resume) reflects all contributions; trace_id stays linked to the same trial_id (synthetic per Item 1 deferral; operator queries LangSmith via metadata)

## Test surface (~5-7 tests)

NEW required:
- `tests/integration/marcus/test_production_runner_resume_continues_execution.py` (~3 tests):
  1. Pause-at-G1 → submit-verdict → execution-continues → trial-completes — assert trial reaches terminal state; envelope has all expected contributions (pre-pause + post-resume); production_clone_launch_evidence=True
  2. Pause-at-G2C → submit-verdict-with-edit-payload → execution-continues with edit applied → trial-completes — assert verdict's edit_payload was marshaled correctly into the post-gate state
  3. Verdict signature validation failure → resume rejected → checkpoint state unchanged → trial remains in paused state — fail-loud verification

- `tests/integration/marcus/test_production_runner_resume_invariants.py` (~2 tests):
  1. Per-specialist contributions persist across pause/resume — envelope at trial close has same Texas+CD+... contributions as if trial had run without pausing
  2. LangSmith trace_id stays linked to same trial_id across pause/resume — same metadata propagation

- `tests/live/test_production_trial_smoke_with_gate.py` (NEW; or augment existing smoke):
  - 1 parametrized test exercising real OpenAI specialists + a gate firing + operator-simulated verdict submission + execution continuation; cost cap ~$0.20-$0.50 (slightly higher than current 31.75s smoke because trial is longer); `pytest -m live` gated

## N-item trace (re-affirm)

Per substrate inventory checklist:
- **N6 (Gate boundary scope hierarchy):** this patch directly improves N6 — production-level gates now work end-to-end at runtime, not just at unit-test level
- **N7 (Replay regression verifies execution path):** verify post-patch that 5a.1 replay regression still passes; resume path should reproduce deterministically across replay
- **N4 (Per-component isolation invariant preserved post-composition):** specialists that fire post-resume must still be invoked through the adapter — no bypass paths
- **N9 (Operator-witnessed evidence at M-gate vote):** operator runs the new live smoke as part of formal Slab 6.1 close

## Disposition rules

Standard halt-and-surface discipline:
- **Substrate disagreement:** if LangGraph's checkpointer doesn't actually support resuming from arbitrary interrupt as cleanly as expected, HALT and surface
- **`decision_needed` items surfaced during implementation:** name each option + tradeoff; do not silently choose
- **Test FAIL during dev:** auto-promote to in-patch fix; do not defer
- **Out-of-scope items that block happy-path:** HALT and surface; do not silently expand scope

## Phasing

Suggested phases (operator-judgement-call; halt-and-adapt budget built in):
- **Phase 1 (~3-4 hr):** Read existing `resume_from_verdict` flow + LangGraph checkpointer state at gate-pause; design `resume_production_trial(...)` entry point; surface decision_needed if runner state isn't reconstructible from checkpoint alone
- **Phase 2 (~4-6 hr):** Implement `resume_production_trial(...)` + verdict-marshaling + graph re-invocation; preserve all FAIL-LOUD invariants
- **Phase 3 (~3-4 hr):** Author 5 integration tests + 1 augmented live smoke; verify happy paths pass
- **Phase 4 (~2-3 hr):** Run focused review suite + replay regression check + ruff clean; commit as `fix(slab-6.1): wire checkpoint resume to continue graph execution`
- **Phase 5 (~1 hr):** Update Slab 6.1 spec Dev Agent Record §"Verification" with new test counts + live smoke result; update bmad-code-review report's Item 2 to RESOLVED-AT-PATCH

Total: ~13-18 hr Codex time. Halt-and-adapt cycles expected at Phase 1 (LangGraph checkpointer semantics) and Phase 3 (live smoke gate-firing path).

## Deliverable

When patch lands and all tests pass:
1. Codex commits the patch as `fix(slab-6.1): wire checkpoint resume to continue graph execution from gate node`
2. Codex updates `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md` Item 2 disposition: "decision_needed → RESOLVED-AT-PATCH (commit <sha>); execution continuation now works end-to-end through gate pause/resume"
3. Codex final report names: tests passing (Codex-side), Codex-side new live smoke result (cost), N-item trace re-confirmation, files changed, any decision_needed items surfaced during implementation

After this patch lands, Slab 6.1 has only Item 1 outstanding (deferred per operator disposition above). Formal close protocol can proceed:
- Operator runs new live smoke with gate-firing corpus to confirm reproducibility (~10 min; cost ~$0.20-$0.50)
- Operator paste evidence into Slab 6.1 spec Dev Agent Record §"Operator dual-gate gate-2 evidence"
- File SIX deferred-inventory entries per the full bmad-code-review-6.1 triage + Item 1 deferral:
  - `migration-6-2-promote-dependency-map-into-manifest` (DFR-6.1-1; ~1pt; Tier A prerequisite)
  - `slab-6-1-multi-pass-envelope-path-x-or-y` (DFR-6.1-2; Path X / Path Y enhancement when multi-pass need emerges)
  - `replay-regression-pack-hash-drift-pre-slab-6.1` (DFR-6.1-3; investigate pre-existing drift; needs golden refresh post-Slab-6.0)
  - `slab-6-1-runner-compiled-edge-traversal` (DFR-6.1-4; runner currently iterates manifest order ignoring compiled graph edges; required before non-linear branch/conditional production manifests)
  - `production-trial-envelope-lifecycle-invariants` (DFR-6.1-5; cross-field validators for completed_at/paused_gate/cost_report_path state matrix; pre-existing issue not introduced by 6.1)
  - **`slab-6-1-langsmith-runner-trace-id-real-binding`** (NEW per DN-1 / Item 1 deferral; ~2-3pt; reactivate when first trial reveals operator-friction on the manual LangSmith trace-id workaround)
- `migration-6-1-production-graph-runner: review → done` flip in `sprint-status.yaml`
- `_bmad-output/upstream-state.md` condition #3 RESOLVED-2026-04-XX flip
- `_bmad-output/planning-artifacts/deferred-inventory.md` `5a-2-production-graph-entrypoint-substrate-gap` flip to RESOLVED
- `_bmad-output/implementation-artifacts/m5-decision.md` Slab 6.1 close annotation; M5 condition #3 RESOLVED; migration verdict promotes from "SHIP for bounded-MVP scope" to unqualified SHIP
- `docs/dev-guide/composition-specification.md` §3 + §10 + §12 updates per bmad-code-review-6.1 closeout protocol
- Slab 6 trial-experience bundle dispatch handed to Codex (`codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md`)

## Substrate Inventory Checklist availability

Per Slab 6.0 governance, this patch dispatch honors the standing N1–N12 trace discipline. The patch directly affects N6 + N7 + N9; verify each at deliverable.

## What this dispatch does NOT do

- Does NOT touch Slab 6.0 substrate (envelope + adapter; out of scope)
- Does NOT address Item 1 (LangSmith runner trace ID synthetic) — explicitly deferred per operator disposition
- Does NOT expand scope beyond happy-path resume (multi-checkpoint walking, cross-restart resume, conflict resolution, verdict-rejection branching, non-gate-node resume, cross-pack-version resume — all OUT OF SCOPE; HALT-and-surface if blocking)
- Does NOT modify per-specialist scaffold (specialists unchanged per Path A-prime)
- Does NOT touch Tier A trial-experience bundle work (separate dispatch already authored)
