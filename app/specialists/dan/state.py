"""State pins for generated specialist dan."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class DanEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "dan"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> DanEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for dan envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for dan envelope")
        return self


class DanReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "dan"
    dan_aux: dict[str, Any] | None = Field(
        default=None,
        description="Dan advisory creative-director aux contributions for G1/G1A/G2.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> DanReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for dan return"
            )
        return self


__all__ = ["DanEnvelope", "DanReturn"]
