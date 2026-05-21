from __future__ import annotations

from app.specialists._scaffold.graph import build_scaffold_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_scaffold_reference_conforms_to_9_node_contract() -> None:
    result = validate_scaffold("_scaffold", build_scaffold_graph())
    assert result.is_conforming, (
        f"_scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
