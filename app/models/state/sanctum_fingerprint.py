"""`SanctumFingerprint` — frozen value object for sanctum snapshot identity.

Architecture **D1** (Sanctum Snapshot Strategy — Option C Hybrid) requires
content-hash-per-checkpoint addressing. NFR-X3 (sanctum reproducibility)
requires the snapshot identity be byte-stable + content-addressable.

This is a frozen value object: equality + hashing are by content, not
reference. Mutation is forbidden after construction (`frozen=True`); any
"new fingerprint" is a new instance.
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version


class SanctumFingerprint(BaseModel):
    """Content-addressable snapshot identity. Frozen by architecture invariant."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    snapshot_id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 identity for this fingerprint instance.",
    )
    content_sha256: str = Field(
        ...,
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
        description="Lowercase-hex SHA-256 of the snapshot's canonical bytes.",
    )
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware capture timestamp.",
    )

    @field_validator("snapshot_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("captured_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = ["SanctumFingerprint"]
