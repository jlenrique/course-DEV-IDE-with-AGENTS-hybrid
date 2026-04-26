"""Scaffold-conformance registration test for generated specialist kim."""

from __future__ import annotations

from app.specialists.kim.graph import build_kim_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_kim_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("kim", build_kim_graph())
    assert result.is_conforming, (
        f"kim scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
