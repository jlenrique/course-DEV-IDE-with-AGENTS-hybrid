"""Gate G3 DecisionCard."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.models.decision_cards.base import DecisionCard


class G3Card(DecisionCard):
    """Mid-trial DecisionCard for in-flight operator review."""

    gate_id: Literal["G3"] = Field(
        default="G3",
        description="Discriminator for the G3 mid-trial gate.",
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
        description="Direct operator question or action request for the gate.",
    )


__all__ = ["G3Card"]
