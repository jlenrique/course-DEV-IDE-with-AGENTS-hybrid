"""State pins for generated specialist mira."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class MiraEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "mira"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> MiraEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for mira envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for mira envelope")
        return self


class MiraReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "mira"
    mira_prompt_pack: dict[str, Any] | None = Field(default=None)

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> MiraReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for mira return"
            )
        return self


__all__ = ["MiraEnvelope", "MiraReturn"]
