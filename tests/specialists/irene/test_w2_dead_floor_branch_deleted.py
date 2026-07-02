"""W-2 (`leg-c-delete-dead-irene-pass1-branch`) — dead floor-honoring copy is DELETED.

Per the D1 adjudication (2026-07-01): the Leg-C min_cluster_floor honoring was
originally wired into ``app/specialists/irene/graph.py::_act_pass_1`` behind a
``pass_phase == "pass-1"`` branch that production NEVER dispatches (the real
Pass-1 surface is the separate ``app/specialists/irene_pass1/`` package,
dispatched at nodes 04A/05/05B). The engine was PORTED to
``app/specialists/irene_pass1/cluster_floor.py`` (self-contained, live-proven;
Leg-C dual-gate CLOSED = the reactivation trigger). W-2 deletes the dead copy
so two copies of "the same" honoring never drift.

These pins assert the dead copy is GONE while the REAL consumer stays intact.
"""

from __future__ import annotations

import importlib
import importlib.util


def test_dead_cluster_floor_module_deleted() -> None:
    """The orphaned old engine module is gone from the irene package."""
    assert importlib.util.find_spec("app.specialists.irene.cluster_floor") is None


def test_irene_graph_binds_no_floor_plumbing() -> None:
    """irene graph.py no longer imports/binds any of the dead floor plumbing."""
    graph = importlib.import_module("app.specialists.irene.graph")
    for name in (
        "consume_min_cluster_floor",
        "assert_floor_consulted",
        "_LLM_HIDDEN_PAYLOAD_KEYS",
    ):
        assert not hasattr(graph, name), (
            f"dead floor plumbing `{name}` still bound in app.specialists.irene.graph"
        )


def test_real_pass1_consumer_intact() -> None:
    """Over-deletion guard: the REAL (live-proven) consumer stays intact."""
    mod = importlib.import_module("app.specialists.irene_pass1.cluster_floor")
    assert callable(mod.consume_min_cluster_floor)
