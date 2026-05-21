from __future__ import annotations

import json

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState


def make_state(cache_prefix: str) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5",
                resolved="gpt-5",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="c" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=0),
    )


def make_envelope(*, gate_phase: str = "pre-composition") -> str:
    return json.dumps(
        {
            "gate_phase": gate_phase,
            "artifact_path": "tests/fixtures/specialists/quinn_r/fixture_artifacts/sample.txt",
            "artifact_paths": [
                "tests/fixtures/specialists/quinn_r/fixture_artifacts/sample.txt",
            ],
            "modality": "image",
        }
    )
