"""Scaffold-conformance registration test for generated specialist mira."""

from __future__ import annotations

from app.specialists.mira.graph import build_mira_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_mira_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("mira", build_mira_graph())
    assert result.is_conforming, (
        f"mira scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
