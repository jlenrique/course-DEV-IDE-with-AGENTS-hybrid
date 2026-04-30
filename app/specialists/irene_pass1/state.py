"""State pins for Irene Pass-1 lesson-plan coauthoring."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class IrenePass1Envelope(SpecialistEnvelope):
    """Pass-1 lesson-plan envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "irene_pass1"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> IrenePass1Envelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                "specialist_id must equal 'irene_pass1' for Irene Pass-1 envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for Irene Pass-1 envelope")
        return self


class IrenePass1Return(SpecialistReturn):
    """Pass-1 return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "irene_pass1"
    lesson_plan: dict[str, Any] = Field(default_factory=dict)
    locked_scope: dict[str, Any] | None = None
    learning_events: list[dict[str, Any]] = Field(default_factory=list)
    artifact_path: str | None = None

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> IrenePass1Return:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                "specialist_id must equal 'irene_pass1' for Irene Pass-1 return"
            )
        return self


__all__ = ["IrenePass1Envelope", "IrenePass1Return"]
