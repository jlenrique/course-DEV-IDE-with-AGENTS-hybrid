from __future__ import annotations

from app.specialists.wanda import graph as wanda_graph
from app.specialists.wanda.graph import TRANSITIONS, build_wanda_graph


def test_wanda_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_wanda_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(wanda_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert wanda_graph._resume_from_verdict is resume_from_verdict


def test_wanda_transitions_match_canonical_chain() -> None:
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
