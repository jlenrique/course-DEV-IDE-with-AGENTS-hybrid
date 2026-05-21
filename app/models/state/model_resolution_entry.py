"""`ModelResolutionEntry` — full cascade-resolution entry (Story 1.3 replacement).

Replaces the 1.2 stub (`{level: str, resolved: str, timestamp: datetime}`) with the
full schema per architecture §D2 + spec AC-1.3-C. Each entry records ONE level
of the three-level cascade resolution (per_call → per_specialist →
registry_default → auto_select_fallback), so `RunState.model_resolution_trail`
captures the full audit trail per NFR-X4.

`cache_prefix_hash` is the load-bearing identifier for NFR-I6 (cache-prefix
stability across cold-read invocations); deterministic SHA-256 over the
canonical-JSON tuple `(specialist_id, model_id, temperature, system_prompt_hash)`.
See `app.models.selector._compute_cache_prefix_hash`.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware

ResolutionLevel = Literal[
    "per_call", "per_specialist", "registry_default", "auto_select_fallback"
]
"""Closed enum: which cascade level resolved this entry."""


class ModelResolutionEntry(BaseModel):
    """One cascade-resolution audit entry (NFR-X4 carrier)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    level: ResolutionLevel = Field(
        ...,
        description=(
            "Closed enum: per_call | per_specialist | registry_default | "
            "auto_select_fallback."
        ),
    )
    requested: str | None = Field(
        default=None,
        description=(
            "The model the caller requested at this level (None if no override "
            "was provided at this level — e.g. registry_default level always "
            "has requested=None)."
        ),
    )
    resolved: str = Field(
        ...,
        min_length=1,
        description="The model the cascade resolved to at this level.",
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Free-text explanation of why this level resolved as it did.",
    )
    timestamp: datetime = Field(
        ...,
        description="Timezone-aware resolution timestamp.",
    )
    cache_prefix_hash: str | None = Field(
        default=None,
        description=(
            "Deterministic SHA-256 hex of the cache-prefix tuple; None for "
            "non-final cascade entries that don't carry the cache identity."
        ),
    )

    @field_validator("timestamp")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("cache_prefix_hash")
    @classmethod
    def _enforce_sha256_hex(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if len(value) != 64 or not all(c in "0123456789abcdef" for c in value):
            raise ValueError(
                f"cache_prefix_hash must be 64-char lowercase-hex SHA-256; got {value!r}"
            )
        return value


__all__ = ["ModelResolutionEntry", "ResolutionLevel"]
