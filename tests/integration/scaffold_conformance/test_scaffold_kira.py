"""Scaffold-conformance registration test for generated specialist kira."""

from __future__ import annotations

from app.specialists.kira.graph import build_kira_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_kira_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("kira", build_kira_graph())
    assert result.is_conforming, (
        f"kira scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
