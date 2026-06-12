"""G3B storyboard-B body twins (PIN-B3, party consensus 2026-06-12).

Finding #10 retired with evidence: the old G3B→"post" mapping crashed live
at Trial-3 cycle-4 node 08B (`sensory.input.missing` — the post body demands
a §14 composed artifact_path that cannot exist before composition). G3B now
reviews Storyboard B = Irene Pass-2 narration joined against Gary's REAL
slide roster. The "post" body remains reachable via gate_phase fallback for
true post-composition dispatches — that leg keeps its own test below.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.specialists.quinn_r._act import GATE_MODES
from app.specialists.quinn_r.graph import _act
from app.specialists.quinn_r.quality_control_dispatch import (
    StoryboardBInputError,
    run_storyboard_b_review,
)
from tests.specialists.quinn_r.conftest import make_state


def _grounded_payload(tmp_path: Path) -> dict[str, Any]:
    return {
        "gate_id": "G3B",
        "gate_phase": "pre-composition",
        "runs_root": str(tmp_path),
        "gary_slide_output": [
            {"slide_id": "slide-01", "file_path": "s1.png"},
            {"slide_id": "slide-02", "file_path": "s2.png"},
        ],
        "narration_script": [
            {"id": "seg-1", "narration_text": "Opening narration."},
            {"id": "seg-2", "narration_text": "Closing narration."},
        ],
        "segment_manifest_deltas": [
            {
                "id": "seg-1",
                "visual_references": [{"perception_source": "slide-01"}],
            },
            {
                "id": "seg-2",
                "visual_references": [{"perception_source": "slide-02"}],
            },
        ],
    }


def test_g3b_no_longer_maps_to_the_post_body() -> None:
    # Red twin of the cycle-4 live crash: "post" at 08B is the retired defect.
    assert GATE_MODES["G3B"] == "storyboard_b"


def test_g3b_reviews_storyboard_b_against_real_roster(tmp_path: Path) -> None:
    state = make_state(json.dumps(_grounded_payload(tmp_path)))
    verdict = json.loads(_act(state)["cache_state"]["cache_prefix"])["quinn_r_review"]
    assert verdict["mode"] == "storyboard-b-review"
    assert verdict["status"] == "reviewed"
    assert verdict["blocking"] == []
    assert verdict["coverage"] == {"roster_size": 2, "covered": 2, "segments": 2}


def test_g3b_coverage_gap_blocks(tmp_path: Path) -> None:
    payload = _grounded_payload(tmp_path)
    payload["segment_manifest_deltas"] = payload["segment_manifest_deltas"][:1]
    verdict = run_storyboard_b_review(payload)
    assert verdict["status"] == "blocked"
    assert any(f["check"] == "coverage" for f in verdict["blocking"])


def test_g3b_orphan_reference_blocks(tmp_path: Path) -> None:
    payload = _grounded_payload(tmp_path)
    payload["segment_manifest_deltas"][1]["visual_references"] = [
        {"perception_source": "slide-99"}
    ]
    verdict = run_storyboard_b_review(payload)
    assert verdict["status"] == "blocked"
    assert any(f["check"] == "roster-join" for f in verdict["blocking"])
    assert any(f["check"] == "coverage" for f in verdict["blocking"])


@pytest.mark.parametrize("missing", ["gary_slide_output", "narration_script"])
def test_g3b_input_starvation_raises_recoverable_family(
    tmp_path: Path, missing: str
) -> None:
    payload = _grounded_payload(tmp_path)
    del payload[missing]
    with pytest.raises(StoryboardBInputError) as excinfo:
        run_storyboard_b_review(payload)
    assert excinfo.value.tag == "quinn_r.storyboard_b.input-missing"


def test_post_body_remains_reachable_via_gate_phase(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    artifact = tmp_path / "assembled.txt"
    artifact.write_text("assembled", encoding="utf-8")
    monkeypatch.setattr(
        "app.specialists.quinn_r._act.dispatch_to_sensory_bridges",
        lambda **_: {"confidence": "HIGH", "layout_description": "assembled video"},
    )
    monkeypatch.setattr(
        "app.specialists.quinn_r._act.run_postcomposition_validators",
        lambda **_: {"status": "ok", "dimension_scores": {"composition": "PASS"}},
    )
    state = make_state(
        json.dumps(
            {
                "gate_phase": "post-composition",
                "runs_root": str(tmp_path),
                "artifact_path": str(artifact),
                "modality": "video",
            }
        )
    )
    verdict = json.loads(_act(state)["cache_state"]["cache_prefix"])["quinn_r_review"]
    assert verdict["mode"] == "post-composition"
    assert verdict["perception"]["confidence"] == "HIGH"
