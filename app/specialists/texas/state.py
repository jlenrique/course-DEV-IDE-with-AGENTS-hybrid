"""State pins for generated specialist texas."""

from __future__ import annotations

import json
from typing import ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class TexasEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "texas"
    schema_version: Literal["1.0"] = Field(default="1.0")
    payload_out: TexasReturn | None = Field(
        default=None,
        description="Texas-specialized return payload envelope slot.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> TexasEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for texas envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for texas envelope")
        return self


class TexasReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "texas"
    bundle_reference: str | None = Field(
        default=None,
        description="Path to a six-artifact Texas retrieval bundle.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> TexasReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for texas return"
            )
        return self


__all__ = ["TexasEnvelope", "TexasReturn"]
