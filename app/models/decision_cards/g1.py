"""Gate G1 DecisionCard."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.models.decision_cards.base import DecisionCard


class G1Card(DecisionCard):
    """Trial-open DecisionCard for the first operator checkpoint."""

    gate_id: Literal["G1"] = Field(
        default="G1",
        description="Discriminator for the G1 trial-open gate.",
    )
    trial_summary: str = Field(
        ...,
        description="Operator-facing summary of the trial-open posture.",
    )
    gate_focus: Literal["trial_open"] = Field(
        default="trial_open",
        description="Closed one-value marker for the G1 gate family.",
    )
    opened_by: str = Field(
        ...,
        min_length=1,
        description="Actor or subsystem that opened the gate.",
    )
    next_nodes: list[str] = Field(
        default_factory=list,
        description="Next manifest node ids if the operator approves the proposal.",
    )


__all__ = ["G1Card"]
