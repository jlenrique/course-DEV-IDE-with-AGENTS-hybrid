"""Irene Pass-1 lesson-plan coauthoring implementation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.models.state.operator_verdict import OperatorVerdict
from app.models.state.run_state import RunState

REPO_ROOT = Path(__file__).resolve().parents[3]
SANCTUM_DIR = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"
REFERENCES_DIR = REPO_ROOT / "skills" / "bmad-agent-content-creator" / "references"
PASS_1_REFERENCES = (
    "cluster-planning.md",
    "content-sequencing.md",
    "learning-objective-decomposition.md",
    "pedagogical-framework.md",
    "retrieval-intake-contract.md",
    "template-lesson-plan.md",
)
PASS_1_SYSTEM_MESSAGE = (
    "You are Irene Pass-1. Coauthor a lesson plan, slide-scope outline, and "
    "per-plan-unit ratification surface. Return strict JSON with key plan_units."
)
PASS1_MODES = {"pass-1", "irene-pass1", "irene_pass1"}
PASS2_MODES = {"pass-2", "irene-pass2", "irene_pass2"}


class ModeMismatchError(RuntimeError):
    """Raised when Pass-1 receives a Pass-2 envelope."""


class BulkRatificationError(RuntimeError):
    """Raised when an operator attempts one verdict for all plan units."""


class PlanUnitRatificationError(RuntimeError):
    """Raised when per-plan-unit ratification is incomplete or invalid."""


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), default=str)


def decode_envelope_payload(state: RunState) -> dict[str, Any]:
    if state.cache_state is None or not state.cache_state.cache_prefix:
        return {}
    try:
        decoded = json.loads(state.cache_state.cache_prefix)
    except json.JSONDecodeError as exc:
        raise ValueError("irene_pass1 cache_prefix must be valid JSON") from exc
    if not isinstance(decoded, dict):
        raise ValueError("irene_pass1 cache_prefix must decode to a mapping")
    return decoded


def enforce_pass1_mode(payload: dict[str, Any]) -> None:
    mode = payload.get("mode") or payload.get("pass_phase") or payload.get("irene_mode")
    if mode is None:
        return
    normalized = str(mode).strip().lower()
    if normalized in PASS2_MODES:
        raise ModeMismatchError("Irene Pass-1 cannot run a Pass-2 envelope")
    if normalized not in PASS1_MODES:
        raise ModeMismatchError(f"Irene Pass-1 received unsupported mode {mode!r}")


def read_sanctum_digest(sanctum_dir: Path = SANCTUM_DIR) -> str:
    if not sanctum_dir.is_dir():
        return ""
    rows = []
    for path in sorted(sanctum_dir.rglob("*"), key=lambda p: p.relative_to(sanctum_dir).as_posix()):
        if path.is_file():
            rel = path.relative_to(sanctum_dir).as_posix()
            rows.append(f"{rel}\t{hashlib.sha256(path.read_bytes()).hexdigest()}")
    return "\n".join(rows)


def read_references(references_dir: Path = REFERENCES_DIR) -> str:
    parts = []
    for name in PASS_1_REFERENCES:
        path = references_dir / name
        body = path.read_text(encoding="utf-8") if path.is_file() else f"<missing: {name}>"
        parts.append(f"### Reference: {name}\n{body}")
    return "\n\n".join(parts)


def assemble_pass1_prompt(payload: dict[str, Any]) -> tuple[str, str]:
    return (
        PASS_1_SYSTEM_MESSAGE,
        "## Sanctum digest\n\n"
        f"{read_sanctum_digest()}\n\n"
        "## Irene Pass-1 references\n\n"
        f"{read_references()}\n\n"
        "## Envelope payload\n\n"
        f"```json\n{_json_dumps(payload)}\n```\n\n"
        "Return JSON: {\"plan_units\":[{\"unit_id\":\"...\",\"title\":\"...\","
        "\"learning_objective\":\"...\",\"scope_decision\":\"in-scope|out-of-scope\","
        "\"rationale\":\"...\"}],\"lesson_summary\":\"...\"}.",
    )


def parse_pass1_response(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if "```json" in stripped:
        start = stripped.find("```json") + len("```json")
        end = stripped.find("```", start)
        if end > start:
            stripped = stripped[start:end].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        parsed = {"lesson_summary": raw_text, "plan_units": []}
    if not isinstance(parsed, dict):
        parsed = {"lesson_summary": raw_text, "plan_units": []}
    units = parsed.get("plan_units")
    if not isinstance(units, list) or not units:
        topic = parsed.get("lesson_summary") or "Irene Pass-1 lesson plan"
        parsed["plan_units"] = [
            {
                "unit_id": "unit-1",
                "title": "Core lesson scope",
                "learning_objective": str(topic),
                "scope_decision": "in-scope",
                "rationale": "Fallback unit from unstructured Pass-1 response.",
            }
        ]
    return parsed


def write_lesson_plan(plan: dict[str, Any], *, run_id: str, runs_root: Path | None = None) -> Path:
    root = runs_root or REPO_ROOT / "runs"
    run_dir = root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "irene-pass1.md"
    lines = ["# Irene Pass-1 Lesson Plan", ""]
    if plan.get("lesson_summary"):
        lines.extend([str(plan["lesson_summary"]), ""])
    for unit in plan["plan_units"]:
        lines.extend(
            [
                f"## {unit.get('unit_id', 'unit')}: {unit.get('title', 'Untitled')}",
                f"- Learning objective: {unit.get('learning_objective', '')}",
                f"- Scope decision: {unit.get('scope_decision', '')}",
                f"- Rationale: {unit.get('rationale', '')}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


def confirm_plan_units(
    plan: dict[str, Any],
    verdicts: dict[str, OperatorVerdict] | OperatorVerdict,
) -> dict[str, Any]:
    units = plan.get("plan_units", [])
    if isinstance(verdicts, OperatorVerdict):
        raise BulkRatificationError("bulk confirmation is forbidden; confirm each unit")
    if not isinstance(verdicts, dict):
        raise PlanUnitRatificationError("verdicts must be keyed by plan unit")
    locked_units = []
    for unit in units:
        unit_id = str(unit.get("unit_id", ""))
        verdict = verdicts.get(unit_id)
        if not isinstance(verdict, OperatorVerdict):
            raise PlanUnitRatificationError(f"missing OperatorVerdict for {unit_id}")
        if verdict.verb not in {"approve", "edit"}:
            raise PlanUnitRatificationError(f"unit {unit_id} rejected")
        updated = dict(unit)
        if verdict.edit_payload:
            updated.update(verdict.edit_payload)
        updated["ratified_by"] = verdict.operator_id
        updated["ratification_verdict_id"] = str(verdict.verdict_id)
        locked_units.append(updated)
    return {"plan_units": locked_units, "locked": True}


def build_learning_events(*, run_id: str, locked_scope: dict[str, Any]) -> list[dict[str, Any]]:
    now = datetime.now(UTC).isoformat()
    base = {"run_id": run_id, "gate": "G1A", "timestamp": now}
    return [
        {**base, "event_type": "scope_decision.set", "payload": locked_scope},
        {**base, "event_type": "plan.locked", "payload": {"locked_scope": locked_scope}},
    ]


def act(state: RunState, *, handle: Any, model_id: str) -> dict[str, Any]:
    payload = decode_envelope_payload(state)
    enforce_pass1_mode(payload)
    system_msg, user_msg = assemble_pass1_prompt(payload)
    response = handle.chat.invoke(
        [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
    )
    raw = response.content if hasattr(response, "content") else str(response)
    plan = parse_pass1_response(raw if isinstance(raw, str) else str(raw))
    run_id = str(payload.get("run_id") or state.run_id)
    runs_root_value = payload.get("runs_root")
    runs_root = Path(str(runs_root_value)) if runs_root_value else None
    artifact_path = write_lesson_plan(plan, run_id=run_id, runs_root=runs_root)
    locked_scope = {"plan_units": plan["plan_units"], "locked": False}
    events = build_learning_events(run_id=run_id, locked_scope=locked_scope)
    output = {
        "specialist_id": "irene_pass1",
        "model_id": model_id,
        "lesson_plan": plan,
        "artifact_path": str(artifact_path),
        "locked_scope": locked_scope,
        "learning_events": events,
        "usage": getattr(response, "usage_metadata", None),
    }
    entries_count = state.cache_state.entries_count if state.cache_state is not None else 0
    return {
        "cache_state": {
            "cache_prefix": _json_dumps(output),
            "entries_count": entries_count + 1,
        }
    }


__all__ = [
    "BulkRatificationError",
    "ModeMismatchError",
    "PASS_1_REFERENCES",
    "PASS_1_SYSTEM_MESSAGE",
    "PlanUnitRatificationError",
    "act",
    "assemble_pass1_prompt",
    "build_learning_events",
    "confirm_plan_units",
    "decode_envelope_payload",
    "enforce_pass1_mode",
    "parse_pass1_response",
    "read_sanctum_digest",
    "write_lesson_plan",
]
