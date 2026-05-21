"""Story 32-1 — workflow runner insertion and baton handoff tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision
from app.marcus.orchestrator.workflow_runner import (
    Step4AWorkflowResult,
    insert_between,
    route_step_04_gate_to_step_05,
)
from scripts.utilities.run_hud import PIPELINE_STEPS


def _make_plan() -> LessonPlan:
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


def _decision(scope: str = "in-scope") -> ScopeDecision:
    return ScopeDecision(
        state="ratified",
        scope=scope,  # type: ignore[arg-type]
        proposed_by="operator",
        ratified_by="maya",
    )


def test_insert_between_places_stage_between_04_and_05() -> None:
    sequence = ("01", "02", "03", "04", "04.5", "05", "06")
    updated = insert_between("04", "05", "04A", sequence)
    assert updated.index("04") < updated.index("04A") < updated.index("05")


def test_insert_between_is_idempotent_with_existing_04a() -> None:
    sequence = ("01", "02", "03", "04", "04A", "05", "06")
    updated = insert_between("04", "05", "04A", sequence)
    assert updated.count("04A") == 1


def test_insert_between_rejects_missing_required_steps() -> None:
    with pytest.raises(ValueError, match="missing required step '04'"):
        insert_between("04", "05", "04A", ("01", "02", "05"))
    with pytest.raises(ValueError, match="missing required step '05'"):
        insert_between("04", "05", "04A", ("01", "02", "04"))


def test_route_step_04_to_05_runs_4a_and_returns_handoff(tmp_path: Path) -> None:
    plan = _make_plan()
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")

    def intake(_state, _unit_id):
        return _decision("in-scope"), "ratified"

    result = route_step_04_gate_to_step_05(
        plan,
        intake_callable=intake,
        log=log,
    )
    assert isinstance(result, Step4AWorkflowResult)
    assert result.locked_plan.revision >= 1
    assert result.handoff.step_from == "04A"
    assert result.handoff.step_to == "05"
    assert result.handoff.lesson_plan_revision == result.locked_plan.revision
    assert result.handoff.lesson_plan_digest == result.locked_plan.digest


def test_hud_pipeline_contains_4a_between_04x_and_05() -> None:
    ids = [step["id"] for step in PIPELINE_STEPS]
    assert "04A" in ids
    idx_04 = ids.index("04")
    idx_05 = ids.index("05")
    idx_4a = ids.index("04A")
    assert idx_04 < idx_4a < idx_05


def test_route_rejects_empty_packet_plan() -> None:
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )

    def intake(_state, _unit_id):
        return _decision("in-scope"), "ratified"

    with pytest.raises(ValueError, match="at least one plan unit"):
        route_step_04_gate_to_step_05(plan, intake_callable=intake)

