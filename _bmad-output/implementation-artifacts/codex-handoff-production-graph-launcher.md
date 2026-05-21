# Codex dispatch: production-graph launcher (closes 5a.2 launcher rider + M5 condition #3)

**Session:** 2026-04-27 (operator-authorized post-Option-C accept of B-extra-as-shim)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:** Post-remediation batch closed 2026-04-27. B-extra accepted-as-shim per operator Option C. M5 SHIP-CONDITIONAL window through 2026-05-03 still open. Conditions: #1 M2 Wondercraft pending operator-window; #2 M3 Texas pending operator-window; #3 5a.2 production clone-launch SHIM-REGISTERED / LIVE-LAUNCHER-PENDING (this dispatch closes it); #4 Plausible-Token Substrate Contamination REMEDIATED-CODE / PENDING-LIVE-VERIFICATION (closes via operator-presence live smoke).
**Mission:** locate + wire the live production-graph entry point so `python -m app.marcus.cli trial start` invokes the ACTUAL migrated runtime against live OpenAI, NOT the deterministic local M3 harness wrapper.

## Why this dispatch exists

Your post-remediation B-extra (2026-04-27) shipped an honest registration shim: it correctly refused to fabricate production evidence, marked offline mode explicitly, and surfaced the gap as `decision_needed` rather than fudging. That discipline was right. The result, however, is that condition #3 (production clone-launch equivalence) cannot close via the shim — it wraps `marcus/orchestrator/m3_trial.py` (a deterministic local M3 harness), not the live production graph.

This dispatch closes that gap properly.

**Operator preference (binding, same as prior dispatches):** "do it right, no band-aids, only rational trade-offs that get named in writing." Substrate-aware adaptation is the discipline you've already exercised — extend it here. If substrate gaps surface that prevent honest closure, HALT and surface (same disposition rule that produced the shim correctly the first time).

## What "live production graph entry point" actually means

The migrated runtime per Slab 1-5a architecture:
- **Marcus orchestrator** lives at `app/marcus/` (NOT the top-level `marcus/` lesson-planner package).
- **Specialists** are LangGraph nodes at `app/specialists/<name>/graph.py` (14 of them).
- **Pipeline manifest** at `state/config/pipeline-manifest.yaml` is the deterministic neck — declares §-step ordering.
- **Frozen graph** at `runtime/graphs/v42/` is the compiled LangGraph reference.
- **Cascade YAML** at `runtime/config/model_cascade.yaml` declares per-agent OpenAI model assignment.
- **HIL gates** (G1/G2C/G3/G4) emit DecisionCards; resume via `app/gates/resume_api.py` per FR34.

The production-graph entry point should:
1. Compose the LangGraph from the pipeline manifest + frozen-graph artifacts.
2. Invoke it against an input bundle (operator-supplied corpus path).
3. Route specialist calls through the cascade YAML to live OpenAI.
4. Pause at HIL gates per FR34; await operator verdict via the gate transports.
5. Capture LangSmith trace + per-trial cost report per 5a.3 cost-engineering foundation.
6. Write artifacts to `state/config/runs/<trial-id>/`.

If this entry point does not yet exist on this branch as a callable, **that is the substrate gap to surface**. The dispatch's first phase is investigation; if the gap is large, halt-and-surface is the right move (same as the shim was the right move when you found B-extra's gap).

## Tasks

### Phase A — Investigation (substrate verification at T1)

**Goal:** determine whether a live production-graph entry point exists on this branch as a callable, OR whether one needs to be implemented from existing pieces, OR whether the substrate is missing pieces that prevent honest closure.

**Read** (do not modify):
- `app/marcus/facade.py` — Marcus's public surface; what does it expose for trial invocation?
- `app/marcus/orchestrator/supervisor.py` + `routing.py` + `write_api.py` — orchestration internals.
- `app/marcus/orchestrator/__init__.py` — what's exported.
- `app/marcus/intake.py` — intake handler shape.
- `app/marcus/dispatch/contract.py` — dispatch contract to specialists.
- `state/config/pipeline-manifest.yaml` — manifest structure.
- `runtime/graphs/v42/compiled-graph-digest.txt` + sibling files — frozen graph artifacts.
- `runtime/graphs/v42/dispatch-registry-snapshot.yaml` — production-promoted dispatch registry.
- `app/marcus/cli/trial.py` (Codex's B-extra shim) — current invocation shape.
- `marcus/orchestrator/m3_trial.py` (deterministic harness) — what it does that the production path SHOULDN'T copy.

**Determine:**
1. Does `app/marcus/facade.py` (or any other module) expose a callable like `run_production_trial(corpus_path, preset, operator_id) -> TrialEnvelope` that hits the live LangGraph compiled graph + live OpenAI?
2. If not, can one be ASSEMBLED from existing pieces (manifest loader + supervisor + dispatch contract + cascade-driven specialist invocation + gate machinery)?
3. If assembly requires building substantial new orchestration code, that's a substrate gap — HALT and surface; do NOT silently invent the production path.

**Deliverable for Phase A:** a short report at `_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-XX.md` (date when run) describing:
- What entry points exist today.
- What the gap is (if any).
- Recommended path: (a) wire existing entry point to trial CLI, (b) assemble entry point from existing pieces, (c) HALT — substantial new orchestration code required.

**Time estimate for Phase A:** 1-2 hours.

### Phase B — Implementation (per Phase A finding)

**Path (a) — Wire existing entry point.** Modify `app/marcus/cli/trial.py` to invoke the existing live entry point instead of the M3 harness. Verify end-to-end via at least one operator-window-conditional test (uses synthetic LangSmith trace + skips when OPENAI_API_KEY absent). ~2-3 hours.

**Path (b) — Assemble entry point from existing pieces.** Compose the LangGraph from manifest + frozen-graph + cascade; invoke; route gates; capture artifacts. Add tests for each composition step. Wire into trial CLI. ~4-8 hours; may halt-and-adapt.

**Path (c) — HALT.** Surface to operator with named substrate gap and proposal for how to fill it (could be: another dispatch, party-mode round, or accept that condition #3 stays open through window expiry). Do NOT proceed with Path (b) if the gap is genuinely large.

### Phase C — Verification (mandatory regardless of path)

Required tests (NEW where missing; modified where existing):

1. **`tests/integration/marcus/test_production_graph_invocation.py`** — invokes trial CLI with synthetic LangSmith trace fixture; asserts (a) LangGraph composes from manifest, (b) at least one specialist node is invoked, (c) cascade YAML resolves per-specialist model_id, (d) trial registers in `state/config/runs/<trial-id>/`, (e) cost report writes correctly per 5a.3 contract, (f) production_clone_launch_evidence flag is `true` (NOT `false` as in the shim).

2. **Existing `test_trial_cli.py`** — update assertions to verify the trial CLI no longer wraps M3 harness when running in production mode (it should invoke the live production graph).

3. **`tests/live/test_production_trial_smoke.py`** (NEW; gated `pytest -m live`) — runs ONE real trial with a tiny synthetic corpus through the real production graph against live OpenAI. Cost cap: ~$0.05 (operator's `MARCUS_TRIAL_BUDGET_USD` should be set; add explicit cap to test). Asserts (a) LangSmith trace uploads, (b) cost report records non-zero spend, (c) at least one specialist invocation completes, (d) the run finalizes cleanly. Skips when `OPENAI_API_KEY` absent.

4. **Lint guard + catalog membership tests** — both must still PASS (no new fictitious model IDs introduced).

5. **Import-linter + ruff** — both must remain clean.

### Phase D — Close artifacts

If Phase B succeeded:
1. Update `_bmad-output/upstream-state.md` condition #3 to mark **RESOLVED** (or **PENDING-OPERATOR-LIVE-RUN** if implementation is verified-correct but operator hasn't run the live trial yet).
2. Update `_bmad-output/implementation-artifacts/m5-decision.md` Accepted Conditional Window section to reflect closure.
3. Update `_bmad-output/planning-artifacts/deferred-inventory.md` `5a-2-production-clone-launcher-and-execution-equivalence-pass` entry → flip from DEFERRED-CONTINUES to RESOLVED.
4. Update `sprint-status.yaml` last_updated note with closure provenance.
5. Update `docs/operator/trial-run-runbook.md` Step 3 to reflect that the launcher now invokes the real production graph (remove any "wraps M3 harness" caveats from the doc).

If Phase B took Path (c) (HALT):
1. Document the substrate gap in detail.
2. File a deferred-inventory entry naming what's missing.
3. Leave condition #3 open in upstream-state.md with updated framing pointing at the new deferred entry.
4. Do NOT update verdicts in m5-decision.md.

## What NOT to do in this dispatch

- **No fabrication of production evidence.** Same discipline that produced the honest shim. If the live path can't be invoked end-to-end, mark `production_clone_launch_evidence=false` and surface.
- **No silent-substrate creation.** If Phase A investigation reveals you need to build new orchestration code substantially, HALT and surface to operator. The dispatch budget is investigation + wiring, not greenfield orchestration.
- **No new fictitious model IDs.** Lint guard catches this.
- **No bypassing HIL gates.** FR34 enforces resume-via-OperatorVerdict path; the production graph honors gates exactly as the M3 harness's intent (without faking deterministic verdicts).
- **No expanding scope to other M5 conditions.** This dispatch is condition #3 only. M2/M3/condition-#4 stay operator-window.

## Sequencing

Linear within this dispatch:
1. Phase A (investigate; produce report).
2. Phase A REVIEW POINT: if Path (a) — proceed to Phase B; if Path (b) — proceed to Phase B with halt-allowance; if Path (c) — STOP and surface report to operator. **Do not silently transition Path (c) → Path (b).**
3. Phase B (implement per path).
4. Phase C (verify; all 5 verification gates must pass).
5. Phase D (close artifacts per Phase B outcome).

## Verification gates at dispatch close

- Phase A report exists at `_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-XX.md`.
- Phase B outcome documented in trial CLI + supporting modules.
- Phase C tests: all 5 verification items pass per their conditions (live-smoke skips cleanly when key absent).
- Phase D artifacts updated per Phase B outcome.
- `bash scripts/setup/ready_for_trial.sh` (or `.ps1`) — exits 0 with READY FOR TRIAL banner.
- `pytest tests/integration/marcus/test_production_graph_invocation.py tests/integration/marcus/test_trial_cli.py tests/test_no_fictitious_model_ids.py tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py -q --tb=short` — all PASS.
- `pytest tests/live/ -q -m live` with placeholders — all skip cleanly.
- `ruff check` on touched surfaces — clean.
- `lint-imports --config pyproject.toml` — 9 KEPT (or higher if new contracts added).

## Operator-presence work after this dispatch

If Path (a) or (b) succeeded, operator-presence work to close M5 SHIP-CONDITIONAL → unconditional SHIP becomes:
1. Live-OpenAI cascade-tier smoke (~3 min, ~$0.0003) — closes condition #4.
2. M2 Wondercraft live-artifact ceremony (~10-15 min) — closes condition #1.
3. M3 Texas live-retrieval ceremony (~5-10 min) — closes condition #2.
4. **One real production trial through the new launcher** (~30-60 min + trial duration; cost ~$1-2 per trial per 5a.3 characterization estimates) — closes condition #3.

All four can fit in one focused operator-presence session. After that session, M5 promotes from SHIP-CONDITIONAL to unconditional SHIP within the 2026-05-03 window.

If Path (c) (HALT), operator decides whether to (a) authorize a follow-on dispatch with expanded scope, (b) accept that condition #3 stays open through window expiry (would force `migration-master-status` demotion to `iterate-pending` per the demotion rule), or (c) defer to post-window remediation cycle.

## Carry-forward notes

- Codex's prior B-extra shim is the **starting state** — preserve the honest framing (`production_clone_launch_evidence=false`, `--allow-offline-cost-report` flag, LangSmith env requirement). The new launcher EXTENDS this discipline; it doesn't replace the registration ceremony.
- The M3 harness at `marcus/orchestrator/m3_trial.py` STAYS as deterministic local test substrate — it has its own legitimate purpose (Slab 3 close artifact, replay-regression baseline). Do NOT delete or modify it. The trial CLI just needs to stop wrapping it as the production path.
- Substrate-aware adaptation precedent: 3.1 (Slab-3 substrate halt), 5a.3 (cost-engineering amendment), Plausible-Token Substrate Contamination (this remediation cycle). The pattern is: investigate at T1, halt if substrate disagrees with spec, document the disagreement, get operator ratification, proceed against the corrected understanding. Apply that pattern here if Phase A reveals genuine substrate gaps.

## Final notes

This dispatch is the load-bearing close for M5 condition #3. Done well, it puts you within one focused operator-presence session of unconditional SHIP. Done poorly (silently inventing the production path, fabricating evidence), it would un-do the discipline that B-extra correctly preserved.

The honest shim Codex shipped earlier today is the model: when the substrate doesn't support the spec, surface the gap and let operator decide. Same discipline applies if Phase A finds a Path (c) situation.
