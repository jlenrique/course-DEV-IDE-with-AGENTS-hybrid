"""Override trail entries referenced by DecisionCard meta."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version


class OverrideEvent(BaseModel):
    """One operator-approved override that affects cache warmth and routing context."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    event_id: UUID = Field(
        ...,
        description="UUID4 identity for this override event.",
    )
    applied_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware timestamp for when the override applied.",
    )
    node_id: str = Field(
        ...,
        min_length=1,
        description="Manifest node id that the override touches.",
    )
    previous_value: dict[str, Any] = Field(
        default_factory=dict,
        description="Canonical JSON-like view of the previous setting.",
    )
    new_value: dict[str, Any] = Field(
        default_factory=dict,
        description="Canonical JSON-like view of the new setting.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        description="Operator identity that confirmed the override.",
    )
    confirm_token: str = Field(
        ...,
        min_length=1,
        description="Confirmation token bound to the override submission surface.",
    )

    @field_validator("event_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("applied_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = ["OverrideEvent"]
