"""Shape-stable contract tests for the CollateralSpec family (Braid S1).

Per checklist §8 (per-family shape-pin) + the schema-shape AC battery
(AC-1..AC-6 of spec-braid-s1-lesson-plan-collateral-research-spec.md). Each
family gets its own allowlist so a single family change fails in isolation and
drives a per-family SCHEMA_CHANGELOG entry.

These are RED-first: written before collateral_spec.py exists.
"""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from app.marcus.lesson_plan.collateral_spec import (
    SCHEMA_VERSION,
    CollateralSpec,
    DepthDeltaContract,
    Exercise,
    ResearchEnrichmentGoal,
    WorkbookSection,
    WorkbookSpec,
)


def _field_names(model_cls) -> frozenset[str]:
    return frozenset(model_cls.model_fields.keys())


def _required_field_names(model_cls) -> frozenset[str]:
    return frozenset(
        name
        for name, field_info in model_cls.model_fields.items()
        if field_info.is_required()
    )


# --------------------------------------------------------------------------- #
# Field-set allowlists (AC-1 — shape pin)                                      #
# --------------------------------------------------------------------------- #
COLLATERAL_SPEC_EXPECTED_FIELDS = frozenset(
    {"schema_version", "declaration", "workbook", "research_goals"}
)
COLLATERAL_SPEC_REQUIRED_FIELDS = frozenset({"declaration"})

# S7 canonical-arc: additive ``kind`` discriminant on the ARTIFACT (WorkbookSpec).
# Defaulted -> back-compatible -> NOT required (required set stays {"sections"}).
WORKBOOK_SPEC_EXPECTED_FIELDS = frozenset({"sections", "kind"})
WORKBOOK_SPEC_REQUIRED_FIELDS = frozenset({"sections"})

WORKBOOK_SECTION_EXPECTED_FIELDS = frozenset(
    {
        "section_id",
        "learning_objective_id",
        "title",
        "depth_delta",
        "exercises",
        "narrative_intent",
    }
)
WORKBOOK_SECTION_REQUIRED_FIELDS = frozenset(
    {"section_id", "learning_objective_id", "title", "depth_delta"}
)

DEPTH_DELTA_EXPECTED_FIELDS = frozenset(
    {"deferred_from_slide", "deferred_depth", "retained_on_slide"}
)
DEPTH_DELTA_REQUIRED_FIELDS = frozenset({"deferred_from_slide", "deferred_depth"})

EXERCISE_EXPECTED_FIELDS = frozenset(
    {"exercise_id", "bloom_level", "prompt_intent", "answer_key_source_ref"}
)
EXERCISE_REQUIRED_FIELDS = frozenset(
    {"exercise_id", "bloom_level", "prompt_intent", "answer_key_source_ref"}
)

RESEARCH_GOAL_EXPECTED_FIELDS = frozenset(
    {"goal_id", "pedagogical_intent", "binds_to_objective_id"}
)
RESEARCH_GOAL_REQUIRED_FIELDS = frozenset({"goal_id", "pedagogical_intent"})


def test_collateral_spec_field_set_matches_allowlist() -> None:
    assert _field_names(CollateralSpec) == COLLATERAL_SPEC_EXPECTED_FIELDS


def test_collateral_spec_required_fields_match() -> None:
    assert _required_field_names(CollateralSpec) == COLLATERAL_SPEC_REQUIRED_FIELDS


def test_workbook_spec_field_set_matches_allowlist() -> None:
    assert _field_names(WorkbookSpec) == WORKBOOK_SPEC_EXPECTED_FIELDS


def test_workbook_spec_required_fields_match() -> None:
    assert _required_field_names(WorkbookSpec) == WORKBOOK_SPEC_REQUIRED_FIELDS


def test_workbook_section_field_set_matches_allowlist() -> None:
    assert _field_names(WorkbookSection) == WORKBOOK_SECTION_EXPECTED_FIELDS


def test_workbook_section_required_fields_match() -> None:
    assert _required_field_names(WorkbookSection) == WORKBOOK_SECTION_REQUIRED_FIELDS


def test_depth_delta_field_set_matches_allowlist() -> None:
    assert _field_names(DepthDeltaContract) == DEPTH_DELTA_EXPECTED_FIELDS


def test_depth_delta_required_fields_match() -> None:
    assert _required_field_names(DepthDeltaContract) == DEPTH_DELTA_REQUIRED_FIELDS


def test_exercise_field_set_matches_allowlist() -> None:
    assert _field_names(Exercise) == EXERCISE_EXPECTED_FIELDS


def test_exercise_required_fields_match() -> None:
    assert _required_field_names(Exercise) == EXERCISE_REQUIRED_FIELDS


def test_research_goal_field_set_matches_allowlist() -> None:
    assert _field_names(ResearchEnrichmentGoal) == RESEARCH_GOAL_EXPECTED_FIELDS


def test_research_goal_required_fields_match() -> None:
    assert _required_field_names(ResearchEnrichmentGoal) == RESEARCH_GOAL_REQUIRED_FIELDS


def test_schema_version_field_present_and_pinned() -> None:
    assert "schema_version" in CollateralSpec.model_fields
    spec = CollateralSpec(declaration="none")
    assert spec.schema_version == SCHEMA_VERSION


# --------------------------------------------------------------------------- #
# AC-1 — every model carries extra="forbid" + validate_assignment             #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "model_cls",
    [
        CollateralSpec,
        WorkbookSpec,
        WorkbookSection,
        DepthDeltaContract,
        Exercise,
        ResearchEnrichmentGoal,
    ],
)
def test_every_model_forbids_extra_and_validates_assignment(model_cls) -> None:
    assert model_cls.model_config.get("extra") == "forbid"
    assert model_cls.model_config.get("validate_assignment") is True


@pytest.mark.parametrize(
    "model_cls",
    [DepthDeltaContract],
)
def test_value_objects_are_frozen(model_cls) -> None:
    assert model_cls.model_config.get("frozen") is True


def test_collateral_spec_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        CollateralSpec(declaration="none", surprise="x")  # type: ignore[call-arg]


# --------------------------------------------------------------------------- #
# AC-1 — free-text fields carry NO min_length (adversarial-string battery)     #
# --------------------------------------------------------------------------- #
_ADVERSARIAL_STRINGS = ["", " ", "\t", "\r\n", "🙂", "x", "  lead-trail  "]


def _valid_depth_delta(deferred_depth: str) -> DepthDeltaContract:
    return DepthDeltaContract(
        deferred_from_slide="unit-1", deferred_depth=deferred_depth
    )


# deferred_depth is the load-bearing dual-coding field: it rejects whitespace-only
# (same bar as answer_key_source_ref; party-close ruling 2026-06-25) but keeps
# non-whitespace content verbatim (surrounding space preserved).
@pytest.mark.parametrize("text", ["", " ", "\t", "\r\n", "   "])
def test_depth_delta_deferred_depth_rejects_whitespace_only(text: str) -> None:
    with pytest.raises(ValidationError):
        _valid_depth_delta(text)


@pytest.mark.parametrize("text", ["🙂", "x", "  lead-trail  ", "the 23% derivation"])
def test_depth_delta_deferred_depth_keeps_nonwhitespace_verbatim(text: str) -> None:
    contract = _valid_depth_delta(text)
    assert contract.deferred_depth == text


@pytest.mark.parametrize("text", _ADVERSARIAL_STRINGS)
def test_section_narrative_intent_is_verbatim_freetext(text: str) -> None:
    section = WorkbookSection(
        section_id="sec-1",
        learning_objective_id="obj-1",
        title="T",
        depth_delta=_valid_depth_delta("more depth"),
        narrative_intent=text,
    )
    assert section.narrative_intent == text


@pytest.mark.parametrize("text", _ADVERSARIAL_STRINGS)
def test_exercise_prompt_intent_is_verbatim_freetext(text: str) -> None:
    exercise = Exercise(
        exercise_id="ex-1",
        bloom_level="apply",
        prompt_intent=text,
        answer_key_source_ref="src-objective-23pct",
    )
    assert exercise.prompt_intent == text


# --------------------------------------------------------------------------- #
# S7 D5 / AC-5 — WorkbookSpec.kind discriminant (default + closed-enum 3x)     #
# --------------------------------------------------------------------------- #
def _min_section() -> WorkbookSection:
    return WorkbookSection(
        section_id="sec-1",
        learning_objective_id="obj-1",
        title="T",
        depth_delta=DepthDeltaContract(
            deferred_from_slide="unit-1", deferred_depth="the deferred depth"
        ),
    )


def test_kind_defaults_to_deck_companion_workbook() -> None:
    spec = WorkbookSpec(sections=[_min_section()])
    assert spec.kind == "deck-companion-workbook"


def test_kind_absent_key_round_trips_to_default() -> None:
    # Absent 'kind' (back-compat legacy payload) validates to the default.
    spec = WorkbookSpec.model_validate({"sections": [_min_section().model_dump()]})
    assert spec.kind == "deck-companion-workbook"
    # Round-trip: the dumped shape re-validates identically.
    restored = WorkbookSpec.model_validate_json(spec.model_dump_json())
    assert restored.kind == "deck-companion-workbook"


def test_kind_is_not_required() -> None:
    assert "kind" not in _required_field_names(WorkbookSpec)


def test_schema_version_bumped_to_1_1() -> None:
    # D5: the family schema version is bumped on the additive shape drift.
    assert SCHEMA_VERSION == "1.1"


# Closed-enum triple red-rejection (mirror the BloomLevel discipline).
def test_kind_rejects_red_value_on_construction() -> None:
    with pytest.raises(ValidationError):
        WorkbookSpec(sections=[_min_section()], kind="job-aid")  # type: ignore[arg-type]


def test_kind_rejects_red_value_on_assignment() -> None:
    spec = WorkbookSpec(sections=[_min_section()])
    with pytest.raises(ValidationError):
        spec.kind = "drill"  # type: ignore[assignment]


def test_kind_closed_set_in_emitted_json_schema() -> None:
    schema = WorkbookSpec.model_json_schema()
    prop = schema["properties"]["kind"]
    # Single-value Literal emits 'const' (pydantic v2) or a one-item 'enum'.
    allowed = prop.get("enum") or ([prop["const"]] if "const" in prop else None)
    assert allowed == ["deck-companion-workbook"]


def test_kind_type_adapter_round_trip_rejects_red() -> None:
    from typing import Literal

    adapter = TypeAdapter(Literal["deck-companion-workbook"])
    assert adapter.validate_python("deck-companion-workbook") == "deck-companion-workbook"
    with pytest.raises(ValidationError):
        adapter.validate_python("job-aid")


def test_schema_changelog_has_s7_kind_entry() -> None:
    from pathlib import Path

    changelog = (
        Path(__file__).resolve().parents[3]
        / "_bmad-output"
        / "implementation-artifacts"
        / "SCHEMA_CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "CollateralSpec" in changelog and "1.1" in changelog
    assert "kind" in changelog and "deck-companion-workbook" in changelog
