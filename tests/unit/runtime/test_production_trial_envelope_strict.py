from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.runtime.production_trial_envelope import ProductionTrialEnvelope

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "runtime"
    / "production_trial_envelope_golden.json"
)


def _payload() -> dict[str, object]:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["trial_id"] = UUID(payload["trial_id"])
    if payload.get("production_envelope") is not None:
        payload["production_envelope"]["trial_id"] = UUID(
            payload["production_envelope"]["trial_id"]
        )
        payload["production_envelope"]["contributions"] = tuple(
            payload["production_envelope"]["contributions"]
        )
    return payload


def test_strict_config_rejects_unknown_fields() -> None:
    payload = _payload()
    payload["unexpected"] = "red"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProductionTrialEnvelope.model_validate(payload)


def test_tz_aware_datetime_enforced() -> None:
    payload = _payload()
    payload["started_at"] = datetime(2026, 4, 27, 10, 0)

    with pytest.raises(ValidationError, match="timezone-aware"):
        ProductionTrialEnvelope.model_validate(payload)

    payload["started_at"] = datetime(2026, 4, 27, 10, 0, tzinfo=UTC)
    assert ProductionTrialEnvelope.model_validate(payload).started_at.tzinfo is not None


def test_literal_red_rejection() -> None:
    payload = _payload()
    payload["status"] = "paused"

    with pytest.raises(ValidationError):
        ProductionTrialEnvelope.model_validate(payload)


def test_production_clone_launch_evidence_is_explicitly_required() -> None:
    payload = _payload()
    payload.pop("production_clone_launch_evidence")

    with pytest.raises(ValidationError, match="Field required"):
        ProductionTrialEnvelope.model_validate(payload)


def test_production_envelope_is_required_full_embed() -> None:
    payload = _payload()
    payload.pop("production_envelope")

    with pytest.raises(ValidationError, match="Field required"):
        ProductionTrialEnvelope.model_validate(payload)


def test_golden_fixture_validates_from_json() -> None:
    envelope = ProductionTrialEnvelope.model_validate_json(FIXTURE.read_text(encoding="utf-8"))

    assert envelope.schema_version == "production-trial-envelope.v1"
    assert envelope.production_clone_launch_evidence is False
    assert envelope.production_envelope is not None
    assert envelope.production_envelope.contributions == ()


def test_json_schema_lockstep_contains_required_evidence_field() -> None:
    schema_path = Path(__file__).resolve().parents[3] / "schema" / (
        "production_trial_envelope.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["additionalProperties"] is False
    assert "production_clone_launch_evidence" in schema["required"]
    assert "production_envelope" in schema["required"]
    assert "production_envelope" in schema["properties"]
    assert schema == ProductionTrialEnvelope.model_json_schema()
