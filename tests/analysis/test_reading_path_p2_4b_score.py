"""Self-test for the P2-4b conformance-finalize scoring harness.

Proves the A6 math on SYNTHETIC emitted/gold fixtures (no live classifier, no
perceiver, no vision/perception substrate). The headline assertion mirrors the
held-out confirm/deny round: 13/14 primary-key -> 0.93.

Authority: reading-path-patterns-catalog.md v1.1 §9.4 + §11;
reading-path-gap-resolution-G2-G3-2026-06-22.md (IN/OUT contract);
reading-path-holdout-gold-labels-2026-06-23.md (gold tuples).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_MODULE_PATH = _ROOT / "scripts" / "analysis" / "reading_path_p2_4b_score.py"
_MODULE_NAME = "reading_path_p2_4b_score"

_spec = importlib.util.spec_from_file_location(_MODULE_NAME, _MODULE_PATH)
rp = importlib.util.module_from_spec(_spec)
# Register before exec so @dataclass can resolve cls.__module__ during class body.
sys.modules[_MODULE_NAME] = rp
_spec.loader.exec_module(rp)  # type: ignore[union-attr]

ReadingPathTuple = rp.ReadingPathTuple
score = rp.score
fold_image_role = rp.fold_image_role
QUARANTINED_SENTINEL = rp.QUARANTINED_SENTINEL


# --------------------------------------------------------------------------- #
# image_role folding (G2): 2.5 -> 2, tier-3 quarantined, none -> None          #
# --------------------------------------------------------------------------- #

def test_fold_image_role_2p5_folds_to_2():
    assert fold_image_role(2.5) == 2
    assert fold_image_role("2.5") == 2


def test_fold_image_role_tier3_quarantined():
    assert fold_image_role(3) == QUARANTINED_SENTINEL
    assert fold_image_role("3") == QUARANTINED_SENTINEL


def test_fold_image_role_none_passthrough():
    assert fold_image_role(None) is None
    assert fold_image_role("none") is None


def test_fold_image_role_scored_tiers_unchanged():
    for tier in (1, 2, 4):
        assert fold_image_role(tier) == tier


# --------------------------------------------------------------------------- #
# Headline A6 math on the synthetic held-out mirror                           #
# --------------------------------------------------------------------------- #

def test_demo_primary_key_top1_is_13_of_14():
    report = score(rp.build_demo_rows())
    assert report.n == 14
    assert report.primary_key_hits == 13
    assert report.primary_key_top1 == pytest.approx(13 / 14, abs=1e-6)
    assert report.primary_key_top1 == pytest.approx(0.9286, abs=1e-3)
    assert report.passes_primary_key  # 0.93 >= 0.85


def test_demo_macro_per_axis_is_13_of_14():
    # 17_ is the only macro miss (two_pane emitted vs multi_column gold).
    report = score(rp.build_demo_rows())
    assert report.per_axis_hits["macro_layout"] == 13


def test_demo_text_substructure_per_axis_is_13_of_14():
    # 21_ is the only text_substructure miss (enumerated_process vs peer_boxes).
    report = score(rp.build_demo_rows())
    assert report.per_axis_hits["text_substructure"] == 13


def test_demo_image_role_and_cadence_per_axis_are_14_of_14():
    report = score(rp.build_demo_rows())
    assert report.per_axis_hits["image_role"] == 14
    assert report.per_axis_hits["narration_cadence"] == 14


def test_demo_full_tuple_rate_passes_threshold():
    # 17_ (macro) and 21_ (text_substructure) each break full-tuple -> 12/14.
    report = score(rp.build_demo_rows())
    assert report.full_tuple_hits == 12
    assert report.full_tuple_rate == pytest.approx(12 / 14, abs=1e-6)
    assert report.passes_full_tuple  # 0.857 >= 0.80


def test_demo_confusion_records_the_17_miss():
    report = score(rp.build_demo_rows())
    # gold multi_column emitted as two_pane for 17_.
    assert report.macro_confusion.get(("multi_column", "two_pane")) == 1


def test_callout_intent_excluded_from_primary_and_full_tuple():
    # 21_ gold callout_intent=takeaway_imperative, emitted=inform -> mismatch on
    # the callout axis, but the primary key + full tuple must still HIT (callout
    # is out of both per D2).
    rows = score(rp.build_demo_rows()).per_slide
    by_id = {r["slide_id"]: r for r in rows}
    r21 = by_id["21_Key-Takeaways"]
    assert r21["primary_key_match"] is True
    assert r21["callout_intent_match"] is False
    # full tuple for 21_ is broken by text_substructure, NOT by callout.
    assert r21["full_tuple_match"] is False


def test_callout_intent_probation_vector_reported():
    report = score(rp.build_demo_rows())
    # Gold carries 4 real (non-inform) callout_intents: 5_, 18_, 22_, 21_.
    assert report.callout_intent_scorable == 4
    # In the demo, 5_/18_/22_ are emitted identical to gold (hit); 21_ emitted
    # inform (miss) -> 3/4.
    assert report.callout_intent_hits == 3
    assert report.callout_intent_agreement == pytest.approx(3 / 4, abs=1e-6)


# --------------------------------------------------------------------------- #
# Synthetic edge cases proving the contract independently of the held-out set  #
# --------------------------------------------------------------------------- #

def test_perfect_match_is_1_0():
    gold = ReadingPathTuple("split_image_text", 1, "hero_message", "moderate", "inform")
    rows = [("s1", gold, gold)]
    report = score(rows)
    assert report.primary_key_top1 == 1.0
    assert report.full_tuple_rate == 1.0


def test_2p5_emitted_matches_tier2_gold_via_fold():
    gold = ReadingPathTuple("split_image_text", 2, "comparison_pair", "moderate")
    emitted = ReadingPathTuple("split_image_text", 2.5, "comparison_pair", "moderate")
    report = score([("s1", emitted, gold)])
    # 2.5 folds to 2 -> primary key matches.
    assert report.primary_key_hits == 1
    assert report.per_axis_hits["image_role"] == 1


def test_tier3_quarantined_gold_is_guaranteed_miss_and_tracked():
    gold = ReadingPathTuple("split_image_text", 3, "dense_exposition", "dense")
    emitted = ReadingPathTuple("split_image_text", 3, "dense_exposition", "dense")
    report = score([("s1", emitted, gold)])
    # Both fold to the quarantine sentinel -> they DO compare equal to each
    # other, but the row is flagged as quarantined for exclusion accounting.
    assert "s1" in report.quarantined_rows
    # The sentinel equals itself, so a tier3-vs-tier3 row still "matches" the
    # primary key; the quarantine list is what callers use to EXCLUDE it.
    assert report.primary_key_hits == 1


def test_tier3_gold_vs_scored_emitted_is_a_miss():
    gold = ReadingPathTuple("split_image_text", 3, "dense_exposition", "dense")
    emitted = ReadingPathTuple("split_image_text", 2, "dense_exposition", "dense")
    report = score([("s1", emitted, gold)])
    assert report.primary_key_hits == 0
    assert "s1" in report.quarantined_rows


def test_macro_mismatch_breaks_primary_key():
    gold = ReadingPathTuple("multi_column", 2, "peer_boxes", "dense")
    emitted = ReadingPathTuple("two_pane", 2, "peer_boxes", "dense")
    report = score([("s1", emitted, gold)])
    assert report.primary_key_hits == 0
    assert report.per_axis_hits["macro_layout"] == 0
    # image_role still matches on its own axis.
    assert report.per_axis_hits["image_role"] == 1


def test_none_image_role_matches_none():
    gold = ReadingPathTuple("two_pane", None, "comparison_pair", "dense")
    emitted = ReadingPathTuple("two_pane", "none", "comparison_pair", "dense")
    report = score([("s1", emitted, gold)])
    assert report.primary_key_hits == 1
