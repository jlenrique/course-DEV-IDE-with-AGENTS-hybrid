"""Scaffold-conformance registration test for generated specialist texas."""

from __future__ import annotations

from app.specialists.texas.graph import build_texas_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_texas_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("texas", build_texas_graph())
    assert result.is_conforming, (
        f"texas scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
