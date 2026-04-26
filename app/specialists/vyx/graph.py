"""Generated 9-node scaffold graph for specialist vyx."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
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


class OperatorInstructionsParseError(RuntimeError):  # noqa: N818
    """Raised when Vyx operator-instructions envelope cannot be parsed."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _new_trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        raise OperatorInstructionsParseError(
            "vyx act envelope cache_prefix is missing",
            tag="storyboard.parsed.missing-key",
        )
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise OperatorInstructionsParseError(
            f"vyx act envelope cache_prefix is not valid JSON: {exc}",
            tag="storyboard.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise OperatorInstructionsParseError(
            "vyx act envelope cache_prefix must decode to a mapping",
            tag="storyboard.parsed.wrong-type",
        )
    return decoded


def _parse_operator_instructions_envelope(payload: dict[str, Any]) -> dict[str, Any]:
    if "prompt" not in payload:
        raise OperatorInstructionsParseError(
            "vyx operator envelope missing key: prompt",
            tag="storyboard.parsed.missing-key",
        )
    prompt = payload["prompt"]
    if not isinstance(prompt, str):
        raise OperatorInstructionsParseError(
            "vyx operator envelope prompt must be a string",
            tag="storyboard.parsed.wrong-type",
        )
    context = payload.get("context", {})
    if context is None:
        context = {}
    if not isinstance(context, dict):
        raise OperatorInstructionsParseError(
            "vyx operator envelope context must be a mapping",
            tag="storyboard.parsed.wrong-type",
        )
    return {
        "tag": "storyboard.parsed.ok",
        "prompt": prompt.strip(),
        "context": context,
    }


def _assemble_storyboard_instructions(parsed: dict[str, Any]) -> dict[str, Any]:
    prompt = parsed["prompt"]
    context = parsed["context"]
    return {
        "brief": prompt,
        "voiceover_tone": str(context.get("voiceover_tone", "clear")),
        "scene_count": int(context.get("scene_count", 6)),
        "frame_schema": ["scene", "visual", "narration", "duration_seconds"],
        "operator_steps": [
            "Extract sequence beats from prompt.",
            "Map each beat to storyboard frames.",
            "Keep transitions deterministic and concise.",
        ],
    }


def _receive(state: RunState) -> dict[str, Any]:
    """Canonical receive slot."""
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="vyx",
        temperature=state.temperature,
        tier_request="fast",
    )
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("vyx act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError("vyx act expected final plan resolution entry with cache_prefix_hash")

    try:
        decoded = _decode_envelope_payload(state)
        parsed = _parse_operator_instructions_envelope(decoded)
    except OperatorInstructionsParseError as exc:
        state.model_resolution_trail.append(_new_trail_entry(last_entry, tag=exc.tag))
        raise

    artifact = _assemble_storyboard_instructions(parsed)
    trail_entry = _new_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "vyx_storyboard": artifact,
            "model_id": last_entry.resolved,
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return {
        "model_resolution_trail": [*state.model_resolution_trail, trail_entry],
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        },
    }


def _verify(state: RunState) -> dict[str, Any]:
    """Canonical verify slot."""
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    """Canonical reflect slot."""
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    """Canonical emit_spans slot."""
    del state
    return {}


def _gate_decision(state: RunState) -> dict[str, Any]:
    """Canonical gate_decision slot using interrupt semantics."""
    _ = _resume_from_verdict
    interrupt({"gate_id": "vyx-gate-decision"})
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


def build_vyx_graph() -> StateGraph:
    """Build scaffold-conformant graph for vyx."""
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
            f"generated scaffold drift for vyx; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "OperatorInstructionsParseError",
    "TRANSITIONS",
    "_act",
    "_parse_operator_instructions_envelope",
    "_plan",
    "build_vyx_graph",
]
