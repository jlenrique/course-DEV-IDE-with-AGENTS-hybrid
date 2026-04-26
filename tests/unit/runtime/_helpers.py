from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.state import CacheState, ModelResolutionEntry, RunState
from app.runtime.override_api import clear_override_registry, register_run_state

TRIAL_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
_DEFAULT = object()


def sample_run_state(*, cache_state: CacheState | None | object = _DEFAULT) -> RunState:
    resolved_cache_state = cache_state
    if resolved_cache_state is _DEFAULT:
        resolved_cache_state = CacheState(
            cache_prefix="sanctum-v1-gpt54-run",
            entries_count=3,
            last_invalidated_at=None,
        )
    return RunState(
        run_id=UUID("55555555-5555-4555-8555-555555555555"),
        status="running",
        created_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="registry_default",
                requested=None,
                resolved="gpt-5.4",
                reason="default fallthrough",
                cache_prefix_hash="0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                timestamp=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
            )
        ],
        cache_state=resolved_cache_state,
    )


def register_sample_run_state(*, cache_state: CacheState | None | object = _DEFAULT) -> RunState:
    clear_override_registry()
    state = sample_run_state(cache_state=cache_state)
    register_run_state(trial_id=TRIAL_ID, state=state)
    return state
