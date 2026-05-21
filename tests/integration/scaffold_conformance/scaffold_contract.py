"""Backward-compat re-export shim for the canonical scaffold contract.

The canonical contract was moved to `app.specialists._scaffold.contract` at
pre-Trial-3 cleanup S1 P0-1 (2026-05-07) per Amelia A1 finding: production
code was importing from `tests/`, breaking on non-pytest entry points.

This shim preserves backward compatibility for existing test imports
(`from tests.integration.scaffold_conformance.scaffold_contract import ...`)
without forcing every test to update in lockstep with the production-code
refactor. New imports should use the canonical app-side path:

    from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS, validate_scaffold, ...
"""

from __future__ import annotations

from app.specialists._scaffold.contract import (  # noqa: F401
    SCAFFOLD_NODE_IDS,
    HasNodes,
    ScaffoldConformanceResult,
    build_specialist_graph,
    discover_specialist_ids,
    validate_scaffold,
)

__all__ = [
    "SCAFFOLD_NODE_IDS",
    "HasNodes",
    "ScaffoldConformanceResult",
    "build_specialist_graph",
    "discover_specialist_ids",
    "validate_scaffold",
]
