"""Shape-pin tests for `SpecialistModelConfig` (Story 1.3 Dev Notes)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.specialist_model_config import SpecialistModelConfig

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "models"


def _golden() -> dict[str, Any]:
    return json.loads(
        (_FIXTURES / "golden_specialist_model_config.json").read_text(encoding="utf-8")
    )


def test_round_trip_against_golden_fixture() -> None:
    golden = _golden()
    rebuilt = SpecialistModelConfig.model_validate(golden).model_dump(mode="json")
    assert rebuilt == golden


def test_forbids_extra_fields() -> None:
    payload = _golden()
    payload["bogus"] = True
    with pytest.raises(ValidationError):
        SpecialistModelConfig.model_validate(payload)


def test_temperature_lower_bound_enforced() -> None:
    payload = _golden()
    payload["temperature_default"] = -0.0001
    with pytest.raises(ValidationError):
        SpecialistModelConfig.model_validate(payload)


def test_temperature_upper_bound_enforced() -> None:
    payload = _golden()
    payload["temperature_default"] = 2.0001
    with pytest.raises(ValidationError):
        SpecialistModelConfig.model_validate(payload)


def test_specialist_id_min_length() -> None:
    payload = _golden()
    payload["specialist_id"] = ""
    with pytest.raises(ValidationError):
        SpecialistModelConfig.model_validate(payload)


def test_default_model_min_length() -> None:
    payload = _golden()
    payload["default_model"] = ""
    with pytest.raises(ValidationError):
        SpecialistModelConfig.model_validate(payload)


def test_per_node_overrides_default_empty() -> None:
    payload = {
        "specialist_id": "irene",
        "default_model": "gpt-5",
        "temperature_default": 0.0,
    }
    config = SpecialistModelConfig.model_validate(payload)
    assert config.per_node_overrides == {}


def test_is_frozen() -> None:
    config = SpecialistModelConfig.model_validate(_golden())
    with pytest.raises(ValidationError):
        config.default_model = "gpt-5-nano"  # frozen=True forbids


def test_canonical_scaffold_yaml_loads() -> None:
    """The shipped _scaffold/model_config.yaml IS valid against the schema (drift guard)."""
    import yaml

    scaffold_path = (
        Path(__file__).resolve().parents[3]
        / "app"
        / "specialists"
        / "_scaffold"
        / "model_config.yaml"
    )
    raw = yaml.safe_load(scaffold_path.read_text(encoding="utf-8"))
    SpecialistModelConfig.model_validate(raw)
