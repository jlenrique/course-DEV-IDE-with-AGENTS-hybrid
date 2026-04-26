"""Gate G2C DecisionCard."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.models.decision_cards.base import DecisionCard


class G2CCard(DecisionCard):
    """Pre-execution sanity-check DecisionCard."""

    gate_id: Literal["G2C"] = Field(
        default="G2C",
        description="Discriminator for the G2C pre-execution gate.",
    )
    readiness_status: Literal["ready", "blocked"] = Field(
        ...,
        description="Closed readiness status emitted before trial execution continues.",
    )
    blocking_issues: list[str] = Field(
        default_factory=list,
        description="Blocking issues that must be resolved before proceeding.",
    )
    ready_nodes: list[str] = Field(
        default_factory=list,
        description="Manifest nodes currently ready to execute.",
    )


__all__ = ["G2CCard"]
