"""Shape-pin tests for `RunState` (Story 1.2 AC-1.2-A/B/C/D)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.state import (
    ALLOWED_GRAPH_VERSIONS,
    ModelResolutionEntry,
    RunState,
)
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


@pytest.fixture
def valid_kwargs() -> dict[str, object]:
    return {"graph_version": "v0.1-stub"}


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(RunState, load_golden("run_state"))


def test_forbids_extra_fields(valid_kwargs: dict[str, object]) -> None:
    assert_forbids_extra_field(RunState, valid_kwargs)


def test_default_run_id_is_uuid4(valid_kwargs: dict[str, object]) -> None:
    rs = RunState(**valid_kwargs)
    assert rs.run_id.version == 4


def test_rejects_non_uuid4_run_id(valid_kwargs: dict[str, object]) -> None:
    """G6-EDGE coverage: explicit UUID-version rejection (was implicit)."""
    import uuid

    valid_kwargs["run_id"] = uuid.uuid1()
    with pytest.raises(ValidationError):
        RunState(**valid_kwargs)


def test_default_status_is_pending(valid_kwargs: dict[str, object]) -> None:
    rs = RunState(**valid_kwargs)
    assert rs.status == "pending"


@pytest.mark.parametrize("status", ["pending", "running", "complete", "failed"])
def test_accepts_valid_status_values(status: str, valid_kwargs: dict[str, object]) -> None:
    if status == "complete":
        valid_kwargs["completed_at"] = datetime.now(UTC)
    valid_kwargs["status"] = status
    rs = RunState(**valid_kwargs)
    assert rs.status == status


def test_rejects_unknown_status(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["status"] = "garbage"
    with pytest.raises(ValidationError):
        RunState(**valid_kwargs)


def test_complete_requires_completed_at(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["status"] = "complete"
    with pytest.raises(ValidationError):
        RunState(**valid_kwargs)


def test_completed_at_only_valid_when_complete(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["completed_at"] = datetime.now(UTC)
    with pytest.raises(ValidationError):
        RunState(**valid_kwargs)  # status='pending' with completed_at set


def test_rejects_unknown_graph_version() -> None:
    with pytest.raises(ValidationError):
        RunState(graph_version="v99-future")


def test_allowed_graph_versions_is_frozen_set() -> None:
    """Slab 4 Story 4.5 wires the real registry; until then this stub is the SoT."""
    assert isinstance(ALLOWED_GRAPH_VERSIONS, frozenset)
    assert "v0.1-stub" in ALLOWED_GRAPH_VERSIONS


@pytest.mark.parametrize("temp", [0.0, 0.5, 1.0, 2.0])
def test_accepts_valid_temperature(temp: float, valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["temperature"] = temp
    rs = RunState(**valid_kwargs)
    assert rs.temperature == temp


@pytest.mark.parametrize("temp", [-0.1, 2.1, 100.0])
def test_rejects_out_of_range_temperature(
    temp: float, valid_kwargs: dict[str, object]
) -> None:
    valid_kwargs["temperature"] = temp
    with pytest.raises(ValidationError):
        RunState(**valid_kwargs)


def test_model_resolution_trail_default_empty(valid_kwargs: dict[str, object]) -> None:
    rs = RunState(**valid_kwargs)
    assert rs.model_resolution_trail == []


def test_model_resolution_trail_accepts_entries(valid_kwargs: dict[str, object]) -> None:
    entry = ModelResolutionEntry(
        level="registry-default",
        resolved="gpt-5.4",
        timestamp=datetime.now(UTC),
    )
    valid_kwargs["model_resolution_trail"] = [entry]
    rs = RunState(**valid_kwargs)
    assert len(rs.model_resolution_trail) == 1


def test_rejects_naive_created_at(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["created_at"] = datetime(2026, 4, 23)  # naive
    with pytest.raises(ValidationError):
        RunState(**valid_kwargs)
