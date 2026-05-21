"""MF-4 — naive datetime rejection across all 5 timestamp fields.

Covers:
    - :attr:`LessonPlan.updated_at`
    - :attr:`ScopeDecision.locked_at`
    - :attr:`ScopeDecisionTransition.timestamp`
    - :attr:`EventEnvelope.timestamp`
    - :attr:`FitReport.generated_at`

Design choice (documented in ``events.py``): accept any timezone-aware
datetime (not strictly UTC) because Pydantic serializes to ISO 8601 with
offset, which is deterministic. Naive datetimes are the only rejected
class.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.events import EventEnvelope, ScopeDecisionTransition
from app.marcus.lesson_plan.schema import (
    FitReport,
    LearningModel,
    LessonPlan,
    PlanRef,
    ScopeDecision,
)

_NON_UTC_TZ = timezone(timedelta(hours=5))


# ---------------------------------------------------------------------------
# Parametrized: factory fn -> naive-datetime → ValidationError expected
# ---------------------------------------------------------------------------


def _build_lesson_plan(ts: datetime) -> LessonPlan:
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[],
        revision=1,
        updated_at=ts,
    )


def _build_scope_decision_locked_at(ts: datetime) -> ScopeDecision:
    return ScopeDecision(
        state="locked",
        scope="in-scope",
        proposed_by="operator",
        _internal_proposed_by="maya",
        ratified_by="maya",
        locked_at=ts,
    )


def _build_scope_decision_transition(ts: datetime) -> ScopeDecisionTransition:
    return ScopeDecisionTransition(
        unit_id="gagne-event-1",
        plan_revision=1,
        from_state="proposed",
        to_state="ratified",
        to_scope="in-scope",
        actor="operator",
        timestamp=ts,
    )


def _build_event_envelope(ts: datetime) -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=ts,
        plan_revision=1,
        event_type="gagne-event-1",
    )


def _build_fit_report(ts: datetime) -> FitReport:
    return FitReport(
        source_ref="source://fixture",
        plan_ref=PlanRef(lesson_plan_revision=1, lesson_plan_digest="d"),
        diagnoses=[],
        generated_at=ts,
        irene_budget_ms=0,
    )


_BUILDERS = [
    ("LessonPlan.updated_at", _build_lesson_plan),
    ("ScopeDecision.locked_at", _build_scope_decision_locked_at),
    ("ScopeDecisionTransition.timestamp", _build_scope_decision_transition),
    ("EventEnvelope.timestamp", _build_event_envelope),
    ("FitReport.generated_at", _build_fit_report),
]


@pytest.mark.parametrize("label,builder", _BUILDERS, ids=[b[0] for b in _BUILDERS])
def test_naive_datetime_rejected(label: str, builder) -> None:
    naive = datetime(2026, 1, 1, 12, 0, 0)
    assert naive.tzinfo is None
    with pytest.raises(ValidationError) as exc:
        builder(naive)
    assert "timezone-aware" in str(exc.value)


@pytest.mark.parametrize("label,builder", _BUILDERS, ids=[b[0] for b in _BUILDERS])
def test_utc_datetime_accepted(label: str, builder) -> None:
    aware = datetime.now(tz=UTC)
    model = builder(aware)
    assert model is not None


@pytest.mark.parametrize("label,builder", _BUILDERS, ids=[b[0] for b in _BUILDERS])
def test_non_utc_timezone_accepted(label: str, builder) -> None:
    """Design choice: any timezone-aware datetime is accepted, not just UTC."""
    aware_non_utc = datetime(2026, 1, 1, 12, 0, 0, tzinfo=_NON_UTC_TZ)
    assert aware_non_utc.tzinfo is not None
    model = builder(aware_non_utc)
    assert model is not None
