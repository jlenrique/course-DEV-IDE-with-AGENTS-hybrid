"""`OperatorVerdict` — frozen value object for HIL gate decisions (FR31, FR34).

Architecture **D3** (HIL Tamper-Evidence) places this model in Slab 1
substrate per architecture decision-of-record (overrides epics §3.3 drift).
The verdict surface MUST never accept ``"timeout"`` or ``"auto_approve"``
as legitimate verbs — those would silently bypass operator agency, the
exact failure mode FR34 forbids. Triple-layer red-rejection (field +
model_validator + schema-pin test) enforces the constraint.

Frozen by invariant: once an operator verdict is recorded, the receipt is
tamper-evident. Any "amended verdict" is a new instance with a new
`decision_card_id` reference.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version
from app.models.state.validators.operator_verdict_validators import (
    enforce_no_tamper_verbs,
    enforce_verb_payload_consistency,
)

OperatorVerdictVerb = Literal["approve", "edit", "reject"]
"""Closed enum: the only three verbs the verdict surface accepts."""


class OperatorVerdict(BaseModel):
    """Frozen tamper-evident receipt of one HIL gate decision.

    The triple-layer red-rejection on `verb` is the FR34 safeguard:
    ``"timeout"`` and ``"auto_approve"`` are explicitly NOT in the
    `Literal` set, the model_validator re-checks it, and the schema-pin
    test asserts the JSON Schema enum array contains exactly the three
    legitimate verbs.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    verb: OperatorVerdictVerb = Field(
        ...,
        description=(
            "Closed enum: approve | edit | reject. "
            "'timeout' and 'auto_approve' are explicitly forbidden per FR34."
        ),
    )
    gate_id: str = Field(
        ...,
        min_length=1,
        description="Gate identifier (e.g. 'G2C', 'G3', 'G4-15').",
    )
    decision_card_id: UUID = Field(
        ...,
        description="UUID4 of the DecisionCard the operator was reviewing.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        description="Operator identifier; single-operator scope in Slab 1 (e.g. 'juanl').",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware verdict timestamp.",
    )
    edit_payload: dict[str, Any] | None = Field(
        default=None,
        description="REQUIRED iff verb == 'edit'; cross-field-validated.",
    )
    reject_reason: str | None = Field(
        default=None,
        description="REQUIRED iff verb == 'reject'; cross-field-validated.",
    )

    @field_validator("decision_card_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("timestamp")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @model_validator(mode="after")
    def _check_invariants(self) -> OperatorVerdict:
        enforce_no_tamper_verbs(self.verb)
        enforce_verb_payload_consistency(
            verb=self.verb,
            edit_payload=self.edit_payload,
            reject_reason=self.reject_reason,
        )
        return self


__all__ = ["OperatorVerdict", "OperatorVerdictVerb"]
