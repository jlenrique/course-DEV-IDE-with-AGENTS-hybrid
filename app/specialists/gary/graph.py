"""Gary gamma-generation specialist graph (Story 2b.1)."""

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
from app.specialists.gary import _act as _gary_act_impl
from app.specialists.gary.gamma_dispatch import dispatch_to_gamma
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = _gary_act_impl.SANCTUM_DIR
GARY_REFERENCES_DIR = _gary_act_impl.REFERENCES_DIR
GARY_REFERENCES = _gary_act_impl.GARY_REFERENCES

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


class ReceiptParseError(RuntimeError):  # noqa: N818
    """Raised when Gary's gamma receipt cannot be parsed into the contract."""

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


def _read_gary_references(
    references_dir: Path = GARY_REFERENCES_DIR,
    names: tuple[str, ...] = GARY_REFERENCES,
) -> str:
    del references_dir, names
    return _gary_act_impl.read_references()


def _decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise ReceiptParseError(
            f"gary act envelope cache_prefix is not valid JSON: {exc}",
            tag="receipt.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise ReceiptParseError(
            "gary act envelope cache_prefix must decode to a mapping",
            tag="receipt.parsed.wrong-type",
        )
    return decoded


def _parse_dispatch_receipt(receipt: Any) -> dict[str, Any]:
    parsed: Any = receipt
    if isinstance(receipt, str):
        try:
            parsed = json.loads(receipt)
        except json.JSONDecodeError as exc:
            raise ReceiptParseError(
                f"gamma receipt JSON decode failed: {exc}",
                tag="receipt.parsed.malformed",
            ) from exc
    if not isinstance(parsed, dict):
        raise ReceiptParseError(
            "gamma receipt must be a mapping",
            tag="receipt.parsed.wrong-type",
        )

    if parsed.get("status") == "export-failure":
        raise ReceiptParseError(
            "gamma receipt reported export failure",
            tag="receipt.parsed.export-failure",
        )

    generation_id = parsed.get("generation_id")
    if not isinstance(generation_id, str) or not generation_id.strip():
        raise ReceiptParseError(
            "gamma receipt missing non-empty generation_id",
            tag="receipt.parsed.missing-key",
        )

    slide_output = parsed.get("gary_slide_output")
    if slide_output is None:
        raise ReceiptParseError(
            "gamma receipt missing gary_slide_output",
            tag="receipt.parsed.missing-key",
        )
    if not isinstance(slide_output, list):
        raise ReceiptParseError(
            "gamma receipt gary_slide_output must be a list",
            tag="receipt.parsed.wrong-type",
        )
    if not slide_output:
        raise ReceiptParseError(
            "gamma receipt gary_slide_output is empty",
            tag="receipt.parsed.empty",
        )
    if not all(isinstance(item, dict) for item in slide_output):
        raise ReceiptParseError(
            "gamma receipt gary_slide_output entries must be objects",
            tag="receipt.parsed.wrong-type",
        )

    return {
        "tag": "receipt.parsed.ok",
        "generation_id": generation_id.strip(),
        "gary_slide_output": slide_output,
        "status": str(parsed.get("status") or "complete"),
        "export_path": parsed.get("export_path"),
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="gary",
        temperature=state.temperature,
        tier_request="fast",
    )
    _ = _read_sanctum_digest()
    _ = _read_gary_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    _gary_act_impl.dispatch_to_gamma = dispatch_to_gamma
    return _gary_act_impl.act(state)


def _verify(state: RunState) -> dict[str, Any]:
    """Canonical verify slot."""
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    """Canonical reflect slot."""
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    return specialist_summary_writer.emit_summary_for_state("gary", state, gate_id="G2B")


def _gate_decision(state: RunState) -> dict[str, Any]:
    _ = _resume_from_verdict
    interrupt({"gate_id": "gary-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_gary_graph() -> StateGraph:
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
            f"generated scaffold drift for gary; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "GARY_REFERENCES",
    "TRANSITIONS",
    "ReceiptParseError",
    "_act",
    "_parse_dispatch_receipt",
    "_plan",
    "_read_gary_references",
    "_read_sanctum_digest",
    "build_gary_graph",
    "dispatch_to_gamma",
]
