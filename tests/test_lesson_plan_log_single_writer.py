"""AC-T.3 — Single-writer matrix (R1 ruling amendment 13 CENTRAL test).

Parametrized over the full (writer_identity × event_type) Cartesian product
(2 × 6 = 12 cases). ACCEPT cases verify the event lands on the log via
read-back; REJECT cases verify ``UnauthorizedWriterError`` is raised with a
message naming both the ``writer_identity`` and ``event_type``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from itertools import product
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import (
    NAMED_MANDATORY_EVENTS,
    WRITER_EVENT_MATRIX,
    LessonPlanLog,
    UnauthorizedWriterError,
)

WRITER_IDENTITIES = ("marcus-orchestrator", "marcus-intake")
EVENT_TYPES = tuple(sorted(NAMED_MANDATORY_EVENTS))


def _env(event_type: str, plan_revision: int) -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=plan_revision,
        event_type=event_type,
        payload={},
    )


@pytest.fixture
def tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "log.jsonl")


@pytest.mark.parametrize(
    "writer_identity,event_type",
    list(product(WRITER_IDENTITIES, EVENT_TYPES)),
)
def test_single_writer_matrix_cartesian(
    tmp_log: LessonPlanLog,
    writer_identity: str,
    event_type: str,
) -> None:
    """All 12 cells of the AC-B.3 single-writer matrix."""
    # For plan.locked, require revision >= 1 to pass the monotonic gate.
    plan_revision = 1 if event_type == "plan.locked" else 0
    env = _env(event_type, plan_revision)
    permitted = WRITER_EVENT_MATRIX[event_type]

    if writer_identity in permitted:
        # ACCEPT case: event lands on the log.
        tmp_log.append_event(env, writer_identity=writer_identity)  # type: ignore[arg-type]
        read_back = list(tmp_log.read_events(event_types={event_type}))
        assert len(read_back) == 1, (
            f"{writer_identity} → {event_type} expected ACCEPT but read-back empty"
        )
        assert read_back[0].event_type == event_type
    else:
        # REJECT case: UnauthorizedWriterError with the writer_identity + event_type
        # both named in the message.
        with pytest.raises(UnauthorizedWriterError) as exc:
            tmp_log.append_event(env, writer_identity=writer_identity)  # type: ignore[arg-type]
        msg = str(exc.value)
        assert writer_identity in msg, (
            f"error message missing writer_identity={writer_identity!r}: {msg}"
        )
        assert event_type in msg, (
            f"error message missing event_type={event_type!r}: {msg}"
        )
        # And no partial line landed in the log.
        # Tightened by party-mode 2026-04-19 follow-on (Auditor#5):
        # require strict zero-byte file (not "stripped-empty") so a stray
        # whitespace-only line on REJECT path would still fail this assertion.
        assert not tmp_log.path.exists() or tmp_log.path.stat().st_size == 0, (
            f"REJECT path left non-empty bytes on disk: "
            f"{tmp_log.path.read_bytes()!r}"
        )


def test_unauthorized_writer_is_permission_error_subclass() -> None:
    """AC-B.2 (c): UnauthorizedWriterError subclasses PermissionError."""
    assert issubclass(UnauthorizedWriterError, PermissionError)


def test_matrix_covers_all_named_mandatory_events() -> None:
    """AC-T.7 sibling: WRITER_EVENT_MATRIX keys == NAMED_MANDATORY_EVENTS."""
    assert set(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS
