from __future__ import annotations

import hashlib
import json

import pytest
from pydantic import ValidationError

from app.marcus.orchestrator.writers.diagram_cards import (
    DiagramCard,
    GaryDiagramCards,
    emit_gary_diagram_cards,
)

SCHEMA_HASH = "36643d7e389681f109eb78bfe511533f5f5e71e3e3d7c71746dc486f290da6cc"


def _payload() -> GaryDiagramCards:
    return GaryDiagramCards(
        plan_unit_id="unit-07",
        target_section="section-07",
        cards=[
            DiagramCard(
                slide_index=1,
                visual_kind="flowchart",
                specification="Show the operator gate sequence from intake to approval.",
                caption="Gate sequence",
            )
        ],
    )


def test_diagram_cards_round_trips_and_emits_lf_only_json(tmp_path):
    payload = GaryDiagramCards.model_validate(_payload().model_dump(mode="json"))
    output_path = emit_gary_diagram_cards(payload, tmp_path / "gary-diagram-cards.json")

    expected = json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
    raw = output_path.read_bytes()
    assert raw == expected.encode("utf-8")
    assert b"\r\n" not in raw


def test_diagram_visual_kind_rejects_unknown_value():
    data = _payload().model_dump(mode="json")
    data["cards"][0]["visual_kind"] = "wireframe"

    with pytest.raises(ValidationError):
        GaryDiagramCards.model_validate(data)


def test_diagram_cards_rejects_blank_plan_unit_id():
    data = _payload().model_dump(mode="json")
    data["plan_unit_id"] = "   "

    with pytest.raises(ValidationError):
        GaryDiagramCards.model_validate(data)


def test_diagram_cards_schema_hash_is_stable():
    schema = json.dumps(GaryDiagramCards.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH
