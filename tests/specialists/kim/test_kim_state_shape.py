"""State-shape pins for generated specialist kim."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.kim.state import KimEnvelope, KimReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "kim"


def test_kim_envelope_and_return_subclass_bases() -> None:
    assert KimEnvelope._SPECIALIST_ID == "kim"
    assert KimReturn._SPECIALIST_ID == "kim"


def test_kim_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = KimEnvelope.model_validate(payload)
    assert model.specialist_id == "kim"


def test_kim_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = KimReturn.model_validate(payload)
    assert model.specialist_id == "kim"
    assert model.kim_coursearc is not None
