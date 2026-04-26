"""Tests for Texas agent extraction_validator.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# Load module from skill path
_MOD_PATH = Path(__file__).resolve().parents[3] / "skills" / "bmad-agent-texas" / "scripts" / "extraction_validator.py"
_spec = importlib.util.spec_from_file_location("extraction_validator", _MOD_PATH)
ev = importlib.util.module_from_spec(_spec)
sys.modules["extraction_validator"] = ev
_spec.loader.exec_module(ev)

QualityTier = ev.QualityTier
validate_extraction = ev.validate_extraction


class TestQualityTierClassification:
    """Verify the four-tier quality classification."""

    def test_full_fidelity_from_adequate_extraction(self) -> None:
        text = "# Heading\n\n" + ("Word " * 5000) + "\n\n- List item\n\n## Another\n\nMore content."
        meta = {"source_type": "pdf", "pages_total": 24, "filename": "test.pdf"}
        result = validate_extraction(text, meta)
        assert result.tier == QualityTier.FULL_FIDELITY
        assert result.passed is True
        assert result.completeness_ratio > 0.8

    def test_failed_from_stub(self) -> None:
        text = "Course 1 Module 1\nSome headings"
        meta = {"source_type": "pdf", "pages_total": 24, "filename": "test.pdf"}
        result = validate_extraction(text, meta)
        assert result.tier == QualityTier.FAILED
        assert result.passed is False
        assert result.completeness_ratio < 0.2

    def test_degraded_from_partial(self) -> None:
        # 1200 words / 4800 expected = 25%, between 20-50% → DEGRADED
        text = "# Section 1\n\n" + ("Word " * 1200)
        meta = {"source_type": "pdf", "pages_total": 24, "filename": "test.pdf"}
        result = validate_extraction(text, meta)
        assert result.tier == QualityTier.DEGRADED
        assert 0.20 <= result.completeness_ratio < 0.50

    def test_adequate_with_gaps(self) -> None:
        text = ("Word " * 2500)  # ~52% of expected 4800
        meta = {"source_type": "pdf", "pages_total": 24, "filename": "test.pdf"}
        result = validate_extraction(text, meta)
        assert result.tier == QualityTier.ADEQUATE_WITH_GAPS
        assert result.passed is True

    def test_empty_extraction_fails(self) -> None:
        result = validate_extraction("", {"source_type": "pdf", "pages_total": 10})
        assert result.tier == QualityTier.FAILED
        assert result.word_count == 0


class TestProportionalityCheck:
    """Verify the proportionality heuristics."""

    def test_word_count_floor_from_page_count(self) -> None:
        meta = {"source_type": "pdf", "pages_total": 24}
        result = validate_extraction("tiny", meta)
        assert result.expected_min_words == 24 * 200  # 4800

    def test_word_count_from_file_size(self) -> None:
        meta = {"source_type": "pdf", "file_size_bytes": 267872}
        result = validate_extraction("tiny", meta)
        assert result.expected_min_words > 100

    def test_fallback_minimum(self) -> None:
        meta = {"source_type": "unknown"}
        result = validate_extraction("tiny", meta)
        assert result.expected_min_words == 100

    def test_different_source_types(self) -> None:
        meta_pptx = {"source_type": "pptx", "pages_total": 20}
        meta_pdf = {"source_type": "pdf", "pages_total": 20}
        r_pptx = validate_extraction("tiny", meta_pptx)
        r_pdf = validate_extraction("tiny", meta_pdf)
        # PPTX has lower words-per-page expectation
        assert r_pptx.expected_min_words < r_pdf.expected_min_words


class TestStructuralFidelity:
    """Verify structural fidelity assessment."""

    def test_high_fidelity_with_headings_and_lists(self) -> None:
        text = "# H1\n\n## H2\n\n### H3\n\n- item 1\n- item 2\n\nParagraph one.\n\nParagraph two.\n\n" + ("word " * 5000)
        result = validate_extraction(text, {"source_type": "pdf", "pages_total": 24})
        assert result.structural_fidelity == "high"
        assert result.heading_count >= 3

    def test_medium_fidelity_heading_and_paragraphs_no_lists(self) -> None:
        text = "# One Heading\n\nParagraph one content.\n\nParagraph two content.\n\nParagraph three.\n\n" + ("word " * 200)
        result = validate_extraction(text, {"source_type": "pdf", "pages_total": 1})
        assert result.structural_fidelity == "medium"

    def test_low_fidelity_paragraphs_only(self) -> None:
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three.\n\n" + ("word " * 200)
        result = validate_extraction(text, {"source_type": "pdf", "pages_total": 1})
        assert result.structural_fidelity == "low"

    def test_no_fidelity_from_flat_text(self) -> None:
        text = "just some words"
        result = validate_extraction(text, {"source_type": "pdf", "pages_total": 1})
        assert result.structural_fidelity == "none"


class TestExtractionReport:
    """Verify report structure and serialization."""

    def test_to_dict_includes_all_fields(self) -> None:
        result = validate_extraction("# Test\n\nContent words here.", {"source_type": "md"})
        d = result.to_dict()
        assert "tier" in d
        assert "passed" in d
        assert "word_count" in d
        assert "completeness_ratio" in d
        assert "evidence" in d
        assert isinstance(d["evidence"], list)

    def test_recommendations_on_failure(self) -> None:
        result = validate_extraction("stub", {"source_type": "pdf", "pages_total": 50})
        assert len(result.recommendations) > 0
        assert any("alternative" in r.lower() or "fallback" in r.lower() or "escalate" in r.lower()
                    for r in result.recommendations)

    def test_evidence_includes_counts(self) -> None:
        result = validate_extraction("word " * 100, {"source_type": "pdf", "pages_total": 1})
        evidence_text = " ".join(result.evidence)
        assert "100" in evidence_text  # word count
        assert "words" in evidence_text.lower()


class TestRepetitionDetection:
    """Verify detection of repetitive content."""

    def test_highly_repetitive_content_degrades(self) -> None:
        # Same line repeated 200 times
        text = "\n".join(["This is the same line repeated." for _ in range(200)])
        meta = {"source_type": "pdf", "pages_total": 1}
        result = validate_extraction(text, meta)
        assert any("repetition" in loss.lower() for loss in result.known_losses)

    def test_repetition_not_flagged_below_threshold(self) -> None:
        """Repetition check only runs when word_count > 100."""
        text = "\n".join(["Same line." for _ in range(15)])  # ~30 words, all same
        meta = {"source_type": "pdf", "pages_total": 1}
        result = validate_extraction(text, meta)
        assert not any("repetition" in loss.lower() for loss in result.known_losses)
