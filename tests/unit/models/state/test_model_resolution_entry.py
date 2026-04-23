"""Shape-pin tests for `ModelResolutionEntry` (Story 1.3 full cascade shape).

Story 1.3 replaced the 1.2 stub with the full cascade-resolution shape per
spec AC-1.3-C. These tests pin the new shape: closed-enum `level`,
`requested` nullable, `resolved` non-empty, `reason` non-empty, tz-aware
`timestamp`, optional `cache_prefix_hash` (sha256 hex).
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.state import ModelResolutionEntry
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


def _valid_kwargs() -> dict[str, object]:
    return {
        "level": "registry_default",
        "requested": None,
        "resolved": "gpt-5.4",
        "reason": "default fallthrough",
        "timestamp": datetime.now(UTC),
    }


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(ModelResolutionEntry, load_golden("model_resolution_entry"))


def test_forbids_extra_fields() -> None:
    assert_forbids_extra_field(ModelResolutionEntry, _valid_kwargs())


@pytest.mark.parametrize(
    "level",
    ["per_call", "per_specialist", "registry_default", "auto_select_fallback"],
)
def test_accepts_valid_level_values(level: str) -> None:
    kwargs = _valid_kwargs()
    kwargs["level"] = level
    entry = ModelResolutionEntry(**kwargs)
    assert entry.level == level


def test_rejects_unknown_level() -> None:
    kwargs = _valid_kwargs()
    kwargs["level"] = "garbage_level"
    with pytest.raises(ValidationError):
        ModelResolutionEntry(**kwargs)


def test_rejects_naive_timestamp() -> None:
    kwargs = _valid_kwargs()
    kwargs["timestamp"] = datetime(2026, 4, 23)  # naive
    with pytest.raises(ValidationError):
        ModelResolutionEntry(**kwargs)


def test_rejects_empty_resolved() -> None:
    kwargs = _valid_kwargs()
    kwargs["resolved"] = ""
    with pytest.raises(ValidationError):
        ModelResolutionEntry(**kwargs)


def test_rejects_empty_reason() -> None:
    kwargs = _valid_kwargs()
    kwargs["reason"] = ""
    with pytest.raises(ValidationError):
        ModelResolutionEntry(**kwargs)


def test_accepts_valid_cache_prefix_hash() -> None:
    kwargs = _valid_kwargs()
    kwargs["cache_prefix_hash"] = "a" * 64
    entry = ModelResolutionEntry(**kwargs)
    assert entry.cache_prefix_hash == "a" * 64


def test_rejects_short_cache_prefix_hash() -> None:
    kwargs = _valid_kwargs()
    kwargs["cache_prefix_hash"] = "a" * 32
    with pytest.raises(ValidationError):
        ModelResolutionEntry(**kwargs)


def test_rejects_non_hex_cache_prefix_hash() -> None:
    kwargs = _valid_kwargs()
    kwargs["cache_prefix_hash"] = "g" * 64
    with pytest.raises(ValidationError):
        ModelResolutionEntry(**kwargs)


def test_cache_prefix_hash_optional() -> None:
    """Non-final cascade entries may have None cache_prefix_hash."""
    entry = ModelResolutionEntry(**_valid_kwargs())
    assert entry.cache_prefix_hash is None


def test_requested_can_be_none_for_default_levels() -> None:
    kwargs = _valid_kwargs()
    kwargs["requested"] = None
    entry = ModelResolutionEntry(**kwargs)
    assert entry.requested is None


def test_requested_can_be_string_for_per_call() -> None:
    kwargs = _valid_kwargs()
    kwargs["level"] = "per_call"
    kwargs["requested"] = "gpt-5-haiku"
    kwargs["resolved"] = "gpt-5-haiku"
    entry = ModelResolutionEntry(**kwargs)
    assert entry.requested == "gpt-5-haiku"
