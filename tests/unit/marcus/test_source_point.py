"""T3 — SourcePoint coverage models (offline; Story concierge-coverage-assurance-interlock).

RED-first behavioural specs for the child-id identity (AC1), assertion unit (AC2),
intent-as-set (AC3), and the risk taxonomy → deterministic verbatim floor (AC5).
NO live LLM/network. Code-enforces the three binding caveats (child-id-never-a-
join-key; deliberately_excluded operator-signed; segmentation stamp present).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.source_point import (
    COVERAGE_INTENTS,
    RISK_FLAGS,
    SEGMENTATION_GRAINS,
    VERBATIM_REQUIRED_RISK_FLOOR,
    SourcePoint,
    assert_join_key,
    derive_coverage_intents,
    join_key,
    load_source_point,
    make_source_point_id,
    ordinal_of,
    parent_component_id_of,
    source_point_json_schema,
    verbatim_required_for,
)


def _sp(**overrides):
    base = dict(
        source_point_id="src-001-c003#1",
        component_id="src-001-c003",
        ordinal=1,
        slide_key="Slide 1",
        verbatim_text="U.S. healthcare spending reached $5.2 trillion in 2024.",
        risk_flags=("numeric",),
        coverage_intents=("gist_on_slide",),
        segmentation="assertion_level",
    )
    base.update(overrides)
    return SourcePoint(**base)


# --------------------------------------------------------------------------- #
# AC1 — child id rides the existing component_id space; NEVER a join key
# --------------------------------------------------------------------------- #


def test_child_id_is_component_id_hash_ordinal() -> None:
    assert make_source_point_id("src-001-c003", 2) == "src-001-c003#2"
    assert parent_component_id_of("src-001-c003#2") == "src-001-c003"
    assert ordinal_of("src-001-c003#2") == 2


def test_make_id_rejects_hash_in_component_id() -> None:
    with pytest.raises(ValueError, match="contain no '#'"):
        make_source_point_id("src-001#9", 1)


def test_source_point_id_must_equal_parent_hash_ordinal() -> None:
    with pytest.raises(ValidationError, match="child-id identity"):
        _sp(source_point_id="src-001-c003#9")  # ordinal mismatch


def test_join_key_returns_parent_never_child() -> None:
    point = _sp()
    assert join_key(point) == "src-001-c003"
    assert point.parent_join_key() == "src-001-c003"
    # the child id is NOT the join key
    assert join_key(point) != point.source_point_id


def test_assert_join_key_refuses_child_id() -> None:
    # a parent id passes through
    assert assert_join_key("src-001-c003") == "src-001-c003"
    # a child #ordinal id is refused (Winston caveat)
    with pytest.raises(ValueError, match="CHILD id"):
        assert_join_key("src-001-c003#1")


# --------------------------------------------------------------------------- #
# AC2 — assertion unit + load-bearing segmentation stamp
# --------------------------------------------------------------------------- #


def test_segmentation_stamp_is_required_and_closed() -> None:
    assert {"assertion_level", "block_level_v1"} == SEGMENTATION_GRAINS
    with pytest.raises(ValidationError):
        _sp(segmentation="paragraph_level")  # not a member


def test_round_trip_load_preserves_and_revalidates() -> None:
    point = _sp(risk_flags=("numeric", "comparator"))
    reloaded = load_source_point(point.model_dump(mode="json"))
    assert reloaded == point
    schema = source_point_json_schema()
    assert "coverage_intents" in schema["properties"]


# --------------------------------------------------------------------------- #
# AC3 — coverage intent is a non-empty SET; deliberately_excluded operator-signed
# --------------------------------------------------------------------------- #


def test_coverage_intents_nonempty_unique_sorted() -> None:
    assert {"gist_on_slide", "detail_in_narration", "deliberately_excluded"} == COVERAGE_INTENTS
    point = _sp(coverage_intents=("detail_in_narration", "gist_on_slide", "gist_on_slide"))
    # deduped + sorted (set semantics, stable serialization)
    assert point.coverage_intents == ("detail_in_narration", "gist_on_slide")


def test_empty_intent_set_rejected() -> None:
    with pytest.raises(ValidationError, match="NON-EMPTY"):
        _sp(coverage_intents=())


def test_deliberately_excluded_requires_operator_signature() -> None:
    with pytest.raises(ValidationError, match="operator_signed_exclusion"):
        _sp(coverage_intents=("deliberately_excluded",), operator_signed_exclusion=False)
    # signed → accepted
    point = _sp(coverage_intents=("deliberately_excluded",), operator_signed_exclusion=True)
    assert "deliberately_excluded" in point.coverage_intents


def test_derive_intents_default_slide_gist_narration_detail() -> None:
    assert derive_coverage_intents(
        source_type="slide", pedagogical_role="definition",
        lo_load_bearing=False, risk_flags=(),
    ) == ("gist_on_slide",)
    assert derive_coverage_intents(
        source_type="narration", pedagogical_role="motivation",
        lo_load_bearing=False, risk_flags=(),
    ) == ("detail_in_narration",)


def test_derive_intents_forces_both_on_lo_or_safety_or_organizing() -> None:
    both = ("detail_in_narration", "gist_on_slide")
    assert derive_coverage_intents(
        source_type="slide", pedagogical_role="definition",
        lo_load_bearing=True, risk_flags=(),
    ) == both
    assert derive_coverage_intents(
        source_type="slide", pedagogical_role="definition",
        lo_load_bearing=False, risk_flags=("clinical_claim",),
    ) == both
    assert derive_coverage_intents(
        source_type="narration", pedagogical_role="motivation",
        lo_load_bearing=False, risk_flags=("negation",),
    ) == both
    assert derive_coverage_intents(
        source_type="slide", pedagogical_role="definition",
        lo_load_bearing=False, risk_flags=(), is_organizing_claim=True,
    ) == both


def test_derive_intents_never_auto_excludes() -> None:
    for kwargs in (
        dict(source_type="slide", pedagogical_role="x", lo_load_bearing=True, risk_flags=()),
        dict(source_type="narration", pedagogical_role="x", lo_load_bearing=False,
             risk_flags=("clinical_claim", "negation")),
    ):
        assert "deliberately_excluded" not in derive_coverage_intents(**kwargs)


# --------------------------------------------------------------------------- #
# AC5 — risk taxonomy drives a DETERMINISTIC verbatim floor (not downgradable)
# --------------------------------------------------------------------------- #


def test_risk_taxonomy_closed_and_floor_partition() -> None:
    assert {
        "clinical_claim", "numeric", "dosing", "negation", "comparator", "exemplary_language",
    } == RISK_FLAGS
    # exemplary_language is the ONLY non-floor member
    assert {"exemplary_language"} == RISK_FLAGS - VERBATIM_REQUIRED_RISK_FLOOR


@pytest.mark.parametrize(
    "flags,expected",
    [
        ((), False),
        (("exemplary_language",), False),
        (("numeric",), True),
        (("dosing",), True),
        (("negation",), True),
        (("comparator",), True),
        (("clinical_claim",), True),
        (("exemplary_language", "numeric"), True),
    ],
)
def test_verbatim_required_floor_is_deterministic(flags, expected) -> None:
    assert verbatim_required_for(flags) is expected


def test_verbatim_required_field_is_derived_not_trusted() -> None:
    # a caller forcing verbatim_required=False on a numeric point cannot downgrade it
    point = _sp(risk_flags=("numeric",), verbatim_required=False)
    assert point.verbatim_required is True
    # a caller forcing True on a non-floor point is corrected to False
    point2 = _sp(risk_flags=("exemplary_language",), verbatim_required=True)
    assert point2.verbatim_required is False


def test_unknown_risk_flag_rejected_three_surfaces() -> None:
    with pytest.raises(ValidationError):
        _sp(risk_flags=("toxic",))
