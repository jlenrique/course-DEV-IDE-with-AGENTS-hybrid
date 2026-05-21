from __future__ import annotations

from app.specialists.vera import graph as vera_graph
from app.specialists.vera.graph import TRANSITIONS, build_vera_graph


def test_vera_gate_decision_present_and_binds_resume_from_verdict() -> None:
    graph = build_vera_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(vera_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert vera_graph._resume_from_verdict is resume_from_verdict


def test_vera_transitions_match_canonical_chain() -> None:
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
