from __future__ import annotations

import pytest

from tests.unit.models.decision_cards._helpers import (
    GATE_MODELS,
    schema_hash_for_file,
    schema_hash_for_model,
)

_SCHEMA_FILES = {
    "g1": "g1.v1.schema.json",
    "g2c": "g2c.v1.schema.json",
    "g3": "g3.v1.schema.json",
    "g4": "g4.v1.schema.json",
}
_GATE_IDS = [name for name, _ in GATE_MODELS]


@pytest.mark.parametrize(("fixture_name", "model_class"), GATE_MODELS, ids=_GATE_IDS)
def test_per_gate_schema_hash_matches_pinned_file(
    fixture_name: str,
    model_class: type,
) -> None:
    assert schema_hash_for_model(model_class) == schema_hash_for_file(_SCHEMA_FILES[fixture_name])
