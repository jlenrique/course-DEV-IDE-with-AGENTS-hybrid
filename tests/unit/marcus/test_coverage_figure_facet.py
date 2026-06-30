"""Numeral-facet carriage refinement for the must-cover coverage gate (RED-first).

Party-RATIFIED (Murat/Irene/Vera/Winston) close-blocking refinement: the must-cover
obligation for a figure-bearing source point is "the load-bearing FIGURE TOKENS reach
the point's resolved anchor surface", NOT "the verbatim sentence is quoted". The
pipeline GENERATES (paraphrases) narration, so a full-span quote check over-blocks
EVERY real run (a vacuous-RED gate). These tests pin the refinement:

  * a DROPPED figure (absent from the anchor surface) -> missing -> BLOCK, with the
    dropped token legible in ``r7_report``;
  * a PARAPHRASE that carries the figure token -> COVERED (the over-block RED);
  * a figure token on a DIFFERENT slide does NOT count (anchor-scoped, never deck-wide);
  * negation/comparator is UNCHANGED (full-span; never greened off a token subset);
  * the VACUOUS-RECEIPT GUARD still fires when every point is token-missing;
  * a framing-only deck (figure lives in the Gamma PNG) is ``not_assessed`` -- never a
    false ``missing`` from deck text absence, never a silent green.

OFFLINE; in-memory anchors; no live LLM. R7 is the reporting caller.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.marcus.lesson_plan.coverage_annotation import CoverageAnnotation
from app.marcus.lesson_plan.coverage_gate import (
    evaluate_coverage_gate,
    evaluate_vacuous_receipt,
)
from app.marcus.lesson_plan.coverage_receipt import (
    AnchorResolution,
    derive_coverage_receipt,
)
from app.marcus.lesson_plan.source_point import SourcePoint

_TS = datetime(2026, 6, 30, 12, 0, 0, tzinfo=UTC)


def _point(
    ordinal: int,
    text: str,
    *,
    component_id: str = "src-001-c001",
    slide_key: str = "Slide 1",
    risk_flags=("numeric",),
    intents=("detail_in_narration",),
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
# DRIFT: a dropped figure on the anchored narration surface -> BLOCK
# --------------------------------------------------------------------------- #


def test_dropped_figure_token_blocks_with_evidence() -> None:
    # The real "$5.3 trillion -> one-fifth" drop: generated narration paraphrases the
    # sentence AND drops the figure token. Must BLOCK, driven by the dropped figure.
    pt = _point(1, "U.S. health spending reached $5.3 trillion.")
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="It climbed to nearly one-fifth of national output.",
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "missing"
    assert row.must_cover is True
    # the BLOCK is driven by the dropped figure token (verbatim-critical absence)
    assert row.verbatim_absent is True
    assert "money-trillion:5.3" in row.r7_report["dropped_figs"]
    assert "money-trillion:5.3" in row.r7_report["source_figs"]
    assert len(evaluate_coverage_gate(receipt)) == 1


# --------------------------------------------------------------------------- #
# COVERED (the over-block RED): a paraphrase that carries the figure token
# --------------------------------------------------------------------------- #


def test_paraphrase_carrying_figure_token_is_covered() -> None:
    # Generated narration paraphrases the sentence BUT keeps the figure ("18%").
    # Today the full-span _span_present check FALSELY makes this missing (the
    # over-block); after the fix it is COVERED + verified.
    pt = _point(1, "Roughly 18% of patients relapsed within a year.")
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="About 18% saw a relapse inside twelve months.",
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_in_narration"
    assert row.containment_verdict == "verbatim_preserved"
    assert row.vouch_level == "verified"  # figure carried + R7 Axis-B clean
    assert row.verbatim_absent is False
    assert row.r7_report["dropped_figs"] == []
    assert evaluate_coverage_gate(receipt) == ()


def test_dose_unit_token_carried_in_paraphrase_is_covered() -> None:
    # A dose unit ("5 mg") the figure neck does not tokenize is captured via _DOSE_RE;
    # a paraphrase keeping "5 mg" is covered.
    pt = _point(1, "Administer 5 mg once daily.", risk_flags=("numeric", "dosing"))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="Give the patient 5 mg per day.",
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_in_narration"
    assert row.vouch_level == "verified"
    assert "dose:5mg" in row.r7_report["source_figs"]
    assert evaluate_coverage_gate(receipt) == ()


# --------------------------------------------------------------------------- #
# Anchor-scope: a figure token on a DIFFERENT slide's surface does not count
# --------------------------------------------------------------------------- #


def test_figure_token_on_other_slide_does_not_count() -> None:
    pt = _point(1, "Spending hit $5.3 trillion.", slide_key="Slide 1")
    anchors = {
        # the point's OWN anchor drops the figure ...
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="It grew substantially over the decade.",
        ),
        # ... while a DIFFERENT slide happens to carry the same token (must not count)
        "Slide 2": AnchorResolution(
            slide_key="Slide 2", slide_present=True, slide_text="$5.3 trillion in total."
        ),
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "missing"
    assert "money-trillion:5.3" in row.r7_report["dropped_figs"]
    assert len(evaluate_coverage_gate(receipt)) == 1


# --------------------------------------------------------------------------- #
# Negation/comparator: UNCHANGED — never greened off a token subset
# --------------------------------------------------------------------------- #


def test_negation_point_never_greened_off_figure_subset() -> None:
    # negation + numeric: advisory risk DOMINATES the figure facet. A narration that
    # carries the $5 billion token but FLIPS polarity (drops "not") must NOT green —
    # the full-span verbatim check (polarity-preserving) governs.
    pt = _point(1, "Costs did not exceed $5 billion.", risk_flags=("negation", "numeric"))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="Costs did exceed $5 billion.",  # token present, polarity FLIPPED
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    # full span absent -> not carried -> missing (NEVER covered/verified off the subset)
    assert row.coverage_status == "missing"
    assert row.vouch_level == "not_assessed"
    assert len(evaluate_coverage_gate(receipt)) == 1


# --------------------------------------------------------------------------- #
# Vacuous-receipt guard: token-missing across the board still blocks
# --------------------------------------------------------------------------- #


def test_vacuous_guard_holds_when_every_point_token_missing() -> None:
    p1 = _point(1, "A was $5.3 trillion.")
    p2 = _point(2, "B was 18% of the total.")
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="Several things changed over time.",
        )
    }
    receipt = derive_coverage_receipt([_ann([p1, p2])], anchors=anchors, generated_at=_TS)
    assert receipt.is_vacuous() is True
    assert (
        evaluate_vacuous_receipt(receipt, note_bearing_content_exists=True) is not None
    )


# --------------------------------------------------------------------------- #
# Deck not text-verifiable: framing-only slide is not_assessed, never false-missing
# --------------------------------------------------------------------------- #


def test_framing_only_deck_is_not_assessed_not_missing() -> None:
    # A gist-on-slide numeric point: the deck renders but slide_text is framing only
    # (the real figure is in the Gamma PNG). It must be covered_on_slide / not_assessed
    # (disclosed), never a false missing from deck text absence, and must NOT block.
    pt = _point(1, "Total was $5.3 trillion.", intents=("gist_on_slide",))
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=True,
            slide_text="Healthcare spending overview",
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_on_slide"
    assert row.vouch_level == "not_assessed"  # deck not text-verifiable
    assert row.containment_verdict is None
    assert row.verbatim_absent is False  # never a false missing from deck text absence
    assert evaluate_coverage_gate(receipt) == ()  # do not block on the deck


def test_altered_figure_on_surface_is_advisory_not_verified() -> None:
    # The source figure IS carried, but the narration ALSO introduces an UNSOURCED
    # figure (reworded/altered context). Graduated: covered (not dropped) but the R7
    # Axis-B violation downgrades the vouch to advisory_caveat — never a silent green.
    pt = _point(1, "Spending was $5.3 trillion.")
    anchors = {
        "Slide 1": AnchorResolution(
            slide_key="Slide 1",
            slide_present=False,
            narration_present=True,
            narration_text="Spending was $5.3 trillion, up from $4 trillion before.",
        )
    }
    receipt = derive_coverage_receipt([_ann([pt])], anchors=anchors, generated_at=_TS)
    row = receipt.rows[0]
    assert row.coverage_status == "covered_in_narration"
    assert row.vouch_level == "advisory_caveat"  # unsourced $4 trillion introduced
    assert "money-trillion:4" in row.r7_report["unsourced"]["numerals_units"]
    assert evaluate_coverage_gate(receipt) == ()  # disclosed, not a block
