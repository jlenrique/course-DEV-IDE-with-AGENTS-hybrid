"""Scaffold-conformance registration test for generated specialist gary."""

from __future__ import annotations

from pathlib import Path

from app.specialists.gary.graph import build_gary_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_gary_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("gary", build_gary_graph())
    assert result.is_conforming, (
        f"gary scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )


def test_gary_appears_in_specialist_directory_discovery() -> None:
    names = {
        path.name
        for path in Path("app/specialists").iterdir()
        if path.is_dir() and not path.name.startswith(("_", "."))
    }
    assert "gary" in names
