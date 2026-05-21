"""AC-T.4 — `scope_decision_transition` event-shape test.

Validates the event primitive: required fields present; `from_state` never
`"locked"`; `to_state` valid; `rationale_snapshot` verbatim through multi-line
/ unicode / embedded quotes / whitespace (R1 ruling amendment 16 surface).

Also exercises the two-level actor model per R2 rider S-4 and the
to_internal_actor helper mapping.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.events import ScopeDecisionTransition, to_internal_actor


def _build_transition(**overrides) -> ScopeDecisionTransition:
    base = dict(
        unit_id="gagne-event-3",
        plan_revision=1,
        from_state="proposed",
        to_state="ratified",
        from_scope="in-scope",
        to_scope="in-scope",
        actor="operator",
        _internal_actor="maya",
        timestamp=datetime.now(tz=UTC),
        rationale_snapshot="revisit prior learning",
    )
    base.update(overrides)
    return ScopeDecisionTransition(**base)


def test_transition_required_fields_present() -> None:
    tr = _build_transition()
    dumped = tr.model_dump()
    for f in (
        "event_type",
        "unit_id",
        "plan_revision",
        "from_state",
        "to_state",
        "to_scope",
        "actor",
        "timestamp",
        "rationale_snapshot",
    ):
        assert f in dumped


def test_transition_from_state_cannot_be_locked() -> None:
    with pytest.raises(ValidationError):
        _build_transition(from_state="locked")


def test_transition_public_actor_is_system_or_operator() -> None:
    tr_system = _build_transition(actor="system", _internal_actor="marcus")
    tr_op = _build_transition(actor="operator", _internal_actor="maya")
    assert tr_system.actor == "system"
    assert tr_op.actor == "operator"


def test_transition_internal_actor_takes_five_values() -> None:
    for internal in (
        "marcus",
        "marcus-intake",
        "marcus-orchestrator",
        "irene",
        "maya",
    ):
        tr = _build_transition(_internal_actor=internal, actor="system")
        assert tr.internal_actor == internal


@pytest.mark.parametrize(
    "rationale",
    [
        "multi\nline\nrationale",
        'rationale with "embedded quotes"',
        "rationale with 🔬 emoji + unicode café",
        "  leading and trailing whitespace  ",
    ],
)
def test_rationale_snapshot_preserved_verbatim(rationale: str) -> None:
    tr = _build_transition(rationale_snapshot=rationale)
    dumped = tr.model_dump_json()
    restored = ScopeDecisionTransition.model_validate_json(dumped)
    assert restored.rationale_snapshot == rationale


def test_to_internal_actor_mapping() -> None:
    assert to_internal_actor("operator") == "maya"
    assert to_internal_actor("system") == "marcus"
    assert to_internal_actor("system", "irene") == "irene"
    assert to_internal_actor("system", "marcus-intake") == "marcus-intake"
    assert to_internal_actor("system", "marcus-orchestrator") == "marcus-orchestrator"
