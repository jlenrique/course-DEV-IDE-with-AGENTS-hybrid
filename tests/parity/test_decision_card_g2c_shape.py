from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g2c import G2CCard
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g2c.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g2c_golden.json"

CONTRACT_FIELDS = {
    "decision_card_digest",
    "meta",
    "schema_version",
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "created_at",
    "readiness_status",
    "blocking_issues",
    "ready_nodes",
    "verb",
}


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_g2c_lockstep_files_are_present() -> None:
    result = LOCKSTEP_CHECK("G2C", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g2c_card_has_required_fields() -> None:
    assert set(G2CCard.model_fields) >= CONTRACT_FIELDS
    assert G2CCard.model_fields["schema_version"].default == "v1"
    assert G2CCard.model_config["extra"] == "forbid"
    assert G2CCard.model_config["validate_assignment"] is True
    assert G2CCard.model_config["frozen"] is True


@pytest.mark.parametrize("gate_id", ["G1", "G3", 42])
def test_g2c_card_gate_id_closed_enum_red_rejection(gate_id: object) -> None:
    payload = _load_golden()
    payload["gate_id"] = gate_id

    with pytest.raises(ValidationError):
        G2CCard.model_validate(payload)


@pytest.mark.parametrize("gate_focus", ["trial_open", "motion_clip_approval", None])
def test_g2c_card_gate_focus_closed_enum_red_rejection(gate_focus: object) -> None:
    payload = _load_golden()
    payload["gate_focus"] = gate_focus

    with pytest.raises(ValidationError):
        G2CCard.model_validate(payload)


@pytest.mark.parametrize("schema_version", ["v0", "v2", None])
def test_g2c_card_schema_version_closed_enum_red_rejection(
    schema_version: object,
) -> None:
    payload = _load_golden()
    payload["schema_version"] = schema_version

    with pytest.raises(ValidationError):
        G2CCard.model_validate(payload)


@pytest.mark.parametrize("readiness_status", ["pending", "READY", None])
def test_g2c_card_readiness_status_closed_enum_red_rejection(
    readiness_status: object,
) -> None:
    payload = _load_golden()
    payload["readiness_status"] = readiness_status

    with pytest.raises(ValidationError):
        G2CCard.model_validate(payload)


def test_g2c_card_rejects_dropped_legacy_fields() -> None:
    payload = _load_golden()
    payload["drafted_proposal"] = {}
    payload["evidence"] = []
    payload["risks"] = []
    payload["meta"]["reject_rate"] = 0.0

    with pytest.raises(ValidationError):
        G2CCard.model_validate(payload)


def test_g2c_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == _canonical_json(
        G2CCard.model_json_schema()
    )


def test_g2c_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G2CCard.model_validate(payload)

    assert _canonical_json(card.model_dump(mode="json")) == GOLDEN_PATH.read_text(
        encoding="utf-8"
    )


def test_g2c_card_frozen_mutation_rejection() -> None:
    card = G2CCard.model_validate(_load_golden())

    with pytest.raises(ValidationError):
        card.gate_id = "G3"
