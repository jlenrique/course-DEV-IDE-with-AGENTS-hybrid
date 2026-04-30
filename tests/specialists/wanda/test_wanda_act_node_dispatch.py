from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.wanda import _act as wanda_act
from app.specialists.wanda.graph import _act


class FakeWondercraftClient:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def check_connectivity(self) -> dict[str, Any]:
        return {"reachable": True, "status_code": 200}

    def generate_audio_bed(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        return {
            "id": "wc-bed-001",
            "url": "https://cdn.wondercraft.test/bed-focused-ambient.mp3",
            "format": "mp3",
            "audio_bytes": b"fake-mp3-bytes",
            "cost_usd": 0.12,
        }


def _build_state(payload: dict[str, Any]) -> RunState:
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
        cache_state=CacheState(cache_prefix=json.dumps(payload), entries_count=0),
    )


def test_generate_audio_beds_writes_storyboard_scoped_bed(tmp_path: Path) -> None:
    client = FakeWondercraftClient()
    payload = {
        "bundle_path": str(tmp_path),
        "storyboard": {"audio_track": {"mood": "focused", "genre": "ambient"}},
        "narration_manifest": {"segments": [{"text": "Explain the concept clearly."}]},
    }

    verdict = wanda_act.generate_audio_beds(payload, client=client)  # type: ignore[arg-type]

    target = tmp_path / "assembly-bundle" / "audio" / "beds" / "bed-focused-ambient.mp3"
    assert target.read_bytes() == b"fake-mp3-bytes"
    assert client.calls[0]["mood"] == "focused"
    assert verdict["gate_id"] == "G2"
    assert verdict["storyboard_audio_track"]["beds"][0]["audio_path"] == str(target)
    assert verdict["compositor_invocation"]["audio_bed_paths"] == [str(target)]


def test_wanda_act_returns_audio_bed_receipt(tmp_path: Path) -> None:
    client = FakeWondercraftClient()
    state = _build_state(
        {
            "bundle_path": str(tmp_path),
            "audio_track": {"beds": [{"bed_id": "intro", "mood": "warm", "genre": "lofi"}]},
            "script": "Narration text for the lesson.",
        }
    )

    update = wanda_act.act(state, client=client)  # type: ignore[arg-type]
    output = json.loads(update["cache_state"]["cache_prefix"])

    assert output["specialist_id"] == "wanda"
    assert output["audio_beds"][0]["bed_id"] == "intro"
    assert output["audio_beds"][0]["provider_id"] == "wc-bed-001"
    assert update["model_resolution_trail"][-1].reason == "wondercraft.audio-bed.ok"


def test_wanda_act_malformed_cache_prefix_sets_trail_tag() -> None:
    state = RunState(
        graph_version="v0.1-stub",
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5",
                resolved="gpt-5",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
            )
        ],
        cache_state=CacheState(cache_prefix="{bad", entries_count=0),
    )
    with pytest.raises(wanda_act.WandaActError) as exc_info:
        wanda_act.act(state, client=FakeWondercraftClient())  # type: ignore[arg-type]
    assert exc_info.value.tag == "wondercraft.malformed"
    assert state.model_resolution_trail[-1].reason == "wondercraft.malformed"


def test_graph_act_is_bounded_wrapper() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 10
