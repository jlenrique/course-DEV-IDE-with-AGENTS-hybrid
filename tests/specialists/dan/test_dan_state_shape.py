"""State-shape pins for generated specialist dan."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.dan.state import DanEnvelope, DanReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "dan"


def test_dan_envelope_and_return_subclass_bases() -> None:
    assert DanEnvelope._SPECIALIST_ID == "dan"
    assert DanReturn._SPECIALIST_ID == "dan"


def test_dan_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = DanEnvelope.model_validate(payload)
    assert model.specialist_id == "dan"


def test_dan_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = DanReturn.model_validate(payload)
    assert model.specialist_id == "dan"
