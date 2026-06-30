"""Step 0 pure core — slide_key reconciliation + anchor projection (offline).

``resolve_slide_key_map`` replicates the enhanced-vo.1 PRIMARY lineage
(``source_ref`` -> plan_units -> source-slide ordinal) ORCHESTRATOR-side (M3-clean:
no cross-import of ``app.specialists``). ``build_coverage_anchors`` is the PURE
reconciliation core (Amelia ruling — reconciliation passed IN, never computed from
run-state), so the adversarial joins are offline-testable. The only live seam is the
≤20-line marshalling adapter the orchestrator finalizes.
"""

from __future__ import annotations

from app.marcus.lesson_plan.coverage_receipt import AnchorResolution
from app.marcus.orchestrator.coverage_anchors import (
    build_coverage_anchors,
    resolve_slide_key_map,
)

# ---------------------------------------------------------------------------
# resolve_slide_key_map (PRIMARY source_ref->plan_units lineage, orchestrator-side)
# ---------------------------------------------------------------------------


def test_resolve_slide_key_map_primary_source_ref() -> None:
    plan_units = [
        {"unit_id": "slide-1"},
        {"unit_id": "slide-2"},
    ]
    slide_briefs = [
        {"slide_id": "slide-01", "source_ref": "slide-1"},
        {"slide_id": "slide-02", "source_ref": "slide-2"},
    ]
    assert resolve_slide_key_map(plan_units, slide_briefs) == {
        "slide-01": "1",
        "slide-02": "2",
    }


def test_resolve_slide_key_map_clustered_sub_slides_share_source_key() -> None:
    # N final sub-slides of one clustered source slide share the source slide_key.
    plan_units = [{"unit_id": "slide-2"}, {"unit_id": "slide-2-i1", "cluster_role": "interstitial",
                                          "parent_slide_id": "slide-2"}]
    slide_briefs = [
        {"slide_id": "slide-05", "source_ref": "slide-2"},
        {"slide_id": "slide-06", "source_ref": "slide-2-i1"},
    ]
    assert resolve_slide_key_map(plan_units, slide_briefs) == {
        "slide-05": "2",
        "slide-06": "2",  # interstitial borrows its head's source ordinal
    }


def test_resolve_slide_key_map_drift_omitted_first_wins() -> None:
    plan_units = [{"unit_id": "slide-1"}]
    slide_briefs = [
        {"slide_id": "slide-01", "source_ref": "slide-1"},
        {"slide_id": "slide-02", "source_ref": "slide-9"},  # drift: not in plan -> omitted
        {"slide_id": "slide-01", "source_ref": "slide-1"},  # dup final -> first wins
    ]
    assert resolve_slide_key_map(plan_units, slide_briefs) == {"slide-01": "1"}


def test_resolve_slide_key_map_empty_inputs() -> None:
    assert resolve_slide_key_map([], []) == {}
    assert resolve_slide_key_map(None, None) == {}


# ---------------------------------------------------------------------------
# build_coverage_anchors (PURE; adversarial joins)
# ---------------------------------------------------------------------------


def test_build_anchors_happy_path_both_surfaces() -> None:
    gary = [{"slide_index": 1, "title": "Trends", "body": "Dose is 5 mg daily."}]
    narration = [{"slide_key": "Slide 1", "narration_text": "Remember the 5 mg ceiling."}]
    slide_key_map = {"1": "Slide 1"}  # deck slide_index -> coverage slide_key
    anchors = build_coverage_anchors(gary, narration, slide_key_map, set())
    assert set(anchors) == {"Slide 1"}
    a = anchors["Slide 1"]
    assert isinstance(a, AnchorResolution)
    assert a.slide_present is True
    assert a.slide_text == "Trends\nDose is 5 mg daily."
    assert a.narration_present is True
    assert a.narration_text == "Remember the 5 mg ceiling."
    assert a.narration_ambiguous is False


def test_build_anchors_off_by_one_misjoin_is_faithful_to_passed_map() -> None:
    # 0-based vs 1-based: a shifted slide_key_map mis-keys the deck surface. The PURE
    # function faithfully applies the passed reconciliation (the off-by-one shows up as
    # the deck text landing on the WRONG coverage slide_key) — the bug surfaces in the
    # map, never silently swallowed here.
    gary = [{"slide_index": 0, "title": "A", "body": "a"},
            {"slide_index": 1, "title": "B", "body": "b"}]
    good = {"0": "Slide 1", "1": "Slide 2"}
    shifted = {"0": "Slide 2", "1": "Slide 3"}  # off-by-one
    assert build_coverage_anchors(gary, [], good, set())["Slide 1"].slide_text == "A\na"
    misjoined = build_coverage_anchors(gary, [], shifted, set())
    assert "Slide 1" not in misjoined  # the off-by-one is visible, not hidden
    assert misjoined["Slide 2"].slide_text == "A\na"


def test_build_anchors_missing_slide_key_narration_falls_back_to_slide_id() -> None:
    # flag-OFF case: a narration row without slide_key falls back to slide_id.
    narration = [{"slide_id": "Slide 7", "narration_text": "spoken"}]
    anchors = build_coverage_anchors([], narration, {}, set())
    assert anchors["Slide 7"].narration_present is True
    assert anchors["Slide 7"].narration_text == "spoken"


def test_build_anchors_ambiguous_ordinal_collision_flagged() -> None:
    narration = [{"slide_key": "Slide 3", "narration_text": "one"}]
    anchors = build_coverage_anchors([], narration, {}, {"Slide 3"})
    assert anchors["Slide 3"].narration_ambiguous is True


def test_build_anchors_deck_row_unresolved_in_map_is_skipped() -> None:
    gary = [{"slide_index": 9, "title": "orphan", "body": "x"}]
    anchors = build_coverage_anchors(gary, [], {"1": "Slide 1"}, set())
    assert anchors == {}  # no slide_key for slide_index 9 -> not anchored (caller diagnoses)


def test_build_anchors_empty_inputs() -> None:
    assert build_coverage_anchors([], [], {}, set()) == {}


# ---------------------------------------------------------------------------
# SF1 — clustered sub-slide text UNION (false-BLOCK that mutes the gate)
# ---------------------------------------------------------------------------


def test_build_anchors_unions_clustered_subslide_slide_text() -> None:
    # Two FINAL sub-slides share ONE source ordinal (clustered deck). A span on the
    # FIRST sub-slide must NOT be lost to last-write-wins (which kept only the LAST
    # sub-slide's text -> spurious `missing` -> false-BLOCK on a legit clustered deck).
    deck = [
        {"slide_id": "slide-01", "title": "", "body": "alpha span on first sub-slide"},
        {"slide_id": "slide-02", "title": "", "body": "beta span on second sub-slide"},
    ]
    key_map = {"slide-01": "1", "slide-02": "1"}  # both share ordinal 1 (clustered)
    anchors = build_coverage_anchors(deck, [], key_map, set())
    text = anchors["1"].slide_text or ""
    assert "alpha span" in text  # the EARLIER sub-slide's text is retained
    assert "beta span" in text  # AND the later one (union, not last-write-wins)


def test_build_anchors_unions_clustered_subslide_narration_text() -> None:
    narration = [
        {"slide_key": "1", "narration_text": "spoken on first sub-slide"},
        {"slide_key": "1", "narration_text": "spoken on second sub-slide"},
    ]
    anchors = build_coverage_anchors([], narration, {}, set())
    text = anchors["1"].narration_text or ""
    assert "first sub-slide" in text and "second sub-slide" in text
