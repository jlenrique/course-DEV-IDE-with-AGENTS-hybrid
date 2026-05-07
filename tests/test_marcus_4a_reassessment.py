"""Story 30-3b — dial tuning + sync reassessment tests."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import Dials, LearningModel, LessonPlan, PlanUnit, ScopeDecision
from app.marcus.orchestrator.dispatch import dispatch_orchestrator_event
from app.marcus.orchestrator.loop import (
    FourAState,
    PlanAlreadyLockedError,
    sync_reassess_with_irene,
    tune_unit_dials,
)


def _make_plan(scope: str = "in-scope") -> LessonPlan:
    """Build a minimal plan with one ratified unit."""
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id="u1",
                event_type="gagne-event-1",
                source_fitness_diagnosis="diagnosis",
                scope_decision=ScopeDecision(
                    state="ratified",
                    scope=scope,  # type: ignore[arg-type]
                    proposed_by="operator",
                    ratified_by="maya",
                ),
                weather_band="green",
                rationale="keep this tight",
            )
        ],
        revision=1,
        updated_at=datetime.now(tz=UTC),
    )


def _dispatch(tmp_path: Path):
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    return partial(dispatch_orchestrator_event, log=log), log


class _FakeClock:
    def __init__(self, values: list[float]) -> None:
        self._values = values
        self._idx = 0

    def __call__(self) -> float:
        value = self._values[self._idx]
        self._idx = min(self._idx + 1, len(self._values) - 1)
        return value


def test_tune_unit_dials_updates_and_emits_dials_tuned(tmp_path: Path) -> None:
    """G6-Opus 30-3b sweep (party-mode 2026-04-19): dial tuning emits the
    dedicated ``dials.tuned`` event, NOT the conflated ``scope_decision.set``."""
    dispatch, log = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"))

    updated = tune_unit_dials(
        state,
        "u1",
        enrichment=0.6,
        corroboration=0.4,
        dispatch=dispatch,
    )

    assert updated.draft_plan.plan_units[0].dials == Dials(enrichment=0.6, corroboration=0.4)
    events = list(log.read_events())
    assert len(events) == 1
    assert events[0].event_type == "dials.tuned"
    assert events[0].payload["dials"] == {"enrichment": 0.6, "corroboration": 0.4}


def test_tune_unit_dials_updates_delegated_unit(tmp_path: Path) -> None:
    dispatch, log = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("delegated"))

    updated = tune_unit_dials(
        state,
        "u1",
        enrichment=0.3,
        corroboration=0.7,
        dispatch=dispatch,
    )

    assert updated.draft_plan.plan_units[0].dials == Dials(enrichment=0.3, corroboration=0.7)
    events = list(log.read_events())
    assert len(events) == 1
    assert events[0].event_type == "dials.tuned"


def test_tune_unit_dials_rejects_out_of_scope_unit(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("out-of-scope"))
    with pytest.raises(ValueError, match="dials can only be tuned"):
        tune_unit_dials(
            state,
            "u1",
            enrichment=0.5,
            corroboration=0.5,
            dispatch=dispatch,
        )


def test_tune_unit_dials_rejects_locked_state(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"), locked=True, locked_revision=2)
    with pytest.raises(PlanAlreadyLockedError):
        tune_unit_dials(
            state,
            "u1",
            enrichment=0.2,
            corroboration=0.1,
            dispatch=dispatch,
        )


def test_sync_reassess_applies_recommended_scope_and_emits_transition(tmp_path: Path) -> None:
    dispatch, log = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"))

    result = sync_reassess_with_irene(
        state,
        source_ref="unit-test",
        dispatch=dispatch,
        prior_declined_rationales={"u1": "carry forward"},
    )

    updated_scope = result.updated_state.draft_plan.plan_units[0].scope_decision
    assert updated_scope is not None
    assert updated_scope.scope == "out-of-scope"
    events = list(log.read_events())
    assert len(events) == 1
    assert events[0].event_type == "scope_decision_transition"


def test_sync_reassess_sets_fallback_when_over_p95(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"))
    clock = _FakeClock([0.0, 31.5, 31.6, 31.7, 31.8])

    result = sync_reassess_with_irene(
        state,
        source_ref="unit-test",
        dispatch=dispatch,
        time_source=clock,
    )

    assert result.fallback_used is True
    assert "summary reassessment" in result.voice_message


def test_sync_reassess_voice_continuity_three_iterations(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"))
    messages: list[str] = []

    for _ in range(3):
        result = sync_reassess_with_irene(
            state,
            source_ref="unit-test",
            dispatch=dispatch,
        )
        messages.append(result.voice_message)
        state = result.updated_state

    assert len(set(messages)) == 3
    assert all(message.startswith("I ") for message in messages)
    assert all(message.endswith("?") for message in messages)


def test_sync_reassess_appends_tracy_narration(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"))

    result = sync_reassess_with_irene(
        state,
        source_ref="unit-test",
        dispatch=dispatch,
        tracy_result={"status": "success", "posture": "embellish"},
    )

    assert "I found a detail that enriches this section" in result.voice_message


def test_sync_reassess_iteration_counter_increments(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"))

    first = sync_reassess_with_irene(
        state,
        source_ref="unit-test",
        dispatch=dispatch,
    )
    second = sync_reassess_with_irene(
        first.updated_state,
        source_ref="unit-test",
        dispatch=dispatch,
    )

    assert first.iteration_index == 1
    assert second.iteration_index == 2


def test_sync_reassess_rejects_locked_state(tmp_path: Path) -> None:
    dispatch, log = _dispatch(tmp_path)
    state = FourAState(draft_plan=_make_plan("in-scope"), locked=True, locked_revision=3)

    with pytest.raises(PlanAlreadyLockedError):
        sync_reassess_with_irene(
            state,
            source_ref="unit-test",
            dispatch=dispatch,
        )

    assert list(log.read_events()) == []
