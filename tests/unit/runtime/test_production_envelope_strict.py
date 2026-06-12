from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.runtime.production_envelope import (
    ProductionEnvelope,
    SpecialistContribution,
    compute_output_digest,
)

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "runtime"
    / "production_envelope_golden.json"
)


def _contribution(**overrides: object) -> SpecialistContribution:
    payload = {
        "specialist_id": "texas",
        "contributed_at": datetime(2026, 4, 27, 12, 0, tzinfo=UTC),
        "output": {"status": "complete"},
        "cost_usd": 0.0,
        "model_used": "gpt-5-nano",
        "output_digest": compute_output_digest({"status": "complete"}),
    }
    payload.update(overrides)
    return SpecialistContribution.model_validate(payload)


def test_strict_config_rejects_unknown_fields() -> None:
    payload = {
        "trial_id": UUID("12345678-1234-4234-8234-123456789abc"),
        "unexpected": "red",
    }

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProductionEnvelope.model_validate(payload)


def test_tz_aware_contributed_at_enforced() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        _contribution(contributed_at=datetime(2026, 4, 27, 12, 0))

    assert _contribution().contributed_at.tzinfo is not None


def test_cost_non_negative_enforced() -> None:
    with pytest.raises(ValidationError):
        _contribution(cost_usd=-0.01)


def test_schema_version_literal_red_rejection() -> None:
    # S2: v1 (legacy read) and v2 (per-node keying) are the closed set;
    # anything else red-rejects.
    payload = {
        "schema_version": "production-envelope.v3",
        "trial_id": UUID("12345678-1234-4234-8234-123456789abc"),
        "contributions": [],
    }

    with pytest.raises(ValidationError):
        ProductionEnvelope.model_validate(payload)


def test_add_contribution_same_node_retry_overwrites_with_attempt() -> None:
    # S2 (SCP 2026-06-11): the per-specialist append-only raise became
    # per-(specialist, node) retry-overwrite with attempt provenance —
    # never a duplicate append, never a silent skip (Murat regression shape).
    envelope = ProductionEnvelope(
        trial_id=UUID("12345678-1234-4234-8234-123456789abc")
    )
    contribution = _contribution()

    envelope.add_contribution(contribution)
    envelope.add_contribution(contribution)

    assert len(envelope.contributions) == 1
    assert envelope.contributions[0].attempt == 2


def test_contributions_cannot_be_appended_around_add_contribution() -> None:
    envelope = ProductionEnvelope(
        trial_id=UUID("12345678-1234-4234-8234-123456789abc")
    )

    with pytest.raises(AttributeError):
        envelope.contributions.append(_contribution())  # type: ignore[attr-defined]


def test_output_digest_is_canonical_json_and_fails_closed() -> None:
    assert compute_output_digest({"b": 1, "a": None}) == compute_output_digest(
        {"a": None, "b": 1}
    )
    assert compute_output_digest({"items": [1, 2]}) != compute_output_digest(
        {"items": [2, 1]}
    )
    assert compute_output_digest({"present": None}) != compute_output_digest({})

    with pytest.raises(ValueError):
        compute_output_digest({"not_json": float("nan")})

    with pytest.raises(TypeError):
        compute_output_digest({"not_json": object()})


def test_golden_fixture_and_json_schema_lockstep() -> None:
    envelope = ProductionEnvelope.model_validate_json(FIXTURE.read_text(encoding="utf-8"))
    schema_path = Path(__file__).resolve().parents[3] / "schema" / (
        "production_envelope.v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert envelope.schema_version == "production-envelope.v1"
    assert envelope.contributions[0].output_digest == compute_output_digest(
        envelope.contributions[0].output
    )
    assert schema == ProductionEnvelope.model_json_schema()
