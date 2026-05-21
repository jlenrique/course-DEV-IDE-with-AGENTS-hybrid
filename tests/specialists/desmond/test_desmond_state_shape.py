"""State-shape pins for generated specialist desmond."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.desmond.state import DesmondEnvelope, DesmondReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "desmond"


def test_desmond_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = DesmondEnvelope.model_validate(payload)
    assert model.specialist_id == "desmond"
    assert DesmondEnvelope._SPECIALIST_ID == "desmond"
    assert DesmondReturn._SPECIALIST_ID == "desmond"


def test_desmond_return_shape_supports_handoff_payload() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = DesmondReturn.model_validate(payload)
    assert model.desmond_handoff is not None
    assert "## Automation Advisory" in model.desmond_handoff["handoff_text"]


def test_desmond_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = DesmondReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = DesmondReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_desmond_return_rejects_invalid_handoff_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["desmond_handoff"] = "oops"
    with pytest.raises(ValidationError):
        DesmondReturn.model_validate(payload)
