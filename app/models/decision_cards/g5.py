"""Gate G5 DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import UUID4, Field, field_serializer, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G5Card(DecisionCardBase):
    """Final-operator-handoff DecisionCard for the G5 gate family."""

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
    gate_id: Literal["G5"] = Field(
        default="G5",
        description="Discriminator for the G5 final-operator-handoff gate.",
    )
    gate_focus: Literal["final_operator_handoff"] = Field(
        default="final_operator_handoff",
        description="Closed marker for the G5 gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    bundle_run_id: UUID4 = Field(
        ...,
        description="UUID4 identity for the run that produced the handoff bundle.",
    )
    handoff_artifact_paths: list[Path] = Field(
        ...,
        description="Artifact paths included in the final operator handoff.",
    )
    handoff_summary: str = Field(
        ...,
        min_length=1,
        description="Operator-facing summary of the final handoff.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )

    @field_validator("card_id", "trial_id", "bundle_run_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID4) -> UUID4:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_created_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("handoff_artifact_paths")
    @classmethod
    def _require_handoff_artifact_paths(cls, value: list[Path]) -> list[Path]:
        if not value:
            raise ValueError("handoff_artifact_paths must contain at least one path")
        return value

    @field_validator("handoff_summary")
    @classmethod
    def _reject_blank_handoff_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("handoff_summary must be non-empty")
        return value

    @field_serializer("handoff_artifact_paths")
    def _serialize_handoff_artifact_paths(self, value: list[Path]) -> list[str]:
        return [path.as_posix() for path in value]


__all__ = ["G5Card"]
