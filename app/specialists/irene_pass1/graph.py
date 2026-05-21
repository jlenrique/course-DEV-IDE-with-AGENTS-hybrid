"""Irene Pass-1 9-node scaffold graph."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.models.adapter import make_chat_model
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.run_state import RunState
from app.specialists.irene_pass1 import _act as _pass1_act
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

ModeMismatchError = _pass1_act.ModeMismatchError


def _receive(state: RunState) -> dict[str, Any]:
    payload = _pass1_act.decode_envelope_payload(state)
    _pass1_act.enforce_pass1_mode(payload)
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="irene_pass1",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _pass1_act.read_sanctum_digest()
    _ = _pass1_act.read_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("irene_pass1 act invoked before plan")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError("irene_pass1 act requires final model resolution entry")
    handle = make_chat_model(
        specialist_id="irene_pass1",
        temperature=state.temperature,
        tier_request="reasoning",
        system_prompt_hash=last_entry.cache_prefix_hash,
    )
    return _pass1_act.act(state, handle=handle, model_id=last_entry.resolved)


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("irene_pass1", state)


def _gate_decision(state: RunState) -> dict[str, Any]:
    interrupt({"gate_id": "irene-pass1-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_irene_pass1_graph() -> StateGraph:
    """Build Irene Pass-1's 9-node scaffold-conformant subgraph."""
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
        raise RuntimeError(
            f"generated scaffold drift for irene_pass1; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "ModeMismatchError",
    "TRANSITIONS",
    "_act",
    "_plan",
    "_receive",
    "build_irene_pass1_graph",
]
