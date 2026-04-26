"""`OperatorVerdict` — frozen value object for HIL gate decisions (FR31, FR34)."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version
from app.models.state.validators.operator_verdict_validators import (
    enforce_no_tamper_verbs,
    enforce_verb_payload_consistency,
)

OperatorVerdictVerb = Literal["approve", "edit", "reject"]


class OperatorVerdict(BaseModel):
    """Frozen tamper-evident receipt of one HIL gate decision."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
        populate_by_name=True,
    )

    verdict_id: UUID = Field(
        default_factory=uuid4,
        description="UUID4 identity for this verdict receipt.",
    )
    trial_id: UUID = Field(
        ...,
        description="UUID4 identity for the enclosing trial run.",
    )
    verb: OperatorVerdictVerb = Field(
        ...,
        description="Closed enum: approve | edit | reject.",
    )
    gate_id: str = Field(
        ...,
        min_length=1,
        description="Gate identifier (for example G2C, G3, G4).",
    )
    card_id: UUID = Field(
        ...,
        validation_alias=AliasChoices("card_id", "decision_card_id"),
        serialization_alias="card_id",
        description="UUID4 of the DecisionCard the operator was reviewing.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]+$",
        description="Operator identifier (letter-first, alnum / underscore / dash).",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware verdict timestamp.",
    )
    decision_card_digest: str = Field(
        ...,
        description="Lowercase sha256 bound to card content, trial, issuance time, and nonce.",
    )
    edit_payload: dict[str, Any] | None = Field(
        default=None,
        description="Required iff verb == 'edit'.",
    )
    reject_reason: str | None = Field(
        default=None,
        description="Required iff verb == 'reject'.",
    )

    @field_validator("verdict_id", "trial_id", "card_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("timestamp")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("decision_card_digest")
    @classmethod
    def _enforce_sha256_digest(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("decision_card_digest must be lowercase sha256 hex")
        return value

    @model_validator(mode="after")
    def _check_invariants(self) -> OperatorVerdict:
        enforce_no_tamper_verbs(self.verb)
        enforce_verb_payload_consistency(
            verb=self.verb,
            edit_payload=self.edit_payload,
            reject_reason=self.reject_reason,
        )
        return self

    @property
    def decision_card_id(self) -> UUID:
        """Backward-compatible alias for older call sites."""
        return self.card_id


__all__ = ["OperatorVerdict", "OperatorVerdictVerb"]
