from __future__ import annotations

from app.runtime.economics import check_trial_budget


def test_check_trial_budget_returns_no_cap_when_budget_unset() -> None:
    status = check_trial_budget(0.75, None)
    assert status.state == "no-cap"
    assert status.over_by_usd == 0.0


def test_check_trial_budget_returns_under_budget_when_total_within_cap() -> None:
    status = check_trial_budget(0.75, 1.0)
    assert status.state == "under-budget"
    assert status.over_by_usd == 0.0


def test_check_trial_budget_returns_over_budget_warning_when_total_exceeds_cap() -> None:
    status = check_trial_budget(1.25, 1.0)
    assert status.state == "over-budget-warning"
    assert status.over_by_usd == 0.25
