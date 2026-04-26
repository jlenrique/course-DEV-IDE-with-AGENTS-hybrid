"""Tests for image sensory bridge."""


import pytest

from skills.sensory_bridges.scripts.bridge_utils import validate_response
from skills.sensory_bridges.scripts.png_to_agent import analyze_image


class TestAnalyzeImage:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            analyze_image("/nonexistent/file.png")

    def test_schema_conformance_with_content(self, tmp_path):
        f = tmp_path / "slide.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(
            f,
            extracted_text="The Three Macro Trends",
            layout_description="Single column with title and three bullet points",
            visual_elements=[{"type": "icon", "description": "medical cross"}],
            slide_title="The Three Macro Trends",
            text_blocks=["The Three Macro Trends", "Digital transformation", "Workforce evolution"],
        )

        assert result["confidence"] == "HIGH"
        assert result["modality"] == "image"
        assert result["extracted_text"] == "The Three Macro Trends"
        assert len(result["visual_elements"]) == 1
        assert result["visual_complexity_level"] in {"low", "moderate", "high"}
        assert "visual complexity" in result["visual_complexity_summary"].lower()
        assert validate_response(result) == []

    def test_empty_extraction_gets_low_confidence(self, tmp_path):
        f = tmp_path / "blank.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(f)

        assert result["confidence"] == "LOW"
        assert "No text extracted" in result["confidence_rationale"]
        assert result["visual_complexity_level"] == "low"
        assert validate_response(result) == []

    def test_custom_confidence(self, tmp_path):
        f = tmp_path / "complex.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(
            f,
            extracted_text="Some text",
            confidence="MEDIUM",
            confidence_rationale="Complex diagram, partial text extraction",
        )

        assert result["confidence"] == "MEDIUM"
        assert "Complex diagram" in result["confidence_rationale"]

    def test_dense_slide_gets_high_complexity_summary(self, tmp_path):
        f = tmp_path / "dense.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(
            f,
            extracted_text=(
                "Stage 1, Stage 2, Stage 3, milestones, roadmap details, supporting copy, "
                "timing notes, and comparison language across multiple panels."
            ),
            layout_description="Two-column roadmap with timeline, comparison callouts, and stacked captions",
            visual_elements=[
                {"type": "roadmap", "description": "three-stage roadmap"},
                {"type": "timeline", "description": "month timeline"},
                {"type": "callout", "description": "supporting note"},
            ],
            text_blocks=["Stage 1", "Stage 2", "Stage 3", "Insight", "Design", "Impact"],
        )

        assert result["visual_complexity_level"] == "high"
        assert "slower orientation" in result["visual_complexity_summary"].lower()
