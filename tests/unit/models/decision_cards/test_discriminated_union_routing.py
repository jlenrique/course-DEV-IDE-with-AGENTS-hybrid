from __future__ import annotations

import pytest

from app.models.decision_cards import AnyDecisionCardAdapter, G1Card, G2CCard, G3Card, G4Card
from tests.unit.models.decision_cards._helpers import GATE_MODELS, load_fixture


@pytest.mark.parametrize(
    ("fixture_name", "expected_type"),
    [(name, model_class) for name, model_class in GATE_MODELS],
    ids=[name for name, _ in GATE_MODELS],
)
def test_any_decision_card_routes_to_expected_subclass(
    fixture_name: str,
    expected_type: type[G1Card | G2CCard | G3Card | G4Card],
) -> None:
    payload = load_fixture(fixture_name)
    parsed = AnyDecisionCardAdapter.validate_python(payload)
    assert isinstance(parsed, expected_type)
