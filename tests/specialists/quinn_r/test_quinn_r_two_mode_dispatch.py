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
            "gate_phase": "post-composition" if gate_id == "G3B" else "pre-composition",
            # S0 fail-loud policy: the G3B post body's sensory dispatch now
            # requires a real artifact; tests must supply one.
            "artifact_path": "tests/fixtures/specialists/quinn_r/fixture_artifacts/sample.txt",
            "runs_root": str(tmp_path),
            "slides": [{"slide_id": "s1", "title": "Intro"}],
            "narration_segments": [
                {
                    "slide_id": "s1",
                    "text": "ten words here now",
                    "duration_seconds": 2,
                }
            ],
            "vtt_text": "WEBVTT\n\n00:00:00.000 --> 00:00:02.000\ncaption\n",
            "narration_profile_controls": {"target_wpm": 120},
        }
    )


@pytest.mark.parametrize(
    ("gate_id", "mode"),
    [("G2C", "pre-composition"), ("G5", "g5-pre-composition-qa"), ("G3B", "post-composition")],
)
def test_quinn_r_dispatches_by_gate_id(
    gate_id: str, mode: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # S0 fail-loud policy: G3B's sensory dispatch refuses missing/unreadable
    # artifacts, so the perception boundary is mocked here (the dedicated
    # G3B test owns that contract).
    monkeypatch.setattr(
        "app.specialists.quinn_r._act.dispatch_to_sensory_bridges",
        lambda **_: {"confidence": "HIGH", "layout_description": "mocked"},
    )
    monkeypatch.setattr(
        "app.specialists.quinn_r._act.run_postcomposition_validators",
        lambda **_: {"status": "ok", "dimension_scores": {"composition": "PASS"}},
    )
    update = _act(make_state(_payload(tmp_path, gate_id)))
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["quinn_r_review"]["mode"] == mode


def test_quinn_r_rejects_wrong_body_for_gate(tmp_path: Path) -> None:
    payload = json.loads(_payload(tmp_path, "G3B"))
    payload["gate_phase"] = "pre-composition"
    with pytest.raises(ModeMismatchError):
        _act(make_state(json.dumps(payload)))
