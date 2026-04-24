from __future__ import annotations

import json
from pathlib import Path

from app.specialists._scaffold.state import ScaffoldEnvelope, ScaffoldReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "_scaffold"


def test_scaffold_state_classvar_pins() -> None:
    assert ScaffoldEnvelope._SPECIALIST_ID == "_scaffold"
    assert ScaffoldReturn._SPECIALIST_ID == "_scaffold"


def test_scaffold_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = ScaffoldEnvelope.model_validate(payload)
    assert model.specialist_id == "_scaffold"


def test_scaffold_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = ScaffoldReturn.model_validate(payload)
    assert model.specialist_id == "_scaffold"
