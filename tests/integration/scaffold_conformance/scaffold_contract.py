"""Canonical 9-node specialist scaffold contract (Slab 1 Story 1.7 framework).

Every Slab 2+ specialist migration ships a `graph.py` exposing a LangGraph
subgraph with the 9 canonical nodes defined here. This module is the grep-able
source of truth for the contract; auto-discovery conformance tests import
`SCAFFOLD_NODE_IDS` + `validate_scaffold` to assert each discovered specialist
matches.

Slab 1 ships the framework with zero registered specialists — running
`pytest tests/integration/scaffold_conformance/` is green (no-op) at Slab 1
close. Slab 2 stories add per-specialist test files that populate the
framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
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


def discover_specialist_ids(
    specialists_root: Path = Path("app/specialists"),
) -> list[str]:
    """Auto-discover specialist package ids from app/specialists."""
    return sorted(
        p.name
        for p in specialists_root.iterdir()
        if p.is_dir() and not p.name.startswith(("_", "."))
    )


def build_specialist_graph(specialist_id: str) -> HasNodes:
    """Import `<specialist>.graph` and call its canonical graph builder."""
    module = import_module(f"app.specialists.{specialist_id}.graph")
    builder_name = f"build_{specialist_id}_graph"
    builder = getattr(module, builder_name)
    return builder()


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
    "build_specialist_graph",
    "discover_specialist_ids",
    "validate_scaffold",
]
