from __future__ import annotations

from pathlib import Path
from typing import Any

from app.specialists.wanda import _act as wanda_act
from tests.parity._sanctum_parity_base import REPO_ROOT


class FakeWondercraftAudioBedClient:
    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []

    def check_connectivity(self) -> dict[str, Any]:
        return {"reachable": True, "status_code": 200}

    def generate_audio_bed(self, **kwargs: Any) -> dict[str, Any]:
        self.requests.append(kwargs)
        return {
            "id": "wc-bed-001",
            "url": "https://cdn.wondercraft.test/bed-focused-ambient.mp3",
            "format": "mp3",
            "audio_bytes": b"fixture-audio",
            "cost_usd": 0.12,
        }


def test_audio_bed_generation_uses_vcr_cassette_and_audio_track(tmp_path: Path) -> None:
    cassette = (
        REPO_ROOT
        / "tests"
        / "fixtures"
        / "specialist-replay"
        / "wanda"
        / "wondercraft_audio_bed_happy_path.yaml"
    )
    assert cassette.is_file()
    client = FakeWondercraftAudioBedClient()

    verdict = wanda_act.generate_audio_beds(
        {
            "bundle_path": str(tmp_path),
            "storyboard": {"audio_track": {"mood": "focused", "genre": "ambient"}},
            "narration_manifest": {"segments": [{"text": "A calm learning sequence."}]},
        },
        client=client,  # type: ignore[arg-type]
    )

    bed = verdict["storyboard_audio_track"]["beds"][0]
    assert Path(bed["audio_path"]).is_file()
    assert Path(bed["audio_path"]).parts[-4:] == (
        "assembly-bundle",
        "audio",
        "beds",
        "bed-focused-ambient.mp3",
    )
    assert client.requests[0]["prompt"] == "A calm learning sequence."
    assert verdict["compositor_invocation"]["audio_bed_paths"] == [bed["audio_path"]]
