"""Adapter-function tests (Story G0-S1 AC-S1-5 / AC-S1-7). RED-first.

The adapters are the back-compat bridge over the legacy reps; round-trips must
preserve the subset fields, and the produce_tejal_workbook.py swap must be
behavior-identical (the resulting LearningObjectiveBrief tuple is unchanged).
"""

from __future__ import annotations

import pytest

from app.marcus.lesson_plan.collateral_spec import (
    DepthDeltaContract,
    WorkbookSection,
)
from app.marcus.lesson_plan.learning_objective import (
    LearningObjective,
    SourceRef,
)
from app.marcus.lesson_plan.learning_objective_adapters import (
    from_irene_statement,
    from_workbook_brief,
    section_binds_objective,
    to_workbook_brief,
)
from app.marcus.lesson_plan.workbook_producer import LearningObjectiveBrief


# --------------------------------------------------------------------------- #
# from_irene_statement                                                        #
# --------------------------------------------------------------------------- #
def test_from_irene_statement_lifts_to_provisional() -> None:
    lo = from_irene_statement("Analyze the trends", objective_id="obj-lo2")
    assert isinstance(lo, LearningObjective)
    assert lo.status == "provisional"
    assert lo.statement == "Analyze the trends"
    assert lo.objective_id == "obj-lo2"
    assert lo.source_refs == ()
    assert lo.adequacy is None
    assert lo.bloom_level is None


def test_from_irene_statement_carries_optional_source_refs_and_bloom() -> None:
    refs = [SourceRef(source_id="s1", locator="p1", quoted_span="span")]
    lo = from_irene_statement(
        "Analyze the trends",
        objective_id="obj-lo2",
        source_refs=refs,
        bloom_level="analyze",
    )
    assert lo.source_refs == tuple(refs)
    assert lo.bloom_level == "analyze"
    # still provisional (Irene cannot self-promote)
    assert lo.status == "provisional"


def test_from_irene_statement_rejects_malformed_objective_id() -> None:
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        from_irene_statement("s", objective_id="NOT VALID ID")


# --------------------------------------------------------------------------- #
# from_workbook_brief / to_workbook_brief round-trip                          #
# --------------------------------------------------------------------------- #
_BRIEFS = [
    LearningObjectiveBrief("obj-lo2-analyze-trends", "analyze", "Analyze the macro trends."),
    LearningObjectiveBrief("obj-lo4-root-cause", "evaluate", "Evaluate operational failures."),
    LearningObjectiveBrief("obj-1", "remember", ""),  # empty statement is verbatim-ok
]


@pytest.mark.parametrize("brief", _BRIEFS)
def test_workbook_brief_round_trip_is_identity_on_subset(brief: LearningObjectiveBrief) -> None:
    assert to_workbook_brief(from_workbook_brief(brief)) == brief


def test_from_workbook_brief_produces_provisional_lo() -> None:
    lo = from_workbook_brief(_BRIEFS[0])
    assert lo.status == "provisional"
    assert lo.bloom_level == "analyze"


# T11 back-compat: LearningObjectiveBrief.bloom_level is a bare str; the canonical
# entity uses the closed BloomLevel enum. Case variance must coerce; genuinely
# non-Bloom data must fail LOUD with a clear message (not a cryptic error / silent
# drop); empty/blank bloom maps to None (optional at provisional).
@pytest.mark.parametrize("raw_bloom", ["Analyze", "ANALYZE", " analyze ", "AnAlYzE"])
def test_from_workbook_brief_coerces_bloom_case(raw_bloom: str) -> None:
    lo = from_workbook_brief(LearningObjectiveBrief("obj-c", raw_bloom, "Stmt."))
    assert lo.bloom_level == "analyze"


@pytest.mark.parametrize("blank", ["", "   "])
def test_from_workbook_brief_blank_bloom_maps_to_none(blank: str) -> None:
    lo = from_workbook_brief(LearningObjectiveBrief("obj-c", blank, "Stmt."))
    assert lo.bloom_level is None


def test_from_workbook_brief_invalid_bloom_fails_loud() -> None:
    # "synthesize" is not one of the six revised-Bloom levels: bad legacy data,
    # surfaced loudly rather than silently coerced.
    with pytest.raises(ValueError, match="not a canonical Bloom level"):
        from_workbook_brief(LearningObjectiveBrief("obj-c", "synthesize", "Stmt."))


def test_to_workbook_brief_requires_bloom_level() -> None:
    lo = from_irene_statement("s", objective_id="obj-1")  # bloom None
    with pytest.raises(ValueError, match="bloom_level"):
        to_workbook_brief(lo)


def test_to_workbook_brief_projects_three_fields() -> None:
    lo = LearningObjective(
        objective_id="obj-x",
        statement="Differentiate idea from opportunity.",
        status="provisional",
        confidence="medium",
        bloom_level="analyze",
    )
    brief = to_workbook_brief(lo)
    assert brief == LearningObjectiveBrief(
        "obj-x", "analyze", "Differentiate idea from opportunity."
    )


# --------------------------------------------------------------------------- #
# binding helper                                                              #
# --------------------------------------------------------------------------- #
def test_section_binds_objective_matches_open_id() -> None:
    section = WorkbookSection(
        section_id="sec-1",
        learning_objective_id="obj-lo2-analyze-trends",
        title="T",
        depth_delta=DepthDeltaContract(
            deferred_from_slide="unit-1", deferred_depth="more"
        ),
    )
    lo = from_irene_statement("Analyze", objective_id="obj-lo2-analyze-trends")
    other = from_irene_statement("Other", objective_id="obj-other")
    assert section_binds_objective(section, lo) is True
    assert section_binds_objective(section, other) is False


# --------------------------------------------------------------------------- #
# AC-S1-7 — produce_tejal_workbook.py swap is behavior-identical              #
# --------------------------------------------------------------------------- #
# Import the REAL seeds the script uses (TEJAL_OBJECTIVE_SEEDS, hoisted to module
# scope) so this test guards against drift instead of re-declaring a copy. The
# inline ``LearningObjectiveBrief(id, bloom, statement)`` construction the script
# USED to do must equal the adapter chain it does NOW over the same seeds.
from scripts.utilities.produce_tejal_workbook import (  # noqa: E402
    TEJAL_OBJECTIVE_SEEDS,
)


def test_tejal_inline_swap_is_behavior_identical() -> None:
    legacy = tuple(
        LearningObjectiveBrief(oid, bloom, statement)
        for oid, bloom, statement in TEJAL_OBJECTIVE_SEEDS
    )
    swapped = tuple(
        to_workbook_brief(
            from_irene_statement(statement, objective_id=oid, bloom_level=bloom)  # type: ignore[arg-type]
        )
        for oid, bloom, statement in TEJAL_OBJECTIVE_SEEDS
    )
    assert swapped == legacy
