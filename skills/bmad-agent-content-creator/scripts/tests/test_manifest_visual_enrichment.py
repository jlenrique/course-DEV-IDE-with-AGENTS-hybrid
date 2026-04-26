# /// script
# requires-python = ">=3.10"
# ///
"""Tests for segment manifest visual reference enrichment (Story 13.3).

Covers acceptance criteria:
  AC1-5: visual_references[] added to segments with correct fields
  AC6: Vera G4 traceability (via validate_manifest_visual_references)
  AC7: Quinn-R flagging (via validate_manifest_visual_references warnings)
  AC8: Compositor assembly cues (reference update, not code test)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.bmad_agent_content_creator.scripts.manifest_visual_enrichment import (
    apply_motion_plan_to_segments,
    enrich_manifest,
    enrich_segment_with_visual_references,
    validate_manifest_motion_fields,
    validate_manifest_visual_references,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_segment(seg_id: str, gary_slide_id: str = "") -> dict:
    return {
        "id": seg_id,
        "gary_slide_id": gary_slide_id,
        "gary_card_number": 1,
        "narration_text": "Sample narration text",
        "behavioral_intent": "credible",
    }


def _make_injection_result(
    slide_id: str = "s-1",
    n_refs: int = 2,
) -> dict:
    refs = []
    for i in range(n_refs):
        refs.append({
            "element": f"Element {i+1} on slide",
            "element_type": "chart",
            "location_on_slide": ["left panel", "center", "right panel"][i % 3],
            "perception_source_slide_id": slide_id,
            "perception_element_index": i,
        })
    return {
        "slide_id": slide_id,
        "card_number": 1,
        "visual_references": refs,
        "count_validation": {"valid": True},
    }


def _make_perception(card_number: int, n_elements: int = 3) -> dict:
    elements = []
    for i in range(n_elements):
        elements.append({
            "type": "chart",
            "description": f"Element {i+1} on slide",
            "position": ["left panel", "center", "right panel"][i % 3],
        })
    return {
        "slide_id": f"s-{card_number}",
        "card_number": card_number,
        "visual_elements": elements,
    }


# ===========================================================================
# AC1-5: Segment enrichment
# ===========================================================================

class TestEnrichSegmentWithVisualReferences:

    def test_adds_visual_references_field(self):
        segment = _make_segment("seg-01", "s-1")
        injection = _make_injection_result("s-1", n_refs=2)

        result = enrich_segment_with_visual_references(segment, injection)

        assert "visual_references" in result
        assert len(result["visual_references"]) == 2

    def test_reference_has_required_fields(self):
        segment = _make_segment("seg-01", "s-1")
        injection = _make_injection_result("s-1", n_refs=1)

        result = enrich_segment_with_visual_references(
            segment, injection, narration_cues=["As you can see in the chart"],
        )

        ref = result["visual_references"][0]
        assert ref["element"] == "Element 1 on slide"
        assert ref["location_on_slide"] == "left panel"
        assert ref["narration_cue"] == "As you can see in the chart"
        assert ref["perception_source"] == "s-1"

    def test_default_empty_narration_cue(self):
        segment = _make_segment("seg-01", "s-1")
        injection = _make_injection_result("s-1", n_refs=1)

        result = enrich_segment_with_visual_references(segment, injection)

        assert result["visual_references"][0]["narration_cue"] == ""

    def test_preserves_existing_segment_fields(self):
        segment = _make_segment("seg-01", "s-1")
        segment["narration_text"] = "Original text"
        injection = _make_injection_result("s-1", n_refs=1)

        result = enrich_segment_with_visual_references(segment, injection)

        assert result["narration_text"] == "Original text"
        assert result["id"] == "seg-01"


# ===========================================================================
# Bulk enrichment
# ===========================================================================

class TestEnrichManifest:

    def test_enriches_all_segments(self):
        segments = [
            _make_segment("seg-01", "s-1"),
            _make_segment("seg-02", "s-2"),
        ]
        injections = [
            _make_injection_result("s-1", n_refs=2),
            _make_injection_result("s-2", n_refs=2),
        ]

        result = enrich_manifest(segments, injections)

        assert len(result) == 2
        assert len(result[0]["visual_references"]) == 2
        assert len(result[1]["visual_references"]) == 2

    def test_matches_by_gary_slide_id(self):
        segments = [_make_segment("seg-01", "s-alpha")]
        injections = [_make_injection_result("s-alpha", n_refs=1)]

        result = enrich_manifest(segments, injections)

        assert result[0]["visual_references"][0]["perception_source"] == "s-alpha"

    def test_falls_back_to_index_matching(self):
        segments = [_make_segment("seg-01")]  # no gary_slide_id
        injections = [_make_injection_result("s-1", n_refs=1)]

        result = enrich_manifest(segments, injections)

        assert len(result[0]["visual_references"]) == 1

    def test_empty_references_when_no_matching_injection(self):
        segments = [_make_segment("seg-01", "s-999")]
        injections = [_make_injection_result("s-1", n_refs=2)]

        result = enrich_manifest(segments, injections)

        assert result[0]["visual_references"] == []

    def test_narration_cues_passed_through(self):
        segments = [_make_segment("seg-01", "s-1")]
        injections = [_make_injection_result("s-1", n_refs=2)]
        cues = {"seg-01": ["Look at the chart on the left", "Notice the trend line"]}

        result = enrich_manifest(segments, injections, narration_cues_by_segment=cues)

        assert result[0]["visual_references"][0]["narration_cue"] == "Look at the chart on the left"
        assert result[0]["visual_references"][1]["narration_cue"] == "Notice the trend line"

    def test_more_segments_than_injections(self):
        segments = [_make_segment("seg-01", "s-1"), _make_segment("seg-02", "s-2")]
        injections = [_make_injection_result("s-1", n_refs=1)]

        result = enrich_manifest(segments, injections)

        assert len(result[0]["visual_references"]) == 1
        assert result[1]["visual_references"] == []


# ===========================================================================
# AC6-7: Traceability validation (Vera G4 + Quinn-R)
# ===========================================================================

class TestValidateManifestVisualReferences:

    def test_valid_when_all_traceable(self):
        segments = [_make_segment("seg-01")]
        segments[0]["narration_text"] = "As shown in the chart, the comparison is clear."
        segments[0]["visual_references"] = [
            {
                "element": "Element 1 on slide",
                "location_on_slide": "left panel",
                "narration_cue": "As shown in the chart",
                "perception_source": "s-1",
            }
        ]
        perceptions = [_make_perception(1, n_elements=3)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_error_when_perception_source_missing(self):
        segments = [_make_segment("seg-01")]
        segments[0]["narration_text"] = "text"
        segments[0]["visual_references"] = [
            {
                "element": "Some element",
                "perception_source": "s-999",
                "narration_cue": "text",
            }
        ]
        perceptions = [_make_perception(1)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is False
        assert any("s-999" in e for e in result["errors"])

    def test_error_when_element_not_in_perception(self):
        segments = [_make_segment("seg-01")]
        segments[0]["narration_text"] = "text"
        segments[0]["visual_references"] = [
            {
                "element": "nonexistent element",
                "perception_source": "s-1",
                "narration_cue": "text",
            }
        ]
        perceptions = [_make_perception(1)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is False
        assert any("nonexistent element" in e for e in result["errors"])

    def test_warning_when_narration_cue_empty(self):
        segments = [_make_segment("seg-01")]
        segments[0]["visual_references"] = [
            {
                "element": "Element 1 on slide",
                "perception_source": "s-1",
                "narration_cue": "",
            }
        ]
        perceptions = [_make_perception(1)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is True  # warnings don't fail validation
        assert len(result["warnings"]) == 1

    def test_multiple_segments_multiple_references(self):
        segments = [_make_segment("seg-01"), _make_segment("seg-02")]
        segments[0]["narration_text"] = "a"
        segments[1]["narration_text"] = "b"
        segments[0]["visual_references"] = [
            {"element": "Element 1 on slide", "perception_source": "s-1", "narration_cue": "a"},
        ]
        segments[1]["visual_references"] = [
            {"element": "Element 1 on slide", "perception_source": "s-2", "narration_cue": "b"},
        ]
        perceptions = [_make_perception(1), _make_perception(2)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is True

    def test_segments_without_visual_references_ok(self):
        segments = [_make_segment("seg-01")]  # no visual_references key
        perceptions = [_make_perception(1)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is True

    def test_non_dict_perceptions_skipped(self):
        segments = [_make_segment("seg-01")]
        segments[0]["narration_text"] = "x"
        segments[0]["visual_references"] = [
            {"element": "Element 1 on slide", "perception_source": "s-1", "narration_cue": "x"},
        ]
        perceptions = [_make_perception(1), "not-a-dict", None]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is True

    def test_error_when_narration_cue_not_in_segment_text(self):
        segments = [_make_segment("seg-01")]
        segments[0]["narration_text"] = "Completely different text"
        segments[0]["visual_references"] = [
            {
                "element": "Element 1 on slide",
                "perception_source": "s-1",
                "narration_cue": "Look at the chart",
            }
        ]
        perceptions = [_make_perception(1)]

        result = validate_manifest_visual_references(segments, perceptions)

        assert result["valid"] is False
        assert any("narration_cue" in error for error in result["errors"])


class TestMotionManifestFields:

    def test_apply_motion_plan_defaults_static_when_no_assignment(self):
        segments = [_make_segment("seg-01", "s-1")]

        result = apply_motion_plan_to_segments(segments, {"slides": []})

        assert result[0]["motion_type"] == "static"
        assert result[0]["motion_asset_path"] is None
        assert result[0]["motion_source"] is None
        assert result[0]["motion_status"] is None

    def test_apply_motion_plan_fails_closed_when_motion_enabled_plan_is_empty(self):
        segments = [_make_segment("seg-01", "s-1")]

        with pytest.raises(ValueError, match="motion_enabled runs require motion_plan slide coverage"):
            apply_motion_plan_to_segments(
                segments,
                {"motion_enabled": True, "slides": []},
            )

    def test_apply_motion_plan_fails_closed_when_motion_enabled_plan_is_partial(self):
        segments = [
            _make_segment("seg-01", "s-1"),
            _make_segment("seg-02", "s-2"),
        ]
        motion_plan = {
            "motion_enabled": True,
            "slides": [
                {
                    "slide_id": "s-1",
                    "motion_type": "video",
                    "motion_asset_path": "course-content/staging/L1/motion/s-1_motion.mp4",
                    "motion_source": "kling",
                    "motion_duration_seconds": 6.5,
                    "motion_brief": "Animate the bar chart growth",
                    "motion_status": "approved",
                }
            ],
        }

        with pytest.raises(ValueError, match="motion_plan is missing Gate 2M assignments"):
            apply_motion_plan_to_segments(segments, motion_plan)

    def test_apply_motion_plan_hydrates_video_assignment(self):
        segments = [_make_segment("seg-01", "s-1")]
        motion_plan = {
            "slides": [
                {
                    "slide_id": "s-1",
                    "motion_type": "video",
                    "motion_asset_path": "course-content/staging/L1/motion/s-1_motion.mp4",
                    "motion_source": "kling",
                    "motion_duration_seconds": 6.5,
                    "motion_brief": "Animate the bar chart growth",
                    "motion_status": "approved",
                }
            ]
        }

        result = apply_motion_plan_to_segments(segments, motion_plan)

        assert result[0]["motion_type"] == "video"
        assert result[0]["motion_asset_path"].endswith("s-1_motion.mp4")
        assert result[0]["motion_source"] == "kling"
        assert result[0]["motion_duration_seconds"] == 6.5
        assert result[0]["motion_status"] == "approved"

    def test_validate_manifest_motion_fields_accepts_static_segments(self):
        segments = [_make_segment("seg-01", "s-1")]
        result = validate_manifest_motion_fields(segments)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_manifest_motion_fields_accepts_animation_segments(self):
        segments = [_make_segment("seg-01", "s-1")]
        segments[0].update(
            {
                "motion_type": "animation",
                "motion_asset_path": "course-content/staging/L1/motion/s-1_motion.mov",
                "motion_source": "manual",
                "motion_duration_seconds": 8.0,
                "motion_brief": "Pulse labels in sequence",
                "motion_status": "approved",
            }
        )

        result = validate_manifest_motion_fields(segments)

        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_manifest_motion_fields_fails_closed_without_asset_path(self):
        segments = [_make_segment("seg-01", "s-1")]
        segments[0].update(
            {
                "motion_type": "video",
                "motion_asset_path": None,
                "motion_source": "kling",
                "motion_status": "generated",
            }
        )

        result = validate_manifest_motion_fields(segments)

        assert result["valid"] is False
        assert any("motion_asset_path" in error for error in result["errors"])
