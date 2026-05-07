"""Step 06 plan-lock fanout consumer boundary (Story 30-4)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.lesson_plan.log import LessonPlanLog, assert_plan_fresh


class Step06PlanLockFanoutEnvelope(BaseModel):
    """Top-level plan-ref envelope consumed at step 06."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)
    step_id: Literal["06"] = "06"


def consume(
    envelope: Step06PlanLockFanoutEnvelope | dict[str, Any],
    *,
    log: LessonPlanLog,
) -> Step06PlanLockFanoutEnvelope:
    """Validate freshness before step-06 consumer logic executes."""
    parsed = (
        envelope
        if isinstance(envelope, Step06PlanLockFanoutEnvelope)
        else Step06PlanLockFanoutEnvelope.model_validate(envelope)
    )
    assert_plan_fresh(parsed, log=log)
    return parsed

