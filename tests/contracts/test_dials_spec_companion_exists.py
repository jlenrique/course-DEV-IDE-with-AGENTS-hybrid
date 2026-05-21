"""AC-T.8 — dials-spec.md companion existence + Q-3 substance test (R2 rider Q-3).

Upgrade from "four-section presence" to "four-section presence AND substance":
each section body must contain ≥1 default-value statement and ≥1 interaction
example.
"""

from __future__ import annotations

import re
from pathlib import Path

DIALS_SPEC = (
    Path(__file__).parents[2] / "app" / "marcus" / "lesson_plan" / "dials-spec.md"
)

REQUIRED_SECTIONS = (
    "## Dial: enrichment",
    "## Dial: corroboration",
    "## Interactions",
    "## Operator-facing wording",
)

_DEFAULT_RX = re.compile(r"default[:\s]+[^\n]+", re.IGNORECASE)
_EXAMPLE_RX = re.compile(r"example|e\.g\.", re.IGNORECASE)


def test_dials_spec_exists_and_non_empty() -> None:
    assert DIALS_SPEC.exists(), f"Missing companion doc at {DIALS_SPEC}"
    text = DIALS_SPEC.read_text(encoding="utf-8").strip()
    assert text, "dials-spec.md is empty"


def test_dials_spec_has_four_required_sections() -> None:
    text = DIALS_SPEC.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, f"dials-spec.md missing required section {section!r}"


def _extract_section_body(text: str, header: str) -> str:
    """Return the text between ``header`` and the next ``## `` header (or EOF)."""
    start = text.index(header) + len(header)
    rest = text[start:]
    next_header = re.search(r"\n## ", rest)
    if next_header:
        return rest[: next_header.start()]
    return rest


def test_each_section_has_default_statement_and_example() -> None:
    """Q-3 substance: each section body contains ≥1 default + ≥1 example."""
    text = DIALS_SPEC.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        body = _extract_section_body(text, section)
        assert _DEFAULT_RX.search(body), (
            f"Section {section!r} missing a `default: ...` statement "
            f"(regex /default[:\\s]+[^\\n]+/i). R2 rider Q-3 substance gate."
        )
        assert _EXAMPLE_RX.search(body), (
            f"Section {section!r} missing an interaction example "
            f"(regex /example|e\\.g\\./i). R2 rider Q-3 substance gate."
        )
