from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g2a import G2ACard
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g2a.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g2a_golden.json"

CONTRACT_FIELDS = {
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "plan_unit_id",
    "plan_unit_summary",
    "ratification_evidence",
    "prior_unit_ids",
    "verb",
    "meta",
}


def _schema_bytes() -> bytes:
    return (
        json.dumps(G2ACard.model_json_schema(), indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def test_g2a_four_file_lockstep_is_satisfied() -> None:
    result = LOCKSTEP_CHECK("G2A", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g2a_card_has_required_contract_fields() -> None:
    assert set(G2ACard.model_fields) >= CONTRACT_FIELDS
    assert G2ACard.model_fields["schema_version"].default == "v1"
    assert G2ACard.model_config["extra"] == "forbid"
    assert G2ACard.model_config["validate_assignment"] is True
    assert G2ACard.model_config["frozen"] is True


@pytest.mark.parametrize("bad_gate_id", ["G1", "G99", 42])
def test_g2a_card_gate_id_closed_enum_red_rejection(bad_gate_id: object) -> None:
    payload = _load_golden()
    payload["gate_id"] = bad_gate_id

    with pytest.raises(ValidationError):
        G2ACard.model_validate(payload)


@pytest.mark.parametrize("bad_gate_focus", ["directive_ratification", None])
def test_g2a_card_gate_focus_closed_enum_red_rejection(
    bad_gate_focus: object,
) -> None:
    payload = _load_golden()
    payload["gate_focus"] = bad_gate_focus

    with pytest.raises(ValidationError):
        G2ACard.model_validate(payload)


def test_g2a_card_rejects_empty_required_plan_fields() -> None:
    payload = _load_golden()
    payload["plan_unit_summary"] = " "
    with pytest.raises(ValidationError, match="plan_unit_summary"):
        G2ACard.model_validate(payload)

    payload = _load_golden()
    payload["ratification_evidence"] = []
    with pytest.raises(ValidationError, match="ratification_evidence"):
        G2ACard.model_validate(payload)


def test_g2a_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_bytes() == _schema_bytes()


def test_g2a_json_schema_declares_version_and_closed_focus() -> None:
    schema = G2ACard.model_json_schema()
    assert schema["properties"]["schema_version"]["const"] == "v1"
    assert schema["properties"]["gate_id"]["const"] == "G2A"
    assert schema["properties"]["gate_focus"]["const"] == "plan_unit_ratification"
    assert schema["additionalProperties"] is False


def test_g2a_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G2ACard.model_validate(payload)

    assert _canonical(card.model_dump(mode="json")) == _canonical(payload)
