from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g5 import G5Card
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g5.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g5_golden.json"

CONTRACT_FIELDS = {
    "decision_card_digest",
    "meta",
    "schema_version",
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "created_at",
    "bundle_run_id",
    "handoff_artifact_paths",
    "handoff_summary",
    "verb",
}


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_g5_lockstep_files_are_present() -> None:
    result = LOCKSTEP_CHECK("G5", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g5_card_has_required_fields() -> None:
    assert set(G5Card.model_fields) >= CONTRACT_FIELDS
    assert G5Card.model_config["extra"] == "forbid"
    assert G5Card.model_config["validate_assignment"] is True
    assert G5Card.model_config["frozen"] is True


@pytest.mark.parametrize("gate_id", ["G0", "G99", 42])
def test_g5_card_gate_id_closed_enum_red_rejection(gate_id: object) -> None:
    payload = _load_golden()
    payload["gate_id"] = gate_id

    with pytest.raises(ValidationError):
        G5Card.model_validate(payload)


@pytest.mark.parametrize("gate_focus", ["slab_close_ceremony", "trial_open", None])
def test_g5_card_gate_focus_closed_enum_red_rejection(gate_focus: object) -> None:
    payload = _load_golden()
    payload["gate_focus"] = gate_focus

    with pytest.raises(ValidationError):
        G5Card.model_validate(payload)


def test_g5_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == _canonical_json(
        G5Card.model_json_schema()
    )


def test_g5_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G5Card.model_validate(payload)

    assert _canonical_json(card.model_dump(mode="json")) == GOLDEN_PATH.read_text(
        encoding="utf-8"
    )


def test_g5_card_rejects_empty_handoff_artifact_paths() -> None:
    payload = _load_golden()
    payload["handoff_artifact_paths"] = []

    with pytest.raises(ValidationError, match="handoff_artifact_paths"):
        G5Card.model_validate(payload)


@pytest.mark.parametrize("handoff_summary", ["", "   "])
def test_g5_card_rejects_empty_handoff_summary(handoff_summary: str) -> None:
    payload = _load_golden()
    payload["handoff_summary"] = handoff_summary

    with pytest.raises(ValidationError, match="handoff_summary"):
        G5Card.model_validate(payload)


def test_g5_card_frozen_mutation_rejection() -> None:
    card = G5Card.model_validate(_load_golden())

    with pytest.raises(ValidationError):
        card.gate_id = "G6"
