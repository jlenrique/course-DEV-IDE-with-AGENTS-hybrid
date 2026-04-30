"""Wanda Wondercraft specialist graph (Story 7b.9)."""

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
from app.specialists.wanda import _act as _wanda_act_impl
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = _wanda_act_impl.SANCTUM_DIR
WANDA_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-wondercraft" / "references"
WANDA_REFERENCES: tuple[str, ...] = (
    "capability-audio-assembly-handoff.md",
    "capability-audio-summary-produce.md",
    "capability-chapter-markers-emit.md",
    "capability-music-bed-apply.md",
    "capability-podcast-dialogue-produce.md",
    "capability-podcast-episode-produce.md",
    "context-envelope-schema.md",
    "first-breath.md",
    "init.md",
    "memory-system.md",
    "save-memory.md",
    "L5-podcast-production/storytelling-framework.md",
    "L5-podcast-production/audio-production-patterns.md",
    "L5-podcast-production/narration-length-vs-engagement.md",
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
        (path for path in sanctum_dir.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(sanctum_dir).as_posix(),
    )
    rows: list[str] = []
    for file_path in files:
        digest = hashlib.sha256(file_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        rows.append(f"{file_path.relative_to(sanctum_dir).as_posix()}\t{digest}")
    return "\n".join(rows)


def _read_wanda_references(
    references_dir: Path = WANDA_REFERENCES_DIR,
    names: tuple[str, ...] = WANDA_REFERENCES,
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
        specialist_id="wanda",
        temperature=state.temperature,
        tier_request="fast",
    )
    _ = _read_sanctum_digest()
    _ = _read_wanda_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    return _wanda_act_impl.act(state)


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("wanda", state, gate_id="G2")


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "wanda-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_wanda_graph() -> StateGraph:
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
        raise RuntimeError(f"generated scaffold drift for wanda; missing={missing} extra={extra}")
    return graph


__all__ = [
    "SANCTUM_DIR",
    "TRANSITIONS",
    "WANDA_REFERENCES",
    "WANDA_REFERENCES_DIR",
    "_act",
    "_emit_spans",
    "_plan",
    "_read_sanctum_digest",
    "_read_wanda_references",
    "build_wanda_graph",
]
