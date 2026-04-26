"""State-shape pins for generated specialist vera."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.vera.state import VeraEnvelope, VeraReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "vera"


def test_vera_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = VeraEnvelope.model_validate(payload)
    assert model.specialist_id == "vera"
    assert VeraEnvelope._SPECIALIST_ID == "vera"
    assert VeraReturn._SPECIALIST_ID == "vera"


def test_vera_return_shape_supports_vera_finding() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = VeraReturn.model_validate(payload)
    assert model.vera_finding is not None
    assert model.vera_finding["status"] == "pass"


def test_vera_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = VeraReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = VeraReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_vera_return_rejects_invalid_vera_finding_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["vera_finding"] = "oops"
    with pytest.raises(ValidationError):
        VeraReturn.model_validate(payload)
