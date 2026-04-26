"""Base DecisionCard models shared by Marcus gate families."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.decision_cards.override_event import OverrideEvent
from app.models.gates.party_mode_contribution import PartyModeContribution
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]
CacheWarmth = Literal["healthy", "mixed", "cold"]


class DecisionCardMeta(BaseModel):
    """Cross-gate context surfaced to the operator with every DecisionCard."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    cache_state: CacheWarmth = Field(
        ...,
        description="Current prompt-cache warmth estimate for the trial.",
    )
    affected_nodes: list[str] = Field(
        default_factory=list,
        description="Manifest node ids affected by current overrides or cache churn.",
    )
    override_trail: list[OverrideEvent] = Field(
        default_factory=list,
        description="Append-only override history already applied to this trial.",
    )
    reject_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Current gate reject-rate snapshot in [0.0, 1.0].",
    )
    party_mode_contributions: list[PartyModeContribution] = Field(
        default_factory=list,
        description="Optional multi-persona contributions consolidated into this card.",
    )
    consolidated_at: datetime | None = Field(
        default=None,
        description="Timezone-aware timestamp when party-mode contributions were consolidated.",
    )

    @field_validator("affected_nodes")
    @classmethod
    def _enforce_affected_nodes(cls, value: list[str]) -> list[str]:
        for node_id in value:
            if not node_id:
                raise ValueError("affected_nodes entries must be non-empty strings")
        return value

    @field_validator("consolidated_at")
    @classmethod
    def _enforce_consolidated_at_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None


class DecisionCard(BaseModel):
    """Base operator-facing gate payload."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=False)

    card_id: UUID = Field(
        ...,
        description="UUID4 identity for this DecisionCard instance.",
    )
    trial_id: UUID = Field(
        ...,
        description="UUID4 identity for the enclosing trial run.",
    )
    gate_id: str = Field(
        ...,
        min_length=1,
        description="Closed gate identifier for the subclass discriminator.",
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
    risks: list[str] = Field(
        default_factory=list,
        description="Plain-language risk bullets surfaced to the operator.",
    )
    verb: DecisionCardVerb = Field(
        ...,
        description="Closed decision verb set: approve | edit | reject.",
    )
    meta: DecisionCardMeta = Field(
        ...,
        description="Cross-gate cache and override context per architecture D2.",
    )

    @field_validator("card_id", "trial_id")
    @classmethod
    def _enforce_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("created_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = [
    "CacheWarmth",
    "DecisionCard",
    "DecisionCardMeta",
    "DecisionCardVerb",
]
