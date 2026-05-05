from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g6 import G6Card
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g6.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g6_golden.json"

CONTRACT_FIELDS = {
    "decision_card_digest",
    "meta",
    "schema_version",
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "created_at",
    "slab_id",
    "closing_run_id",
    "retrospective_path",
    "closing_artifact_paths",
    "slab_close_summary",
    "verb",
}


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _schema_bytes() -> bytes:
    return (
        json.dumps(G6Card.model_json_schema(), indent=2, sort_keys=True)
        + "\n"
    ).encode("utf-8")


def test_g6_four_file_lockstep_is_satisfied() -> None:
    result = LOCKSTEP_CHECK("G6", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g6_card_has_required_fields() -> None:
    assert set(G6Card.model_fields) >= CONTRACT_FIELDS
    assert G6Card.model_fields["schema_version"].default == "v1"
    assert G6Card.model_config["extra"] == "forbid"
    assert G6Card.model_config["validate_assignment"] is True
    assert G6Card.model_config["frozen"] is True


@pytest.mark.parametrize("gate_id", ["G5", "G99", 42])
def test_g6_card_gate_id_closed_enum_red_rejection(gate_id: object) -> None:
    payload = _load_golden()
    payload["gate_id"] = gate_id

    with pytest.raises(ValidationError):
        G6Card.model_validate(payload)


@pytest.mark.parametrize("gate_focus", ["final_operator_handoff", "trial_open", None])
def test_g6_card_gate_focus_closed_enum_red_rejection(gate_focus: object) -> None:
    payload = _load_golden()
    payload["gate_focus"] = gate_focus

    with pytest.raises(ValidationError):
        G6Card.model_validate(payload)


def test_g6_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_bytes() == _schema_bytes()


def test_g6_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G6Card.model_validate(payload)

    dumped = json.loads(card.model_dump_json(by_alias=True))

    assert _canonical(dumped) == _canonical(payload)


def test_g6_card_rejects_empty_required_closure_fields() -> None:
    payload = _load_golden()
    payload["closing_artifact_paths"] = []
    with pytest.raises(ValidationError, match="closing_artifact_paths"):
        G6Card.model_validate(payload)

    payload = _load_golden()
    payload["slab_close_summary"] = ""
    with pytest.raises(ValidationError, match="slab_close_summary"):
        G6Card.model_validate(payload)

    payload = _load_golden()
    payload["slab_close_summary"] = " \t "
    with pytest.raises(ValidationError, match="slab_close_summary"):
        G6Card.model_validate(payload)


@pytest.mark.parametrize("slab_id", ["7", "7c", "12", "12b", "5a"])
def test_g6_card_accepts_valid_slab_id_pattern(slab_id: str) -> None:
    payload = _load_golden()
    payload["slab_id"] = slab_id

    assert G6Card.model_validate(payload).slab_id == slab_id


@pytest.mark.parametrize("slab_id", ["", "slab-7c", "7C", "7-c", "7cd", "7ab"])
def test_g6_card_rejects_invalid_slab_id_pattern(slab_id: str) -> None:
    payload = _load_golden()
    payload["slab_id"] = slab_id

    with pytest.raises(ValidationError, match="slab_id"):
        G6Card.model_validate(payload)


def test_g6_card_frozen_mutation_rejection() -> None:
    card = G6Card.model_validate(_load_golden())

    with pytest.raises(ValidationError):
        card.gate_id = "G5"  # type: ignore[misc]
