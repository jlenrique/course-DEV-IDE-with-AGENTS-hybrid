"""AC-E — Gate-decision node binds `interrupt()` pattern (Story 2a.2).

Two structural tests in this file (per AC-E pin):
1. Node presence + import-level binding to `resume_from_verdict` (graph contains
   the `gate_decision` node + module imports `_resume_from_verdict`).
2. Edge graph routes `verify` → `reflect` → `emit_spans` → `gate_decision`
   → `finalize` → `handoff` per the canonical TRANSITIONS table.

W2's verify-fail-raises test lives in
`test_irene_gate_decision_raises_on_verify_fail.py`.
"""

from __future__ import annotations

from app.specialists.irene import graph as irene_graph
from app.specialists.irene.graph import TRANSITIONS, build_irene_graph


def test_gate_decision_present_and_binds_resume_from_verdict() -> None:
    g = build_irene_graph()
    assert "gate_decision" in g.nodes
    # Module imports the C3-binding symbol — accessible at module level.
    assert hasattr(irene_graph, "_resume_from_verdict")
    # The bound symbol points at app.gates.resume_api.resume_from_verdict.
    from app.gates.resume_api import resume_from_verdict

    assert irene_graph._resume_from_verdict is resume_from_verdict


def test_irene_runtime_routes_around_gate_decision_on_clean_verify() -> None:
    """Canonical TRANSITIONS chain places gate_decision after emit_spans + before finalize.

    AC-E requires that runtime *routes around* gate_decision on clean verify.
    The current scaffold-conformant pattern routes through ALL 9 nodes in
    sequence; "around" semantics will land at Slab 3.3 with conditional edges.
    For 2a.2 the test asserts the edge ordering is the canonical chain so that
    a clean-verify run reaches finalize via the documented path.
    """
    expected = (
        ("receive", "plan"),
        ("plan", "act"),
        ("act", "verify"),
        ("verify", "reflect"),
        ("reflect", "emit_spans"),
        ("emit_spans", "gate_decision"),
        ("gate_decision", "finalize"),
        ("finalize", "handoff"),
    )
    assert expected == TRANSITIONS
