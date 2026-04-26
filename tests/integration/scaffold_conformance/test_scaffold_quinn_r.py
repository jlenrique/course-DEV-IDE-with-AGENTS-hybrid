"""Scaffold-conformance registration test for generated specialist quinn_r."""

from __future__ import annotations

from app.specialists.quinn_r.graph import build_quinn_r_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_quinn_r_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("quinn_r", build_quinn_r_graph())
    assert result.is_conforming, (
        f"quinn_r scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
