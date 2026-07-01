"""Leg-4: Irene Pass-2 SOURCE-direction narration figure-fidelity gate + reground.

RED-first down-payment. Root cause (verified): Pass-2 grounds on the DECK as the
sole visual authority, so when Gamma confabulates a chart numeral Irene faithfully
narrates the invented value over source truth. The one in-graph figure gate
(`_assert_figure_citations_within_perceived`) only enforces narration ⊆ deck, so a
deck-invented figure PASSES today; the source-direction signal
(`source_fidelity_audit.audit_numeric_provenance`) is WARN-only.

This suite pins the ADDITIVE source-direction gate + reground, behind the
`MARCUS_NARRATION_FIGURE_FIDELITY_ACTIVE` flag (default OFF → byte-identical). The
existing deck-direction gate is asserted UNCHANGED in every case (VO↔on-screen
protected invariant: the new gate only BLOCKS, it never rewrites/reorders VO).
"""

from __future__ import annotations

from typing import Any

import pytest

from app.specialists.irene.graph import (
    FIGURE_FIDELITY_ACTIVE_ENV,
    SOURCE_FIGURE_AUTHORITY_HEADER,
    VISUAL_AUTHORITY_HEADER,
    Pass2GroundingError,
    _assemble_pass_2_prompt,
    _assert_figure_citations_within_perceived,
    _assert_narration_figures_sourced,
    _slide_roster,
    _source_figure_authority_block,
)

FLAG = FIGURE_FIDELITY_ACTIVE_ENV


def _payload(slide_id: str, perceived_text: str) -> dict[str, Any]:
    """Minimal Pass-2 payload whose single slide's perceived (deck) figure is
    whatever numeral ``perceived_text`` carries."""
    return {
        "bundle_reference": "bundle",
        "lesson_plan": {"title": "Adoption Trends"},
        "gary_slide_output": [
            {"slide_id": slide_id, "visual_description": "Stat callout slide."}
        ],
        "slide_briefs": [{"slide_id": slide_id, "prompt": "Stat callout."}],
        "perception_artifacts": [
            {
                "slide_id": slide_id,
                "confidence": "HIGH",
                "coverage": "perceived",
                "extracted_text": perceived_text,
                "layout_description": "Full-bleed stat callout.",
                "slide_title": "Adoption",
                "text_blocks": [{"text": perceived_text, "role": "callout"}],
                "visual_elements": [{"kind": "stat_callout", "text": perceived_text}],
                "source_png_path": f"bundle/{slide_id}.png",
            }
        ],
    }


def _segment(slide_id: str, text: str) -> dict[str, Any]:
    return {
        "narration_script": [
            {"id": "seg-1", "slide_id": slide_id, "narration_text": text}
        ],
        "segment_manifest_deltas": [],
    }


def test_red_unsourced_confabulated_figure_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """RED: deck rendered $4.6B (absent from source); narration cites it. The
    deck-direction gate PASSES (it is in the deck) → today it ships. The new
    source-direction gate RAISES figure-unsourced (flag ON)."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-01", "$4.6B market")
    roster = _slide_roster(payload)
    source = "Adoption rose to 67% while 18% still lag."  # NO money figure
    parsed = _segment("slide-01", "The market reached $4.6B this year.")

    # Deck-direction gate is UNCHANGED and PASSES on the deck-confabulated figure
    # (this is exactly the false-green the WARN-only source signal lets through).
    _assert_figure_citations_within_perceived(parsed, roster)

    with pytest.raises(Pass2GroundingError) as exc:
        _assert_narration_figures_sourced(parsed, roster, source_text=source)
    assert exc.value.tag == "irene.pass2.figure-unsourced"
    assert "money-trillion:0.0046" in str(exc.value)


def test_red_source_vs_deck_conflict_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """RED (🔒 VO-protection): source 67%, deck 60%, narration 60%. Deck-direction
    gate PASSES (60% is in the deck). New gate RAISES figure-source-deck-conflict
    → routes the repair to Gamma; never desyncs VO from on-screen (flag ON)."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-02", "60% adoption")  # deck confabulated 60%
    roster = _slide_roster(payload)
    source = "Adoption reached 67%, up from 18% a year earlier."
    parsed = _segment("slide-02", "Adoption climbed to 60% this year.")

    _assert_figure_citations_within_perceived(parsed, roster)  # deck-direction PASSES

    with pytest.raises(Pass2GroundingError) as exc:
        _assert_narration_figures_sourced(parsed, roster, source_text=source)
    assert exc.value.tag == "irene.pass2.figure-source-deck-conflict"
    assert "percent:60" in str(exc.value)
    assert "Gamma" in str(exc.value)


def test_green_sourced_and_deck_consistent_no_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GREEN control: narration figure ⊆ source AND consistent with deck → NO raise;
    the existing deck-direction gate on the clean case is unchanged (also passes)."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-03", "67% adoption")  # deck matches source
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."
    parsed = _segment("slide-03", "Two-thirds — 67% — of teams have adopted it.")

    _assert_figure_citations_within_perceived(parsed, roster)  # deck-direction clean
    _assert_narration_figures_sourced(parsed, roster, source_text=source)  # no raise


def test_green_flag_off_gate_inert_and_prompt_byte_identical(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GREEN firewall: flag OFF → gate inert (no raise even on the confabulated
    case) AND the Pass-2 prompt is byte-identical to the flag-ON prompt minus the
    spliced source-figure block (proves the flag is the ONLY behavioral seam)."""
    monkeypatch.delenv(FLAG, raising=False)
    payload = _payload("slide-01", "$4.6B market")
    roster = _slide_roster(payload)
    source = "Adoption rose to 67% while 18% still lag."
    parsed = _segment("slide-01", "The market reached $4.6B this year.")

    # Flag OFF → gate is inert on input that RAISES flag-ON.
    _assert_narration_figures_sourced(parsed, roster, source_text=source)

    _, user_off = _assemble_pass_2_prompt(
        payload, extracted_source=source, slide_roster=roster
    )
    assert SOURCE_FIGURE_AUTHORITY_HEADER not in user_off

    monkeypatch.setenv(FLAG, "1")
    _, user_on = _assemble_pass_2_prompt(
        payload, extracted_source=source, slide_roster=roster
    )
    assert SOURCE_FIGURE_AUTHORITY_HEADER in user_on
    assert "67%" in user_on  # source figures surfaced to the model

    # The ON prompt is EXACTLY the OFF prompt with the block spliced between the
    # source corpus and the visual-authority header — nothing else changes.
    block_start = user_on.index(SOURCE_FIGURE_AUTHORITY_HEADER)
    block_end = user_on.index(VISUAL_AUTHORITY_HEADER)
    reconstructed_off = user_on[:block_start] + user_on[block_end:]
    assert reconstructed_off == user_off


def _two_slide_payload(
    a_id: str, a_perceived: str, b_id: str, b_perceived: str
) -> dict[str, Any]:
    """Two-slide Pass-2 payload; each slide's perceived (deck) figure is whatever
    numeral its ``*_perceived`` text carries (used to prove per-slide conflict
    keying does not leak slide A's deck figure into slide B)."""
    payload = _payload(a_id, a_perceived)
    payload["gary_slide_output"].append(
        {"slide_id": b_id, "visual_description": "Stat callout slide."}
    )
    payload["slide_briefs"].append({"slide_id": b_id, "prompt": "Stat callout."})
    payload["perception_artifacts"].append(
        {
            "slide_id": b_id,
            "confidence": "HIGH",
            "coverage": "perceived",
            "extracted_text": b_perceived,
            "layout_description": "Full-bleed stat callout.",
            "slide_title": "Adoption",
            "text_blocks": [{"text": b_perceived, "role": "callout"}],
            "visual_elements": [{"kind": "stat_callout", "text": b_perceived}],
            "source_png_path": f"bundle/{b_id}.png",
        }
    )
    return payload


def test_edge2_unkeyed_segment_confab_figure_still_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Edge-2 RED-first: a narration segment with NO slide_id / perception_source
    and no delta to resolve one carries a confabulated ``$9.9B``. The whole-segment
    ``continue`` skip let it ESCAPE pre-fix (no raise). Post-fix the GLOBAL
    source-provenance check still runs on the unkeyed segment and RAISES
    figure-unsourced; only the deck-conflict sub-check degrades (no per-slide key)."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-01", "Chart of adoption over time")
    roster = _slide_roster(payload)
    source = "Adoption rose to 67% while 18% still lag."  # NO money figure
    # Unkeyed segment: no slide_id, no perception_source, no matching delta.
    parsed = {
        "narration_script": [
            {"id": "seg-x", "narration_text": "The market hit $9.9B this year."}
        ],
        "segment_manifest_deltas": [],
    }

    with pytest.raises(Pass2GroundingError) as exc:
        _assert_narration_figures_sourced(parsed, roster, source_text=source)
    assert exc.value.tag == "irene.pass2.figure-unsourced"
    assert "money-trillion:0.0099" in str(exc.value)
    assert "<unkeyed>" in str(exc.value)


def test_multi_slide_keying_no_false_conflict_on_other_slide(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Per-slide conflict keying: slide-A's deck legitimately shows 60%; slide-B's
    narration cites 60% (absent from source). Because slide-B's OWN perceived set
    ({18%}) does not contain 60%, this must classify as figure-unsourced — NOT a
    false figure-source-deck-conflict driven by slide-A's deck figure."""
    monkeypatch.setenv(FLAG, "1")
    payload = _two_slide_payload("slide-A", "60% share", "slide-B", "18% lag")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."  # kinds={percent}; 60% NOT present
    # slide-A narrates its sourced 67% (clean); slide-B narrates 60%, which lives in
    # slide-A's deck but NOT slide-B's. With correct per-slide conflict keying,
    # slide-B's own perceived set ({18%}) governs → figure-unsourced. A buggy GLOBAL
    # perceived union ({60%, 18%}) would misclassify it as figure-source-deck-conflict.
    parsed = {
        "narration_script": [
            {"id": "seg-a", "slide_id": "slide-A", "narration_text": "Adoption reached 67%."},
            {"id": "seg-b", "slide_id": "slide-B", "narration_text": "It climbed to 60%."},
        ],
        "segment_manifest_deltas": [],
    }

    with pytest.raises(Pass2GroundingError) as exc:
        _assert_narration_figures_sourced(parsed, roster, source_text=source)
    assert exc.value.tag == "irene.pass2.figure-unsourced"
    assert "slide-B" in str(exc.value)
    assert "percent:60" in str(exc.value)


def test_empty_source_every_digit_figure_unsourced_and_none_present_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty-source: a source with ZERO digit-form numerals + flag ON → any narrated
    digit-form figure raises figure-unsourced, and _source_figure_authority_block
    emits its explicit "none present" form."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-04", "60% adoption")
    roster = _slide_roster(payload)
    source = "Adoption is rising steadily across many teams and organizations."
    parsed = _segment("slide-04", "Adoption climbed to 60% this year.")

    with pytest.raises(Pass2GroundingError) as exc:
        _assert_narration_figures_sourced(parsed, roster, source_text=source)
    assert exc.value.tag == "irene.pass2.figure-unsourced"
    assert "percent:60" in str(exc.value)

    block = _source_figure_authority_block(source)
    assert "<none present in source>" in block


def test_word_form_and_bare_integer_ignored_no_neck_widening(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Guard against a future _FIGURE_RE regression: word-form ("sixty percent") and
    bare-integer ("3 pillars") numerals in narration are OUT of the frozen neck →
    they neither raise figure-unsourced nor widen the gate (no raise at all)."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-05", "67% adoption")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."
    parsed = _segment(
        "slide-05", "Sixty percent of the 3 pillars are now widely adopted."
    )

    # No digit-form $N / N% / Nx figure is present in the narration → gate is silent.
    _assert_narration_figures_sourced(parsed, roster, source_text=source)
