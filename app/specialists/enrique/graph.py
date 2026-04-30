"""Enrique ElevenLabs specialist graph (Story 2b.7)."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.run_state import RunState
from app.specialists.enrique import _act as _enrique_act_impl
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = _enrique_act_impl.SANCTUM_DIR
ENRIQUE_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-elevenlabs" / "references"
ENRIQUE_REFERENCES: tuple[str, ...] = (
    "audio-direction.md",
    "context-envelope-schema.md",
    "init.md",
    "memory-system.md",
    "save-memory.md",
)
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


def _read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.exists() or not sanctum_dir.is_dir():
        return ""
    files = sorted(
        (p for p in sanctum_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(sanctum_dir).as_posix(),
    )
    rows: list[str] = []
    for file_path in files:
        rel = file_path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(file_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        rows.append(f"{rel}\t{digest}")
    return "\n".join(rows)


def _read_enrique_references(
    references_dir: Path = ENRIQUE_REFERENCES_DIR,
    names: tuple[str, ...] = ENRIQUE_REFERENCES,
) -> str:
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    return "\n\n".join(parts)


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="enrique",
        temperature=state.temperature,
        tier_request="fast",
    )
    _ = _read_sanctum_digest()
    _ = _read_enrique_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    return _enrique_act_impl.act(state)


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("enrique", state, gate_id="G2")


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "enrique-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_enrique_graph() -> StateGraph:
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
        raise RuntimeError(f"generated scaffold drift for enrique; missing={missing} extra={extra}")
    return graph


__all__ = [
    "ENRIQUE_REFERENCES",
    "SANCTUM_DIR",
    "TRANSITIONS",
    "_act",
    "_plan",
    "_read_enrique_references",
    "_read_sanctum_digest",
    "build_enrique_graph",
]
