"""Motion-plan producer specialist graph (07D.5 — composition-catalog B2).

Deterministic ADAPTER over the Epic-14 motion-plan engine. Mirrors the kira /
vision 9-node scaffold: ``plan()`` records the model-resolution trail (FR16
uniformity) but does NOT invoke an LLM; ``act()`` is pure deterministic (binding
amendment A — no model client touched in the critical path).
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.run_state import RunState
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS
from app.specialists.motion_planner import _act as _motion_planner_act_impl
from app.specialists.motion_planner.payload_contract import CONSUMED_PAYLOAD_KEYS

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
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    # Records a model-resolution trail entry for FR16 trail uniformity; the
    # handle is NEVER invoked (the producer is deterministic — amendment A).
    handle = make_chat_model(
        specialist_id="motion_planner",
        temperature=state.temperature,
        tier_request="fast",
    )
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    return _motion_planner_act_impl.act(state)


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("motion_planner", state)


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "motion_planner-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_motion_planner_graph() -> StateGraph:
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
            f"generated scaffold drift for motion_planner; missing={missing} extra={extra}"
        )
    return graph


__all__ = ["CONSUMED_PAYLOAD_KEYS", "TRANSITIONS", "_act", "build_motion_planner_graph"]
