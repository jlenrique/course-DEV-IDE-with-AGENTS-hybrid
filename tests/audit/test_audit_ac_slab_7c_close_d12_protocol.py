from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EPICS = REPO_ROOT / "_bmad-output/planning-artifacts/epics-langchain-langgraph-migration.md"
ANTI_PATTERNS = REPO_ROOT / "docs/dev-guide/specialist-anti-patterns.md"
MIGRATION_GUIDE = REPO_ROOT / "docs/dev-guide/langgraph-migration-guide.md"


def test_d12_1_slab_7c_invariant_preservation_note_present() -> None:
    text = EPICS.read_text(encoding="utf-8")
    assert "Slab 7c Invariant-Preservation Notes" in text
    for token in ("SG-1", "SG-2", "SG-3", "SG-4"):
        assert token in text
    for path_token in (
        "tests/audit/test_audit_ac_sg_aggregate_enforcement.py",
        "tests/parity/test_mapping_checklist_status.py",
        "app/marcus/orchestrator/writers/outbound_envelope.py",
    ):
        assert path_token in text


def test_d12_2_slab_7c_antipattern_harvest_present() -> None:
    text = ANTI_PATTERNS.read_text(encoding="utf-8")
    assert "A19. Class-definition substring scanners go stale" in text
    assert "Story 7c.20b" in text
    assert "AST" in text
    assert "Slab 7c" in text


def test_d12_3_slab_7c_migration_guide_update_present() -> None:
    text = MIGRATION_GUIDE.read_text(encoding="utf-8")
    assert "Slab 7c - Marcus Orchestrational Tail" in text
    for token in (
        "AUDIT-AC",
        "AMEND-7c",
        "sanctum-alignment",
        "Trial3Transcript",
        "dual-FR fold",
    ):
        assert token in text
