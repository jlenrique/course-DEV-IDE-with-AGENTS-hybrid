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
    PERCEIVED_SPEAKABLE_FIGURES_HEADER,
    SOURCE_FIGURE_AUTHORITY_HEADER,
    UNRENDERED_SOURCE_FIGURE_TOKEN,
    Pass2GroundingError,
    _assemble_pass_2_prompt,
    _assert_figure_citations_within_perceived,
    _assert_narration_figures_sourced,
    _assert_source_figures_positively_carried,
    _redact_unrendered_source_figures,
    _slide_roster,
    _source_figure_authority_block,
    _union_perceived_figures,
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
    """GREEN firewall: flag OFF → gate inert AND Flag-ON prompt is Flag-OFF
    plus the spliced source-figure block only.

    NFR-I6 carve-out: the always-on perceived-speakable block is present in
    BOTH prompts (baseline VO↔on-screen). Flag-OFF stability means absence of
    the Flag-ON-only source-authority block — not eternal pre-speakable bytes.
    """
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
    assert PERCEIVED_SPEAKABLE_FIGURES_HEADER in user_off

    monkeypatch.setenv(FLAG, "1")
    _, user_on = _assemble_pass_2_prompt(
        payload, extracted_source=source, slide_roster=roster
    )
    assert SOURCE_FIGURE_AUTHORITY_HEADER in user_on
    assert PERCEIVED_SPEAKABLE_FIGURES_HEADER in user_on
    assert "67%" in user_on  # source figures surfaced in authority block
    assert "SOURCE WINS" not in user_on
    assert "narrate the source value" not in user_on.lower()

    # ON == OFF with the Flag-ON-only source-authority block spliced before the
    # always-on speakable block — nothing else changes.
    block_start = user_on.index(SOURCE_FIGURE_AUTHORITY_HEADER)
    block_end = user_on.index(PERCEIVED_SPEAKABLE_FIGURES_HEADER)
    reconstructed_off = user_on[:block_start] + user_on[block_end:]
    assert reconstructed_off == user_off


def test_tejal_slide05_source_10_90_figure_free_deck_prompt_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tejal P4 live halt shape: source has 10%/90%; slide-05 has no perceived
    digit-form figures. Prompt must not license speaking those digits; gate still
    fail-loud if narration cites them.
    """
    monkeypatch.setenv(FLAG, "1")
    payload = _payload(
        "slide-05",
        "Why Ideas Alone Are Not Enough. A brilliant idea without a capable "
        "champion is just a hypothesis waiting to expire.",
    )
    roster = _slide_roster(payload)
    assert _union_perceived_figures(roster) == set()
    source = (
        "Having the right idea is only 10% of the battle; the other 90% is "
        "having the political savvy to carry it."
    )
    redacted = _redact_unrendered_source_figures(source, deck_figures=set())
    assert "10%" not in redacted
    assert "90%" not in redacted
    assert UNRENDERED_SOURCE_FIGURE_TOKEN in redacted

    _, user = _assemble_pass_2_prompt(
        payload, extracted_source=source, slide_roster=roster
    )
    assert PERCEIVED_SPEAKABLE_FIGURES_HEADER in user
    assert "slide-05: <none" in user
    assert UNRENDERED_SOURCE_FIGURE_TOKEN in user
    # Raw digit forms must not remain in the prompt corpus region (authority
    # may still list provenance surfaces — but speech rules forbid speaking them).
    corpus_end = user.index(SOURCE_FIGURE_AUTHORITY_HEADER)
    corpus = user[:corpus_end]
    assert "10%" not in corpus
    assert "90%" not in corpus
    assert "on-screen binds speech" in user.lower() or "perceived speakable" in user.lower()
    assert "SOURCE WINS" not in user
    assert "narrate the source value" not in user.lower()

    # Hard bailiff unchanged: if Irene still speaks 10%/90%, gate fails loud.
    parsed = _segment(
        "slide-05",
        "Having the right idea is only 10% of the battle; the other 90% is execution.",
    )
    with pytest.raises(Pass2GroundingError) as exc:
        _assert_figure_citations_within_perceived(parsed, roster)
    assert exc.value.tag == "irene.pass2.figure-contradiction"
    assert "percent:10" in str(exc.value)
    assert "percent:90" in str(exc.value)

    # Paraphrase without digit-form figures is legal.
    clean = _segment(
        "slide-05",
        "Having the right idea is only a small part of the battle; most of the "
        "work is the political savvy to carry it.",
    )
    _assert_figure_citations_within_perceived(clean, roster)
    _assert_narration_figures_sourced(clean, roster, source_text=source)


def test_per_slide_speakable_does_not_widen_from_other_slide(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deck-union must not license speaking slide-A's figures on slide-B."""
    monkeypatch.setenv(FLAG, "1")
    payload = _two_slide_payload("slide-A", "10% of the battle", "slide-B", "no digits here")
    roster = _slide_roster(payload)
    source = "Having the right idea is only 10% of the battle."
    _, user = _assemble_pass_2_prompt(
        payload, extracted_source=source, slide_roster=roster
    )
    assert "slide-A: percent:10" in user or "slide-A: percent:10" in user.replace(" ", "")
    # Accept either normalized token listing
    assert "slide-B: <none" in user
    # 10% may survive in prompt_source because it is on the deck (slide-A).
    # Speech on slide-B is still forbidden by the per-slide speakable line + gate.
    parsed = _segment("slide-B", "It is only 10% of the battle.")
    with pytest.raises(Pass2GroundingError) as exc:
        _assert_figure_citations_within_perceived(parsed, roster)
    assert exc.value.tag == "irene.pass2.figure-contradiction"


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


def test_t4a_percent_tolerance_source_18_4_narration_18_no_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T4a precision: source 18.4% → deck/narration 18% must not false-halt."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-t4a", "18% still lag")
    roster = _slide_roster(payload)
    source = "Adoption rose to 67% while 18.4% still lag."
    parsed = _segment("slide-t4a", "About 18% of teams still lag.")
    _assert_figure_citations_within_perceived(parsed, roster)
    _assert_narration_figures_sourced(parsed, roster, source_text=source)


def test_t4a_comma_money_surface_form_matches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T4a surface-form: thousands separators in source money normalize cleanly."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-money", "$1,200 billion market")
    roster = _slide_roster(payload)
    source = "The addressable market is $1,200 billion worldwide."
    parsed = _segment("slide-money", "The market is $1200 billion worldwide.")
    _assert_figure_citations_within_perceived(parsed, roster)
    _assert_narration_figures_sourced(parsed, roster, source_text=source)


def test_t4a_large_percent_drift_still_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tolerance must not swallow real conflicts (67% vs 60%)."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-drift", "60% adoption")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."
    parsed = _segment("slide-drift", "Adoption climbed to 60% this year.")
    with pytest.raises(Pass2GroundingError) as exc:
        _assert_narration_figures_sourced(parsed, roster, source_text=source)
    assert exc.value.tag == "irene.pass2.figure-source-deck-conflict"


def test_t4b_positive_carry_miss_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """T4b RED: source∩deck figure present on-screen but omitted from narration."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-pc", "67% adoption")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year while 18% still lag."
    # Narration omits the on-screen 67% (and invents no digit-form figure).
    parsed = _segment("slide-pc", "Adoption is climbing across many teams.")
    _assert_figure_citations_within_perceived(parsed, roster)
    _assert_narration_figures_sourced(parsed, roster, source_text=source)
    with pytest.raises(Pass2GroundingError) as exc:
        _assert_source_figures_positively_carried(
            parsed, roster, source_text=source
        )
    assert exc.value.tag == "irene.pass2.figure-positive-carry-miss"
    assert "percent:67" in str(exc.value)


def test_t4b_positive_carry_happy_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """T4b GREEN: source∩deck figures spoken → no raise."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-pc-ok", "67% adoption")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."
    parsed = _segment("slide-pc-ok", "Two-thirds — 67% — of teams have adopted it.")
    _assert_figure_citations_within_perceived(parsed, roster)
    _assert_narration_figures_sourced(parsed, roster, source_text=source)
    _assert_source_figures_positively_carried(parsed, roster, source_text=source)


def test_t4b_positive_carry_flag_off_inert(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T4b firewall: flag OFF → positive-carry miss is inert."""
    monkeypatch.delenv(FLAG, raising=False)
    payload = _payload("slide-pc-off", "67% adoption")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."
    parsed = _segment("slide-pc-off", "Adoption is climbing across many teams.")
    _assert_source_figures_positively_carried(parsed, roster, source_text=source)


def test_t4b_positive_carry_tolerates_percent_near_match(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T4b + T4a: deck 18% near-matches source 18.4% and counts as carried."""
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-pc-tol", "18% still lag")
    roster = _slide_roster(payload)
    source = "Adoption rose to 67% while 18.4% still lag."
    parsed = _segment("slide-pc-tol", "About 18% of teams still lag.")
    _assert_narration_figures_sourced(parsed, roster, source_text=source)
    _assert_source_figures_positively_carried(parsed, roster, source_text=source)


def test_t4c_pass2_act_path_halts_on_confab_and_carry_miss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """T4c: flag-ON activation path mirrors _act_pass_2 gate order.

    Exercises the same post-parse assert sequence used inside ``_act_pass_2``
    (deck ⊆ perceived → source-direction → positive-carry) with the flag ON,
    proving both halt arms without a paid Pass-2 LLM call.
    """
    monkeypatch.setenv(FLAG, "1")
    payload = _payload("slide-t4c", "67% adoption")
    roster = _slide_roster(payload)
    source = "Adoption reached 67% this year."

    # Clean twin: no false halt.
    clean = _segment("slide-t4c", "Adoption reached 67% this year.")
    _assert_figure_citations_within_perceived(clean, roster)
    _assert_narration_figures_sourced(clean, roster, source_text=source)
    _assert_source_figures_positively_carried(clean, roster, source_text=source)

    # Confab halt (source-direction).
    confab = _segment("slide-t4c", "The market hit $4.6B at 67% adoption.")
    with pytest.raises(Pass2GroundingError) as exc_confab:
        _assert_narration_figures_sourced(confab, roster, source_text=source)
    assert exc_confab.value.tag == "irene.pass2.figure-unsourced"

    # Positive-carry halt after source-direction would pass.
    miss = _segment("slide-t4c", "Adoption is climbing across many teams.")
    _assert_narration_figures_sourced(miss, roster, source_text=source)
    with pytest.raises(Pass2GroundingError) as exc_miss:
        _assert_source_figures_positively_carried(miss, roster, source_text=source)
    assert exc_miss.value.tag == "irene.pass2.figure-positive-carry-miss"
