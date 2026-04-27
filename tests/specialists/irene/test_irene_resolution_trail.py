"""AC-G — Resolution trail entry shape from Irene `_plan` node (Story 2a.2).

One test per spec AC-G pin: invoking `_plan` on a fresh RunState appends one
ModelResolutionEntry naming the resolved model + cache_prefix_hash + level.
"""

from __future__ import annotations

from app.models.state.run_state import RunState
from app.specialists.irene.graph import _plan


def test_irene_plan_appends_resolution_entry_to_trail() -> None:
    state = RunState(graph_version="v0.1-stub", temperature=0.3)
    assert state.model_resolution_trail == []
    update = _plan(state)
    assert "model_resolution_trail" in update
    new_trail = update["model_resolution_trail"]
    assert len(new_trail) == 1
    entry = new_trail[0]
    assert entry.resolved == "gpt-5"
    assert entry.level == "per_specialist"
    # cache_prefix_hash is a deterministic SHA-256 over the canonical-JSON tuple.
    assert entry.cache_prefix_hash is not None
    assert len(entry.cache_prefix_hash) == 64
    assert entry.requested == "gpt-5"
