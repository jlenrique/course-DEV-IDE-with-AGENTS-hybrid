"""AC-C.2 — schema_version root field presence test.

Every emitted lesson_plan artifact MUST carry ``schema_version: "1.0"`` at the
root (pattern from 27-0 AC-T.1 equivalent on the retrieval side).
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.marcus.lesson_plan.schema import (
    SCHEMA_VERSION,
    LearningModel,
    LessonPlan,
)


def test_schema_version_constant_is_1_0() -> None:
    assert SCHEMA_VERSION == "1.0"


def test_lesson_plan_default_carries_schema_version_on_model_dump() -> None:
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )
    dumped = plan.model_dump()
    assert dumped["schema_version"] == SCHEMA_VERSION


def test_lesson_plan_default_carries_schema_version_on_json() -> None:
    plan = LessonPlan(
        learning_model=LearningModel(id="gagne-9", version=1),
        plan_units=[],
        revision=0,
        updated_at=datetime.now(tz=UTC),
    )
    js = plan.model_dump_json()
    assert '"schema_version":"1.0"' in js
