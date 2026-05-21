from __future__ import annotations

import json

import pytest

from tests.unit.models.decision_cards._helpers import FIXTURES_DIR, GATE_MODELS, load_fixture

_GATE_IDS = [name for name, _ in GATE_MODELS]


@pytest.mark.parametrize(("fixture_name", "model_class"), GATE_MODELS, ids=_GATE_IDS)
def test_per_gate_golden_fixture_round_trip_is_byte_identical(
    fixture_name: str,
    model_class: type,
) -> None:
    payload = load_fixture(fixture_name)
    instance = model_class.model_validate(payload)
    dumped = json.dumps(instance.model_dump(mode="json"), indent=2, sort_keys=True) + "\n"
    assert dumped == (FIXTURES_DIR / f"{fixture_name}_golden.json").read_text(encoding="utf-8")
