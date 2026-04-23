# SCHEDULED FOR REPLACEMENT IN STORY 1.3 — do not extend here; 1.3 deletes
# + re-authors this file with the full field set
# (level: Literal[...], requested: str | None, resolved: str, reason: str,
#  timestamp: datetime, cache_prefix_hash: str | None).
"""`ModelResolutionEntry` — STUB for `RunState.model_resolution_trail` (NFR-X4).

**Stub: 1.3 tightens this** — Story 1.3 (three-level model selector) replaces
this minimal shape with the full cascade-resolution entry per the spec's
Amelia amendment. Field set locked at `{level: str, resolved: str,
timestamp: datetime}` only; do NOT add fields here that conflict with the
1.3 full shape.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware


class ModelResolutionEntry(BaseModel):
    """STUB resolution entry; 1.3 replaces with the full cascade-resolution shape."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    level: str = Field(
        ...,
        min_length=1,
        description=(
            "Resolution level (e.g. 'per-call', 'per-specialist', 'registry-default'); "
            "1.3 tightens this to a Literal."
        ),
    )
    resolved: str = Field(
        ...,
        min_length=1,
        description="The model identifier the cascade resolved to at this level.",
    )
    timestamp: datetime = Field(
        ...,
        description="Timezone-aware resolution timestamp.",
    )

    @field_validator("timestamp")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = ["ModelResolutionEntry"]
