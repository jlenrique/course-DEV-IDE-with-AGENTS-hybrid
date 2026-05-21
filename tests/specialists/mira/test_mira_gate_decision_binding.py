from __future__ import annotations

from app.specialists.mira import graph as mira_graph
from app.specialists.mira.graph import TRANSITIONS, build_mira_graph


def test_mira_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_mira_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(mira_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert mira_graph._resume_from_verdict is resume_from_verdict


def test_mira_transitions_match_canonical_chain() -> None:
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
