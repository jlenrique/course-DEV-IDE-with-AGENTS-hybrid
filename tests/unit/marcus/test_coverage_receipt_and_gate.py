"""T5 + T6 — derived coverage receipt (two axes + vouch) and the fail-loud gate.

KEYSTONE: a source_point coverage receipt + the deterministic fail-loud gate. All
OFFLINE — the joins are projected from in-memory anchors (the dispatch-site
projection pattern), no producer self-report, no live LLM. R7 is exercised as the
REPORTING caller.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.coverage_annotation import CoverageAnnotation
from app.marcus.lesson_plan.coverage_gate import (
    CoverageAssuranceError,
    assert_coverage_gate,
    coverage_warnings,
    evaluate_coverage_gate,
)
from app.marcus.lesson_plan.coverage_receipt import (
    CONTAINMENT_VERDICTS,
    COVERAGE_STATUSES,
    VOUCH_LEVELS,
    AnchorResolution,
    CoverageReceipt,
    CoverageReceiptRow,
    derive_coverage_receipt,
    load_coverage_receipt,
)
from app.marcus.lesson_plan.source_point import SourcePoint

_TS = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)


def _point(
    ordinal: int,
    text: str,
    *,
    component_id: str = "src-001-c001",
    slide_key: str = "Slide 1",
    risk_flags=(),
    intents=("gist_on_slide",),
    operator_signed: bool = False,
) -> SourcePoint:
    return SourcePoint(
        source_point_id=f"{component_id}#{ordinal}",
        component_id=component_id,
        ordinal=ordinal,
        slide_key=slide_key,
        verbatim_text=text,
        risk_flags=risk_flags,
        coverage_intents=intents,
        segmentation="assertion_level",
        operator_signed_exclusion=operator_signed,
    )


def _ann(points) -> CoverageAnnotation:
    return CoverageAnnotation(
        component_id=points[0].component_id,
        slide_key=points[0].slide_key,
        source_points=tuple(points),
        segmentation="assertion_level",
        generated_at=_TS,
    )


# --------------------------------------------------------------------------- #
# Closed enums
# --------------------------------------------------------------------------- #


def test_closed_enums() -> None:
    assert {
        "covered_on_slide", "covered_in_narration", "both", "deliberately_excluded", "missing",
    } == COVERAGE_STATUSES
    assert {"verbatim_preserved", "altered", "risky"} == CONTAINMENT_VERDICTS
    assert {"verified", "advisory_caveat", "not_assessed"} == VOUCH_LEVELS


# --------------------------------------------------------------------------- #
# AC7 — deterministic anchor FIRST: no anchor → forced missing
# --------------------------------------------------------------------------- #


def test_no_anchor_forces_missing() -> None:
    pt = _point(1, "U.S. spending reached $5.2 trillion in 2024.", risk_flags=("numeric",))
    receipt = derive_coverage_receipt([_ann([pt])], anchors={}, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "missing"
    assert row.anchor_resolved is False
    assert row.containment_verdict is None
    assert row.vouch_level == "not_assessed"


# --------------------------------------------------------------------------- #
# AC4/AC6 — covered_on_slide with deterministic verified vouch
# --------------------------------------------------------------------------- #


def test_covered_on_slide_verbatim_verified() -> None:
    span = "U.S. spending reached $5.2 trillion in 2024."
    pt = _point(1, span, risk_flags=("numeric",))
    anchors = {
        "Slide 1": AnchorResolution(slide_key="Slide 1", slide_present=True, slide_text=span)
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_on_slide"
    assert row.containment_verdict == "verbatim_preserved"
    assert row.vouch_level == "verified"  # numeric + deterministic span match
    assert row.verbatim_required is True


def test_covered_in_narration_status() -> None:
    span = "You must navigate a large enterprise."
    pt = _point(1, span, intents=("detail_in_narration",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=True, slide_text="something else entirely",
            narration_present=True, narration_text=span,
        )
    }
    row = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS).rows[0]
    assert row.coverage_status == "covered_in_narration"


def test_both_surfaces() -> None:
    span = "Burnout is a system problem."
    pt = _point(1, span, intents=("detail_in_narration", "gist_on_slide"))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=True, slide_text=span,
            narration_present=True, narration_text=span,
        )
    }
    row = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS).rows[0]
    assert row.coverage_status == "both"


# --------------------------------------------------------------------------- #
# AC6 — negation/comparator never a green vouch (disclosed bag-of-words FN)
# --------------------------------------------------------------------------- #


def test_negation_point_is_advisory_not_verified() -> None:
    span = "This is not a personal failing."
    pt = _point(1, span, risk_flags=("negation",))
    anchors = {
        "Slide 1": AnchorResolution(slide_key="Slide 1", slide_present=True, slide_text=span)
    }
    row = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS).rows[0]
    assert row.verbatim_required is True
    assert row.vouch_level == "advisory_caveat"  # NEVER verified for negation
    assert row.containment_verdict == "verbatim_preserved"


# --------------------------------------------------------------------------- #
# AC9 — the :335 silent role-seed drop becomes a logged missing
# --------------------------------------------------------------------------- #


def test_ambiguous_narration_drop_logged_missing(caplog) -> None:
    span = "Detail only spoken aloud."
    pt = _point(1, span, intents=("detail_in_narration",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=False,
            narration_present=True, narration_ambiguous=True, narration_text=span,
        )
    }
    with caplog.at_level("WARNING"):
        row = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS).rows[0]
    # narration is ambiguous (0/>1 match) and no slide → missing, logged
    assert row.coverage_status == "missing"
    assert any("ambiguous" in m for m in caplog.messages)


# --------------------------------------------------------------------------- #
# Render-time vouch gate (Vera caveat) — model rejects illegal cells
# --------------------------------------------------------------------------- #


def _row(**over):
    base = dict(
        source_point_id="src-001-c001#1", component_id="src-001-c001", slide_key="Slide 1",
        human_label="Slide 1 / note", intent_set=("gist_on_slide",), risk_flags=("numeric",),
        verbatim_required=True, coverage_status="covered_on_slide",
        containment_verdict="verbatim_preserved", vouch_level="verified", anchor_resolved=True,
        must_cover=True, segmentation="assertion_level",
    )
    base.update(over)
    return CoverageReceiptRow(**base)


def test_missing_row_cannot_carry_containment() -> None:
    with pytest.raises(ValidationError, match="coverage hole"):
        _row(coverage_status="missing", containment_verdict="verbatim_preserved",
             vouch_level="not_assessed")


def test_verified_requires_verbatim_required() -> None:
    with pytest.raises(ValidationError, match="reserved for deterministic"):
        _row(verbatim_required=False, risk_flags=())


def test_verified_rejected_for_negation_risk() -> None:
    with pytest.raises(ValidationError, match="negation/comparator"):
        _row(risk_flags=("negation",))


def test_containment_requires_resolved_anchor() -> None:
    with pytest.raises(ValidationError, match="resolved\\s+anchor|NO resolved"):
        _row(anchor_resolved=False)


def test_receipt_declares_grain_and_rejects_mismatch() -> None:
    row = _row()
    with pytest.raises(ValidationError, match="never dropped"):
        CoverageReceipt(segmentation="block_level_v1", rows=(row,), generated_at=_TS)


# --------------------------------------------------------------------------- #
# T6 — the fail-loud gate (keystone)
# --------------------------------------------------------------------------- #


def test_gate_blocks_must_cover_uncovered_no_surface() -> None:
    # a must-cover (numeric → verbatim_required) point with NO anchor at all
    pt = _point(1, "Dose is 5 mg daily.", risk_flags=("numeric", "dosing"),
                intents=("detail_in_narration",))
    receipt = derive_coverage_receipt([_ann([pt])], anchors={}, generated_at=_TS)
    blocking = evaluate_coverage_gate(receipt)
    assert len(blocking) == 1
    with pytest.raises(CoverageAssuranceError) as exc:
        assert_coverage_gate(receipt)
    assert exc.value.tag == "marcus.coverage.must-cover-uncovered"
    assert exc.value.blocking_rows[0].source_point_id == "src-001-c001#1"


def test_gate_passes_when_covered() -> None:
    span = "Dose is 5 mg daily."
    pt = _point(1, span, risk_flags=("numeric", "dosing"), intents=("detail_in_narration",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=False,
            narration_present=True, narration_text=span,
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    assert evaluate_coverage_gate(receipt) == ()
    assert assert_coverage_gate(receipt) is None  # clear


def test_gate_does_not_block_deliberately_excluded() -> None:
    pt = _point(1, "Optional aside, 3 examples.", risk_flags=("numeric",),
                intents=("deliberately_excluded",), operator_signed=True)
    receipt = derive_coverage_receipt([_ann([pt])], anchors={}, generated_at=_TS)
    assert evaluate_coverage_gate(receipt) == ()


def test_gate_verbatim_absent_blocks_even_with_slide_present_but_no_planned_surface() -> None:
    # verbatim_required span not present on the only (slide) surface, intent is
    # detail_in_narration (so the slide is not a planned surface for it) and no
    # narration surface → must_cover ∧ verbatim_absent ∧ no_planned_surface.
    pt = _point(1, "Exactly 5.2 trillion dollars.", risk_flags=("numeric",),
                intents=("detail_in_narration",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=False,
            narration_present=False,
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    assert len(evaluate_coverage_gate(receipt)) == 1


def test_fix1_verbatim_absent_blocks_even_with_planned_slide_surface() -> None:
    # FIX 1: a must-cover, verbatim-required point whose span is DROPPED off a
    # rendered slide (slide surface present, span absent) with NO narration must
    # BLOCK — verbatim_absent is an INDEPENDENT blocking condition, not gated behind
    # no_planned_surface (the dead-term fail-open). intent=detail_in_narration so the
    # slide is not a planned surface for the obligation, but a slide DOES render.
    span = "Exactly 5.2 trillion dollars."
    pt = _point(1, span, risk_flags=("numeric",), intents=("detail_in_narration",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=True, slide_text="a different figure entirely",
            narration_present=False,
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.verbatim_absent is True
    assert row.planned_on_slide is True  # a slide DID render (the dead-term trap)
    # money-on-the-line: span lost off the rendered slide, no narration → BLOCK
    assert len(evaluate_coverage_gate(receipt)) == 1
    with pytest.raises(CoverageAssuranceError):
        assert_coverage_gate(receipt)


def test_fix2_detail_in_narration_covered_only_on_slide_blocks() -> None:
    # FIX 2: a must-cover point carrying a detail_in_narration intent that is covered
    # ONLY on the slide (its span renders on the slide but never reaches the
    # narration) has an UNMET narration obligation → must be treated as uncovered for
    # its intent → BLOCK. Non-verbatim so verbatim_absent is NOT the trigger (isolate
    # the narration-obligation term).
    span = "You must navigate a large enterprise."
    pt = _point(1, span, risk_flags=(), intents=("detail_in_narration",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=True, slide_text=span,
            narration_present=False,
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_on_slide"
    assert row.must_cover is True  # detail_in_narration → must_cover
    assert row.narration_obligation_unmet is True
    assert row.verbatim_absent is False  # isolate: the trigger is the narration miss
    assert len(evaluate_coverage_gate(receipt)) == 1
    with pytest.raises(CoverageAssuranceError):
        assert_coverage_gate(receipt)


def test_warnings_are_ledger_only_not_blocking() -> None:
    # A genuinely FUZZY verdict: a non-verbatim, non-must-cover point COVERED on the
    # slide, but R7 flags an unsourced comparator the surface introduces → 'risky'.
    # This is WARN / ledger-only (no deterministic, money-on-the-line failure), and
    # the fuzzy WARN routing must stay intact after FIX 1 / FIX 2 tightened the gate.
    span = "burnout is a problem"
    pt = _point(1, span, risk_flags=(), intents=("gist_on_slide",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1", slide_present=True,
            slide_text="burnout is a problem and rates increased dramatically",
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_on_slide"
    assert row.containment_verdict == "risky"  # R7 unsourced comparator → fuzzy
    assert row.must_cover is False
    # fuzzy verdict, not money-on-the-line → not blocking, but a WARN
    assert evaluate_coverage_gate(receipt) == ()
    assert len(coverage_warnings(receipt)) >= 1


def test_receipt_round_trip_load() -> None:
    span = "Burnout is a system problem."
    pt = _point(1, span, intents=("gist_on_slide",))
    anchors = {
        "Slide 1": AnchorResolution(slide_key="Slide 1", slide_present=True, slide_text=span)
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    assert load_coverage_receipt(receipt.model_dump(mode="json")) == receipt
