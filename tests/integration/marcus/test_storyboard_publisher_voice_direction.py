"""P5 Step 3 — Storyboard B carries per-segment ``voice_direction`` before spend.

Authority:
`_bmad-output/planning-artifacts/p5-directed-voice-audition-rubric-2026-06-27.md`
§8 (Storyboard B display checklist) + §7 (precedence);
`_bmad-output/planning-artifacts/p5-directed-voice-implementation-control-cards-2026-06-27.md`
Card 2 (Must-Show / Complete-When);
`_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
§F MUR-3 (display↔dispatch parity).

This module pins the PUBLISHER seam leg: ``_write_segment_manifest_for_b``
re-attaches ``voice_direction`` from the matching Pass-2 delta AFTER the frozen
``join_narration_segments`` neck drops it — exactly the way cluster labels are
re-attached. CRITICAL byte-stability guard: a delta WITHOUT ``voice_direction``
(flag-OFF / non-directed run) must produce a manifest with NO ``voice_direction``
key (byte-identical to today; additive-only).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.marcus.orchestrator import storyboard_publisher


def _directed_irene_output() -> dict[str, object]:
    """Two segments: one DIRECTED (seg-01 carries a voice_direction) + one
    UNDIRECTED (seg-02 has no voice_direction) — mirrors the Step-2 annotation
    output shape (voice_direction is a model_dump(mode="json", exclude_none)
    dict attached onto the delta)."""
    return {
        "narration_script": [
            {"id": "seg-01", "narration_text": "Reflective synthesis narration."},
            {"id": "seg-02", "narration_text": "Plain baseline narration."},
        ],
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-01"}],
                "voice_direction": {
                    "schema_version": "voice-direction.v1",
                    "render_strategy": "tts",
                    "emotional_tone": "reflective",
                    "pace": "slower",
                    "energy": "low",
                    "source": "cd-authored",
                },
            },
            {
                "id": "seg-02",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-02"}],
                # NO voice_direction — the undirected / flag-OFF shape.
            },
        ],
    }


def _undirected_irene_output() -> dict[str, object]:
    """Two segments, NEITHER carrying voice_direction (the legacy / flag-OFF
    manifest shape)."""
    return {
        "narration_script": [
            {"id": "seg-01", "narration_text": "Opening narration."},
            {"id": "seg-02", "narration_text": "Closing narration."},
        ],
        "segment_manifest_deltas": [
            {
                "id": "seg-01",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-01"}],
            },
            {
                "id": "seg-02",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-02"}],
            },
        ],
    }


def _read_segments(manifest_path: Path) -> dict[str, dict[str, object]]:
    loaded = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return {seg["id"]: seg for seg in loaded["segments"]}


def test_voice_direction_carries_into_segment_manifest_b(tmp_path: Path) -> None:
    """A directed segment carries its voice_direction through the export
    projection (re-attached after the frozen join drops it)."""
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=_directed_irene_output(),
    )
    segs = _read_segments(manifest_path)

    directed = segs["seg-01"]
    assert isinstance(directed.get("voice_direction"), dict)
    vd = directed["voice_direction"]
    assert vd["emotional_tone"] == "reflective"
    assert vd["pace"] == "slower"
    assert vd["energy"] == "low"
    assert vd["source"] == "cd-authored"


def test_undirected_segment_has_no_voice_direction_key(tmp_path: Path) -> None:
    """A segment whose delta carries no voice_direction must NOT gain a
    voice_direction key (additive-only; missing stays missing)."""
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=_directed_irene_output(),
    )
    segs = _read_segments(manifest_path)
    assert "voice_direction" not in segs["seg-02"]


def test_flag_off_manifest_has_no_voice_direction_anywhere(tmp_path: Path) -> None:
    """CRITICAL byte-stability guard: when NO delta carries voice_direction
    (flag-OFF / non-directed run), the serialized manifest contains no
    voice_direction substring at all — the re-attach adds nothing, so the
    output is byte-identical to today."""
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output=_undirected_irene_output(),
    )
    text = manifest_path.read_text(encoding="utf-8")
    assert "voice_direction" not in text


def _vd(tone: str) -> dict[str, object]:
    return {
        "schema_version": "voice-direction.v1",
        "render_strategy": "tts",
        "emotional_tone": tone,
        "source": "cd-authored",
    }


def test_empty_id_deltas_do_not_misroute_voice_direction(tmp_path: Path) -> None:
    """Edge #4: two deltas with EMPTY ids carrying DIFFERENT directions must NOT
    mis-attribute a voice_direction to either segment — an empty id cannot be
    matched unambiguously, so spend-critical direction is withheld rather than
    routed to the wrong segment."""
    irene_output = {
        "narration_script": [
            {"id": "", "narration_text": "A."},
            {"id": "", "narration_text": "B."},
        ],
        "segment_manifest_deltas": [
            {
                "id": "",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-01"}],
                "voice_direction": _vd("warm"),
            },
            {
                "id": "",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-02"}],
                "voice_direction": _vd("concerned"),
            },
        ],
    }
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path, irene_output=irene_output
    )
    for seg in _read_segments(manifest_path).values():
        assert "voice_direction" not in seg


def test_duplicate_id_deltas_do_not_misroute_voice_direction(tmp_path: Path) -> None:
    """Edge #4: a DUPLICATE non-empty id is equally ambiguous (last-write-wins
    index) — withhold the re-attach rather than mis-attribute it."""
    irene_output = {
        "narration_script": [
            {"id": "dup", "narration_text": "A."},
            {"id": "dup", "narration_text": "B."},
        ],
        "segment_manifest_deltas": [
            {
                "id": "dup",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-01"}],
                "voice_direction": _vd("warm"),
            },
            {
                "id": "dup",
                "timing_role": "concept-build",
                "bridge_type": "intro",
                "visual_references": [{"perception_source": "slide-02"}],
                "voice_direction": _vd("concerned"),
            },
        ],
    }
    manifest_path = storyboard_publisher._write_segment_manifest_for_b(
        run_dir=tmp_path, irene_output=irene_output
    )
    for seg in _read_segments(manifest_path).values():
        assert "voice_direction" not in seg
