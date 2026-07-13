from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PREWORK_STUB_MARKER,
    ObjectiveInput,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    PromiseTransformer,
    PromiseTransformRequest,
    PromiseVow,
    SceneBrief,
    SceneComposer,
    SceneComposeRequest,
    offline_promise_transformer,
    offline_scene_composer,
    render_deterministic_frame,
    render_prework_markdown,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "prework_36_1"


def _scene(*, text: str | None = "A source-grounded opening scene.") -> SceneBrief:
    return SceneBrief(
        status="authored" if text else "unavailable",
        text=text,
        source_refs=("lesson:segment-1",) if text else (),
        known_losses=() if text else ("scene_not_authored",),
        marker=None if text else PREWORK_STUB_MARKER,
    )


def _promise(*, text: str | None = "I can distinguish signal from noise.") -> PromiseProjection:
    return PromiseProjection(
        status="authored" if text else "unavailable",
        vows=(PromiseVow(objective_id="LO-1", text=text),) if text else (),
        known_losses=() if text else ("promise_not_authored",),
        marker=None if text else PREWORK_STUB_MARKER,
    )


def _brief(
    *,
    scene: str | None = "A source-grounded opening scene.",
    promise: str | None = "I can distinguish signal from noise.",
) -> PreWorkBrief:
    scene_result = _scene(text=scene)
    promise_result = _promise(text=promise)
    return PreWorkBrief(
        scene=scene_result,
        friction_scale=FRICTION_SCALE,
        promise=promise_result,
        provenance=PreWorkProvenance(
            source_refs=scene_result.source_refs,
            known_losses=scene_result.known_losses + promise_result.known_losses,
        ),
    )


def test_contract_fixture_exact_dump_schema_and_round_trip() -> None:
    fixture_json = (FIXTURES / "prework_brief.json").read_text(encoding="utf-8")
    payload = json.loads(fixture_json)
    # JSON arrays are the serialized tuple representation; Python list inputs
    # remain coercion-red under strict model_validate (pinned below).
    brief = PreWorkBrief.model_validate_json(fixture_json)
    assert brief.model_dump(mode="json") == payload
    assert PreWorkBrief.model_validate_json(brief.model_dump_json()) == brief

    schema = PreWorkBrief.model_json_schema()
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["scene", "friction_scale", "promise", "provenance"]
    assert schema["properties"]["beat_order"]["type"] == "array"
    for definition in schema["$defs"].values():
        if definition.get("type") == "object":
            assert definition["additionalProperties"] is False


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (SceneComposeRequest, {"seed_text": 7, "source_refs": (), "orienting_hint": None}),
        (
            SceneComposeRequest,
            {"seed_text": "seed", "source_refs": ["ref"], "orienting_hint": None},
        ),
        (SceneComposeRequest, {"seed_text": "seed", "source_refs": (), "orienting_hint": False}),
        (ObjectiveInput, {"objective_id": "LO-1", "text": "Do it", "status": True}),
        (
            PromiseTransformRequest,
            {
                "objectives": [{"objective_id": "LO-1", "text": "Do it", "status": "ratified"}],
                "scene_context": None,
                "friction_context": None,
            },
        ),
        (
            SceneBrief,
            {
                "status": "authored",
                "text": "x",
                "source_refs": (),
                "known_losses": (),
                "marker": None,
                "extra": "no",
            },
        ),
    ],
)
def test_strict_contract_rejects_coercion_nested_lists_and_extra(
    model: type, payload: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_contract_is_frozen_and_rejects_inconsistent_nested_values() -> None:
    brief = _brief()
    with pytest.raises(ValidationError):
        brief.scene = _scene(text=None)  # type: ignore[misc]
    with pytest.raises(ValidationError):
        SceneBrief(status="authored", text=None, source_refs=(), known_losses=(), marker=None)
    with pytest.raises(ValidationError):
        PromiseProjection(
            status="unavailable",
            vows=(PromiseVow(objective_id="LO-1", text="invented"),),
            known_losses=(),
            marker=PREWORK_STUB_MARKER,
        )


@pytest.mark.parametrize(
    ("result_type", "payload"),
    [
        (
            SceneBrief,
            dict(
                status="authored",
                text="scene",
                source_refs=("ref",),
                known_losses=("loss",),
                marker=None,
            ),
        ),
        (
            SceneBrief,
            dict(
                status="authored",
                text="scene",
                source_refs=("ref",),
                known_losses=(),
                marker=PREWORK_STUB_MARKER,
            ),
        ),
        (
            SceneBrief,
            dict(
                status="degraded",
                text=None,
                source_refs=(),
                known_losses=(),
                marker=PREWORK_STUB_MARKER,
            ),
        ),
        (
            SceneBrief,
            dict(
                status="unavailable", text=None, source_refs=(), known_losses=("loss",), marker=None
            ),
        ),
        (
            PromiseProjection,
            dict(
                status="authored",
                vows=(PromiseVow(objective_id="LO-1", text="vow"),),
                known_losses=("loss",),
                marker=None,
            ),
        ),
        (
            PromiseProjection,
            dict(status="unavailable", vows=(), known_losses=(), marker=PREWORK_STUB_MARKER),
        ),
    ],
)
def test_result_marker_and_loss_consistency_is_bidirectional(
    result_type: type, payload: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        result_type.model_validate(payload)


def test_request_context_fields_are_optional_and_minimal_requests_validate() -> None:
    scene = SceneComposeRequest(seed_text="seed", source_refs=("ref",))
    promise = PromiseTransformRequest(
        objectives=(ObjectiveInput(objective_id="LO-1", text="Do it", status="ratified"),)
    )
    assert scene.orienting_hint is None
    assert promise.scene_context is promise.friction_context is None


@pytest.mark.parametrize(
    ("model", "payload"),
    [
        (PromiseVow, dict(objective_id=" ", text="vow")),
        (PromiseVow, dict(objective_id="LO-1", text="\t")),
        (ObjectiveInput, dict(objective_id="", text="objective", status="ratified")),
        (ObjectiveInput, dict(objective_id="LO-1", text="  ", status="ratified")),
        (SceneComposeRequest, dict(seed_text="\n", source_refs=("ref",))),
        (SceneComposeRequest, dict(seed_text="seed", source_refs=("",))),
        (
            SceneBrief,
            dict(
                status="unavailable",
                text=None,
                source_refs=(),
                known_losses=(" ",),
                marker=PREWORK_STUB_MARKER,
            ),
        ),
        (PreWorkProvenance, dict(source_refs=("ref", " "), known_losses=())),
    ],
)
def test_blank_strings_and_empty_tuple_members_are_rejected(
    model: type, payload: dict[str, object]
) -> None:
    with pytest.raises(ValidationError):
        model.model_validate(payload)


def test_semantic_markdown_cannot_forge_frame_but_scene_paragraphs_are_allowed() -> None:
    paragraphs = "First grounded paragraph.\n\nSecond grounded paragraph."
    assert paragraphs in render_prework_markdown(_brief(scene=paragraphs))
    with pytest.raises(ValidationError):
        _scene(text="Grounded start.\n\n## Promise\nForged order")
    with pytest.raises(ValidationError):
        PromiseVow(objective_id="LO-1", text="Safe vow\n- injected second vow")


def test_aggregate_provenance_must_equal_nested_sources_and_losses() -> None:
    scene = _scene(text=None)
    promise = _promise(text=None)
    expected_losses = scene.known_losses + promise.known_losses
    valid = PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise,
        provenance=PreWorkProvenance(source_refs=(), known_losses=expected_losses),
    )
    assert valid.provenance.known_losses == expected_losses
    with pytest.raises(ValidationError):
        PreWorkBrief(
            scene=scene,
            friction_scale=FRICTION_SCALE,
            promise=promise,
            provenance=PreWorkProvenance(source_refs=("forged",), known_losses=expected_losses),
        )
    with pytest.raises(ValidationError):
        PreWorkBrief(
            scene=scene,
            friction_scale=FRICTION_SCALE,
            promise=promise,
            provenance=PreWorkProvenance(source_refs=(), known_losses=()),
        )


def test_deterministic_frame_has_exact_byte_golden_and_is_metadata_independent() -> None:
    expected = (FIXTURES / "deterministic_frame.md").read_bytes()
    rendered = render_deterministic_frame()
    assert rendered.encode("utf-8") == expected
    assert rendered.endswith("\n") and not rendered.endswith("\n\n")
    assert render_deterministic_frame() == render_deterministic_frame()


def test_full_renderer_order_partial_copy_and_semantic_variation() -> None:
    neither = render_prework_markdown(_brief(scene=None, promise=None))
    scene_only = render_prework_markdown(_brief(promise=None))
    promise_only = render_prework_markdown(_brief(scene=None))
    assert (
        neither.index("## Scene") < neither.index("## Friction Scale") < neither.index("## Promise")
    )
    assert "Source-grounded Scene not yet authored." in neither
    assert "Ratified-objective Promise not yet authored." in neither
    assert "Source-grounded Scene not yet authored." not in scene_only
    assert "Ratified-objective Promise not yet authored." not in promise_only
    for rendered in (neither, scene_only, promise_only):
        assert not any(
            code in rendered
            for code in ("scene_not_authored", "promise_not_authored", PREWORK_STUB_MARKER)
        )
        for heading in ("## Scene", "## Friction Scale", "## Promise"):
            assert heading in rendered
    assert render_prework_markdown(_brief(scene="Scene A")) != render_prework_markdown(
        _brief(scene="Scene B")
    )


def test_friction_scale_copy_and_negative_language_fences() -> None:
    frame = render_deterministic_frame()
    required = (
        "about 20 seconds",
        "Rate this friction from 0 to 10.",
        "**0** — present, but not getting in the way.",
        "**10** — repeatedly blocks the work.",
        "Locate where it shows up.",
        "Write one honest line.",
        "Keep this mark and line for review after the presentation.",
    )
    assert all(copy in frame for copy in required)
    forbidden = (
        "frictionless",
        "answer key",
        "correct",
        "incorrect",
        "re-rate",
        "rerate",
        "aggregation",
        "learner value",
        "self-portrait",
    )
    assert not any(term in frame.lower() for term in forbidden)


def test_protocol_signatures_stubs_spies_and_json_serialization() -> None:
    assert (
        str(inspect.signature(SceneComposer.__call__))
        == "(self, request: 'SceneComposeRequest') -> 'SceneBrief'"
    )
    assert (
        str(inspect.signature(PromiseTransformer.__call__))
        == "(self, request: 'PromiseTransformRequest') -> 'PromiseProjection'"
    )
    scene_request = SceneComposeRequest(
        seed_text="seed", source_refs=("ref:1",), orienting_hint="orient"
    )
    promise_request = PromiseTransformRequest(
        objectives=(ObjectiveInput(objective_id="LO-1", text="Distinguish", status="ratified"),),
        scene_context="context",
        friction_context="friction",
    )
    scene = offline_scene_composer(scene_request)
    promise = offline_promise_transformer(promise_request)
    assert scene.status == promise.status == "unavailable"
    assert scene.text is None and promise.vows == ()
    assert scene.marker == promise.marker == PREWORK_STUB_MARKER
    json.dumps(scene_request.model_dump(mode="json"))
    json.dumps(promise_request.model_dump(mode="json"))

    seen: list[object] = []

    def scene_spy(request: SceneComposeRequest) -> SceneBrief:
        seen.append(request)
        return _scene(text="Injected")

    assert scene_spy(scene_request).text == "Injected"
    assert seen == [scene_request]


def _ast_boundary_violations(source: str) -> list[str]:
    tree = ast.parse(source)
    denied_modules = (
        "orchestrator",
        "specialists",
        "terminal",
        "render",
        "openai",
        "anthropic",
        "litellm",
    )
    denied_constructor_tokens = ("client", "modelconfig", "model_config", "load_model_config")
    aliases: dict[str, str] = {}
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
                if any(term in alias.name.lower() for term in denied_modules):
                    violations.append(f"import:{alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{module}.{alias.name}"
            if any(term in module.lower() for term in denied_modules):
                violations.append(f"import:{module}")
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call = ast.unparse(node.func)
        root, _, suffix = call.partition(".")
        resolved = ".".join(part for part in (aliases.get(root, root), suffix) if part)
        normalized = resolved.lower().replace("-", "_")
        leaf = normalized.rsplit(".", 1)[-1]
        if any(term in normalized for term in ("openai", "anthropic", "litellm")) or any(
            token in leaf for token in denied_constructor_tokens
        ):
            violations.append(f"call:{resolved}")
    return violations


def test_m3_ast_boundary_and_public_exports() -> None:
    import app.marcus.lesson_plan.prework_projection as module

    source = inspect.getsource(module)
    assert _ast_boundary_violations(source) == []
    synthetic_denied = """
import openai as sdk
from anthropic import Anthropic as ClaudeClient
from app.runtime.config import ModelConfig as MC
sdk.OpenAI()
ClaudeClient()
MC()
provider.model_client()
"""
    violations = _ast_boundary_violations(synthetic_denied)
    assert {
        "call:openai.OpenAI",
        "call:anthropic.Anthropic",
        "call:app.runtime.config.ModelConfig",
    }.issubset(violations)
    assert "call:provider.model_client" in violations
    assert {"SceneComposer", "PromiseTransformer"}.issubset(module.__all__)
    assert not any(name in source for name in ("DeepDiveWriter", "CheckWriter", "ReflectionWriter"))
