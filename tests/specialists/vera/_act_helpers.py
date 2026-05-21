from __future__ import annotations

import json

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState


def build_vera_state(payload: dict[str, object]) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5",
                resolved="gpt-5",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="e" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=0),
    )
