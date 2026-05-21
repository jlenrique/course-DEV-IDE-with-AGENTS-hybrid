from __future__ import annotations

from pathlib import Path

DOC_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "dev-guide"
    / "frozen-graph-version-ceremony.md"
)
GUIDE_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "dev-guide"
    / "langgraph-migration-guide.md"
)


def test_frozen_graph_ceremony_doc_present_with_required_sections() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for heading in (
        "## Tier-1 Patch",
        "## Tier-2 Minor",
        "## Tier-3 Major",
        "## Worked Example: v42 to v42.1",
        "## Worked Example: v42 to v43",
        "## Rollback",
    ):
        assert heading in text


def test_migration_guide_cross_references_ceremony_doc() -> None:
    text = GUIDE_PATH.read_text(encoding="utf-8")

    assert "### 7.1 Frozen-Graph Ceremony (Story 4.5)" in text
    assert "frozen-graph-version-ceremony.md" in text
    assert "compiled-graph-digest.txt" in text
