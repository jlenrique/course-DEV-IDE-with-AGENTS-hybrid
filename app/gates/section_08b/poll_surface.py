"""Section 08B G3B storyboard/live-URL review poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.decision_cards.g3 import G3Card
from app.models.operator_verdict_section_08b import (
    SECTION_08B_SURFACE_ID,
    Section08BOperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_08B_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_08b_g3b_poll",
    mandatory_transports=["cli", "http"],
    optional_transports=["mcp-stdio"],
    alias_of="G3",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 08B G3B."""
    return "section_08b_g3b_poll"


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


def load_storyboard_b(storyboard_path: Path) -> G3Card:
    """Load a Section 08B G3 decision card from JSON or YAML."""

    raw_text = storyboard_path.read_text(encoding="utf-8")
    if storyboard_path.suffix.lower() == ".json":
        return G3Card.model_validate_json(raw_text)
    payload = yaml.safe_load(raw_text)
    return G3Card.model_validate(payload)


def _coerce_storyboard_b(storyboard_or_path: G3Card | Mapping[str, Any] | Path) -> G3Card:
    if isinstance(storyboard_or_path, G3Card):
        return storyboard_or_path
    if isinstance(storyboard_or_path, Path):
        return load_storyboard_b(storyboard_or_path)
    return G3Card.model_validate(dict(storyboard_or_path))


def display_storyboard_b(
    storyboard_or_path: G3Card | Mapping[str, Any] | Path,
) -> dict[str, Any]:
    """Return the Storyboard B payload plus the digest shown to the operator."""

    storyboard = _coerce_storyboard_b(storyboard_or_path)
    return {
        "surface_id": SURFACE_ID,
        "storyboard_id": str(storyboard.card_id),
        "decision_card_digest": compute_model_digest(storyboard),
        "decision_card": storyboard.model_dump(mode="json"),
    }


def submit_verdict(
    storyboard_id: str,
    verdict_payload: Section08BOperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section08BOperatorVerdict:
    """Submit an operator verdict for the displayed Storyboard B card."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 08B supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_storyboard_id = storyboard_id.strip()
    if not normalized_storyboard_id:
        raise GateError("storyboard_id_missing", "storyboard_id must be non-empty")
    if isinstance(verdict_payload, Section08BOperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("storyboard_id")
        if supplied_id is not None and str(supplied_id).strip() != normalized_storyboard_id:
            raise GateError(
                "storyboard_id_mismatch",
                "verdict storyboard_id does not match submitted storyboard_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["storyboard_id"] = normalized_storyboard_id
        verdict = Section08BOperatorVerdict.model_validate(payload)
    if verdict.storyboard_id != normalized_storyboard_id:
        raise GateError(
            "storyboard_id_mismatch",
            "verdict storyboard_id does not match submitted storyboard_id",
        )
    return verdict


def resume_from_verdict(
    storyboard_or_path: G3Card | Mapping[str, Any] | Path,
    verdict: Section08BOperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 08B verdict after digest verification."""

    displayed = display_storyboard_b(storyboard_or_path)
    if verdict.storyboard_id != displayed["storyboard_id"]:
        raise GateError(
            "storyboard_id_mismatch",
            "verdict storyboard_id does not match the displayed Section 08B card",
        )
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 08B card digest",
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
    "display_storyboard_b",
    "load_storyboard_b",
    "resume_from_verdict",
    "submit_verdict",
]
