"""Tests for PPTX sensory bridge."""

from unittest.mock import MagicMock, patch

import pytest

from skills.sensory_bridges.scripts.bridge_utils import validate_response
from skills.sensory_bridges.scripts.pptx_to_agent import extract_pptx


class TestExtractPptx:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            extract_pptx("/nonexistent/file.pptx")

    def test_corrupt_file(self, tmp_path):
        f = tmp_path / "corrupt.pptx"
        f.write_text("not a pptx file")
        result = extract_pptx(f)
        assert result["confidence"] == "LOW"
        assert result["modality"] == "pptx"
        assert result["total_slides"] == 0
        assert validate_response(result) == []

    def test_response_schema_conformance(self, tmp_path):
        """Even error responses must conform to the canonical schema."""
        f = tmp_path / "bad.pptx"
        f.write_text("garbage")
        result = extract_pptx(f)
        errors = validate_response(result)
        assert errors == [], f"Schema errors: {errors}"

    @patch("skills.sensory_bridges.scripts.pptx_to_agent.Presentation")
    def test_successful_extraction(self, mock_prs_cls, tmp_path):
        f = tmp_path / "test.pptx"
        f.write_bytes(b"\x00")

        mock_shape = MagicMock()
        mock_shape.has_text_frame = True
        mock_shape.shape_type = 1
        mock_para = MagicMock()
        mock_para.text = "Hello World"
        mock_shape.text_frame.paragraphs = [mock_para]

        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]
        mock_slide.has_notes_slide = False

        mock_prs = MagicMock()
        mock_prs.slides = [mock_slide]
        mock_prs_cls.return_value = mock_prs

        result = extract_pptx(f)

        assert result["confidence"] == "HIGH"
        assert result["total_slides"] == 1
        assert len(result["slides"]) == 1
        assert "Hello World" in result["slides"][0]["text_frames"]
        assert validate_response(result) == []

    @patch("skills.sensory_bridges.scripts.pptx_to_agent.Presentation")
    def test_slide_with_no_text(self, mock_prs_cls, tmp_path):
        f = tmp_path / "test.pptx"
        f.write_bytes(b"\x00")

        mock_shape = MagicMock()
        mock_shape.has_text_frame = False
        mock_shape.shape_type = 13  # picture
        mock_shape.image.content_type = "image/png"
        mock_shape.width = 100
        mock_shape.height = 100

        mock_slide = MagicMock()
        mock_slide.shapes = [mock_shape]
        mock_slide.has_notes_slide = False

        mock_prs = MagicMock()
        mock_prs.slides = [mock_slide]
        mock_prs_cls.return_value = mock_prs

        result = extract_pptx(f)
        assert result["confidence"] == "MEDIUM"
        assert result["total_slides"] == 1
