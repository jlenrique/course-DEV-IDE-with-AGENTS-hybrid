"""`CacheState` — sanctum cold-read + cache-prefix tracking (architecture D5).

Records the cache-prefix-stability state per the architecture decision on
sanctum cold-read discipline. Story 1.3 will tighten the relationship to
the model-resolution cascade (cache-prefix-hash + invalidation source);
1.2 lands the shape only.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware


class CacheState(BaseModel):
    """Cache prefix + invalidation tracking for sanctum + model-resolution caches."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    cache_prefix: str = Field(
        ...,
        min_length=1,
        description="Stable prefix derived from sanctum + model + manifest version.",
    )
    entries_count: int = Field(
        default=0,
        ge=0,
        description="Number of entries currently held under this prefix.",
    )
    last_invalidated_at: datetime | None = Field(
        default=None,
        description=(
            "Timezone-aware timestamp of the most recent invalidation event; "
            "None means 'never invalidated since process start'."
        ),
    )

    @field_validator("last_invalidated_at")
    @classmethod
    def _enforce_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None


__all__ = ["CacheState"]
