"""Story 30-4 — plan-lock fanout tests."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from app.marcus.facade import Facade
from app.marcus.lesson_plan.event_type_registry import EVENT_FANOUT_ENVELOPE_EMITTED
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog, PlanLockedPayload, StalePlanRefError
from app.marcus.lesson_plan.schema import (
    IdentifiedGap,
    LearningModel,
    LessonPlan,
    PlanUnit,
    ScopeDecision,
)
from app.marcus.lesson_plan.step_05_pre_packet_handoff import consume as consume_step_05
from app.marcus.lesson_plan.step_06_plan_lock_fanout import consume as consume_step_06
from app.marcus.lesson_plan.step_07_gap_dispatch import consume as consume_step_07
from app.marcus.orchestrator.dispatch import dispatch_orchestrator_event
from app.marcus.orchestrator.fanout import emit_plan_lock_fanout


def _decision(scope: str) -> ScopeDecision:
    return ScopeDecision(
        state="ratified",
        scope=scope,  # type: ignore[arg-type]
        proposed_by="operator",
        ratified_by="maya",
    )


def _locked_plan(include_gap: bool = True) -> LessonPlan:
    gaps = []
    if include_gap:
        gaps = [
            IdentifiedGap(
                    gap_id="gap-1",
                description="Need one concrete classroom example",
                    suggested_posture="embellish",
            )
        ]
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id="u1",
                event_type="gagne-event-1",
                source_fitness_diagnosis="diagnosis",
                scope_decision=_decision("in-scope"),
                weather_band="green",
                rationale="ratified",
                gaps=gaps,
            ),
            PlanUnit(
                unit_id="u2",
                event_type="gagne-event-2",
                source_fitness_diagnosis="diagnosis",
                scope_decision=_decision("out-of-scope"),
                weather_band="green",
                rationale="ratified",
            ),
        ],
        revision=3,
        updated_at=datetime.now(tz=UTC),
        digest="digest-locked-plan",
    )


def _dispatch(tmp_path: Path) -> tuple[Any, LessonPlanLog]:
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    return partial(dispatch_orchestrator_event, log=log), log


def _append_locked(
    log: LessonPlanLog,
    revision: int = 3,
    digest: str = "digest-locked-plan",
) -> None:
    dispatch = partial(dispatch_orchestrator_event, log=log)
    dispatch(
        envelope=EventEnvelope(
            timestamp=datetime.now(tz=UTC),
            plan_revision=revision,
            event_type="plan.locked",
            payload=PlanLockedPayload(lesson_plan_digest=digest).model_dump(mode="json"),
        )
    )


class _FakeBridge:
    def process_plan_locked(self, lesson_plan: dict[str, Any]) -> list[dict[str, Any]]:
        units = lesson_plan.get("units", [])
        if not units:
            return []
        return [{"status": "success", "posture": "embellish"}]


class _BadBridge:
    def process_plan_locked(self, _lesson_plan: dict[str, Any]) -> object:
        return {"not": "a-sequence"}


def test_emit_plan_lock_fanout_emits_step_05_and_06(tmp_path: Path) -> None:
    dispatch, log = _dispatch(tmp_path)
    result = emit_plan_lock_fanout(_locked_plan(include_gap=False), dispatch=dispatch)

    assert [e.step_id for e in result.envelopes] == ["05", "06"]
    events = list(log.read_events())
    assert len(events) == 2
    assert all(e.event_type == EVENT_FANOUT_ENVELOPE_EMITTED for e in events)


def test_emit_plan_lock_fanout_emits_gap_envelope_for_in_scope_gaps(tmp_path: Path) -> None:
    dispatch, log = _dispatch(tmp_path)
    result = emit_plan_lock_fanout(_locked_plan(include_gap=True), dispatch=dispatch)

    step_ids = [e.step_id for e in result.envelopes]
    assert step_ids == ["05", "06", "07"]
    gap = result.envelopes[-1]
    assert gap.unit_id == "u1"
    assert gap.gap_type == "enrichment"
    assert len(list(log.read_events())) == 3


def test_emit_plan_lock_fanout_bridge_integration_populates_bridge_status(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    result = emit_plan_lock_fanout(
        _locked_plan(include_gap=True),
        dispatch=dispatch,
        bridge=_FakeBridge(),
    )
    assert result.bridge_results[0]["status"] == "success"
    assert result.envelopes[-1].bridge_status == "success"


def test_emit_plan_lock_fanout_computes_missing_digest(tmp_path: Path) -> None:
    dispatch, _ = _dispatch(tmp_path)
    plan = _locked_plan(include_gap=False).model_copy(update={"digest": ""})

    result = emit_plan_lock_fanout(plan, dispatch=dispatch)
    assert result.envelopes[0].lesson_plan_digest != ""


def test_step_05_consume_accepts_fresh_envelope(tmp_path: Path) -> None:
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    _append_locked(log)

    envelope = consume_step_05(
        {"lesson_plan_revision": 3, "lesson_plan_digest": "digest-locked-plan", "step_id": "05"},
        log=log,
    )
    assert envelope.step_id == "05"


def test_step_06_consume_rejects_stale_envelope(tmp_path: Path) -> None:
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    _append_locked(log)

    with pytest.raises(StalePlanRefError):
        consume_step_06(
            {
                "lesson_plan_revision": 2,
                "lesson_plan_digest": "digest-locked-plan",
                "step_id": "06",
            },
            log=log,
        )


def test_step_07_consume_accepts_fresh_gap_dispatch_envelope(tmp_path: Path) -> None:
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    _append_locked(log)

    envelope = consume_step_07(
        {
            "lesson_plan_revision": 3,
            "lesson_plan_digest": "digest-locked-plan",
            "step_id": "07",
            "unit_id": "u1",
            "gap_type": "enrichment",
        },
        log=log,
    )
    assert envelope.unit_id == "u1"


def test_step_05_consume_rejects_wrong_step_id(tmp_path: Path) -> None:
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    _append_locked(log)

    with pytest.raises(ValidationError):
        consume_step_05(
            {
                "lesson_plan_revision": 3,
                "lesson_plan_digest": "digest-locked-plan",
                "step_id": "06",
            },
            log=log,
        )


def test_emit_plan_lock_fanout_handles_malformed_bridge_result(tmp_path: Path) -> None:
    dispatch, log = _dispatch(tmp_path)
    result = emit_plan_lock_fanout(
        _locked_plan(include_gap=True),
        dispatch=dispatch,
        bridge=_BadBridge(),
    )
    assert len(result.bridge_results) == 0
    assert len(list(log.read_events())) == 3


def test_facade_run_4a_emits_fanout_events_after_lock(tmp_path: Path) -> None:
    facade = Facade()
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")

    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id="u1",
                event_type="gagne-event-1",
                source_fitness_diagnosis="diagnosis",
                weather_band="green",
                rationale="",
            )
        ],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )

    def intake(_state: Any, _unit_id: str) -> tuple[ScopeDecision, str]:
        return _decision("in-scope"), "ratified"

    facade.run_4a(plan, intake_callable=intake, log=log, tracy_bridge=_FakeBridge())
    event_types = [event.event_type for event in log.read_events()]
    assert "plan.locked" in event_types
    assert event_types.count(EVENT_FANOUT_ENVELOPE_EMITTED) >= 2

