"""Story 30-3a — Facade.run_4a Maya-surface test.

AC-T.8 — `Facade.greet` is gone; `Facade.run_4a` is the real conversation
entrypoint. Smoke: invoke with minimal packet + test-stub intake_callable +
tmp_path log → get a locked LessonPlan. Confirms facade wiring without
leaking internal-routing tokens.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.marcus.facade import Facade, get_facade, reset_facade
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.lesson_plan.schema import LearningModel, LessonPlan, PlanUnit, ScopeDecision


def _single_unit_plan() -> LessonPlan:
    return LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[
            PlanUnit(
                unit_id="u1",
                event_type="gain_attention",
                source_fitness_diagnosis="diag",
                weather_band="green",
                rationale="",
            )
        ],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )


def test_facade_run_4a_replaces_greet_and_returns_locked_plan(tmp_path: Path) -> None:
    """AC-T.8 — run_4a exists; greet is gone; runs a minimal loop to lock."""
    # Structural: greet is gone, run_4a is present.
    assert not hasattr(Facade, "greet"), (
        "30-3a removes Facade.greet; run_4a is the replacement."
    )
    assert hasattr(Facade, "run_4a")

    reset_facade()
    try:
        facade = get_facade()
        log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")

        def intake(state, unit_id):  # noqa: ARG001 — stub signature match
            return (
                ScopeDecision(
                    state="ratified",
                    scope="in-scope",
                    proposed_by="operator",
                    ratified_by="maya",
                ),
                "go",
            )

        locked = facade.run_4a(
            _single_unit_plan(),
            intake_callable=intake,
            log=log,
        )

        assert locked.revision == 1
        assert locked.digest != ""
        assert "plan.locked" in [e.event_type for e in log.read_events()]

        # Maya-surface repr still renders one "Marcus".
        assert repr(facade) == "Marcus"
    finally:
        reset_facade()
