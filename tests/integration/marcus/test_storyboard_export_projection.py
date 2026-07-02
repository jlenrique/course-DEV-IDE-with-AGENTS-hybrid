"""Projection unit pins for ``enrich_segments_for_export`` (carried-findings D-B).

The post-join EXPORT projection was extracted from
``_write_segment_manifest_for_b`` (mechanical, byte-neutral lift witnessed at
``_bmad-output/implementation-artifacts/evidence/carried-findings-b-witness-*``)
into a module-level pure function so the byte-stability oracle can compose
``yaml(project(join(...)))`` without forking the projection.

Anti-tautology discipline (Murat, D-B amendment 2): every expectation below is
HAND-WRITTEN — authored literals, never computed by calling the function under
test.
"""

from __future__ import annotations

from app.marcus.orchestrator.storyboard_publisher import enrich_segments_for_export


def test_delta_value_wins_verbatim() -> None:
    """(i) A delta cluster value that could NOT be derived from the segment
    appears verbatim in the projected row (copy-through, never re-derive)."""
    segments = [
        {"segment_id": "seg-1", "slide_id": "s1", "narration_text": "Opening."}
    ]
    deltas = [
        {
            "id": "seg-1",
            "cluster_id": "cl-alpha",
            "cluster_role": "tension-builder",
            "cluster_position": "2/3",
        }
    ]
    out = enrich_segments_for_export(segments, deltas, {"cl-alpha": "setup-payoff"})
    assert out is segments, "mutate-in-place-and-return contract"
    assert out[0] == {
        "segment_id": "seg-1",
        "slide_id": "s1",
        "narration_text": "Opening.",
        "cluster_id": "cl-alpha",
        "cluster_role": "tension-builder",
        "cluster_position": "2/3",
        "narrative_arc": "setup-payoff",
    }


def test_voice_direction_and_slide_key_present_branch() -> None:
    """(ii-present) delta carries voice_direction + slide_key -> both attach."""
    segments = [{"segment_id": "seg-1", "slide_id": "s1", "narration_text": "Hi."}]
    deltas = [
        {
            "id": "seg-1",
            "voice_direction": "warm, measured pace",
            "slide_key": "slide-key-07",
        }
    ]
    out = enrich_segments_for_export(segments, deltas, {})
    assert out[0] == {
        "segment_id": "seg-1",
        "slide_id": "s1",
        "narration_text": "Hi.",
        "cluster_id": None,
        "cluster_role": None,
        "cluster_position": None,
        "narrative_arc": None,
        "voice_direction": "warm, measured pace",
        "slide_key": "slide-key-07",
    }


def test_voice_direction_falsy_but_present_attaches_empty_string() -> None:
    """(ii-falsy-present) delta carries voice_direction="" -> the EMPTY STRING
    attaches (presence check is `is not None`, not truthiness). Documents the
    current copy-through semantics for the falsy-but-present cell."""
    segments = [{"segment_id": "seg-1", "slide_id": "s1", "narration_text": "Hi."}]
    deltas = [{"id": "seg-1", "voice_direction": ""}]
    out = enrich_segments_for_export(segments, deltas, {})
    assert out[0] == {
        "segment_id": "seg-1",
        "slide_id": "s1",
        "narration_text": "Hi.",
        "cluster_id": None,
        "cluster_role": None,
        "cluster_position": None,
        "narrative_arc": None,
        "voice_direction": "",
    }


def test_voice_direction_and_slide_key_absent_branch() -> None:
    """(ii-absent) delta carries neither -> the KEYS are absent, not None."""
    segments = [{"segment_id": "seg-1", "slide_id": "s1", "narration_text": "Hi."}]
    deltas = [{"id": "seg-1"}]
    out = enrich_segments_for_export(segments, deltas, {})
    assert out[0] == {
        "segment_id": "seg-1",
        "slide_id": "s1",
        "narration_text": "Hi.",
        "cluster_id": None,
        "cluster_role": None,
        "cluster_position": None,
        "narrative_arc": None,
    }
    assert "voice_direction" not in out[0]
    assert "slide_key" not in out[0]


def test_ambiguous_duplicate_delta_id_blocks_spend_critical_fields() -> None:
    """(iii) Edge-#4 guard: a duplicate delta id must NOT attach
    voice_direction / slide_key (spend-critical, cannot be attributed
    unambiguously); the cluster labels keep last-write-wins best-effort."""
    segments = [
        {"segment_id": "seg-dup", "slide_id": "s1", "narration_text": "Dup."}
    ]
    deltas = [
        {
            "id": "seg-dup",
            "cluster_id": "cl-1",
            "voice_direction": "first-voice",
            "slide_key": "key-1",
        },
        {
            "id": "seg-dup",
            "cluster_id": "cl-2",
            "voice_direction": "second-voice",
            "slide_key": "key-2",
        },
    ]
    out = enrich_segments_for_export(segments, deltas, {"cl-2": "arc-two"})
    assert out[0] == {
        "segment_id": "seg-dup",
        "slide_id": "s1",
        "narration_text": "Dup.",
        # last-write-wins best-effort for the non-spend-critical labels:
        "cluster_id": "cl-2",
        "cluster_role": None,
        "cluster_position": None,
        "narrative_arc": "arc-two",
    }
    assert "voice_direction" not in out[0]
    assert "slide_key" not in out[0]


def test_pre_era_pin_no_cluster_p5_vo_fields() -> None:
    """(iv) PRE-ERA PIN: segments + deltas with no cluster / P5 / vo fields
    -> cluster keys attached as None (unconditional) and NO
    voice_direction / slide_key keys. Exact dicts."""
    segments = [
        {
            "segment_id": "seg-1",
            "id": "seg-1",
            "slide_id": "s1",
            "narration_text": "Opening.",
            "timing_role": "head",
        },
        {
            "segment_id": "seg-2",
            "id": "seg-2",
            "slide_id": "s2",
            "narration_text": "Closing.",
            "timing_role": None,
        },
    ]
    deltas = [
        {"id": "seg-1", "visual_references": [{"perception_source": "s1"}]},
        {"id": "seg-2", "visual_references": [{}, {"perception_source": "s2"}]},
    ]
    out = enrich_segments_for_export(segments, deltas, None)
    assert out == [
        {
            "segment_id": "seg-1",
            "id": "seg-1",
            "slide_id": "s1",
            "narration_text": "Opening.",
            "timing_role": "head",
            "cluster_id": None,
            "cluster_role": None,
            "cluster_position": None,
            "narrative_arc": None,
        },
        {
            "segment_id": "seg-2",
            "id": "seg-2",
            "slide_id": "s2",
            "narration_text": "Closing.",
            "timing_role": None,
            "cluster_id": None,
            "cluster_role": None,
            "cluster_position": None,
            "narrative_arc": None,
        },
    ]
