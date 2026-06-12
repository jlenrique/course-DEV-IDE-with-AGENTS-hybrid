"""Narration-join shared-substrate pins (audio-arc, 2026-06-12).

Winston REQUIRE: the join policy ("slide_id = first non-empty
perception_source; narration_text by segment id") lives in EXACTLY ONE
module, and the publisher/enrique/G5 consumers all route through it —
import-identity pinned so a fourth private join cannot reappear.
"""

from __future__ import annotations

import inspect

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
    assert join_narration_segments([], DELTAS) == [
        {**row, "narration_text": ""} for row in join_narration_segments([], DELTAS)
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
    assert "narration_join import join_narration_segments" in source
    # No consumer re-implements the policy locally (docstrings may MENTION
    # perception_source; code must not READ it).
    for module in (storyboard_publisher, enrique_act):
        body = inspect.getsource(module)
        assert 'get("perception_source")' not in body, (
            f"{module.__name__} re-implements the slide-id join policy"
        )


def test_publisher_segment_manifest_byte_stable_through_shared_join(tmp_path) -> None:
    """Amelia REQUIRE: the publisher's B segment-manifest output through the
    shared helper carries the same rows the private join produced."""
    from app.marcus.orchestrator.storyboard_publisher import (
        _write_segment_manifest_for_b,
    )

    path = _write_segment_manifest_for_b(
        run_dir=tmp_path,
        irene_output={
            "narration_script": NARRATION,
            "segment_manifest_deltas": DELTAS,
        },
    )
    text = path.read_text(encoding="utf-8")
    assert "slide_id: s1" in text
    assert "slide_id: s2" in text
    assert "Opening." in text and "Closing." in text
    assert "seg-x" not in text
