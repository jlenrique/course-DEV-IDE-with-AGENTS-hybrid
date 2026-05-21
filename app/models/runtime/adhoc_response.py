"""Strict response contract for one-shot Marcus ad-hoc asks."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TokenCount(BaseModel):
    """Token usage returned by the ad-hoc LLM call."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _total_must_cover_parts(self) -> TokenCount:
        if self.total_tokens < self.input_tokens + self.output_tokens:
            raise ValueError("total_tokens must be >= input_tokens + output_tokens")
        return self


class AdhocResponse(BaseModel):
    """Marcus ad-hoc response with inline economics metadata."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    text: str = Field(..., min_length=1)
    model_used: str = Field(..., min_length=1)
    tokens: TokenCount
    cost_usd: float = Field(..., ge=0.0)


__all__ = ["AdhocResponse", "TokenCount"]
