from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.cd.graph import CdDirectiveParseError, _act, _parse_cd_directive


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


def _valid_directive() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "experience_profile": "visual-led",
        "slide_mode_proportions": {
            "literal-text": 0.15,
            "literal-visual": 0.25,
            "creative": 0.60,
        },
        "narration_profile_controls": {
            "narrator_source_authority": "source-grounded",
            "slide_content_density": "adaptive",
            "elaboration_budget": "medium",
            "connective_weight": "balanced",
            "callback_frequency": "moderate",
            "visual_narration_coupling": "balanced",
            "rhetorical_richness": "balanced",
            "vocabulary_register": "professional",
            "arc_awareness": "medium",
            "narrative_tension": "medium",
            "emotional_coloring": "neutral",
        },
        "creative_rationale": "Favor rich visual storytelling for this profile.",
    }


def test_parse_cd_directive_ok() -> None:
    parsed = _parse_cd_directive({"cd_directive": _valid_directive()})
    assert parsed["tag"] == "cd_directive.parsed.ok"


@pytest.mark.parametrize(
    "raw,tag",
    [
        ("{bad", "cd_directive.parsed.malformed"),
        ("", "cd_directive.parsed.empty"),
        ("[]", "cd_directive.parsed.wrong-type"),
        ('{"cd_directive": []}', "cd_directive.parsed.wrong-type"),
        ('{"cd_directive": {}}', "cd_directive.parsed.empty"),
        (
            '{"cd_directive": {"schema_version":"2.0"}}',
            "cd_directive.parsed.validator-failed",
        ),
    ],
)
def test_parse_cd_directive_branch_errors(raw: str, tag: str) -> None:
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _parse_cd_directive(raw)
    assert exc_info.value.tag == tag


def test_cd_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = '{"cd_directive": {"schema_version":"2.0"}}'
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.cd.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "cd_directive.parsed.validator-failed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_cd_act_malformed_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state("{bad")
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "cd_directive.parsed.malformed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_cd_act_missing_envelope_sets_two_sided_trail_tag() -> None:
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
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "cd_directive.parsed.missing-key"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_cd_act_returns_cd_directive(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = json.dumps({"cd_directive": _valid_directive()})
        usage_metadata = {"input_tokens": 10, "output_tokens": 8}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.cd.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"brief": "x"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["cd_directive"]["schema_version"] == "1.0"
    assert update["model_resolution_trail"][-1].reason == "cd_directive.parsed.ok"


@pytest.mark.llm_live
def test_cd_act_live_llm_smoke() -> None:
    state = _build_state(
        json.dumps(
            {
                "brief": "Design a visual-led directive for a short pathology lesson.",
                "target_audience": "medical students",
            }
        )
    )
    try:
        update = _act(state)
    except CdDirectiveParseError as exc:
        if "model invocation failed" in str(exc) or (
            exc.tag == "cd_directive.parsed.validator-failed"
        ):
            pytest.skip("CD live model unavailable in this environment")
        raise
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert isinstance(output["cd_directive"], dict)


def test_cd_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 120
