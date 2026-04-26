"""Scaffold-conformance registration test for generated specialist vera."""

from __future__ import annotations

from pathlib import Path

from app.specialists.vera.graph import build_vera_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_vera_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("vera", build_vera_graph())
    assert result.is_conforming, (
        f"vera scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )


def test_vera_appears_in_specialist_directory_discovery() -> None:
    names = {
        path.name
        for path in Path("app/specialists").iterdir()
        if path.is_dir() and not path.name.startswith(("_", "."))
    }
    assert "vera" in names
