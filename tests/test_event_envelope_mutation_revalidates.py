"""MF-1 + MF-2 — ``validate_assignment=True`` enforces re-validation on mutation.

Ensures that once an :class:`EventEnvelope` or
:class:`ScopeDecisionTransition` is constructed, subsequent field mutations
are re-validated against the field type + constraints. Any bypass attempt
(invalid regex on ``event_type``, negative ``plan_revision``, bad state
literal) must raise :class:`pydantic.ValidationError`.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.events import EventEnvelope, ScopeDecisionTransition

# ---------------------------------------------------------------------------
# EventEnvelope
# ---------------------------------------------------------------------------


def _envelope() -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=1,
        event_type="gagne-event-1",
    )


def test_event_envelope_event_type_mutation_revalidates_regex() -> None:
    env = _envelope()
    with pytest.raises(ValidationError):
        env.event_type = "Has Caps"


def test_event_envelope_event_type_mutation_revalidates_with_spaces() -> None:
    env = _envelope()
    with pytest.raises(ValidationError):
        env.event_type = "has spaces"


def test_event_envelope_plan_revision_mutation_rejects_negative() -> None:
    env = _envelope()
    with pytest.raises(ValidationError):
        env.plan_revision = -1


def test_event_envelope_event_id_mutation_rejects_non_uuid() -> None:
    env = _envelope()
    with pytest.raises(ValidationError):
        env.event_id = "not-a-uuid"


# ---------------------------------------------------------------------------
# ScopeDecisionTransition
# ---------------------------------------------------------------------------


def _transition() -> ScopeDecisionTransition:
    return ScopeDecisionTransition(
        unit_id="gagne-event-1",
        plan_revision=2,
        from_state="proposed",
        to_state="ratified",
        to_scope="in-scope",
        actor="operator",
        timestamp=datetime.now(tz=UTC),
    )


def test_scope_decision_transition_from_state_mutation_rejects_locked() -> None:
    t = _transition()
    # Literal type does not permit "locked" on from_state.
    with pytest.raises(ValidationError):
        t.from_state = "locked"  # type: ignore[assignment]


def test_scope_decision_transition_plan_revision_mutation_rejects_negative() -> None:
    t = _transition()
    with pytest.raises(ValidationError):
        t.plan_revision = -1
