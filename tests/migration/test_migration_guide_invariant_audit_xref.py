from __future__ import annotations

from pathlib import Path

GUIDE = Path("docs/dev-guide/langgraph-migration-guide.md")


def test_migration_guide_invariant_audit_xref() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    assert "_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md" in text
    assert "docs/dev-guide/specialist-anti-patterns.md" in text
