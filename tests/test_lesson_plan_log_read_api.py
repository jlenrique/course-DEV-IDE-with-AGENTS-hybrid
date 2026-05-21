"""AC-T.8 — Read API filter + ordering + no-mutation-leak.

Read API: ``read_events(since_revision=None, event_types=None)`` returns
an iterator. Combined filter composes. Mutating a yielded envelope does
not leak state to subsequent reads.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog


@pytest.fixture
def populated_log(tmp_path: Path) -> LessonPlanLog:
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    # Seed a mixed set of events. Plan.locked events are strictly monotonic.
    events = [
        ("plan_unit.created", 1),
        ("scope_decision.set", 1),
        ("plan.locked", 1),
        ("scope_decision_transition", 2),
        ("plan_unit.created", 2),
        ("plan.locked", 2),
        ("fanout.envelope.emitted", 3),
        ("plan.locked", 3),
    ]
    for event_type, rev in events:
        payload = (
            {"lesson_plan_digest": f"d{rev}"} if event_type == "plan.locked" else {}
        )
        env = EventEnvelope(
            event_id=str(uuid4()),
            timestamp=datetime.now(tz=UTC),
            plan_revision=rev,
            event_type=event_type,
            payload=payload,
        )
        log.append_event(env, writer_identity="marcus-orchestrator")
    return log


def test_read_events_returns_iterator(populated_log: LessonPlanLog) -> None:
    """AC-B.4: read_events returns an iterator, not a list."""
    result = populated_log.read_events()
    assert isinstance(result, Iterator)


def test_filter_by_revision(populated_log: LessonPlanLog) -> None:
    """since_revision=N yields events where plan_revision >= N."""
    events_ge_2 = list(populated_log.read_events(since_revision=2))
    assert all(e.plan_revision >= 2 for e in events_ge_2)
    # Five events at rev >= 2: scope_decision_transition, plan_unit.created,
    # plan.locked, fanout.envelope.emitted, plan.locked.
    assert len(events_ge_2) == 5


def test_filter_by_event_type(populated_log: LessonPlanLog) -> None:
    """event_types={'plan.locked'} yields only plan.locked events."""
    plan_locked = list(populated_log.read_events(event_types={"plan.locked"}))
    assert all(e.event_type == "plan.locked" for e in plan_locked)
    assert len(plan_locked) == 3


def test_combined_filter_composes(populated_log: LessonPlanLog) -> None:
    """since_revision + event_types compose (AND)."""
    # scope_decision_transition at revision >= 2: exactly 1 event.
    results = list(
        populated_log.read_events(
            since_revision=2,
            event_types={"scope_decision_transition"},
        )
    )
    assert len(results) == 1
    assert results[0].event_type == "scope_decision_transition"
    assert results[0].plan_revision == 2


def test_ordering_is_stable_across_reads(populated_log: LessonPlanLog) -> None:
    """AC-B.4: insertion-order (file-offset-order), stable across reads."""
    read_1 = [e.event_id for e in populated_log.read_events()]
    read_2 = [e.event_id for e in populated_log.read_events()]
    assert read_1 == read_2


def test_no_mutation_leak_on_yielded_envelope(populated_log: LessonPlanLog) -> None:
    """AC-B.4: mutating a yielded envelope does not affect subsequent reads.

    G6 SF-BH-10: this tests that ``read_events`` produces FRESH instances
    per call; the specific mutation used doesn't matter. We bypass
    Pydantic validation with ``object.__setattr__`` to sidestep the
    ``validate_assignment=True`` path — what we assert is *instance
    identity*, not validator behavior.
    """
    # First read — mutate first event via object.__setattr__ (bypasses
    # validation; we don't care about the value, only that mutation does
    # not bleed into a subsequent read_events call).
    first_read = list(populated_log.read_events())
    object.__setattr__(first_read[0], "plan_revision", 999)
    # Second read — MUST return unmutated originals.
    second_read = list(populated_log.read_events())
    # The first event's plan_revision must NOT be 999.
    assert second_read[0].plan_revision != 999
    # All envelopes are freshly-constructed (not the same objects).
    assert first_read[0] is not second_read[0]


def test_empty_filter_set_yields_nothing(populated_log: LessonPlanLog) -> None:
    """event_types=set() (empty set) filters everything out."""
    results = list(populated_log.read_events(event_types=set()))
    assert results == []


def test_since_revision_zero_returns_all(populated_log: LessonPlanLog) -> None:
    """since_revision=0 returns all (equivalent to None for MVP seed)."""
    all_events = list(populated_log.read_events())
    from_zero = list(populated_log.read_events(since_revision=0))
    assert len(all_events) == len(from_zero)
