from __future__ import annotations

import json
from typing import Any

import pytest

from app.specialists.vera.graph import _act
from tests.specialists.vera._act_helpers import build_vera_state


@pytest.mark.timeout(30)
def test_g3_storyboard_a_records_confidence_per_modality(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    def _fake_dispatch(**kwargs: Any) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "modality": kwargs["modality"],
            "artifact_path": str(kwargs.get("artifact_path") or ""),
            "confidence": "MEDIUM" if kwargs["modality"] == "audio" else "HIGH",
        }

    monkeypatch.setattr("app.specialists.vera.graph.dispatch_to_sensory_bridges", _fake_dispatch)
    update = _act(
        build_vera_state(
            {
                "gate_id": "G3",
                "image_artifact_path": "storyboard-a.png",
                "audio_artifact_path": "narration.mp3",
                "motion_artifact_path": "motion.mp4",
                "runs_root": str(tmp_path),
            }
        )
    )
    rubric = json.loads(update["cache_state"]["cache_prefix"])["vera_finding"]["rubrics"]["G3"]
    assert rubric["storyboard"] == "A"
    assert rubric["confidence_rubric"]["visual"]["score"] == 1.0
    assert rubric["confidence_rubric"]["audio"]["score"] == 0.7
    assert rubric["confidence_rubric"]["motion"]["confidence"] == "HIGH"
