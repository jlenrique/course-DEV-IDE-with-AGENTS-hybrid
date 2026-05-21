"""Shape-pin tests for `NodeCheckpoint` (Story 1.2 AC-1.2-A/B/C)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.state import NodeCheckpoint
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


@pytest.fixture
def valid_kwargs() -> dict[str, object]:
    return {
        "node_id": "noop",
        "step_index": 0,
        "status": "pending",
        "checkpoint_at": datetime.now(UTC),
    }


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(NodeCheckpoint, load_golden("node_checkpoint"))


def test_forbids_extra_fields(valid_kwargs: dict[str, object]) -> None:
    assert_forbids_extra_field(NodeCheckpoint, valid_kwargs)


@pytest.mark.parametrize("status", ["pending", "running", "complete", "failed"])
def test_accepts_valid_status_values(status: str, valid_kwargs: dict[str, object]) -> None:
    if status == "complete":
        valid_kwargs["completed_at"] = datetime.now(UTC)
    valid_kwargs["status"] = status
    nc = NodeCheckpoint(**valid_kwargs)
    assert nc.status == status


def test_rejects_unknown_status(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["status"] = "garbage"
    with pytest.raises(ValidationError):
        NodeCheckpoint(**valid_kwargs)


def test_complete_requires_completed_at(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["status"] = "complete"
    with pytest.raises(ValidationError):
        NodeCheckpoint(**valid_kwargs)


def test_completed_at_only_valid_when_complete(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["completed_at"] = datetime.now(UTC)
    with pytest.raises(ValidationError):
        NodeCheckpoint(**valid_kwargs)  # status='pending' with completed_at set


def test_rejects_negative_step_index(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["step_index"] = -1
    with pytest.raises(ValidationError):
        NodeCheckpoint(**valid_kwargs)


def test_rejects_naive_checkpoint_at(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["checkpoint_at"] = datetime(2026, 4, 23)  # naive
    with pytest.raises(ValidationError):
        NodeCheckpoint(**valid_kwargs)
