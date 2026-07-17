---
id: 41-4
epic: 41
status: ready-for-dev   # rider R4 (Epic-42 sign-off) = the named twin of 41-3; the Epic-41 dollar brake
depends_on: 41-3
gate_mode: dual-gate   # LOCKSTEP (production_runner.py) + a real spend-enforcement rail
baseline_commit: 39f006ac
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
