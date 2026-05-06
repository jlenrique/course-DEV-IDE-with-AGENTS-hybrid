"""Section 06B literal-visual operator-build poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.operator_verdict_section_06b import (
    SECTION_06B_SURFACE_ID,
    Section06BOperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_06B_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_06b_literal_visual_build",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 06B."""
    return "section_06b_literal_visual_build"


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


def load_literal_visual_targets(targets_path: Path) -> dict[str, Any]:
    """Load Section 06B literal-visual targets from JSON or YAML."""

    raw_text = targets_path.read_text(encoding="utf-8")
    if targets_path.suffix.lower() == ".json":
        payload = json.loads(raw_text)
    else:
        payload = yaml.safe_load(raw_text)
    if not isinstance(payload, dict):
        raise GateError("literal_visual_targets_invalid", "targets payload must be an object")
    return payload


def _coerce_targets(upstream_or_path: Path | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(upstream_or_path, Path):
        return load_literal_visual_targets(upstream_or_path)
    return dict(upstream_or_path)


def _target_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    for key in ("slide_specifications", "cards", "literal_visual_targets"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [dict(row) for row in rows if isinstance(row, Mapping)]
    return []


def display_literal_visual_targets(
    upstream_or_path: Path | Mapping[str, Any],
) -> dict[str, Any]:
    """Return literal-visual targets plus the digest shown to the operator."""

    payload = _coerce_targets(upstream_or_path)
    return {
        "surface_id": SURFACE_ID,
        "plan_unit_id": str(payload.get("plan_unit_id", "")).strip(),
        "target_section": str(payload.get("target_section", "")).strip(),
        "decision_card_digest": _canonical_payload_digest(payload),
        "literal_visual_targets": _target_rows(payload),
        "source_payload": payload,
    }


def submit_verdict(
    plan_unit_id: str,
    verdict_payload: Section06BOperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section06BOperatorVerdict:
    """Submit an operator build verdict for Section 06B."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 06B supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_plan_unit_id = plan_unit_id.strip()
    if not normalized_plan_unit_id:
        raise GateError("plan_unit_id_missing", "plan_unit_id must be non-empty")
    if isinstance(verdict_payload, Section06BOperatorVerdict):
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
        verdict = Section06BOperatorVerdict.model_validate(payload)
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
    "display_literal_visual_targets",
    "load_literal_visual_targets",
    "submit_verdict",
]
