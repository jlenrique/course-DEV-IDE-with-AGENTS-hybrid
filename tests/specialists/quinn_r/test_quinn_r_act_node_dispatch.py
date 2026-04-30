from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from app.specialists.quinn_r.graph import (
    ModeMismatchError,
    QRRParseError,
    _act,
    _parse_qrr,
)
from tests.specialists.quinn_r.conftest import make_state


def _payload(tmp_path: Path, *, gate_id: str = "G2C") -> str:
    return json.dumps(
        {
            "gate_id": gate_id,
            "gate_phase": "post-composition" if gate_id == "G3B" else "pre-composition",
            "runs_root": str(tmp_path),
            "artifact_path": str(tmp_path / "assembled.mp4"),
            "modality": "video",
            "slides": [
                {
                    "slide_id": "s1",
                    "title": "Intro",
                    "narration_pointer": "narration/s1.vtt",
                    "motion_pointer": "motion/s1.mp4",
                    "evidence_block": "fixture",
                }
            ],
            "narration_profile_controls": {"target_wpm": 120},
            "vtt_text": "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nhello\n",
            "narration_segments": [
                {
                    "slide_id": "s1",
                    "text": "one two three four five six seven eight nine ten",
                    "duration_seconds": 5,
                    "motion_duration_seconds": 5.3,
                }
            ],
        }
    )


@pytest.mark.parametrize(
    "raw,expected",
    [
        (
            '{"status":"pass","severity":"low","summary":"ok","findings":[{"id":"1"}],"dimension_scores":{"accessibility":"PASS"}}',
            "pass",
        ),
        (
            '{"status":"warning","severity":"medium","summary":"ok","findings":[{"id":"1"}],"dimension_scores":{"accessibility":"WARN"}}',
            "warn",
        ),
        (
            '```json\n{"status":"failed","severity":"high","summary":"ok","findings":[{"id":"1"}],"dimension_scores":{"accessibility":"WARN"}}\n```',
            "fail",
        ),
    ],
)
def test_parse_qrr_ok(raw: str, expected: str) -> None:
    out = _parse_qrr(raw)
    assert out["status"] == expected


def test_parse_qrr_branch_error_tag() -> None:
    with pytest.raises(QRRParseError, match="parse failed") as exc_info:
        _parse_qrr("{bad")
    assert exc_info.value.tag == "qrr.parsed.malformed"


def test_quinn_r_act_g2c_writes_authorized_storyboard(tmp_path: Path) -> None:
    state = make_state(_payload(tmp_path, gate_id="G2C"))
    update = _act(state)
    payload = json.loads(update["cache_state"]["cache_prefix"])
    artifact = Path(payload["quinn_r_review"]["artifact_paths"][0])
    assert artifact.name == "authorized-storyboard.json"
    assert payload["quinn_r_review"]["mode"] == "pre-composition"
    assert update["model_resolution_trail"][-1].reason == "qrr.parsed.ok"


def test_quinn_r_act_g5_runs_structured_qa(tmp_path: Path) -> None:
    state = make_state(_payload(tmp_path, gate_id="G5"))
    update = _act(state)
    verdict = json.loads(update["cache_state"]["cache_prefix"])["quinn_r_review"]
    assert verdict["checks"] == ["wpm", "vtt", "coverage", "duration", "partition"]
    assert verdict["blocking"] == []
    assert verdict["advisory"] == []


def test_quinn_r_act_g3b_consumes_dispatch_helpers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[str] = []

    def _sensory(**_: Any) -> dict[str, Any]:
        calls.append("sensory")
        return {"confidence": "HIGH"}

    def _quality(**_: Any) -> dict[str, Any]:
        calls.append("quality")
        return {"status": "ok"}

    monkeypatch.setattr("app.specialists.quinn_r._act.dispatch_to_sensory_bridges", _sensory)
    monkeypatch.setattr("app.specialists.quinn_r._act.run_postcomposition_validators", _quality)
    state = make_state(_payload(tmp_path, gate_id="G3B"))
    update = _act(state)
    verdict = json.loads(update["cache_state"]["cache_prefix"])["quinn_r_review"]
    assert verdict["mode"] == "post-composition"
    assert calls == ["sensory", "quality"]


def test_quinn_r_act_mode_mismatch_fails_loudly(tmp_path: Path) -> None:
    bad = json.loads(_payload(tmp_path, gate_id="G2C"))
    bad["gate_phase"] = "post-composition"
    state = make_state(json.dumps(bad))
    with pytest.raises(ModeMismatchError):
        _act(state)


def test_quinn_r_act_body_loc_budget() -> None:
    import app.specialists.quinn_r._act as act_module

    source = inspect.getsource(act_module)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 150
