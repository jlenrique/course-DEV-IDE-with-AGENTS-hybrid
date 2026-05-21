"""`SpecialistReturn` — payload returned from a specialist node back to the orchestrator.

Mirrors the verb-based decision shape of `OperatorVerdict` for the
specialist-side return surface. Cross-field invariants enforce that
``edit`` payloads carry data and ``reject`` payloads carry rationale.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware
from app.models.state.validators.specialist_return_validators import (
    enforce_specialist_verb_payload_consistency,
)

SpecialistReturnVerb = Literal["proceed", "edit", "reject"]
"""Closed enum: specialist verbs (analogous to OperatorVerdict but with proceed/edit/reject)."""


class SpecialistReturn(BaseModel):
    """Specialist-side return payload. Cross-field invariants on verb/payload pairing."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    specialist_id: str = Field(..., min_length=1, description="Stable specialist identifier.")
    verb: SpecialistReturnVerb = Field(
        ...,
        description="Closed enum: proceed | edit | reject.",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Specialist's primary output payload (shape varies per specialist).",
    )
    edit_payload: dict[str, Any] | None = Field(
        default=None,
        description="REQUIRED iff verb == 'edit'; cross-field-validated.",
    )
    reject_reason: str | None = Field(
        default=None,
        description="REQUIRED iff verb == 'reject'; cross-field-validated.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware return timestamp.",
    )

    @field_validator("timestamp")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @model_validator(mode="after")
    def _check_invariants(self) -> SpecialistReturn:
        enforce_specialist_verb_payload_consistency(
            verb=self.verb,
            edit_payload=self.edit_payload,
            reject_reason=self.reject_reason,
        )
        return self


__all__ = ["SpecialistReturn", "SpecialistReturnVerb"]
