from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.runtime import TrialEconomicsReport

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "runtime"
    / "trial_economics_report_golden.json"
)
SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "schema"
    / "trial_economics_report.v1.schema.json"
)


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _valid_payload() -> dict[str, object]:
    return {
        "trial_id": "C1-M1-PRES-20260419B",
        "measured_at": datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        "total_cost_usd": 0.01325,
        "per_agent_breakdown": {
            "marcus": {
                "agent_name": "marcus",
                "model_assigned": "gpt-5",
                "call_count": 1,
                "input_tokens": 4200,
                "output_tokens": 800,
                "cost_usd": 0.01325,
            }
        },
        "per_model_breakdown": {
            "gpt-5": 0.01325,
        },
        "cascade_config_digest": "a" * 64,
        "pricing_table_digest": "b" * 64,
        "langsmith_trace_url": "https://smith.langchain.com/traces/trace-123",
        "drift_alerts": [],
        "budget_status": {
            "state": "under-budget",
            "over_by_usd": 0.0,
        },
    }


def test_trial_economics_report_strict_config() -> None:
    report = TrialEconomicsReport(**_valid_payload())
    assert report.model_config["extra"] == "forbid"
    assert report.model_config["validate_assignment"] is True


def test_trial_economics_report_rejects_tz_naive_datetimes() -> None:
    payload = _valid_payload()
    payload["measured_at"] = datetime(2026, 4, 26, 12, 0)
    with pytest.raises(ValidationError):
        TrialEconomicsReport(**payload)


def test_trial_economics_report_rejects_negative_costs() -> None:
    payload = _valid_payload()
    payload["total_cost_usd"] = -0.01
    with pytest.raises(ValidationError):
        TrialEconomicsReport(**payload)


def test_trial_economics_report_budget_state_closed() -> None:
    payload = _valid_payload()
    payload["budget_status"] = {"state": "surprise", "over_by_usd": 0.0}
    with pytest.raises(ValidationError):
        TrialEconomicsReport(**payload)


def test_trial_economics_report_cost_posture_is_internally_consistent() -> None:
    payload = _valid_payload()
    payload["cost_posture"] = "exact"
    payload["unavailable_attempt_count"] = 1
    with pytest.raises(ValidationError, match="cost posture contradicts"):
        TrialEconomicsReport(**payload)


def test_trial_economics_report_round_trip_and_schema_pin() -> None:
    payload = FIXTURE.read_text(encoding="utf-8")
    report = TrialEconomicsReport.model_validate_json(payload)

    assert report.model_dump(mode="json") == json.loads(payload)
    assert _hash(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))) == _hash(
        TrialEconomicsReport.model_json_schema()
    )
