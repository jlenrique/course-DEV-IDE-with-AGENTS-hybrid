"""Cross-Validator — compare extraction output against reference assets.

Validates extraction completeness by checking whether key content from
reference assets (MD files, DOCX, etc.) appears in the primary extraction.
Supports multiple reference assets with different coverage scopes and strengths.

Usage:
    from skills.bmad_agent_texas.scripts.cross_validator import (
        cross_validate,
        CrossValidationResult,
    )
    result = cross_validate(extracted_text, reference_text, reference_meta)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CrossValidationResult:
    """Result of cross-validating extraction against a reference asset."""
    asset_ref_id: str
    asset_description: str
    coverage_scope: str                  # "full_module" | "part_1_only" | etc.
    sections_in_reference: int
    sections_matched: int
    key_terms_total: int
    key_terms_found: int
    key_terms_coverage: float            # 0.0 - 1.0
    word_count_ratio: float              # extraction words / reference words
    verdict: str                         # human-readable assessment
    matched_sections: list[str] = field(default_factory=list)
    missing_sections: list[str] = field(default_factory=list)
    missing_key_terms: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.key_terms_coverage >= 0.70 and self.sections_matched > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_ref_id": self.asset_ref_id,
            "asset_description": self.asset_description,
            "coverage_scope": self.coverage_scope,
            "sections_matched": f"{self.sections_matched}/{self.sections_in_reference}",
            "key_terms_coverage": round(self.key_terms_coverage, 3),
            "word_count_ratio": round(self.word_count_ratio, 2),
            "verdict": self.verdict,
            "passed": self.passed,
            "missing_sections": self.missing_sections,
            "missing_key_terms": self.missing_key_terms[:10],  # cap for readability
        }


def _extract_headings(text: str) -> list[str]:
    """Extract markdown headings from text."""
    headings = []
    for line in text.splitlines():
        # Handle both normal and escaped markdown headings (\# or #)
        cleaned = re.sub(r"^\\+", "", line).strip()
        # Also strip escaped bold markers for matching
        cleaned = cleaned.replace("\\*\\*", "**").replace("\\*", "*")
        cleaned = cleaned.replace("\\&", "&")
        match = re.match(r"^#{1,6}\s+(.+)", cleaned)
        if match:
            heading = match.group(1).strip()
            heading = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", heading)
            heading = heading.strip()
            if heading:
                headings.append(heading)
    return headings


def _extract_key_terms(text: str, min_word_length: int = 3) -> set[str]:
    """Extract significant terms from text for coverage comparison.

    Focuses on proper nouns, technical terms, and multi-word phrases that
    indicate substantive content presence. Single common words are excluded.
    """
    terms: set[str] = set()

    # Extract capitalized phrases (proper nouns, titles)
    for match in re.finditer(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+", text):
        terms.add(match.group(0).lower())

    # Extract quoted terms
    for match in re.finditer(r'"([^"]{4,60})"', text):
        terms.add(match.group(1).lower())
    for match in re.finditer(r"\*\*([^*]{4,60})\*\*", text):
        term = match.group(1).strip().lower()
        if len(term.split()) <= 6:  # skip very long bold passages
            terms.add(term)

    # Extract terms with specific patterns (Dr., acronyms, etc.)
    for match in re.finditer(r"Dr\.\s+[A-Z]\w+(?:\s+[A-Z]\w+)?", text):
        terms.add(match.group(0).lower())
    for match in re.finditer(r"\b[A-Z]{2,6}\b", text):
        term = match.group(0)
        if term not in ("THE", "AND", "FOR", "BUT", "NOT", "ARE", "WAS", "HAS"):
            terms.add(term.lower())

    return {t for t in terms if len(t) >= min_word_length and "\n" not in t}


def _normalize_for_comparison(text: str) -> str:
    """Normalize text for fuzzy comparison (lowercase, collapse whitespace)."""
    text = re.sub(r"\\([#*_\[\]()])", r"\1", text)  # unescape markdown
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _heading_matches(heading: str, text_normalized: str) -> bool:
    """Check if a heading's content appears in the normalized text."""
    # Normalize the heading the same way
    h_norm = _normalize_for_comparison(heading)
    if not h_norm or len(h_norm) < 3:
        return False

    # Direct substring match
    if h_norm in text_normalized:
        return True

    # Check if the significant words (3+ chars) from the heading appear nearby
    words = [w for w in h_norm.split() if len(w) >= 3]
    if not words:
        return False
    # Require at least 70% of significant words to appear
    found = sum(1 for w in words if w in text_normalized)
    return found / len(words) >= 0.70


def cross_validate(
    extracted_text: str,
    reference_text: str,
    reference_meta: dict[str, Any],
) -> CrossValidationResult:
    """Cross-validate extraction against a reference asset.

    Args:
        extracted_text: The primary extraction output.
        reference_text: The reference asset content.
        reference_meta: Metadata about the reference. Expected keys:
            - ref_id: Reference identifier (e.g., "src-002")
            - description: Human-readable description
            - coverage_scope: "full_module" | "part_1_only" | etc.

    Returns:
        CrossValidationResult with section matching and key term coverage.
    """
    ref_id = reference_meta.get("ref_id", "unknown")
    description = reference_meta.get("description", "reference asset")
    scope = reference_meta.get("coverage_scope", "unknown")

    # Extract structure from reference
    ref_headings = _extract_headings(reference_text)
    ref_key_terms = _extract_key_terms(reference_text)

    # Normalize extraction for comparison
    ext_normalized = _normalize_for_comparison(extracted_text)

    # Section matching
    matched_sections = []
    missing_sections = []
    for heading in ref_headings:
        if _heading_matches(heading, ext_normalized):
            matched_sections.append(heading)
        else:
            missing_sections.append(heading)

    sections_in_ref = len(ref_headings)
    sections_matched = len(matched_sections)

    # Key term coverage
    found_terms = []
    missing_terms = []
    for term in ref_key_terms:
        if term in ext_normalized:
            found_terms.append(term)
        else:
            missing_terms.append(term)

    key_terms_total = len(ref_key_terms)
    key_terms_found = len(found_terms)
    key_terms_coverage = key_terms_found / key_terms_total if key_terms_total > 0 else 0.0

    # Word count ratio
    ext_words = len(extracted_text.split())
    ref_words = len(reference_text.split())
    word_ratio = ext_words / ref_words if ref_words > 0 else 0.0

    # Verdict
    if sections_in_ref > 0 and sections_matched == sections_in_ref and key_terms_coverage >= 0.80:
        verdict = f"Strong match: all {sections_in_ref} sections found, {key_terms_coverage:.0%} key term coverage"
    elif sections_matched > 0 and key_terms_coverage >= 0.60:
        verdict = (
            f"Partial match: {sections_matched}/{sections_in_ref} sections, "
            f"{key_terms_coverage:.0%} key terms. "
            f"Missing: {', '.join(missing_sections[:3])}"
        )
    elif sections_matched == 0 and key_terms_coverage < 0.30:
        verdict = (
            f"Poor match: extraction appears to be missing the content covered by {description}. "
            f"Only {key_terms_coverage:.0%} key term overlap."
        )
    else:
        verdict = (
            f"Moderate match: {sections_matched}/{sections_in_ref} sections, "
            f"{key_terms_coverage:.0%} key terms"
        )

    return CrossValidationResult(
        asset_ref_id=ref_id,
        asset_description=description,
        coverage_scope=scope,
        sections_in_reference=sections_in_ref,
        sections_matched=sections_matched,
        key_terms_total=key_terms_total,
        key_terms_found=key_terms_found,
        key_terms_coverage=key_terms_coverage,
        word_count_ratio=word_ratio,
        verdict=verdict,
        matched_sections=matched_sections,
        missing_sections=missing_sections,
        missing_key_terms=missing_terms,
    )
