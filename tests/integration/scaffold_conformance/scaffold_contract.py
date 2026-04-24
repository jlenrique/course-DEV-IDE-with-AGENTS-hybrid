"""Canonical 9-node specialist scaffold contract (Slab 1 Story 1.7 framework).

Every Slab 2+ specialist migration ships a `graph.py` exposing a LangGraph
subgraph with the 9 canonical nodes defined here. This module is the grep-able
source of truth for the contract; per-specialist conformance tests (registered
under `tests/integration/scaffold_conformance/test_scaffold_<name>.py`) import
`SCAFFOLD_NODE_IDS` + `validate_scaffold` to assert their specialist matches.

Slab 1 ships the framework with zero registered specialists — running
`pytest tests/integration/scaffold_conformance/` is green (no-op) at Slab 1
close. Slab 2 stories add per-specialist test files that populate the
framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

# Canonical 9-node scaffold ids per architecture §Specialist Scaffold (Slab 2
# decomposition). Each node's role is fixed; a conforming specialist exposes a
# LangGraph subgraph whose `.nodes` dict contains these ids exactly.
SCAFFOLD_NODE_IDS: frozenset[str] = frozenset(
    {
        "receive",        # Accept SpecialistEnvelope; validate lane + cache-prefix.
        "plan",           # Pre-act planning; cache-warming + resolution-trail append.
        "act",            # The LLM-invoking step (Slab 1 passthrough stub target).
        "verify",         # Cross-field invariants + schema-pin checks on outputs.
        "reflect",        # Self-assessment; feeds Vera-style drift detection.
        "emit_spans",     # LangSmith span emission per NFR-O4 resolution trail.
        "gate_decision",  # Optional HIL gate pause via interrupt().
        "finalize",       # Build SpecialistReturn; attach OperatorVerdict if present.
        "handoff",        # Return Command(goto=..., update=...) to orchestrator.
    }
)


@dataclass(frozen=True)
class ScaffoldConformanceResult:
    """Outcome of a per-specialist scaffold shape check."""

    specialist_id: str
    present: frozenset[str]
    missing: frozenset[str]
    extra: frozenset[str]

    @property
    def is_conforming(self) -> bool:
        return not self.missing and not self.extra


class HasNodes(Protocol):
    """Structural type for a LangGraph subgraph with a `.nodes` mapping."""

    nodes: dict[str, object]


def validate_scaffold(specialist_id: str, subgraph: HasNodes) -> ScaffoldConformanceResult:
    """Assert that `subgraph.nodes` matches `SCAFFOLD_NODE_IDS` exactly.

    Args:
        specialist_id: Name of the specialist under test (for diagnostic message).
        subgraph: A LangGraph `StateGraph` or `CompiledStateGraph` exposing `.nodes`.

    Returns:
        A `ScaffoldConformanceResult` — callers treat non-conforming as a test
        failure (use `.is_conforming` to short-circuit an `assert`).
    """
    present = frozenset(subgraph.nodes.keys())
    missing = SCAFFOLD_NODE_IDS - present
    extra = present - SCAFFOLD_NODE_IDS
    return ScaffoldConformanceResult(
        specialist_id=specialist_id,
        present=present,
        missing=missing,
        extra=extra,
    )


__all__ = [
    "SCAFFOLD_NODE_IDS",
    "ScaffoldConformanceResult",
    "validate_scaffold",
]
