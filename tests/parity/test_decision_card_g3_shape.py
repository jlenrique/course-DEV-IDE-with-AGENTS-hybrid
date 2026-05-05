from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g3 import G3Card
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g3.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g3_golden.json"

CONTRACT_FIELDS = {
    "decision_card_digest",
    "meta",
    "schema_version",
    "card_id",
    "trial_id",
    "gate_id",
    "gate_focus",
    "created_at",
    "progress_percent",
    "active_node_id",
    "pending_nodes",
    "operator_prompt",
    "verb",
}


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_g3_lockstep_files_are_present() -> None:
    result = LOCKSTEP_CHECK("G3", repo_root=REPO_ROOT)

    assert result.failure_reason is None
    assert result.files_present == {
        "golden_fixture": True,
        "model": True,
        "schema": True,
        "shape_pin": True,
    }


def test_g3_card_has_required_fields() -> None:
    assert set(G3Card.model_fields) >= CONTRACT_FIELDS
    assert G3Card.model_fields["schema_version"].default == "v1"
    assert G3Card.model_config["extra"] == "forbid"
    assert G3Card.model_config["validate_assignment"] is True
    assert G3Card.model_config["frozen"] is True


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("gate_id", "G2C"),
        ("gate_focus", "pre_composition_qa"),
        ("schema_version", "v2"),
    ],
)
def test_g3_card_closed_enums_red_rejection(field_name: str, bad_value: object) -> None:
    payload = _load_golden()
    payload[field_name] = bad_value

    with pytest.raises(ValidationError):
        G3Card.model_validate(payload)


@pytest.mark.parametrize("progress_percent", [0.0, 100.0])
def test_g3_card_accepts_progress_percent_boundaries(progress_percent: float) -> None:
    payload = _load_golden()
    payload["progress_percent"] = progress_percent

    card = G3Card.model_validate(payload)

    assert card.progress_percent == progress_percent


@pytest.mark.parametrize("progress_percent", [-0.1, 100.1])
def test_g3_card_rejects_progress_percent_out_of_bounds(progress_percent: float) -> None:
    payload = _load_golden()
    payload["progress_percent"] = progress_percent

    with pytest.raises(ValidationError, match="progress_percent"):
        G3Card.model_validate(payload)


@pytest.mark.parametrize("active_node_id", ["", "   "])
def test_g3_card_rejects_empty_active_node_id(active_node_id: str) -> None:
    payload = _load_golden()
    payload["active_node_id"] = active_node_id

    with pytest.raises(ValidationError, match="active_node_id"):
        G3Card.model_validate(payload)


@pytest.mark.parametrize("operator_prompt", ["", "   "])
def test_g3_card_rejects_empty_operator_prompt(operator_prompt: str) -> None:
    payload = _load_golden()
    payload["operator_prompt"] = operator_prompt

    with pytest.raises(ValidationError, match="operator_prompt"):
        G3Card.model_validate(payload)


def test_g3_json_schema_byte_for_byte_match() -> None:
    assert SCHEMA_PATH.read_text(encoding="utf-8") == _canonical_json(
        G3Card.model_json_schema()
    )


def test_g3_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G3Card.model_validate(payload)

    assert _canonical_json(card.model_dump(mode="json")) == GOLDEN_PATH.read_text(
        encoding="utf-8"
    )


def test_g3_card_frozen_mutation_rejection() -> None:
    card = G3Card.model_validate(_load_golden())

    with pytest.raises(ValidationError):
        card.gate_id = "G4"
