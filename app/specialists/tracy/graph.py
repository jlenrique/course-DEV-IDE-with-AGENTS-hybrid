"""Tracy research-intent-shaper specialist graph (Story 2b.5)."""

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
from app.specialists.texas.graph import SanctumLockViolation as _SanctumLockViolation
from app.specialists.tracy.posture_dispatch import _VALID_INTENT_CLASSES, record_posture_selection
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad_agent_tracy"
TRACY_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad_agent_tracy" / "references"
TRACY_REFERENCES: tuple[str, ...] = ("vocabulary.yaml", "postures.md")

TRACY_SYSTEM_MESSAGE = (
    "You are Tracy, a research intent shaper. Return strict JSON with top-level "
    "keys: query, query_attempted, results. Each result must include intent_class, "
    "fit_score, authority_tier, editorial_note, and provider_metadata."
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


class ManifestParseError(RuntimeError):  # noqa: N818
    """Raised when Tracy's manifest cannot be parsed."""

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
        digest = hashlib.sha256(file_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        lines.append(f"{rel}\t{digest}")
    return "\n".join(lines)


def _read_tracy_references(
    references_dir: Path = TRACY_REFERENCES_DIR,
    names: tuple[str, ...] = TRACY_REFERENCES,
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
        raise ManifestParseError(
            "tracy act envelope cache_prefix is missing",
            tag="manifest.parsed.missing-key",
        )
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise ManifestParseError(
            f"tracy act envelope cache_prefix is not valid JSON: {exc}",
            tag="manifest.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise ManifestParseError(
            "tracy act envelope cache_prefix must decode to a mapping",
            tag="manifest.parsed.wrong-type",
        )
    return decoded


def _assemble_tracy_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
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
        "## Tracy references\n\n"
        f"{_read_tracy_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "## Task\n\n"
        "Produce a suggested-resources manifest with vocabulary-conformant "
        "intent_class values. Use only: "
        f"{', '.join(sorted(_VALID_INTENT_CLASSES))}."
    )
    return TRACY_SYSTEM_MESSAGE, user


def _parse_manifest(raw_content: Any) -> dict[str, Any]:
    payload: Any
    if isinstance(raw_content, dict):
        payload = raw_content
    elif isinstance(raw_content, str):
        stripped = raw_content.strip()
        if "```json" in stripped:
            start = stripped.find("```json") + len("```json")
            end = stripped.find("```", start)
            if end > start:
                stripped = stripped[start:end].strip()
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ManifestParseError(
                f"tracy manifest parse failed: {exc}",
                tag="manifest.parsed.malformed",
            ) from exc
    else:
        raise ManifestParseError(
            "tracy manifest must be mapping-or-json-string",
            tag="manifest.parsed.wrong-type",
        )
    if not isinstance(payload, dict):
        raise ManifestParseError(
            "tracy manifest must be a mapping",
            tag="manifest.parsed.wrong-type",
        )
    if "query" not in payload:
        raise ManifestParseError(
            "tracy manifest missing key: query",
            tag="manifest.parsed.missing-key",
        )
    if "results" not in payload:
        raise ManifestParseError(
            "tracy manifest has empty results",
            tag="manifest.parsed.empty",
        )
    query = payload.get("query")
    if not isinstance(query, str):
        raise ManifestParseError(
            "tracy manifest query must be a string",
            tag="manifest.parsed.wrong-type",
        )
    results = payload.get("results")
    if results is None:
        raise ManifestParseError(
            "tracy manifest has empty results",
            tag="manifest.parsed.empty",
        )
    if not isinstance(results, list):
        raise ManifestParseError(
            "tracy manifest results must be a list",
            tag="manifest.parsed.wrong-type",
        )
    query_attempted = payload.get("query_attempted")
    if query_attempted is not None and not isinstance(query_attempted, str):
        raise ManifestParseError(
            "tracy manifest query_attempted must be a string",
            tag="manifest.parsed.wrong-type",
        )
    if not results:
        if isinstance(query_attempted, str) and query_attempted.strip():
            raise ManifestParseError(
                "tracy manifest query ran but returned no results",
                tag="manifest.parsed.no-results",
            )
        raise ManifestParseError(
            "tracy manifest has empty results",
            tag="manifest.parsed.empty",
        )
    required_row_keys = (
        "intent_class",
        "fit_score",
        "authority_tier",
        "editorial_note",
        "provider_metadata",
    )
    for row in results:
        if not isinstance(row, dict):
            raise ManifestParseError(
                "tracy manifest result rows must be mappings",
                tag="manifest.parsed.wrong-type",
            )
        for key in required_row_keys:
            if key not in row:
                raise ManifestParseError(
                    f"tracy manifest row missing {key}",
                    tag="manifest.parsed.missing-key",
                )
        intent_class = row["intent_class"]
        if not isinstance(intent_class, str):
            raise ManifestParseError(
                "tracy manifest intent_class must be string",
                tag="manifest.parsed.wrong-type",
            )
        if not isinstance(row["fit_score"], (int, float)):
            raise ManifestParseError(
                "tracy manifest fit_score must be numeric",
                tag="manifest.parsed.wrong-type",
            )
        if not isinstance(row["authority_tier"], str):
            raise ManifestParseError(
                "tracy manifest authority_tier must be string",
                tag="manifest.parsed.wrong-type",
            )
        if not isinstance(row["editorial_note"], str):
            raise ManifestParseError(
                "tracy manifest editorial_note must be string",
                tag="manifest.parsed.wrong-type",
            )
        if not isinstance(row["provider_metadata"], dict):
            raise ManifestParseError(
                "tracy manifest provider_metadata must be mapping",
                tag="manifest.parsed.wrong-type",
            )
        if intent_class not in _VALID_INTENT_CLASSES:
            raise ManifestParseError(
                f"tracy manifest vocabulary violation: {intent_class}",
                tag="manifest.parsed.vocabulary-violation",
            )
    return {
        "tag": "manifest.parsed.ok",
        "query": query,
        "query_attempted": query_attempted if isinstance(query_attempted, str) else query,
        "results": results,
    }


def _receive(state: RunState) -> dict[str, Any]:
    """Canonical receive slot."""
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    _ = _SanctumLockViolation
    handle = make_chat_model(
        specialist_id="tracy",
        temperature=state.temperature,
        tier_request="reasoning",
    )
    _ = _read_sanctum_digest()
    _ = _read_tracy_references()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("tracy act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "tracy act expected final plan resolution entry with cache_prefix_hash"
        )
    try:
        envelope_payload = _decode_envelope_payload(state)
    except ManifestParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    system_message, user_message = _assemble_tracy_prompt(envelope_payload)
    try:
        handle = make_chat_model(
            specialist_id="tracy",
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
        parsed = _parse_manifest(raw_content)
    except ManifestParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = ManifestParseError(
            "tracy model invocation failed",
            tag="manifest.parsed.malformed",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc

    first_intent = str(parsed["results"][0].get("intent_class", "reserved"))
    posture_tag = record_posture_selection(first_intent)
    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "tracy_manifest": {
                "query": parsed["query"],
                "query_attempted": parsed["query_attempted"],
                "results": parsed["results"],
            },
            "posture_tag": posture_tag,
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
    """Canonical verify slot."""
    del state
    return {}


def _reflect(state: RunState) -> dict[str, Any]:
    """Canonical reflect slot."""
    del state
    return {}


def _emit_spans(state: RunState) -> dict[str, Any]:
    """Canonical emit_spans slot."""
    return specialist_summary_writer.emit_summary_for_state("tracy", state)


def _gate_decision(state: RunState) -> dict[str, Any]:
    """Canonical gate_decision slot using interrupt semantics."""
    # resume_from_verdict body lands at Slab 3 Story 3.3.
    _ = _resume_from_verdict
    interrupt({"gate_id": "tracy-gate-decision"})
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


def build_tracy_graph() -> StateGraph:
    """Build scaffold-conformant graph for tracy."""
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
            f"generated scaffold drift for tracy; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "ManifestParseError",
    "TRACY_REFERENCES",
    "TRANSITIONS",
    "_VALID_INTENT_CLASSES",
    "_act",
    "_parse_manifest",
    "_plan",
    "_read_sanctum_digest",
    "_read_tracy_references",
    "build_tracy_graph",
]
