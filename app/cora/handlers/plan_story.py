"""Plan-story node for the Cora dev graph."""

from __future__ import annotations

from app.cora.handlers import append_checkpoint
from app.models.state.story_state import StoryState


def plan_story(state: StoryState) -> dict[str, object]:
    return append_checkpoint(state, node_id="plan_story", step_index=0)


__all__ = ["plan_story"]
