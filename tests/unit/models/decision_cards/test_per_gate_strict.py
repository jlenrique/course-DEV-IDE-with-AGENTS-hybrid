from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.decision_cards import G1Card, G2CCard, G3Card, G4Card
from tests.unit.models.decision_cards._helpers import GATE_MODELS, load_fixture

_GATE_IDS = [name for name, _ in GATE_MODELS]


@pytest.mark.parametrize(("fixture_name", "model_class"), GATE_MODELS, ids=_GATE_IDS)
def test_gate_subclass_model_config_is_strict(
    fixture_name: str,
    model_class: type[G1Card | G2CCard | G3Card | G4Card],
) -> None:
    del fixture_name
    assert model_class.model_config["extra"] == "forbid"
    assert model_class.model_config["validate_assignment"] is True


@pytest.mark.parametrize(("fixture_name", "model_class"), GATE_MODELS, ids=_GATE_IDS)
def test_gate_subclass_rejects_naive_created_at(
    fixture_name: str,
    model_class: type[G1Card | G2CCard | G3Card | G4Card],
) -> None:
    payload = load_fixture(fixture_name)
    payload["created_at"] = datetime(2026, 4, 26, 12, 0, 0).isoformat()
    with pytest.raises(ValidationError, match="timezone-aware"):
        model_class.model_validate(payload)


@pytest.mark.parametrize(("fixture_name", "model_class"), GATE_MODELS, ids=_GATE_IDS)
def test_gate_subclass_rejects_invalid_gate_id(
    fixture_name: str,
    model_class: type[G1Card | G2CCard | G3Card | G4Card],
) -> None:
    payload = load_fixture(fixture_name)
    payload["gate_id"] = "G999"
    with pytest.raises(ValidationError):
        model_class.model_validate(payload)


@pytest.mark.parametrize(("fixture_name", "model_class"), GATE_MODELS, ids=_GATE_IDS)
def test_gate_subclass_rejects_invalid_verb(
    fixture_name: str,
    model_class: type[G1Card | G2CCard | G3Card | G4Card],
) -> None:
    payload = load_fixture(fixture_name)
    payload["verb"] = "timeout"
    with pytest.raises(ValidationError):
        model_class.model_validate(payload)
