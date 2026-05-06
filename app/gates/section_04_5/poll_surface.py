"""Section 04.5 G1.5 run-budget estimator poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.decision_cards.g1 import G1Card
from app.models.operator_verdict_section_04_5 import (
    SECTION_04_5_SURFACE_ID,
    Section04_5OperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_04_5_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_04_5_g1_5_estimator",
    mandatory_transports=["cli", "http"],
    optional_transports=["mcp-stdio"],
    alias_of="G1",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 04.5 G1.5."""
    return "section_04_5_g1_5_estimator"


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


def load_estimator(estimator_path: Path) -> G1Card:
    """Load a Section 04.5 estimator DecisionCard from JSON or YAML."""

    raw_text = estimator_path.read_text(encoding="utf-8")
    if estimator_path.suffix.lower() == ".json":
        return G1Card.model_validate_json(raw_text)
    payload = yaml.safe_load(raw_text)
    return G1Card.model_validate(payload)


def _coerce_estimator(estimator_or_path: G1Card | Mapping[str, Any] | Path) -> G1Card:
    if isinstance(estimator_or_path, G1Card):
        return estimator_or_path
    if isinstance(estimator_or_path, Path):
        return load_estimator(estimator_or_path)
    return G1Card.model_validate(dict(estimator_or_path))


def display_estimator(estimator_or_path: G1Card | Mapping[str, Any] | Path) -> dict[str, Any]:
    """Return the estimator payload plus the digest shown to the operator."""

    estimator = _coerce_estimator(estimator_or_path)
    return {
        "surface_id": SURFACE_ID,
        "estimator_id": str(estimator.card_id),
        "decision_card_digest": compute_model_digest(estimator),
        "estimator": estimator.model_dump(mode="json"),
    }


def submit_verdict(
    estimator_id: str,
    verdict_payload: Section04_5OperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section04_5OperatorVerdict:
    """Submit an operator verdict for a displayed run-budget estimator."""

    if transport not in _TRANSPORTS:
        raise GateError("transport_invalid", f"unsupported Section 04.5 transport: {transport}")
    if isinstance(verdict_payload, Section04_5OperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        payload.setdefault("estimator_id", estimator_id)
        verdict = Section04_5OperatorVerdict.model_validate(payload)
    if verdict.estimator_id != estimator_id.strip():
        raise GateError(
            "estimator_id_mismatch",
            "verdict estimator_id does not match the displayed Section 04.5 estimator",
        )
    return verdict


def resume_from_verdict(
    estimator_or_path: G1Card | Mapping[str, Any] | Path,
    verdict: Section04_5OperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 04.5 verdict after digest verification."""

    displayed = display_estimator(estimator_or_path)
    if verdict.estimator_id != displayed["estimator_id"]:
        raise GateError(
            "estimator_id_mismatch",
            "verdict estimator_id does not match the Section 04.5 estimator",
        )
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 04.5 estimator digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "estimator": displayed["estimator"],
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_estimator",
    "load_estimator",
    "resume_from_verdict",
    "submit_verdict",
]
