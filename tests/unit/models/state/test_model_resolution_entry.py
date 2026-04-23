"""Shape-pin tests for `ModelResolutionEntry` (Story 1.2 stub for 1.3 replacement).

These tests pin the 1.2 stub shape ONLY. Story 1.3 deletes + re-authors
the model with the full cascade-resolution shape; these tests will be
replaced wholesale at that time.
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


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(ModelResolutionEntry, load_golden("model_resolution_entry"))


def test_forbids_extra_fields() -> None:
    """1.3 will add fields; the stub forbids them so accidental drift fails fast here."""
    assert_forbids_extra_field(
        ModelResolutionEntry,
        {
            "level": "registry-default",
            "resolved": "gpt-5.4",
            "timestamp": datetime.now(UTC),
        },
    )


def test_rejects_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        ModelResolutionEntry(
            level="registry-default",
            resolved="gpt-5.4",
            timestamp=datetime(2026, 4, 23),  # naive
        )


def test_rejects_empty_level() -> None:
    with pytest.raises(ValidationError):
        ModelResolutionEntry(
            level="",
            resolved="gpt-5.4",
            timestamp=datetime.now(UTC),
        )


def test_rejects_empty_resolved() -> None:
    with pytest.raises(ValidationError):
        ModelResolutionEntry(
            level="registry-default",
            resolved="",
            timestamp=datetime.now(UTC),
        )
