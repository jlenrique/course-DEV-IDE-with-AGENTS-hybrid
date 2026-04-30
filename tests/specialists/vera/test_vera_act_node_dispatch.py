from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.vera.graph import FTRParseError, _act, _parse_ftr


def _build_state(cache_prefix: str) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5",
                resolved="gpt-5",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="c" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=0),
    )


@pytest.mark.parametrize(
    "raw,expected",
    [
        (
            '{"status":"pass","severity":"low","summary":"ok","findings":[{"id":"1"}]}',
            "pass",
        ),
        (
            '{"status":"passed","severity":"low","summary":"ok","findings":[{"id":"1"}]}',
            "pass",
        ),
        (
            '{"status":"warning","severity":"medium","summary":"ok","findings":[{"id":"1"}]}',
            "warn",
        ),
        (
            '```json\n{"status":"pass","severity":"low","summary":"ok","findings":[{"id":"1"}]}\n```',
            "pass",
        ),
    ],
)
def test_parse_ftr_ok(raw: str, expected: str) -> None:
    assert _parse_ftr(raw)["status"] == expected


@pytest.mark.parametrize(
    "raw,match,tag",
    [
        ("{bad", "parse failed", "ftr.parsed.malformed"),
        ('{"status":"x"}', "missing key", "ftr.parsed.missing-key"),
        (
            '{"status":"x","severity":"low","summary":"s","findings":"oops"}',
            "must be a list",
            "ftr.parsed.wrong-type",
        ),
        (
            '{"status":"pass","severity":"low","summary":"s","findings":[]}',
            "cannot be empty",
            "ftr.parsed.empty",
        ),
        (
            '{"status":"pass","severity":"low","summary":"s","findings":[1]}',
            "must be objects",
            "ftr.parsed.wrong-type",
        ),
        (
            '{"status":"mystery","severity":"low","summary":"s","findings":[{"id":"1"}]}',
            "contract validation failed",
            "ftr.parsed.contract-failure",
        ),
    ],
)
def test_parse_ftr_branch_errors(raw: str, match: str, tag: str) -> None:
    with pytest.raises(FTRParseError, match=match) as exc_info:
        _parse_ftr(raw)
    assert exc_info.value.tag == tag


def test_vera_act_malformed_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state("{bad-json")
    with pytest.raises(FTRParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "ftr.parsed.malformed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_vera_act_wrong_type_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state('["not-a-mapping"]')
    with pytest.raises(FTRParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "ftr.parsed.wrong-type"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_vera_act_writes_trace_report(tmp_path: Path) -> None:
    extracted = tmp_path / "extracted.md"
    extracted.write_text(
        "Claim one. [evidence: src-1]\nClaim two. [evidence: src-1]\n",
        encoding="utf-8",
    )
    state = _build_state(
        json.dumps(
            {
                "gate_id": "G0",
                "extracted_path": str(extracted),
                "runs_root": str(tmp_path),
            }
        )
    )

    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    trace = Path(output["trace_report_path"])
    report = json.loads(trace.read_text(encoding="utf-8"))

    assert trace.name.startswith("g0-vera-")
    assert {"O", "I", "A"} == {item["category"] for item in report["findings"]}
    assert output["vera_finding"]["verdict"]["verb"] == "proceed"
    assert update["model_resolution_trail"][-1].reason == "ftr.parsed.ok"


def test_vera_g3_dispatches_visual_audio_motion(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: list[str] = []

    def _fake_dispatch(**kwargs: Any) -> dict[str, Any]:
        captured.append(str(kwargs["modality"]))
        return {
            "schema_version": "1.0",
            "modality": kwargs["modality"],
            "artifact_path": str(kwargs.get("artifact_path") or ""),
            "confidence": "HIGH",
        }

    monkeypatch.setattr("app.specialists.vera.graph.dispatch_to_sensory_bridges", _fake_dispatch)
    state = _build_state(
        json.dumps(
            {
                "gate_id": "G3",
                "image_artifact_path": "slide.png",
                "audio_artifact_path": "voice.mp3",
                "motion_artifact_path": "clip.mp4",
                "runs_root": str(tmp_path),
            }
        )
    )

    output = json.loads(_act(state)["cache_state"]["cache_prefix"])
    assert captured == ["image", "audio", "video"]
    assert output["vera_finding"]["rubrics"]["G3"]["confidence_rubric"]["visual"][
        "score"
    ] == 1.0


def test_vera_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 20
