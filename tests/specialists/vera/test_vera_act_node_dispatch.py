from __future__ import annotations

import inspect
import json
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
                requested="gpt-5.4",
                resolved="gpt-5.4",
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
    out = _parse_ftr(raw)
    assert out["status"] == expected


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


def test_parse_ftr_error_tag_contract() -> None:
    with pytest.raises(FTRParseError) as exc_info:
        _parse_ftr('{"status":"mystery","severity":"low","summary":"s","findings":[{"id":"1"}]}')
    assert exc_info.value.tag == "ftr.parsed.contract-failure"


def test_vera_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "modality": "image",
            "artifact_path": "artifact.png",
            "confidence": "HIGH",
            "confidence_rationale": "clear",
            "perception_timestamp": "2026-01-01T00:00:00Z",
        }

    class _Resp:
        content = '{"status":"mystery","severity":"low","summary":"bad","findings":[{"id":"F-1"}]}'
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.vera.graph.dispatch_to_sensory_bridges", _fake_dispatch)
    monkeypatch.setattr("app.specialists.vera.graph.make_chat_model", lambda **_: _Handle())

    state = _build_state(
        json.dumps(
            {
                "artifact_path": "artifact.png",
                "source_of_truth_path": "truth.md",
                "modality": "image",
                "gate": "fidelity",
            }
        )
    )
    with pytest.raises(FTRParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "ftr.parsed.contract-failure"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


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


def test_vera_act_dispatch_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _broken_dispatch(**_: Any) -> dict[str, Any]:
        raise RuntimeError("bridge failure")

    monkeypatch.setattr("app.specialists.vera.graph.dispatch_to_sensory_bridges", _broken_dispatch)
    state = _build_state(
        json.dumps(
            {
                "artifact_path": "artifact.png",
                "source_of_truth_path": "truth.md",
                "modality": "image",
                "gate": "fidelity",
            }
        )
    )
    with pytest.raises(FTRParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "ftr.parsed.contract-failure"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_vera_act_dispatches_and_returns_finding(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "modality": "image",
            "artifact_path": "artifact.png",
            "confidence": "HIGH",
            "confidence_rationale": "clear",
            "perception_timestamp": "2026-01-01T00:00:00Z",
        }

    class _Resp:
        content = (
            '{"status":"pass","severity":"low","summary":"ok",'
            '"findings":[{"id":"F-1","detail":"none"}]}'
        )
        usage_metadata = {"input_tokens": 10, "output_tokens": 5}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.vera.graph.dispatch_to_sensory_bridges", _fake_dispatch)
    monkeypatch.setattr("app.specialists.vera.graph.make_chat_model", lambda **_: _Handle())
    envelope = json.dumps(
        {
            "artifact_path": "artifact.png",
            "source_of_truth_path": "truth.md",
            "modality": "image",
            "gate": "fidelity",
        }
    )
    state = _build_state(envelope)
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["vera_finding"]["status"] == "pass"
    assert update["model_resolution_trail"][-1].reason == "ftr.parsed.ok"


@pytest.mark.llm_live
def test_vera_act_live_llm_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "modality": "image",
            "artifact_path": "artifact.png",
            "confidence": "HIGH",
            "confidence_rationale": "clear",
            "perception_timestamp": "2026-01-01T00:00:00Z",
        }

    monkeypatch.setattr("app.specialists.vera.graph.dispatch_to_sensory_bridges", _fake_dispatch)
    state = _build_state(
        json.dumps(
            {
                "artifact_path": "artifact.png",
                "source_of_truth_path": "truth.md",
                "modality": "image",
                "gate": "fidelity",
            }
        )
    )
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    finding = output["vera_finding"]
    assert isinstance(finding, dict)
    assert {"status", "severity", "summary", "findings"} <= set(finding.keys())
    assert isinstance(finding["findings"], list)


def test_vera_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 115
