"""State pins for generated specialist kira."""

from __future__ import annotations

import json
from typing import ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class KiraEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "kira"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> KiraEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for kira envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for kira envelope")
        return self


class KiraReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "kira"
    motion_asset_path: str | None = Field(
        default=None,
        description="Optional MP4 path produced by Kling dispatch (Storyboard B additive field).",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> KiraReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for kira return"
            )
        return self


__all__ = ["KiraEnvelope", "KiraReturn"]
