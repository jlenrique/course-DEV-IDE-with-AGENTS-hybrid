"""Section 07D G2.5 motion-plan polling HIL surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.decision_cards.g2c import G2CCard
from app.models.operator_verdict_section_07d import (
    SECTION_07D_SURFACE_ID,
    Section07DOperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_07D_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_07d_g2_5_motion_plan_polling",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
    alias_of="G2C",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 07D G2.5."""
    return "section_07d_g2_5_motion_plan_polling"


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


def load_motion_plan_card(motion_plan_path: Path) -> G2CCard:
    """Load a Section 07D G2C decision card from JSON or YAML."""

    raw_text = motion_plan_path.read_text(encoding="utf-8")
    if motion_plan_path.suffix.lower() == ".json":
        return G2CCard.model_validate_json(raw_text)
    payload = yaml.safe_load(raw_text)
    return G2CCard.model_validate(payload)


def _coerce_motion_plan_card(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
) -> G2CCard:
    if isinstance(g2c_card_or_path, G2CCard):
        return g2c_card_or_path
    if isinstance(g2c_card_or_path, Path):
        return load_motion_plan_card(g2c_card_or_path)
    return G2CCard.model_validate(dict(g2c_card_or_path))


def _motion_plan_status(g2c_card: G2CCard) -> Literal["pending", "completed"]:
    if g2c_card.readiness_status == "ready":
        return "completed"
    return "pending"


def display_motion_plan_status(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
) -> dict[str, Any]:
    """Return motion-plan generation status plus the digest shown to the operator."""

    g2c_card = _coerce_motion_plan_card(g2c_card_or_path)
    return {
        "surface_id": SURFACE_ID,
        "motion_plan_id": str(g2c_card.card_id),
        "motion_plan_status": _motion_plan_status(g2c_card),
        "decision_card_digest": compute_model_digest(g2c_card),
        "decision_card": g2c_card.model_dump(mode="json"),
    }


def submit_verdict(
    motion_plan_id: str,
    verdict_payload: Section07DOperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section07DOperatorVerdict:
    """Submit an operator verdict for the completed motion-plan card."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 07D supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_motion_plan_id = motion_plan_id.strip()
    if not normalized_motion_plan_id:
        raise GateError("motion_plan_id_missing", "motion_plan_id must be non-empty")
    if isinstance(verdict_payload, Section07DOperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("motion_plan_id")
        if supplied_id is not None and str(supplied_id).strip() != normalized_motion_plan_id:
            raise GateError(
                "motion_plan_id_mismatch",
                "verdict motion_plan_id does not match submitted motion_plan_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["motion_plan_id"] = normalized_motion_plan_id
        verdict = Section07DOperatorVerdict.model_validate(payload)
    if verdict.motion_plan_id != normalized_motion_plan_id:
        raise GateError(
            "motion_plan_id_mismatch",
            "verdict motion_plan_id does not match submitted motion_plan_id",
        )
    return verdict


def resume_from_verdict(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
    verdict: Section07DOperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 07D verdict after digest verification."""

    displayed = display_motion_plan_status(g2c_card_or_path)
    if verdict.motion_plan_id != displayed["motion_plan_id"]:
        raise GateError(
            "motion_plan_id_mismatch",
            "verdict motion_plan_id does not match the displayed Section 07D card",
        )
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 07D G2C card digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "motion_plan_status": displayed["motion_plan_status"],
        "decision_card": displayed["decision_card"],
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_motion_plan_status",
    "load_motion_plan_card",
    "resume_from_verdict",
    "submit_verdict",
]
