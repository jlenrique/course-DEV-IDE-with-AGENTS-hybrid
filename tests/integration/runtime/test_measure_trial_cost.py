from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.models.runtime import AgentCostEntry, BudgetStatus, TrialEconomicsReport
from app.runtime.cascade_config import load_cascade, load_pricing
from app.runtime.economics import load_trace_fixture, measure_trial_cost

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "runtime"
    / "trial_cost_trace_fixture.json"
)


def _history_entry(*, measured_at: datetime, marcus_cost: float) -> TrialEconomicsReport:
    return TrialEconomicsReport(
        trial_id=f"history-{measured_at.isoformat()}",
        measured_at=measured_at,
        total_cost_usd=marcus_cost,
        per_agent_breakdown={
            "marcus": AgentCostEntry(
                agent_name="marcus",
                model_assigned="gpt-5",
                call_count=1,
                input_tokens=2000,
                output_tokens=200,
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


def test_measure_trial_cost_builds_report_from_fixture_trace() -> None:
    root = load_trace_fixture(FIXTURE)

    report = measure_trial_cost(
        "C1-M1-PRES-20260419B",
        trace_root=root,
        cascade=load_cascade(),
        pricing=load_pricing(),
        history=[],
    )

    assert report.total_cost_usd > 0.0
    assert "irene" in report.per_agent_breakdown
    assert "gpt-5" in report.per_model_breakdown
    per_agent_total = round(
        sum(entry.cost_usd for entry in report.per_agent_breakdown.values()),
        8,
    )
    assert per_agent_total == report.total_cost_usd


def test_measure_trial_cost_populates_drift_alert_when_agent_spend_spikes() -> None:
    root = load_trace_fixture(FIXTURE)
    base = datetime(2026, 4, 26, 9, 0, tzinfo=UTC)
    history = [
        _history_entry(measured_at=base + timedelta(minutes=index), marcus_cost=0.001)
        for index in range(5)
    ]

    report = measure_trial_cost(
        "C1-M1-PRES-20260419B",
        trace_root=root,
        cascade=load_cascade(),
        pricing=load_pricing(),
        history=history,
    )

    assert any(alert.agent_name == "marcus" for alert in report.drift_alerts)
