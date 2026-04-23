"""`StoryState` — per-story execution slice within a `RunState`.

Holds the chain of `NodeCheckpoint` records produced as a story walks the
graph. Slab 1 substrate; Slab 2+ stories enrich with specialist
attachments, scoring, etc.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.state._base import enforce_tz_aware
from app.models.state.node_checkpoint import NodeCheckpoint


class StoryState(BaseModel):
    """One story's execution slice: identity + ordered checkpoint history."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    story_id: str = Field(..., min_length=1, description="Stable story identifier.")
    node_checkpoints: list[NodeCheckpoint] = Field(
        default_factory=list,
        description=(
            "Ordered history of node checkpoints for this story "
            "(append-only by convention)."
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timezone-aware timestamp of the most recent state mutation.",
    )

    @field_validator("updated_at")
    @classmethod
    def _enforce_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)


__all__ = ["StoryState"]
