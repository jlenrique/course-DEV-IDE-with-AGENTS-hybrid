from __future__ import annotations

from scripts.utilities.migration_health_dashboard import HealthReport, render_text


def test_dashboard_output_contains_cost_rows() -> None:
    report = HealthReport(
        timestamp="2026-04-26T12:00:00+00:00",
        cost_reports={
            "trials_with_cost_reports": 2,
            "median_trial_cost_last_5": 0.171105,
            "drift_alerts_last_24h": 1,
        },
    )

    rendered = render_text(report)

    assert "Trials with cost reports" in rendered
    assert "Median trial cost USD (last 5)" in rendered
    assert "Drift alerts (last 24h)" in rendered
