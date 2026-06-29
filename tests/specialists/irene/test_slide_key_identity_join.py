"""Story enhanced-vo.1 (Slice 0) RED-first: directed-voice role->slide linkage is a
deterministic IDENTITY JOIN on a stable ``slide_key`` (the SOURCE-deck slide
ordinal each final segment descends from), replacing the source/final
ORDINAL-SET comparison that FAILS OPEN on clustered Gary decks.

Grounded in the REAL ``c2c6dcbf`` clustered deck (AC-A2 fixture): SIX source
slides (Pass-1 cluster heads c-u01..c-u06) exploded into THIRTEEN final slides.
NO mocks — the lineage carrier (slide_briefs.source_ref + lesson_plan.plan_units)
is the real shape Irene Pass-2 receives in its envelope.

  * AC-A3 — the OLD ordinal-set join FAILS OPEN on this deck; the NEW slide_key
    identity join FIRES the correct seed on the correct final segment. No fuzzy
    fallback: an unresolvable slide_key fails LOUD (build-breaking), it never
    silently falls back to ordinal matching.
  * AC-A4 — the same source slide yields the SAME slide_key across two clustering
    runs (re-clustering changes the FINAL ordinals, never the source identity).
  * AC-A1 — slide_key is stamped on every Pass-2 delta of a directed+enriched run.
  * AC-A5 — slide_key rides the segment_manifest_deltas blob to the join consumer.

OFFLINE ONLY: pure, deterministic, zero LLM/network/TTS spend.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.specialists.irene import graph
from app.specialists.irene.authoring.voice_direction_annotation import (
    VoiceDirectionError,
)

NARRATION_FLAG = "MARCUS_NARRATION_VOICE_DIRECTION_ACTIVE"

_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "specialists"
    / "irene"
    / "c2c6dcbf_source_to_final_slide_map.json"
)


def _fixture() -> dict[str, Any]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def flag_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(NARRATION_FLAG, "1")


def _deltas_for(final_ids: list[str]) -> list[dict[str, Any]]:
    """Frozen Pass-2 deltas for the given final slide ids (grounded shape)."""
    return [
        {
            "id": f"seg-{ordinal:02d}",
            "slide_id": slide_id,
            "narration_text": f"Narration for {slide_id}.",
            "behavioral_intent": "credible",
            "visual_references": [{"perception_source": slide_id}],
        }
        for ordinal, slide_id in enumerate(final_ids, start=1)
    ]


def _roster(final_ids: list[str], variant: str = "A") -> list[dict[str, Any]]:
    """A gary_slide_output roster (post-variant-filter: one row per slide_id)."""
    return [{"slide_id": sid, "dispatch_variant": variant} for sid in final_ids]


# --------------------------------------------------------------------------- #
# S2 (reworded; was a tautological "fails open" test) — PRECONDITION only: the
# real clustered deck's source/final ordinal sets DIVERGE (the condition under
# which the legacy ordinal-set join failed open). The genuine BEHAVIORAL proof
# that the NEW join FIRES on this exact divergence lives in
# `test_identity_join_fires_for_all_subslides_of_a_clustered_source`, which
# invokes the production function `_attach_voice_direction`.
# --------------------------------------------------------------------------- #
def test_clustered_deck_divergence_precondition() -> None:
    fx = _fixture()
    source_set = set(fx["source_slide_ordinals"])  # {1..6}
    final_set = set(fx["final_slide_ordinals"])  # {1..13}
    assert source_set != final_set  # the deck IS clustered -> the sets diverge
    assert source_set == {1, 2, 3, 4, 5, 6}
    assert final_set == set(range(1, 14))


# --------------------------------------------------------------------------- #
# AC-A3 (GREEN target) — the NEW slide_key map resolves every final segment to
# its TRUE source-slide identity from the real lineage carrier.
# --------------------------------------------------------------------------- #
def test_source_slide_key_map_matches_real_fixture() -> None:
    fx = _fixture()
    slide_key_by_final = graph._source_slide_key_by_final(
        fx["lesson_plan"], fx["slide_briefs"]
    )
    assert slide_key_by_final == fx["expected_slide_key_by_final"]
    # slide_key is the SOURCE ordinal, NOT the final ordinal: final slide-03
    # (3rd final slide) descends from SOURCE slide 2.
    assert slide_key_by_final["slide-03"] == "2"
    assert slide_key_by_final["slide-13"] == "6"


# --------------------------------------------------------------------------- #
# AC-A3 — the identity join FIRES: all sub-slides of one clustered source slide
# inherit that source slide's role seed (the intended pedagogical behavior).
# --------------------------------------------------------------------------- #
def test_identity_join_fires_for_all_subslides_of_a_clustered_source(
    flag_on: None,
) -> None:
    fx = _fixture()
    # Orchestrator seed table keyed by SOURCE ordinal: seed only source slide 2.
    by_slide = {"2": {"emotional_tone": "warm", "pace": "neutral", "energy": "medium"}}
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": _deltas_for(fx["final_segment_ids"]),
    }
    envelope = {
        "role_derived_voice_by_slide": {"by_slide": by_slide},
        "lesson_plan": fx["lesson_plan"],
        "slide_briefs": fx["slide_briefs"],
    }
    result = graph._attach_voice_direction(parsed, envelope)
    by_id = {d["id"]: d for d in result["segment_manifest_deltas"]}
    # final slide-02 (head), slide-03 (i1), slide-04 (i2) ALL descend from source
    # slide 2 -> all three fire the role-derived seed. The OLD join gave none.
    for seg in ("seg-02", "seg-03", "seg-04"):
        assert by_id[seg]["voice_direction"]["source"] == "role-derived"
        assert by_id[seg]["voice_direction"]["emotional_tone"] == "warm"
    # A source slide with no seed (e.g. source 1, 3..6) takes the built-in.
    assert by_id["seg-01"]["voice_direction"]["source"] == "cd-authored"
    assert by_id["seg-05"]["voice_direction"]["source"] == "cd-authored"


# --------------------------------------------------------------------------- #
# AC-A1 / AC-A5 — slide_key is stamped on EVERY delta and rides the blob.
# --------------------------------------------------------------------------- #
def test_slide_key_stamped_on_every_delta(flag_on: None) -> None:
    fx = _fixture()
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": _deltas_for(fx["final_segment_ids"]),
    }
    envelope = {
        "role_derived_voice_by_slide": {"by_slide": {"2": {"pace": "neutral"}}},
        "lesson_plan": fx["lesson_plan"],
        "slide_briefs": fx["slide_briefs"],
    }
    result = graph._attach_voice_direction(parsed, envelope)
    for delta in result["segment_manifest_deltas"]:
        assert delta.get("slide_key") == fx["expected_slide_key_by_final"][delta["slide_id"]]
        assert delta["slide_key"] is not None


# --------------------------------------------------------------------------- #
# AC-A3 / M1 — NO fuzzy fallback: a TRUE lineage gap fails LOUD, and the ONE
# diagnostic names ALL uncovered slide_ids (not just the first).
# --------------------------------------------------------------------------- #
def test_unresolvable_slide_key_fails_loud_naming_all_uncovered(flag_on: None) -> None:
    fx = _fixture()
    # Two final segments with no resolvable lineage (not in slide_briefs and not
    # reconstructable from the roster) + a seed table present -> must raise ONE
    # diagnostic listing BOTH, never silently fall back to ordinal matching.
    orphans = [
        {"id": "seg-98", "slide_id": "slide-98", "narration_text": "o1",
         "behavioral_intent": "credible", "visual_references": [{"perception_source": "slide-98"}]},
        {"id": "seg-99", "slide_id": "slide-99", "narration_text": "o2",
         "behavioral_intent": "credible", "visual_references": [{"perception_source": "slide-99"}]},
    ]
    deltas = _deltas_for(fx["final_segment_ids"]) + orphans
    parsed = {"narration_script": "x", "segment_manifest_deltas": deltas}
    envelope = {
        "role_derived_voice_by_slide": {"by_slide": {"2": {"pace": "neutral"}}},
        "lesson_plan": fx["lesson_plan"],
        "slide_briefs": fx["slide_briefs"],
        # roster intentionally OMITS slide-98/99 so the fallback cannot rescue them.
        "gary_slide_output": _roster(fx["final_segment_ids"]),
    }
    with pytest.raises(VoiceDirectionError) as exc:
        graph._attach_voice_direction(parsed, envelope)
    msg = str(exc.value)
    assert "slide-98" in msg and "slide-99" in msg  # ALL uncovered named, not just the first


# --------------------------------------------------------------------------- #
# M1 — a B-variant-filtered roster (slide_id-preserving: one row per slide_id,
# any variant) RESOLVES correctly; it does NOT hard-stop the run.
# --------------------------------------------------------------------------- #
def test_b_variant_filtered_roster_resolves(flag_on: None) -> None:
    fx = _fixture()
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": _deltas_for(fx["final_segment_ids"]),
    }
    envelope = {
        "role_derived_voice_by_slide": {"by_slide": {"2": {"pace": "neutral"}}},
        "lesson_plan": fx["lesson_plan"],
        "slide_briefs": fx["slide_briefs"],
        # Post-variant-filter roster: every slide_id retained, dispatch_variant "B".
        "gary_slide_output": _roster(fx["final_segment_ids"], variant="B"),
    }
    result = graph._attach_voice_direction(parsed, envelope)  # must NOT raise
    by_id = {d["id"]: d for d in result["segment_manifest_deltas"]}
    assert by_id["seg-02"]["slide_key"] == "2"
    assert by_id["seg-03"]["slide_key"] == "2"


# --------------------------------------------------------------------------- #
# M1 — absent slide_briefs RESOLVES via the deterministic roster+plan_units
# fallback (NOT a degrade-to-neutral): the grounding-asserted lesson_plan +
# gary_slide_output reconstruct the same source identity build_gary_briefs would.
# --------------------------------------------------------------------------- #
def test_absent_slide_briefs_resolves_via_roster_fallback(flag_on: None) -> None:
    fx = _fixture()
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": _deltas_for(fx["final_segment_ids"]),
    }
    envelope = {
        "role_derived_voice_by_slide": {"by_slide": {"2": {"emotional_tone": "warm",
                                                           "pace": "neutral", "energy": "high"}}},
        "lesson_plan": fx["lesson_plan"],
        # NO slide_briefs key at all.
        "gary_slide_output": _roster(fx["final_segment_ids"]),
    }
    result = graph._attach_voice_direction(parsed, envelope)  # must NOT raise
    by_id = {d["id"]: d for d in result["segment_manifest_deltas"]}
    # Same source identity as the slide_briefs path.
    for delta in result["segment_manifest_deltas"]:
        assert delta["slide_key"] == fx["expected_slide_key_by_final"][delta["slide_id"]]
    # And the seed still fires for source slide 2's sub-slides.
    for seg in ("seg-02", "seg-03", "seg-04"):
        assert by_id[seg]["voice_direction"]["source"] == "role-derived"


# --------------------------------------------------------------------------- #
# S1 — an interstitial with a missing/dangling parent_slide_id must FAIL LOUD
# (never silently parse its OWN id "slide-2-i1" -> "1", the exact mis-seed this
# story exists to kill).
# --------------------------------------------------------------------------- #
def test_interstitial_without_parent_fails_loud(flag_on: None) -> None:
    # Un-normalized: an interstitial that never got a parent_slide_id from
    # normalize_clusters (invariant violation).
    lesson_plan = {
        "plan_units": [
            {"unit_id": "slide-2", "cluster_id": "c-u02", "cluster_role": "head"},
            {"unit_id": "slide-2-i1", "cluster_id": "c-u02", "cluster_role": "interstitial"},
        ]
    }
    slide_briefs = [
        {"slide_id": "slide-01", "source_ref": "slide-2"},
        {"slide_id": "slide-02", "source_ref": "slide-2-i1"},
    ]
    parsed = {
        "narration_script": "x",
        "segment_manifest_deltas": _deltas_for(["slide-01", "slide-02"]),
    }
    envelope = {
        "role_derived_voice_by_slide": {"by_slide": {"2": {"pace": "neutral"}}},
        "lesson_plan": lesson_plan,
        "slide_briefs": slide_briefs,
        "gary_slide_output": _roster(["slide-01", "slide-02"]),
    }
    with pytest.raises(VoiceDirectionError):
        graph._attach_voice_direction(parsed, envelope)


def test_source_slide_key_by_final_raises_on_parentless_interstitial() -> None:
    # Unit-level: the map builder itself fails loud (never mis-keys "slide-2-i1"->"1").
    lesson_plan = {
        "plan_units": [
            {"unit_id": "slide-2-i1", "cluster_id": "c-u02", "cluster_role": "interstitial"},
        ]
    }
    slide_briefs = [{"slide_id": "slide-02", "source_ref": "slide-2-i1"}]
    with pytest.raises(VoiceDirectionError):
        graph._source_slide_key_by_final(lesson_plan, slide_briefs)


# --------------------------------------------------------------------------- #
# AC-A4 — stability across re-clustering: the same SOURCE slide -> same slide_key
# even when the clustering (and therefore the FINAL ordinals) changes.
# --------------------------------------------------------------------------- #
def test_slide_key_stable_across_reclustering() -> None:
    fx = _fixture()
    run_a = graph._source_slide_key_by_final(fx["lesson_plan"], fx["slide_briefs"])

    # Run B: source slide 3 re-clustered with ONE interstitial instead of three,
    # and source slide 2 with zero -> the FINAL ordinals shift, the source
    # identity does not.
    plan_b = {
        "plan_units": [
            {"unit_id": "slide-1", "cluster_id": "c-u01", "cluster_role": "head"},
            {"unit_id": "slide-2", "cluster_id": "c-u02", "cluster_role": "head"},
            {"unit_id": "slide-3", "cluster_id": "c-u03", "cluster_role": "head"},
            {
                "unit_id": "slide-3-i1",
                "cluster_id": "c-u03",
                "cluster_role": "interstitial",
                "parent_slide_id": "slide-3",
            },
            {"unit_id": "slide-4", "cluster_id": "c-u04", "cluster_role": "head"},
            {"unit_id": "slide-5", "cluster_id": "c-u05", "cluster_role": "head"},
            {"unit_id": "slide-6", "cluster_id": "c-u06", "cluster_role": "head"},
        ]
    }
    briefs_b = [
        {"slide_id": "slide-01", "source_ref": "slide-1"},
        {"slide_id": "slide-02", "source_ref": "slide-2"},
        {"slide_id": "slide-03", "source_ref": "slide-3"},
        {"slide_id": "slide-04", "source_ref": "slide-3-i1"},
        {"slide_id": "slide-05", "source_ref": "slide-4"},
        {"slide_id": "slide-06", "source_ref": "slide-5"},
        {"slide_id": "slide-07", "source_ref": "slide-6"},
    ]
    run_b = graph._source_slide_key_by_final(plan_b, briefs_b)

    # Source slide 3 in run A surfaced at finals slide-05..slide-08 (key "3");
    # in run B it surfaces at slide-03/slide-04 (final ordinals 3,4) -- but the
    # slide_key is "3" in BOTH runs. The source identity is invariant.
    assert run_a["slide-05"] == "3"
    assert run_b["slide-03"] == "3"
    assert run_b["slide-04"] == "3"
    # Every final descended from source slide 3 carries key "3" in both runs.
    assert {run_a[s] for s in ("slide-05", "slide-06", "slide-07", "slide-08")} == {"3"}
    assert {run_b[s] for s in ("slide-03", "slide-04")} == {"3"}


# --------------------------------------------------------------------------- #
# MURAT condition (order-invariant, mutation-class) — the positional fallback's
# `slide-NN -> Nth in-scope unit` assumption is BLIND to a same-length,
# contiguous-ordinal RE-ORDERING. `_resolve_slide_key_map` cross-checks the two
# INDEPENDENT derivations (explicit slide_briefs.source_ref vs positional) and
# FAILS LOUD on any disagreement, so a future roster-construction change that
# breaks the order coupling trips a guard on every normal (briefs-present) run
# rather than silently mis-seeding a later briefs-absent run.
# --------------------------------------------------------------------------- #
def test_fallback_order_divergence_fails_loud() -> None:
    # Same count (2 units / 2 finals), same contiguous ordinals (1,2) — but the
    # slide_briefs source_ref order DIVERGES from the plan_units order: the
    # explicit carrier says final-01<-source-2 / final-02<-source-1, while the
    # positional fallback says final-01<-source-1 / final-02<-source-2.
    lesson_plan = {
        "plan_units": [
            {"unit_id": "slide-1", "cluster_role": "head"},
            {"unit_id": "slide-2", "cluster_role": "head"},
        ]
    }
    slide_briefs = [
        {"slide_id": "slide-01", "source_ref": "slide-2"},
        {"slide_id": "slide-02", "source_ref": "slide-1"},
    ]
    roster = ["slide-01", "slide-02"]
    with pytest.raises(VoiceDirectionError) as exc:
        graph._resolve_slide_key_map(lesson_plan, slide_briefs, roster)
    msg = str(exc.value)
    assert "slide-01" in msg and "slide-02" in msg  # both conflicting finals named


def test_resolve_slide_key_map_agrees_on_consistent_envelope() -> None:
    # The cross-check does NOT over-fire: on the real fixture the explicit carrier
    # and the positional fallback AGREE, so the map resolves identically.
    fx = _fixture()
    merged = graph._resolve_slide_key_map(
        fx["lesson_plan"], fx["slide_briefs"], fx["final_segment_ids"]
    )
    assert merged == fx["expected_slide_key_by_final"]
