"""Quinn-R quality-reviewer specialist graph (Story 2b.3)."""

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
from app.models.state import specialist_summary_artifacts as specialist_summary_writer
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists._scaffold.contract import SCAFFOLD_NODE_IDS
from app.specialists.dispatch_errors import SpecialistDispatchError
from app.specialists.quinn_r import _act as _quinn_r_act_impl
from app.specialists.quinn_r.quality_control_dispatch import (
    run_postcomposition_validators,
    run_precomposition_validators,
)
from app.specialists.quinn_r.sensory_bridges_dispatch import dispatch_to_sensory_bridges
from app.specialists.texas.graph import SanctumLockViolation as _SanctumLockViolation

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

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-quinn-r"
QUINN_R_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-quality-reviewer" / "references"
QUINN_R_REFERENCES: tuple[str, ...] = (
    "feedback-format.md",
    "init.md",
    "memory-system.md",
    "review-protocol.md",
    "save-memory.md",
)

QUINN_R_SYSTEM_MESSAGE = (
    "You are Quinn-R, a quality reviewer. Return strict JSON with keys: "
    "status, severity, summary, findings, dimension_scores."
)

DIMENSION_IDS = (
    "accessibility",
    "brand",
    "learning",
    "instructional",
    "intent",
    "content",
    "audio",
    "composition",
)


class QRRParseError(SpecialistDispatchError):  # noqa: N818
    """Raised when Quinn-R's quality review report cannot be parsed.

    Audio-arc taxonomy re-base (2026-06-12): an LLM parse flake is a
    transient dispatch failure — error-pause + `trial recover`, not a
    process crash.
    """


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


def _read_quinn_r_references(
    references_dir: Path = QUINN_R_REFERENCES_DIR,
    names: tuple[str, ...] = QUINN_R_REFERENCES,
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
        raise QRRParseError(
            f"quinn_r act envelope cache_prefix is not valid JSON: {exc}",
            tag="qrr.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise QRRParseError(
            "quinn_r act envelope cache_prefix must decode to a mapping",
            tag="qrr.parsed.wrong-type",
        )
    return decoded


def _assemble_quinn_r_prompt(
    envelope_payload: dict[str, Any], deterministic: dict[str, Any], perception: dict[str, Any]
) -> tuple[str, str]:
    payload_json = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    deterministic_json = json.dumps(
        deterministic,
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
        f"{_read_sanctum_digest()}\n\n"
        "## Quinn-R references\n\n"
        f"{_read_quinn_r_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "## Deterministic checks\n\n"
        f"```json\n{deterministic_json}\n```\n\n"
        "## Perception\n\n"
        f"```json\n{perception_json}\n```\n\n"
        "Return strict JSON report."
    )
    return QUINN_R_SYSTEM_MESSAGE, user


def _parse_qrr(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise QRRParseError(
            f"quinn_r qrr parse failed: {exc}",
            tag="qrr.parsed.malformed",
        ) from exc
    if not isinstance(parsed, dict):
        raise QRRParseError("quinn_r qrr must be a mapping", tag="qrr.parsed.wrong-type")

    required = ("status", "severity", "summary", "findings", "dimension_scores")
    for key in required:
        if key not in parsed:
            raise QRRParseError(
                f"quinn_r qrr missing key: {key}",
                tag="qrr.parsed.missing-key",
            )
    if not isinstance(parsed["findings"], list):
        raise QRRParseError("quinn_r qrr findings must be a list", tag="qrr.parsed.wrong-type")
    if not parsed["findings"]:
        raise QRRParseError("quinn_r qrr findings cannot be empty", tag="qrr.parsed.empty")
    if not isinstance(parsed["dimension_scores"], dict):
        raise QRRParseError(
            "quinn_r qrr dimension_scores must be a mapping",
            tag="qrr.parsed.wrong-type",
        )
    for dimension in DIMENSION_IDS:
        if dimension not in parsed["dimension_scores"]:
            continue
        value = str(parsed["dimension_scores"][dimension]).strip().lower()
        if value.startswith("fail"):
            raise QRRParseError(
                f"quinn_r qrr dimension failure: {dimension}",
                tag=f"qrr.parsed.dimension-failure:{dimension}",
            )

    status_value = str(parsed["status"]).strip().lower()
    status_aliases = {
        "pass": "pass",
        "passed": "pass",
        "warn": "warn",
        "warning": "warn",
        "partial review": "warn",
        "fail": "fail",
        "failed": "fail",
    }
    normalized_status = status_aliases.get(status_value)
    if normalized_status is None:
        raise QRRParseError(
            "quinn_r qrr contract validation failed",
            tag="qrr.parsed.contract-failure",
        )
    parsed["status"] = normalized_status
    return parsed


def _invoke_quinn_r_llm(
    *,
    state: RunState,
    last_entry: ModelResolutionEntry,
    payload: dict[str, Any],
    deterministic: dict[str, Any],
    perception: dict[str, Any],
) -> dict[str, Any]:
    system_message, user_message = _assemble_quinn_r_prompt(payload, deterministic, perception)
    handle = make_chat_model(
        specialist_id="quinn_r",
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
    raw_text = raw_content if isinstance(raw_content, str) else str(raw_content)
    parsed = _parse_qrr(raw_text)
    parsed["usage"] = getattr(response, "usage_metadata", None)
    return parsed


def _act_precomposition(state: RunState, payload: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = payload.get("artifact_paths")
    if not isinstance(artifact_paths, list):
        artifact_paths = []
    deterministic = run_precomposition_validators(artifact_paths=artifact_paths)
    last_entry = state.model_resolution_trail[-1]
    return _invoke_quinn_r_llm(
        state=state,
        last_entry=last_entry,
        payload=payload,
        deterministic=deterministic,
        perception={"mode": "pre-composition"},
    )


def _act_postcomposition(state: RunState, payload: dict[str, Any]) -> dict[str, Any]:
    perception: dict[str, Any]
    try:
        perception = dispatch_to_sensory_bridges(
            artifact_path=payload.get("artifact_path"),
            modality=str(payload.get("modality") or "image"),
            gate="quality-post-composition",
        )
    except Exception:
        perception = {
            "mode": "post-composition",
            "status": "degraded",
            "sensory": "SKIPPED",
        }
    deterministic = run_postcomposition_validators(
        artifact_path=payload.get("artifact_path"),
    )
    last_entry = state.model_resolution_trail[-1]
    return _invoke_quinn_r_llm(
        state=state,
        last_entry=last_entry,
        payload=payload,
        deterministic=deterministic,
        perception=perception,
    )


def _run_gate_phase(state: RunState, payload: dict[str, Any]) -> dict[str, Any]:
    gate_phase = payload.get("gate_phase")
    if gate_phase not in ("pre-composition", "post-composition"):
        raise ValueError(f"unknown gate_phase: {gate_phase!r}")
    if gate_phase == "pre-composition":
        return _act_precomposition(state, payload)
    return _act_postcomposition(state, payload)


def _require_planned_state(state: RunState) -> ModelResolutionEntry:
    if not state.model_resolution_trail:
        raise RuntimeError("quinn_r act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "quinn_r act expected final plan resolution entry with cache_prefix_hash"
        )
    return last_entry


def _act_with_trail(state: RunState, last_entry: ModelResolutionEntry) -> dict[str, Any]:
    try:
        payload = _decode_envelope_payload(state)
        parsed = _run_gate_phase(state, payload)
    except ValueError:
        raise
    except QRRParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = QRRParseError(
            "quinn_r dispatch/model invocation failed",
            tag="qrr.parsed.contract-failure",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc

    trail_entry = _new_dispatch_trail_entry(last_entry, tag="qrr.parsed.ok")
    output_blob = json.dumps(
        {
            "quinn_r_review": parsed,
            "model_id": last_entry.resolved,
            "gate_phase": payload.get("gate_phase"),
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


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    _ = _SanctumLockViolation
    handle = make_chat_model(
        specialist_id="quinn_r",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _read_sanctum_digest()
    _ = _read_quinn_r_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


ModeMismatchError = _quinn_r_act_impl.ModeMismatchError
WpmThresholdError = _quinn_r_act_impl.WpmThresholdError
VttMonotonicityError = _quinn_r_act_impl.VttMonotonicityError
CoverageGapError = _quinn_r_act_impl.CoverageGapError
DurationCoherenceError = _quinn_r_act_impl.DurationCoherenceError
run_g5_checks = _quinn_r_act_impl.run_g5_checks


def _act(state: RunState) -> dict[str, Any]:
    return _quinn_r_act_impl.act(state)


def _verify(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("quinn_r", state)


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "quinn_r-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_quinn_r_graph() -> StateGraph:
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
            f"generated scaffold drift for quinn_r; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "DIMENSION_IDS",
    "QUINN_R_REFERENCES",
    "QRRParseError",
    "TRANSITIONS",
    "_act",
    "_act_postcomposition",
    "_act_precomposition",
    "_parse_qrr",
    "_plan",
    "_read_quinn_r_references",
    "_read_sanctum_digest",
    "build_quinn_r_graph",
]
