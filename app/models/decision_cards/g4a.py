"""Gate G4A DecisionCard — woken voice-pick HIL (Arc 2, 2026-06-18).

Emitted when the runner pauses at the woken `11-gate` (G4A), AFTER node `11`
(elevenlabs) has produced its voice options. Carries the voice candidates the
operator chooses among. Distinct from the generic `G4Card` (fidelity closeout)
— the voice pick is its own decision once the gate is surfaced as a standalone
pause point.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import UUID4, Field, field_validator

from app.models.decision_cards._base import DecisionCardBase
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

DecisionCardVerb = Literal["approve", "edit", "reject"]


class G4ACard(DecisionCardBase):
    """Woken voice-selection HIL DecisionCard."""

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
    gate_id: Literal["G4A"] = Field(
        default="G4A",
        description="Discriminator for the G4A voice-selection gate.",
    )
    gate_focus: Literal["voice_selection"] = Field(
        default="voice_selection",
        description="Closed one-value marker for the G4A gate family.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware creation timestamp for the emitted DecisionCard.",
    )
    voice_candidates: list[str] = Field(
        default_factory=list,
        description="Voice candidates the operator selects among (from node 11 elevenlabs).",
    )
    selected_voice_id: str | None = Field(
        default=None,
        description="Operator-selected voice id; None until the pick is made (default-accept).",
    )
    pick_context: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Evidence the operator picks FROM — the adjacent elevenlabs voice "
            "options (specialist summary) surfaced at the pause."
        ),
    )
    operator_prompt: str = Field(
        ...,
        min_length=1,
        description="Operator-facing prompt for the voice pick.",
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


__all__ = ["G4ACard"]
