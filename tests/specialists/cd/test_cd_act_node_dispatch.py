from __future__ import annotations

import inspect
import json
from typing import Any

import pytest

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.cd.graph import CdDirectiveParseError, _act, _parse_cd_directive


def _bundle_payload(tmp_path: Any, **extra: Any) -> str:
    """Payload with a real tmp source bundle (content-plane contract,
    2026-06-12: cd refuses to style a corpus it cannot see)."""
    bundle = tmp_path / "bundle"
    bundle.mkdir(exist_ok=True)
    (bundle / "extracted.md").write_text(
        "# Sample corpus\n\nHealthcare inflection-point lesson content.",
        encoding="utf-8",
    )
    return json.dumps({"bundle_reference": str(bundle), **extra})


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


# ---------------------------------------------------------------------------
# Trial-3 finding #9 fix (2026-06-11): the validator's parity rule forbids
# any deviation from experience-profiles.yaml targets, so the LLM judgment
# surface is exactly {experience_profile, creative_rationale}; the parse
# path canonicalizes the rest deterministically. The live 2/2 failure mode
# (LLM inventing the 11 narration-control values) is structurally closed.
# ---------------------------------------------------------------------------


def test_parse_minimal_llm_output_canonicalizes_to_full_directive() -> None:
    """profile + rationale alone parse OK; values bound from profile targets."""
    parsed = _parse_cd_directive(
        json.dumps(
            {
                "cd_directive": {
                    "experience_profile": "visual-led",
                    "creative_rationale": "Lead with imagery for this lesson.",
                }
            }
        )
    )
    assert parsed["tag"] == "cd_directive.parsed.ok"
    directive = parsed["cd_directive"]
    assert directive == _valid_directive() | {
        "creative_rationale": "Lead with imagery for this lesson."
    }


def test_parse_deviating_values_are_canonicalized_to_profile_targets() -> None:
    """LLM-invented proportions/controls (the live failure mode) are replaced
    by the chosen profile's configured targets instead of failing parity."""
    deviating = {
        "cd_directive": {
            "experience_profile": "visual-led",
            "creative_rationale": "Verbatim rationale.",
            "slide_mode_proportions": {
                "literal-text": 0.9,
                "literal-visual": 0.05,
                "creative": 0.05,
            },
            "narration_profile_controls": {"narrator_source_authority": "invented"},
        }
    }
    parsed = _parse_cd_directive(json.dumps(deviating))
    assert parsed["cd_directive"]["slide_mode_proportions"] == {
        "literal-text": 0.15,
        "literal-visual": 0.25,
        "creative": 0.60,
    }
    assert (
        parsed["cd_directive"]["narration_profile_controls"]
        == _valid_directive()["narration_profile_controls"]
    )


def test_parse_unknown_profile_fails_with_raw_excerpt_captured() -> None:
    raw = json.dumps(
        {
            "cd_directive": {
                "experience_profile": "cinematic-led",
                "creative_rationale": "x",
            }
        }
    )
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _parse_cd_directive(raw)
    assert exc_info.value.tag == "cd_directive.parsed.validator-failed"
    assert "cinematic-led" in str(exc_info.value)
    assert exc_info.value.raw_excerpt is not None
    assert "cinematic-led" in exc_info.value.raw_excerpt


def test_parse_missing_rationale_fails_with_raw_excerpt_captured() -> None:
    raw = json.dumps({"cd_directive": {"experience_profile": "text-led"}})
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _parse_cd_directive(raw)
    assert exc_info.value.tag == "cd_directive.parsed.validator-failed"
    assert "creative_rationale" in str(exc_info.value)
    assert exc_info.value.raw_excerpt is not None


def test_parse_post_canonicalization_validator_drift_surfaces_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If schema and profiles config ever drift apart, the validator error
    list is surfaced on the exception instead of being discarded."""
    monkeypatch.setattr(
        "app.specialists.cd.graph.validate_creative_directive",
        lambda _directive: ["synthetic drift error"],
    )
    raw = json.dumps(
        {
            "cd_directive": {
                "experience_profile": "visual-led",
                "creative_rationale": "x",
            }
        }
    )
    with pytest.raises(CdDirectiveParseError) as exc_info:
        _parse_cd_directive(raw)
    assert exc_info.value.tag == "cd_directive.parsed.validator-failed"
    assert exc_info.value.errors == ["synthetic drift error"]
    assert "synthetic drift error" in str(exc_info.value)


def test_assembled_prompt_embeds_authoritative_profile_targets() -> None:
    """Lockstep guard: the prompt must carry the values the parity rule
    enforces (finding #9 root cause was their absence)."""
    from app.specialists.cd.graph import _assemble_cd_prompt

    _system, user_message = _assemble_cd_prompt(
        {"brief": "x"}, extracted_source="Sample corpus body."
    )
    assert "Experience profile targets (authoritative)" in user_message
    assert "narrator_source_authority" in user_message
    assert "source-grounded" in user_message  # visual-led control value
    assert "0.6" in user_message  # text-led literal-text / visual-led creative
    # Content-plane contract 2026-06-12: the directive choice SEES the corpus.
    assert "Sample corpus body." in user_message


def test_cd_act_parse_failure_sets_two_sided_trail_tag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
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
    state = _build_state(_bundle_payload(tmp_path, brief="x"))
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


def test_cd_act_returns_cd_directive(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    class _Resp:
        content = json.dumps({"cd_directive": _valid_directive()})
        usage_metadata = {"input_tokens": 10, "output_tokens": 8}

    class _Chat:
        def invoke(self, _: Any) -> _Resp:
            return _Resp()

    class _Handle:
        chat = _Chat()

    monkeypatch.setattr("app.specialists.cd.graph.make_chat_model", lambda **_: _Handle())
    state = _build_state(_bundle_payload(tmp_path, brief="x"))
    update = _act(state)
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert output["cd_directive"]["schema_version"] == "1.0"
    assert update["model_resolution_trail"][-1].reason == "cd_directive.parsed.ok"


@pytest.mark.llm_live
def test_cd_act_live_llm_smoke(tmp_path: Any) -> None:
    state = _build_state(
        _bundle_payload(
            tmp_path,
            brief="Design a visual-led directive for a short pathology lesson.",
            target_audience="medical students",
        )
    )
    try:
        update = _act(state)
    except CdDirectiveParseError as exc:
        # Trial-3 finding #9: this test previously ALSO skipped on
        # validator-failed, masking the live prompt<->validator mismatch in
        # every green run. Only environment unavailability may skip now;
        # a validator failure on a live roll is a real defect and must fail.
        if "model invocation failed" in str(exc):
            pytest.skip("CD live model unavailable in this environment")
        raise
    output = json.loads(update["cache_state"]["cache_prefix"])
    assert isinstance(output["cd_directive"], dict)


def test_cd_act_loc_budget() -> None:
    source = inspect.getsource(_act)
    logical_lines = [line for line in source.splitlines() if line.strip()]
    assert len(logical_lines) <= 120
