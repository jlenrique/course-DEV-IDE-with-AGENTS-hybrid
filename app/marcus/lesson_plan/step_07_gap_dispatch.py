"""Step 07 gap-dispatch consumer boundary (Story 30-4)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.marcus.lesson_plan.log import LessonPlanLog, assert_plan_fresh


class Step07GapDispatchEnvelope(BaseModel):
    """Top-level plan-ref envelope consumed at step 07 gap dispatch."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    lesson_plan_revision: int = Field(..., ge=0)
    lesson_plan_digest: str = Field(..., min_length=1)
    step_id: Literal["07"] = "07"
    unit_id: str = Field(..., min_length=1)
    gap_type: str = Field(..., min_length=1)
    bridge_status: str | None = None


def consume(
    envelope: Step07GapDispatchEnvelope | dict[str, Any],
    *,
    log: LessonPlanLog,
) -> Step07GapDispatchEnvelope:
    """Validate freshness before step-07 consumer logic executes."""
    parsed = (
        envelope
        if isinstance(envelope, Step07GapDispatchEnvelope)
        else Step07GapDispatchEnvelope.model_validate(envelope)
    )
    assert_plan_fresh(parsed, log=log)
    return parsed

