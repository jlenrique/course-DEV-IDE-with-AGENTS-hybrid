"""Gate G4 DecisionCard."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.models.decision_cards.base import DecisionCard


class G4Card(DecisionCard):
    """Post-trial closeout DecisionCard."""

    gate_id: Literal["G4"] = Field(
        default="G4",
        description="Discriminator for the G4 closeout gate.",
    )
    final_status: Literal["completed", "partial", "failed"] = Field(
        ...,
        description="Closed final-status summary for trial closeout.",
    )
    artifact_paths: list[str] = Field(
        default_factory=list,
        description="Repo-relative artifact paths produced by the trial.",
    )
    outcome_summary: str = Field(
        ...,
        description="Operator-facing summary of the closeout outcome.",
    )


__all__ = ["G4Card"]
