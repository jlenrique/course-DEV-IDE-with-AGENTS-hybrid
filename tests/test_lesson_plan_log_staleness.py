"""AC-T.4 — `assert_plan_fresh` 2×2 staleness matrix (M-1 R2 rider).
AC-T.11 — re-read-after-write consistency (M-5 R2 rider).

Two parametrized 2×2 cells + edge cases + M-5 consistency test.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import (
    LessonPlanLog,
    StalePlanRefError,
    assert_plan_fresh,
)


@dataclass
class _FakeEnvelope:
    """Duck-typed envelope carrying plan-ref fields (per AC-B.5 duck-typing contract)."""

    lesson_plan_revision: int
    lesson_plan_digest: str


@pytest.fixture
def tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "log.jsonl")


def _plan_locked_envelope(plan_revision: int, digest: str) -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=plan_revision,
        event_type="plan.locked",
        payload={"lesson_plan_digest": digest},
    )


def _seed_log(log: LessonPlanLog, revision: int, digest: str) -> None:
    """Seed a log with a single plan.locked event at the given revision/digest."""
    log.append_event(
        _plan_locked_envelope(revision, digest),
        writer_identity="marcus-orchestrator",
    )


# ---------------------------------------------------------------------------
# M-1 2×2 staleness matrix
# ---------------------------------------------------------------------------


def test_cell1_rev_match_digest_match_passes(tmp_log: LessonPlanLog) -> None:
    """Cell 1: (rev_match=True, digest_match=True) → no raise."""
    _seed_log(tmp_log, revision=5, digest="abc")
    env = _FakeEnvelope(lesson_plan_revision=5, lesson_plan_digest="abc")
    # No raise.
    assert_plan_fresh(env, log=tmp_log)


def test_cell2_rev_match_digest_mismatch_names_digest_axis(tmp_log: LessonPlanLog) -> None:
    """Cell 2: (rev_match=True, digest_match=False) → names digest axis only."""
    _seed_log(tmp_log, revision=5, digest="abc")
    env = _FakeEnvelope(lesson_plan_revision=5, lesson_plan_digest="def")
    with pytest.raises(StalePlanRefError) as exc:
        assert_plan_fresh(env, log=tmp_log)
    msg = str(exc.value)
    assert "digest mismatch" in msg
    # Must NOT name revision as a mismatch when only digest diverges.
    assert "revision mismatch" not in msg, (
        f"Cell 2 must name digest only; got: {msg}"
    )
    # Tightened by party-mode 2026-04-19 follow-on (Auditor#2):
    # assert the exact envelope/log naming so a future refactor that swaps
    # the two axis values cannot pass with substring-only matching.
    assert "envelope='def'" in msg, (
        f"Cell 2 must name envelope digest verbatim ('def'); got: {msg}"
    )
    assert "log='abc'" in msg, (
        f"Cell 2 must name log digest verbatim ('abc'); got: {msg}"
    )


def test_cell3_rev_mismatch_digest_match_names_revision_axis(tmp_log: LessonPlanLog) -> None:
    """Cell 3: (rev_match=False, digest_match=True) → names revision axis only."""
    _seed_log(tmp_log, revision=5, digest="abc")
    env = _FakeEnvelope(lesson_plan_revision=7, lesson_plan_digest="abc")
    with pytest.raises(StalePlanRefError) as exc:
        assert_plan_fresh(env, log=tmp_log)
    msg = str(exc.value)
    assert "revision mismatch" in msg
    # Must NOT name digest as a mismatch when only revision diverges.
    assert "digest mismatch" not in msg, (
        f"Cell 3 must name revision only; got: {msg}"
    )
    # G6 SF-AA-2: axis-named literal format (avoids spurious substring
    # matches inside digests like "abc5def").
    assert "envelope=7" in msg
    assert "log=5" in msg


def test_cell4_both_axes_mismatch_names_both(tmp_log: LessonPlanLog) -> None:
    """Cell 4: (rev_match=False, digest_match=False) → names BOTH axes."""
    _seed_log(tmp_log, revision=5, digest="abc")
    env = _FakeEnvelope(lesson_plan_revision=7, lesson_plan_digest="def")
    with pytest.raises(StalePlanRefError) as exc:
        assert_plan_fresh(env, log=tmp_log)
    msg = str(exc.value)
    assert "revision mismatch" in msg
    assert "digest mismatch" in msg


# ---------------------------------------------------------------------------
# Empty-log bootstrap edges
# ---------------------------------------------------------------------------


def test_empty_log_bootstrap_revision_zero_digest_empty_passes(
    tmp_log: LessonPlanLog,
) -> None:
    """Envelope claiming revision=0, digest='' against empty log passes.

    G6 MF-BH-4: bootstrap sentinel aligned with ``PlanLockedPayload`` contract.
    ``latest_plan_digest()`` returns ``None`` for empty logs (read-side
    contract); a bootstrap envelope may carry either ``""`` or ``None``
    to signal "no prior lock yet."
    """
    env = _FakeEnvelope(lesson_plan_revision=0, lesson_plan_digest="")
    assert_plan_fresh(env, log=tmp_log)
    # G6 MF-BH-4: latest_plan_digest() returns None on empty log; envelope
    # bootstrap must also accept the None sentinel.
    assert tmp_log.latest_plan_digest() is None


def test_empty_log_any_other_envelope_raises(tmp_log: LessonPlanLog) -> None:
    """Envelope with revision >= 1 against empty log is stale."""
    env = _FakeEnvelope(lesson_plan_revision=1, lesson_plan_digest="abc")
    with pytest.raises(StalePlanRefError):
        assert_plan_fresh(env, log=tmp_log)


def test_error_message_class_prefix(tmp_log: LessonPlanLog) -> None:
    """Error message starts with 'StalePlanRefError:' (M-1 format pin)."""
    _seed_log(tmp_log, revision=5, digest="abc")
    env = _FakeEnvelope(lesson_plan_revision=7, lesson_plan_digest="def")
    with pytest.raises(StalePlanRefError) as exc:
        assert_plan_fresh(env, log=tmp_log)
    assert str(exc.value).startswith("StalePlanRefError:")


# ---------------------------------------------------------------------------
# M-5 — re-read-after-write consistency (AC-T.11)
# ---------------------------------------------------------------------------


def test_re_read_after_write_consistency(tmp_log: LessonPlanLog) -> None:
    """AC-T.11 (M-5): immediate read_events after append_event yields the event.

    Regression shield against a dev-agent forgetting ``fsync`` or using
    unbuffered ``open(..., "a")`` naively — write-side OS buffering could
    otherwise mask a not-yet-persisted line from an immediate reader.
    """
    env = EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=3,
        event_type="scope_decision_transition",
        payload={},
    )
    tmp_log.append_event(env, writer_identity="marcus-orchestrator")
    # IMMEDIATE read-back — must yield the just-appended event.
    read_back = list(tmp_log.read_events())
    assert len(read_back) == 1
    assert read_back[0].event_id == env.event_id
    assert read_back[0].event_type == "scope_decision_transition"


def test_re_read_after_multiple_writes(tmp_log: LessonPlanLog) -> None:
    """M-5 extended: sequential write → read → write → read stays consistent."""
    e1 = EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=1,
        event_type="plan_unit.created",
        payload={},
    )
    tmp_log.append_event(e1, writer_identity="marcus-orchestrator")
    assert len(list(tmp_log.read_events())) == 1

    e2 = EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=1,
        event_type="scope_decision.set",
        payload={},
    )
    tmp_log.append_event(e2, writer_identity="marcus-orchestrator")
    read_back = list(tmp_log.read_events())
    assert len(read_back) == 2
    assert [e.event_type for e in read_back] == [
        "plan_unit.created",
        "scope_decision.set",
    ]
