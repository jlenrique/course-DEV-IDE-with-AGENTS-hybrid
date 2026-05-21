"""Emitter-to-manifest reconciliation checks for Story 33-2."""

from __future__ import annotations

from datetime import UTC, datetime

from app.marcus.lesson_plan.event_type_registry import EVENT_PLAN_LOCKED, EVENT_PLAN_UNIT_CREATED
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision
from app.marcus.orchestrator.loop import FourALoop
from scripts.utilities.pipeline_manifest import load_manifest


def _seed_plan() -> LessonPlan:
    return LessonPlan(
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


def test_loop_py_emitter_pairs_reconcile_to_manifest() -> None:
    captured: list[EventEnvelope] = []

    def dispatch(envelope: EventEnvelope) -> None:
        captured.append(envelope)

    def intake(_state, _unit_id):
        return (
            ScopeDecision(
                state="ratified",
                scope="in-scope",
                proposed_by="operator",
                ratified_by="maya",
            ),
            "ratified",
        )

    loop = FourALoop(dispatch=dispatch)
    loop.run_4a(_seed_plan(), intake_callable=intake)

    event_to_step = {
        EVENT_PLAN_UNIT_CREATED: "04.5",
        EVENT_PLAN_LOCKED: "04.55",
    }
    emitted_pairs = {
        (event_to_step[event.event_type], event.event_type)
        for event in captured
        if event.event_type in event_to_step
    }

    manifest = load_manifest()
    manifest_pairs = {
        (step.id, event_type)
        for step in manifest.steps
        if step.learning_events.emits
        for event_type in step.learning_events.event_types
    }
    assert ("04.5", EVENT_PLAN_UNIT_CREATED) in emitted_pairs
    assert ("04.55", EVENT_PLAN_LOCKED) in emitted_pairs
    assert emitted_pairs.issubset(manifest_pairs)

