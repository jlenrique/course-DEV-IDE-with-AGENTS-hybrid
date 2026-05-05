"""TripwireLedgerEntry schema for Slab 7c tripwire-ledger rows.

Per Story 7c.0a Decision Foundation; primary enforcement of NFR-7c-OD2.
Consumed by sprint-status.yaml::tripwire_events writers and the FR-7c-50
audit-chain integrity scaffold that lands in Story 7c.0b.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

TripwireIdLiteral = Literal[
    "TW-7c-1",
    "TW-7c-2",
    "TW-7c-3",
    "TW-7c-4",
    "TW-7c-5",
    "TW-7c-6",
]

FiredVerdict = Literal[
    "fired",
    "not_fired",
    "not_yet_evaluated",
    "not-applicable",
    "marginal-fired",
    "false",
    "true",
]

_TRIPWIRE_ID_LITERAL_ADAPTER: TypeAdapter[TripwireIdLiteral] = TypeAdapter(
    TripwireIdLiteral
)


class TripwireId(StrEnum):
    """Closed Slab 7c tripwire IDs."""

    TW_7C_1 = "TW-7c-1"
    TW_7C_2 = "TW-7c-2"
    TW_7C_3 = "TW-7c-3"
    TW_7C_4 = "TW-7c-4"
    TW_7C_5 = "TW-7c-5"
    TW_7C_6 = "TW-7c-6"


class TripwireSeverity(StrEnum):
    """Closed severity tiers for tripwire fires."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class TripwireLedgerEntry(BaseModel):
    """Canonical tripwire-ledger entry (Murat A5; NFR-7c-OD2)."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    tripwire_id: TripwireId = Field(
        ...,
        description="Closed enum: TW-7c-1..TW-7c-6.",
    )
    story_owner: str = Field(
        ...,
        min_length=1,
        description="Primary story key, for example '7c-20c'.",
    )
    fired_at: datetime = Field(
        ...,
        description="Timezone-aware datetime.",
    )
    fired_verdict: FiredVerdict = Field(
        ...,
        description="Tripwire evaluation verdict.",
    )
    measured_value: dict | None = Field(
        default=None,
        description="Free-form per-tripwire payload.",
    )
    escalation_action_taken: str | None = Field(
        default=None,
        description="Action taken when the tripwire evaluated.",
    )
    decision_record_link: str | None = Field(
        default=None,
        description="Pipe-or-newline-separated artifact paths.",
    )
    severity: TripwireSeverity = Field(
        ...,
        description="Closed enum: critical / high / medium.",
    )
    trace_id: UUID | None = Field(
        default=None,
        description="UUID4 trace identifier.",
    )

    @field_validator("tripwire_id", mode="before")
    @classmethod
    def _reject_unknown_tripwire_id(cls, value: object) -> object:
        """Literal adapter adds the explicit coercion-path red-rejection layer."""
        if isinstance(value, TripwireId):
            return value
        return _TRIPWIRE_ID_LITERAL_ADAPTER.validate_python(value)

    @field_validator("fired_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("trace_id")
    @classmethod
    def _require_uuid4(cls, value: UUID | None) -> UUID | None:
        if value is None:
            return None
        return enforce_uuid4_version(value)


__all__ = [
    "TripwireId",
    "TripwireLedgerEntry",
    "TripwireSeverity",
]
