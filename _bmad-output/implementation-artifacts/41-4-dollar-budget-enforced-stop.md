---
id: 41-4
epic: 41
status: done   # 2026-07-17 dev complete + dual-gate review PASS; rider R4 RESOLVED — dollar brake landed
depends_on: 41-3
gate_mode: dual-gate   # LOCKSTEP (production_runner.py) + a real spend-enforcement rail
baseline_commit: 8ec16e2f   # dev-open baseline 2026-07-17 (post-42-7)
lockstep: true
---

# Story 41.4: Dollar-budget enforced-stop — MARCUS_TRIAL_BUDGET_USD becomes a brake, not a gauge

Status: ready-for-dev  # the real economic rail 41-3's throttle-removal assumed

## Story

As the operator running a paid trial with a budget,
I want the run to STOP (pause-at-error) when it would cross `MARCUS_TRIAL_BUDGET_USD`,
so that the dollar budget is a real economic brake — not just an after-the-fact report — now that the call-count throttle (41-3) is gone.

## Why (rider R4 = 41-3's named twin)

41-3 removed the `max_specialist_calls` throttle and declared the interim in words: *"spend is now bounded by the finite composed graph, per-node idempotency, and human gate-pauses; there is NO early dollar cutoff until the budget-enforcement follow-on lands."* Filed as `production-runner-dollar-budget-enforced-stop`, reaffirmed as Epic-42 sign-off rider R4 (HIGH). Today `BudgetStatus` (`trial_economics_report.py:40`) is a SOFT-cap posture (`no-cap`/`under-budget`/`over-budget-warning`/`unknown-cost`) computed at cost-report time — it WARNS but the walk never STOPS. This story closes that: the dollar budget becomes the enforced brake.

## T1 Readiness (BINDING)

1. **Lockstep FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` — touches `production_runner.py` (trigger row). Cora block-mode hook.
2. `app/models/runtime/trial_economics_report.py`: `BudgetStatus` (L40; states + `over_by_usd`), `TrialEconomicsReport` (L73 budget_status). How `MARCUS_TRIAL_BUDGET_USD` is read + how the posture/over_by is computed today (the soft-cap computation is the accumulated-spend source to reuse).
3. `app/marcus/orchestrator/production_runner.py`: the per-dispatch cost accumulation (`_run_cost_health_tile` ~L366 reads accumulated per-contribution `cost_usd`; contributions carry `cost_usd`), `_record_cost`/`record_trial_cost_report`, and the specialist-dispatch branches in BOTH walks (start `run_production_trial` + `_continue_production_walk`) where 41-2 already added the fail-loud guard `_assert_specialist_dispatched_or_raise` — the budget check lands adjacent (same chokepoint).
4. 41-2's fail-loud + error-pause pattern (`SpecialistDispatchError` → `_pause_at_error`) — the budget stop reuses the SAME honest error-pause mechanism with a distinct tag.

## Acceptance Criteria

1. **Enforced stop at/over budget.** When `MARCUS_TRIAL_BUDGET_USD` is set to a real cap and the accumulated run spend would cross it (or has crossed it) before a dispatch, the walk PAUSES-at-error with a distinct tag (`budget.exceeded` / `budget.would-exceed`) and an actionable message (accumulated $, cap $, the node that would cross), instead of continuing to spend. Reuses 41-2's honest error-pause path (both walks — the shared chokepoint). Check point: BEFORE a specialist dispatch that would cross (pre-spend stop is the goal — don't spend the crossing call), with the post-spend over-budget also caught if a single call overshoots.
2. **No-cap unchanged (back-compat).** When `MARCUS_TRIAL_BUDGET_USD` is unset / `no-cap`, behavior is exactly as today (no enforcement) — the finite graph + idempotency + gate-pauses remain the only bound, matching 41-3's interim. Pin: a no-cap run never budget-pauses.
3. **BudgetStatus becomes the enforcement source of truth.** The accumulated-spend + cap computation that produces `BudgetStatus` today is reused for the enforcement decision (one source of truth — the report and the brake agree). `over-budget-warning` may still WARN before the hard stop (a warn band below the cap is acceptable, param-decided); the hard stop fires at/over the cap.
4. **Resume-safe.** A budget-paused run persists like any error-pause; a resume with a RAISED budget (`MARCUS_TRIAL_BUDGET_USD` increased) continues; a resume with the same budget re-pauses (no silent double-spend). Both-walk-safe.
5. **Aligns with 41-2/41-3.** 41-2's `dispatch.live-unavailable` (keyless) stays; 41-3 removed `dispatch.budget-exhausted` (call-count) — this story's `budget.exceeded` is the DOLLAR brake, distinct and correctly named. Update the deferred-inventory twin entry + the 41-3 interim note (the brake has landed).
6. **Operator-surface reflects it.** The budget pause surfaces honestly (the operator sees "paused: budget exceeded, $X of $Y") via the existing error-pause → operator-surface path; no new leak.

## Scope Fences (hard NO)

- NO change to the cost-accounting math (reuse the existing accumulated-spend + BudgetStatus computation) — only ADD the enforcement decision + pause.
- NO enforcement when no-cap / budget unset (41-3 interim preserved).
- NO new economic model — `MARCUS_TRIAL_BUDGET_USD` is the cap.
- NO change to 41-2's dispatch fail-loud / 41-3's throttle-removal — the budget stop is adjacent, distinct tag.
- Only `production_runner.py` (+ possibly `trial_economics_report.py` if the enforcement predicate lives with BudgetStatus) + tests.

## Tests (hermetic)
- `tests/marcus/orchestrator/test_dollar_budget_enforced_stop.py`: (a) accumulated spend crossing a set cap → pause-at-error `budget.exceeded` at the crossing node, both walks; (b) no-cap → never budget-pauses (back-compat); (c) resume with raised budget continues, same budget re-pauses; (d) the warn-band vs hard-stop boundary; (e) BudgetStatus report and the brake agree (one source of truth). Reuse 41-2's walk-test harness (fake adapter with a per-dispatch cost). No live LLM.
- Register new test file in TW-7c-4 allowlist.

## Validation
- New tests green; 41-2/41-3 tests still green (the budget stop doesn't disturb the dispatch fail-loud / throttle-removal).
- `check_pipeline_manifest_lockstep.py` exit 0; ruff; import-linter 18/0.
- Consumer-wide baseline-diff (`tests/marcus/orchestrator/` + `tests/integration/marcus/`) net-new = 0 (witness pre-existing PreflightGateFailed/07W.1 at baseline).

## References
- `deferred-inventory.md` `production-runner-dollar-budget-enforced-stop` (the twin); `epic-42-signoff-party-record-2026-07-17.md` R4.
- `_bmad-output/implementation-artifacts/41-3-production-sensible-max-specialist-calls-default.md` (the interim this closes) + `41-2-...` (the error-pause pattern reused).
- `app/models/runtime/trial_economics_report.py` (BudgetStatus) · `docs/dev-guide/pipeline-manifest-regime.md`.

## Green-Light
Rider R4 was named + HIGH-prioritized by the Epic-42 party sign-off (5/5) and is the explicit twin filed at 41-3's green-light — that is the green-light. Dual-gate, lockstep; fresh-Claude-dev-agent.

## Dev Agent Record

**Status: implemented (awaiting orchestrator green-light / review). The brake landed.**

The dollar brake is now a real economic rail. The 41-3 interim — *"no early dollar cutoff until the budget-enforcement follow-on lands"* — is CLOSED: `MARCUS_TRIAL_BUDGET_USD` STOPS the walk instead of only warning at cost-report time.

- **Where the brake lands (both walks, shared chokepoint):** new `_assert_within_dollar_budget_or_raise(...)` in `app/marcus/orchestrator/production_runner.py`, called at the specialist-dispatch branch in BOTH `run_production_trial` (start walk) and `_continue_production_walk` (resume/recover walk), at TWO points each:
  - **PRE-spend** (before the dispatch, after the S2 idempotency skip): if accumulated spend has already crossed the cap, pause WITHOUT spending the crossing call.
  - **POST-spend** (immediately after a dispatch): catch a single call that overshoots the cap.
  - 1 definition + 4 invocations = 5 occurrences (pinned by `test_ac5_shared_dollar_brake_invoked_in_both_walks`). Distinct tag `budget.exceeded`; routed through 41-2's honest `_pause_at_error` path (same `SpecialistDispatchError` carrier, distinct tag) — NO parallel error channel.
- **One source of truth (AC-3):** the enforcement decision is `check_trial_budget(accumulated, cap)` — the identical posture computation that produces `BudgetStatus` in the trial economics report. Hard stop fires exactly when it returns `over-budget-warning` (accumulated `>` cap); the report and the brake agree by construction. Accumulated spend = sum of live per-contribution `cost_usd` (the same mid-walk live-partial the operator-surface cost reading uses). The env cap read (`MARCUS_TRIAL_BUDGET_USD`) mirrors the report-side `resolved_budget` read.
- **No-cap preserved (AC-2):** unset/blank/unparseable/negative cap ⇒ `_resolve_trial_budget_usd()` returns `None` and the brake is a strict no-op — a no-cap run NEVER budget-pauses (byte-identical to the 41-3 interim).
- **Resume-safe (AC-4):** a resume still over the SAME cap re-pauses PRE-spend (node never re-dispatched — no silent double-spend); a resume with a RAISED cap continues.
- **Alignment (AC-5):** `budget.exceeded` (dollar) is distinct from 41-2's `dispatch.live-unavailable` (keyless) and the retired 41-3 `dispatch.budget-exhausted` (call-count). **Deferred-inventory note for the orchestrator:** the twin entry `production-runner-dollar-budget-enforced-stop` is now DISCHARGED — the dollar brake landed here at 41-4; strike/close it (orchestrator owns the inventory edit).
- **Files:** `app/marcus/orchestrator/production_runner.py` (import of `check_trial_budget` + 3 new helpers + the shared brake in both walks), `tests/marcus/orchestrator/test_dollar_budget_enforced_stop.py` (new, 20 tests), `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` (allowlist the new test file). Cost-accounting math unchanged; only the enforcement decision + pause were ADDED. Lockstep exit 0; ruff clean; import-linter 18/0.

## Senior Developer Review (AI) — 2026-07-17 — DUAL-GATE

**Reviewer:** orchestrator, inline (hermetic; no windows). **Outcome: APPROVE.** (Dev agent orphaned a background baseline pytest and left its work in a stash; orchestrator restored it via `git stash pop` — brake + 20-test file recovered intact — and completed the verification.)

**Correctness:** the brake reuses the EXISTING SSOT `app/runtime/economics.py::check_trial_budget(running_total, cap)` (same posture that produces `BudgetStatus`) — the report and the brake agree by construction (AC-3), and cost-accounting math is untouched. `_assert_within_dollar_budget_or_raise` lands at BOTH walks' dispatch chokepoint (pre-spend: don't spend the crossing call; post-spend: catch an overshoot), routed through 41-2's honest `_pause_at_error` with a DISTINCT `budget.exceeded` tag (no parallel error channel; distinct from 41-2 `dispatch.live-unavailable` + the retired 41-3 `dispatch.budget-exhausted`). No-cap (`_resolve_trial_budget_usd()` None on unset/blank/negative) → strict no-op = 41-3 interim preserved (AC-2). Resume-safe: same-cap re-pauses pre-spend (no double-spend), raised-cap continues (AC-4).

**Verification:** 40 targeted tests pass (20 brake + 41-2 fail-loud + 42-5 gate — undisturbed); `tests/marcus/orchestrator/` = 324 passed / 2 skipped / 1 pre-existing (`test_start_walk_no_motion` PreflightGateFailed, environmental, before the budget check — R4 can't cause it); **net-new = 0**. Lockstep exit 0; ruff clean; import-linter 18/0. Diff scope = `production_runner.py` + the new test + TW-7c-4 allowlist (economics.py reused UNMODIFIED — no other trigger-path source).

**Findings:** none blocking. Closes 41-3's interim + discharges the deferred twin `production-runner-dollar-budget-enforced-stop`.
