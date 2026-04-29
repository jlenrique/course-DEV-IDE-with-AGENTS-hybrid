"""Per-gate operator reference docs structural test (Story 7a.7, AC-7.7-F)."""

from __future__ import annotations

from pathlib import Path

import pytest

DOC_DIR = Path(__file__).resolve().parents[2] / "docs" / "conversational-gates"

REQUIRED_SECTIONS = (
    "## Verdict file shape",
    "## Decision tokens",
    "## Directive tokens",
    "## Common patterns",
    "## Troubleshooting",
)


@pytest.mark.parametrize("gate", ["g1", "g2c", "g3", "g4"])
def test_per_gate_operator_reference_doc_exists(gate: str) -> None:
    doc = DOC_DIR / f"{gate}-operator-reference.md"
    assert doc.exists(), f"missing {doc}"


@pytest.mark.parametrize("gate", ["g1", "g2c", "g3", "g4"])
def test_per_gate_operator_reference_doc_has_5_named_subsections(gate: str) -> None:
    doc = DOC_DIR / f"{gate}-operator-reference.md"
    text = doc.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, f"missing section {section!r} in {doc}"


@pytest.mark.parametrize("gate", ["g1", "g2c", "g3", "g4"])
def test_per_gate_doc_carries_operator_verdict_shape_block(gate: str) -> None:
    doc = DOC_DIR / f"{gate}-operator-reference.md"
    text = doc.read_text(encoding="utf-8")
    assert "verdict_id" in text
    assert "decision_card_digest" in text
    assert "revise_count" in text
