"""AC-T.2 — Append-only enforcement on LessonPlanLog.

Asserts:
    - N events written → N events read in insertion order.
    - Public API exposes no mutation methods (delete, update_event, overwrite).
    - Duplicate event_id produces TWO log lines (dedup is out-of-scope).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog


@pytest.fixture
def tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "log.jsonl")


def _env(event_type: str, plan_revision: int, event_id: str | None = None) -> EventEnvelope:
    return EventEnvelope(
        event_id=event_id if event_id is not None else str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=plan_revision,
        event_type=event_type,
        payload={},
    )


def test_no_mutation_methods_on_public_api() -> None:
    """AC-T.2: delete / update_event / overwrite must not exist on LessonPlanLog."""
    assert not hasattr(LessonPlanLog, "delete"), "LessonPlanLog must not expose .delete"
    assert not hasattr(LessonPlanLog, "update_event"), (
        "LessonPlanLog must not expose .update_event"
    )
    assert not hasattr(LessonPlanLog, "overwrite"), (
        "LessonPlanLog must not expose .overwrite"
    )
    assert not hasattr(LessonPlanLog, "truncate"), (
        "LessonPlanLog must not expose .truncate (append-only)"
    )
    assert not hasattr(LessonPlanLog, "clear"), (
        "LessonPlanLog must not expose .clear (append-only)"
    )


def test_appended_events_read_back_in_insertion_order(tmp_log: LessonPlanLog) -> None:
    envs = [
        _env("plan_unit.created", 1),
        _env("scope_decision.set", 1),
        _env("scope_decision_transition", 2),
        _env("plan.locked", 2),
    ]
    for env in envs:
        tmp_log.append_event(env, writer_identity="marcus-orchestrator")
    # Read back; plan.locked is tied to revision 2, others interleave fine.
    read_back = list(tmp_log.read_events())
    assert len(read_back) == 4
    assert [e.event_type for e in read_back] == [
        "plan_unit.created",
        "scope_decision.set",
        "scope_decision_transition",
        "plan.locked",
    ]


def test_duplicate_event_id_produces_two_log_lines(tmp_log: LessonPlanLog) -> None:
    """AC-T.2: dedup on event_id is OUT-OF-SCOPE for 31-2."""
    shared_id = str(uuid4())
    e1 = _env("plan_unit.created", 1, event_id=shared_id)
    e2 = _env("plan_unit.created", 1, event_id=shared_id)
    tmp_log.append_event(e1, writer_identity="marcus-orchestrator")
    tmp_log.append_event(e2, writer_identity="marcus-orchestrator")
    lines = tmp_log.path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2, "duplicate event_id must produce TWO log lines (no dedup)"
    # Both envelopes share the same event_id.
    read_back = list(tmp_log.read_events())
    assert read_back[0].event_id == shared_id
    assert read_back[1].event_id == shared_id


def test_read_events_on_missing_file_returns_empty(tmp_path: Path) -> None:
    """Reading an un-created log returns no events without error."""
    log = LessonPlanLog(path=tmp_path / "nonexistent.jsonl")
    assert list(log.read_events()) == []
