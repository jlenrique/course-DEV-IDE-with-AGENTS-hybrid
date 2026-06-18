"""Arc 3 (measured-durations, 2026-06-18): enrique probes the real synthesized
mp3 and labels its duration "measured", which arms G5's WPM raise against
reality. Dep-free frame-duration parser (no mutagen/ffprobe). Non-mp3 bytes
(fixtures) probe to None → fall back to provided/estimated, so folded/fixture
behavior is unchanged.
"""

from __future__ import annotations

from pathlib import Path

from app.specialists.enrique import _act as enrique_act
from app.specialists.enrique._act import _mp3_duration_seconds

# One MPEG-1 Layer III frame @ 128 kbps / 44100 Hz: header FF FB 90 00, frame
# length = int(144*128000/44100)+0 = 417 bytes, duration = 1152/44100 = 0.026 s.
_FRAME = bytes([0xFF, 0xFB, 0x90, 0x00]) + bytes(413)


def test_probe_returns_none_for_non_mp3_bytes() -> None:
    # The fixture-fallback guarantee: a non-mp3 payload yields None so the
    # caller keeps its estimate (zero behavior change on fixtures).
    assert _mp3_duration_seconds(b"mp3:narrator:hello") is None
    assert _mp3_duration_seconds(b"") is None
    assert _mp3_duration_seconds(b"\x00" * 500) is None


def test_probe_sums_frame_durations() -> None:
    assert _mp3_duration_seconds(_FRAME) == 0.026
    assert _mp3_duration_seconds(_FRAME * 38) == 0.993  # ~1 second, summed


def test_probe_skips_id3v2_tag() -> None:
    # ID3v2 header: "ID3" + ver(2) + flags(1) + syncsafe size(4). 20-byte tag.
    id3 = b"ID3\x04\x00\x00" + bytes([0, 0, 0, 20]) + bytes(20)
    assert _mp3_duration_seconds(id3 + _FRAME) == 0.026


class _RealMp3Client:
    """Returns a genuine multi-frame mp3 so the probe yields a measured value."""

    def list_voices(self) -> list[dict[str, object]]:
        return [{"voice_id": "narrator", "name": "Narrator", "preview_url": "https://cdn.test/n.mp3"}]

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        return _FRAME * 38  # ~0.993s of real mp3 frames


def test_enrique_labels_real_mp3_duration_measured(tmp_path: Path) -> None:
    # No duration_seconds in the payload: pre-Arc-3 this would be
    # "estimated-chars"; now the real-mp3 probe wins and labels it "measured".
    payload = {
        "bundle_path": str(tmp_path),
        "segments": [
            {"segment_id": "seg-01", "text": "A narration segment with several words here."}
        ],
    }
    result = enrique_act.generate_enrique_outputs(payload, client=_RealMp3Client())  # type: ignore[arg-type]
    row = result["narration_outputs"][0]
    assert row["duration_source"] == "measured"
    assert row["duration_seconds"] == 0.993  # from the mp3, not len/14


def test_fixture_bytes_fall_back_to_estimate_not_measured(tmp_path: Path) -> None:
    class _FakeBytesClient:
        def list_voices(self):
            return [{"voice_id": "narrator", "name": "Narrator", "preview_url": "https://cdn.test/n.mp3"}]

        def text_to_speech(self, text: str, voice_id: str) -> bytes:
            return f"mp3:{voice_id}:{text}".encode()

    payload = {
        "bundle_path": str(tmp_path),
        "segments": [{"segment_id": "seg-01", "text": "Some words here for the estimate."}],
    }
    result = enrique_act.generate_enrique_outputs(payload, client=_FakeBytesClient())  # type: ignore[arg-type]
    row = result["narration_outputs"][0]
    # Non-mp3 fixture bytes → probe None → estimate, never falsely "measured".
    assert row["duration_source"] == "estimated-chars"
