"""Structural test for the G0 at-gate operator doc (Story 7a.1, AC-7.1-I)."""

from __future__ import annotations

from pathlib import Path

DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "conversational-gates"
    / "g0-directive-composition.md"
)


def test_doc_exists() -> None:
    assert DOC_PATH.exists(), f"missing G0 at-gate doc at {DOC_PATH}"


def test_doc_has_four_named_subsections() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "## (a) What the directive is" in text
    assert "## (b) Why operator-confirm matters" in text
    assert "## (c) When to edit vs accept" in text
    assert "## (d) Worked example" in text


def test_doc_carries_p_r4_reservation_sentence() -> None:
    """P-R4: explicit reservation note for non-file-fetch providers.

    Tolerant to wrap-around line breaks AND blockquote markers: strip ``>``
    markers, then collapse whitespace, then substring-match.
    """
    text = DOC_PATH.read_text(encoding="utf-8")
    stripped = "\n".join(line.lstrip("> ").rstrip() for line in text.splitlines())
    collapsed = " ".join(stripped.split())
    expected = (
        "Notion / Box-URL / Playwright-URL provider shapes are reserved for "
        "Texas's `_act` in a later story"
    )
    assert expected in collapsed, "P-R4 reservation sentence missing or drifted"


def test_doc_has_mermaid_sequence_diagram() -> None:
    """P-R5: subsection (b) carries a Mermaid sequence diagram."""
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "```mermaid" in text
    assert "sequenceDiagram" in text


def test_doc_worked_example_uses_local_file_provider_only() -> None:
    """P-R4 enforcement: worked example sticks to MVP shape (no notion/box/playwright)."""
    text = DOC_PATH.read_text(encoding="utf-8")
    worked_example_section = text.split("## (d) Worked example")[1]
    # Allow mentions in (a) reservation context, but not in worked example as live providers
    assert "provider: local_file" in worked_example_section
    assert "provider: notion" not in worked_example_section
    assert "provider: box_url" not in worked_example_section
    assert "provider: playwright_url" not in worked_example_section
