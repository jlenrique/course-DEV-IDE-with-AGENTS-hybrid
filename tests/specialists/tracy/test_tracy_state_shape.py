"""State-shape pins for generated specialist tracy."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.tracy.state import TracyEnvelope, TracyReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "tracy"


def test_tracy_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = TracyEnvelope.model_validate(payload)
    assert model.specialist_id == "tracy"
    assert TracyEnvelope._SPECIALIST_ID == "tracy"
    assert TracyReturn._SPECIALIST_ID == "tracy"


def test_tracy_return_shape_supports_manifest_payload() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = TracyReturn.model_validate(payload)
    assert model.tracy_manifest is not None
    assert model.tracy_manifest["results"][0]["intent_class"] == "supporting_evidence"


def test_tracy_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = TracyReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = TracyReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_tracy_return_rejects_invalid_manifest_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["tracy_manifest"] = "oops"
    with pytest.raises(ValidationError):
        TracyReturn.model_validate(payload)
