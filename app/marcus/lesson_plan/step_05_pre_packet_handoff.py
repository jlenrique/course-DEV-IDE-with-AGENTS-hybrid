"""Step 05 pre-packet handoff consumer boundary (Story 30-4)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.lesson_plan.log import LessonPlanLog, assert_plan_fresh


class Step05PrePacketEnvelope(BaseModel):
    """Top-level plan-ref envelope consumed at step 05."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)
    step_id: Literal["05"] = "05"


def consume(
    envelope: Step05PrePacketEnvelope | dict[str, Any],
    *,
    log: LessonPlanLog,
) -> Step05PrePacketEnvelope:
    """Validate freshness before step-05 consumer logic executes."""
    parsed = (
        envelope
        if isinstance(envelope, Step05PrePacketEnvelope)
        else Step05PrePacketEnvelope.model_validate(envelope)
    )
    assert_plan_fresh(parsed, log=log)
    return parsed

