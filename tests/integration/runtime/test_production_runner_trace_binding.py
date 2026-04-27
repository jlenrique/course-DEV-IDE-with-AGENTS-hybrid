from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from app.runtime.economics import load_trace_fixture, measure_trial_cost

TRIAL_ID = UUID("12345678-1234-4234-8234-123456789abc")


def test_trace_fixture_metadata_contains_trial_id(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace-fixture.json"
    trace_path.write_text(
        json.dumps(
            {
                "root": {
                    "id": str(TRIAL_ID),
                    "trace_id": str(TRIAL_ID),
                    "name": "production trial",
                    "run_type": "chain",
                    "extra": {"metadata": {"trial_id": str(TRIAL_ID)}},
                    "child_runs": [
                        {
                            "id": "11111111-1111-4111-8111-111111111111",
                            "trace_id": str(TRIAL_ID),
                            "name": "Texas",
                            "run_type": "llm",
                            "prompt_tokens": 100,
                            "completion_tokens": 20,
                            "total_tokens": 120,
                            "extra": {
                                "metadata": {
                                    "trial_id": str(TRIAL_ID),
                                    "specialist_id": "texas",
                                    "model_id": "gpt-5-nano",
                                }
                            },
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    root = load_trace_fixture(trace_path)
    assert root.extra["metadata"]["trial_id"] == str(TRIAL_ID)


def test_measure_trial_cost_returns_report_from_production_runner_trace(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace-fixture.json"
    trace_path.write_text(
        json.dumps(
            {
                "root": {
                    "id": str(TRIAL_ID),
                    "trace_id": str(TRIAL_ID),
                    "name": "production trial",
                    "run_type": "chain",
                    "extra": {"metadata": {"trial_id": str(TRIAL_ID)}},
                    "child_runs": [
                        {
                            "id": "11111111-1111-4111-8111-111111111111",
                            "trace_id": str(TRIAL_ID),
                            "name": "Texas",
                            "run_type": "llm",
                            "prompt_tokens": 100,
                            "completion_tokens": 20,
                            "total_tokens": 120,
                            "extra": {
                                "metadata": {
                                    "trial_id": str(TRIAL_ID),
                                    "specialist_id": "texas",
                                    "model_id": "gpt-5-nano",
                                }
                            },
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )

    report = measure_trial_cost(
        str(TRIAL_ID),
        trace_root=load_trace_fixture(trace_path),
        history=[],
    )
    assert report.total_cost_usd > 0
    assert "texas" in report.per_agent_breakdown
