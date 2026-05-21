"""State-shape pins for generated specialist tamara."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.tamara.state import TamaraEnvelope, TamaraReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "tamara"


def test_tamara_envelope_and_return_subclass_bases() -> None:
    assert TamaraEnvelope._SPECIALIST_ID == "tamara"
    assert TamaraReturn._SPECIALIST_ID == "tamara"


def test_tamara_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = TamaraEnvelope.model_validate(payload)
    assert model.specialist_id == "tamara"


def test_tamara_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = TamaraReturn.model_validate(payload)
    assert model.specialist_id == "tamara"
    assert model.tamara_design_spec is not None
