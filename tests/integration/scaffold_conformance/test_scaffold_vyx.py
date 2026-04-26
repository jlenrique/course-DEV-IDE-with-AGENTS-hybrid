"""Scaffold-conformance registration test for generated specialist vyx."""

from __future__ import annotations

from app.specialists.vyx.graph import build_vyx_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_vyx_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("vyx", build_vyx_graph())
    assert result.is_conforming, (
        f"vyx scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
