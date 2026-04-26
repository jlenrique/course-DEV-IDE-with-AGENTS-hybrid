from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.wanda.graph import WandaAudioParseError, _act, _parse_wanda_audio
from app.specialists.wanda.wondercraft_dispatch import WondercraftDispatchError


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


def test_parse_wanda_audio_ok() -> None:
    parsed = _parse_wanda_audio(
        {
            "capability": "CM",
            "operation_payload": {"chapter_titles": ["Intro", "Body"]},
        }
    )
    assert parsed["tag"] == "wanda_audio.parsed.ok"


@pytest.mark.parametrize(
    "raw,tag",
    [
        ("{bad", "wanda_audio.parsed.malformed"),
        ("", "wanda_audio.parsed.empty"),
        ("[]", "wanda_audio.parsed.wrong-type"),
        ('{"operation_payload": {}}', "wanda_audio.parsed.missing-key"),
        ('{"capability": "ZZ", "operation_payload": {}}', "wanda_audio.parsed.missing-key"),
        ('{"capability": "EP", "operation_payload": []}', "wanda_audio.parsed.wrong-type"),
    ],
)
def test_parse_wanda_audio_branch_errors(raw: str, tag: str) -> None:
    with pytest.raises(WandaAudioParseError) as exc_info:
        _parse_wanda_audio(raw)
    assert exc_info.value.tag == tag


def test_wanda_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = '{"capability":"ZZ","operation_payload":{}}'
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.wanda.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(WandaAudioParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "wanda_audio.parsed.missing-key"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_wanda_act_dispatch_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = '{"capability":"EP","operation_payload":{"prompt":"x"}}'
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    def _broken_dispatch(**_: Any) -> dict[str, Any]:
        raise WondercraftDispatchError("boom", tag="wanda_audio.parsed.dispatch-failed")

    monkeypatch.setattr("app.specialists.wanda.graph.make_chat_model", lambda **_: _Handle())
    monkeypatch.setattr("app.specialists.wanda.graph.dispatch_to_wondercraft", _broken_dispatch)
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(WondercraftDispatchError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "wanda_audio.parsed.dispatch-failed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_wanda_act_returns_audio_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = '{"capability":"CM","operation_payload":{"chapter_titles":["Intro"]}}'
        usage_metadata = {"input_tokens": 10, "output_tokens": 6}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {"capability": "CM", "receipt": {"status": "success", "chapter_markers": []}}

    monkeypatch.setattr("app.specialists.wanda.graph.make_chat_model", lambda **_: _Handle())
    monkeypatch.setattr("app.specialists.wanda.graph.dispatch_to_wondercraft", _fake_dispatch)
    state = _build_state(json.dumps({"brief": "x"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["wanda_audio"]["capability"] == "CM"
    assert update["model_resolution_trail"][-1].reason == "wanda_audio.parsed.ok"


@pytest.mark.llm_live
def test_wanda_act_live_llm_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {"capability": "CM", "receipt": {"status": "success", "chapter_markers": []}}

    monkeypatch.setattr("app.specialists.wanda.graph.dispatch_to_wondercraft", _fake_dispatch)
    state = _build_state(
        json.dumps(
            {
                "script": "Podcast script draft",
                "preferred_capability": "CM",
            }
        )
    )
    try:
        update = _act(state)
    except WandaAudioParseError as exc:
        if "model invocation failed" in str(exc):
            pytest.skip("Wanda live model unavailable in this environment")
        raise
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert isinstance(output["wanda_audio"], dict)


def test_wanda_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 120
