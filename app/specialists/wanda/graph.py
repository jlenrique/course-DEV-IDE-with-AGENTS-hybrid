"""Wanda wondercraft specialist graph (Story 2b.8)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.wanda.wondercraft_dispatch import (
    CAPABILITY_CODES,
    WondercraftDispatchError,
    dispatch_to_wondercraft,
)
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "wanda-sidecar"
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
)

WANDA_SYSTEM_MESSAGE = (
    "You are Wanda, the podcast director. Return only JSON with keys "
    "`capability` and `operation_payload`. capability must be one of EP, DP, AS, MB, CM, AH."
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


class WandaAudioParseError(RuntimeError):  # noqa: N818
    """Raised when Wanda capability selection cannot be parsed."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _new_dispatch_trail_entry(
    last_entry: ModelResolutionEntry, *, tag: str
) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def _read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.exists() or not sanctum_dir.is_dir():
        return ""
    files = sorted(
        (p for p in sanctum_dir.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(sanctum_dir).as_posix(),
    )
    if not files:
        return ""
    lines: list[str] = []
    for file_path in files:
        rel = file_path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(
            file_path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return "\n".join(lines)


def _read_wanda_references(
    references_dir: Path = WANDA_REFERENCES_DIR,
    names: tuple[str, ...] = WANDA_REFERENCES,
) -> str:
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        header = f"### Reference: {name}\n"
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(header + body)
    return "\n\n".join(parts)


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise WandaAudioParseError(
            f"wanda act envelope cache_prefix is not valid JSON: {exc}",
            tag="wanda_audio.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise WandaAudioParseError(
            "wanda act envelope cache_prefix must decode to a mapping",
            tag="wanda_audio.parsed.wrong-type",
        )
    return decoded


def _assemble_wanda_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
    payload_json = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    user = (
        "## Sanctum digest\n\n"
        f"{_read_sanctum_digest()}\n\n"
        "## Wanda references\n\n"
        f"{_read_wanda_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "Choose one capability and provide operation_payload for dispatch."
    )
    return WANDA_SYSTEM_MESSAGE, user


def _extract_json_text(raw_text: str) -> str:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    return stripped


def _parse_wanda_audio(raw_content: Any) -> dict[str, Any]:
    payload: Any
    if isinstance(raw_content, dict):
        payload = raw_content
    elif isinstance(raw_content, str):
        text = _extract_json_text(raw_content)
        if not text:
            raise WandaAudioParseError(
                "wanda selection payload cannot be empty",
                tag="wanda_audio.parsed.empty",
            )
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise WandaAudioParseError(
                f"wanda selection parse failed: {exc}",
                tag="wanda_audio.parsed.malformed",
            ) from exc
    else:
        raise WandaAudioParseError(
            "wanda selection payload must be string-or-mapping",
            tag="wanda_audio.parsed.wrong-type",
        )

    if not isinstance(payload, dict):
        raise WandaAudioParseError(
            "wanda selection payload must be a mapping",
            tag="wanda_audio.parsed.wrong-type",
        )

    capability = payload.get("capability")
    if not isinstance(capability, str) or not capability.strip():
        raise WandaAudioParseError(
            "wanda selection missing key: capability",
            tag="wanda_audio.parsed.missing-key",
        )
    capability = capability.strip().upper()
    if capability not in CAPABILITY_CODES:
        raise WandaAudioParseError(
            f"wanda capability unsupported: {capability!r}",
            tag="wanda_audio.parsed.missing-key",
        )

    operation_payload = payload.get("operation_payload", {})
    if not isinstance(operation_payload, dict):
        raise WandaAudioParseError(
            "wanda operation_payload must be a mapping",
            tag="wanda_audio.parsed.wrong-type",
        )

    return {
        "tag": "wanda_audio.parsed.ok",
        "capability": capability,
        "operation_payload": operation_payload,
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="wanda",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _read_sanctum_digest()
    _ = _read_wanda_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("wanda act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "wanda act expected final plan resolution entry with cache_prefix_hash"
        )

    try:
        envelope_payload = _decode_envelope_payload(state)
    except WandaAudioParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    system_message, user_message = _assemble_wanda_prompt(envelope_payload)
    try:
        handle = make_chat_model(
            specialist_id="wanda",
            temperature=state.temperature,
            tier_request="reasoning",
            system_prompt_hash=last_entry.cache_prefix_hash,
        )
        response = handle.chat.invoke(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ]
        )
        raw_content = response.content if hasattr(response, "content") else str(response)
        parsed = _parse_wanda_audio(raw_content)
        dispatch_payload = {**envelope_payload, **parsed["operation_payload"]}
        dispatched = dispatch_to_wondercraft(
            capability=parsed["capability"],
            operation_payload=dispatch_payload,
        )
    except WandaAudioParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except WondercraftDispatchError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = WandaAudioParseError(
            "wanda model invocation failed",
            tag="wanda_audio.parsed.malformed",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc

    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "wanda_audio": {
                "capability": parsed["capability"],
                "selection": parsed,
                "dispatch_receipt": dispatched,
            },
            "model_id": last_entry.resolved,
            "usage": getattr(response, "usage_metadata", None),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
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
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    del state
    return {}


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
        raise RuntimeError(
            f"generated scaffold drift for wanda; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "CAPABILITY_CODES",
    "TRANSITIONS",
    "WANDA_REFERENCES",
    "WandaAudioParseError",
    "_act",
    "_parse_wanda_audio",
    "_plan",
    "_read_sanctum_digest",
    "_read_wanda_references",
    "build_wanda_graph",
]
