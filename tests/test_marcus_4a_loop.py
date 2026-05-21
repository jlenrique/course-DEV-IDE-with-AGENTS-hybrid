"""Story 30-3a — `FourALoop` end-to-end tests.

Covers:
* AC-T.2 happy path
* AC-T.4 plan-lock fires only when all units ratified
* AC-T.5 plan-lock invariance
* AC-T.10 plan_unit.created ordering
* AC-T.11 prior-declined-rationale carry-forward
"""

from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision
from app.marcus.orchestrator.dispatch import dispatch_orchestrator_event
from app.marcus.orchestrator.loop import (
    FourALoop,
    FourAState,
    PlanAlreadyLockedError,
    intake_scope_decision,
    trigger_plan_lock_if_ready,
)

_GAGNE_EVENTS = (
    "gain_attention",
    "inform_objectives",
    "stimulate_recall",
    "present_content",
    "guide_learning",
    "elicit_performance",
    "provide_feedback",
    "assess_performance",
    "enhance_retention",
)


def _make_plan(unit_ids: list[str]) -> LessonPlan:
    """Build a minimal draft :class:`LessonPlan` with N unratified units."""
    plan_units = [
        PlanUnit(
            unit_id=uid,
            event_type=_GAGNE_EVENTS[idx % len(_GAGNE_EVENTS)],
            source_fitness_diagnosis=f"diagnosis for {uid}",
            weather_band="green",
            rationale="",
        )
        for idx, uid in enumerate(unit_ids)
    ]
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=plan_units,
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )


def _make_decision(scope: str) -> ScopeDecision:
    """Build a ratified :class:`ScopeDecision` for the given scope."""
    return ScopeDecision(
        state="ratified",
        scope=scope,  # type: ignore[arg-type]
        proposed_by="operator",
        ratified_by="maya",
    )


def _tmp_log_dispatch(tmp_path: Path):
    """Return a (dispatch, log) pair bound to a tmp_path log."""
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    dispatch = partial(dispatch_orchestrator_event, log=log)
    return dispatch, log


# ---------------------------------------------------------------------------
# AC-T.2 — 4A loop happy path
# ---------------------------------------------------------------------------


def test_four_a_loop_happy_path(tmp_path: Path) -> None:
    """AC-T.2 — 3-unit plan → fully ratify → plan.locked + locked return."""
    dispatch, log = _tmp_log_dispatch(tmp_path)
    plan = _make_plan(["u1", "u2", "u3"])
    decisions = iter(
        [
            (_make_decision("in-scope"), "top priority"),
            (_make_decision("delegated"), "hand to specialist"),
            (_make_decision("out-of-scope"), "not this quarter"),
        ]
    )

    def intake(state: FourAState, unit_id: str):
        return next(decisions)

    loop = FourALoop(dispatch=dispatch)
    locked = loop.run_4a(plan, intake_callable=intake)

    assert locked.revision == 1
    assert locked.digest != ""

    # Exactly 3 plan_unit.created + 3 scope_decision.set + 1 plan.locked = 7.
    events = list(log.read_events())
    event_types = [e.event_type for e in events]
    assert event_types.count("plan_unit.created") == 3
    assert event_types.count("scope_decision.set") == 3
    assert event_types.count("plan.locked") == 1
    assert len(events) == 7


# ---------------------------------------------------------------------------
# AC-T.4 — plan-lock fires only when all units ratified
# ---------------------------------------------------------------------------


def test_plan_lock_does_not_fire_with_pending_units(tmp_path: Path) -> None:
    """AC-T.4 — partial ratification leaves the state unlocked."""
    dispatch, log = _tmp_log_dispatch(tmp_path)
    plan = _make_plan(["u1", "u2"])
    state = FourAState(draft_plan=plan)
    state = intake_scope_decision(state, "u1", _make_decision("in-scope"), "go", dispatch=dispatch)
    # u2 still pending.
    result = trigger_plan_lock_if_ready(state, dispatch=dispatch)
    assert result.locked is False
    # No plan.locked event emitted.
    assert [e.event_type for e in log.read_events()].count("plan.locked") == 0

    # Now ratify u2 and retry.
    result = intake_scope_decision(
        result, "u2", _make_decision("in-scope"), "go too", dispatch=dispatch
    )
    result = trigger_plan_lock_if_ready(result, dispatch=dispatch)
    assert result.locked is True
    assert [e.event_type for e in log.read_events()].count("plan.locked") == 1


# ---------------------------------------------------------------------------
# AC-T.5 — plan-lock invariance
# ---------------------------------------------------------------------------


def test_plan_lock_invariance_raises_on_post_lock_intake(tmp_path: Path) -> None:
    """AC-T.5 — intake after lock raises PlanAlreadyLockedError with no emission."""
    dispatch, log = _tmp_log_dispatch(tmp_path)
    plan = _make_plan(["u1"])
    state = FourAState(draft_plan=plan)
    state = intake_scope_decision(
        state, "u1", _make_decision("in-scope"), "ratify", dispatch=dispatch
    )
    state = trigger_plan_lock_if_ready(state, dispatch=dispatch)
    assert state.locked

    pre_event_count = len(list(log.read_events()))

    with pytest.raises(PlanAlreadyLockedError) as exc_info:
        intake_scope_decision(
            state, "u1", _make_decision("out-of-scope"), "nope", dispatch=dispatch
        )
    # Maya-safe str — no hyphenated internal-routing tokens.
    assert "intake" not in str(exc_info.value).lower()
    assert "orchestrator" not in str(exc_info.value).lower()
    # No new events emitted on the locked path.
    assert len(list(log.read_events())) == pre_event_count


# ---------------------------------------------------------------------------
# AC-T.10 — plan_unit.created ordering
# ---------------------------------------------------------------------------


def test_plan_unit_created_precedes_scope_decision_set(tmp_path: Path) -> None:
    """AC-T.10 — all plan_unit.created events precede the first scope_decision.set."""
    dispatch, log = _tmp_log_dispatch(tmp_path)
    plan = _make_plan(["u1", "u2", "u3"])
    decisions = iter(
        [
            (_make_decision("in-scope"), "a"),
            (_make_decision("in-scope"), "b"),
            (_make_decision("in-scope"), "c"),
        ]
    )

    def intake(state: FourAState, unit_id: str):
        return next(decisions)

    loop = FourALoop(dispatch=dispatch)
    loop.run_4a(plan, intake_callable=intake)

    events = list(log.read_events())
    first_scope_idx = next(i for i, e in enumerate(events) if e.event_type == "scope_decision.set")
    # All plan_unit.created events are at indices 0..first_scope_idx-1.
    assert all(events[i].event_type == "plan_unit.created" for i in range(first_scope_idx))
    assert first_scope_idx == 3  # exactly 3 plan_unit.created before first decision.


# ---------------------------------------------------------------------------
# AC-T.11 — prior-declined-rationale carry-forward (R1-15)
# ---------------------------------------------------------------------------


def test_prior_declined_rationale_carries_forward(tmp_path: Path) -> None:
    """AC-T.11 — unit named in prior-declines is pre-ratified; intake not called."""
    dispatch, log = _tmp_log_dispatch(tmp_path)
    plan = _make_plan(["u1", "u2", "u3"])

    calls: list[str] = []

    def intake(state: FourAState, unit_id: str):
        calls.append(unit_id)
        return _make_decision("in-scope"), f"rationale-for-{unit_id}"

    loop = FourALoop(dispatch=dispatch)
    locked = loop.run_4a(
        plan,
        intake_callable=intake,
        prior_declined_rationales=[("u2", "previously declined — no change")],
    )

    # u2 was NOT prompted.
    assert calls == ["u1", "u3"]

    # u2 in the locked plan carries the verbatim prior rationale + out-of-scope.
    u2_unit = next(u for u in locked.plan_units if u.unit_id == "u2")
    assert u2_unit.rationale == "previously declined — no change"
    assert u2_unit.scope_decision is not None
    assert u2_unit.scope_decision.scope == "out-of-scope"

    # Log contains 3 plan_unit.created + 3 scope_decision.set + 1 plan.locked.
    events = list(log.read_events())
    assert [e.event_type for e in events].count("scope_decision.set") == 3
