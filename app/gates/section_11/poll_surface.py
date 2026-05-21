"""Section 11 G4A ElevenLabs voice-selection poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel

from app.gates.errors import GateError
from app.models.decision_cards.g4 import G4Card
from app.models.operator_verdict_section_11 import (
    SECTION_11_SURFACE_ID,
    Section11OperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_11_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_TRANSPORTS: frozenset[str] = frozenset({"cli", "http", "mcp-stdio"})


@parity_contract(
    surface_id="section_11_g4a_voice_selection",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
    alias_of="G4",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 11 G4A."""
    return "section_11_g4a_voice_selection"


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


def load_voice_selection(g4_card_path: Path) -> G4Card:
    """Load a Section 11 G4 decision card from JSON or YAML."""

    raw_text = g4_card_path.read_text(encoding="utf-8")
    if g4_card_path.suffix.lower() == ".json":
        return G4Card.model_validate_json(raw_text)
    payload = yaml.safe_load(raw_text)
    return G4Card.model_validate(payload)


def _coerce_voice_selection(g4_card_or_path: G4Card | Mapping[str, Any] | Path) -> G4Card:
    if isinstance(g4_card_or_path, G4Card):
        return g4_card_or_path
    if isinstance(g4_card_or_path, Path):
        return load_voice_selection(g4_card_or_path)
    return G4Card.model_validate(dict(g4_card_or_path))


def _voice_selection_payload(g4_card: G4Card) -> dict[str, Any]:
    return {
        "artifact_paths": list(g4_card.artifact_paths),
        "outcome_summary": g4_card.outcome_summary,
        "final_status": g4_card.final_status,
    }


def display_voice_candidates(
    g4_card_or_path: G4Card | Mapping[str, Any] | Path,
) -> dict[str, Any]:
    """Return voice-selection candidates plus the digest shown to the operator."""

    g4_card = _coerce_voice_selection(g4_card_or_path)
    return {
        "surface_id": SURFACE_ID,
        "voice_selection_id": str(g4_card.card_id),
        "decision_card_digest": compute_model_digest(g4_card),
        "decision_card": g4_card.model_dump(mode="json"),
        "voice_selection_payload": _voice_selection_payload(g4_card),
    }


def submit_verdict(
    voice_selection_id: str,
    verdict_payload: Section11OperatorVerdict | Mapping[str, Any],
    transport: TransportName,
) -> Section11OperatorVerdict:
    """Submit an operator verdict for displayed voice candidates."""

    if transport not in _TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 11 supports cli/http/mcp-stdio verdict submission, got {transport!r}",
        )
    normalized_voice_selection_id = voice_selection_id.strip()
    if not normalized_voice_selection_id:
        raise GateError(
            "voice_selection_id_missing",
            "voice_selection_id must be non-empty",
        )
    if isinstance(verdict_payload, Section11OperatorVerdict):
        verdict = verdict_payload
    else:
        payload = dict(verdict_payload)
        supplied_id = payload.get("voice_selection_id")
        if (
            supplied_id is not None
            and str(supplied_id).strip() != normalized_voice_selection_id
        ):
            raise GateError(
                "voice_selection_id_mismatch",
                "verdict voice_selection_id does not match submitted voice_selection_id",
            )
        payload["surface_id"] = SURFACE_ID
        payload["voice_selection_id"] = normalized_voice_selection_id
        verdict = Section11OperatorVerdict.model_validate(payload)
    if verdict.voice_selection_id != normalized_voice_selection_id:
        raise GateError(
            "voice_selection_id_mismatch",
            "verdict voice_selection_id does not match submitted voice_selection_id",
        )
    return verdict


def resume_from_verdict(
    g4_card_or_path: G4Card | Mapping[str, Any] | Path,
    verdict: Section11OperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 11 verdict after digest verification."""

    displayed = display_voice_candidates(g4_card_or_path)
    if verdict.voice_selection_id != displayed["voice_selection_id"]:
        raise GateError(
            "voice_selection_id_mismatch",
            "verdict voice_selection_id does not match the displayed Section 11 card",
        )
    if verdict.decision_card_digest != displayed["decision_card_digest"]:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 11 card digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "decision_card": displayed["decision_card"],
        "voice_selection_payload": displayed["voice_selection_payload"],
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_voice_candidates",
    "load_voice_selection",
    "resume_from_verdict",
    "submit_verdict",
]
