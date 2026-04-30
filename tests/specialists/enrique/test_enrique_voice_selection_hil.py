from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.enrique import _act as enrique_act


class FakeElevenLabsClient:
    def list_voices(self) -> list[dict[str, object]]:
        return [
            {
                "voice_id": "voice-a",
                "name": "Alicia",
                "preview_url": "https://cdn.eleven.test/a.mp3",
                "labels": {"tone": "warm", "pace": "measured"},
            },
            {
                "voice_id": "voice-b",
                "name": "Ben",
                "preview_url": "https://cdn.eleven.test/b.mp3",
                "labels": {"tone": "clear"},
            },
        ]


@pytest.mark.parametrize(
    "selection,expected_voice",
    [
        (
            {"selected_voice_id": "voice-b", "operator_id": "juan", "rationale": "clearer"},
            "voice-b",
        ),
        ({}, "voice-a"),
    ],
)
def test_voice_selection_hil_artifacts(
    tmp_path: Path, selection: dict[str, str], expected_voice: str
) -> None:
    payload = {"bundle_path": str(tmp_path), "voice_selection": selection}

    result = enrique_act.build_voice_selection_contract(
        payload,
        client=FakeElevenLabsClient(),  # type: ignore[arg-type]
    )

    selection_dir = tmp_path / "voice-selection"
    preview_path = selection_dir / "voice-preview-options.json"
    review_path = selection_dir / "voice-selection-review.md"
    selected_path = selection_dir / "voice-selection.json"
    assert preview_path.is_file()
    assert review_path.is_file()
    assert selected_path.is_file()
    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    selected = json.loads(selected_path.read_text(encoding="utf-8"))
    assert preview["voices"][0] == {
        "voice_id": "voice-a",
        "voice_name": "Alicia",
        "sample_audio_url": "https://cdn.eleven.test/a.mp3",
        "characteristics": {"tone": "warm", "pace": "measured"},
        "eta_seconds": 30.0,
        "cost_per_1k_chars": 0.3,
    }
    assert "[recommended]" in review_path.read_text(encoding="utf-8")
    assert selected["selected_voice_id"] == expected_voice
    assert result["voice_selection"]["selected_voice_id"] == expected_voice
