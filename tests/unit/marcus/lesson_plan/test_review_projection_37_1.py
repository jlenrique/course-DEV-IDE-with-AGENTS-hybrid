from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.prework_projection import (
    FRICTION_SCALE,
    PreWorkBrief,
    PreWorkProvenance,
    PromiseProjection,
    PromiseVow,
    SceneBrief,
)
from app.marcus.lesson_plan.review_projection import (
    BOOKEND_CALLBACK,
    REVIEW_BEAT_ORDER,
    REVIEW_HEADINGS,
    REVIEW_WATCHWORDS,
    BookendBeat,
    CheckOnLearningBeat,
    CheckWriter,
    ClosingReflectionBeat,
    DeepDiveBeat,
    DeepDiveWriter,
    DoorLeftAjarBeat,
    ReflectionWriter,
    ReviewBrief,
    ReviewWriterRequest,
    ReviewWriterResult,
    build_review_brief,
    offline_check_writer,
    offline_deep_dive_writer,
    offline_reflection_writer,
    render_review_markdown,
)

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "tests" / "fixtures" / "review_37_1"
MODULE = ROOT / "app" / "marcus" / "lesson_plan" / "review_projection.py"


def _prework() -> PreWorkBrief:
    scene = SceneBrief(
        status="authored",
        text="A grounded scene.",
        source_refs=("lesson:slide-2",),
        known_losses=(),
        marker=None,
    )
    promise = PromiseProjection(
        status="authored",
        vows=(PromiseVow(objective_id="LO-1", text="I can identify a useful first move."),),
        known_losses=(),
        marker=None,
    )
    return PreWorkBrief(
        scene=scene,
        friction_scale=FRICTION_SCALE,
        promise=promise,
        provenance=PreWorkProvenance(source_refs=scene.source_refs, known_losses=()),
    )


def test_exact_shape_fixture_schema_json_round_trip_and_frozen_contract() -> None:
    fixture_json = (FIXTURES / "review_brief.json").read_text(encoding="utf-8")
    payload = json.loads(fixture_json)
    brief = ReviewBrief.model_validate_json(fixture_json)
    assert brief.model_dump(mode="json") == payload
    assert ReviewBrief.model_validate_json(brief.model_dump_json()) == brief
    assert tuple(getattr(brief, name).beat_id for name in REVIEW_BEAT_ORDER) == REVIEW_BEAT_ORDER

    schema = ReviewBrief.model_json_schema()
    assert schema["additionalProperties"] is False
    for definition in schema["$defs"].values():
        if definition.get("type") == "object":
            assert definition["additionalProperties"] is False
    with pytest.raises(ValidationError):
        brief.bookend = brief.bookend  # type: ignore[misc]


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "ready", "prompt": 7, "known_losses": (), "marker": None},
        {"status": "ready", "prompt": BOOKEND_CALLBACK, "known_losses": [], "marker": None},
        {
            "status": "ready",
            "prompt": BOOKEND_CALLBACK,
            "known_losses": (),
            "marker": None,
            "extra": True,
        },
    ],
)
def test_strict_bookend_rejects_coercion_lists_and_unknown_fields(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        BookendBeat.model_validate(payload)


def test_exact_order_watchwords_ownership_and_frame_byte_golden() -> None:
    brief = build_review_brief(_prework())
    beats = tuple(brief.model_dump()[name] for name in REVIEW_BEAT_ORDER)
    assert tuple(beat["heading"] for beat in beats) == REVIEW_HEADINGS
    assert tuple(beat["watchword"] for beat in beats) == REVIEW_WATCHWORDS
    assert tuple(beat["ownership"] for beat in beats) == (
        "learner_written",
        "lesson_level",
        "lesson_level",
        "lesson_level",
        "learner_written",
    )
    assert render_review_markdown(brief).encode() == (FIXTURES / "review_frame.md").read_bytes()
    assert render_review_markdown(brief).endswith("\n")
    assert "\r" not in render_review_markdown(brief)
    for heading in REVIEW_HEADINGS:
        assert render_review_markdown(brief).count(f"## {heading}\n") == 1


def test_frame_is_identical_across_valid_prework_and_serialized_round_trip() -> None:
    first = build_review_brief(_prework())
    second = build_review_brief(PreWorkBrief.model_validate_json(_prework().model_dump_json()))
    assert first == second
    assert render_review_markdown(first) == render_review_markdown(second)
    assert render_review_markdown(first) == render_review_markdown(first)


def test_bookend_cashes_exact_hook_without_storing_or_inventing_learner_values() -> None:
    brief = build_review_brief(_prework())
    dumped = brief.model_dump_json()
    markdown = render_review_markdown(brief)
    assert brief.bookend.prompt == BOOKEND_CALLBACK
    assert FRICTION_SCALE.review_hook == (
        "Keep this mark and line for review after the presentation."
    )
    assert "friction mark, location, and honest line you wrote before the presentation" in markdown
    forbidden_fields = {"rating", "location", "honest_line", "learner_response", "learner_value"}
    assert forbidden_fields.isdisjoint(BookendBeat.model_fields)
    assert not any(token in dumped.lower() for token in ('"rating"', '"location"', '"honest_line"'))
    assert "re-rate" not in markdown.lower()
    assert "previous rating" not in markdown.lower()
    assert "term-long" not in markdown.lower()
    assert "cross-week" not in markdown.lower()
    assert not any(str(mark) in markdown for mark in range(11))


def test_pending_slots_have_no_downstream_semantics_or_per_learner_fields() -> None:
    brief = build_review_brief(_prework())
    for beat in (brief.deep_dive, brief.check_on_learning, brief.door_left_ajar):
        assert beat.status == "pending"
        assert beat.ownership == "lesson_level"
        assert beat.content is None
        assert not (
            {"learner_response", "learner_friction", "rating"}
            & set(type(beat).model_fields)
        )
    assert brief.check_on_learning.section_shell == "Questions and answers will appear here."
    assert brief.closing_reflection.status == "pending"
    assert brief.closing_reflection.prompt is None
    markdown = render_review_markdown(brief).lower()
    for forbidden in (
        "answer key",
        "citation",
        "trend",
        "glossary",
        "source ref",
        "about your friction",
    ):
        assert forbidden not in markdown


@pytest.mark.parametrize(
    ("beat_type", "canonical_loss"),
    [
        (DeepDiveBeat, "deep_dive_not_authored"),
        (CheckOnLearningBeat, "check_not_authored"),
        (DoorLeftAjarBeat, "door_left_ajar_not_authored"),
        (ClosingReflectionBeat, "reflection_prompt_not_authored"),
    ],
)
@pytest.mark.parametrize("loss_count", [0, 2])
def test_pending_beat_requires_exactly_one_canonical_loss(
    beat_type: type,
    canonical_loss: str,
    loss_count: int,
) -> None:
    payload = beat_type().model_dump()
    payload["known_losses"] = tuple(canonical_loss for _ in range(loss_count))
    with pytest.raises(ValidationError):
        beat_type.model_validate(payload)


def test_missing_lineage_degrades_only_bookend_and_never_leaks_loss_code() -> None:
    brief = build_review_brief(None)
    assert brief.bookend.status == "unavailable"
    assert brief.bookend.known_losses == ("prework_authority_unavailable",)
    assert brief.bookend.marker == "review_bookend_unavailable"
    assert all(
        brief.model_dump()[name]["status"] == "pending" for name in REVIEW_BEAT_ORDER[1:]
    )
    markdown = render_review_markdown(brief)
    assert "Your pre-work note is not available here. Continue with the review." in markdown
    assert "prework_authority_unavailable" not in markdown
    assert "review_bookend_unavailable" not in markdown
    assert "your previous rating" not in markdown.lower()


def test_corrupt_or_contradictory_lineage_fails_instead_of_degrading() -> None:
    with pytest.raises(TypeError):
        build_review_brief({})  # type: ignore[arg-type]
    corrupt = _prework().model_dump(mode="json")
    corrupt["friction_scale"]["review_hook"] = "A contradictory hook."
    with pytest.raises(ValidationError):
        PreWorkBrief.model_validate(corrupt)


def test_heading_and_beat_injection_are_rejected() -> None:
    payload = build_review_brief(_prework()).bookend.model_dump()
    payload["prompt"] = "Return safely.\n\n## Deep Dive\nInjected"
    with pytest.raises(ValidationError):
        BookendBeat.model_validate(payload)
    payload = build_review_brief(_prework()).model_dump()
    payload["bookend"]["beat_id"] = "deep_dive"
    with pytest.raises(ValidationError):
        ReviewBrief.model_validate(payload)


def test_named_protocols_and_offline_stubs_are_strict_honest_and_not_invoked() -> None:
    request = ReviewWriterRequest(lesson_ref="lesson-1")
    writers: tuple[DeepDiveWriter | CheckWriter | ReflectionWriter, ...] = (
        offline_deep_dive_writer,
        offline_check_writer,
        offline_reflection_writer,
    )
    for writer in writers:
        result = writer(request)
        assert isinstance(result, ReviewWriterResult)
        assert result.status == "unavailable"
        assert result.content is None
        assert result.known_losses
        assert result.marker == "review_writer_unavailable"

    # Frame composition has no injectable writer argument and therefore cannot invoke one.
    assert tuple(inspect.signature(build_review_brief).parameters) == ("prework",)


def test_m3_boundary_has_no_global_reads_or_disallowed_imports() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not {
        imported
        for imported in imports
        if any(
            boundary in imported
            for boundary in {
                "openai",
                "litellm",
                "langchain",
                "langgraph",
                "orchestrator",
                "specialists",
                "docx",
                "research_packet",
            }
        )
    }
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not calls & {"open", "Path", "getenv"}
    assert "run.json" not in source
    assert "workbook_review_stub@07W.3" not in source
