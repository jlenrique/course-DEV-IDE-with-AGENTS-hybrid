from __future__ import annotations

from pathlib import Path

CATALOG = Path("docs/dev-guide/specialist-anti-patterns.md")


def _section(body: str, heading: str) -> str:
    start = body.index(heading)
    next_heading = body.find("\n### ", start + len(heading))
    if next_heading == -1:
        return body[start:]
    return body[start:next_heading]


def _assert_four_field_shape(section: str) -> None:
    assert "- **Example:**" in section
    assert "- **Counter-pattern:**" in section
    assert "- **Slab-of-discovery:**" in section
    assert "- **Severity:**" not in section
    assert "- **Owner:**" not in section


def test_a17_and_p4_entries_present_with_frozen_shape() -> None:
    """Composition-Shape Vote entry was renumbered P3 → P4 at pre-Trial-3 cleanup
    S1 P0-4 (2026-05-07) per Mary's surgical-precision amendment. The original
    `## Process Anti-Patterns` section had a duplicate-heading + reserved-placeholder
    structural defect (P1/P2 reserved + shadowed P3); collapse + renumber rescued
    the post-Slab-5a Composition-Shape Vote entry to P4 while Slab 7c entries
    became canonical P1/P2/P3."""
    body = CATALOG.read_text(encoding="utf-8")

    post_cycle_index = body.index("## Post-Cycle Harvest")
    a17_index = body.index("### A17. Substrate Designed for Isolation, Composition Assumed")
    process_index = body.index("## Process Anti-Patterns")
    p4_index = body.index("### P4. Composition-Shape Vote Without End-to-End Exercise")

    assert post_cycle_index < a17_index < process_index < p4_index
    _assert_four_field_shape(
        _section(body, "### A17. Substrate Designed for Isolation, Composition Assumed")
    )
    _assert_four_field_shape(
        _section(body, "### P4. Composition-Shape Vote Without End-to-End Exercise")
    )
