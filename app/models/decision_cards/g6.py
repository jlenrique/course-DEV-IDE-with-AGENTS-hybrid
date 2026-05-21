"""Gate G6 DecisionCard."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import UUID4, Field, field_serializer, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G6Card(DecisionCardBase):
    """Slab-close ceremony DecisionCard."""

    schema_version: Literal["v1"] = Field(
        default="v1",
        description="Schema version for the G6 DecisionCard contract.",
    )
    card_id: UUID4 = Field(
        ...,
        description="UUID4 identity for this DecisionCard instance.",
    )
    trial_id: UUID4 = Field(
        ...,
        description="UUID4 identity for the enclosing trial run.",
    )
    gate_id: Literal["G6"] = Field(
        default="G6",
        description="Discriminator for the G6 slab-close ceremony gate.",
    )
    gate_focus: Literal["slab_close_ceremony"] = Field(
        default="slab_close_ceremony",
        description="Closed marker for the G6 slab-close ceremony gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted card.",
    )
    slab_id: str = Field(
        ...,
        description="Slab identifier in numeric plus optional lowercase-letter form.",
    )
    closing_run_id: UUID4 = Field(
        ...,
        description="UUID4 identity for the final trial run referenced by closure.",
    )
    retrospective_path: Path = Field(
        ...,
        description="Canonical retrospective document path for the closed slab.",
    )
    closing_artifact_paths: list[Path] = Field(
        ...,
        description="Non-empty paths for slab-close ceremony evidence artifacts.",
    )
    slab_close_summary: str = Field(
        ...,
        description="Non-empty operator-facing summary of slab closure.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )

    @field_validator("card_id", "trial_id", "closing_run_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID4) -> UUID4:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("slab_id")
    @classmethod
    def _validate_slab_id_pattern(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9]+[a-z]?", value):
            raise ValueError("slab_id must match ^[0-9]+[a-z]?$")
        return value

    @field_validator("closing_artifact_paths")
    @classmethod
    def _require_closing_artifact_paths(cls, value: list[Path]) -> list[Path]:
        if not value:
            raise ValueError("closing_artifact_paths must include at least one path")
        return value

    @field_validator("slab_close_summary")
    @classmethod
    def _require_slab_close_summary(cls, value: str) -> str:
        if not value.strip():
            raise ValueError(
                "slab_close_summary must be non-empty (excluding whitespace)"
            )
        return value

    @field_serializer("retrospective_path")
    def _serialize_retrospective_path(self, value: Path) -> str:
        return value.as_posix()

    @field_serializer("closing_artifact_paths")
    def _serialize_closing_artifact_paths(self, value: list[Path]) -> list[str]:
        return [path.as_posix() for path in value]


__all__ = ["G6Card"]
