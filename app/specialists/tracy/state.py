"""State pins for generated specialist tracy."""

from __future__ import annotations

import json
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class TracyEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "tracy"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> TracyEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for tracy envelope"
            )
        payload_size = len(json.dumps(self.payload_in, sort_keys=True))
        if payload_size > 50_000:
            raise ValueError("payload_in exceeds 50KB cap for tracy envelope")
        return self


class TracyReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "tracy"
    tracy_manifest: dict[str, Any] | None = Field(
        default=None,
        description="Suggested resources manifest produced by Tracy.",
    )
    retrieval_intents: list[dict[str, Any]] | None = Field(
        default=None,
        description="Texas-compatible RetrievalIntent objects emitted by Tracy.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> TracyReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError(
                f"specialist_id must equal {self._SPECIALIST_ID!r} for tracy return"
            )
        return self


__all__ = ["TracyEnvelope", "TracyReturn"]
