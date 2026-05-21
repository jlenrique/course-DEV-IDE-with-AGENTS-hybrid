"""AC-T.5 — Monotonic revision on ``plan.locked`` + M-2 positive test.

M-2 (Murat R2 rider): monotonic-revision gate applies ONLY to ``plan.locked``
events. Non-``plan.locked`` events at stale revision are LEGAL (interleaved
writes ordering). This test prevents a future "fix" from tightening the
monotonic check to all events.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import StaleRevisionError


@pytest.fixture
def tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "log.jsonl")


def _plan_locked(rev: int, digest: str = "x") -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=rev,
        event_type="plan.locked",
        payload={"lesson_plan_digest": digest},
    )


def _other(event_type: str, rev: int) -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=rev,
        event_type=event_type,
        payload={},
    )


def test_plan_locked_rev1_accepts(tmp_log: LessonPlanLog) -> None:
    tmp_log.append_event(_plan_locked(1), writer_identity="marcus-orchestrator")
    assert tmp_log.latest_plan_revision() == 1


def test_plan_locked_rev1_then_rev2_accepts(tmp_log: LessonPlanLog) -> None:
    tmp_log.append_event(_plan_locked(1), writer_identity="marcus-orchestrator")
    tmp_log.append_event(_plan_locked(2), writer_identity="marcus-orchestrator")
    assert tmp_log.latest_plan_revision() == 2


def test_plan_locked_same_revision_raises_stale(tmp_log: LessonPlanLog) -> None:
    tmp_log.append_event(_plan_locked(2), writer_identity="marcus-orchestrator")
    with pytest.raises(StaleRevisionError):
        tmp_log.append_event(_plan_locked(2), writer_identity="marcus-orchestrator")


def test_plan_locked_regression_raises_stale(tmp_log: LessonPlanLog) -> None:
    tmp_log.append_event(_plan_locked(2), writer_identity="marcus-orchestrator")
    with pytest.raises(StaleRevisionError):
        tmp_log.append_event(_plan_locked(1), writer_identity="marcus-orchestrator")


def test_plan_locked_bootstrap_rev_must_be_at_least_one(tmp_log: LessonPlanLog) -> None:
    """Empty log → latest_plan_revision() == 0. plan.locked with revision=0 is stale."""
    with pytest.raises(StaleRevisionError):
        tmp_log.append_event(_plan_locked(0), writer_identity="marcus-orchestrator")


# ---------------------------------------------------------------------------
# M-2 POSITIVE TEST — non-plan.locked at stale revision is ACCEPTED
# ---------------------------------------------------------------------------


def test_non_plan_locked_stale_revision_is_accepted(tmp_log: LessonPlanLog) -> None:
    """M-2 (Murat R2 rider): non-plan.locked events at stale revision are LEGAL.

    Interleave is legal per AC-B.6 M-2 scope — the monotonic gate applies
    ONLY to plan.locked.
    """
    # Lock plan at rev=7.
    tmp_log.append_event(_plan_locked(7), writer_identity="marcus-orchestrator")
    assert tmp_log.latest_plan_revision() == 7

    # Now append a scope_decision_transition at plan_revision=5 (stale by
    # plan.locked standards but legal for this event type).
    stale_event = _other("scope_decision_transition", rev=5)
    # MUST NOT raise.
    tmp_log.append_event(stale_event, writer_identity="marcus-orchestrator")

    # Event landed; plan.locked latest unchanged.
    all_events = list(tmp_log.read_events())
    assert len(all_events) == 2
    assert tmp_log.latest_plan_revision() == 7


def test_multiple_non_plan_locked_stale_interleaves_accepted(tmp_log: LessonPlanLog) -> None:
    """M-2 extended: multiple stale non-plan.locked events interleave freely."""
    tmp_log.append_event(_plan_locked(5), writer_identity="marcus-orchestrator")
    # A bouquet of stale non-plan.locked events at revisions 1..4.
    for rev, et in [
        (1, "plan_unit.created"),
        (2, "scope_decision.set"),
        (3, "scope_decision_transition"),
        (4, "fanout.envelope.emitted"),
        (2, "pre_packet_snapshot"),
    ]:
        # NOTE: pre_packet_snapshot row permits marcus-intake, but we use
        # marcus-orchestrator here (still permitted per matrix).
        tmp_log.append_event(_other(et, rev=rev), writer_identity="marcus-orchestrator")
    all_events = list(tmp_log.read_events())
    assert len(all_events) == 6
    assert tmp_log.latest_plan_revision() == 5  # plan.locked unchanged


def test_latest_plan_digest_tracks_plan_locked_only(tmp_log: LessonPlanLog) -> None:
    """latest_plan_digest reads plan.locked payload, ignores other events."""
    tmp_log.append_event(_plan_locked(1, digest="d1"), writer_identity="marcus-orchestrator")
    tmp_log.append_event(
        _other("scope_decision.set", 1), writer_identity="marcus-orchestrator"
    )
    tmp_log.append_event(_plan_locked(2, digest="d2"), writer_identity="marcus-orchestrator")
    assert tmp_log.latest_plan_digest() == "d2"


def test_empty_log_latest_plan_revision_is_zero(tmp_log: LessonPlanLog) -> None:
    assert tmp_log.latest_plan_revision() == 0


def test_empty_log_latest_plan_digest_is_none(tmp_log: LessonPlanLog) -> None:
    assert tmp_log.latest_plan_digest() is None
