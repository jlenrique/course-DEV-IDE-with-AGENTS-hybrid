"""Extraction Validator — quality checks for source extraction output.

Classifies extraction quality into four tiers and provides evidence-based
pass/fail decisions.  Designed to catch the "30-line stub from a 24-page
PDF" failure mode that ruined a trial run.

Usage:
    from skills.bmad_agent_texas.scripts.extraction_validator import (
        validate_extraction,
        QualityTier,
    )
    result = validate_extraction(extracted_text, source_meta)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class QualityTier(Enum):
    """Four-tier extraction quality classification."""
    FULL_FIDELITY = 1       # Complete, structure preserved
    ADEQUATE_WITH_GAPS = 2  # Mostly complete, known losses
    DEGRADED = 3            # Significant loss, needs fallback
    FAILED = 4              # Near-empty or nonsensical


@dataclass
class ExtractionReport:
    """Structured report from extraction validation."""
    tier: QualityTier
    word_count: int
    line_count: int
    heading_count: int
    expected_min_words: int
    completeness_ratio: float       # actual / expected (0.0 - 1.0+)
    structural_fidelity: str        # "high" | "medium" | "low" | "none"
    evidence: list[str] = field(default_factory=list)
    known_losses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.tier in (QualityTier.FULL_FIDELITY, QualityTier.ADEQUATE_WITH_GAPS)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier.name,
            "tier_value": self.tier.value,
            "passed": self.passed,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "heading_count": self.heading_count,
            "expected_min_words": self.expected_min_words,
            "completeness_ratio": round(self.completeness_ratio, 3),
            "structural_fidelity": self.structural_fidelity,
            "evidence": self.evidence,
            "known_losses": self.known_losses,
            "recommendations": self.recommendations,
        }


# ---------------------------------------------------------------------------
# Heuristics
# ---------------------------------------------------------------------------

# Words per page for different source types (conservative floors)
_WORDS_PER_PAGE: dict[str, int] = {
    "pdf": 200,         # text-heavy PDFs average 250-400, use 200 as floor
    "docx": 200,
    "pptx": 50,         # slides have less text
    "html": 150,
    "notion": 200,
    "default": 150,
}

# Completeness thresholds
_TIER_THRESHOLDS = {
    "full_fidelity": 0.80,      # ≥80% of expected = tier 1
    "adequate": 0.50,           # ≥50% = tier 2
    "degraded": 0.20,           # ≥20% = tier 3
    # below 20% = tier 4 (failed)
}


def _count_headings(text: str) -> int:
    """Count markdown headings in extracted text."""
    return len(re.findall(r"^#{1,6}\s+", text, re.MULTILINE))


def _assess_structural_fidelity(text: str, heading_count: int) -> str:
    """Assess how well the extraction preserved document structure."""
    has_lists = bool(re.search(r"^[\s]*[-*]\s+", text, re.MULTILINE))
    has_paragraphs = len(re.findall(r"\n\n", text)) > 2

    if heading_count >= 3 and has_lists and has_paragraphs:
        return "high"
    elif heading_count >= 1 and has_paragraphs:
        return "medium"
    elif has_paragraphs:
        return "low"
    return "none"


def _estimate_expected_words(
    source_meta: dict[str, Any],
) -> int:
    """Estimate expected word count from source metadata."""
    source_type = source_meta.get("source_type", "default")
    wpp = _WORDS_PER_PAGE.get(source_type, _WORDS_PER_PAGE["default"])

    # If we know the page count, use it
    page_count = source_meta.get("pages_total") or source_meta.get("page_count")
    if page_count:
        return int(page_count) * wpp

    # If we know the file size, estimate pages
    file_size = source_meta.get("file_size_bytes")
    if file_size:
        # Rough heuristic: ~3KB per text page, ~10KB per PDF page
        if source_type == "pdf":
            estimated_pages = max(1, file_size // 10_000)
        else:
            estimated_pages = max(1, file_size // 3_000)
        return estimated_pages * wpp

    # Fallback: require at least 100 words from any source
    return 100


def validate_extraction(
    extracted_text: str,
    source_meta: dict[str, Any],
) -> ExtractionReport:
    """Validate extraction quality and classify into a quality tier.

    Args:
        extracted_text: The extracted content (typically markdown).
        source_meta: Metadata about the source. Expected keys:
            - source_type: "pdf", "docx", "html", "notion", etc.
            - pages_total: Number of pages (if known)
            - file_size_bytes: File size (if known)
            - filename: Source filename (for evidence messages)

    Returns:
        ExtractionReport with tier classification and evidence.
    """
    words = extracted_text.split()
    word_count = len(words)
    line_count = len(extracted_text.splitlines())
    heading_count = _count_headings(extracted_text)
    expected_min = _estimate_expected_words(source_meta)
    filename = source_meta.get("filename", "unknown source")

    # Completeness ratio
    ratio = word_count / expected_min if expected_min > 0 else 0.0

    # Structural fidelity
    fidelity = _assess_structural_fidelity(extracted_text, heading_count)

    # Evidence collection
    evidence: list[str] = []
    known_losses: list[str] = []
    recommendations: list[str] = []

    evidence.append(
        f"Extracted {word_count} words / {line_count} lines / "
        f"{heading_count} headings from '{filename}'"
    )
    evidence.append(
        f"Expected minimum: {expected_min} words "
        f"(completeness ratio: {ratio:.1%})"
    )
    evidence.append(f"Structural fidelity: {fidelity}")

    # Classify tier
    if ratio >= _TIER_THRESHOLDS["full_fidelity"] and fidelity in ("high", "medium"):
        tier = QualityTier.FULL_FIDELITY
        evidence.append("PASS: Extraction meets completeness and structure thresholds")

    elif ratio >= _TIER_THRESHOLDS["adequate"]:
        tier = QualityTier.ADEQUATE_WITH_GAPS
        if ratio < _TIER_THRESHOLDS["full_fidelity"]:
            known_losses.append(
                f"Content may be {1 - ratio:.0%} below expected volume"
            )
        if fidelity in ("low", "none"):
            known_losses.append("Document structure not well preserved")
        evidence.append("PASS WITH GAPS: Content is usable but has known losses")

    elif ratio >= _TIER_THRESHOLDS["degraded"]:
        tier = QualityTier.DEGRADED
        evidence.append(
            f"DEGRADED: Only {ratio:.0%} of expected content extracted"
        )
        recommendations.append("Try alternative extraction method (fallback chain)")
        recommendations.append("Check if source is scanned/image-based PDF")

    else:
        tier = QualityTier.FAILED
        evidence.append(
            f"FAILED: Extraction produced only {word_count} words "
            f"({ratio:.0%} of expected {expected_min})"
        )
        recommendations.append("Source may be image-only, password-protected, or corrupt")
        recommendations.append("Check for alternative source providers (MD, DOCX, Notion)")
        recommendations.append("Escalate to HIL operator for manual intervention")

    # Extra checks
    if word_count > 0 and word_count < 50:
        evidence.append(
            f"WARNING: Extremely thin extraction ({word_count} words) — "
            "likely a stub or metadata-only output"
        )
        if tier.value < QualityTier.DEGRADED.value:
            tier = QualityTier.DEGRADED

    # Check for repetitive content (sign of extraction loop/error)
    if word_count > 100:
        unique_lines = len(set(extracted_text.splitlines()))
        total_lines = max(1, line_count)
        if unique_lines / total_lines < 0.5:
            known_losses.append(
                f"High line repetition detected ({unique_lines}/{total_lines} unique)"
            )
            if tier == QualityTier.FULL_FIDELITY:
                tier = QualityTier.ADEQUATE_WITH_GAPS

    return ExtractionReport(
        tier=tier,
        word_count=word_count,
        line_count=line_count,
        heading_count=heading_count,
        expected_min_words=expected_min,
        completeness_ratio=ratio,
        structural_fidelity=fidelity,
        evidence=evidence,
        known_losses=known_losses,
        recommendations=recommendations,
    )
