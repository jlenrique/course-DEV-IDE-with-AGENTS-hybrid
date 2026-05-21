from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.models.runtime import AgentCostEntry, BudgetStatus, TrialEconomicsReport
from app.runtime.economics import record_trial_cost_report


def _sample_report() -> TrialEconomicsReport:
    return TrialEconomicsReport(
        trial_id="C1-M1-PRES-20260419B",
        measured_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        total_cost_usd=0.01325,
        per_agent_breakdown={
            "marcus": AgentCostEntry(
                agent_name="marcus",
                model_assigned="gpt-5",
                call_count=1,
                input_tokens=4200,
                output_tokens=800,
                cost_usd=0.01325,
            )
        },
        per_model_breakdown={"gpt-5": 0.01325},
        cascade_config_digest="a" * 64,
        pricing_table_digest="b" * 64,
        langsmith_trace_url="https://smith.langchain.com/traces/trace-123",
        drift_alerts=[],
        budget_status=BudgetStatus(state="under-budget", over_by_usd=0.0),
    )


def test_record_trial_cost_report_round_trips_json(tmp_path: Path) -> None:
    report = _sample_report()

    json_path = record_trial_cost_report(report.trial_id, report, runs_root=tmp_path)

    loaded = TrialEconomicsReport.model_validate_json(json_path.read_text(encoding="utf-8"))
    assert loaded.model_dump(mode="json") == report.model_dump(mode="json")


def test_record_trial_cost_report_markdown_contains_required_sections(tmp_path: Path) -> None:
    report = _sample_report()

    json_path = record_trial_cost_report(report.trial_id, report, runs_root=tmp_path)
    markdown = json_path.with_suffix(".md").read_text(encoding="utf-8")

    for heading in ("## Total", "## Per-Agent", "## Drift Alerts", "## Budget Status"):
        assert heading in markdown
