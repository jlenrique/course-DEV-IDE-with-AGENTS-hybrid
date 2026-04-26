from __future__ import annotations

from app.specialists.kim import graph as kim_graph
from app.specialists.kim.graph import TRANSITIONS, build_kim_graph


def test_kim_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_kim_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(kim_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert kim_graph._resume_from_verdict is resume_from_verdict


def test_kim_transitions_match_canonical_chain() -> None:
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
