from __future__ import annotations

from app.specialists.cd import graph as cd_graph
from app.specialists.cd.graph import TRANSITIONS, build_cd_graph


def test_cd_gate_decision_present_and_binds_interrupt() -> None:
    graph = build_cd_graph()
    assert "gate_decision" in graph.nodes
    assert hasattr(cd_graph, "_resume_from_verdict")
    from app.gates.resume_api import resume_from_verdict

    assert cd_graph._resume_from_verdict is resume_from_verdict


def test_cd_transitions_match_canonical_chain() -> None:
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
