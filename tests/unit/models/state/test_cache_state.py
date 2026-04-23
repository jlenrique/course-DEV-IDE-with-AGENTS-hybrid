"""Shape-pin tests for `CacheState` (Story 1.2 AC-1.2-A/B/C)."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.state import CacheState
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(CacheState, load_golden("cache_state"))


def test_forbids_extra_fields() -> None:
    assert_forbids_extra_field(CacheState, {"cache_prefix": "abc"})


def test_rejects_empty_cache_prefix() -> None:
    with pytest.raises(ValidationError):
        CacheState(cache_prefix="")


def test_rejects_negative_entries_count() -> None:
    with pytest.raises(ValidationError):
        CacheState(cache_prefix="abc", entries_count=-1)


def test_rejects_naive_invalidated_at() -> None:
    with pytest.raises(ValidationError):
        CacheState(
            cache_prefix="abc",
            last_invalidated_at=datetime(2026, 4, 23, 12, 0, 0),  # naive
        )


def test_default_entries_count_zero() -> None:
    cs = CacheState(cache_prefix="abc")
    assert cs.entries_count == 0
    assert cs.last_invalidated_at is None


def test_validate_assignment_rejects_naive_after_construction() -> None:
    """validate_assignment=True hardens against MF-4-class mutation drift."""
    cs = CacheState(cache_prefix="abc")
    with pytest.raises(ValidationError):
        cs.last_invalidated_at = datetime(2026, 4, 23)  # naive
