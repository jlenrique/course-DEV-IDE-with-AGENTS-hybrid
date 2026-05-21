"""Tests for resolve_source_ref provenance resolver."""

from pathlib import Path

import pytest

from scripts.resolve_source_ref import resolve_source_ref


@pytest.fixture
def sample_doc(tmp_path: Path) -> Path:
    """Create a sample markdown document for testing."""
    content = """\
# Course Content

## Chapter 1

Introduction to the course.

### Section A

First section content about pharmacology.

### Section B

Second section content about clinical practice.

## Chapter 2

Advanced topics.

### Knowledge Check

The 10 knowledge check topics are:
1. Digital transformation
2. Workforce evolution
3. Regulatory compliance
4. Patient safety
5. Data analytics

### Clinical Assessment

Assessment criteria for clinical competence.

## Chapter 3

Final chapter with summary.
"""
    doc = tmp_path / "extracted.md"
    doc.write_text(content, encoding="utf-8")
    return tmp_path


class TestHeadingAnchor:
    def test_exact_heading_match(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md### Chapter 2", str(sample_doc)
        )
        assert confidence == "exact"
        assert "Advanced topics" in content
        assert "Knowledge Check" in content

    def test_heading_without_hash_prefix(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#Chapter 2", str(sample_doc)
        )
        assert confidence == "exact"
        assert "Advanced topics" in content

    def test_missing_heading(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md### Nonexistent", str(sample_doc)
        )
        assert confidence == "broken"
        assert content == ""


class TestHeadingHierarchy:
    def test_two_level_hierarchy(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#Chapter 2 > Knowledge Check", str(sample_doc)
        )
        assert confidence == "exact"
        assert "Digital transformation" in content
        assert "Clinical Assessment" not in content

    def test_partial_hierarchy_match(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#Chapter 2 > Nonexistent Subsection", str(sample_doc)
        )
        assert confidence in ("approximate", "broken")

    def test_single_level_hierarchy(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#Chapter 1 > Section A", str(sample_doc)
        )
        assert confidence == "exact"
        assert "pharmacology" in content
        assert "clinical practice" not in content


class TestLineRange:
    def test_valid_line_range(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#L1-L3", str(sample_doc)
        )
        assert confidence == "exact"
        assert "Course Content" in content

    def test_out_of_range(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#L9999-L10000", str(sample_doc)
        )
        assert confidence == "broken"


class TestFileResolution:
    def test_missing_file(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "nonexistent.md#Chapter 1", str(sample_doc)
        )
        assert confidence == "broken"

    def test_file_only_no_path_expr(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md", str(sample_doc)
        )
        assert confidence == "exact"
        assert "Course Content" in content

    def test_case_insensitive_heading(self, sample_doc: Path) -> None:
        content, confidence = resolve_source_ref(
            "extracted.md#chapter 2", str(sample_doc)
        )
        assert confidence == "exact"
        assert "Advanced topics" in content
