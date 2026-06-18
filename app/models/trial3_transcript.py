"""Trial-3 operator transcript schema.

Story 7c.21 owns the FR-7c-51 Trial3Transcript shape. Gate identifiers are
closed against the live production-gate surface from
``production_gate_ids(state/config/pipeline-manifest.yaml)`` as of this schema
version; the shape-pin test fails if the manifest and Literal drift.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import UUID4, BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

GateId = Literal[
    "G1",
    "G2B",  # Arc 2 (2026-06-18): woken variant pick
    "G2C",
    "G3",
    "G4",
    "G4A",  # Arc 2 (2026-06-18): woken voice pick
]
TrialEventType = Literal["edit", "approve", "reject", "complete"]

SHA256_PATTERN = r"^[0-9a-f]{64}$"


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


class TrialEvent(BaseModel):
    """One operator interaction captured during Trial-3."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    event_id: UUID4
    gate_id: GateId
    event_type: TrialEventType
    event_at: datetime
    operator_id: str = Field(..., min_length=1)
    payload_digest: str = Field(..., pattern=SHA256_PATTERN)

    @field_validator("event_id")
    @classmethod
    def _require_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("event_at")
    @classmethod
    def _require_event_at_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("operator_id", mode="before")
    @classmethod
    def _strip_operator_id(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)


class Trial3Transcript(BaseModel):
    """Append-only transcript envelope for the Trial-3 closeout attempt."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    trial_id: UUID4
    started_at: datetime
    completed_at: datetime | None = None
    events: list[TrialEvent] = Field(..., min_length=1)
    schema_version: int = 1

    @field_validator("trial_id")
    @classmethod
    def _require_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("started_at", "completed_at")
    @classmethod
    def _require_transcript_tz_aware(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        return enforce_tz_aware(value)


__all__ = [
    "GateId",
    "SHA256_PATTERN",
    "Trial3Transcript",
    "TrialEvent",
    "TrialEventType",
]
