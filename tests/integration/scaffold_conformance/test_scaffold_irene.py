"""Scaffold-conformance registration test for generated specialist irene."""

from __future__ import annotations

from app.specialists.irene.graph import build_irene_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_irene_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("irene", build_irene_graph())
    assert result.is_conforming, (
        f"irene scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
