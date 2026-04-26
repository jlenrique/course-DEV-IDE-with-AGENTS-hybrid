"""Vera fidelity-assessor specialist graph (Story 2b.2)."""

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
from app.specialists.vera.sensory_bridges_dispatch import dispatch_to_sensory_bridges
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-fidelity-assessor"
VERA_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-fidelity-assessor" / "references"
VERA_REFERENCES: tuple[str, ...] = (
    "context-envelope-schema.md",
    "fidelity-trace-report.md",
    "gate-evaluation-protocol.md",
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

VERA_SYSTEM_MESSAGE = (
    "You are Vera, a fidelity assessor. Return only JSON with keys: "
    "status, severity, summary, findings."
)


class FTRParseError(RuntimeError):  # noqa: N818
    """Raised when Vera's Fidelity Trace Report cannot be parsed."""

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


def _read_vera_references(
    references_dir: Path = VERA_REFERENCES_DIR,
    names: tuple[str, ...] = VERA_REFERENCES,
) -> str:
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        header = f"### Reference: {name}\n"
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(header + body)
    return "\n\n".join(parts)


def _assemble_vera_prompt(
    envelope_payload: dict[str, Any], perception: dict[str, Any]
) -> tuple[str, str]:
    sanctum_section = _read_sanctum_digest()
    references = _read_vera_references()
    payload_json = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    perception_json = json.dumps(
        perception,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    user = (
        "## Sanctum digest\n\n"
        f"{sanctum_section}\n\n"
        "## Vera references\n\n"
        f"{references}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "## Perception\n\n"
        f"```json\n{perception_json}\n```\n\n"
        "Evaluate fidelity and return strict JSON."
    )
    return VERA_SYSTEM_MESSAGE, user


def _parse_ftr(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise FTRParseError(
            f"vera ftr parse failed: {exc}",
            tag="ftr.parsed.malformed",
        ) from exc
    if not isinstance(parsed, dict):
        raise FTRParseError(
            "vera ftr must be a mapping",
            tag="ftr.parsed.wrong-type",
        )
    required = ("status", "severity", "summary", "findings")
    for key in required:
        if key not in parsed:
            raise FTRParseError(
                f"vera ftr missing key: {key}",
                tag="ftr.parsed.missing-key",
            )
    if not isinstance(parsed["findings"], list):
        raise FTRParseError(
            "vera ftr findings must be a list",
            tag="ftr.parsed.wrong-type",
        )
    if not parsed["findings"]:
        raise FTRParseError(
            "vera ftr findings cannot be empty",
            tag="ftr.parsed.empty",
        )
    if not all(isinstance(item, dict) for item in parsed["findings"]):
        raise FTRParseError(
            "vera ftr findings entries must be objects",
            tag="ftr.parsed.wrong-type",
        )
    if not isinstance(parsed["status"], str) or not isinstance(parsed["severity"], str):
        raise FTRParseError(
            "vera ftr status/severity must be strings",
            tag="ftr.parsed.wrong-type",
        )
    if not isinstance(parsed["summary"], str):
        raise FTRParseError(
            "vera ftr summary must be a string",
            tag="ftr.parsed.wrong-type",
        )
    status_aliases = {
        "pass": "pass",
        "passed": "pass",
        "warn": "warn",
        "warning": "warn",
        "fail": "fail",
        "failed": "fail",
    }
    normalized_status = status_aliases.get(parsed["status"].strip().lower())
    if normalized_status is None or parsed["severity"] not in {
        "low",
        "medium",
        "high",
        "critical",
    }:
        raise FTRParseError(
            "vera ftr contract validation failed",
            tag="ftr.parsed.contract-failure",
        )
    parsed["status"] = normalized_status
    return parsed


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise FTRParseError(
            f"vera act envelope cache_prefix is not valid JSON: {exc}",
            tag="ftr.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise FTRParseError(
            "vera act envelope cache_prefix must decode to a mapping",
            tag="ftr.parsed.wrong-type",
        )
    return decoded


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="vera",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _read_sanctum_digest()
    _ = _read_vera_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("vera act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError("vera act expected final plan resolution entry with cache_prefix_hash")

    try:
        envelope_payload = _decode_envelope_payload(state)
    except FTRParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    try:
        perception = dispatch_to_sensory_bridges(
            artifact_path=envelope_payload.get("artifact_path"),
            source_of_truth_path=envelope_payload.get("source_of_truth_path"),
            modality=str(envelope_payload.get("modality") or "image"),
            gate=str(envelope_payload.get("gate") or "fidelity"),
        )
    except Exception as exc:
        error = FTRParseError(
            "vera sensory dispatch failed",
            tag="ftr.parsed.contract-failure",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=error.tag)
        )
        raise error from exc
    system_message, user_message = _assemble_vera_prompt(envelope_payload, perception)
    try:
        handle = make_chat_model(
            specialist_id="vera",
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
    except Exception as exc:
        error = FTRParseError(
            "vera model invocation failed",
            tag="ftr.parsed.contract-failure",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=error.tag)
        )
        raise error from exc
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    try:
        parsed = _parse_ftr(raw_text)
    except FTRParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    trail_entry = _new_dispatch_trail_entry(last_entry, tag="ftr.parsed.ok")
    output_blob = json.dumps(
        {
            "vera_finding": parsed,
            "perception": perception,
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
        }
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
    del state
    return {}


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "vera-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_vera_graph() -> StateGraph:
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
            f"generated scaffold drift for vera; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "TRANSITIONS",
    "VERA_REFERENCES",
    "_act",
    "_assemble_vera_prompt",
    "FTRParseError",
    "_parse_ftr",
    "_plan",
    "_read_sanctum_digest",
    "_read_vera_references",
    "build_vera_graph",
]
