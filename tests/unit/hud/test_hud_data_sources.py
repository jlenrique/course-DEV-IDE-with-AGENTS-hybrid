from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from scripts.utilities.hud_data_sources import (
    read_active_trial,
    read_cost_engineering_state,
    read_m5_window_state,
)


def _write_cost_report(run_dir: Path) -> None:
    payload = {
        "trial_id": run_dir.name,
        "measured_at": "2026-04-27T12:00:00Z",
        "total_cost_usd": 0.0125,
        "per_agent_breakdown": {
            "marcus": {
                "agent_name": "marcus",
                "model_assigned": "gpt-5",
                "call_count": 1,
                "input_tokens": 1000,
                "output_tokens": 100,
                "cost_usd": 0.00225,
            },
            "irene": {
                "agent_name": "irene",
                "model_assigned": "gpt-5",
                "call_count": 1,
                "input_tokens": 2000,
                "output_tokens": 800,
                "cost_usd": 0.01025,
            },
        },
        "per_model_breakdown": {"gpt-5": 0.0125},
        "cascade_config_digest": "a" * 64,
        "pricing_table_digest": "b" * 64,
        "langsmith_trace_url": "https://smith.langchain.com/traces/trace-1",
        "drift_alerts": [],
        "budget_status": {"state": "under-budget", "over_by_usd": 0.0},
    }
    (run_dir / "cost-report.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )


def test_read_active_trial_returns_none_without_runs(tmp_path: Path) -> None:
    assert read_active_trial(None, runs_root=tmp_path) is None


def test_read_active_trial_reads_cost_report(tmp_path: Path) -> None:
    run_dir = tmp_path / "trial-1"
    run_dir.mkdir()
    (run_dir / "trial-start.json").write_text(
        json.dumps({"status": "started", "preset": "production"}),
        encoding="utf-8",
    )
    _write_cost_report(run_dir)

    view = read_active_trial("trial-1", runs_root=tmp_path)

    assert view is not None
    assert view.trial_id == "trial-1"
    assert view.status == "started"
    assert view.current_step == "production"
    assert view.current_model == "gpt-5"
    assert view.per_agent_cost["marcus"] == 0.00225
    assert view.langsmith_trace_url == "https://smith.langchain.com/traces/trace-1"


def test_read_cost_engineering_state_reads_configs_and_budget(
    tmp_path: Path,
    monkeypatch,
) -> None:
    cascade = tmp_path / "cascade.yaml"
    pricing = tmp_path / "pricing.yaml"
    runs = tmp_path / "runs"
    runs.mkdir()
    cascade.write_text(
        yaml.dump({"marcus": {"model": "gpt-5"}, "specialists": {"irene": {"model": "gpt-5"}}}),
        encoding="utf-8",
    )
    pricing.write_text(
        yaml.dump(
            {
                "models": {
                    "gpt-5": {
                        "input_per_1m_tokens_usd": 1.25,
                        "output_per_1m_tokens_usd": 10.0,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    run_dir = runs / "trial-1"
    run_dir.mkdir()
    _write_cost_report(run_dir)
    monkeypatch.setenv("MARCUS_TRIAL_BUDGET_USD", "5.5")

    view = read_cost_engineering_state(
        cascade_path=cascade,
        pricing_path=pricing,
        runs_root=runs,
    )

    assert view.cascade_preview == {"marcus": "gpt-5", "irene": "gpt-5"}
    assert view.pricing_preview["gpt-5"]["input"] == 1.25
    assert view.median_trial_cost_last_5 == 0.0125
    assert view.soft_cap_budget_usd == 5.5


def test_read_m5_window_state_reports_remaining_days(tmp_path: Path) -> None:
    upstream = tmp_path / "upstream-state.md"
    deferred = tmp_path / "deferred-inventory.md"
    upstream.write_text(
        "SHIP-CONDITIONAL\nM2 Wondercraft live artifact open\n",
        encoding="utf-8",
    )
    deferred.write_text("production runner pending\n", encoding="utf-8")

    view = read_m5_window_state(
        upstream_state_path=upstream,
        deferred_inventory_path=deferred,
        now=datetime(2026, 4, 27, tzinfo=UTC),
    )

    assert view.visible is True
    assert view.days_remaining == 6
    assert view.open_conditions[0]["status"] == "open"
    assert "2026-05-03" in view.demotion_threshold
