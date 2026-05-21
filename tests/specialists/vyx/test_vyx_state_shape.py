"""State-shape pins for generated specialist vyx."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.vyx.state import VyxEnvelope, VyxReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "vyx"


def test_vyx_envelope_and_return_subclass_bases() -> None:
    assert VyxEnvelope._SPECIALIST_ID == "vyx"
    assert VyxReturn._SPECIALIST_ID == "vyx"


def test_vyx_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = VyxEnvelope.model_validate(payload)
    assert model.specialist_id == "vyx"


def test_vyx_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = VyxReturn.model_validate(payload)
    assert model.specialist_id == "vyx"
    assert model.vyx_storyboard is not None
