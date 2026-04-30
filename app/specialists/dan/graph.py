"""Dan creative-director aux specialist graph (Story 7b.10)."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.run_state import RunState
from app.specialists.dan import _act as _dan_act_impl
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

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
SANCTUM_DIR = _dan_act_impl.SANCTUM_DIR


def _receive(state: RunState) -> dict[str, Any]:
    _dan_act_impl.decode_envelope_payload(state)
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="dan",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _dan_act_impl.read_sanctum_digest()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("dan act invoked before plan")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError("dan act requires final model resolution entry")
    handle = make_chat_model(
        specialist_id="dan",
        temperature=state.temperature,
        tier_request="reasoning",
        system_prompt_hash=last_entry.cache_prefix_hash,
    )
    return _dan_act_impl.act(state, handle=handle, model_id=last_entry.resolved)


def _verify(state: RunState) -> dict[str, Any]:
    """Canonical verify slot."""
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    """Canonical reflect slot."""
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("dan", state, gate_id="G2")


def _gate_decision(state: RunState) -> dict[str, Any]:
    """Canonical gate_decision slot using interrupt semantics."""
    # resume_from_verdict body lands at Slab 3 Story 3.3.
    _ = _resume_from_verdict
    interrupt({"gate_id": "dan-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    """Canonical finalize slot (idempotent; returns empty partial update)."""
    del state
    return {}


def _handoff(state: RunState) -> Command:
    """Canonical handoff slot (idempotent terminal command)."""
    del state
    return Command(goto=END, update={})


def build_dan_graph() -> StateGraph:
    """Build scaffold-conformant graph for dan."""
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
            f"generated scaffold drift for dan; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "SANCTUM_DIR",
    "TRANSITIONS",
    "_act",
    "_emit_spans",
    "_plan",
    "_receive",
    "build_dan_graph",
]
