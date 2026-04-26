"""Scaffold-conformance registration test for generated specialist enrique."""

from __future__ import annotations

from app.specialists.enrique.graph import build_enrique_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_enrique_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("enrique", build_enrique_graph())
    assert result.is_conforming, (
        f"enrique scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
