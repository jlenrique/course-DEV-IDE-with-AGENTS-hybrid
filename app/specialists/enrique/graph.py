"""Enrique elevenlabs specialist graph (Story 2b.7)."""

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
from app.specialists.enrique.elevenlabs_dispatch import (
    ALLOWED_ENRIQUE_MODES,
    ElevenlabsDispatchError,
    dispatch_to_elevenlabs,
)
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "enrique-sidecar"
ENRIQUE_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-elevenlabs" / "references"
ENRIQUE_REFERENCES: tuple[str, ...] = (
    "audio-direction.md",
    "context-envelope-schema.md",
    "init.md",
    "memory-system.md",
    "save-memory.md",
)

ENRIQUE_SYSTEM_MESSAGE = (
    "You are Enrique, the voice director. Return only JSON with keys `mode` and "
    "`operation_payload`. Mode must be one of: voice-preview, narration, sfx, music."
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


class EnriqueAudioParseError(RuntimeError):  # noqa: N818
    """Raised when Enrique's mode-selection payload cannot be parsed."""

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


def _read_enrique_references(
    references_dir: Path = ENRIQUE_REFERENCES_DIR,
    names: tuple[str, ...] = ENRIQUE_REFERENCES,
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
        raise EnriqueAudioParseError(
            f"enrique act envelope cache_prefix is not valid JSON: {exc}",
            tag="enrique_audio.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise EnriqueAudioParseError(
            "enrique act envelope cache_prefix must decode to a mapping",
            tag="enrique_audio.parsed.wrong-type",
        )
    return decoded


def _assemble_enrique_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
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
        "## Enrique references\n\n"
        f"{_read_enrique_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "Choose the execution mode and mode-specific operation_payload."
    )
    return ENRIQUE_SYSTEM_MESSAGE, user


def _extract_json_text(raw_text: str) -> str:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    return stripped


def _parse_enrique_audio(raw_content: Any) -> dict[str, Any]:
    payload: Any
    if isinstance(raw_content, dict):
        payload = raw_content
    elif isinstance(raw_content, str):
        text = _extract_json_text(raw_content)
        if not text:
            raise EnriqueAudioParseError(
                "enrique selection payload cannot be empty",
                tag="enrique_audio.parsed.empty",
            )
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise EnriqueAudioParseError(
                f"enrique selection parse failed: {exc}",
                tag="enrique_audio.parsed.malformed",
            ) from exc
    else:
        raise EnriqueAudioParseError(
            "enrique selection payload must be string-or-mapping",
            tag="enrique_audio.parsed.wrong-type",
        )

    if not isinstance(payload, dict):
        raise EnriqueAudioParseError(
            "enrique selection payload must be a mapping",
            tag="enrique_audio.parsed.wrong-type",
        )

    mode = payload.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        raise EnriqueAudioParseError(
            "enrique selection missing key: mode",
            tag="enrique_audio.parsed.missing-key",
        )
    mode = mode.strip()
    if mode not in ALLOWED_ENRIQUE_MODES:
        raise EnriqueAudioParseError(
            f"enrique mode unsupported: {mode!r}",
            tag="enrique_audio.parsed.missing-key",
        )

    operation_payload = payload.get("operation_payload", {})
    if not isinstance(operation_payload, dict):
        raise EnriqueAudioParseError(
            "enrique operation_payload must be a mapping",
            tag="enrique_audio.parsed.wrong-type",
        )

    return {
        "tag": "enrique_audio.parsed.ok",
        "mode": mode,
        "operation_payload": operation_payload,
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="enrique",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _read_sanctum_digest()
    _ = _read_enrique_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("enrique act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "enrique act expected final plan resolution entry with cache_prefix_hash"
        )

    try:
        envelope_payload = _decode_envelope_payload(state)
    except EnriqueAudioParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    system_message, user_message = _assemble_enrique_prompt(envelope_payload)
    try:
        handle = make_chat_model(
            specialist_id="enrique",
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
        parsed = _parse_enrique_audio(raw_content)
        dispatch_payload = {**envelope_payload, **parsed["operation_payload"]}
        dispatched = dispatch_to_elevenlabs(
            mode=parsed["mode"],
            operation_payload=dispatch_payload,
        )
    except EnriqueAudioParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except ElevenlabsDispatchError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = EnriqueAudioParseError(
            "enrique model invocation failed",
            tag="enrique_audio.parsed.malformed",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc

    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "enrique_audio": {
                "mode": parsed["mode"],
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
        raise RuntimeError(
            f"generated scaffold drift for enrique; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "ALLOWED_ENRIQUE_MODES",
    "ENRIQUE_REFERENCES",
    "EnriqueAudioParseError",
    "TRANSITIONS",
    "_act",
    "_parse_enrique_audio",
    "_plan",
    "_read_enrique_references",
    "_read_sanctum_digest",
    "build_enrique_graph",
]
