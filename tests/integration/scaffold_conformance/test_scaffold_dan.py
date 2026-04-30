"""Scaffold-conformance registration test for generated specialist dan."""

from __future__ import annotations

from app.specialists.dan.graph import build_dan_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_dan_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("dan", build_dan_graph())
    assert result.is_conforming, (
        f"dan scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
