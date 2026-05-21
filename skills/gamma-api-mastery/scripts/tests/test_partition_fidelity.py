"""Tests for mixed-fidelity partition, reassembly, naming, and URL validation."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "gamma_operations", SCRIPTS_DIR / "gamma_operations.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules["gamma_operations"] = mod
spec.loader.exec_module(mod)

partition_by_fidelity = mod.partition_by_fidelity
build_doc_title = mod.build_doc_title
reassemble_slide_output = mod.reassemble_slide_output
validate_image_url = mod.validate_image_url


class TestPartitionByFidelity:
    def test_all_creative(self) -> None:
        slides = [
            {"slide_number": 1, "content": "A", "fidelity": "creative"},
            {"slide_number": 2, "content": "B", "fidelity": "creative"},
        ]
        result = partition_by_fidelity(slides)
        assert len(result["creative"]) == 2
        assert len(result["literal-text"]) == 0
        assert len(result["literal-visual"]) == 0

    def test_all_literal(self) -> None:
        slides = [
            {"slide_number": 1, "content": "A", "fidelity": "literal-text"},
            {"slide_number": 2, "content": "B", "fidelity": "literal-visual"},
        ]
        result = partition_by_fidelity(slides)
        assert len(result["creative"]) == 0
        assert len(result["literal-text"]) == 1
        assert len(result["literal-visual"]) == 1

    def test_mixed(self) -> None:
        slides = [
            {"slide_number": 1, "fidelity": "creative"},
            {"slide_number": 2, "fidelity": "literal-text"},
            {"slide_number": 3, "fidelity": "creative"},
            {"slide_number": 4, "fidelity": "literal-visual"},
        ]
        result = partition_by_fidelity(slides)
        assert len(result["creative"]) == 2
        assert len(result["literal-text"]) == 1
        assert len(result["literal-visual"]) == 1
        assert result["creative"][0]["slide_number"] == 1
        assert result["literal-text"][0]["slide_number"] == 2
        assert result["literal-visual"][0]["slide_number"] == 4

    def test_default_fidelity_is_creative(self) -> None:
        slides = [{"slide_number": 1, "content": "A"}]
        result = partition_by_fidelity(slides)
        assert len(result["creative"]) == 1
        assert len(result["literal-text"]) == 0
        assert len(result["literal-visual"]) == 0


class TestBuildDocTitle:
    def test_single_slide(self) -> None:
        title = build_doc_title("C1-M1-P2-Macro-Trends", "literal", [10])
        assert title == "C1-M1-P2-Macro-Trends_literal_s10"

    def test_range(self) -> None:
        title = build_doc_title("C1-M1-P2-Macro-Trends", "creative", [1, 2, 3, 9])
        assert title == "C1-M1-P2-Macro-Trends_creative_s01-s09"

    def test_zero_padded(self) -> None:
        title = build_doc_title("C1-M1-P2", "literal-text", [3, 7])
        assert title == "C1-M1-P2_literal-text_s03-s07"


class TestReassembleSlideOutput:
    def test_merged_order(self) -> None:
        creative = [
            {"card_number": 1, "slide_id": "test-card-01", "file_path": "c1.png"},
            {"card_number": 3, "slide_id": "test-card-03", "file_path": "c3.png"},
        ]
        literal = [
            {"card_number": 2, "slide_id": "test-card-02", "file_path": "l2.png", "fidelity": "literal-text"},
        ]
        result = reassemble_slide_output(creative, literal)
        assert len(result) == 3
        assert result[0]["card_number"] == 1
        assert result[0]["source_call"] == "creative"
        assert result[0]["slide_id"] == "test-card-01"
        assert result[1]["card_number"] == 2
        assert result[1]["source_call"] == "literal-text"
        assert result[2]["card_number"] == 3

    def test_empty_literal(self) -> None:
        creative = [{"card_number": 1, "slide_id": "test-card-01", "file_path": "c1.png"}]
        result = reassemble_slide_output(creative, [])
        assert len(result) == 1
        assert result[0]["source_call"] == "creative"


class TestValidateImageUrl:
    def test_non_https(self) -> None:
        valid, reason = validate_image_url("http://example.com/img.png")
        assert not valid
        assert "HTTPS" in reason

    @patch("gamma_operations.requests.head")
    def test_valid_url(self, mock_head: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "image/png"}
        mock_head.return_value = mock_resp

        valid, reason = validate_image_url("https://example.com/img.png")
        assert valid
        assert reason == "OK"

    @patch("gamma_operations.requests.head")
    def test_404(self, mock_head: MagicMock) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.headers = {}
        mock_head.return_value = mock_resp

        valid, reason = validate_image_url("https://example.com/img.png")
        assert not valid
        assert "404" in reason
