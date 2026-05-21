"""Section 07B G2M per-slide A/B variant poll-surface helpers."""

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
from app.models.operator_verdict_section_07b import (
    SECTION_07B_SURFACE_ID,
    Section07BOperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_07B_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_07b_g2m_per_slide_variant",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
    alias_of="G2C",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 07B G2M."""
    return "section_07b_g2m_per_slide_variant"


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


def load_per_slide_variant(g2c_card_path: Path) -> G2CCard:
    """Load a Section 07B G2C decision card from JSON or YAML."""

    raw_text = g2c_card_path.read_text(encoding="utf-8")
    if g2c_card_path.suffix.lower() == ".json":
        return G2CCard.model_validate_json(raw_text)
    payload = yaml.safe_load(raw_text)
    return G2CCard.model_validate(payload)


def _coerce_per_slide_variant(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
) -> G2CCard:
    if isinstance(g2c_card_or_path, G2CCard):
        return g2c_card_or_path
    if isinstance(g2c_card_or_path, Path):
        return load_per_slide_variant(g2c_card_or_path)
    return G2CCard.model_validate(dict(g2c_card_or_path))


def _per_slide_variant_payload(g2c_card: G2CCard) -> dict[str, Any]:
    return {
        "readiness_status": g2c_card.readiness_status,
        "ready_nodes": list(g2c_card.ready_nodes),
        "blocking_issues": list(g2c_card.blocking_issues),
    }


def _slide_ids(g2c_card: G2CCard) -> list[str]:
    slide_ids = list(g2c_card.ready_nodes)
    if slide_ids:
        return slide_ids
    return list(g2c_card.meta.affected_nodes)


def display_per_slide_variant(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
) -> dict[str, Any]:
    """Return A/B variant review payload plus the digest shown to the operator."""

    g2c_card = _coerce_per_slide_variant(g2c_card_or_path)
    slide_ids = _slide_ids(g2c_card)
    return {
        "surface_id": SURFACE_ID,
        "slide_variant_id": str(g2c_card.card_id),
        "slide_id": slide_ids[0] if len(slide_ids) == 1 else None,
        "slide_ids": slide_ids,
        "decision_card_digest": compute_model_digest(g2c_card),
        "decision_card": g2c_card.model_dump(mode="json"),
        "per_slide_variant_payload": _per_slide_variant_payload(g2c_card),
    }


def submit_verdict(
    slide_id: str,
    verdict_payload: Section07BOperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section07BOperatorVerdict:
    """Submit an operator verdict for one displayed A/B slide variant."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 07B supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_slide_id = slide_id.strip()
    if not normalized_slide_id:
        raise GateError("slide_id_missing", "slide_id must be non-empty")
    if isinstance(verdict_payload, Section07BOperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("slide_id")
        if (
            supplied_id is not None
            and str(supplied_id).strip() != normalized_slide_id
        ):
            raise GateError(
                "slide_id_mismatch",
                "verdict slide_id does not match submitted slide_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["slide_id"] = normalized_slide_id
        verdict = Section07BOperatorVerdict.model_validate(payload)
    if verdict.slide_id != normalized_slide_id:
        raise GateError(
            "slide_id_mismatch",
            "verdict slide_id does not match submitted slide_id",
        )
    return verdict


def resume_from_verdict(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
    verdict: Section07BOperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 07B verdict after digest verification."""

    displayed = display_per_slide_variant(g2c_card_or_path)
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 07B card digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "slide_id": verdict.slide_id,
        "decision_card": displayed["decision_card"],
        "per_slide_variant_payload": displayed["per_slide_variant_payload"],
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_per_slide_variant",
    "load_per_slide_variant",
    "resume_from_verdict",
    "submit_verdict",
]
