"""Kira motion specialist graph (Story 2a.3)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state.run_state import RunState
from app.specialists.kira.kling_dispatch import dispatch_to_kling
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-kling"
KIRA_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-kling" / "references"
KIRA_REFERENCES: tuple[str, ...] = (
    "content-type-mapping.md",
    "context-envelope-schema.md",
    "init.md",
    "memory-system.md",
    "save-memory.md",
    "video-prompt-engineering.md",
)
KIRA_SYSTEM_MESSAGE = (
    "You are Kira, a motion-direction specialist. Convert the envelope payload "
    "into a deterministic Kling motion instruction package. Return only JSON "
    "with keys: kling_prompt, model_name, mode, duration, negative_prompt."
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
    if not files:
        return ""
    lines: list[str] = []
    for file_path in files:
        rel = file_path.relative_to(sanctum_dir).as_posix()
        # Normalize CRLF→LF before hashing (BH-7): on Windows checkouts with
        # autocrlf=true, sanctum text files arrive with CRLF on disk while POSIX
        # checkouts keep LF. Hashing raw bytes would diverge cross-platform and
        # collapse cache-prefix determinism for the FR54 cache-hit-rate AC.
        digest = hashlib.sha256(
            file_path.read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return "\n".join(lines)


def _read_kira_references(
    references_dir: Path = KIRA_REFERENCES_DIR, names: tuple[str, ...] = KIRA_REFERENCES
) -> str:
    parts: list[str] = []
    for name in names:
        path = references_dir / name
        header = f"### Reference: {name}\n"
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(header + body)
    return "\n\n".join(parts)


def _assemble_kira_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
    sanctum_section = _read_sanctum_digest()
    reference_section = _read_kira_references()
    payload_section = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    user_message = (
        "## Sanctum digest\n\n"
        f"{sanctum_section}\n\n"
        "## Kira references\n\n"
        f"{reference_section}\n\n"
        "## Envelope payload (canonical JSON)\n\n"
        f"```json\n{payload_section}\n```\n\n"
        "## Task\n\n"
        "Produce a Kling dispatch JSON object:\n"
        "{"
        '"kling_prompt": str, '
        '"model_name": str, '
        '"mode": str, '
        '"duration": number, '
        '"negative_prompt": str'
        "}."
    )
    return KIRA_SYSTEM_MESSAGE, user_message


def _extract_kling_response(content: str) -> dict[str, Any]:
    stripped = content.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    parsed: dict[str, Any]
    try:
        decoded = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"kira act could not parse LLM JSON response: {exc}"
        ) from exc
    if not isinstance(decoded, dict):
        raise RuntimeError(
            f"kira act expected JSON object at top level; got {type(decoded).__name__}"
        )
    parsed = decoded

    kling_prompt = str(parsed.get("kling_prompt") or "").strip()
    model_name = str(parsed.get("model_name") or "").strip()
    mode = str(parsed.get("mode") or "").strip()
    duration_raw = parsed.get("duration", 5)
    try:
        duration = float(duration_raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"invalid duration in Kira response: {duration_raw!r}") from exc
    if not kling_prompt:
        raise RuntimeError("kira response missing non-empty kling_prompt")
    if not model_name:
        raise RuntimeError("kira response missing non-empty model_name")
    if not mode:
        raise RuntimeError("kira response missing non-empty mode")
    return {
        "kling_prompt": kling_prompt,
        "model_name": model_name,
        "mode": mode,
        "duration": duration,
        "negative_prompt": str(parsed.get("negative_prompt") or ""),
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="kira",
        temperature=state.temperature,
        tier_request="fast",
    )
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("kira act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "kira act expected final plan resolution entry with cache_prefix_hash"
        )
    handle = make_chat_model(
        specialist_id="kira",
        temperature=state.temperature,
        tier_request="fast",
        system_prompt_hash=last_entry.cache_prefix_hash,
    )
    envelope_payload: dict[str, Any] = {}
    if state.cache_state is not None and state.cache_state.cache_prefix:
        try:
            decoded = json.loads(state.cache_state.cache_prefix)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, dict):
            envelope_payload = decoded
    system_message, user_message = _assemble_kira_prompt(envelope_payload)
    response = handle.chat.invoke(
        [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
    )
    raw_content = response.content if hasattr(response, "content") else str(response)
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    llm_payload = _extract_kling_response(raw_text)
    dispatch_receipt = dispatch_to_kling(
        kling_prompt=llm_payload["kling_prompt"],
        model_name=llm_payload["model_name"],
        mode=llm_payload["mode"],
        duration=llm_payload["duration"],
        negative_prompt=llm_payload["negative_prompt"],
        motion_plan_path=envelope_payload.get("motion_plan_path"),
        slide_id=envelope_payload.get("slide_id"),
    )
    output_blob = json.dumps(
        {
            "kling_prompt": llm_payload["kling_prompt"],
            "kling_choices": dispatch_receipt["kling_choices"],
            "motion_asset_path": dispatch_receipt["motion_asset_path"],
            "visual_file": envelope_payload.get("visual_file"),
            "model_id": last_entry.resolved,
            "usage": getattr(response, "usage_metadata", None),
        },
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    return {
        "cache_state": {
            "cache_prefix": output_blob,
            "entries_count": (state.cache_state.entries_count + 1)
            if state.cache_state is not None
            else 1,
        }
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
    interrupt({"gate_id": "kira-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_kira_graph() -> StateGraph:
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
        raise RuntimeError(f"generated scaffold drift for kira; missing={missing} extra={extra}")
    return graph


__all__ = [
    "KIRA_REFERENCES",
    "TRANSITIONS",
    "_act",
    "_assemble_kira_prompt",
    "_extract_kling_response",
    "_plan",
    "_read_kira_references",
    "_read_sanctum_digest",
    "build_kira_graph",
]
