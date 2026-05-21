from __future__ import annotations

from app.specialists.kira import graph as kira_graph
from app.specialists.kira.graph import TRANSITIONS, build_kira_graph


def test_kira_gate_decision_present_and_binds_resume_from_verdict() -> None:
    graph = build_kira_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(kira_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert kira_graph._resume_from_verdict is resume_from_verdict


def test_kira_transitions_match_canonical_chain() -> None:
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
