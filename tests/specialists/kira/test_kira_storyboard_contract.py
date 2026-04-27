from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.kira.graph import _act


def test_storyboard_b_visual_file_is_preserved_and_motion_added(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "status": "mocked",
            "motion_asset_path": "artifacts/segment-001-motion.mp4",
            "kling_choices": {
                "model_name": "kling-v1",
                "mode": "std",
                "duration": 5.0,
                "negative_prompt": "",
            },
        }

    mock_response = MagicMock()
    mock_response.content = json.dumps(
        {
            "kling_prompt": "cinematic pan across the slide visual",
            "model_name": "kling-v1",
            "mode": "std",
            "duration": 5,
            "negative_prompt": "",
        }
    )
    mock_response.usage_metadata = {"input_tokens": 1500, "output_tokens": 200}

    class _Handle:
        def __init__(self) -> None:
            self.chat = MagicMock()
            self.chat.invoke.return_value = mock_response
            self.entry = ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="a" * 64,
            )

    monkeypatch.setattr("app.specialists.kira.graph.make_chat_model", lambda **_: _Handle())
    monkeypatch.setattr("app.specialists.kira.graph.dispatch_to_kling", _fake_dispatch)

    envelope = {"slide_id": "s1", "visual_file": "artifacts/segment-001.png"}
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="b" * 64,
            )
        ],
        cache_state=CacheState(
            cache_prefix=json.dumps(
                envelope, sort_keys=True, ensure_ascii=True, separators=(",", ":")
            ),
            entries_count=0,
        ),
    )
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["visual_file"] == "artifacts/segment-001.png"
    assert output["motion_asset_path"] == "artifacts/segment-001-motion.mp4"
