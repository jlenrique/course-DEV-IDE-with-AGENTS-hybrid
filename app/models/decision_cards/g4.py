"""Gate G4 DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G4Card(DecisionCardBase):
    """Post-trial closeout DecisionCard."""

    schema_version: Literal["v1"] = Field(
        default="v1",
        description="DecisionCard schema version.",
    )
    card_id: UUID4 = Field(
        ...,
        description="UUID4 identity for this DecisionCard instance.",
    )
    trial_id: UUID4 = Field(
        ...,
        description="UUID4 identity for the enclosing trial run.",
    )
    gate_id: Literal["G4"] = Field(
        default="G4",
        description="Discriminator for the G4 closeout gate.",
    )
    gate_focus: Literal["fidelity_gate"] = Field(
        default="fidelity_gate",
        description="Closed one-value marker for the G4 gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    final_status: Literal["completed", "partial", "failed"] = Field(
        ...,
        description="Closed final-status summary for trial closeout.",
    )
    artifact_paths: list[str] = Field(
        default_factory=list,
        description="Repo-relative artifact paths produced by the trial.",
    )
    outcome_summary: str = Field(
        ...,
        min_length=1,
        description="Operator-facing summary of the closeout outcome.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )

    @field_validator("card_id", "trial_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID4) -> UUID4:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_created_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("outcome_summary")
    @classmethod
    def _reject_blank_outcome_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("outcome_summary must be non-empty (excluding whitespace)")
        return value


__all__ = ["G4Card"]
