"""State-shape pins for generated specialist enrique."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.enrique.state import EnriqueEnvelope, EnriqueReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "enrique"


def test_enrique_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = EnriqueEnvelope.model_validate(payload)
    assert model.specialist_id == "enrique"
    assert EnriqueEnvelope._SPECIALIST_ID == "enrique"
    assert EnriqueReturn._SPECIALIST_ID == "enrique"


def test_enrique_return_shape_supports_audio_receipt() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = EnriqueReturn.model_validate(payload)
    assert model.enrique_audio is not None
    assert model.enrique_audio["mode"] == "voice-preview"


def test_enrique_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = EnriqueReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = EnriqueReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_enrique_return_rejects_invalid_enrique_audio_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["enrique_audio"] = "oops"
    with pytest.raises(ValidationError):
        EnriqueReturn.model_validate(payload)
