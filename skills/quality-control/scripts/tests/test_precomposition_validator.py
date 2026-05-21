from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "precomposition_validator.py"
)
SPEC = importlib.util.spec_from_file_location("precomposition_validator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_validate_precomposition_passes_complete_static_bundle(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:01.500 --> 00:00:03.000\nHello clinicians\n",
    )
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
                {
                    "id": "seg-01",
                    "narration_text": "Hello clinicians this lesson welcomes you to innovation practice.",
                    "narration_duration": 4.0,
                    "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                    "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                    "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "motion_type": "static",
                "sfx_file": None,
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "pass"
    assert result["dimension_scores"]["audio_quality"]["status"] == "pass"
    assert result["dimension_scores"]["composition_integrity"]["status"] == "pass"


def test_validate_precomposition_fails_wpm_and_motion_mismatch(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    motion = tmp_path / "motion" / "seg-01.mp4"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:01.500 --> 00:00:02.000\nRapid speech here\n",
    )
    _write_bytes(visual, b"png")
    _write_bytes(motion, b"mp4")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": " ".join(["word"] * 40),
                "narration_duration": 10.0,
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "motion_type": "video",
                "motion_asset_path": str(motion.relative_to(tmp_path)).replace("\\", "/"),
                "motion_duration_seconds": 3.0,
                "sfx_file": None,
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "fail"
    descriptions = [finding["description"] for finding in result["findings"]]
    assert any("Narration pace" in description for description in descriptions)
    assert any("Motion duration mismatch" in description for description in descriptions)


def test_validate_precomposition_downgrades_wpm_when_script_plan_already_implies_it(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:01.500 --> 00:00:02.000\nRapid speech here\n",
    )
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": " ".join(["word"] * 80),
                "duration_estimate_seconds": 45.0,
                "narration_duration": 25.0,
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "motion_type": "static",
                "sfx_file": None,
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "pass_with_notes"
    assert result["findings"] == []
    assert any("Review Irene runtime planning" in note for note in result["notes"])


def test_validate_precomposition_fails_negative_timing_values(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:04.000\nTiming check text\n",
    )
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": "Timing check text for non-negative guardrail.",
                "narration_duration": 4.0,
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "bridge_type": "none",
                "onset_delay": -0.1,
                "dwell": 0.2,
                "cluster_gap": 0.0,
                "transition_buffer": 0.1,
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "fail"
    descriptions = [finding["description"] for finding in result["findings"]]
    assert any("onset_delay must be a non-negative number" in description for description in descriptions)


def test_validate_precomposition_fails_cluster_gap_without_boundary_bridge(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:04.000\nCluster gap check text\n",
    )
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": "Cluster gap check text with invalid bridge pairing.",
                "narration_duration": 4.0,
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "bridge_type": "intro",
                "onset_delay": 0.0,
                "dwell": 0.0,
                "cluster_gap": 0.4,
                "transition_buffer": 0.1,
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "fail"
    descriptions = [finding["description"] for finding in result["findings"]]
    assert any("cluster_gap is only valid on cluster-boundary segments" in description for description in descriptions)


def test_validate_precomposition_fails_non_numeric_narration_duration(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(vtt, "WEBVTT\n\n1\n00:00:00.000 --> 00:00:02.000\nNarration\n")
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": "Narration content",
                "narration_duration": "abc",
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "motion_type": "static",
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "fail"
    descriptions = [finding["description"] for finding in result["findings"]]
    assert any("narration_duration must be numeric" in description for description in descriptions)


def test_validate_precomposition_accepts_vtt_cue_settings(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:04.000 align:start position:0%\none two three four five six seven eight nine ten\n",
    )
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": "one two three four five six seven eight nine ten",
                "narration_duration": 4.0,
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "motion_type": "static",
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "pass"


def test_validate_precomposition_flags_non_numeric_duration_estimate(tmp_path: Path) -> None:
    audio = tmp_path / "audio" / "seg-01.mp3"
    vtt = tmp_path / "captions" / "seg-01.vtt"
    visual = tmp_path / "visuals" / "seg-01.png"
    _write_text(audio, "fake mp3")
    _write_text(
        vtt,
        "WEBVTT\n\n1\n00:00:00.000 --> 00:00:04.000\nNarration with estimate issue\n",
    )
    _write_bytes(visual, b"png")

    manifest_path = tmp_path / "segment-manifest.yaml"
    manifest = {
        "segments": [
            {
                "id": "seg-01",
                "narration_text": "Narration with estimate issue",
                "narration_duration": 4.0,
                "duration_estimate_seconds": "not-a-number",
                "narration_file": str(audio.relative_to(tmp_path)).replace("\\", "/"),
                "narration_vtt": str(vtt.relative_to(tmp_path)).replace("\\", "/"),
                "visual_file": str(visual.relative_to(tmp_path)).replace("\\", "/"),
                "motion_type": "static",
            }
        ]
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    result = MODULE.validate_precomposition(manifest_path, repo_root=tmp_path)

    assert result["status"] == "fail"
    descriptions = [finding["description"] for finding in result["findings"]]
    assert any("duration_estimate_seconds must be numeric" in description for description in descriptions)
