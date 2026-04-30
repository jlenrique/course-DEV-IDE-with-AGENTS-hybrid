from __future__ import annotations

import json
from pathlib import Path

from app.specialists.enrique import _act as enrique_act


class FakeElevenLabsClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def list_voices(self) -> list[dict[str, object]]:
        return [
            {"voice_id": "narrator", "name": "Narrator", "preview_url": "https://cdn.test/n.mp3"}
        ]

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        self.calls.append((text, voice_id))
        return f"mp3:{voice_id}:{text}".encode()


def test_assembly_bundle_builds_audio_captions_and_progress(tmp_path: Path, capsys) -> None:
    client = FakeElevenLabsClient()
    payload = {
        "bundle_path": str(tmp_path),
        "segments": [
            {"segment_id": "seg-01", "text": "First narration segment.", "duration_seconds": 2.5},
            {"segment_id": "seg-02", "text": "Second narration segment.", "duration_seconds": 3.0},
        ],
    }

    result = enrique_act.generate_enrique_outputs(payload, client=client)  # type: ignore[arg-type]

    assert len(client.calls) == 2
    for segment_id in ("seg-01", "seg-02"):
        assert (tmp_path / "assembly-bundle" / "audio" / f"{segment_id}.mp3").is_file()
        caption = tmp_path / "assembly-bundle" / "captions" / f"{segment_id}.vtt"
        assert caption.is_file()
        assert caption.read_text(encoding="utf-8").startswith("WEBVTT")
    captured = capsys.readouterr()
    assert "Enrique segment seg-01 [1/2] OK" in captured.err
    assert "duration=2.5s" in captured.err
    assert result["compositor_invocation"]["audio_paths"][0].endswith("seg-01.mp3")
    preview = json.loads(
        (tmp_path / "voice-selection" / "voice-preview-options.json").read_text(encoding="utf-8")
    )
    assert preview["recommended_voice_id"] == "narrator"
