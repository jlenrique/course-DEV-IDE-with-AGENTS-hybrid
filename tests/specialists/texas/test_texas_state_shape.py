"""State-shape pins for generated specialist texas."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.texas.state import TexasEnvelope, TexasReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "texas"


def test_texas_envelope_and_return_subclass_bases() -> None:
    assert TexasEnvelope._SPECIALIST_ID == "texas"
    assert TexasReturn._SPECIALIST_ID == "texas"


def test_texas_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = TexasEnvelope.model_validate(payload)
    assert model.specialist_id == "texas"


def test_texas_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = TexasReturn.model_validate(payload)
    assert model.specialist_id == "texas"
    assert model.bundle_reference is not None
    assert "fixture_bundle" in model.bundle_reference
