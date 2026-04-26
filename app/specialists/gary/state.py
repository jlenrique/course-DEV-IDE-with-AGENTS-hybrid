"""State pins for generated specialist gary."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class GaryEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "gary"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> GaryEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for gary envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for gary envelope")
        return self


class GaryReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "gary"
    gary_slide_output: list[dict[str, Any]] | None = Field(
        default=None,
        description="Per-card slide-output array per Gary SKILL.md outbound contract.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> GaryReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for gary return"
            )
        return self


__all__ = ["GaryEnvelope", "GaryReturn"]
