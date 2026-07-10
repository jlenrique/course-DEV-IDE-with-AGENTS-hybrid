"""Narration-join shared-substrate pins (audio-arc, 2026-06-12).

Winston REQUIRE: the join policy ("slide_id = first non-empty
perception_source; narration_text by segment id") lives in EXACTLY ONE
module, and the publisher/enrique/G5 consumers all route through it —
import-identity pinned so a fourth private join cannot reappear.
"""

from __future__ import annotations

import inspect

import yaml

from app.specialists.narration_join import join_narration_segments

NARRATION = [
    {"id": "seg-1", "narration_text": "Opening."},
    {"id": "seg-2", "narration_text": "Closing."},
]
DELTAS = [
    {"id": "seg-1", "visual_references": [{"perception_source": "s1"}], "timing_role": "head"},
    {"id": "seg-2", "visual_references": [{}, {"perception_source": "s2"}]},
    {"id": "seg-x", "visual_references": []},  # no slide ref → dropped
]


def test_join_policy() -> None:
    rows = join_narration_segments(NARRATION, DELTAS)
    assert [(r["segment_id"], r["slide_id"], r["narration_text"]) for r in rows] == [
        ("seg-1", "s1", "Opening."),
        ("seg-2", "s2", "Closing."),
    ]
    assert rows[0]["timing_role"] == "head"
    assert join_narration_segments(None, None) == []
    # Winston R1 (dp-v1.2 rider): explicit expectation — the prior form
    # re-derived its expectation from the call under test (only the
    # empty-text field was falsifiable).
    empty_script_rows = join_narration_segments([], DELTAS)
    assert [
        (r["segment_id"], r["slide_id"], r["narration_text"]) for r in empty_script_rows
    ] == [
        ("seg-1", "s1", ""),
        ("seg-2", "s2", ""),
    ]


def test_consumers_import_the_one_join() -> None:
    """Import-identity: each consumer's module references the shared
    function object, and none re-implements the first-reference policy."""
    from app.marcus.orchestrator import storyboard_publisher
    from app.specialists.enrique import _act as enrique_act
    from app.specialists.quinn_r import quality_control_dispatch as qcd

    assert storyboard_publisher.join_narration_segments is join_narration_segments
    assert enrique_act.join_narration_segments is join_narration_segments
    # G5 grounding imports inside the function (cycle-import hygiene) —
    # pin via source reference to the shared module.
    source = inspect.getsource(qcd.run_g5_grounding)
    assert "narration_join import" in source
    assert "join_narration_segments" in source
    # No consumer re-implements the policy locally (docstrings may MENTION
    # perception_source; code must not READ it).
    for module in (storyboard_publisher, enrique_act):
        body = inspect.getsource(module)
        assert 'get("perception_source")' not in body, (
            f"{module.__name__} re-implements the slide-id join policy"
        )


def test_phantom_detection_single_homed() -> None:
    """dp-v1.2 rider (Amelia R1): phantom detection (joined row with empty
    narration_text) lives in the shared module; enrique refuses pre-spend
    and G5 drops pre-coverage through the SAME helper — import-identity
    pinned like the join itself."""
    from app.specialists.narration_join import phantom_segment_ids

    rows = join_narration_segments([NARRATION[0]], DELTAS)
    assert phantom_segment_ids(rows) == ["seg-2"]
    assert phantom_segment_ids(join_narration_segments(NARRATION, DELTAS)) == []
    assert phantom_segment_ids([{"segment_id": "w", "narration_text": "   "}]) == ["w"]
    assert phantom_segment_ids(
        [{"segment_id": "d", "narration_text": ""}, {"id": "d", "narration_text": " "}]
    ) == ["d"]  # de-duplicated

    from app.specialists.enrique import _act as enrique_act
    from app.specialists.quinn_r import quality_control_dispatch as qcd

    assert enrique_act.phantom_segment_ids is phantom_segment_ids
    # Module-qualified pin (review patch): a private re-implementation or an
    # import from elsewhere must not satisfy this.
    g5_source = inspect.getsource(qcd.run_g5_grounding)
    assert "narration_join import" in g5_source
    assert "join_narration_segments" in g5_source
    assert "phantom_segment_ids" in g5_source
    assert "collapsed_segment_ids" in g5_source


def test_collapsed_segment_ids_detects_duplicate_join_keys() -> None:
    """Mine-next T3: duplicate delta ids flood distinct slides; detector surfaces them."""
    from app.specialists.narration_join import collapsed_segment_ids

    narration = [
        {"id": "seg-1", "narration_text": "First."},
        {"id": "seg-2", "narration_text": "Second."},
    ]
    deltas = [
        {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
        {"id": "seg-1", "visual_references": [{"perception_source": "s2"}]},
        {"id": "seg-2", "visual_references": [{"perception_source": "s3"}]},
    ]
    rows = join_narration_segments(narration, deltas)
    assert collapsed_segment_ids(rows) == ["seg-1"]
    assert collapsed_segment_ids(join_narration_segments(NARRATION, DELTAS)) == []


def test_collapsed_detector_imported_by_spend_consumers() -> None:
    from app.marcus.orchestrator import storyboard_publisher
    from app.specialists.enrique import _act as enrique_act
    from app.specialists.narration_join import collapsed_segment_ids

    assert enrique_act.collapsed_segment_ids is collapsed_segment_ids
    assert storyboard_publisher.collapsed_segment_ids is collapsed_segment_ids


def test_publisher_segment_manifest_byte_stable_through_shared_join(tmp_path) -> None:
    """Amelia REQUIRE: the publisher's B segment-manifest output through the
    shared helper carries the same rows the private join produced.

    Carried-findings D-B oracle repair (2026-07-02): since 1.3-carry the
    publisher applies a documented post-join EXPORT projection (cluster
    labels; P5 voice_direction; enhanced-vo.1 slide_key). The oracle is the
    same composition the writer performs — ``yaml(project(join(...)))`` via
    the extracted ``enrich_segments_for_export`` — plus HAND-WRITTEN literal
    anchors (Murat anti-tautology: byte-equality alone would move with a
    projection regression; the anchors are the independent content oracle).
    """
    from app.marcus.orchestrator.storyboard_publisher import (
        _write_segment_manifest_for_b,
        enrich_segments_for_export,
    )

    path = _write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output={
            "narration_script": NARRATION,
            "segment_manifest_deltas": DELTAS,
        },
    )
    # Winston R1 (dp-v1.2 rider): byte-equality against the canonical
    # serialization of the shared-join output THROUGH the export projection
    # (same composition as the writer; safe_dump kwargs pinned identical).
    text = path.read_text(encoding="utf-8")
    expected = yaml.safe_dump(
        {
            "segments": enrich_segments_for_export(
                join_narration_segments(NARRATION, DELTAS), DELTAS, {}
            )
        },
        sort_keys=False,
        allow_unicode=True,
    )
    assert text == expected
    assert "Opening." in text and "Closing." in text
    assert "slide_id: s1" in text and "slide_id: s2" in text
    assert "seg-x" not in text
    # Mandatory literal anchors — one per projected key family this fixture
    # carries (D-B amendment 2). DELTAS holds no cluster fields, so the
    # unconditional cluster keys project as explicit nulls:
    assert "cluster_id: null" in text
    assert "cluster_role: null" in text
    assert "cluster_position: null" in text
    assert "narrative_arc: null" in text
    # voice_direction / slide_key are conditional-on-presence and this
    # fixture carries neither -> the keys must be ABSENT (pre-era byte
    # discipline; the present-branch literals live in the projection unit
    # test tests/integration/marcus/test_storyboard_export_projection.py).
    assert "voice_direction" not in text
    assert "slide_key" not in text
