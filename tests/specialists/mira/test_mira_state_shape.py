"""State-shape pins for generated specialist mira."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.mira.state import MiraEnvelope, MiraReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "mira"


def test_mira_envelope_and_return_subclass_bases() -> None:
    assert MiraEnvelope._SPECIALIST_ID == "mira"
    assert MiraReturn._SPECIALIST_ID == "mira"


def test_mira_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = MiraEnvelope.model_validate(payload)
    assert model.specialist_id == "mira"


def test_mira_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = MiraReturn.model_validate(payload)
    assert model.specialist_id == "mira"
    assert model.mira_prompt_pack is not None
