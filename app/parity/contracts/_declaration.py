"""Parity-contract transport declarations."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Transport = Literal["cli", "http", "mcp-stdio", "mcp-subprocess"]


class SurfaceTransportDeclaration(BaseModel):
    """Declared transport parity contract for one operator-facing surface."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    surface_id: str = Field(..., min_length=1)
    mandatory_transports: list[Transport] = Field(..., min_length=1)
    optional_transports: list[Transport] = Field(default_factory=list)

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


__all__ = ["SurfaceTransportDeclaration", "Transport"]
