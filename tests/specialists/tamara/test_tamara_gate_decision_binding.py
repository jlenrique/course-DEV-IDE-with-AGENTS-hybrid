from __future__ import annotations

from app.specialists.tamara import graph as tamara_graph
from app.specialists.tamara.graph import TRANSITIONS, build_tamara_graph


def test_tamara_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_tamara_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(tamara_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert tamara_graph._resume_from_verdict is resume_from_verdict


def test_tamara_transitions_match_canonical_chain() -> None:
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
