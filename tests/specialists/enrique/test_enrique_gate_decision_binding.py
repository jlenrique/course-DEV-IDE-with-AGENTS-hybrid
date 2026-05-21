from __future__ import annotations

from app.specialists.enrique import graph as enrique_graph
from app.specialists.enrique.graph import TRANSITIONS, build_enrique_graph


def test_enrique_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_enrique_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(enrique_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert enrique_graph._resume_from_verdict is resume_from_verdict


def test_enrique_transitions_match_canonical_chain() -> None:
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
