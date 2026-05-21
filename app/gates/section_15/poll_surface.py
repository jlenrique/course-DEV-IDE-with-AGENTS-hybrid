"""Section 15 G5 final-operator-handoff poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.decision_cards.g5 import G5Card
from app.models.operator_verdict_section_15 import (
    SECTION_15_SURFACE_ID,
    Section15OperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_15_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_15_g5_final_handoff",
    mandatory_transports=["cli", "http", "mcp-stdio"],
    optional_transports=[],
    alias_of="G5",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 15 G5."""
    return "section_15_g5_final_handoff"


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


def load_final_handoff(g5_card_path: Path) -> G5Card:
    """Load a Section 15 G5 decision card from JSON or YAML."""
    raw_text = g5_card_path.read_text(encoding="utf-8")
    if g5_card_path.suffix.lower() == ".json":
        return G5Card.model_validate_json(raw_text)
    return G5Card.model_validate(yaml.safe_load(raw_text))


def _coerce_final_handoff(g5_card_or_path: G5Card | Mapping[str, Any] | Path) -> G5Card:
    if isinstance(g5_card_or_path, G5Card):
        return g5_card_or_path
    if isinstance(g5_card_or_path, Path):
        return load_final_handoff(g5_card_or_path)
    return G5Card.model_validate(dict(g5_card_or_path))


def _final_handoff_payload(g5_card: G5Card) -> dict[str, Any]:
    return {
        "bundle_run_id": str(g5_card.bundle_run_id),
        "handoff_artifact_paths": [
            path.as_posix() for path in g5_card.handoff_artifact_paths
        ],
        "handoff_summary": g5_card.handoff_summary,
    }


def display_final_handoff(
    g5_card_or_path: G5Card | Mapping[str, Any] | Path,
) -> dict[str, Any]:
    """Return final-handoff preview plus digest shown to the operator."""
    g5_card = _coerce_final_handoff(g5_card_or_path)
    return {
        "surface_id": SURFACE_ID,
        "handoff_id": str(g5_card.card_id),
        "decision_card_digest": compute_model_digest(g5_card),
        "decision_card": g5_card.model_dump(mode="json"),
        "final_handoff_payload": _final_handoff_payload(g5_card),
    }


def submit_verdict(
    handoff_id: str,
    verdict_payload: Section15OperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section15OperatorVerdict:
    """Submit an operator verdict for a displayed G5 final handoff."""
    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 15 supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_handoff_id = handoff_id.strip()
    if not normalized_handoff_id:
        raise GateError("handoff_id_missing", "handoff_id must be non-empty")
    if isinstance(verdict_payload, Section15OperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("handoff_id")
        if supplied_id is not None and str(supplied_id).strip() != normalized_handoff_id:
            raise GateError(
                "handoff_id_mismatch",
                "verdict handoff_id does not match submitted handoff_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["handoff_id"] = normalized_handoff_id
        verdict = Section15OperatorVerdict.model_validate(payload)
    if verdict.handoff_id != normalized_handoff_id:
        raise GateError(
            "handoff_id_mismatch",
            "verdict handoff_id does not match submitted handoff_id",
        )
    return verdict


def resume_from_verdict(
    g5_card_or_path: G5Card | Mapping[str, Any] | Path,
    verdict: Section15OperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 15 verdict after digest verification."""
    displayed = display_final_handoff(g5_card_or_path)
    if verdict.handoff_id != displayed["handoff_id"]:
        raise GateError(
            "handoff_id_mismatch",
            "verdict handoff_id does not match the displayed Section 15 card",
        )
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 15 card digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "decision_card": displayed["decision_card"],
        "final_handoff_payload": displayed["final_handoff_payload"],
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_final_handoff",
    "load_final_handoff",
    "resume_from_verdict",
    "submit_verdict",
]
