"""Audio-segment arc twins (dp-v1.2, party consensus 2026-06-12).

Cycle-5 defects pinned red/green:
1. Enrique ungrounded → zero audio, silent skip (PIN-AUD-1R/1G);
2. quinn_r G5 fabricated slide-1 roster (PIN-AUD-2R/2G);
3. bare-ValueError crash class (taxonomy suite owns 3T; the lost-progress
   integration twin 3P lives in the runner suite).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.specialists.compositor._act import run_compositor_pipeline
from app.specialists.enrique._act import EnriqueActError, generate_enrique_outputs
from app.specialists.quinn_r._act import CoverageGapError, run_g5_checks
from app.specialists.quinn_r.quality_control_dispatch import (
    StoryboardBInputError,
    run_g5_grounding,
)

NARRATION = [
    {"id": "seg-1", "narration_text": "Opening narration for slide one."},
    {"id": "seg-2", "narration_text": "Closing narration for slide two."},
]
DELTAS = [
    {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
    {"id": "seg-2", "visual_references": [{"perception_source": "s2"}]},
]
SLIDES = [
    {"slide_id": "s1", "file_path": "s1.png"},
    {"slide_id": "s2", "file_path": "s2.png"},
]


class _FakeElevenLabs:
    def __init__(self) -> None:
        self.tts_calls: list[tuple[str, str]] = []

    def list_voices(self) -> list[dict[str, Any]]:
        return [{"voice_id": "v-1", "name": "Test Voice"}]

    def text_to_speech(self, text: str, voice_id: str) -> bytes:
        self.tts_calls.append((text, voice_id))
        return b"ID3fake-mp3-bytes"


def test_enrique_grounded_synthesizes_per_joined_segment(tmp_path: Path) -> None:
    client = _FakeElevenLabs()
    result = generate_enrique_outputs(
        {
            "bundle_path": str(tmp_path),
            "narration_script": NARRATION,
            "segment_manifest_deltas": DELTAS,
        },
        client=client,
    )
    outputs = result["narration_outputs"]
    assert [row["segment_id"] for row in outputs] == ["seg-1", "seg-2"]
    assert [row["slide_id"] for row in outputs] == ["s1", "s2"]
    assert all(row["duration_source"] == "estimated-chars" for row in outputs)
    assert len(client.tts_calls) == 2
    for row in outputs:
        assert Path(row["audio_path"]).is_file()
        assert Path(row["caption_path"]).is_file()
    assert result["compositor_invocation"]["audio_paths"] == [
        row["audio_path"] for row in outputs
    ]


def test_enrique_join_drop_refuses_pre_spend(tmp_path: Path) -> None:
    client = _FakeElevenLabs()
    with pytest.raises(EnriqueActError) as excinfo:
        generate_enrique_outputs(
            {
                "bundle_path": str(tmp_path),
                "narration_script": NARRATION,
                # seg-2 delta lost its slide reference → join drops it →
                # paid audio would not cover the approved narration.
                "segment_manifest_deltas": [DELTAS[0], {"id": "seg-2", "visual_references": []}],
            },
            client=client,
        )
    assert excinfo.value.tag == "elevenlabs.join.dropped-segments"
    assert client.tts_calls == []  # refused BEFORE spend


def test_enrique_phantom_delta_refuses_pre_spend(tmp_path: Path) -> None:
    """PIN (dp-v1.2 rider Amelia R1): a delta id with NO matching narration
    segment joins with empty text; pre-fix, the TTS loop skipped it silently
    (no mp3, no error) while G5 counted its slide as covered. Refuse BEFORE
    spend, naming the phantom id."""
    client = _FakeElevenLabs()
    with pytest.raises(EnriqueActError) as excinfo:
        generate_enrique_outputs(
            {
                "bundle_path": str(tmp_path),
                # seg-2 exists in the manifest deltas but not in narration.
                "narration_script": [NARRATION[0]],
                "segment_manifest_deltas": DELTAS,
            },
            client=client,
        )
    assert excinfo.value.tag == "elevenlabs.join.empty-narration-text"
    assert "seg-2" in str(excinfo.value)
    assert client.tts_calls == []  # refused BEFORE spend


def test_enrique_whitespace_narration_is_phantom(tmp_path: Path) -> None:
    client = _FakeElevenLabs()
    with pytest.raises(EnriqueActError) as excinfo:
        generate_enrique_outputs(
            {
                "bundle_path": str(tmp_path),
                "narration_script": [
                    NARRATION[0],
                    {"id": "seg-2", "narration_text": "   "},
                ],
                "segment_manifest_deltas": DELTAS,
            },
            client=client,
        )
    assert excinfo.value.tag == "elevenlabs.join.empty-narration-text"
    assert "seg-2" in str(excinfo.value)
    assert client.tts_calls == []


def test_enrique_voice_only_dispatch_stays_voice_only(tmp_path: Path) -> None:
    # Nodes 11/11B carry no narration projections by design (single shared
    # act body; only node 12 synthesizes). No segments → no TTS.
    client = _FakeElevenLabs()
    result = generate_enrique_outputs({"bundle_path": str(tmp_path)}, client=client)
    assert client.tts_calls == []
    assert "narration_outputs" not in result
    assert result["voice_selection"]["selected_voice_id"] == "v-1"


def test_g5_grounding_builds_segments_with_enrique_durations(tmp_path: Path) -> None:
    caption = tmp_path / "seg-1.vtt"
    caption.write_text("WEBVTT\n", encoding="utf-8")
    grounded = run_g5_grounding(
        {
            "slides": SLIDES,
            "narration_script": NARRATION,
            "segment_manifest_deltas": DELTAS,
            "narration_outputs": [
                {
                    "segment_id": "seg-1",
                    "duration_seconds": 12.5,
                    "duration_source": "estimated-chars",
                    "caption_path": str(caption),
                }
            ],
        }
    )
    segments = grounded["narration_segments"]
    assert [s["slide_id"] for s in segments] == ["s1", "s2"]
    assert segments[0]["duration_seconds"] == 12.5
    assert grounded["wpm_durations_estimated"] is True
    # Full pipeline: grounded payload passes the real checks.
    verdict = run_g5_checks(grounded)
    assert verdict["blocking"] == []


def test_g5_phantom_delta_drops_to_coverage_gap(tmp_path: Path) -> None:
    """PIN twin (dp-v1.2 rider Amelia R1): at G5 the phantom row drops
    BEFORE coverage counting, so the silent slide raises CoverageGapError
    naming it — pre-fix it counted as covered while enrique skipped its
    audio."""
    caption = tmp_path / "seg-1.vtt"
    caption.write_text("WEBVTT\n", encoding="utf-8")
    grounded = run_g5_grounding(
        {
            "slides": SLIDES,
            "narration_script": [NARRATION[0]],  # seg-2 is a phantom delta
            "segment_manifest_deltas": DELTAS,
            "narration_outputs": [
                {
                    "segment_id": "seg-1",
                    "duration_seconds": 12.5,
                    "duration_source": "estimated-chars",
                    "caption_path": str(caption),
                }
            ],
        }
    )
    assert [s["slide_id"] for s in grounded["narration_segments"]] == ["s1"]
    assert grounded["phantom_segment_ids_dropped"] == ["seg-2"]  # witness trail
    with pytest.raises(CoverageGapError) as excinfo:
        run_g5_checks(grounded)
    assert "s2" in str(excinfo.value)


def test_g5_all_phantom_raises_input_missing() -> None:
    """Every delta phantom → zero segments after the pre-coverage drop →
    the existing starvation raise fires (never an empty-but-passing G5)."""
    with pytest.raises(StoryboardBInputError) as excinfo:
        run_g5_grounding(
            {
                "slides": SLIDES,
                "narration_script": [{"id": "seg-9", "narration_text": "Unjoined."}],
                "segment_manifest_deltas": DELTAS,
            }
        )
    assert excinfo.value.tag == "quinn_r.g5.input-missing"


def test_g5_grounding_starved_raises(tmp_path: Path) -> None:
    with pytest.raises(StoryboardBInputError) as excinfo:
        run_g5_grounding({"slides": SLIDES})
    assert excinfo.value.tag == "quinn_r.g5.input-missing"


@pytest.mark.parametrize("caption", ["gone.vtt", None])
def test_g5_missing_or_absent_caption_raises(tmp_path: Path, caption: str | None) -> None:
    """Winston MUST-FIX 1: a synthesized segment with a MISSING caption file
    OR no caption_path at all is a failure — the check exists precisely for
    the producer that doesn't write one."""
    row: dict[str, object] = {
        "segment_id": "seg-1",
        "audio_path": str(tmp_path / "seg-1.mp3"),
    }
    if caption:
        row["caption_path"] = str(tmp_path / caption)
    with pytest.raises(StoryboardBInputError) as excinfo:
        run_g5_grounding(
            {
                "slides": SLIDES,
                "narration_script": NARRATION,
                "segment_manifest_deltas": DELTAS,
                "narration_outputs": [row],
            }
        )
    assert excinfo.value.tag == "quinn_r.g5.caption-missing"


def test_g5_fabricated_default_is_retired() -> None:
    """PIN-AUD-2R: the slide-1 phantom roster is gone — behavior AND source."""
    import inspect

    from app.specialists.quinn_r import _act as act_module

    with pytest.raises(StoryboardBInputError) as excinfo:
        act_module._slides({})
    assert excinfo.value.tag == "quinn_r.slides.starved"
    assert '[{"slide_id": "slide-1"}]' not in inspect.getsource(act_module)


def test_compositor_derives_audio_from_invocation(tmp_path: Path) -> None:
    png = tmp_path / "s1.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\nx")
    result = run_compositor_pipeline(
        {
            "bundle_path": str(tmp_path / "bundle"),
            "gary_slide_output": [{"slide_id": "s1", "file_path": str(png)}],
            "motion_receipts": [],
            "compositor_invocation": {
                "audio_paths": [str(tmp_path / "seg-1.mp3")],
                "caption_paths": [str(tmp_path / "seg-1.vtt")],
            },
        }
    )
    guide = Path(result["assembly_guide_path"]).read_text(encoding="utf-8")
    assert "seg-1.mp3" in guide
    assert "s1.png" in guide or "visuals/s1.png" in guide
    assert json.loads(json.dumps(result["synced_assets"]))["visuals"]["s1"]
