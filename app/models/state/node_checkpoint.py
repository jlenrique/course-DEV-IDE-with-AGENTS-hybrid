"""`NodeCheckpoint` — per-node execution checkpoint record.

Records one node's execution boundary in a story-state's history. Pairs
with `SanctumFingerprint` so the sanctum-content snapshot at the moment
of checkpoint is content-addressable for replay.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware
from app.models.state.sanctum_fingerprint import SanctumFingerprint
from app.models.state.validators.node_checkpoint_validators import (
    enforce_complete_requires_completed_at,
)

NodeCheckpointStatus = Literal["pending", "running", "complete", "failed"]
"""Closed enum: status of a single node checkpoint."""


class NodeCheckpoint(BaseModel):
    """Single-node checkpoint record. Cross-field invariant: complete ⇒ completed_at."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    node_id: str = Field(..., min_length=1, description="Stable node identifier.")
    step_index: int = Field(..., ge=0, description="0-based position in the graph topology.")
    status: NodeCheckpointStatus = Field(
        ...,
        description="Closed enum: pending | running | complete | failed.",
    )
    checkpoint_at: datetime = Field(
        ...,
        description="Timezone-aware timestamp of this checkpoint write.",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="REQUIRED iff status == 'complete'; timezone-aware.",
    )
    sanctum_fingerprint: SanctumFingerprint | None = Field(
        default=None,
        description=(
            "Content-addressable sanctum identity at this checkpoint. "
            "Optional in 1.2 substrate; downstream stories tighten when applicable."
        ),
    )

    @field_validator("checkpoint_at")
    @classmethod
    def _enforce_checkpoint_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("completed_at")
    @classmethod
    def _enforce_completed_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None

    @model_validator(mode="after")
    def _check_invariants(self) -> NodeCheckpoint:
        enforce_complete_requires_completed_at(
            status=self.status,
            completed_at=self.completed_at,
        )
        return self


__all__ = ["NodeCheckpoint", "NodeCheckpointStatus"]
