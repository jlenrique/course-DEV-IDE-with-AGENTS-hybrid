"""Scaffold-conformance registration test for generated specialist cd."""

from __future__ import annotations

from app.specialists.cd.graph import build_cd_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_cd_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("cd", build_cd_graph())
    assert result.is_conforming, (
        f"cd scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
