"""Invariant + red-rejection tests for the CollateralSpec family (Braid S1).

Covers AC-2 (objective binding), AC-3 (depth-delta required), AC-4 (exercise
fidelity / Bloom enum), AC-5 (research = intent not query), AC-6 (explicit empty
declaration round-trip). RED-first: written before collateral_spec.py exists.
"""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from app.marcus.lesson_plan.collateral_spec import (
    BloomLevel,
    CollateralSpec,
    DepthDeltaContract,
    Exercise,
    ResearchEnrichmentGoal,
    WorkbookSection,
    WorkbookSpec,
)


def _depth_delta() -> DepthDeltaContract:
    return DepthDeltaContract(
        deferred_from_slide="unit-1",
        deferred_depth="the full derivation of the 23% figure",
    )


def _exercise() -> Exercise:
    return Exercise(
        exercise_id="ex-1",
        bloom_level="apply",
        prompt_intent="learner applies the trend to a new market",
        answer_key_source_ref="src-trends-23pct",
    )


def _section(**overrides) -> WorkbookSection:
    base = {
        "section_id": "sec-1",
        "learning_objective_id": "obj-trends-1",
        "title": "Reading the trend line",
        "depth_delta": _depth_delta(),
        "exercises": [_exercise()],
        "narrative_intent": "fuller narrative on the trend mechanism",
    }
    base.update(overrides)
    return WorkbookSection(**base)


# --------------------------------------------------------------------------- #
# AC-2 — objective-binding invariant (construction AND assignment)            #
# --------------------------------------------------------------------------- #
def test_ac2_section_without_objective_id_rejects_at_construction() -> None:
    with pytest.raises(ValidationError):
        WorkbookSection(
            section_id="sec-1",
            title="T",
            depth_delta=_depth_delta(),
        )  # type: ignore[call-arg]


def test_ac2_section_objective_id_malformed_rejects_at_construction() -> None:
    with pytest.raises(ValidationError):
        _section(learning_objective_id="NOT VALID ID")


def test_ac2_section_objective_id_empty_rejects() -> None:
    with pytest.raises(ValidationError):
        _section(learning_objective_id="")


def test_ac2_section_objective_id_rejects_on_assignment() -> None:
    section = _section()
    with pytest.raises(ValidationError):
        section.learning_objective_id = "BAD ID WITH SPACES"


def test_ac2_section_objective_id_accepts_open_id() -> None:
    section = _section(learning_objective_id="gagne-event-3")
    assert section.learning_objective_id == "gagne-event-3"


# --------------------------------------------------------------------------- #
# AC-3 — depth-delta required + round-trips                                    #
# --------------------------------------------------------------------------- #
def test_ac3_section_without_depth_delta_rejects() -> None:
    with pytest.raises(ValidationError):
        WorkbookSection(
            section_id="sec-1",
            learning_objective_id="obj-1",
            title="T",
        )  # type: ignore[call-arg]


def test_ac3_depth_delta_round_trips_slide_and_depth() -> None:
    contract = DepthDeltaContract(
        deferred_from_slide="unit-7",
        deferred_depth="step-by-step proof",
        retained_on_slide="just the headline number",
    )
    rt = DepthDeltaContract.model_validate_json(contract.model_dump_json())
    assert rt.deferred_from_slide == "unit-7"
    assert rt.deferred_depth == "step-by-step proof"
    assert rt.retained_on_slide == "just the headline number"


def test_ac3_depth_delta_slide_id_must_be_open_id() -> None:
    with pytest.raises(ValidationError):
        DepthDeltaContract(
            deferred_from_slide="NOT VALID", deferred_depth="x"
        )


def test_ac3_depth_delta_retained_on_slide_optional() -> None:
    contract = DepthDeltaContract(deferred_from_slide="u1", deferred_depth="x")
    assert contract.retained_on_slide is None


# --------------------------------------------------------------------------- #
# AC-4 — exercise fidelity (Bloom closed enum, 3 surfaces) + source_ref shape  #
# --------------------------------------------------------------------------- #
_VALID_BLOOM = ["remember", "understand", "apply", "analyze", "evaluate", "create"]


@pytest.mark.parametrize("level", _VALID_BLOOM)
def test_ac4_bloom_accepts_each_valid_level(level: str) -> None:
    ex = Exercise(
        exercise_id="ex-1",
        bloom_level=level,  # type: ignore[arg-type]
        prompt_intent="x",
        answer_key_source_ref="src-1",
    )
    assert ex.bloom_level == level


def test_ac4_bloom_rejects_red_on_direct_construction() -> None:
    with pytest.raises(ValidationError):
        Exercise(
            exercise_id="ex-1",
            bloom_level="synthesize",  # type: ignore[arg-type]
            prompt_intent="x",
            answer_key_source_ref="src-1",
        )


def test_ac4_bloom_rejects_red_on_assignment() -> None:
    ex = _exercise()
    with pytest.raises(ValidationError):
        ex.bloom_level = "synthesize"  # type: ignore[assignment]


def test_ac4_bloom_json_schema_enumerates_the_six_levels() -> None:
    schema = Exercise.model_json_schema()
    # BloomLevel is a Literal; its enum lands inline or in $defs.
    found_enum = None
    if "properties" in schema and "bloom_level" in schema["properties"]:
        prop = schema["properties"]["bloom_level"]
        if "enum" in prop:
            found_enum = prop["enum"]
        elif "$ref" in prop:
            ref_name = prop["$ref"].rsplit("/", 1)[-1]
            found_enum = schema["$defs"][ref_name]["enum"]
    assert found_enum is not None
    assert set(found_enum) == set(_VALID_BLOOM)


def test_ac4_bloom_type_adapter_round_trip_rejects_red() -> None:
    adapter = TypeAdapter(BloomLevel)
    for level in _VALID_BLOOM:
        assert adapter.validate_python(level) == level
    with pytest.raises(ValidationError):
        adapter.validate_python("synthesize")


def test_ac4_answer_key_source_ref_required() -> None:
    with pytest.raises(ValidationError):
        Exercise(
            exercise_id="ex-1",
            bloom_level="apply",
            prompt_intent="x",
        )  # type: ignore[call-arg]


def test_ac4_answer_key_source_ref_malformed_rejects() -> None:
    # source_ref shape: non-empty open-id reference; whitespace-only is malformed.
    with pytest.raises(ValidationError):
        Exercise(
            exercise_id="ex-1",
            bloom_level="apply",
            prompt_intent="x",
            answer_key_source_ref="   ",
        )


def test_ac4_answer_key_source_ref_empty_rejects() -> None:
    with pytest.raises(ValidationError):
        Exercise(
            exercise_id="ex-1",
            bloom_level="apply",
            prompt_intent="x",
            answer_key_source_ref="",
        )


# --------------------------------------------------------------------------- #
# AC-5 — research = pedagogical intent, NOT a fetch query                      #
# --------------------------------------------------------------------------- #
def test_ac5_pedagogical_intent_accepted() -> None:
    goal = ResearchEnrichmentGoal(
        goal_id="rg-1",
        pedagogical_intent=(
            "learner needs the primary-source basis for the 23% figure"
        ),
    )
    assert "primary-source" in goal.pedagogical_intent


def test_ac5_raw_url_query_rejected() -> None:
    with pytest.raises(ValidationError):
        ResearchEnrichmentGoal(
            goal_id="rg-1",
            pedagogical_intent="https://scholar.google.com/scholar?q=23%25+trend",
        )


def test_ac5_boolean_operator_query_rejected() -> None:
    with pytest.raises(ValidationError):
        ResearchEnrichmentGoal(
            goal_id="rg-1",
            pedagogical_intent='"market trend" AND (2024 OR 2025) NOT crypto',
        )


def test_ac5_near_boundary_intent_accepted_false_positive_averse() -> None:
    # Mentions a topic that *could* be searched, phrased as pedagogical intent.
    # Conservative heuristic must NOT reject this (false-positive-averse).
    goal = ResearchEnrichmentGoal(
        goal_id="rg-1",
        pedagogical_intent=(
            "learners should understand how the 2024 market trend data was "
            "collected before they trust the 23% claim"
        ),
    )
    assert goal.goal_id == "rg-1"


def test_ac5_binds_to_objective_id_optional_open_id() -> None:
    goal = ResearchEnrichmentGoal(
        goal_id="rg-1",
        pedagogical_intent="learner needs the source",
        binds_to_objective_id="obj-trends-1",
    )
    assert goal.binds_to_objective_id == "obj-trends-1"
    with pytest.raises(ValidationError):
        ResearchEnrichmentGoal(
            goal_id="rg-1",
            pedagogical_intent="learner needs the source",
            binds_to_objective_id="BAD ID",
        )


# Characterization (party-close 2026-06-25, Murat item-3): pin the CURRENT
# false-positive-averse v1 heuristic so its known imprecision is a recorded
# baseline, not an invisible permanent floor. These raw-query-ish shapes are
# ACCEPTED today (scheme-less domain, site:/filetype: operators, a bare quoted
# phrase) because the v1 heuristic only rejects a URL scheme or boolean-soup.
# Tightening is deferred to S3 (the real research boundary) — see
# deferred-inventory `braid-research-query-heuristic-tightening`. If S3 changes
# this, update this baseline deliberately.
@pytest.mark.parametrize(
    "lenient_text",
    [
        "google.com/search?q=market+trends",  # scheme-less domain
        "site:nasa.gov climate data",  # search operator
        "filetype:pdf 2024 market report",  # search operator
        '"market trend"',  # bare quoted phrase, no boolean op
    ],
)
def test_ac5_known_lenient_v1_heuristic_baseline(lenient_text: str) -> None:
    # ACCEPTED today (documented imprecision; S3 owns tightening).
    goal = ResearchEnrichmentGoal(goal_id="rg-1", pedagogical_intent=lenient_text)
    assert goal.pedagogical_intent == lenient_text


# --------------------------------------------------------------------------- #
# AC-6 — explicit empty declaration round-trip + discriminant invariant       #
# --------------------------------------------------------------------------- #
def test_ac6_none_declaration_constructs_with_null_workbook() -> None:
    spec = CollateralSpec(declaration="none")
    assert spec.workbook is None
    assert spec.research_goals == []


def test_ac6_none_declaration_round_trips_byte_faithfully() -> None:
    spec = CollateralSpec(declaration="none")
    dumped = spec.model_dump_json()
    restored = CollateralSpec.model_validate_json(dumped)
    assert restored.model_dump_json() == dumped


def test_ac6_present_with_null_workbook_rejects() -> None:
    with pytest.raises(ValidationError):
        CollateralSpec(declaration="present", workbook=None)


def test_ac6_present_with_zero_sections_rejects() -> None:
    with pytest.raises(ValidationError):
        CollateralSpec(
            declaration="present", workbook=WorkbookSpec(sections=[])
        )


def test_ac6_none_with_non_null_workbook_rejects() -> None:
    section = _section()
    with pytest.raises(ValidationError):
        CollateralSpec(
            declaration="none", workbook=WorkbookSpec(sections=[section])
        )


def test_ac6_present_with_section_constructs_and_round_trips() -> None:
    spec = CollateralSpec(
        declaration="present",
        workbook=WorkbookSpec(sections=[_section()]),
        research_goals=[
            ResearchEnrichmentGoal(
                goal_id="rg-1",
                pedagogical_intent="learner needs the source for 23%",
            )
        ],
    )
    dumped = spec.model_dump_json()
    restored = CollateralSpec.model_validate_json(dumped)
    assert restored.model_dump_json() == dumped
    assert restored.workbook is not None
    assert restored.workbook.sections[0].learning_objective_id == "obj-trends-1"


def test_ac6_present_allows_empty_research_goals() -> None:
    spec = CollateralSpec(
        declaration="present",
        workbook=WorkbookSpec(sections=[_section()]),
    )
    assert spec.research_goals == []


def test_ac6_discriminant_enforced_on_assignment() -> None:
    spec = CollateralSpec(declaration="none")
    with pytest.raises(ValidationError):
        spec.declaration = "present"
