"""Scaffold-conformance registration test for generated specialist aria."""

from __future__ import annotations

from app.specialists.aria.graph import build_aria_graph
from tests.integration.scaffold_conformance.scaffold_contract import validate_scaffold


def test_aria_conforms_to_9_node_scaffold() -> None:
    result = validate_scaffold("aria", build_aria_graph())
    assert result.is_conforming, (
        f"aria scaffold drift - missing: {sorted(result.missing)}; "
        f"extra: {sorted(result.extra)}"
    )
