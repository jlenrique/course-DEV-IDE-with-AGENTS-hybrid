from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.enrique.elevenlabs_dispatch import ElevenlabsDispatchError
from app.specialists.enrique.graph import EnriqueAudioParseError, _act, _parse_enrique_audio


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


def test_parse_enrique_audio_ok() -> None:
    parsed = _parse_enrique_audio(
        {
            "mode": "voice-preview",
            "operation_payload": {"presentation_attributes": {"content_type": "med"}},
        }
    )
    assert parsed["tag"] == "enrique_audio.parsed.ok"


@pytest.mark.parametrize(
    "raw,tag",
    [
        ("{bad", "enrique_audio.parsed.malformed"),
        ("", "enrique_audio.parsed.empty"),
        ("[]", "enrique_audio.parsed.wrong-type"),
        ('{"operation_payload": {}}', "enrique_audio.parsed.missing-key"),
        ('{"mode": "unknown", "operation_payload": {}}', "enrique_audio.parsed.missing-key"),
        ('{"mode": "music", "operation_payload": []}', "enrique_audio.parsed.wrong-type"),
    ],
)
def test_parse_enrique_audio_branch_errors(raw: str, tag: str) -> None:
    with pytest.raises(EnriqueAudioParseError) as exc_info:
        _parse_enrique_audio(raw)
    assert exc_info.value.tag == tag


def test_enrique_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = '{"mode":"unknown","operation_payload":{}}'
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.enrique.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(EnriqueAudioParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "enrique_audio.parsed.missing-key"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_enrique_act_dispatch_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = '{"mode":"music","operation_payload":{}}'
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    def _broken_dispatch(**_: Any) -> dict[str, Any]:
        raise ElevenlabsDispatchError("boom", tag="enrique_audio.parsed.api-error")

    monkeypatch.setattr("app.specialists.enrique.graph.make_chat_model", lambda **_: _Handle())
    monkeypatch.setattr("app.specialists.enrique.graph.dispatch_to_elevenlabs", _broken_dispatch)
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(ElevenlabsDispatchError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "enrique_audio.parsed.api-error"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_enrique_act_returns_audio_receipt(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = '{"mode":"voice-preview","operation_payload":{}}'
        usage_metadata = {"input_tokens": 10, "output_tokens": 6}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {"mode": "voice-preview", "receipt": {"status": "success"}}

    monkeypatch.setattr("app.specialists.enrique.graph.make_chat_model", lambda **_: _Handle())
    monkeypatch.setattr("app.specialists.enrique.graph.dispatch_to_elevenlabs", _fake_dispatch)
    state = _build_state(json.dumps({"brief": "x"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["enrique_audio"]["mode"] == "voice-preview"
    assert update["model_resolution_trail"][-1].reason == "enrique_audio.parsed.ok"


@pytest.mark.llm_live
def test_enrique_act_live_llm_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    def _fake_dispatch(**_: Any) -> dict[str, Any]:
        return {"mode": "voice-preview", "receipt": {"status": "success"}}

    monkeypatch.setattr("app.specialists.enrique.graph.dispatch_to_elevenlabs", _fake_dispatch)
    state = _build_state(
        json.dumps(
            {
                "script": "Explain renal physiology in two concise paragraphs.",
                "preferred_mode": "voice-preview",
            }
        )
    )
    try:
        update = _act(state)
    except EnriqueAudioParseError as exc:
        if "model invocation failed" in str(exc):
            pytest.skip("Enrique live model unavailable in this environment")
        raise
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert isinstance(output["enrique_audio"], dict)


def test_enrique_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 120
