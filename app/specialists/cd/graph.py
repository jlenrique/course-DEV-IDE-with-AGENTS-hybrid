"""Dan creative-director specialist graph (Story 2b.6)."""

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
from app.specialists.texas.graph import SanctumLockViolation as _SanctumLockViolation
from scripts.utilities.creative_directive_validator import validate_creative_directive
from tests.integration.scaffold_conformance.scaffold_contract import SCAFFOLD_NODE_IDS

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-cd"
CD_REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-cd" / "references"
CD_REFERENCES: tuple[str, ...] = (
    "capability-authoring.md",
    "creative-directive-contract.md",
    "first-breath.md",
    "memory-guidance.md",
    "profile-targets.md",
)
CD_SANCTUM_LOCK_BASELINE: dict[str, str] = {
    "BOND.md": "7fd28acbf4ed5e46663559e7a5b8192d6fa6148ca02bda5b4eafa670a9ca8747",
    "CAPABILITIES.md": "ed104320a7c9aee47d8c8808e9de4255b72272775b67d4b8e32ffe009bf36d44",
    "CLONE-FORK-NOTICE.md": "3f217dda8cb9f251277c9cba647c6331c1da166abf43931979da7e75366423aa",
    "CREED.md": "c78c2e7431c1315d32dba8ceb10ac0b899e9ca56f0437e28225f900c98d7573c",
    "INDEX.md": "cc74ce849711e7bbb0f707cf73dcd75ef0922cd35409bec32e63773d6c45337f",
    "MEMORY.md": "43259e9f8d903e2addb92724dde5adfe69399cd7da2cc0f41931e998d7170962",
    "PERSONA.md": "e5404eca64fcc0cecf7a5038cf406cf3b6dcdc1e5eb479cc921c0c5d7f3d9a6e",
}

CD_SYSTEM_MESSAGE = (
    "You are Dan, the creative director. Return only JSON with one top-level "
    "key `cd_directive` whose value is a valid creative directive object."
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


class CdDirectiveParseError(RuntimeError):  # noqa: N818
    """Raised when Dan's creative directive cannot be parsed/validated."""

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
        if rel in CD_SANCTUM_LOCK_BASELINE:
            manifest[rel] = sha
    return manifest


def assert_sanctum_lock(
    expected_manifest: dict[str, str] = CD_SANCTUM_LOCK_BASELINE,
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
            "cd sanctum lock baseline drift detected; "
            f"missing={missing}, extra={extra}, mismatched={mismatched}"
        )


def _read_cd_references(
    references_dir: Path = CD_REFERENCES_DIR,
    names: tuple[str, ...] = CD_REFERENCES,
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
        raise CdDirectiveParseError(
            "cd act envelope cache_prefix is missing",
            tag="cd_directive.parsed.missing-key",
        )
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise CdDirectiveParseError(
            f"cd act envelope cache_prefix is not valid JSON: {exc}",
            tag="cd_directive.parsed.malformed",
        ) from exc
    if not isinstance(decoded, dict):
        raise CdDirectiveParseError(
            "cd act envelope cache_prefix must decode to a mapping",
            tag="cd_directive.parsed.wrong-type",
        )
    return decoded


def _assemble_cd_prompt(envelope_payload: dict[str, Any]) -> tuple[str, str]:
    payload_json = json.dumps(
        envelope_payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=str,
    )
    user_message = (
        "## Sanctum digest\n\n"
        f"{_read_sanctum_digest()}\n\n"
        "## CD references\n\n"
        f"{_read_cd_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{payload_json}\n```\n\n"
        "Return a single creative directive object under `cd_directive`."
    )
    return CD_SYSTEM_MESSAGE, user_message


def _extract_json_text(raw_text: str) -> str:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    return stripped


def _parse_cd_directive(raw_content: Any) -> dict[str, Any]:
    parsed: Any
    if isinstance(raw_content, dict):
        parsed = raw_content
    elif isinstance(raw_content, str):
        text = _extract_json_text(raw_content)
        if not text:
            raise CdDirectiveParseError(
                "cd directive cannot be empty",
                tag="cd_directive.parsed.empty",
            )
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise CdDirectiveParseError(
                f"cd directive parse failed: {exc}",
                tag="cd_directive.parsed.malformed",
            ) from exc
    else:
        raise CdDirectiveParseError(
            "cd directive must be string-or-mapping",
            tag="cd_directive.parsed.wrong-type",
        )

    if not isinstance(parsed, dict):
        raise CdDirectiveParseError(
            "cd directive payload must be a mapping",
            tag="cd_directive.parsed.wrong-type",
        )

    directive = parsed.get("cd_directive", parsed)
    if not isinstance(directive, dict):
        raise CdDirectiveParseError(
            "cd directive value must be a mapping",
            tag="cd_directive.parsed.wrong-type",
        )
    if not directive:
        raise CdDirectiveParseError(
            "cd directive cannot be empty",
            tag="cd_directive.parsed.empty",
        )

    errors = validate_creative_directive(directive)
    if errors:
        raise CdDirectiveParseError(
            "cd directive validator failed",
            tag="cd_directive.parsed.validator-failed",
        )

    return {
        "tag": "cd_directive.parsed.ok",
        "cd_directive": directive,
    }


def _receive(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _plan(state: RunState) -> dict[str, Any]:
    handle = make_chat_model(
        specialist_id="cd",
        temperature=state.temperature,
        tier_request="fast",
    )
    _ = _read_sanctum_digest()
    _ = _read_cd_references()
    assert_sanctum_lock()
    return {"model_resolution_trail": [*state.model_resolution_trail, handle.entry]}


def _act(state: RunState) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("cd act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    if last_entry.cache_prefix_hash is None:
        raise RuntimeError(
            "cd act expected final plan resolution entry with cache_prefix_hash"
        )

    try:
        envelope_payload = _decode_envelope_payload(state)
    except CdDirectiveParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise

    system_message, user_message = _assemble_cd_prompt(envelope_payload)
    try:
        handle = make_chat_model(
            specialist_id="cd",
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
        parsed = _parse_cd_directive(raw_content)
    except CdDirectiveParseError as exc:
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=exc.tag)
        )
        raise
    except Exception as exc:
        err = CdDirectiveParseError(
            "cd model invocation failed",
            tag="cd_directive.parsed.malformed",
        )
        state.model_resolution_trail.append(
            _new_dispatch_trail_entry(last_entry, tag=err.tag)
        )
        raise err from exc

    trail_entry = _new_dispatch_trail_entry(last_entry, tag=parsed["tag"])
    output_blob = json.dumps(
        {
            "cd_directive": parsed["cd_directive"],
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
    interrupt({"gate_id": "cd-gate-decision"})
    del state
    return {}


def _finalize(state: RunState) -> dict[str, Any]:
    del state
    return {}


def _handoff(state: RunState) -> Command:
    del state
    return Command(goto=END, update={})


def build_cd_graph() -> StateGraph:
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
        raise RuntimeError(f"generated scaffold drift for cd; missing={missing} extra={extra}")
    return graph


__all__ = [
    "CD_REFERENCES",
    "CD_SANCTUM_LOCK_BASELINE",
    "CdDirectiveParseError",
    "SANCTUM_DIR",
    "TRANSITIONS",
    "_act",
    "_current_sanctum_manifest",
    "_parse_cd_directive",
    "_plan",
    "_read_cd_references",
    "_read_sanctum_digest",
    "assert_sanctum_lock",
    "build_cd_graph",
    "validate_creative_directive",
]
