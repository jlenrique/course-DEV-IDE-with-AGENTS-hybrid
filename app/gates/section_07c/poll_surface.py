"""Section 07C storyboard-build poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.operator_verdict_section_07c import (
    SECTION_07C_SURFACE_ID,
    Section07COperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_07C_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_07c_storyboard_build",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 07C."""
    return "section_07c_storyboard_build"


def canonical_model_bytes(model: BaseModel) -> bytes:
    """Return transport-neutral canonical JSON bytes for any Pydantic model."""

    return json.dumps(
        model.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def compute_model_digest(model: BaseModel) -> str:
    """Return the sha256 digest for a canonicalized model payload."""

    return hashlib.sha256(canonical_model_bytes(model)).hexdigest()


def _canonical_payload_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_storyboard_targets(targets_path: Path) -> dict[str, Any]:
    """Load Section 07C storyboard targets from JSON or YAML."""

    raw_text = targets_path.read_text(encoding="utf-8")
    if targets_path.suffix.lower() == ".json":
        payload = json.loads(raw_text)
    else:
        payload = yaml.safe_load(raw_text)
    if not isinstance(payload, dict):
        raise GateError("storyboard_targets_invalid", "targets payload must be an object")
    return payload


def _coerce_targets(upstream_or_path: Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(upstream_or_path, Path):
        return load_storyboard_targets(upstream_or_path)
    return dict(upstream_or_path)


def _slide_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("slides")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    rows = payload.get("storyboard_targets")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def display_storyboard_targets(
    upstream_or_path: Path | Mapping[str, Any],
) -> dict[str, Any]:
    """Return storyboard targets plus the digest shown to the operator."""

    payload = _coerce_targets(upstream_or_path)
    slides = _slide_rows(payload)
    return {
        "surface_id": SURFACE_ID,
        "plan_unit_id": str(payload.get("plan_unit_id", "")).strip(),
        "target_section": str(payload.get("target_section", "")).strip(),
        "decision_card_digest": _canonical_payload_digest(payload),
        "storyboard_targets": slides,
        "slide_count": len(slides),
        "source_payload": payload,
    }


def submit_verdict(
    plan_unit_id: str,
    verdict_payload: Section07COperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section07COperatorVerdict:
    """Submit an operator build verdict for Section 07C."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 07C supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_plan_unit_id = plan_unit_id.strip()
    if not normalized_plan_unit_id:
        raise GateError("plan_unit_id_missing", "plan_unit_id must be non-empty")
    if isinstance(verdict_payload, Section07COperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("plan_unit_id")
        if supplied_id is not None and str(supplied_id).strip() != normalized_plan_unit_id:
            raise GateError(
                "plan_unit_id_mismatch",
                "verdict plan_unit_id does not match submitted plan_unit_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["plan_unit_id"] = normalized_plan_unit_id
        verdict = Section07COperatorVerdict.model_validate(payload)
    if verdict.plan_unit_id != normalized_plan_unit_id:
        raise GateError(
            "plan_unit_id_mismatch",
            "verdict plan_unit_id does not match submitted plan_unit_id",
        )
    return verdict


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_storyboard_targets",
    "load_storyboard_targets",
    "submit_verdict",
]
