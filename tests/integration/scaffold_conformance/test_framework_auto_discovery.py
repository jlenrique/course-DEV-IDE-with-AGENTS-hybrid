from __future__ import annotations

from pathlib import Path

from tests.integration.scaffold_conformance.scaffold_contract import (
    build_specialist_graph,
    discover_specialist_ids,
    validate_scaffold,
)


def test_discovery_uses_specialists_directory_filter() -> None:
    specialist_ids = discover_specialist_ids()
    assert "irene" in specialist_ids
    assert "_scaffold" not in specialist_ids


def test_auto_discovered_specialists_conform_to_9_node_scaffold() -> None:
    for specialist_id in discover_specialist_ids():
        result = validate_scaffold(specialist_id, build_specialist_graph(specialist_id))
        assert result.is_conforming, (
            f"{specialist_id} scaffold drift - missing: {sorted(result.missing)}; "
            f"extra: {sorted(result.extra)}"
        )


def test_zero_framework_changes_needed_for_new_specialist(tmp_path: Path) -> None:
    specialists_root = tmp_path / "app" / "specialists"
    specialists_root.mkdir(parents=True, exist_ok=True)
    (specialists_root / "alpha").mkdir()
    (specialists_root / "_scaffold").mkdir()
    (specialists_root / ".hidden").mkdir()
    assert discover_specialist_ids(specialists_root=specialists_root) == ["alpha"]
