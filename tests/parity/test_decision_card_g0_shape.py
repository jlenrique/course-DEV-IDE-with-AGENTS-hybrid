from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.decision_cards.g0 import G0Card
from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app" / "models" / "decision_cards" / "schema" / "g0.v1.schema.json"
GOLDEN_PATH = REPO_ROOT / "tests" / "fixtures" / "decision_cards" / "g0_golden.json"


def _load_golden() -> dict[str, Any]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def test_g0_card_has_required_fields() -> None:
    expected = {
        "card_id",
        "trial_id",
        "gate_id",
        "gate_focus",
        "corpus_paths_confirmed",
        "directive_run_id",
        "corpus_confirmation_summary",
        "verb",
        "meta",
    }

    assert expected <= set(G0Card.model_fields)


@pytest.mark.parametrize("gate_id", ["G1", "G99", 42])
def test_g0_card_gate_id_closed_enum_red_rejection(gate_id: object) -> None:
    payload = _load_golden()
    payload["gate_id"] = gate_id

    with pytest.raises(ValidationError):
        G0Card.model_validate(payload)


@pytest.mark.parametrize("gate_focus", ["directive_ratification", None])
def test_g0_card_gate_focus_closed_enum_red_rejection(gate_focus: object) -> None:
    payload = _load_golden()
    payload["gate_focus"] = gate_focus

    with pytest.raises(ValidationError):
        G0Card.model_validate(payload)


def test_g0_card_rejects_empty_corpus_path_list() -> None:
    payload = _load_golden()
    payload["corpus_paths_confirmed"] = []

    with pytest.raises(ValidationError, match="corpus_paths_confirmed"):
        G0Card.model_validate(payload)


def test_g0_json_schema_byte_for_byte_match() -> None:
    expected = _canonical_json(G0Card.model_json_schema())

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected


def test_g0_golden_fixture_round_trips() -> None:
    payload = _load_golden()
    card = G0Card.model_validate(payload)

    assert _canonical_json(card.model_dump(mode="json")) == GOLDEN_PATH.read_text(
        encoding="utf-8"
    )


def test_g0_shape_pin_cites_lockstep_check_by_reference() -> None:
    lockstep = LOCKSTEP_CHECK("G0", repo_root=REPO_ROOT)

    assert set(lockstep.files_present) == {
        "golden_fixture",
        "model",
        "schema",
        "shape_pin",
    }
    assert all(lockstep.files_present.values())
