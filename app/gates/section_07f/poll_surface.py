"""Section 07F G2F motion gate poll-surface helpers."""

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
from app.models.operator_verdict_section_07f import (
    SECTION_07F_SURFACE_ID,
    Section07FOperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_07F_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_07f_g2f_motion_gate",
    mandatory_transports=["cli", "http"],
    optional_transports=["mcp-stdio"],
    alias_of="G2C",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 07F G2F."""
    return "section_07f_g2f_motion_gate"


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


def load_motion_clip(motion_clip_path: Path) -> G2CCard:
    """Load a Section 07F G2C decision card from JSON or YAML."""

    raw_text = motion_clip_path.read_text(encoding="utf-8")
    if motion_clip_path.suffix.lower() == ".json":
        return G2CCard.model_validate_json(raw_text)
    payload = yaml.safe_load(raw_text)
    return G2CCard.model_validate(payload)


def _coerce_motion_clip(g2c_card_or_path: G2CCard | Mapping[str, Any] | Path) -> G2CCard:
    if isinstance(g2c_card_or_path, G2CCard):
        return g2c_card_or_path
    if isinstance(g2c_card_or_path, Path):
        return load_motion_clip(g2c_card_or_path)
    return G2CCard.model_validate(dict(g2c_card_or_path))


def display_motion_clip(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
) -> dict[str, Any]:
    """Return the motion-clip payload plus the digest shown to the operator."""

    motion_clip = _coerce_motion_clip(g2c_card_or_path)
    return {
        "surface_id": SURFACE_ID,
        "motion_clip_id": str(motion_clip.card_id),
        "decision_card_digest": compute_model_digest(motion_clip),
        "decision_card": motion_clip.model_dump(mode="json"),
    }


def submit_verdict(
    motion_clip_id: str,
    verdict_payload: Section07FOperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section07FOperatorVerdict:
    """Submit an operator verdict for the displayed motion clip."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 07F supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_motion_clip_id = motion_clip_id.strip()
    if not normalized_motion_clip_id:
        raise GateError("motion_clip_id_missing", "motion_clip_id must be non-empty")
    if isinstance(verdict_payload, Section07FOperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("motion_clip_id")
        if (
            supplied_id is not None
            and str(supplied_id).strip() != normalized_motion_clip_id
        ):
            raise GateError(
                "motion_clip_id_mismatch",
                "verdict motion_clip_id does not match submitted motion_clip_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["motion_clip_id"] = normalized_motion_clip_id
        verdict = Section07FOperatorVerdict.model_validate(payload)
    if verdict.motion_clip_id != normalized_motion_clip_id:
        raise GateError(
            "motion_clip_id_mismatch",
            "verdict motion_clip_id does not match submitted motion_clip_id",
        )
    return verdict


def resume_from_verdict(
    g2c_card_or_path: G2CCard | Mapping[str, Any] | Path,
    verdict: Section07FOperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 07F verdict after digest verification."""

    displayed = display_motion_clip(g2c_card_or_path)
    if verdict.motion_clip_id != displayed["motion_clip_id"]:
        raise GateError(
            "motion_clip_id_mismatch",
            "verdict motion_clip_id does not match the displayed Section 07F card",
        )
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 07F card digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "decision_card": displayed["decision_card"],
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_motion_clip",
    "load_motion_clip",
    "resume_from_verdict",
    "submit_verdict",
]
