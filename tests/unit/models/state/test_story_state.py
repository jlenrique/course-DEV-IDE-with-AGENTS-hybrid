"""Shape-pin tests for `StoryState` (Story 1.2 AC-1.2-A/B/C)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.state import NodeCheckpoint, StoryState
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(StoryState, load_golden("story_state"))


def test_forbids_extra_fields() -> None:
    assert_forbids_extra_field(StoryState, {"story_id": "story-001"})


def test_default_node_checkpoints_is_empty_list() -> None:
    ss = StoryState(story_id="story-001")
    assert ss.node_checkpoints == []


def test_accepts_node_checkpoint_list() -> None:
    nc = NodeCheckpoint(
        node_id="noop",
        step_index=0,
        status="pending",
        checkpoint_at=datetime.now(UTC),
    )
    ss = StoryState(story_id="story-001", node_checkpoints=[nc])
    assert len(ss.node_checkpoints) == 1
    assert ss.node_checkpoints[0].node_id == "noop"


def test_rejects_empty_story_id() -> None:
    with pytest.raises(ValidationError):
        StoryState(story_id="")


def test_default_updated_at_tz_aware() -> None:
    ss = StoryState(story_id="story-001")
    assert ss.updated_at.tzinfo is not None


def test_rejects_naive_updated_at() -> None:
    with pytest.raises(ValidationError):
        StoryState(story_id="story-001", updated_at=datetime(2026, 4, 23))
