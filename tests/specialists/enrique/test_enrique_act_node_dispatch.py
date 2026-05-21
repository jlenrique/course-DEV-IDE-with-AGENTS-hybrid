from __future__ import annotations

import inspect
import json
from pathlib import Path

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.enrique import _act as enrique_act
from app.specialists.enrique.graph import _act


class FakeElevenLabsClient:
    def list_voices(self) -> list[dict[str, object]]:
        return [
            {
                "voice_id": "voice-alpha",
                "name": "Alpha",
                "preview_url": "https://cdn.eleven.test/alpha.mp3",
                "labels": {"tone": "clear"},
            }
        ]

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        return f"{voice_id}:{text}".encode()


def _build_state(cache_prefix: str) -> RunState:
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


def test_enrique_act_returns_voice_and_assembly_receipts(tmp_path: Path) -> None:
    state = _build_state(
        json.dumps(
            {
                "bundle_path": str(tmp_path),
                "segments": [{"segment_id": "seg-01", "text": "Welcome to renal physiology."}],
            }
        )
    )

    update = enrique_act.act(state, client=FakeElevenLabsClient())  # type: ignore[arg-type]
    output = json.loads(update["cache_state"]["cache_prefix"])

    assert output["specialist_id"] == "enrique"
    assert output["gate_id"] == "G2"
    assert output["voice_selection"]["selected_voice_id"] == "voice-alpha"
    assert output["narration_outputs"][0]["audio_path"].endswith("seg-01.mp3")


def test_graph_act_delegates_to_enrique_act(monkeypatch) -> None:
    called: list[RunState] = []

    def _fake_act(state: RunState) -> dict[str, object]:
        called.append(state)
        return {}

    monkeypatch.setattr("app.specialists.enrique.graph._enrique_act_impl.act", _fake_act)
    state = _build_state("{}")
    assert _act(state) == {}
    assert called == [state]


def test_enrique_act_loc_budget() -> None:
    source = inspect.getsource(enrique_act.act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 80
