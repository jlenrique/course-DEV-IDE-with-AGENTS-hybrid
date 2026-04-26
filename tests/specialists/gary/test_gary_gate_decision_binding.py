from __future__ import annotations

from app.specialists.gary import graph as gary_graph
from app.specialists.gary.graph import TRANSITIONS, build_gary_graph


def test_gary_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_gary_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(gary_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert gary_graph._resume_from_verdict is resume_from_verdict


def test_gary_transitions_match_canonical_chain() -> None:
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
