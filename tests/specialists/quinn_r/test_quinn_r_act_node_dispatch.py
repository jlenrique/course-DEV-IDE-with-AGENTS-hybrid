from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.specialists.quinn_r.graph import QRRParseError, _act, _parse_qrr
from tests.specialists.quinn_r.conftest import make_envelope, make_state


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


@pytest.mark.parametrize(
    "raw,match,tag",
    [
        ("{bad", "parse failed", "qrr.parsed.malformed"),
        ('{"status":"x"}', "missing key", "qrr.parsed.missing-key"),
        (
            '{"status":"x","severity":"low","summary":"s","findings":"oops","dimension_scores":{}}',
            "findings must be a list",
            "qrr.parsed.wrong-type",
        ),
        (
            '{"status":"pass","severity":"low","summary":"s","findings":[],"dimension_scores":{}}',
            "findings cannot be empty",
            "qrr.parsed.empty",
        ),
        (
            '{"status":"pass","severity":"low","summary":"s","findings":[{"id":"1"}],"dimension_scores":"oops"}',
            "dimension_scores must be a mapping",
            "qrr.parsed.wrong-type",
        ),
        (
            '{"status":"mystery","severity":"low","summary":"s","findings":[{"id":"1"}],"dimension_scores":{"a":"b"}}',
            "contract validation failed",
            "qrr.parsed.contract-failure",
        ),
    ],
)
def test_parse_qrr_branch_errors(raw: str, match: str, tag: str) -> None:
    with pytest.raises(QRRParseError, match=match) as exc_info:
        _parse_qrr(raw)
    assert exc_info.value.tag == tag


@pytest.mark.parametrize(
    "dimension",
    [
        "accessibility",
        "brand",
        "learning",
        "instructional",
        "intent",
        "content",
        "audio",
        "composition",
    ],
)
def test_parse_qrr_dimension_failure_tags(dimension: str) -> None:
    raw = json.dumps(
        {
            "status": "warn",
            "severity": "medium",
            "summary": "dimension fail",
            "findings": [{"id": "Q-4"}],
            "dimension_scores": {dimension: "FAIL"},
        }
    )
    with pytest.raises(QRRParseError) as exc_info:
        _parse_qrr(raw)
    assert exc_info.value.tag == f"qrr.parsed.dimension-failure:{dimension}"


def test_quinn_r_act_precomposition_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = (
            '{"status":"pass","severity":"low","summary":"ok","findings":[{"id":"Q-1"}],'
            '"dimension_scores":{"accessibility":"PASS"}}'
        )
        usage_metadata = {"input_tokens": 10, "output_tokens": 5}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.run_precomposition_validators",
        lambda **_: {"status": "ok"},
    )
    monkeypatch.setattr("app.specialists.quinn_r.graph.make_chat_model", lambda **_: _Handle())
    state = make_state(make_envelope(gate_phase="pre-composition"))
    update = _act(state)
    payload = json.loads(update["cache_state"]["cache_prefix"])
    assert payload["quinn_r_review"]["status"] == "pass"
    assert update["model_resolution_trail"][-1].reason == "qrr.parsed.ok"


def test_quinn_r_act_postcomposition_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = (
            '{"status":"warn","severity":"medium","summary":"ok","findings":[{"id":"Q-2"}],'
            '"dimension_scores":{"composition":"WARN"}}'
        )
        usage_metadata = {"input_tokens": 10, "output_tokens": 5}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.dispatch_to_sensory_bridges",
        lambda **_: {"mode": "post-composition", "confidence": "HIGH"},
    )
    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.run_postcomposition_validators",
        lambda **_: {"status": "ok"},
    )
    monkeypatch.setattr("app.specialists.quinn_r.graph.make_chat_model", lambda **_: _Handle())
    state = make_state(make_envelope(gate_phase="post-composition"))
    update = _act(state)
    payload = json.loads(update["cache_state"]["cache_prefix"])
    assert payload["quinn_r_review"]["status"] == "warn"


def test_quinn_r_act_invalid_gate_phase_raises_value_error() -> None:
    state = make_state(make_envelope(gate_phase="unknown"))
    with pytest.raises(ValueError, match="unknown gate_phase"):
        _act(state)


def test_quinn_r_act_malformed_envelope_sets_two_sided_trail_tag() -> None:
    state = make_state("{bad-json")
    with pytest.raises(QRRParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "qrr.parsed.malformed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_quinn_r_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = (
            '{"status":"warn","severity":"medium","summary":"bad","findings":[{"id":"Q-5"}],'
            '"dimension_scores":{"composition":"FAIL"}}'
        )
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.run_precomposition_validators",
        lambda **_: {"status": "ok"},
    )
    monkeypatch.setattr("app.specialists.quinn_r.graph.make_chat_model", lambda **_: _Handle())
    state = make_state(make_envelope(gate_phase="pre-composition"))
    with pytest.raises(QRRParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "qrr.parsed.dimension-failure:composition"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_quinn_r_postcomposition_cross_wrapper_coordination(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def _broken_sensory(**_: Any) -> dict[str, Any]:
        calls.append("sensory")
        raise ImportError("bridge unavailable")

    def _postcomp(**_: Any) -> dict[str, Any]:
        calls.append("quality")
        return {"status": "ok", "dimension_scores": {"sensory": "SKIPPED"}}

    class _Resp:
        content = (
            '{"status":"warn","severity":"medium","summary":"degraded","findings":[{"id":"Q-3"}],'
            '"dimension_scores":{"sensory":"SKIPPED"}}'
        )
        usage_metadata = {"input_tokens": 10, "output_tokens": 5}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.dispatch_to_sensory_bridges",
        _broken_sensory,
    )
    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.run_postcomposition_validators",
        _postcomp,
    )
    monkeypatch.setattr("app.specialists.quinn_r.graph.make_chat_model", lambda **_: _Handle())

    state = make_state(make_envelope(gate_phase="post-composition"))
    update = _act(state)
    payload = json.loads(update["cache_state"]["cache_prefix"])
    assert payload["quinn_r_review"]["dimension_scores"]["sensory"] == "SKIPPED"
    assert calls == ["sensory", "quality"]


@pytest.mark.llm_live
def test_quinn_r_act_live_llm_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "app.specialists.quinn_r.graph.run_precomposition_validators",
        lambda **_: {"status": "ok"},
    )
    state = make_state(make_envelope(gate_phase="pre-composition"))
    update = _act(state)
    payload = json.loads(update["cache_state"]["cache_prefix"])
    review = payload["quinn_r_review"]
    assert {"status", "severity", "summary", "findings", "dimension_scores"} <= set(
        review.keys()
    )


def test_quinn_r_act_loc_budgets() -> None:
    from app.specialists.quinn_r.graph import _act_postcomposition, _act_precomposition

    for fn, cap in ((_act, 40), (_act_precomposition, 60), (_act_postcomposition, 60)):
        source = inspect.getsource(fn)
        logical_lines = [line for line in source.splitlines() if line.strip()]
        assert len(logical_lines) <= cap
