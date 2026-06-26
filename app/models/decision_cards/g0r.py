"""Gate G0R DecisionCard — operator ratify-gate #2 (Story G0-S3).

Emitted when the runner pauses at the ``g0-ratify-gate`` (``G0R``), AFTER the
``irene-refinement`` orchestration node has refined the gate-#1 provisional LOs
in place and frozen the signed LO-delta contract. Re-presents the refined plan +
the LO-delta ledger + the per-LO adequacy report + the count reconciliation, with
any ``recommend-drop`` / ``proposed-new`` entries flagged for the operator's call.

Deterministic guard (mirrors the S2 G0E card): the model NEVER auto-ratifies — the
operator verdict advances ``refined -> ratified``. This card is the surface the
operator ratifies; advancing is the runner's job on the operator verdict.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G0RCard(DecisionCardBase):
    """Operator ratify-gate #2 DecisionCard (Irene-refined LOs + signed LO-delta)."""

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
    gate_id: Literal["G0R"] = Field(
        default="G0R",
        description="Discriminator for the G0R LO-ratification gate.",
    )
    gate_focus: Literal["lo_ratification"] = Field(
        default="lo_ratification",
        description="Closed one-value marker for the G0R gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    refined_los: list[dict[str, Any]] = Field(
        default_factory=list,
        description="The surviving LOs after refinement (status=refined / held).",
    )
    lo_delta: list[dict[str, Any]] = Field(
        default_factory=list,
        description="The signed LO-delta ledger entries (one disposition per id).",
    )
    reconcile: dict[str, Any] = Field(
        default_factory=dict,
        description="Count reconciliation (g0_count <-> irene_count via the ledger).",
    )
    flagged_for_operator: list[dict[str, Any]] = Field(
        default_factory=list,
        description="proposed-new + recommend-drop entries the operator must rule on.",
    )
    operator_prompt: str = Field(
        ...,
        min_length=1,
        description="Operator-facing prompt for the LO-ratification verdict.",
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


__all__ = ["G0RCard"]
