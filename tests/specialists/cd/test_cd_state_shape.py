"""State-shape pins for generated specialist cd."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.specialists.cd.state import CdEnvelope, CdReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "cd"


def test_cd_envelope_shape_and_payload_cap() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = CdEnvelope.model_validate(payload)
    assert model.specialist_id == "cd"
    assert CdEnvelope._SPECIALIST_ID == "cd"
    assert CdReturn._SPECIALIST_ID == "cd"


def test_cd_return_shape_supports_cd_directive() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = CdReturn.model_validate(payload)
    assert model.cd_directive is not None
    assert model.cd_directive["schema_version"] == "1.0"


def test_cd_return_round_trip_is_deterministic() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = CdReturn.model_validate(payload)
    dumped = model.model_dump(mode="json")
    reloaded = CdReturn.model_validate(dumped)
    assert reloaded.model_dump(mode="json") == dumped


def test_cd_return_rejects_invalid_cd_directive_type() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    payload["cd_directive"] = "oops"
    with pytest.raises(ValidationError):
        CdReturn.model_validate(payload)
