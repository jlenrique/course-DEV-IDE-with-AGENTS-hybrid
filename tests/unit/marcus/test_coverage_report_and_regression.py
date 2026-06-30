"""T7 + T9 — coverage report render, plan view, and the additive regression firewall.

Storyboard-B coverage section render (AC10), the G0E plan view (AC10), and the
byte-identical additive firewall on G0EnrichmentResult (AC11). OFFLINE only.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.gates.section_07c.storyboard_html_emitter import render_coverage_section
from app.marcus.lesson_plan.coverage_annotation import CoverageAnnotation
from app.marcus.lesson_plan.coverage_receipt import (
    AnchorResolution,
    coverage_plan_view,
    derive_coverage_receipt,
)
from app.marcus.lesson_plan.g0_enrichment import (
    Dissent,
    G0EnrichmentResult,
    IndependentParse,
    ReconcileView,
)
from app.marcus.lesson_plan.source_point import SourcePoint

_TS = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)


def _point(
    text="Spending reached $5.2 trillion in 2024.",
    intents=("gist_on_slide",),
    risk=("numeric",),
):
    return SourcePoint(
        source_point_id="src-001-c001#1", component_id="src-001-c001", ordinal=1,
        slide_key="Slide 1", verbatim_text=text, risk_flags=risk,
        coverage_intents=intents, segmentation="assertion_level",
    )


def _ann(pt):
    return CoverageAnnotation(
        component_id="src-001-c001", slide_key="Slide 1", source_points=(pt,),
        segmentation="assertion_level", generated_at=_TS,
    )


def _result(**over) -> G0EnrichmentResult:
    base = dict(
        corpus_fingerprint="fp-test",
        model_id="offline",
        typed_components=[],
        provisional_los=[],
        reconcile=ReconcileView(
            n_files_in=1, n_files_covered=1, n_files_ignored=0, n_components=1, n_flagged=0
        ),
        dissents=[Dissent(against="src-001", marcus_position="x")],
        independent_parse=IndependentParse(proposal={}, ts=_TS),
    )
    base.update(over)
    return G0EnrichmentResult(**base)


# --------------------------------------------------------------------------- #
# T7 — render + plan view
# --------------------------------------------------------------------------- #


def test_render_coverage_section_declares_grain_and_columns() -> None:
    span = "Spending reached $5.2 trillion in 2024."
    receipt = derive_coverage_receipt(
        [_ann(_point(span))],
        anchors={
            "Slide 1": AnchorResolution(slide_key="Slide 1", slide_present=True, slide_text=span)
        },
        generated_at=_TS,
    )
    html = render_coverage_section(receipt.model_dump(mode="json"))
    assert "Segmentation grain: <strong>assertion_level</strong>" in html  # Irene caveat
    assert "src-001-c001#1" in html
    assert "covered_on_slide" in html
    assert "verbatim_preserved" in html
    assert "verified" in html


def test_render_coverage_section_empty_is_byte_identical_noop() -> None:
    assert render_coverage_section({}) == ""
    assert render_coverage_section(None) == ""  # type: ignore[arg-type]


def test_coverage_plan_view_declares_grain_and_must_cover() -> None:
    plan = coverage_plan_view([_ann(_point(intents=("detail_in_narration",)))])
    assert plan["segmentation"] == "assertion_level"
    assert plan["n_points"] == 1
    pt = plan["points"][0]
    assert pt["source_point_id"] == "src-001-c001#1"
    assert pt["must_cover"] is True  # verbatim_required (numeric) + detail_in_narration


# --------------------------------------------------------------------------- #
# T9 — additive firewall: flag-OFF card is byte-identical (coverage layer omitted)
# --------------------------------------------------------------------------- #


def test_card_payload_omits_coverage_layer_when_empty() -> None:
    card = _result().to_card_payload()
    assert "coverage_annotations" not in card  # byte-identical firewall
    # the prior additive layers are still emitted (unchanged behaviour)
    assert "pedagogy_annotations" in card
    assert "citation_resolutions" in card


def test_card_payload_includes_coverage_layer_when_present() -> None:
    result = _result(coverage_annotations=(_ann(_point()),))
    card = result.to_card_payload()
    assert "coverage_annotations" in card
    assert card["coverage_annotations"][0]["component_id"] == "src-001-c001"


def test_default_result_has_empty_coverage_tuple() -> None:
    assert _result().coverage_annotations == ()
