"""Gate G2B DecisionCard — woken variant-pick HIL (Arc 2, 2026-06-18).

Emitted when the runner pauses at the woken `07B-gate` (G2B), AFTER node `07B`
(quinn-r) has produced its per-slide variant evaluation. Carries the variant
candidates the operator chooses among. Distinct from the generic `G2CCard`
(pre-composition QA readiness) — the variant pick is its own decision once the
gate is surfaced as a standalone pause point.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G2BCard(DecisionCardBase):
    """Woken variant-selection HIL DecisionCard."""

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
    gate_id: Literal["G2B"] = Field(
        default="G2B",
        description="Discriminator for the G2B variant-selection gate.",
    )
    gate_focus: Literal["variant_selection"] = Field(
        default="variant_selection",
        description="Closed one-value marker for the G2B gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    variant_candidates: list[str] = Field(
        default_factory=list,
        description="Per-slide variant candidates the operator selects among (from node 07B).",
    )
    selected_variant_id: str | None = Field(
        default=None,
        description="Operator-selected variant id; None until the pick is made (default-accept).",
    )
    gamma_settings: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Optional per-variant Gamma settings surfaced for operator review/override.",
    )
    pick_context: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Evidence the operator picks FROM — the adjacent quinn-r variant "
            "evaluation (specialist summary) surfaced at the pause."
        ),
    )
    operator_prompt: str = Field(
        ...,
        min_length=1,
        description="Operator-facing prompt for the variant pick.",
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

    @field_validator("operator_prompt")
    @classmethod
    def _reject_blank_operator_prompt(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("operator_prompt must be non-empty (excluding whitespace)")
        return value


__all__ = ["G2BCard"]
