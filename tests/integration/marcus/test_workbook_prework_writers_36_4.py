from types import SimpleNamespace

import pytest
from pydantic import ValidationError

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
    LivePromiseTransformer,
    LiveSceneComposer,
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
