"""Gate G3 DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G3Card(DecisionCardBase):
    """Mid-trial DecisionCard for in-flight operator review."""

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
    gate_id: Literal["G3"] = Field(
        default="G3",
        description="Discriminator for the G3 mid-trial gate.",
    )
    gate_focus: Literal["motion_clip_approval"] = Field(
        default="motion_clip_approval",
        description="Closed one-value marker for the G3 gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    progress_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Observed trial completion percentage at the checkpoint.",
    )
    active_node_id: str = Field(
        ...,
        min_length=1,
        description="Manifest node actively under review when the gate fired.",
    )
    pending_nodes: list[str] = Field(
        default_factory=list,
        description="Manifest node ids still waiting to execute.",
    )
    operator_prompt: str = Field(
        ...,
        min_length=1,
        description="Direct operator question or action request for the gate.",
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

    @field_validator("active_node_id")
    @classmethod
    def _reject_blank_active_node_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("active_node_id must be non-empty (excluding whitespace)")
        return value

    @field_validator("operator_prompt")
    @classmethod
    def _reject_blank_operator_prompt(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("operator_prompt must be non-empty (excluding whitespace)")
        return value


__all__ = ["G3Card"]
