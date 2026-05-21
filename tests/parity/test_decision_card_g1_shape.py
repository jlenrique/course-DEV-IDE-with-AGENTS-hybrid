from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g1 import G1Card
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g1.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g1_golden.json"

CONTRACT_FIELDS = {
    "decision_card_digest",
    "meta",
    "schema_version",
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "created_at",
    "drafted_proposal",
    "evidence",
    "trial_summary",
    "opened_by",
    "next_nodes",
    "verb",
}


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_g1_lockstep_files_are_present() -> None:
    result = LOCKSTEP_CHECK("G1", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g1_card_has_required_fields() -> None:
    assert set(G1Card.model_fields) >= CONTRACT_FIELDS
    assert G1Card.model_fields["schema_version"].default == "v1"
    assert G1Card.model_config["extra"] == "forbid"
    assert G1Card.model_config["validate_assignment"] is True
    assert G1Card.model_config["frozen"] is True


@pytest.mark.parametrize("gate_id", ["G0", "G99", 42])
def test_g1_card_gate_id_closed_enum_red_rejection(gate_id: object) -> None:
    payload = _load_golden()
    payload["gate_id"] = gate_id

    with pytest.raises(ValidationError):
        G1Card.model_validate(payload)


@pytest.mark.parametrize("gate_focus", ["directive_ratification", "trial_close", None])
def test_g1_card_gate_focus_closed_enum_red_rejection(gate_focus: object) -> None:
    payload = _load_golden()
    payload["gate_focus"] = gate_focus

    with pytest.raises(ValidationError):
        G1Card.model_validate(payload)


@pytest.mark.parametrize("schema_version", ["v0", "v2", None])
def test_g1_card_schema_version_closed_enum_red_rejection(
    schema_version: object,
) -> None:
    payload = _load_golden()
    payload["schema_version"] = schema_version

    with pytest.raises(ValidationError):
        G1Card.model_validate(payload)


def test_g1_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == _canonical_json(
        G1Card.model_json_schema()
    )


def test_g1_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G1Card.model_validate(payload)

    assert _canonical_json(card.model_dump(mode="json")) == GOLDEN_PATH.read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize("trial_summary", ["", "   "])
def test_g1_card_rejects_empty_trial_summary(trial_summary: str) -> None:
    payload = _load_golden()
    payload["trial_summary"] = trial_summary

    with pytest.raises(ValidationError, match="trial_summary"):
        G1Card.model_validate(payload)


@pytest.mark.parametrize("opened_by", ["", "   "])
def test_g1_card_rejects_empty_opened_by(opened_by: str) -> None:
    payload = _load_golden()
    payload["opened_by"] = opened_by

    with pytest.raises(ValidationError, match="opened_by"):
        G1Card.model_validate(payload)


def test_g1_card_frozen_mutation_rejection() -> None:
    card = G1Card.model_validate(_load_golden())

    with pytest.raises(ValidationError):
        card.gate_id = "G2C"
