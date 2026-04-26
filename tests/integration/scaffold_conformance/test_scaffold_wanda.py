"""Scaffold-conformance registration test for generated specialist wanda."""

from __future__ import annotations

from app.specialists.wanda.graph import build_wanda_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_wanda_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("wanda", build_wanda_graph())
    assert result.is_conforming, (
        f"wanda scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
