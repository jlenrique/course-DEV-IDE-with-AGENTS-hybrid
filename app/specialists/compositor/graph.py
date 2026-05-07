"""Compositor deterministic assembly specialist graph (Story 7b.11)."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.compositor import _act as _compositor_act_impl
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS

SANCTUM_DIR = _compositor_act_impl.SANCTUM_DIR
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
    _compositor_act_impl.decode_envelope_payload(state)
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    digest = hashlib.sha256(b"compositor-deterministic-v0").hexdigest()
    entry = ModelResolutionEntry(
        level="per_specialist",
        requested=None,
        resolved="deterministic-compositor-v0",
        reason="Class-D2 deterministic pipeline; no LLM handle resolved",
        timestamp=datetime.now(UTC),
        cache_prefix_hash=digest,
    )
    return {"model_resolution_trail": [*state.model_resolution_trail, entry]}


def _act(state: RunState) -> dict[str, Any]:
    return _compositor_act_impl.act(state)


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("compositor", state, gate_id="G3")


def _gate_decision(state: RunState) -> dict[str, Any]:
    interrupt({"gate_id": "compositor-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_compositor_graph() -> StateGraph:
    """Build scaffold-conformant graph for compositor."""
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
        raise RuntimeError("generated scaffold drift for compositor")
    return graph


__all__ = ["SANCTUM_DIR", "TRANSITIONS", "_act", "_plan", "build_compositor_graph"]
