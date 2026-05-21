from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models.runtime import AgentCostEntry, BudgetStatus, TrialEconomicsReport
from app.runtime.economics import compute_per_agent_drift


def _report(*, measured_at: datetime, marcus_cost: float) -> TrialEconomicsReport:
    return TrialEconomicsReport(
        trial_id=f"trial-{measured_at.isoformat()}",
        measured_at=measured_at,
        total_cost_usd=marcus_cost,
        per_agent_breakdown={
            "marcus": AgentCostEntry(
                agent_name="marcus",
                model_assigned="gpt-5",
                call_count=1,
                input_tokens=1000,
                output_tokens=100,
                cost_usd=marcus_cost,
            )
        },
        per_model_breakdown={"gpt-5": marcus_cost},
        cascade_config_digest="a" * 64,
        pricing_table_digest="b" * 64,
        langsmith_trace_url=None,
        drift_alerts=[],
        budget_status=BudgetStatus(state="no-cap", over_by_usd=0.0),
    )


def test_compute_per_agent_drift_returns_no_alert_within_band() -> None:
    base = datetime(2026, 4, 26, 12, 0, tzinfo=UTC)
    history = [
        _report(measured_at=base + timedelta(minutes=index), marcus_cost=1.0)
        for index in range(5)
    ]
    current = _report(measured_at=base + timedelta(hours=1), marcus_cost=1.4)

    alerts = compute_per_agent_drift(current, history)

    assert alerts == {}


def test_compute_per_agent_drift_emits_alert_when_over_band() -> None:
    base = datetime(2026, 4, 26, 12, 0, tzinfo=UTC)
    history = [
        _report(measured_at=base + timedelta(minutes=index), marcus_cost=1.0)
        for index in range(5)
    ]
    current = _report(measured_at=base + timedelta(hours=1), marcus_cost=1.75)

    alerts = compute_per_agent_drift(current, history)

    assert "marcus" in alerts
    assert alerts["marcus"].rolling_median_usd_per_call == 1.0
    assert alerts["marcus"].observed_usd_per_call == 1.75
    assert alerts["marcus"].deviation_pct == 75.0


def test_compute_per_agent_drift_returns_empty_when_history_shorter_than_five() -> None:
    base = datetime(2026, 4, 26, 12, 0, tzinfo=UTC)
    history = [
        _report(measured_at=base + timedelta(minutes=index), marcus_cost=1.0)
        for index in range(4)
    ]
    current = _report(measured_at=base + timedelta(hours=1), marcus_cost=2.0)

    alerts = compute_per_agent_drift(current, history)

    assert alerts == {}
