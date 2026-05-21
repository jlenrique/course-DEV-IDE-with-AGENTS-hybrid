"""State-shape pins for generated specialist irene."""

from __future__ import annotations

import json
from pathlib import Path

from app.specialists.irene.state import IreneEnvelope, IreneReturn

FIXTURE_ROOT = Path("tests") / "fixtures" / "specialists" / "irene"


def test_irene_envelope_and_return_subclass_bases() -> None:
    assert IreneEnvelope._SPECIALIST_ID == "irene"
    assert IreneReturn._SPECIALIST_ID == "irene"


def test_irene_golden_envelope_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_envelope.json").read_text(encoding="utf-8"))
    model = IreneEnvelope.model_validate(payload)
    assert model.specialist_id == "irene"


def test_irene_golden_return_round_trip() -> None:
    payload = json.loads((FIXTURE_ROOT / "golden_return.json").read_text(encoding="utf-8"))
    model = IreneReturn.model_validate(payload)
    assert model.specialist_id == "irene"


def test_irene_return_includes_pass_fields() -> None:
    model = IreneReturn(
        specialist_id="irene",
        verb="proceed",
        payload={},
        irene_lesson_design={"learning_objectives": []},
        irene_pass_2_envelope={"narration_script": []},
        timestamp="2026-04-24T00:00:01Z",
    )
    assert model.irene_lesson_design == {"learning_objectives": []}
    assert model.irene_pass_2_envelope == {"narration_script": []}
