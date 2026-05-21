"""State-shape pins for generated specialist wanda."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.wanda.state import WandaEnvelope, WandaReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "wanda"


def test_wanda_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = WandaEnvelope.model_validate(payload)
    assert model.specialist_id == "wanda"
    assert WandaEnvelope._SPECIALIST_ID == "wanda"
    assert WandaReturn._SPECIALIST_ID == "wanda"


def test_wanda_return_shape_supports_wanda_audio() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = WandaReturn.model_validate(payload)
    assert model.wanda_audio is not None
    assert model.wanda_audio["capability"] == "CM"


def test_wanda_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = WandaReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = WandaReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_wanda_return_rejects_invalid_wanda_audio_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["wanda_audio"] = "oops"
    with pytest.raises(ValidationError):
        WandaReturn.model_validate(payload)
