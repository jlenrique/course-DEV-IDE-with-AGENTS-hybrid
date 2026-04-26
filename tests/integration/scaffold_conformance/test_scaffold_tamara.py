"""Scaffold-conformance registration test for generated specialist tamara."""

from __future__ import annotations

from app.specialists.tamara.graph import build_tamara_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_tamara_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("tamara", build_tamara_graph())
    assert result.is_conforming, (
        f"tamara scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
