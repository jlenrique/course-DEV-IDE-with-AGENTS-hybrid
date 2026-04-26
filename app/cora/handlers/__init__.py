"""Cora handler exports and shared checkpoint helper."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from app.models.state.node_checkpoint import NodeCheckpoint
from app.models.state.sanctum_fingerprint import SanctumFingerprint
from app.models.state.story_state import StoryState


def append_checkpoint(state: StoryState, *, node_id: str, step_index: int) -> dict[str, object]:
    """Append one completed node checkpoint to the story state."""
    now = datetime.now(UTC)
    checkpoint = NodeCheckpoint(
        node_id=node_id,
        step_index=step_index,
        status="complete",
        checkpoint_at=now,
        completed_at=now,
        sanctum_fingerprint=SanctumFingerprint(
            content_sha256=hashlib.sha256(node_id.encode("utf-8")).hexdigest()
        ),
    )
    return {
        "node_checkpoints": [*state.node_checkpoints, checkpoint],
        "updated_at": now,
    }
__all__ = ["append_checkpoint"]
