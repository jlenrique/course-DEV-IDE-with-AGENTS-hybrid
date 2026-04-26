"""Tests for PDF sensory bridge."""

from unittest.mock import MagicMock, patch

import pytest

from skills.sensory_bridges.scripts.bridge_utils import validate_response
from skills.sensory_bridges.scripts.pdf_to_agent import extract_pdf


class TestExtractPdf:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            extract_pdf("/nonexistent/file.pdf")

    def test_corrupt_file(self, tmp_path):
        f = tmp_path / "corrupt.pdf"
        f.write_text("not a pdf")
        result = extract_pdf(f)
        assert result["confidence"] == "LOW"
        assert result["modality"] == "pdf"
        assert validate_response(result) == []

    @patch("skills.sensory_bridges.scripts.pdf_to_agent.PdfReader")
    def test_all_machine_readable(self, mock_reader_cls, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_bytes(b"\x00")

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is a full page of medical education content with plenty of text."

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page, mock_page]
        mock_reader_cls.return_value = mock_reader

        result = extract_pdf(f)
        assert result["confidence"] == "HIGH"
        assert result["total_pages"] == 2
        assert result["scanned_pages"] == 0
        assert all(not p["is_scanned"] for p in result["pages"])
        assert validate_response(result) == []

    @patch("skills.sensory_bridges.scripts.pdf_to_agent.PdfReader")
    def test_scanned_page_detection(self, mock_reader_cls, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_bytes(b"\x00")

        text_page = MagicMock()
        text_page.extract_text.return_value = "Full content with enough characters to pass threshold."

        scanned_page = MagicMock()
        scanned_page.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.pages = [text_page, scanned_page]
        mock_reader_cls.return_value = mock_reader

        result = extract_pdf(f)
        assert result["confidence"] == "MEDIUM"
        assert result["scanned_pages"] == 1
        assert result["pages"][0]["is_scanned"] is False
        assert result["pages"][1]["is_scanned"] is True

    @patch("skills.sensory_bridges.scripts.pdf_to_agent.PdfReader")
    def test_all_scanned(self, mock_reader_cls, tmp_path):
        f = tmp_path / "test.pdf"
        f.write_bytes(b"\x00")

        scanned = MagicMock()
        scanned.extract_text.return_value = ""

        mock_reader = MagicMock()
        mock_reader.pages = [scanned, scanned]
        mock_reader_cls.return_value = mock_reader

        result = extract_pdf(f)
        assert result["confidence"] == "LOW"
        assert result["scanned_pages"] == 2
