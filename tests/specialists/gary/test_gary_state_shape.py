from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.gary.state import GaryEnvelope, GaryReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "gary"


def test_gary_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = GaryEnvelope.model_validate(payload)
    assert model.specialist_id == "gary"
    assert GaryEnvelope._SPECIALIST_ID == "gary"


def test_gary_return_shape_supports_gary_slide_output() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = GaryReturn.model_validate(payload)
    assert model.specialist_id == "gary"
    assert model.gary_slide_output is not None
    assert len(model.gary_slide_output) == 2


def test_gary_return_default_gary_slide_output_is_none() -> None:
    model = GaryReturn(
        specialist_id="gary",
        verb="proceed",
        payload={"generation_id": "gen-default"},
    )
    assert model.gary_slide_output is None


def test_gary_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = GaryReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = GaryReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_gary_return_rejects_invalid_slide_output_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["gary_slide_output"] = "not-a-list"
    with pytest.raises(ValidationError):
        GaryReturn.model_validate(payload)
