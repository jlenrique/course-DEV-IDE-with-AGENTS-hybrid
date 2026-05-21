"""`SpecialistEnvelope` — request/response envelope around one specialist invocation.

Wraps the `SpecialistReturn` with request-side identity + payload so the
orchestrator can correlate specialist outputs to their corresponding
inputs across async boundaries. Slab 2 specialist migrations populate
the `payload_in` shape per-specialist; 1.2 lands the substrate envelope.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version
from app.models.state.specialist_return import SpecialistReturn


class SpecialistEnvelope(BaseModel):
    """Request/response envelope wrapping a SpecialistReturn with correlation identity."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    specialist_id: str = Field(..., min_length=1, description="Stable specialist identifier.")
    request_id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 correlation ID; pairs request to response across async boundaries.",
    )
    payload_in: dict[str, Any] = Field(
        default_factory=dict,
        description="Inbound payload to the specialist; shape per-specialist (Slab 2 tightens).",
    )
    payload_out: SpecialistReturn | None = Field(
        default=None,
        description="Specialist's return; None until the specialist responds.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware envelope-creation timestamp (request-side).",
    )

    @field_validator("request_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = ["SpecialistEnvelope"]
