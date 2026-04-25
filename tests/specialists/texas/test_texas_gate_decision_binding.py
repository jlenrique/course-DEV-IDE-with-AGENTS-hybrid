from __future__ import annotations

from app.specialists.texas import graph as texas_graph
from app.specialists.texas.graph import TRANSITIONS, build_texas_graph


def test_texas_gate_decision_present_and_binds_resume_from_verdict() -> None:
    graph = build_texas_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(texas_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert texas_graph._resume_from_verdict is resume_from_verdict


def test_texas_transitions_match_canonical_chain() -> None:
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
