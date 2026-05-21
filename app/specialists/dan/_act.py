"""Dan Class-D1 LLM-only creative-director aux implementation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models.state.cache_state import CacheState
from app.models.state.model_resolution_entry import ModelResolutionEntry
from app.models.state.run_state import RunState

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-dan"
DAN_SYSTEM_MESSAGE = (
    "You are Dan, a creative-director aux specialist. Return strict JSON with "
    "advisory G1, G1A, and G2 prose contributions. Do not block gates."
)
GATE_LIMITS = {"G1": 300, "G1A": 200, "G2": 300}
DEFAULT_CONTRIBUTIONS = (
    (
        "G1",
        "creative_director_critique",
        "Sharpen {topic} by naming the learner tension early; "
        "then check that each outline move earns its place.",
    ),
    (
        "G1A",
        "narrative_arc_check",
        "Lock cluster boundaries where the learner question changes.",
    ),
    (
        "G2",
        "tone_voice_consistency_review",
        "Keep Pass-2 narration concrete, calm, and visually grounded.",
    ),
)


class DanAuxParseError(RuntimeError):
    """Raised when Dan cannot shape valid aux contributions."""

    def __init__(self, message: str, *, tag: str) -> None:
        super().__init__(message)
        self.tag = tag


def _json_dumps(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str
    )


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise DanAuxParseError(
            "dan envelope cache_prefix is not JSON", tag="dan.malformed"
        ) from exc
    if not isinstance(decoded, dict):
        raise DanAuxParseError(
            "dan envelope cache_prefix must decode to an object",
            tag="dan.wrong-type",
        )
    return decoded


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows: list[str] = []
    files = sorted(
        (path for path in sanctum_dir.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(sanctum_dir).as_posix(),
    )
    for path in files:
        rel = path.relative_to(sanctum_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        rows.append(f"{rel}\t{digest}")
    return "\n".join(rows)


def assemble_dan_prompt(payload: dict[str, Any]) -> tuple[str, str]:
    user = (
        "## Sanctum digest\n\n"
        f"{read_sanctum_digest()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{_json_dumps(payload)}\n```\n\n"
        "Return JSON with contributions for G1, G1A, and G2. Each row needs "
        "gate_id, contribution_type, and prose; every row is advisory."
    )
    return DAN_SYSTEM_MESSAGE, user


def _extract_json(raw_text: str) -> Any:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise DanAuxParseError(
            "dan LLM JSON parse failed", tag="dan.contributions.malformed"
        ) from exc


def parse_aux_contributions(raw_content: Any, payload: dict[str, Any]) -> list[dict[str, Any]]:
    parsed = raw_content if isinstance(raw_content, dict) else _extract_json(str(raw_content))
    rows = parsed.get("contributions") if isinstance(parsed, dict) else None
    if not rows:
        topic = str(payload.get("topic") or payload.get("lesson_title") or "the lesson")
        rows = [
            {"gate_id": gate, "contribution_type": kind, "prose": prose.format(topic=topic)}
            for gate, kind, prose in DEFAULT_CONTRIBUTIONS
        ]
    if not isinstance(rows, list):
        raise DanAuxParseError(
            "dan contributions must be a list", tag="dan.contributions.wrong-type"
        )
    shaped: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise DanAuxParseError(
                "dan contribution rows must be objects",
                tag="dan.contributions.row-type",
            )
        gate_id = str(row.get("gate_id") or "")
        if gate_id not in GATE_LIMITS:
            raise DanAuxParseError(
                f"dan contribution has unknown gate {gate_id!r}",
                tag="dan.contributions.gate",
            )
        prose = " ".join(str(row.get("prose") or "").split())
        if not prose:
            raise DanAuxParseError(
                "dan contribution prose is empty", tag="dan.contributions.empty"
            )
        if len(prose.split()) > GATE_LIMITS[gate_id]:
            raise DanAuxParseError(
                f"dan {gate_id} prose exceeds word limit",
                tag="dan.contributions.too-long",
            )
        shaped.append(
            {
                "gate_id": gate_id,
                "contribution_type": str(
                    row.get("contribution_type") or "creative_director_aux"
                ),
                "prose": prose,
                "advisory": True,
                "blocking": False,
            }
        )
    gates = {row["gate_id"] for row in shaped}
    if gates != set(GATE_LIMITS):
        raise DanAuxParseError(
            f"dan contributions must cover G1/G1A/G2; got {sorted(gates)}",
            tag="dan.contributions.coverage",
        )
    return shaped


def _trail_entry(last_entry: ModelResolutionEntry, *, tag: str) -> ModelResolutionEntry:
    return ModelResolutionEntry(
        level=last_entry.level,
        requested=last_entry.requested,
        resolved=last_entry.resolved,
        reason=tag,
        timestamp=datetime.now(UTC),
        cache_prefix_hash=last_entry.cache_prefix_hash,
    )


def act(state: RunState, *, handle: Any, model_id: str) -> dict[str, Any]:
    if not state.model_resolution_trail:
        raise RuntimeError("dan act invoked before plan; resolution trail is empty")
    last_entry = state.model_resolution_trail[-1]
    payload = decode_envelope_payload(state)
    system_msg, user_msg = assemble_dan_prompt(payload)
    try:
        response = handle.chat.invoke(
            [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
        )
        raw = response.content if hasattr(response, "content") else str(response)
        contributions = parse_aux_contributions(raw, payload)
    except DanAuxParseError as exc:
        state.model_resolution_trail.append(_trail_entry(last_entry, tag=exc.tag))
        raise
    output = {
        "specialist_id": "dan",
        "model_id": model_id,
        "verb": "proceed",
        "advisory_only": True,
        "contributions": contributions,
        "aux_contributions_by_gate": {row["gate_id"]: row for row in contributions},
        "usage": getattr(response, "usage_metadata", None),
    }
    entries = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "model_resolution_trail": [
            *state.model_resolution_trail,
            _trail_entry(last_entry, tag="dan.aux.ok"),
        ],
        "cache_state": CacheState(
            cache_prefix=_json_dumps(output), entries_count=entries + 1
        ).model_dump(mode="json"),
    }
