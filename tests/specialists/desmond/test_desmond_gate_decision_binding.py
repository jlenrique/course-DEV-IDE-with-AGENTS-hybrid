from __future__ import annotations

from app.specialists.desmond import graph as desmond_graph
from app.specialists.desmond.graph import TRANSITIONS, build_desmond_graph


def test_desmond_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_desmond_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(desmond_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert desmond_graph._resume_from_verdict is resume_from_verdict


def test_desmond_transitions_match_canonical_chain() -> None:
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

