"""Strict warning model for sanctum mutations surfaced at the next gate."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware


class SanctumWarning(BaseModel):
    """One operator-visible sanctum mutation warning."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    file_path: str = Field(..., min_length=1)
    hash_before: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    hash_after: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")
    mutated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    suggested_invalidating_commit: str | None = None

    @field_validator("mutated_at")
    @classmethod
    def _enforce_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = ["SanctumWarning"]
