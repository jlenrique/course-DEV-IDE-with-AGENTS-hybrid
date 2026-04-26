from __future__ import annotations

import json

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.tamara.graph import (
    OperatorInstructionsParseError,
    _act,
    _parse_operator_instructions_envelope,
)


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


def test_tamara_parse_envelope_happy_path() -> None:
    parsed = _parse_operator_instructions_envelope({"prompt": "Draft operator steps"})
    assert parsed["tag"] == "design_spec.parsed.ok"


@pytest.mark.parametrize(
    "payload,tag",
    [
        ({}, "design_spec.parsed.missing-key"),
        ({"prompt": 7}, "design_spec.parsed.wrong-type"),
        ({"prompt": "ok", "context": "bad"}, "design_spec.parsed.wrong-type"),
    ],
)
def test_tamara_parse_envelope_errors(payload: object, tag: str) -> None:
    with pytest.raises(OperatorInstructionsParseError) as exc_info:
        _parse_operator_instructions_envelope(payload)  # type: ignore[arg-type]
    assert exc_info.value.tag == tag


@pytest.mark.parametrize(
    "cache_prefix,tag",
    [
        ("{bad", "design_spec.parsed.malformed"),
        ("[]", "design_spec.parsed.wrong-type"),
        (json.dumps({}), "design_spec.parsed.missing-key"),
        (json.dumps({"prompt": 7}), "design_spec.parsed.wrong-type"),
    ],
)
def test_tamara_act_error_branches_append_trail_tag(cache_prefix: str, tag: str) -> None:
    state = _build_state(cache_prefix)
    with pytest.raises(OperatorInstructionsParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == tag
    assert state.model_resolution_trail[-1].reason == tag


def test_tamara_act_missing_cache_state_appends_trail_tag() -> None:
    state = RunState(
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
        cache_state=None,
    )
    with pytest.raises(OperatorInstructionsParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "design_spec.parsed.missing-key"
    assert state.model_resolution_trail[-1].reason == "design_spec.parsed.missing-key"


def test_tamara_act_returns_deterministic_payload() -> None:
    state = _build_state(json.dumps({"prompt": "Build operator instructions"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert "tamara_design_spec" in output
    assert output["model_id"] == "gpt-5.4"
    assert update["model_resolution_trail"][-1].reason == "design_spec.parsed.ok"
