"""Gate G2C DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G2CCard(DecisionCardBase):
    """Pre-execution sanity-check DecisionCard."""

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
    gate_id: Literal["G2C"] = Field(
        default="G2C",
        description="Discriminator for the G2C pre-execution gate.",
    )
    gate_focus: Literal["pre_composition_qa"] = Field(
        default="pre_composition_qa",
        description="Closed one-value marker for the G2C gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    readiness_status: Literal["ready", "blocked"] = Field(
        ...,
        description="Closed readiness status emitted before trial execution continues.",
    )
    blocking_issues: list[str] = Field(
        default_factory=list,
        description="Blocking issues that must be resolved before proceeding.",
    )
    ready_nodes: list[str] = Field(
        default_factory=list,
        description="Manifest nodes currently ready to execute.",
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


__all__ = ["G2CCard"]
