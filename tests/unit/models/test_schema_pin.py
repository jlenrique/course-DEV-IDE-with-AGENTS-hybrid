"""Schema-pin emission tests for the 3 new top-level schemas (Story 1.3).

Pairs with `tests/unit/models/state/test_schema_pin.py` (which pins the 9
state-package schemas). Drift = test failure; intentional schema changes
update the pin in the same PR per bundle §3 idiom #11.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.models.registry import PipelineRegistry
from app.models.selection_policy import ModelSelectionPolicy
from app.models.specialist_model_config import SpecialistModelConfig

_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "models"

_PIN_TARGETS: list[tuple[str, type[BaseModel]]] = [
    ("pipeline_registry", PipelineRegistry),
    ("model_selection_policy", ModelSelectionPolicy),
    ("specialist_model_config", SpecialistModelConfig),
]


@pytest.mark.parametrize(("name", "model_class"), _PIN_TARGETS, ids=[n for n, _ in _PIN_TARGETS])
def test_live_schema_matches_pinned_fixture(name: str, model_class: type[BaseModel]) -> None:
    pin_path = _FIXTURES_DIR / f"schema_pin_{name}.json"
    pinned = json.loads(pin_path.read_text(encoding="utf-8"))
    live = model_class.model_json_schema()
    assert live == pinned, (
        f"{model_class.__name__} JSON Schema drifted from pin.\n"
        f"  pin file: {pin_path}\n"
        "  Update the pin in the SAME PR if intentional, OR fix the model."
    )
