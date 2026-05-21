"""Canonical 9-node scaffold graph used by the specialist generator."""

from __future__ import annotations

from collections import deque
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.state.run_state import RunState
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS

TRANSITIONS: tuple[tuple[str, str], ...] = (
    ("receive", "plan"),
    ("plan", "act"),
    ("act", "verify"),
    ("verify", "reflect"),
    ("reflect", "emit_spans"),
    ("emit_spans", "gate_decision"),
    ("gate_decision", "finalize"),
    ("finalize", "handoff"),
)


def _receive(state: RunState) -> dict[str, Any]:
    """Accept envelope-adjacent state updates; scaffold keeps state unchanged."""
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    """Plan phase placeholder; concrete specialists append real planning updates."""
    del state
    return {}


def _act(state: RunState) -> dict[str, Any]:
    """Act placeholder; Slab 2 concrete specialists replace this with LLM calls."""
    del state
    return {}


def _verify(state: RunState) -> dict[str, Any]:
    """Verification placeholder; concrete specialists assert domain invariants."""
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    """Reflection placeholder for self-assessment hooks."""
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    """Span emission placeholder; concrete specialists add LangSmith annotations."""
    del state
    return {}


def _gate_decision(state: RunState) -> dict[str, Any]:
    """Gate placeholder using interrupt semantics."""
    # resume_from_verdict body lands at Slab 3 Story 3.3.
    _ = _resume_from_verdict
    interrupt({"gate_id": "scaffold-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    """Finalize placeholder for SpecialistReturn assembly (idempotent)."""
    del state
    return {}


def _handoff(state: RunState) -> Command:
    """Handoff placeholder returning terminal Command (idempotent)."""
    del state
    return Command(goto=END, update={})


def _assert_transition_reachability() -> None:
    adjacency: dict[str, set[str]] = {}
    for src, dst in TRANSITIONS:
        adjacency.setdefault(src, set()).add(dst)

    visited: set[str] = set()
    queue: deque[str] = deque(["receive"])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for nxt in adjacency.get(current, set()):
            queue.append(nxt)

    if visited != SCAFFOLD_NODE_IDS:
        missing = sorted(SCAFFOLD_NODE_IDS - visited)
        raise RuntimeError(f"unreachable scaffold nodes from receive: {missing}")
    if adjacency.get("handoff") is not None:
        raise RuntimeError("handoff must terminate; it cannot have outbound scaffold transitions")


def build_scaffold_graph() -> StateGraph:
    """Build the canonical scaffold graph with the exact 9-node set."""
    _assert_transition_reachability()
    graph = StateGraph(state_schema=RunState)
    graph.add_node("receive", _receive)
    graph.add_node("plan", _plan)
    graph.add_node("act", _act)
    graph.add_node("verify", _verify)
    graph.add_node("reflect", _reflect)
    graph.add_node("emit_spans", _emit_spans)
    graph.add_node("gate_decision", _gate_decision)
    graph.add_node("finalize", _finalize)
    graph.add_node("handoff", _handoff)

    graph.add_edge(START, "receive")
    for src, dst in TRANSITIONS:
        graph.add_edge(src, dst)
    graph.add_edge("handoff", END)

    present = frozenset(graph.nodes.keys())
    if present != SCAFFOLD_NODE_IDS:
        missing = sorted(SCAFFOLD_NODE_IDS - present)
        extra = sorted(present - SCAFFOLD_NODE_IDS)
        raise RuntimeError(f"scaffold graph node drift; missing={missing} extra={extra}")
    return graph


__all__ = ["build_scaffold_graph"]
