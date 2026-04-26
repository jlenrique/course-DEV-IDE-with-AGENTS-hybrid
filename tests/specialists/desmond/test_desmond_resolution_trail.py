from __future__ import annotations

from app.models.adapter import make_chat_model
from app.models.state.run_state import RunState
from app.specialists.desmond.graph import _plan


def test_desmond_plan_appends_resolution_entry_to_trail() -> None:
    state = RunState(graph_version="v0.1-stub", temperature=0.0)
    update = _plan(state)
    trail = update["model_resolution_trail"]
    assert len(trail) == 1
    entry = trail[0]
    assert entry.resolved == "gpt-5-haiku"
    assert entry.level == "per_specialist"
    assert entry.cache_prefix_hash is not None


def test_desmond_chat_metadata_contains_span_fields() -> None:
    handle = make_chat_model(specialist_id="desmond", tier_request="fast")
    metadata = getattr(handle.chat, "metadata", {}) or {}
    assert metadata.get("specialist_id") == "desmond"
    assert metadata.get("level")
    assert metadata.get("cache_prefix_hash")
