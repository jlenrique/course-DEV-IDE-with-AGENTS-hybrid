"""Ledger event models and builders."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Annotated, Literal, TypeAlias
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version
from app.models.state.operator_verdict import OperatorVerdict

LedgerEventKind = Literal["verdict", "override", "sanctum_mutation"]


class _LedgerEventBase(BaseModel):
    """Common typed fields for all ledger events."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    trial_id: UUID
    gate_id: str = Field(..., min_length=1)
    kind: LedgerEventKind
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("event_id", "trial_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    def natural_key(self) -> str:
        raise NotImplementedError

    def payload(self) -> dict[str, object]:
        data = self.model_dump(mode="json")
        for key in ("event_id", "trial_id", "gate_id", "kind", "created_at"):
            data.pop(key, None)
        return data

    def idempotency_key(self) -> str:
        raw = f"{self.trial_id}|{self.gate_id}|{self.kind}|{self.natural_key()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class VerdictLedgerEvent(_LedgerEventBase):
    """One operator verdict emitted at a gate boundary."""

    kind: Literal["verdict"] = "verdict"
    verdict_id: UUID
    card_id: UUID
    operator_id: str = Field(..., min_length=1)
    verb: Literal["approve", "edit", "reject"]
    transport_kind: str = Field(default="unknown", min_length=1)

    @field_validator("verdict_id", "card_id")
    @classmethod
    def _enforce_related_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    def natural_key(self) -> str:
        return str(self.verdict_id)


class OverrideLedgerEvent(_LedgerEventBase):
    """One runtime override proto-event."""

    kind: Literal["override"] = "override"
    node_id: str = Field(..., min_length=1)
    operator_id: str = Field(..., min_length=1)
    previous_model: str = Field(..., min_length=1)
    new_model: str = Field(..., min_length=1)
    confirm_token: str = Field(..., min_length=1)
    phase: Literal["submitted", "applied"] = "applied"

    def natural_key(self) -> str:
        return f"{self.confirm_token}|{self.phase}"


class SanctumMutationLedgerEvent(_LedgerEventBase):
    """One detected sanctum mutation."""

    kind: Literal["sanctum_mutation"] = "sanctum_mutation"
    file_path: str = Field(..., min_length=1)
    hash_before: str = Field(..., min_length=1)
    hash_after: str = Field(..., min_length=1)
    mutated_at: datetime
    suggested_invalidating_commit: str | None = None

    @field_validator("mutated_at")
    @classmethod
    def _enforce_mutated_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    def natural_key(self) -> str:
        return f"{self.file_path}|{self.hash_after}|{self.mutated_at.isoformat()}"


LedgerEvent: TypeAlias = Annotated[
    VerdictLedgerEvent | OverrideLedgerEvent | SanctumMutationLedgerEvent,
    Field(discriminator="kind"),
]
LedgerEventAdapter = TypeAdapter(LedgerEvent)
VerdictEvent = VerdictLedgerEvent
OverrideEvent = OverrideLedgerEvent
SanctumMutationEvent = SanctumMutationLedgerEvent


def build_verdict_ledger_event(
    verdict: OperatorVerdict,
    *,
    transport_kind: str,
) -> VerdictLedgerEvent:
    """Build a ledger verdict event from an operator verdict."""
    return VerdictLedgerEvent(
        trial_id=verdict.trial_id,
        gate_id=verdict.gate_id,
        verdict_id=verdict.verdict_id,
        card_id=verdict.card_id,
        operator_id=verdict.operator_id,
        verb=verdict.verb,
        transport_kind=transport_kind,
        created_at=verdict.timestamp,
    )


def build_override_ledger_event(
    *,
    trial_id: UUID,
    node_id: str,
    operator_id: str,
    previous_model: str,
    new_model: str,
    confirm_token: str,
    phase: Literal["submitted", "applied"],
    created_at: datetime | None = None,
) -> OverrideLedgerEvent:
    """Build one override ledger event for the runtime override flow."""
    return OverrideLedgerEvent(
        trial_id=trial_id,
        gate_id="override",
        node_id=node_id,
        operator_id=operator_id,
        previous_model=previous_model,
        new_model=new_model,
        confirm_token=confirm_token,
        phase=phase,
        created_at=created_at or datetime.now(UTC),
    )


def build_sanctum_mutation_ledger_event(
    *,
    trial_id: UUID,
    file_path: str,
    hash_before: str,
    hash_after: str,
    mutated_at: datetime,
    suggested_invalidating_commit: str | None = None,
) -> SanctumMutationLedgerEvent:
    """Build one sanctum-mutation ledger event."""
    return SanctumMutationLedgerEvent(
        trial_id=trial_id,
        gate_id="sanctum",
        file_path=file_path,
        hash_before=hash_before,
        hash_after=hash_after,
        mutated_at=mutated_at,
        suggested_invalidating_commit=suggested_invalidating_commit,
        created_at=mutated_at,
    )


__all__ = [
    "LedgerEvent",
    "LedgerEventAdapter",
    "LedgerEventKind",
    "OverrideEvent",
    "OverrideLedgerEvent",
    "SanctumMutationEvent",
    "SanctumMutationLedgerEvent",
    "VerdictEvent",
    "VerdictLedgerEvent",
    "build_override_ledger_event",
    "build_sanctum_mutation_ledger_event",
    "build_verdict_ledger_event",
]
