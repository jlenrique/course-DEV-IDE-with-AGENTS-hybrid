# /// script
# requires-python = ">=3.10"
# ///
"""Tests for visual reference injection (Story 13.2).

Covers all 7 acceptance criteria:
  AC1: visual_references_per_slide parameter controls count
  AC2: Narration includes target ±tolerance references
  AC3: Natural language integration (tested via metadata structure)
  AC4: Each reference grounded in perception_artifacts — traceable
  AC5: References complement, not duplicate (structural; content quality is agentic)
  AC6: Narration template updated with visual_references[] (template change, not code test)
  AC7: Unit tests validate count compliance and traceability
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.bmad_agent_content_creator.scripts.visual_reference_injector import (
    build_visual_reference_metadata,
    extract_visual_references,
    inject_all_slides,
    inject_visual_references,
    load_visual_reference_params,
    validate_reference_count,
    validate_references_traceable,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_perception(
    card_number: int,
    n_elements: int = 3,
    confidence: str = "HIGH",
) -> dict:
    elements = []
    positions = ["left panel", "center", "right panel", "top-right", "bottom"]
    types = ["chart", "table", "diagram", "image", "text block"]
    for i in range(n_elements):
        elements.append({
            "type": types[i % len(types)],
            "description": f"Element {i+1} on slide {card_number}",
            "position": positions[i % len(positions)],
        })
    return {
        "schema_version": "1.0",
        "modality": "image",
        "artifact_path": f"course-content/staging/card-{card_number:02d}.png",
        "confidence": confidence,
        "confidence_rationale": "Test perception",
        "perception_timestamp": "2026-04-05T12:00:00Z",
        "extracted_text": f"Text from slide {card_number}",
        "layout_description": "Two-column layout",
        "visual_elements": elements,
        "slide_title": f"Slide {card_number} Title",
        "text_blocks": [f"Block {card_number}"],
        "slide_id": f"s-{card_number}",
        "card_number": card_number,
        "source_image_path": f"course-content/staging/card-{card_number:02d}.png",
    }


def _make_sparse_perception(card_number: int) -> dict:
    """Perception with only 1 element (less than default target of 2)."""
    return _make_perception(card_number, n_elements=1)


def _make_empty_perception(card_number: int) -> dict:
    """Perception with zero visual elements."""
    return _make_perception(card_number, n_elements=0)


def _make_rich_perception(card_number: int) -> dict:
    """Perception with many elements (more than target)."""
    return _make_perception(card_number, n_elements=6)


# ===========================================================================
# AC1: Parameter loading
# ===========================================================================

class TestLoadVisualReferenceParams:

    def test_loads_from_real_config(self):
        params = load_visual_reference_params()
        assert params["target"] == 2
        assert params["tolerance"] == 1

    def test_defaults_when_file_missing(self, tmp_path):
        params = load_visual_reference_params(tmp_path / "nonexistent.yaml")
        assert params["target"] == 2
        assert params["tolerance"] == 1

    def test_loads_custom_values(self, tmp_path):
        config = tmp_path / "test-params.yaml"
        config.write_text(
            "visual_narration:\n"
            "  visual_references_per_slide: 3\n"
            "  visual_references_tolerance: 2\n",
            encoding="utf-8",
        )
        params = load_visual_reference_params(config)
        assert params["target"] == 3
        assert params["tolerance"] == 2


# ===========================================================================
# AC2: Reference count compliance (±tolerance)
# ===========================================================================

class TestExtractVisualReferences:

    def test_extracts_target_count(self):
        perception = _make_perception(1, n_elements=5)
        refs = extract_visual_references(perception, count=2)
        assert len(refs) == 2

    def test_extracts_fewer_when_not_enough_elements(self):
        perception = _make_perception(1, n_elements=1)
        refs = extract_visual_references(perception, count=2)
        assert len(refs) == 1

    def test_extracts_zero_from_empty_perception(self):
        perception = _make_empty_perception(1)
        refs = extract_visual_references(perception, count=2)
        assert len(refs) == 0

    def test_prioritizes_elements_with_position(self):
        perception = {
            "visual_elements": [
                {"type": "chart", "description": "A chart"},  # no position
                {"type": "table", "description": "A table with data", "position": "left"},
            ],
            "slide_id": "s-1",
        }
        refs = extract_visual_references(perception, count=1)
        assert refs[0].get("position") == "left"

    def test_handles_non_dict_elements(self):
        perception = {
            "visual_elements": [
                {"type": "chart", "description": "Valid", "position": "center"},
                "not-a-dict",
                None,
                {"type": "table", "description": "Also valid", "position": "right"},
            ],
            "slide_id": "s-1",
        }
        refs = extract_visual_references(perception, count=3)
        assert len(refs) == 2  # only the two valid dicts


class TestValidateReferenceCount:

    def test_exact_match_is_valid(self):
        refs = [{"element": "a"}, {"element": "b"}]
        result = validate_reference_count(refs, target=2, tolerance=1)
        assert result["valid"] is True
        assert result["deviation"] == 0

    def test_plus_one_within_tolerance(self):
        refs = [{"element": "a"}, {"element": "b"}, {"element": "c"}]
        result = validate_reference_count(refs, target=2, tolerance=1)
        assert result["valid"] is True
        assert result["deviation"] == 1

    def test_minus_one_within_tolerance(self):
        refs = [{"element": "a"}]
        result = validate_reference_count(refs, target=2, tolerance=1)
        assert result["valid"] is True
        assert result["deviation"] == -1

    def test_out_of_tolerance_above(self):
        refs = [{"element": "a"}, {"element": "b"}, {"element": "c"}, {"element": "d"}]
        result = validate_reference_count(refs, target=2, tolerance=1)
        assert result["valid"] is False
        assert result["deviation"] == 2

    def test_zero_references_out_of_tolerance(self):
        result = validate_reference_count([], target=2, tolerance=1)
        assert result["valid"] is False
        assert result["deviation"] == -2

    def test_zero_target_zero_refs_is_valid(self):
        result = validate_reference_count([], target=0, tolerance=0)
        assert result["valid"] is True


# ===========================================================================
# AC4: Traceability to perception artifacts
# ===========================================================================

class TestBuildVisualReferenceMetadata:

    def test_metadata_has_required_fields(self):
        perception = _make_perception(1, n_elements=3)
        refs = extract_visual_references(perception, count=2)
        metadata = build_visual_reference_metadata(refs, perception)

        assert len(metadata) == 2
        for m in metadata:
            assert "element" in m
            assert "element_type" in m
            assert "location_on_slide" in m
            assert "perception_source_slide_id" in m
            assert "perception_element_index" in m

    def test_metadata_links_to_correct_slide(self):
        perception = _make_perception(3, n_elements=2)
        refs = extract_visual_references(perception, count=2)
        metadata = build_visual_reference_metadata(refs, perception)

        for m in metadata:
            assert m["perception_source_slide_id"] == "s-3"


class TestValidateReferencesTraceable:

    def test_all_traceable(self):
        perception = _make_perception(1, n_elements=3)
        refs = extract_visual_references(perception, count=2)
        metadata = build_visual_reference_metadata(refs, perception)

        result = validate_references_traceable(metadata, [perception])
        assert result["traceable"] is True
        assert result["untraceable"] == []

    def test_untraceable_when_element_not_in_perception(self):
        perception = _make_perception(1, n_elements=2)
        fake_metadata = [
            {
                "element": "nonexistent chart",
                "perception_source_slide_id": "s-1",
            }
        ]

        result = validate_references_traceable(fake_metadata, [perception])
        assert result["traceable"] is False
        assert "nonexistent chart" in result["untraceable"]

    def test_traceable_across_multiple_slides(self):
        p1 = _make_perception(1, n_elements=2)
        p2 = _make_perception(2, n_elements=2)

        refs1 = extract_visual_references(p1, count=1)
        refs2 = extract_visual_references(p2, count=1)
        meta1 = build_visual_reference_metadata(refs1, p1)
        meta2 = build_visual_reference_metadata(refs2, p2)

        result = validate_references_traceable(meta1 + meta2, [p1, p2])
        assert result["traceable"] is True


# ===========================================================================
# AC7: Integration — inject_visual_references and inject_all_slides
# ===========================================================================

class TestInjectVisualReferences:

    def test_per_slide_result_structure(self):
        perception = _make_perception(1, n_elements=3)
        result = inject_visual_references(perception, target=2, tolerance=1)

        assert result["slide_id"] == "s-1"
        assert result["card_number"] == 1
        assert len(result["visual_references"]) == 2
        assert result["count_validation"]["valid"] is True

    def test_sparse_slide_within_tolerance(self):
        perception = _make_sparse_perception(1)
        result = inject_visual_references(perception, target=2, tolerance=1)

        assert len(result["visual_references"]) == 1
        assert result["count_validation"]["valid"] is True  # 1 is within ±1 of 2

    def test_empty_slide_out_of_tolerance(self):
        perception = _make_empty_perception(1)
        result = inject_visual_references(perception, target=2, tolerance=1)

        assert len(result["visual_references"]) == 0
        assert result["count_validation"]["valid"] is False


class TestInjectAllSlides:

    def test_all_compliant(self):
        artifacts = [_make_perception(i, n_elements=3) for i in range(1, 4)]
        result = inject_all_slides(artifacts)

        assert result["status"] == "compliant"
        assert result["compliance_summary"]["total_slides"] == 3
        assert result["compliance_summary"]["compliant"] == 3
        assert result["compliance_summary"]["non_compliant"] == 0
        assert result["traceability"]["traceable"] is True

    def test_mixed_compliance(self):
        artifacts = [
            _make_perception(1, n_elements=3),  # compliant
            _make_empty_perception(2),  # non-compliant (0 refs, target 2±1)
        ]
        result = inject_all_slides(artifacts)

        assert result["status"] == "non_compliant"
        assert result["compliance_summary"]["compliant"] == 1
        assert result["compliance_summary"]["non_compliant"] == 1

    def test_uses_config_params(self):
        artifacts = [_make_perception(1, n_elements=5)]
        result = inject_all_slides(artifacts)

        # Should use real config: target=2, tolerance=1
        assert result["params"]["target"] == 2
        assert result["params"]["tolerance"] == 1

    def test_custom_config_path(self, tmp_path):
        config = tmp_path / "custom.yaml"
        config.write_text(
            "visual_narration:\n"
            "  visual_references_per_slide: 4\n"
            "  visual_references_tolerance: 0\n",
            encoding="utf-8",
        )
        artifacts = [_make_perception(1, n_elements=5)]
        result = inject_all_slides(artifacts, config_path=config)

        assert result["params"]["target"] == 4
        assert len(result["slides"][0]["visual_references"]) == 4

    def test_empty_artifacts_list(self):
        result = inject_all_slides([])
        assert result["status"] == "compliant"
        assert result["compliance_summary"]["total_slides"] == 0

    def test_skips_non_dict_artifacts(self):
        artifacts = [_make_perception(1, n_elements=3), "not-a-dict", None]
        result = inject_all_slides(artifacts)
        assert result["compliance_summary"]["total_slides"] == 1
