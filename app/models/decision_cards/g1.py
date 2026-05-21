"""Gate G1 DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G1Card(DecisionCardBase):
    """Trial-open DecisionCard for the first operator checkpoint."""

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
    gate_id: Literal["G1"] = Field(
        default="G1",
        description="Discriminator for the G1 trial-open gate.",
    )
    gate_focus: Literal["trial_open"] = Field(
        default="trial_open",
        description="Closed one-value marker for the G1 gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    drafted_proposal: dict[str, Any] = Field(
        default_factory=dict,
        description="Marcus-authored proposed action the operator is reviewing.",
    )
    evidence: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Machine-readable supporting evidence snippets for the proposal.",
    )
    trial_summary: str = Field(
        ...,
        min_length=1,
        description="Operator-facing summary of the trial-open posture.",
    )
    opened_by: str = Field(
        ...,
        min_length=1,
        description="Actor or subsystem that opened the gate.",
    )
    next_nodes: list[str] = Field(
        default_factory=list,
        description="Next manifest node ids if the operator approves the proposal.",
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

    @field_validator("trial_summary")
    @classmethod
    def _reject_blank_trial_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("trial_summary must be non-empty (excluding whitespace)")
        return value

    @field_validator("opened_by")
    @classmethod
    def _reject_blank_opened_by(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("opened_by must be non-empty (excluding whitespace)")
        return value


__all__ = ["G1Card"]
