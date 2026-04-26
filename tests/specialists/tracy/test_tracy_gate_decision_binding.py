from __future__ import annotations

from app.specialists.tracy import graph as tracy_graph
from app.specialists.tracy.graph import TRANSITIONS, build_tracy_graph


def test_tracy_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_tracy_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(tracy_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert tracy_graph._resume_from_verdict is resume_from_verdict


def test_tracy_transitions_match_canonical_chain() -> None:
    assert TRANSITIONS == (
        ("receive", "plan"),
        ("plan", "act"),
        ("act", "verify"),
        ("verify", "reflect"),
        ("reflect", "emit_spans"),
        ("emit_spans", "gate_decision"),
        ("gate_decision", "finalize"),
        ("finalize", "handoff"),
    )

