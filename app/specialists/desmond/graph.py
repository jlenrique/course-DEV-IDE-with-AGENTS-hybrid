"""Desmond descript-assembly specialist graph (Story 2b.4)."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.gates.resume_api import resume_from_verdict as _resume_from_verdict
from app.models.adapter import make_chat_model
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState
from app.specialists.texas.graph import SanctumLockViolation as _SanctumLockViolation
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-desmond"
DESMOND_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-desmond" / "references"
DESMOND_REFERENCES: tuple[str, ...] = (
    "assembly-handoff.md",
    "automation-advisory.md",
    "capability-authoring.md",
    "descript-doc-registry.json",
    "doc-research.md",
    "first-breath.md",
    "memory-guidance.md",
    "pipeline-bridge.md",
)

DESMOND_SANCTUM_LOCK_BASELINE: dict[str, str] = {
    "BOND.md": "58a422e1d150ec201a3c14f7fd98372d96bd4865cf2fb769ad6deb8a7f9c69a3",
    "CAPABILITIES.md": "1eec672ff737046f438972ba972e3b359d7fd9406af2beb2905951b55b3898aa",
    "CLONE-FORK-NOTICE.md": "3f217dda8cb9f251277c9cba647c6331c1da166abf43931979da7e75366423aa",
    "CREED.md": "b645f321f63690767c0f77e0e812b610f8f15bd774433e2ae57a70326205790c",
    "INDEX.md": "407930e35a1f599a1f617d96121a0695f621cb04873c64deffd9a4bd2ee81631",
    "MEMORY.md": "a65ece0c4c75aaaa35b7aa87eedf31b2b72bd5470866c5939c5304aa90f91bcb",
    "PERSONA.md": "86357df3733bba50042b8ce87ccf1b3c274b18668b8fd78f28a524f3e34b8ce7",
}

DESMOND_SYSTEM_MESSAGE = (
    "You are Desmond, a descript assembly specialist. Return only a markdown "
    "handoff package with a mandatory heading exactly `## Automation Advisory`."
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


class HandoffParseError(RuntimeError):  # noqa: N818
    """Raised when Desmond handoff output cannot be parsed."""

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


def _current_sanctum_manifest(sanctum_dir: Path = SANCTUM_DIR) -> dict[str, str]:
    digest = _read_sanctum_digest(sanctum_dir=sanctum_dir)
    if not digest:
        return {}
    manifest: dict[str, str] = {}
    for line in digest.splitlines():
        rel, sha = line.split("\t", 1)
        manifest[rel] = sha
    return manifest


def assert_sanctum_lock(
    expected_manifest: dict[str, str] = DESMOND_SANCTUM_LOCK_BASELINE,
    *,
    sanctum_dir: Path = SANCTUM_DIR,
) -> None:
    current = _current_sanctum_manifest(sanctum_dir=sanctum_dir)
    if current != expected_manifest:
        missing = sorted(set(expected_manifest) - set(current))
        extra = sorted(set(current) - set(expected_manifest))
        mismatched = sorted(
            rel
            for rel in set(expected_manifest).intersection(current)
            if current[rel] != expected_manifest[rel]
        )
        raise _SanctumLockViolation(
            "desmond sanctum lock baseline drift detected; "
            f"missing={missing}, extra={extra}, mismatched={mismatched}"
        )


def _read_desmond_references(
    references_dir: Path = DESMOND_REFERENCES_DIR,
    names: tuple[str, ...] = DESMOND_REFERENCES,
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
        raise HandoffParseError(
            "desmond act envelope cache_prefix is missing",
            tag="handoff.parsed.missing-key",
        )
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise HandoffParseError(
            f"desmond act envelope cache_prefix is not valid JSON: {exc}",
            tag="handoff.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise HandoffParseError(
            "desmond act envelope cache_prefix must decode to a mapping",
            tag="handoff.parsed.wrong-type",
        )
    return decoded


def _assemble_desmond_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
    payload_json = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    user_message = (
        "## Sanctum digest (sorted path+sha256)\n\n"
        f"{_read_sanctum_digest()}\n\n"
        "## Desmond references\n\n"
        f"{_read_desmond_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "## Task\n\n"
        "Author a descript assembly handoff in markdown. Include a mandatory "
        "heading exactly `## Automation Advisory` with concrete operator "
        "guidance and caveats."
    )
    return DESMOND_SYSTEM_MESSAGE, user_message


def _parse_handoff(raw_content: Any) -> dict[str, Any]:
    candidate: str
    if isinstance(raw_content, dict):
        if "handoff_text" not in raw_content:
            raise HandoffParseError(
                "desmond handoff missing key: handoff_text",
                tag="handoff.parsed.missing-key",
            )
        value = raw_content["handoff_text"]
        if not isinstance(value, str):
            raise HandoffParseError(
                "desmond handoff_text must be a string",
                tag="handoff.parsed.wrong-type",
            )
        candidate = value
    elif isinstance(raw_content, str):
        stripped = raw_content.strip()
        if stripped.startswith(("{", "[")):
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise HandoffParseError(
                    f"desmond handoff parse failed: {exc}",
                    tag="handoff.parsed.malformed",
                ) from exc
            if not isinstance(payload, dict):
                raise HandoffParseError(
                    "desmond handoff JSON payload must be a mapping",
                    tag="handoff.parsed.wrong-type",
                )
            if "handoff_text" not in payload:
                raise HandoffParseError(
                    "desmond handoff missing key: handoff_text",
                    tag="handoff.parsed.missing-key",
                )
            value = payload["handoff_text"]
            if not isinstance(value, str):
                raise HandoffParseError(
                    "desmond handoff_text must be a string",
                    tag="handoff.parsed.wrong-type",
                )
            candidate = value
        else:
            candidate = raw_content
    else:
        raise HandoffParseError(
            "desmond handoff must be string-or-mapping",
            tag="handoff.parsed.wrong-type",
        )

    parsed_text = candidate.strip()
    if not parsed_text:
        raise HandoffParseError(
            "desmond handoff cannot be empty",
            tag="handoff.parsed.empty",
        )
    if not re.search(r"^## Automation Advisory[ \t]*$", parsed_text, re.MULTILINE):
        raise HandoffParseError(
            "desmond handoff missing mandatory Automation Advisory section",
            tag="handoff.parsed.advisory-missing",
        )
    advisory = parsed_text.split("## Automation Advisory", 1)[1].strip()
    return {
        "tag": "handoff.parsed.ok",
        "handoff_text": parsed_text,
        "automation_advisory": advisory,
    }


def _receive(state: RunState) -> dict[str, Any]:
    """Canonical receive slot."""
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="desmond",
        temperature=state.temperature,
        tier_request="fast",
    )
    _ = _read_sanctum_digest()
    _ = _read_desmond_references()
    assert_sanctum_lock()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("desmond act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "desmond act expected final plan resolution entry with cache_prefix_hash"
        )

    try:
        envelope_payload = _decode_envelope_payload(state)
    except HandoffParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    system_message, user_message = _assemble_desmond_prompt(envelope_payload)
    try:
        handle = make_chat_model(
            specialist_id="desmond",
            temperature=state.temperature,
            tier_request="fast",
            system_prompt_hash=last_entry.cache_prefix_hash,
        )
        response = handle.chat.invoke(
            [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ]
        )
        raw_content = response.content if hasattr(response, "content") else str(response)
        parsed = _parse_handoff(raw_content)
    except HandoffParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = HandoffParseError(
            "desmond model invocation failed",
            tag="handoff.parsed.malformed",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc
    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "desmond_handoff": {
                "handoff_text": parsed["handoff_text"],
                "automation_advisory": parsed["automation_advisory"],
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
    # resume_from_verdict body lands at Slab 3 Story 3.3.
    _ = _resume_from_verdict
    interrupt({"gate_id": "desmond-gate-decision"})
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


def build_desmond_graph() -> StateGraph:
    """Build Desmond's scaffold-conformant graph."""
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
            f"generated scaffold drift for desmond; missing={missing} extra={extra}"
        )
    return graph


__all__ = [
    "DESMOND_REFERENCES",
    "DESMOND_SANCTUM_LOCK_BASELINE",
    "HandoffParseError",
    "TRANSITIONS",
    "_act",
    "_parse_handoff",
    "_plan",
    "_read_desmond_references",
    "_read_sanctum_digest",
    "assert_sanctum_lock",
    "build_desmond_graph",
]
