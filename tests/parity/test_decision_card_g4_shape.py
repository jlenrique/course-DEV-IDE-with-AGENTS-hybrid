from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g4 import G4Card
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g4.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g4_golden.json"

CONTRACT_FIELDS = {
    "decision_card_digest",
    "meta",
    "schema_version",
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "created_at",
    "final_status",
    "artifact_paths",
    "outcome_summary",
    "verb",
}


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_g4_lockstep_files_are_present() -> None:
    result = LOCKSTEP_CHECK("G4", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g4_card_has_required_fields() -> None:
    assert set(G4Card.model_fields) >= CONTRACT_FIELDS
    assert G4Card.model_fields["schema_version"].default == "v1"
    assert G4Card.model_config["extra"] == "forbid"
    assert G4Card.model_config["validate_assignment"] is True
    assert G4Card.model_config["frozen"] is True


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("gate_id", "G3"),
        ("gate_focus", "motion_clip_approval"),
        ("schema_version", "v2"),
    ],
)
def test_g4_card_closed_enums_red_rejection(field_name: str, bad_value: object) -> None:
    payload = _load_golden()
    payload[field_name] = bad_value

    with pytest.raises(ValidationError):
        G4Card.model_validate(payload)


@pytest.mark.parametrize("final_status", ["in_progress", "unknown", "COMPLETED", 1])
def test_g4_card_final_status_closed_enum_red_rejection(final_status: object) -> None:
    payload = _load_golden()
    payload["final_status"] = final_status

    with pytest.raises(ValidationError):
        G4Card.model_validate(payload)


def test_g4_card_accepts_empty_artifact_paths_default() -> None:
    payload = _load_golden()
    del payload["artifact_paths"]

    card = G4Card.model_validate(payload)

    assert card.artifact_paths == []


@pytest.mark.parametrize("outcome_summary", ["", "   "])
def test_g4_card_rejects_empty_outcome_summary(outcome_summary: str) -> None:
    payload = _load_golden()
    payload["outcome_summary"] = outcome_summary

    with pytest.raises(ValidationError, match="outcome_summary"):
        G4Card.model_validate(payload)


def test_g4_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == _canonical_json(
        G4Card.model_json_schema()
    )


def test_g4_json_schema_declares_closed_values() -> None:
    schema = G4Card.model_json_schema()

    assert schema["properties"]["schema_version"]["const"] == "v1"
    assert schema["properties"]["gate_id"]["const"] == "G4"
    assert schema["properties"]["gate_focus"]["const"] == "fidelity_gate"
    assert schema["properties"]["final_status"]["enum"] == ["completed", "partial", "failed"]
    assert schema["additionalProperties"] is False


def test_g4_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G4Card.model_validate(payload)

    assert _canonical_json(card.model_dump(mode="json")) == GOLDEN_PATH.read_text(
        encoding="utf-8"
    )


def test_g4_card_frozen_mutation_rejection() -> None:
    card = G4Card.model_validate(_load_golden())

    with pytest.raises(ValidationError):
        card.gate_id = "G3"
