"""Single write surface for app-namespace Marcus orchestration tests."""

from __future__ import annotations

from typing import Any


def append_event(state: Any, event: dict[str, Any]) -> dict[str, Any]:
    events = getattr(state, "events", None)
    if events is None:
        events = []
        state.events = events
    events.append(event)
    return event


__all__ = ["append_event"]
