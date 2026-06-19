from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.quinn_r.graph import ModeMismatchError, _act
from tests.specialists.quinn_r.conftest import make_state


def _payload(tmp_path: Path, gate_id: str) -> str:
    return json.dumps(
        {
            "gate_id": gate_id,
            # dp-v1.1: G3B is pre-composition (storyboard-B review) — the
            # post-composition mapping was the cycle-4 live crash.
            "gate_phase": "pre-composition",
            "runs_root": str(tmp_path),
            "slides": [{"slide_id": "s1", "title": "Intro"}],
            "perception_artifacts": [
                {
                    "artifact_path": "fixtures/s1.png",
                    "card_number": 1,
                    "confidence": "HIGH",
                    "coverage": "perceived",
                    "extracted_text": "Intro",
                    "layout_description": "Intro title slide.",
                    "slide_id": "s1",
                    "slide_title": "Intro",
                    "text_blocks": [{"text": "Intro"}],
                    "visual_elements": [{"kind": "title", "label": "intro title"}],
                }
            ],
            "narration_segments": [
                {
                    "slide_id": "s1",
                    "text": "ten words here now",
                    "duration_seconds": 2,
                }
            ],
            "vtt_text": "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\ncaption\n",
            "narration_profile_controls": {"target_wpm": 120},
            "gary_slide_output": [{"slide_id": "s1", "file_path": "s1.png"}],
            "narration_script": [{"id": "seg-1", "narration_text": "Opening."}],
            "segment_manifest_deltas": [
                {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]}
            ],
        }
    )


@pytest.mark.parametrize(
    ("gate_id", "mode"),
    [("G2C", "pre-composition"), ("G5", "g5-pre-composition-qa"), ("G3B", "storyboard-b-review")],
)
def test_quinn_r_dispatches_by_gate_id(gate_id: str, mode: str, tmp_path: Path) -> None:
    update = _act(make_state(_payload(tmp_path, gate_id)))
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["quinn_r_review"]["mode"] == mode


def test_quinn_r_rejects_wrong_body_for_gate(tmp_path: Path) -> None:
    payload = json.loads(_payload(tmp_path, "G3B"))
    payload["gate_phase"] = "post-composition"
    with pytest.raises(ModeMismatchError):
        _act(make_state(json.dumps(payload)))
