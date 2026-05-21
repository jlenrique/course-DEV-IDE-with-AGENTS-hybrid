"""State-shape pins for generated specialist aria."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.aria.state import AriaEnvelope, AriaReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "aria"


def test_aria_envelope_and_return_subclass_bases() -> None:
    assert AriaEnvelope._SPECIALIST_ID == "aria"
    assert AriaReturn._SPECIALIST_ID == "aria"


def test_aria_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = AriaEnvelope.model_validate(payload)
    assert model.specialist_id == "aria"


def test_aria_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = AriaReturn.model_validate(payload)
    assert model.specialist_id == "aria"
    assert model.aria_build_spec is not None
