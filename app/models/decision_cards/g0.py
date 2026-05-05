"""Gate G0 DecisionCard."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import Field, field_serializer, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G0Card(DecisionCardBase):
    """Trial-open corpus-confirmation DecisionCard."""

    schema_version: Literal["v1"] = Field(
        default="v1",
        description="Schema version for the G0 DecisionCard contract.",
    )
    card_id: UUID = Field(
        ...,
        description="UUID4 identity for this DecisionCard instance.",
    )
    trial_id: UUID = Field(
        ...,
        description="UUID4 identity for the enclosing trial run.",
    )
    gate_id: Literal["G0"] = Field(
        default="G0",
        description="Discriminator for the G0 trial-open gate.",
    )
    gate_focus: Literal["trial_open"] = Field(
        default="trial_open",
        description="Closed marker for the G0 trial-open gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted card.",
    )
    corpus_paths_confirmed: list[Path] = Field(
        ...,
        description="Corpus paths confirmed by the operator for this trial.",
    )
    directive_run_id: UUID = Field(
        ...,
        description="UUID4 identity for the directive-composer run being confirmed.",
    )
    corpus_confirmation_summary: str = Field(
        ...,
        description="Non-empty operator-facing summary of corpus confirmation.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )

    @field_validator("card_id", "trial_id", "directive_run_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("corpus_paths_confirmed")
    @classmethod
    def _require_confirmed_paths(cls, value: list[Path]) -> list[Path]:
        if not value:
            raise ValueError("corpus_paths_confirmed must include at least one path")
        return value

    @field_validator("corpus_confirmation_summary")
    @classmethod
    def _require_confirmation_summary(cls, value: str) -> str:
        if not value:
            raise ValueError("corpus_confirmation_summary must be non-empty")
        return value

    @field_serializer("corpus_paths_confirmed")
    def _serialize_corpus_paths(self, value: list[Path]) -> list[str]:
        return [path.as_posix() for path in value]


__all__ = ["G0Card"]
