"""State-shape pins for generated specialist kira."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.kira.state import KiraEnvelope, KiraReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "kira"


def test_kira_envelope_and_return_subclass_bases() -> None:
    assert KiraEnvelope._SPECIALIST_ID == "kira"
    assert KiraReturn._SPECIALIST_ID == "kira"


def test_kira_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = KiraEnvelope.model_validate(payload)
    assert model.specialist_id == "kira"


def test_kira_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = KiraReturn.model_validate(payload)
    assert model.specialist_id == "kira"
    assert model.motion_asset_path is not None
    assert model.motion_asset_path.endswith(".mp4")
