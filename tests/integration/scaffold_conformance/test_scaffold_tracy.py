"""Scaffold-conformance registration test for generated specialist tracy."""

from __future__ import annotations

from app.specialists.tracy.graph import build_tracy_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_tracy_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("tracy", build_tracy_graph())
    assert result.is_conforming, (
        f"tracy scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
