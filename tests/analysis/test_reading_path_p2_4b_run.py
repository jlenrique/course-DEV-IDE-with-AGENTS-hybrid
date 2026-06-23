"""Tests for the P2-4b runner's testable core (load_gold + score_emitted).

Does NOT import the in-flight classifier — exercises only gold-loading + the
scoring glue with synthetic emitted tuples. Mirrors the held-out round so the
0.93 primary-key number is reproduced through the runner path.
"""

from __future__ import annotations

from scripts.analysis.reading_path_p2_4b_run import load_gold, score_emitted
from scripts.analysis.reading_path_p2_4b_score import ReadingPathTuple


def test_load_gold_builds_14_tuples() -> None:
    gold = load_gold()
    assert len(gold) == 14
    # spot-check the two DENY corrections
    g17 = gold["17_Examples-of-Effective-Leadership-in-Public-Health"]
    assert g17.macro_layout == "multi_column"
    assert g17.derived_primary == "multi_column"
    g21 = gold["21_Key-Takeaways"]
    assert g21.text_substructure == "peer_boxes"
    assert g21.callout_intent == "takeaway_imperative"
    assert g21.macro_layout == "split_image_text"  # primary key unchanged by the denial
    # card_grid -> grid_quadrant reconciliation
    g20 = gold["20_Resources-for-Entrepreneurship-and-Innovation"]
    assert g20.derived_primary == "grid_quadrant"
    # a 'none' image_role slide
    assert gold["9_Comparing-Expected-Value-and-Expected-Utility"].image_role is None


def test_score_emitted_perfect_match_is_100pct() -> None:
    gold = load_gold()
    # emit exactly the gold -> every primary key matches
    report = score_emitted(dict(gold), gold)
    assert report.primary_key_top1 == 1.0
    assert report.passes_primary_key


def test_score_emitted_reproduces_heldout_093() -> None:
    """Mirror the held-out round: emit the catalog-v1 'kit' tuples; 17_ emitted as
    two_pane (kit proposal) is the single primary-key miss vs gold multi_column.
    """
    gold = load_gold()
    emitted = dict(gold)
    # 17_: kit proposed two_pane (the denied label) -> primary-key MISS vs gold
    g17 = gold["17_Examples-of-Effective-Leadership-in-Public-Health"]
    emitted["17_Examples-of-Effective-Leadership-in-Public-Health"] = ReadingPathTuple(
        macro_layout="two_pane",
        image_role=g17.image_role,
        text_substructure=g17.text_substructure,
        narration_cadence=g17.narration_cadence,
        callout_intent=g17.callout_intent,
        derived_primary="two_up_comparison",
    )
    report = score_emitted(emitted, gold)
    assert report.primary_key_top1 == 13 / 14  # 0.9286 >= 0.85
    assert report.passes_primary_key


def test_score_emitted_missing_slide_is_hard_error() -> None:
    gold = load_gold()
    partial = dict(gold)
    partial.pop("1_Diagnosis-Innovation")
    try:
        score_emitted(partial, gold)
    except ValueError as exc:
        assert "missing" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("expected a hard error for a missing held-out emission")
