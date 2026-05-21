"""Parity-contract transport declarations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

Transport = Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]
GateFamilyId = Literal["G0", "G1", "G2A", "G2C", "G3", "G4", "G5", "G6"]
GATE_FAMILY_IDS: frozenset[str] = frozenset(
    {"G0", "G1", "G2A", "G2C", "G3", "G4", "G5", "G6"}
)
_GATE_FAMILY_ADAPTER: TypeAdapter[GateFamilyId] = TypeAdapter(GateFamilyId)


class SurfaceTransportDeclaration(BaseModel):
    """Declared transport parity contract for one operator-facing surface."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    surface_id: str = Field(..., min_length=1)
    mandatory_transports: list[Transport] = Field(..., min_length=1)
    optional_transports: list[Transport] = Field(default_factory=list)
    alias_of: GateFamilyId | None = Field(default=None)

    @field_validator("alias_of", mode="before")
    @classmethod
    def _reject_unknown_alias_family(cls, value: object) -> object:
        if value is None:
            return None
        return _GATE_FAMILY_ADAPTER.validate_python(value)

    @model_validator(mode="after")
    def _validate_transport_sets(self) -> SurfaceTransportDeclaration:
        mandatory = set(self.mandatory_transports)
        optional = set(self.optional_transports)
        if len(mandatory) != len(self.mandatory_transports):
            raise ValueError("mandatory_transports must not contain duplicates")
        if len(optional) != len(self.optional_transports):
            raise ValueError("optional_transports must not contain duplicates")
        overlap = mandatory & optional
        if overlap:
            raise ValueError(
                f"mandatory and optional transports overlap: {sorted(overlap)}"
            )
        return self


__all__ = [
    "GATE_FAMILY_IDS",
    "GateFamilyId",
    "SurfaceTransportDeclaration",
    "Transport",
]
