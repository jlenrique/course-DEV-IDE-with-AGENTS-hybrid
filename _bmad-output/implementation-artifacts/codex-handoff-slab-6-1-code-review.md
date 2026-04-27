# Codex dispatch: bmad-code-review on Slab 6.1 production-graph runner

**Session:** 2026-04-27 (operator-authorized post-Slab-6.1-implementation-and-operator-witnessed-live-smoke)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.1 implementation landed (Codex final report 2026-04-27)
- 38 tests passed, 1 deselected
- Codex-side live smoke: `pytest tests/live/test_production_trial_smoke.py -m live -q` = 1 passed
- **Operator-side live smoke: 1 passed in 9.35s on 2026-04-27 (operator-witnessed; cost ~$0.10 within cap)**
- Story status: `review` (Codex correctly held at review pending formal close)
- ruff clean; lint-imports 9 KEPT

**Mission:** independent multi-layer code review on the Slab 6.1 diff per the dual-gate `operator_acceptance_gate` rationale. Surface any defects before formal `done` flip.

## Why this dispatch exists

Slab 6.1 (`migration-6-1-production-graph-runner.md`) is dual-gate per `substrate_shape` + `operator_acceptance_gate`. Operator-side live smoke just cleared (2026-04-27 9.35s pass). The remaining formal-close gate is independent code review with triage discipline.

This is bmad-code-review, NOT the lighter `bmad-review-adversarial-general` standalone — three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + triage into patch / defer / dismiss / decision_needed. The Acceptance Auditor layer is load-bearing here because the Slab 6.1 spec has 8 ACs (A through H) plus the integration-exercise AC per A16 counter-pattern; the auditor reads the spec and traces the diff against each AC.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Three substantive A16 instances surfaced today across M2/M3/Slab-6.1 prep work; the A16 prevention pattern is working but only because we've been running integration-exercise checks. This code review is the next instance of that discipline — it should surface anything subtle in the production-runner composition that the live smoke didn't exercise.

## Scope

**Diff input:** all Slab 6.1 implementation changes since the operator-session-housekeeping commit. Compute the actual range from `git log --oneline` at run time. Likely includes:
- `app/marcus/orchestrator/production_runner.py` (NEW; ~300-500 LOC est)
- `app/manifest/compiler.py` modifications (replaced `_passthrough_node` with real dispatch-registry-backed specialist resolution per AC-A)
- `app/marcus/cli/trial.py` modifications (rewired to invoke production_runner instead of M3 harness wrapper)
- `app/models/runtime/production_trial_envelope.py` (NEW; Pydantic v2 strict)
- `schema/production_trial_envelope.v1.schema.json` (NEW; emitted JSON Schema)
- `tests/fixtures/runtime/production_trial_envelope_golden.json` (NEW)
- 7 new test files per AC structure
- `tests/live/test_production_trial_smoke.py` (NEW; AC-G integration-exercise)
- `docs/dev-guide/migration-story-governance.json` updates (Slab 6 inaugural entry; version bumped to 2026-04-27-slab6)
- `docs/dev-guide/langgraph-migration-guide.md` updates (§"Production Runner" added)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` updates
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` Dev Agent Record populated

**Spec inputs (Acceptance Auditor reads these):**
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` — primary spec; 8 ACs (A through H) + 11 file-structure entries + Pydantic four-file-lockstep + 4 phasing decisions + 5-line D12 close protocol
- `_bmad-output/implementation-artifacts/production-graph-investigation-2026-04-27.md` — Codex's Phase A investigation report; the 6 missing integration points named there are the deliverable scope
- `docs/dev-guide/specialist-anti-patterns.md` A15 + A16 entries — the prevention pattern this story addresses
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — four-file-lockstep contract for `ProductionTrialEnvelope`

**Mode:** `"full"` (Acceptance Auditor activates; do NOT use `"no-spec"` mode).

**Project context:** existing `docs/project-context.md` + `CLAUDE.md` for repo conventions.

## Disposition rules (same as prior code reviews)

- **`patch` items:** Codex addresses in this dispatch before declaring done. Each `patch` becomes a small commit with descriptive message referencing this review file.
- **`defer` items:** file as deferred-inventory entries with explicit reactivation gates; do NOT silently shelve.
- **`dismiss` items:** explain in the close note why the dismissal is justified (cosmetic NIT vs real finding).
- **`decision_needed` items:** HALT and surface to operator with each option's tradeoff. Do not silently choose.

## Specific things to review for substantively (Acceptance Auditor focus)

The reviewers should pay particular attention to:

1. **AC-A real-handler resolution** — `compile_run_graph(...)` actually resolves specialist graph builders for the run lane, NOT just a thin wrapper that still calls `_passthrough_node` under the hood. Verify by tracing the compiler logic against `state/config/dispatch-registry.yaml`.

2. **AC-D HIL gate pause/resume per FR34** — gate-node execution actually persists LangGraph checkpoint, emits the right DecisionCard kind (G1/G2C/G3/G4), accepts `OperatorVerdict` via `app/gates/resume_api.py::resume_from_verdict`, restores state from checkpoint. Tamper-evidence (decision-card-digest binding + anti-replay tuple per Story 3.3 W-R1-3.3-2) preserved. NO bypass paths.

3. **AC-E LangSmith trace binding with trial_id** — verify the trace context wraps the entire trial invocation; specialist node calls become child runs within the parent trace; `app/runtime/economics.py::measure_trial_cost(trial_id)` filter actually finds spans by `extra.metadata.trial_id == trial_id`.

4. **AC-F evidence discipline** — `production_clone_launch_evidence` flips to `True` ONLY after at least one real specialist call completes through the live OpenAI path. Offline mode (per `--allow-offline-cost-report` or absent OPENAI_API_KEY) keeps evidence at `False`. No silent paths to `True` without real API call.

5. **AC-H A16 counter-pattern compliance** — the FR-trace traceability matrix entries for FR51 (replay byte-for-byte) and FR52 (head-to-head parity) should now be ready to flip from PARTIAL to TRACED because the integration-exercise AC (live-OpenAI smoke) provides end-to-end verification path. Verify the matrix update is consistent with the code change.

6. **Dual-source-of-truth concern** — Production runner reads from manifest + dispatch registry by default per Decision #2 recomposer choice. Verify the recomposer is the active path AND that the frozen `runtime/graphs/v42/dispatch-registry-snapshot.yaml` snapshot is read ONLY in replay-regression mode (per FR51), NOT in production runner mode. If the replay-regression path is broken or the production path silently uses the snapshot, that's a substantive finding.

7. **Deterministic M3 harness preservation** — `marcus/orchestrator/m3_trial.py` should be UNCHANGED. The harness stays as Slab 3 close artifact + replay-regression baseline. Trial CLI just stops wrapping it as production path. If the harness itself was modified, that's a substantive finding.

8. **Pydantic v2 strict on `ProductionTrialEnvelope`** — verify the four-file-lockstep is honored; tz-aware datetime enforced; closed-set Literals red-rejected; `production_clone_launch_evidence` is required boolean (no default; explicit set required). Per the checklist.

## Things NOT to flag

- Substrate inheritance from prior Slabs (don't re-litigate Slab 5a closure)
- Per-specialist code in `app/specialists/<name>/graph.py` (specialists are scaffold-conformant; out of Slab 6.1 scope)
- Cost-engineering machinery (5a.3 closed; out of scope unless production runner misuses it)
- Live-smoke tests in `tests/live/` for non-OpenAI providers (those are Batch 3 work; out of scope)
- WondercraftClient or NotionClient (not invoked by Slab 6.1; out of scope)

## Sequencing

Same as prior reviews:
1. Three layers run in parallel (Blind Hunter + Edge Case Hunter + Acceptance Auditor)
2. Triage merges + classifies
3. Codex addresses `patch` items in commits
4. Codex files `defer` items in deferred-inventory
5. Codex documents `dismiss` justifications
6. Codex surfaces `decision_needed` items to operator (do NOT silently choose)

## Deliverable

Triaged punch list at `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md` (or `2026-04-XX` if review runs across day boundary) with:
- Per-layer findings (Blind Hunter / Edge Case Hunter / Acceptance Auditor)
- Per-finding triage classification (patch / defer / dismiss / decision_needed)
- For each `patch`: which commit addresses it
- For each `defer`: which deferred-inventory entry was filed
- For each `dismiss`: justification
- For each `decision_needed`: options + recommendation, surfaced to operator

## Verification gates at dispatch close

- Code review file exists at the path above with all sections populated
- All `patch` items have corresponding commits
- All `defer` items appear in `_bmad-output/planning-artifacts/deferred-inventory.md`
- All `decision_needed` items are surfaced (not silently chosen)
- Existing test gates remain GREEN: 38 passed + 1 live smoke + ruff + lint-imports 9 KEPT
- After patches: re-run targeted slice for any patched files

## What this dispatch does NOT do

- Does NOT formally close Slab 6.1. After review clears, operator orchestrates the close (story `review → done`; deferred-inventory `5a-2-production-graph-entrypoint-substrate-gap` flips to RESOLVED; sprint-status flip; m5-decision.md amendment with Slab 6.1 close annotation).
- Does NOT update upstream-state.md condition #3 yet. The close orchestration handles that as a paired update.
- Does NOT dispatch Slab 6.2 (SciteProvider OAuth migration). That's operator-decision when/if to send.

## Effort estimate

~2-4 hours Codex time (3 layers parallel; triage + patch sequential).

## Operator-witnessed live-smoke evidence (preserved here for the close-record)

```
$ .venv\Scripts\python.exe -m pytest tests/live/test_production_trial_smoke.py -m live -q
.                                                                                                                [100%]
1 passed in 9.35s
```

Operator: juanleon@comcast.net (`Juan Leon` per git config)
Date: 2026-04-27
Cost: ≤ $0.10 per spec cap
Environment: operator's Windows machine, .venv, real `OPENAI_API_KEY` + `LANGSMITH_API_KEY` from `.env`
Result: PASS — first operator-witnessed end-to-end real production trial through the migrated runtime

## Final notes

This is the formal-close gate for Slab 6.1. The operator-witness gate cleared (live smoke PASSED on operator's machine). The independent-code-review gate is what this dispatch executes. After both clear, formal close orchestration runs, and the migration ships its actual production capability under both bounded-MVP scope (5a-shipped) and post-MVP production capability (6.1-shipped).

Done well, this review dispatch is the last step before "the migration is genuinely shipped" reads as honest in the close record. Done poorly (rubber-stamp review without substantive scrutiny), it would un-do the discipline that the dual-gate `operator_acceptance_gate` rationale exists to enforce.
