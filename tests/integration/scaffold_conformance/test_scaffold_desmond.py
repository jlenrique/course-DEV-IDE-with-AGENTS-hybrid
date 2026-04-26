"""Scaffold-conformance registration test for generated specialist desmond."""

from __future__ import annotations

from app.specialists.desmond.graph import build_desmond_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_desmond_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("desmond", build_desmond_graph())
    assert result.is_conforming, (
        f"desmond scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
