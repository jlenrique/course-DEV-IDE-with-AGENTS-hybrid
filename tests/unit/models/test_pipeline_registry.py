"""Shape-pin tests for `PipelineRegistry` (Story 1.3 AC-1.3-A)."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.registry import PipelineRegistry, RegistryEntry

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "models"


def _golden() -> dict[str, Any]:
    return json.loads((_FIXTURES / "golden_pipeline_registry.json").read_text(encoding="utf-8"))


def _entry_kwargs() -> dict[str, Any]:
    return {
        "id": "11111111-1111-4111-8111-111111111111",
        "model_id": "gpt-5",
        "display_name": "GPT-5",
        "provider": "openai",
        "context_window": 400000,
        "cost_per_million_input_tokens": Decimal("1.25"),
        "cost_per_million_output_tokens": Decimal("10.00"),
        "tier": "reasoning",
        "available": True,
    }


def test_round_trip_against_golden_fixture() -> None:
    golden = _golden()
    rebuilt = PipelineRegistry.model_validate(golden).model_dump(mode="json")
    assert rebuilt == golden


def test_forbids_extra_field_on_registry() -> None:
    payload = _golden()
    payload["bogus"] = True
    with pytest.raises(ValidationError):
        PipelineRegistry.model_validate(payload)


def test_forbids_extra_field_on_entry() -> None:
    e = _entry_kwargs()
    e["bogus"] = True
    with pytest.raises(ValidationError):
        RegistryEntry.model_validate(e)


def test_default_model_id_must_match_available_entry() -> None:
    payload = {
        "id": "00000000-0000-4000-8000-000000000099",
        "default_model_id": "gpt-99-fictional",  # not in entries
        "auto_select_enabled": True,
        "entries": [_entry_kwargs()],
    }
    with pytest.raises(ValidationError):
        PipelineRegistry.model_validate(payload)


def test_default_model_id_unavailable_entry_rejected() -> None:
    payload = {
        "id": "00000000-0000-4000-8000-00000000aaaa",
        "default_model_id": "gpt-5",
        "auto_select_enabled": True,
        "entries": [{**_entry_kwargs(), "available": False}],
    }
    with pytest.raises(ValidationError):
        PipelineRegistry.model_validate(payload)


def test_empty_registry_passes_default_check() -> None:
    """Empty registry skips the default-match invariant; selector handles at runtime."""
    payload = {
        "id": "00000000-0000-4000-8000-00000000bbbb",
        "default_model_id": "gpt-5",
        "auto_select_enabled": True,
        "entries": [],
    }
    registry = PipelineRegistry.model_validate(payload)
    assert registry.entries == []


def test_provider_closed_enum_rejects_unknown() -> None:
    e = _entry_kwargs()
    e["provider"] = "anthropic"  # not in Slab 1 closed enum
    with pytest.raises(ValidationError):
        RegistryEntry.model_validate(e)


def test_tier_closed_enum_rejects_unknown() -> None:
    e = _entry_kwargs()
    e["tier"] = "magic"
    with pytest.raises(ValidationError):
        RegistryEntry.model_validate(e)


def test_context_window_must_be_positive() -> None:
    e = _entry_kwargs()
    e["context_window"] = 0
    with pytest.raises(ValidationError):
        RegistryEntry.model_validate(e)


def test_cost_must_be_non_negative() -> None:
    e = _entry_kwargs()
    e["cost_per_million_input_tokens"] = Decimal("-0.01")
    with pytest.raises(ValidationError):
        RegistryEntry.model_validate(e)


def test_entry_is_frozen() -> None:
    entry = RegistryEntry.model_validate(_entry_kwargs())
    with pytest.raises(ValidationError):
        entry.available = False  # frozen=True forbids mutation


def test_registry_check_yaml_loads_canonical_catalog() -> None:
    """The shipped registry.yaml IS valid against the schema (drift guard)."""
    import yaml

    from app.models.registry_check import REGISTRY_PATH

    raw = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry = PipelineRegistry.model_validate(raw)
    assert len(registry.entries) >= 3
    assert registry.default_model_id in {e.model_id for e in registry.entries}
