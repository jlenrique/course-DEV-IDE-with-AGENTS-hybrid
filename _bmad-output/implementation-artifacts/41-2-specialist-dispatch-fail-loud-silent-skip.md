---
id: 41-2
epic: 41
status: ready-for-dev
depends_on: 41-1
gate_mode: dual-gate   # block_mode/lockstep + load-bearing runtime invariant
anchor_provenance: HEAD 23480353  # all line anchors verified against this tree; re-verify at dev-open
baseline_commit: 3919c7fbe28f8fd18a8360eae707a486084db958  # dev-open baseline 2026-07-16 (post-41-1)
lockstep: true   # touches app/marcus/orchestrator/production_runner.py (block_mode_trigger_paths)
---

# Story 41.2: Specialist-dispatch fail-loud on silent skip — both walks

Status: done  # 2026-07-16 dev complete (fresh Claude dev agent) + dual-gate review PASS; LOCKSTEP; RED-first vs bc747b51 proven

## Story

As the production runtime,
I want a specialist node that is entered and does not emit its contribution to **fail loud at that node** (naming the specialist and the cause) instead of silently marking itself complete,
so that a skipped required specialist (e.g. CD @ 4.75) can never again surface as a misattributed downstream error (`builder.gary.upstream-missing` at §06) three nodes away from the real cause.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-resume-walk-dispatch-integrity-2026-07-16.md` §Story 41-2 (E41-AC2) + the **binding invariant** (Winston P-2).
- **Green-light:** `party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` — P-1 (two-story split), P-2 (invariant, both walks), P-3 (RED-first vs `bc747b51`).
- **Depends on 41-1:** the front-door preflight lands first. 41-2 is the defense-in-depth that makes the CLASS of silent-skip impossible even if a future path (offline-flag slip, budget exhaustion, a new skip branch) reopens it.
- **Two-walk trap (memory `project-production-runner-two-walks`):** the invariant MUST land in BOTH the start walk (`run_production_trial`, specialist branch ~L3595-3637) and the resume/recover walk (`_continue_production_walk`, specialist branch ~L4587-4627). A fix in one copy leaves the other rotten.

## Binding invariant (the spec sentence — Winston P-2)

> In a production run (`allow_offline_cost_report=False`), a specialist node that is **entered** and is **not already-carrying** its contribution MUST emit a contribution or **fail loud at that node**. Silent advance is forbidden.

## T1 Readiness (BINDING readings before any code)

1. **Lockstep gate FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` + `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` (`production_runner.py` IS a trigger row). Read before any code; Cora block-mode hook gates this story.
2. `app/marcus/orchestrator/production_runner.py` — the **two** specialist-dispatch branches:
   - Start walk (`run_production_trial`, L3061): L3595-3637 — `if node_kind == "specialist" and specialist_calls < max_specialist_calls:` → already-carrying skip (L3600-3609) → `if _has_live_openai() and not allow_offline_cost_report:` dispatch (L3610-3636) → **`graph_step_completed = True` (L3637) set unconditionally**.
   - Resume/recover walk (`_continue_production_walk`, L4102): L4587-4627 — same shape; `allow_offline_cost_report` read at L4150 (`runner.get(..., False)`); **`graph_step_completed = True` (L4627) set unconditionally**.
   - `_has_live_openai` (L211), `_active_node_handler` (L1838), `__production_node_kind__`/`__production_specialist_id__` stamping (L2070-area).
3. **The idempotent-resume path is legitimate and must be preserved:** the already-carrying skip (L3600/L4590) is correct — a resumed node that already has its contribution is not re-dispatched. The fail-loud must fire ONLY for entered-and-NOT-carrying-and-NOT-dispatched, never for already-carrying.
4. Frozen `bc747b51` run dir — the RED reproduction substrate (`run.json`, `error-pause.json`, node path 04.55 → 4.75 → 05/05B → 06).
5. Existing offline-harness tests that resume/run with `allow_offline_cost_report=True` — they MUST stay green (the fail-loud is gated on `not allow_offline_cost_report`).

## Acceptance Criteria

1. **Fail-loud at the node — resume/recover walk.** In `_continue_production_walk`, when `node_kind == "specialist"`, the node is NOT already-carrying, and dispatch did NOT run because live was unavailable while `allow_offline_cost_report=False`, the walk raises at that node with a tag `dispatch.live-unavailable` (or a shared, specific tag) and a message naming the specialist_id + node.id + cause — instead of `graph_step_completed = True`. The raise carries enough context to error-pause honestly at that node (specialist_id, node_id, node_index).
2. **Fail-loud at the node — start walk.** The SAME invariant lands in `run_production_trial`'s specialist branch (L3595-3637). Both walks enforce identically (a shared helper is preferred so they cannot drift — Yui/Winston).
3. **RED-first vs the frozen trial (P-3, BLOCKING evidence bar).** A test reconstructs a keyless resume walk (`_has_live_openai()` False, `allow_offline_cost_report=False`) over the `bc747b51` manifest+envelope shape, drives it to node 4.75, and asserts it raises `dispatch.live-unavailable` **at 4.75** — NOT `builder.gary.upstream-missing` at 06. This test must be RED against the current code (proving the misattribution) and GREEN after the fix. No live call.
4. **Idempotent resume preserved.** A node already carrying its contribution still skips cleanly (no raise) — the already-carrying branch is untouched. Pin: a resume where 4.75 already has a `cd` contribution advances past it silently and correctly.
5. **Offline harness preserved.** With `allow_offline_cost_report=True`, specialist nodes still skip dispatch WITHOUT raising (offline reports never dispatch live) — the fail-loud is strictly gated on `not allow_offline_cost_report`. Existing offline-harness suites stay green.
6. **Budget/max-calls is a DISTINCT honest stop (not folded into this tag).** If `specialist_calls >= max_specialist_calls` causes the branch to be skipped, that is a budget condition — it must ALSO not silently advance a required node, but it raises a budget-specific tag (`dispatch.budget-exhausted` or the existing budget-guard path), not `live-unavailable`. Name the two causes distinctly so the operator sees the true reason. (If the existing budget-guard already fail-louds elsewhere, cite it and assert this branch defers to it; do not double-raise.)

## Scope Fences (hard NO)

- **NO change to the already-carrying idempotency contract** (S2 per-node keying) — it stays exactly as-is.
- **NO change to the offline-harness dispatch-skip** except that a required node in a production run raises; offline (`allow_offline_cost_report=True`) is untouched.
- **NO change to `trial.py`** — that's 41-1.
- **NO widening of what counts as "required"** beyond the invariant: entered + not-already-carrying + not-dispatched in a production run. Do not add per-node "required" manifest flags this pass (a specialist node that is traversed in a production run is required by construction — if it were optional it would be composed out of the manifest).
- **NO silent gate/orchestration behavior change** — only the specialist branch of both walks.
- **Mid-dev drift into any OTHER trigger row** (`workbook_wiring.py`, `pipeline-manifest.yaml`, `operator_surface_assembler.py`, `production_trial_envelope.py`, etc.) is a STOP → party-gate.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/orchestrator/production_runner.py` | **trigger (manifest)** | **yes** (both specialist branches — fail-loud invariant) |
| `app/marcus/cli/trial.py` | not listed | **NO** (41-1) |

**Verdict: lockstep regime TRIGGERED.** Read `pipeline-manifest-regime.md` at T1; Cora block-mode hook gates; lockstep checker (`check_pipeline_manifest_lockstep.py`) exit 0 required before review.

## Dev Notes

- Prefer a shared helper, e.g. `_assert_specialist_dispatched_or_raise(*, node, specialist_id, node_index, dispatched, allow_offline_cost_report)` called from both walks right where `graph_step_completed = True` is set today, so the two copies enforce ONE implementation (two-walk trap defense). Track whether dispatch actually ran (the `if _has_live_openai() and not allow_offline_cost_report:` branch) via an explicit local, and raise when required-and-not-dispatched-and-not-already-carrying.
- The raise should produce the same honest error-pause shape the builder path uses (tag + message + node context) so the operator sees `dispatch.live-unavailable @ 4.75 (cd)` instead of `builder.gary.upstream-missing @ 06`.
- Keep the `specialist_calls < max_specialist_calls` outer condition semantics in mind: if that outer guard is False, the branch body (including any new raise) does not run — handle budget as AC-6 specifies (distinct tag or defer to the existing budget-guard), don't let a budget-exhausted required node silently advance either.
- Tests: `tests/marcus/orchestrator/test_dispatch_fail_loud_silent_skip.py` (new) — both-walk RED-first vs `bc747b51` shape (AC-3); idempotent-resume preserved (AC-4); offline preserved (AC-5); budget-distinct-tag (AC-6); start-walk parity (AC-2). Fixtures = mutated copies of the frozen `bc747b51` run shape (live-shape rule), never synthetic. No live LLM/network.

## References

- `_bmad-output/planning-artifacts/epics-resume-walk-dispatch-integrity-2026-07-16.md` (§invariant)
- `_bmad-output/planning-artifacts/party-greenlight-post-trial-bc747b51-arc-2026-07-16.md` (P-1/P-2/P-3)
- `docs/dev-guide/pipeline-manifest-regime.md` · `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`
- memory `project-production-runner-two-walks` (both-walk discipline)
- `state/config/runs/bc747b51-7009-4742-9f65-8de6abc29ca4/{run.json,error-pause.json,cost-report.json,operator-surface.json}`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Winston/John/Amelia/Murat/Sally, orchestrator concurred. Folded: P-1 (two-story split, one head); P-2 (invariant sentence, BOTH walks, shared helper); P-3 (RED-first vs `bc747b51` asserting fail-loud AT 4.75 not at 06); Murat's AC-6 (budget is a distinct honest stop, distinct tag); the idempotent-resume + offline-harness preservation fences. Dual-gate per Winston (lockstep + load-bearing invariant). Status → ready-for-dev.

## Dev Agent Record

**Dev complete 2026-07-16 (fresh Claude dev agent, general-purpose subagent). Baseline `3919c7fb`. Status → review → done.**

### File List
- `app/marcus/orchestrator/production_runner.py` (M) — shared `_assert_specialist_dispatched_or_raise` guard (offline/dispatched → return; else budget-exhausted vs live-unavailable, distinct tags); BOTH walk specialist branches restructured (outer `and specialist_calls < max_specialist_calls` → inner `budget_available` local; `dispatched_specialist` bool; guard call → `_pause_at_error` on raise). +148/−4.
- `tests/marcus/orchestrator/test_dispatch_fail_loud_silent_skip.py` (A) — 8 hermetic tests (AC-1..AC-6, RED-first vs bc747b51).
- `tests/integration/marcus/test_production_runner_gate_pause_resume.py` (M) — the bug's own regression pin renamed `test_starved_resume_fails_loud_budget_exhausted_at_cd_node`; asserts the NEW contract (`dispatch.budget-exhausted @ 4.75 (cd)`, not `builder.gary.upstream-missing @ 06`); recover leg re-enters 4.75, dispatches cd, re-pauses at next starved node.
- `tests/integration/marcus/test_workbook_band_wiring.py` (M) — 4 `test_real_start_then_continuation_reaches_band_in_order[*]` setups fixed (keyless silent-skip reliance → valid production config: `sk-test` key + fake adapter; `[False-None]` param carries a plan_authority_receipt for the now-live §06).
- `tests/integration/marcus/test_pre_gate_marcus_langsmith_trace.py` (M) + `tests/integration/marcus/test_runner_threads_pre_fill_to_decision_card.py` (M) — cap=0 setups → cap=12 + deterministic fake adapter (real subjects/assertions unchanged).
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` (M) — registered the new + updated test files in `PERMITTED_PYTHON_DIFFS` (governance allowlist).

### Completion Notes
- Fail-loud invariant landed in BOTH walks via one shared guard (two-walk-trap defense). RED-first proven: pre-fix, keyless resume → silent `completed`; cap=1 → `builder.gary.upstream-missing @ 06` (the exact frozen misattribution). Post-fix: `dispatch.live-unavailable` / `dispatch.budget-exhausted` AT 4.75. Idempotent-resume + offline-harness preserved.
- **DIAGNOSIS CORRECTION surfaced here:** the real `bc747b51` cause was `max_specialist_calls=1` starvation (confirmed frozen `runner`), not keyless — so AC-6 (budget) is the primary real fix, AC-3 (keyless) its twin. Root-fix (remove the throttle) filed as **41-3** per operator steer.
- Contract-encoding tests updated (green-light authorized the CD-fails-loud-at-4.75 contract change) + TW-7c-4 registration.

### Change Log
- 2026-07-16: fail-loud invariant both walks (Story 41-2); 6 old-contract tests aligned; TW-7c-4 registered; dual-gate review PASS; done.

## Senior Developer Review (AI) — 2026-07-16 — DUAL-GATE

**Reviewer:** orchestrator, inline adversarial review (correctness + edge + acceptance lenses) — run INLINE rather than as parallel test-running subagents, to honor the operator's explicit no-console-window-storm constraint (2026-07-16); appropriate given the surgical, both-walk-symmetric, RED-first-proven change. **Outcome: APPROVE.**

**Correctness (adversarial diff read):** guard precedence correct (`offline|dispatched → return`; `not budget → budget-exhausted`; else `live-unavailable`) — distinct tags, no double-raise. Both walks fixed identically; the outer budget condition correctly moved INSIDE so a budget-exhausted node now ENTERS the branch and fails loud instead of falling through to silent advance. Already-carrying idempotency skip preserved BEFORE the guard; batch-wait early-return exits before the guard (a batch pause is not a silent skip); `dispatched` (call result) vs `dispatched_specialist` (bool) are distinct — no collision. Raise routes through `_pause_at_error` (builder-parity honest error-pause).

**Acceptance:** AC-1..AC-6 satisfied with real tests; AC-3 RED-before/GREEN-after confirmed by the dev's stash-witness; AC-6 budget/live distinction pinned; idempotency (AC-4) + offline (AC-5) preserved. Contract-encoding tests (incl. the bug's own regression pin) updated to the new fail-loud contract — not weakened.

**Verification:** new test file 8/8; lockstep checker exit 0; TW-7c-4 audit PASS; ruff clean; import-linter 18/0; baseline-diff (git-stash) net-new failures = 0 (residual 65 are pre-existing `PreflightGateFailed openai=fail/hud-server-healthz=fail` environmental, witnessed at baseline).

**Findings:** none blocking. One NIT (dismissed): `dispatched` vs `dispatched_specialist` naming is slightly confusing but not a defect.

**Note:** AC-6's `dispatch.budget-exhausted` is keyed to the call-count throttle (`max_specialist_calls`). Per the operator steer, **41-3 removes that throttle** (dollar budget becomes the guard); when 41-3 lands, this tag re-keys to the dollar budget and the `test_starved_*` pin updates accordingly. 41-2's core invariant (fail loud at the node, never silent-advance/misattribute) is unchanged by that.
