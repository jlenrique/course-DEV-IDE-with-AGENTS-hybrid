"""State pins for generated specialist compositor."""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from app.models.state.specialist_envelope import SpecialistEnvelope
from app.models.state.specialist_return import SpecialistReturn


class CompositorEnvelope(SpecialistEnvelope):
    """Generated envelope with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "compositor"
    schema_version: Literal["1.0"] = Field(default="1.0")

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> CompositorEnvelope:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError("specialist_id must equal 'compositor'")
        return self


class CompositorReturn(SpecialistReturn):
    """Generated return payload with specialist-id pin."""

    _SPECIALIST_ID: ClassVar[str] = "compositor"
    assembly_output: dict[str, Any] | None = Field(
        default=None,
        description="Deterministic assembly-bundle output and guide hashes.",
    )

    @model_validator(mode="after")
    def _pin_specialist_id(self) -> CompositorReturn:
        if self.specialist_id != self._SPECIALIST_ID:
            raise ValueError("specialist_id must equal 'compositor'")
        return self


__all__ = ["CompositorEnvelope", "CompositorReturn"]
