"""State pins for generated specialist motion_planner."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class MotionPlannerEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "motion_planner"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> MotionPlannerEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for motion_planner envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for motion_planner envelope")
        return self


class MotionPlannerReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "motion_planner"
    motion_plan: dict[str, Any] = Field(
        default_factory=dict,
        description="Deterministic per-slide motion plan projected into kira's consumed shape.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> MotionPlannerReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for motion_planner return"
            )
        return self


__all__ = ["MotionPlannerEnvelope", "MotionPlannerReturn"]
