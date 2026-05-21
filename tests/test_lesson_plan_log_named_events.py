"""AC-T.7 — `NAMED_MANDATORY_EVENTS` ↔ `RESERVED_LOG_EVENT_TYPES` parity
+ M-3 frozenset immutability assertion (Murat R2 rider).

M-3: NAMED_MANDATORY_EVENTS.add("custom-event") must raise AttributeError
(frozensets have no ``add``). Prevents runtime-mutation backdoors.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.event_type_registry import RESERVED_LOG_EVENT_TYPES
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import NAMED_MANDATORY_EVENTS, LessonPlanLog


@pytest.fixture
def tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "log.jsonl")


# ---------------------------------------------------------------------------
# Parity (AC-T.7)
# ---------------------------------------------------------------------------


def test_named_mandatory_events_equals_reserved_log_event_types() -> None:
    assert NAMED_MANDATORY_EVENTS == RESERVED_LOG_EVENT_TYPES, (
        f"NAMED_MANDATORY_EVENTS drifted from RESERVED_LOG_EVENT_TYPES. "
        f"Missing: {RESERVED_LOG_EVENT_TYPES - NAMED_MANDATORY_EVENTS}. "
        f"New: {NAMED_MANDATORY_EVENTS - RESERVED_LOG_EVENT_TYPES}."
    )


def test_named_mandatory_events_is_alias_of_reserved() -> None:
    """AC-B.8: single source of truth. NAMED_MANDATORY_EVENTS IS RESERVED_LOG_EVENT_TYPES."""
    assert NAMED_MANDATORY_EVENTS is RESERVED_LOG_EVENT_TYPES


def test_named_mandatory_events_contains_all_six_amendment_8_events() -> None:
    """R1 ruling amendment 8 — the six named mandatory event_types are
    minimums, not ceilings.

    Subsequent stories may extend the registered set via ruling amendment
    (e.g. Story 29-1 adds ``fit_report.emitted`` per R1 amendment 5 and
    the 29-1 spec). The invariant pinned by this test is that the original
    six R1-amendment-8 events remain a SUBSET of NAMED_MANDATORY_EVENTS —
    removing any of them requires a new ruling amendment, not a quiet edit.
    """
    r1_amendment_8_minimum = {
        "plan_unit.created",
        "scope_decision.set",
        "scope_decision_transition",
        "plan.locked",
        "fanout.envelope.emitted",
        "pre_packet_snapshot",
    }
    missing = r1_amendment_8_minimum - NAMED_MANDATORY_EVENTS
    assert not missing, (
        f"R1 amendment 8 minimum set drifted — missing: {sorted(missing)}. "
        f"Removing any amendment-8 event requires a ruling amendment."
    )


# ---------------------------------------------------------------------------
# Unknown event_type rejected at append_event
# ---------------------------------------------------------------------------


def test_append_event_rejects_unknown_event_type(tmp_log: LessonPlanLog) -> None:
    """AC-B.2 (b): unknown event_type → ValueError with explanatory message."""
    env = EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=0,
        event_type="arbitrary.extra",
        payload={},
    )
    with pytest.raises(ValueError) as exc:
        tmp_log.append_event(env, writer_identity="marcus-orchestrator")
    msg = str(exc.value)
    assert "arbitrary.extra" in msg
    assert "NAMED_MANDATORY_EVENTS" in msg
    assert "governance artifact" in msg


# ---------------------------------------------------------------------------
# M-3 frozenset immutability (Murat R2 rider)
# ---------------------------------------------------------------------------


def test_m3_frozenset_add_raises_attribute_error() -> None:
    """M-3: NAMED_MANDATORY_EVENTS.add must not exist (frozenset)."""
    with pytest.raises(AttributeError):
        NAMED_MANDATORY_EVENTS.add("custom-event")  # type: ignore[attr-defined]


def test_m3_frozenset_remove_raises_attribute_error() -> None:
    """M-3 sibling: remove must also not exist."""
    with pytest.raises(AttributeError):
        NAMED_MANDATORY_EVENTS.remove("plan.locked")  # type: ignore[attr-defined]


def test_m3_frozenset_discard_raises_attribute_error() -> None:
    """M-3 sibling: discard must also not exist."""
    with pytest.raises(AttributeError):
        NAMED_MANDATORY_EVENTS.discard("plan.locked")  # type: ignore[attr-defined]


def test_m3_frozenset_clear_raises_attribute_error() -> None:
    """M-3 sibling: clear must also not exist."""
    with pytest.raises(AttributeError):
        NAMED_MANDATORY_EVENTS.clear()  # type: ignore[attr-defined]


def test_m3_type_is_frozenset_not_set() -> None:
    """M-3 direct type assertion.

    G6 SF-BH-12: simplified from the original two-disjunct form. Since
    :class:`frozenset` is NOT a subclass of :class:`set`, the direct type
    check is sufficient and non-tautological.
    """
    assert type(NAMED_MANDATORY_EVENTS) is frozenset
