from __future__ import annotations

from app.specialists.quinn_r.graph import TRANSITIONS, build_quinn_r_graph


def test_quinn_r_gate_decision_node_present() -> None:
    compiled = build_quinn_r_graph().compile()
    assert "gate_decision" in compiled.get_graph().nodes


def test_quinn_r_transitions_chain_includes_gate_decision() -> None:
    assert ("emit_spans", "gate_decision") in TRANSITIONS
    assert ("gate_decision", "finalize") in TRANSITIONS
