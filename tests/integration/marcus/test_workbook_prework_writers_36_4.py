import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveAbilityInput,
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonWriterResult,
    NarrationSourceSpan,
    SourceClaim,
)
from app.marcus.lesson_plan.prework_projection import (
    ObjectiveInput,
    PromiseProjection,
    PromiseTransformRequest,
    PromiseVow,
    SceneBrief,
    SceneComposeRequest,
)
from app.marcus.lesson_plan.scene_extraction import (
    _faithfulness_failures,
    scene_faithfulness_prompt_constraints,
)
from app.marcus.orchestrator.workbook_prework_writers import (
    DEEP_DIVE_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
    WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS,
    DeepDiveProviderOutputError,
    LiveDeepDiveWriter,
    LivePromiseTransformer,
    LiveSceneComposer,
    normalize_deep_dive_provider_payload,
)


class _Structured:
    last_messages = None

    def __init__(self, value):
        self.value = value

    def invoke(self, messages):
        assert len(messages) == 2
        _Structured.last_messages = messages
        return {
            "parsed": self.value,
            "raw": SimpleNamespace(
                response_metadata={
                    "request_id": "req-fixture",
                    "token_usage": {
                        "input_tokens": 120,
                        "output_tokens": 30,
                        "cost_usd": 0.01,
                    },
                }
            ),
            "parsing_error": None,
        }


class _Chat:
    def __init__(self, values):
        self.values = values

    def with_structured_output(self, output_type, *, include_raw=False):
        assert include_raw is True
        return _Structured(self.values[output_type])


def test_named_adapters_make_one_call_each_without_live_provider() -> None:
    values = {
        SceneBrief: SceneBrief(
            status="authored",
            text="A delay blocks transport work.",
            source_refs=("source#Q5",),
            known_losses=(),
            marker=None,
            lesson_type="fresh_pain",
            archetype="external_friction",
        ),
        PromiseProjection: PromiseProjection(
            status="authored",
            vows=(PromiseVow(objective_id="LO-1", text="I can take a first move."),),
            known_losses=(),
            marker=None,
        ),
    }

    def factory(*args, **kwargs):
        return SimpleNamespace(chat=_Chat(values), entry=None)

    scene = LiveSceneComposer(chat_factory=factory)
    promise = LivePromiseTransformer(chat_factory=factory)
    scene(
        SceneComposeRequest(
            seed_text="delay transport",
            source_refs=("source#Q5",),
            lesson_type="fresh_pain",
            archetype="external_friction",
            payoff_slide_keys=("slides/slide-1.md",),
        )
    )
    promise(
        PromiseTransformRequest(
            objectives=(
                ObjectiveInput(objective_id="LO-1", text="Take a first move", status="ratified"),
            ),
            transformation_posture="pertinent_ability_first_move",
        )
    )
    assert scene.calls_made == promise.calls_made == 1
    assert scene.model_config.default_model == promise.model_config.default_model == "gpt-5"
    assert scene.model_config_digest.startswith("sha256:")
    assert scene.last_request_id == promise.last_request_id == "req-fixture"
    assert scene.last_input_tokens == promise.last_input_tokens == 120
    assert scene.last_output_tokens == promise.last_output_tokens == 30
    assert scene.last_cost_usd + promise.last_cost_usd == 0.02
    scene_prompt = _Structured.last_messages[0][1]
    assert "known_losses MUST be []" in scene_prompt
    assert "marker MUST be null" in scene_prompt
    assert "objective IDs" in scene_prompt


def test_deep_dive_alone_binds_32k_and_effective_config_identity() -> None:
    calls: list[dict[str, object]] = []

    def factory(*args, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(chat=_Chat({}), entry=None)

    scene = LiveSceneComposer(chat_factory=factory)
    promise = LivePromiseTransformer(chat_factory=factory)
    deep = LiveDeepDiveWriter(chat_factory=factory)
    overridden = LiveDeepDiveWriter(chat_factory=factory, max_completion_tokens=12345)

    assert WORKBOOK_DEEP_DIVE_MAX_COMPLETION_TOKENS == 32000
    assert [call["max_completion_tokens"] for call in calls] == [
        4096,
        4096,
        32000,
        12345,
    ]
    assert scene.model_config_digest == promise.model_config_digest
    assert deep.model_config_digest != scene.model_config_digest
    assert overridden.model_config_digest != deep.model_config_digest
    assert calls[2]["system_prompt_hash"] == deep.model_config_digest
    assert calls[3]["system_prompt_hash"] == overridden.model_config_digest
    assert DEEP_DIVE_PROVIDER_CONTRACT_MODE == "raw-json-schema"
    assert DEEP_DIVE_PROVIDER_NORMALIZER_VERSION == "deep-dive-provider-normalizer.v1"


def test_deep_dive_normalizer_only_removes_safe_exact_duplicate_terms() -> None:
    raw = {
        "status": "authored",
        "sections": [],
        "bold_terms": [
            {"term": "burnout"},
            {"term": "burnout"},
            {"term": "Burnout"},
            {"term": "burnout "},
            {"term": "burnout", "extra": "unsafe"},
            {"term": "burnout"},
        ],
        "known_losses": [],
        "marker": None,
    }
    normalized, records = normalize_deep_dive_provider_payload(raw)
    assert raw["bold_terms"] != normalized["bold_terms"]
    assert normalized == {
        **raw,
        "bold_terms": [
            {"term": "burnout"},
            {"term": "Burnout"},
            {"term": "burnout "},
            {"extra": "unsafe", "term": "burnout"},
        ],
    }
    assert records == (
        "deduplicated_exact_bold_term:burnout",
        "deduplicated_exact_bold_term:burnout",
    )


def test_deep_dive_normalizer_refuses_non_json_list_coercion() -> None:
    raw = {
        "status": "authored",
        "sections": [],
        "bold_terms": ({"term": "burnout"}, {"term": "burnout"}),
        "known_losses": [],
        "marker": None,
    }
    with pytest.raises(TypeError, match="JSON list"):
        normalize_deep_dive_provider_payload(raw)
    assert raw["bold_terms"][1] == {"term": "burnout"}


def test_deep_dive_normalizer_never_merges_unicode_equivalents() -> None:
    composed = "caf\u00e9"
    decomposed = "cafe\u0301"
    raw = {
        "status": "authored",
        "sections": [],
        "bold_terms": [
            {"term": composed},
            {"term": decomposed},
            {"term": composed},
            {"term": decomposed},
        ],
        "known_losses": [],
        "marker": None,
    }
    normalized, records = normalize_deep_dive_provider_payload(raw)
    assert normalized["bold_terms"] == [{"term": composed}, {"term": decomposed}]
    assert records == (
        f"deduplicated_exact_bold_term:{composed}",
        f"deduplicated_exact_bold_term:{decomposed}",
    )


@pytest.mark.parametrize("status", ["degraded", "unavailable"])
def test_deep_dive_normalizer_never_changes_non_authored_payload(status: str) -> None:
    raw = {
        "status": status,
        "sections": [],
        "bold_terms": [{"term": "burnout"}, {"term": "burnout"}],
        "known_losses": ["deep_dive_writer_unavailable"],
        "marker": "deep_dive_skeleton_unavailable",
    }
    normalized, records = normalize_deep_dive_provider_payload(raw)
    assert normalized == raw
    assert records == ()


def test_live_deep_dive_observes_raw_schema_then_strictly_validates_normalized() -> None:
    fixture = Path("tests/fixtures/deep_dive_37_2a")
    request = DeepDiveSkeletonRequest.model_validate_json(
        (fixture / "request.json").read_text("utf-8")
    )
    raw = json.loads((fixture / "writer_result.json").read_text("utf-8"))
    raw["bold_terms"].append({"term": "two stages"})

    class RawStructured:
        def invoke(self, messages):
            return {
                "parsed": raw,
                "raw": SimpleNamespace(response_metadata={}),
                "parsing_error": None,
            }

    class RawChat:
        def with_structured_output(self, schema, *, include_raw=False):
            assert schema == DeepDiveSkeletonWriterResult.model_json_schema()
            assert include_raw is True
            return RawStructured()

    writer = LiveDeepDiveWriter(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=RawChat(), entry=None)
    )
    candidate = writer(request)
    assert tuple(term.term for term in candidate.bold_terms) == ("two stages",)
    assert writer.last_raw_provider_payload["bold_terms"] == [
        {"term": "two stages"},
        {"term": "two stages"},
    ]
    assert writer.last_provider_normalizations == (
        "deduplicated_exact_bold_term:two stages",
    )


def test_live_deep_dive_refuses_tuple_before_provider_payload_canonicalization() -> None:
    fixture = Path("tests/fixtures/deep_dive_37_2a")
    request = DeepDiveSkeletonRequest.model_validate_json(
        (fixture / "request.json").read_text("utf-8")
    )
    raw = json.loads((fixture / "writer_result.json").read_text("utf-8"))
    raw["bold_terms"] = tuple((*raw["bold_terms"], raw["bold_terms"][0]))

    class TupleChat:
        def with_structured_output(self, schema, *, include_raw=False):
            return SimpleNamespace(
                invoke=lambda messages: {
                    "parsed": raw,
                    "raw": SimpleNamespace(response_metadata={}),
                    "parsing_error": None,
                }
            )

    writer = LiveDeepDiveWriter(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=TupleChat(), entry=None)
    )
    with pytest.raises(DeepDiveProviderOutputError, match="JSON list"):
        writer(request)
    assert writer.last_raw_provider_payload["bold_terms"] == list(raw["bold_terms"])
    assert writer.last_raw_provider_payload_digest.startswith("sha256:")
    assert "JSON list" in writer.last_provider_normalization_error


def test_live_deep_dive_leaves_unsafe_duplicate_untouched_and_fails_strict() -> None:
    fixture = Path("tests/fixtures/deep_dive_37_2a")
    request = DeepDiveSkeletonRequest.model_validate_json(
        (fixture / "request.json").read_text("utf-8")
    )
    raw = json.loads((fixture / "writer_result.json").read_text("utf-8"))
    raw["bold_terms"].append({"term": "two stages", "extra": "planted"})

    class RawChat:
        def with_structured_output(self, schema, *, include_raw=False):
            return SimpleNamespace(
                invoke=lambda messages: {
                    "parsed": raw,
                    "raw": SimpleNamespace(response_metadata={}),
                    "parsing_error": None,
                }
            )

    writer = LiveDeepDiveWriter(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=RawChat(), entry=None)
    )
    with pytest.raises(DeepDiveProviderOutputError):
        writer(request)
    assert writer.last_provider_normalizations == ()
    assert writer.last_raw_provider_payload["bold_terms"][-1]["extra"] == "planted"


def test_live_scene_prompt_and_validator_reject_mixed_authored_shape() -> None:
    malformed = {
        "status": "authored",
        "text": "A delay blocks work.",
        "source_refs": ("source#Q5",),
        "known_losses": ("fabricated_loss",),
        "marker": "unavailable",
        "lesson_type": "fresh_pain",
        "archetype": "external_friction",
    }

    class BadStructured:
        def invoke(self, messages):
            assert "Never mix authored with a marker/loss" in messages[0][1]
            assert "source#Q5" in messages[0][1]
            return {
                "parsed": malformed,
                "raw": SimpleNamespace(response_metadata={}),
                "parsing_error": None,
            }

    class BadChat:
        def with_structured_output(self, output_type, *, include_raw=False):
            assert output_type is SceneBrief and include_raw
            return BadStructured()

    writer = LiveSceneComposer(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=BadChat(), entry=None)
    )
    with pytest.raises(ValidationError, match="authored Scene cannot carry losses"):
        writer(
            SceneComposeRequest(
                seed_text="A delay blocks work.",
                source_refs=("source#Q5",),
                lesson_type="fresh_pain",
                archetype="external_friction",
                payoff_slide_keys=("slides/slide-5.md",),
            )
        )


def test_provider_tokens_use_established_pricing_when_cost_omitted() -> None:
    scene = SceneBrief(
        status="authored",
        text="A delay blocks work.",
        source_refs=("source#Q5",),
        known_losses=(),
        marker=None,
        lesson_type="fresh_pain",
        archetype="external_friction",
    )

    class TokenStructured:
        def invoke(self, messages):
            return {
                "parsed": scene,
                "raw": SimpleNamespace(
                    response_metadata={
                        "request_id": "req-token-only",
                        "token_usage": {"input_tokens": 120, "output_tokens": 30},
                    }
                ),
                "parsing_error": None,
            }

    class TokenChat:
        def with_structured_output(self, output_type, *, include_raw=False):
            return TokenStructured()

    writer = LiveSceneComposer(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=TokenChat(), entry=None)
    )
    writer(
        SceneComposeRequest(
            seed_text="A delay blocks work.",
            source_refs=("source#Q5",),
            lesson_type="fresh_pain",
            archetype="external_friction",
            payoff_slide_keys=("slides/slide-5.md",),
        )
    )
    assert writer.last_cost_usd == pytest.approx(0.00045)
    assert writer.last_cost_unavailable_reason is None


def test_provider_metadata_preserves_explicit_zero_values() -> None:
    writer = LiveSceneComposer(
        chat_factory=lambda *args, **kwargs: SimpleNamespace(chat=object(), entry=None)
    )
    writer._record_metadata(  # noqa: SLF001
        SimpleNamespace(
            response_metadata={
                "request_id": "req-zero",
                "token_usage": {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                },
            }
        )
    )
    assert writer.last_input_tokens == 0
    assert writer.last_output_tokens == 0
    assert writer.last_cost_usd == 0.0
    assert writer.last_cost_unavailable_reason is None


def test_scene_prompt_constraints_are_the_gate_constraints() -> None:
    seed = "Never let 7 delayed teams lose clinical context."
    constraints = scene_faithfulness_prompt_constraints(seed)
    request = SceneComposeRequest(
        seed_text=seed,
        source_refs=("source#Q5",),
        lesson_type="fresh_pain",
        archetype="external_friction",
        payoff_slide_keys=("slides/slide-5.md",),
    )
    writer = LiveSceneComposer.__new__(LiveSceneComposer)
    prompt = writer._system_prompt(request)
    assert str(constraints.required_shared_count) in prompt
    assert f"{constraints.minimum_recall:.0%}" in prompt
    assert repr(dict(constraints.digit_multiset)) in prompt
    assert repr(dict(constraints.negator_multiset)) in prompt
    assert "Do not copy the Correct Answer" in prompt
    assert "do not fabricate a resolution" in prompt

    passing = "Never let 7 delayed teams lose context."
    assert _faithfulness_failures(seed, passing)[0] == ()
    for mutation, expected in (
        ("A smooth workflow resolves everything.", "scene_faithfulness_overlap"),
        ("Never let 8 delayed teams lose context.", "scene_faithfulness_numeral"),
        ("Let 7 delayed teams lose context.", "scene_faithfulness_negator"),
    ):
        assert expected in _faithfulness_failures(seed, mutation)[0]


def test_setup_only_scene_prompt_never_exposes_resolution_and_fences_payoff_authority() -> None:
    request = SceneComposeRequest(
        seed_text=(
            "You are an attending physician managing a complex workflow. "
            "You notice a recurring delay in patient transport."
        ),
        source_refs=("assessment.md#Q5",),
        lesson_type="fresh_pain",
        archetype="external_friction",
        payoff_slide_keys=("slides/slide-5.md",),
        setup_only=True,
    )
    writer = LiveSceneComposer.__new__(LiveSceneComposer)
    prompt = writer._system_prompt(request)
    assert "setup-only assessment scenario" in prompt
    assert "Do not state or infer an answer, cause, barrier" in prompt
    assert "Payoff slides are coverage targets, not content authority" in prompt
    assert "structured innovation process" not in prompt
    assert "organizational authority/safety" not in prompt


def test_deep_dive_thin_authority_prompt_does_not_invent_delta_requirement() -> None:
    request = DeepDiveSkeletonRequest(
        lesson_ref="run:fixture",
        source_spans=(
            NarrationSourceSpan(
                span_id="vo:seg-01",
                text="A visible workflow symptom deserves analysis.",
                source_ref="exports/segment-manifest-storyboard-b.yaml#segments/seg-01/narration_text",
            ),
        ),
        source_claims=(
            SourceClaim(
                claim_id="claim:vo:seg-01",
                text="A visible workflow symptom deserves analysis.",
                source_span_refs=("vo:seg-01",),
                role="vo",
            ),
        ),
        abilities=(DeepDiveAbilityInput(ability_id="LO-1", text="I can analyze it."),),
    )
    prompt = LiveDeepDiveWriter.__new__(LiveDeepDiveWriter)._system_prompt(request)
    assert "no source_supported_delta authority is declared" in prompt
    assert "at least one source_supported_delta claim" not in prompt
