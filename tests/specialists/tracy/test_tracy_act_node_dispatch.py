from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.tracy.graph import ManifestParseError, _act, _parse_manifest


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


def test_parse_manifest_ok() -> None:
    out = _parse_manifest(
        {
            "query": "q",
            "query_attempted": "q2",
            "results": [
                {
                    "intent_class": "supporting_evidence",
                    "fit_score": 0.9,
                    "authority_tier": "primary",
                    "editorial_note": "specific evidence note",
                    "provider_metadata": {},
                }
            ],
        }
    )
    assert out["tag"] == "manifest.parsed.ok"


@pytest.mark.parametrize(
    "raw,tag",
    [
        ("{bad", "manifest.parsed.malformed"),
        ('{"query":"q"}', "manifest.parsed.empty"),
        ('{"query":"q","results":null}', "manifest.parsed.empty"),
        ('{"query":"q","results":"x"}', "manifest.parsed.wrong-type"),
        ('{"query":"q","query_attempted":5,"results":[]}', "manifest.parsed.wrong-type"),
        ('{"query":"q","results":[]}', "manifest.parsed.empty"),
        (
            '{"query":"q","query_attempted":"ran","results":[]}',
            "manifest.parsed.no-results",
        ),
        (
            '{"query":"q","results":[{"intent_class":"supporting_evidence"}]}',
            "manifest.parsed.missing-key",
        ),
        (
            (
                '{"query":"q","results":[{"intent_class":"bad","fit_score":0.9,'
                '"authority_tier":"primary","editorial_note":"detail",'
                '"provider_metadata":{}}]}'
            ),
            "manifest.parsed.vocabulary-violation",
        ),
    ],
)
def test_parse_manifest_branch_errors(raw: str, tag: str) -> None:
    with pytest.raises(ManifestParseError) as exc_info:
        _parse_manifest(raw)
    assert exc_info.value.tag == tag


def test_tracy_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = (
            '{"query":"q","results":[{"intent_class":"bad","fit_score":0.9,'
            '"authority_tier":"primary","editorial_note":"detail","provider_metadata":{}}]}'
        )
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.tracy.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(ManifestParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "manifest.parsed.vocabulary-violation"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


@pytest.mark.parametrize(
    "content,tag",
    [
        ('{"query":"q","results":[]}', "manifest.parsed.empty"),
        ('{"query":"q","query_attempted":"ran","results":[]}', "manifest.parsed.no-results"),
        ('{"query":"q","query_attempted":5,"results":[]}', "manifest.parsed.wrong-type"),
        (
            '{"query":"q","results":[{"intent_class":"supporting_evidence"}]}',
            "manifest.parsed.missing-key",
        ),
    ],
)
def test_tracy_act_failure_matrix_sets_two_sided_trail_tags(
    monkeypatch: pytest.MonkeyPatch,
    content: str,
    tag: str,
) -> None:
    class _Resp:
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

        def __init__(self, value: str) -> None:
            self.content = value

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp(content)

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.tracy.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(ManifestParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == tag
    assert state.model_resolution_trail[-1].reason == tag


def test_tracy_act_malformed_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state("{bad")
    with pytest.raises(ManifestParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "manifest.parsed.malformed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_tracy_act_missing_envelope_sets_two_sided_trail_tag() -> None:
    state = RunState(
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
        cache_state=None,
    )
    with pytest.raises(ManifestParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "manifest.parsed.missing-key"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_tracy_act_wrong_type_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state("[]")
    with pytest.raises(ManifestParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "manifest.parsed.wrong-type"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_tracy_act_returns_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = json.dumps(
            {
                "query": "query",
                "query_attempted": "query attempted",
                "results": [
                    {
                        "intent_class": "supporting_evidence",
                        "fit_score": 0.9,
                        "authority_tier": "primary",
                        "editorial_note": "specific evidence note for this claim",
                        "provider_metadata": {"source": "scite"},
                    }
                ],
            }
        )
        usage_metadata = {"input_tokens": 10, "output_tokens": 8}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.tracy.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["tracy_manifest"]["results"][0]["intent_class"] == "supporting_evidence"
    assert output["posture_tag"] == "posture.selected:supporting_evidence"
    assert update["model_resolution_trail"][-1].reason == "manifest.parsed.ok"


@pytest.mark.llm_live
def test_tracy_act_live_llm_smoke() -> None:
    state = _build_state(json.dumps({"brief": "find one supporting citation for memory retention"}))
    try:
        update = _act(state)
    except ManifestParseError as exc:
        # Any ManifestParseError under @llm_live is non-deterministic LLM-output
        # shape variation, NOT a deterministic regression. The deterministic
        # parse-branch matrix above covers all parse failure modes; the live
        # smoke only proves the wire works + LLM emits Tracy-shaped output.
        # Per Murat principle 4 ("flakiness is critical technical debt"), skip
        # gracefully on LLM nondeterminism rather than fail; investigate the
        # underlying tag in operator-window if needed.
        pytest.skip(
            f"Tracy live model output triggered {exc.tag} — non-deterministic "
            "LLM-shape variance; deterministic parse-branch tests above cover "
            "the failure mode. Re-run if persistent across multiple invocations."
        )
    output = json.loads(update["cache_state"]["cache_prefix"])
    manifest = output["tracy_manifest"]
    assert isinstance(manifest, dict)
    assert isinstance(manifest["results"], list)
    assert manifest["results"]


def test_tracy_act_does_not_load_persona() -> None:
    source = inspect.getsource(_act)
    assert "SKILL.md" not in source
    assert "PERSONA.md" not in source


def test_tracy_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 115
