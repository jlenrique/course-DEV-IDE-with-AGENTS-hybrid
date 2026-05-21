"""Gate G2A DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G2ACard(DecisionCardBase):
    """Plan-unit-ratification DecisionCard for the G2A gate family."""

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
    gate_id: Literal["G2A"] = Field(
        default="G2A",
        description="Discriminator for the G2A plan-unit-ratification gate.",
    )
    gate_focus: Literal["plan_unit_ratification"] = Field(
        default="plan_unit_ratification",
        description="Closed one-value marker for the G2A gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    plan_unit_id: UUID4 = Field(
        ...,
        description="UUID4 identity for the plan unit being ratified.",
    )
    plan_unit_summary: str = Field(
        ...,
        min_length=1,
        description="Operator-facing summary of the plan unit under review.",
    )
    ratification_evidence: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Machine-readable evidence supporting plan-unit ratification.",
    )
    prior_unit_ids: list[UUID4] = Field(
        default_factory=list,
        description="Ordered UUID4 identities for prior plan units that frame this decision.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )

    @field_validator("card_id", "trial_id", "plan_unit_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID4) -> UUID4:
        return enforce_uuid4_version(value)

    @field_validator("prior_unit_ids")
    @classmethod
    def _enforce_prior_unit_ids_uuid4(cls, value: list[UUID4]) -> list[UUID4]:
        for unit_id in value:
            enforce_uuid4_version(unit_id)
        return value

    @field_validator("created_at")
    @classmethod
    def _enforce_created_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("plan_unit_summary")
    @classmethod
    def _reject_blank_plan_unit_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("plan_unit_summary must be non-empty")
        return value

    @field_validator("ratification_evidence")
    @classmethod
    def _reject_empty_ratification_evidence(
        cls,
        value: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not value:
            raise ValueError("ratification_evidence must contain at least one item")
        return value


__all__ = ["G2ACard"]
