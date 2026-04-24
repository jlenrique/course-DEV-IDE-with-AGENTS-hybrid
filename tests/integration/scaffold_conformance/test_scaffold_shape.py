"""Scaffold-conformance framework shape tests (AC-1.7-D).

Slab 1 Story 1.7 lands the scaffold-conformance framework. Slab 2 specialist
stories register per-specialist tests that instantiate their subgraph and
call `validate_scaffold()`; those tests live alongside this one under
`tests/integration/scaffold_conformance/test_scaffold_<specialist>.py`.

This file verifies the FRAMEWORK itself — the contract module's shape, the
9-node id set, the validator's accept / reject / diagnostic behavior — so a
regression in the framework is caught before it silently accepts a broken
specialist.
"""

from __future__ import annotations

from dataclasses import dataclass

from tests.integration.scaffold_conformance.scaffold_contract import (
    SCAFFOLD_NODE_IDS,
    ScaffoldConformanceResult,
    validate_scaffold,
)


@dataclass
class _FakeSubgraph:
    """Structural-type stand-in for a LangGraph subgraph (test-only)."""

    nodes: dict[str, object]


def test_scaffold_node_ids_are_exactly_nine() -> None:
    assert len(SCAFFOLD_NODE_IDS) == 9


def test_scaffold_node_ids_cover_canonical_roles() -> None:
    # Grep-able role coverage: each id maps to one of the architecturally-named roles.
    for name in ("receive", "plan", "act", "verify", "reflect",
                 "emit_spans", "gate_decision", "finalize", "handoff"):
        assert name in SCAFFOLD_NODE_IDS


def test_validate_accepts_exact_match() -> None:
    subgraph = _FakeSubgraph(nodes={nid: object() for nid in SCAFFOLD_NODE_IDS})
    result = validate_scaffold("fake", subgraph)
    assert result.is_conforming
    assert result.missing == frozenset()
    assert result.extra == frozenset()


def test_validate_reports_missing_nodes() -> None:
    subgraph = _FakeSubgraph(nodes={"receive": object(), "act": object()})
    result = validate_scaffold("incomplete", subgraph)
    assert not result.is_conforming
    assert "plan" in result.missing
    assert "finalize" in result.missing
    assert result.extra == frozenset()


def test_validate_reports_extra_nodes() -> None:
    nodes = {nid: object() for nid in SCAFFOLD_NODE_IDS}
    nodes["undeclared_node"] = object()
    subgraph = _FakeSubgraph(nodes=nodes)
    result = validate_scaffold("bloated", subgraph)
    assert not result.is_conforming
    assert result.missing == frozenset()
    assert "undeclared_node" in result.extra


def test_validate_result_specialist_id_propagates() -> None:
    subgraph = _FakeSubgraph(nodes={})
    result = validate_scaffold("texas", subgraph)
    assert result.specialist_id == "texas"
    assert isinstance(result, ScaffoldConformanceResult)
