from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.desmond.graph import HandoffParseError, _act, _parse_handoff


def _build_state(cache_prefix: str) -> RunState:
    return RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="c" * 64,
            )
        ],
        cache_state=CacheState(cache_prefix=cache_prefix, entries_count=0),
    )


def test_parse_handoff_ok() -> None:
    parsed = _parse_handoff(
        "## Assembly Handoff\nDo the thing.\n\n## Automation Advisory\nValidate timings."
    )
    assert parsed["tag"] == "handoff.parsed.ok"
    assert parsed["automation_advisory"] == "Validate timings."


@pytest.mark.parametrize(
    "raw,match,tag",
    [
        ("{bad", "parse failed", "handoff.parsed.malformed"),
        ('{"message":"x"}', "missing key", "handoff.parsed.missing-key"),
        ('{"handoff_text": 7}', "must be a string", "handoff.parsed.wrong-type"),
        ("", "cannot be empty", "handoff.parsed.empty"),
        (
            "## Assembly Handoff\nNo advisory section",
            "missing mandatory Automation Advisory",
            "handoff.parsed.advisory-missing",
        ),
        (
            "## Assembly Handoff\nx\n\n## Automation Advisory Extra\nnope",
            "missing mandatory Automation Advisory",
            "handoff.parsed.advisory-missing",
        ),
        (
            "## Assembly Handoff\nx\n\n### Automation Advisory\nnope",
            "missing mandatory Automation Advisory",
            "handoff.parsed.advisory-missing",
        ),
        ("[]", "must be a mapping", "handoff.parsed.wrong-type"),
    ],
)
def test_parse_handoff_branch_errors(raw: str, match: str, tag: str) -> None:
    with pytest.raises(HandoffParseError, match=match) as exc_info:
        _parse_handoff(raw)
    assert exc_info.value.tag == tag


def test_parse_handoff_empty_precedence_over_advisory_missing() -> None:
    with pytest.raises(HandoffParseError) as exc_info:
        _parse_handoff("   \n\t")
    assert exc_info.value.tag == "handoff.parsed.empty"


def test_parse_handoff_accepts_exact_heading_with_trailing_spaces() -> None:
    parsed = _parse_handoff(
        "## Assembly Handoff\nx\n\n## Automation Advisory   \nUse caution."
    )
    assert parsed["automation_advisory"] == "Use caution."


def test_parse_handoff_accepts_heading_with_trailing_colon() -> None:
    """Common LLM slip: ``## Automation Advisory:`` still counts as the section."""
    parsed = _parse_handoff(
        "## Assembly Handoff\nx\n\n## Automation Advisory:\nValidate timings."
    )
    assert parsed["tag"] == "handoff.parsed.ok"
    assert parsed["automation_advisory"] == "Validate timings."


def test_handoff_parse_error_is_dispatch_family() -> None:
    from app.specialists.dispatch_errors import SpecialistDispatchError

    err = HandoffParseError("missing", tag="handoff.parsed.advisory-missing")
    assert isinstance(err, SpecialistDispatchError)
    assert err.tag == "handoff.parsed.advisory-missing"


def test_parse_handoff_dict_missing_key() -> None:
    with pytest.raises(HandoffParseError) as exc_info:
        _parse_handoff({"message": "x"})
    assert exc_info.value.tag == "handoff.parsed.missing-key"


def test_parse_handoff_dict_wrong_type() -> None:
    with pytest.raises(HandoffParseError) as exc_info:
        _parse_handoff({"handoff_text": 123})
    assert exc_info.value.tag == "handoff.parsed.wrong-type"


def test_parse_handoff_non_string_non_dict_input() -> None:
    with pytest.raises(HandoffParseError) as exc_info:
        _parse_handoff(123)
    assert exc_info.value.tag == "handoff.parsed.wrong-type"


def test_desmond_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Resp:
        content = "## Assembly Handoff\nNo advisory"
        usage_metadata = {"input_tokens": 1, "output_tokens": 1}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.desmond.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"assembly_request": "demo"}))
    with pytest.raises(HandoffParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "handoff.parsed.advisory-missing"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_desmond_act_malformed_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state("{bad-json")
    with pytest.raises(HandoffParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "handoff.parsed.malformed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_desmond_act_missing_envelope_sets_two_sided_trail_tag() -> None:
    state = RunState(
        graph_version="v0.1-stub",
        temperature=0.0,
        model_resolution_trail=[
            ModelResolutionEntry(
                level="per_specialist",
                requested="gpt-5-nano",
                resolved="gpt-5-nano",
                reason="test",
                timestamp="2026-01-01T00:00:00Z",
                cache_prefix_hash="c" * 64,
            )
        ],
        cache_state=None,
    )
    with pytest.raises(HandoffParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "handoff.parsed.missing-key"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_desmond_act_wrong_type_envelope_sets_two_sided_trail_tag() -> None:
    state = _build_state('["not-a-mapping"]')
    with pytest.raises(HandoffParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "handoff.parsed.wrong-type"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_desmond_act_generic_invoke_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Chat:
        def invoke(self, _: Any) -> Any:
            raise RuntimeError("boom")

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.desmond.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"assembly_request": "demo"}))
    with pytest.raises(HandoffParseError) as exc_info:
        _act(state)
    assert exc_info.value.tag == "handoff.parsed.malformed"
    assert state.model_resolution_trail[-1].reason == exc_info.value.tag


def test_desmond_act_returns_handoff_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = (
            "## Assembly Handoff\n"
            "1. Load timeline\n"
            "2. Align transitions\n\n"
            "## Automation Advisory\n"
            "Double-check crossfade timing before export."
        )
        usage_metadata = {"input_tokens": 20, "output_tokens": 15}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.desmond.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"assembly_request": "demo"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    handoff = output["desmond_handoff"]
    assert "## Automation Advisory" in handoff["handoff_text"]
    assert handoff["automation_advisory"].startswith("Double-check")
    assert update["model_resolution_trail"][-1].reason == "handoff.parsed.ok"


def test_desmond_act_accepts_dict_content_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Resp:
        content = {
            "handoff_text": (
                "## Assembly Handoff\nDo it.\n\n## Automation Advisory\nValidate."
            )
        }
        usage_metadata = {"input_tokens": 10, "output_tokens": 5}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.desmond.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(json.dumps({"assembly_request": "demo"}))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["desmond_handoff"]["automation_advisory"] == "Validate."
    assert update["model_resolution_trail"][-1].reason == "handoff.parsed.ok"


@pytest.mark.llm_live
def test_desmond_act_live_llm_smoke() -> None:
    state = _build_state(
        json.dumps(
            {
                "assembly_request": "Produce a concise assembly handoff for a 3-slide lesson.",
                "slide_count": 3,
            }
        )
    )
    try:
        update = _act(state)
    except HandoffParseError as exc:
        if "model invocation failed" in str(exc):
            pytest.skip("Desmond live model unavailable in this environment")
        raise
    output = json.loads(update["cache_state"]["cache_prefix"])
    handoff = output["desmond_handoff"]
    assert isinstance(handoff, dict)
    assert "handoff_text" in handoff
    assert "## Automation Advisory" in handoff["handoff_text"]
    assert handoff.get("automation_advisory")


def test_desmond_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 115
