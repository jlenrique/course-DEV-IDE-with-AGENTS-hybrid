"""Implement-story node for the Cora dev graph."""

from __future__ import annotations

from app.cora.handlers import append_checkpoint
from app.models.state.story_state import StoryState


def implement_story(state: StoryState) -> dict[str, object]:
    return append_checkpoint(state, node_id="implement_story", step_index=1)


__all__ = ["implement_story"]
