"""Section 04.55 G1.5 run-constants lock poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.gates.errors import GateError
from app.models.operator_verdict_section_04_55 import (
    SECTION_04_55_SURFACE_ID,
    Section04_55OperatorVerdict,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_04_55_SURFACE_ID
TransportName = Literal["cli", "http"]
_ALLOWED_TRANSPORTS = frozenset({"cli", "http"})
_RUN_CONSTANTS_ID_FIELDS = ("run_constants_id", "run_id", "RUN_ID")


class _RunConstantsReviewPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    run_constants_id: str = Field(..., min_length=1)
    constants: dict[str, Any] = Field(...)

    @field_validator("run_constants_id")
    @classmethod
    def _strip_non_empty_id(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("run_constants_id must be non-empty")
        return stripped


@parity_contract(
    surface_id="section_04_55_g1_5_run_constants",
    mandatory_transports=["cli", "http"],
    optional_transports=[],
    alias_of="G1",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 04.55 G1.5."""
    return "section_04_55_g1_5_run_constants"


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


def load_run_constants(constants_path: Path) -> dict[str, Any]:
    """Load a run-constants YAML file with explicit UTF-8 decoding."""

    payload = yaml.safe_load(constants_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise GateError(
            "run_constants_invalid",
            "run-constants payload must be a mapping",
        )
    return dict(payload)


def _coerce_run_constants(constants_or_path: Mapping[str, Any] | Path) -> dict[str, Any]:
    if isinstance(constants_or_path, Path):
        return load_run_constants(constants_or_path)
    return dict(constants_or_path)


def _extract_run_constants_id(constants: Mapping[str, Any]) -> str:
    for field_name in _RUN_CONSTANTS_ID_FIELDS:
        value = constants.get(field_name)
        if value is None:
            continue
        rendered = str(value).strip()
        if rendered:
            return rendered
    raise GateError(
        "run_constants_id_missing",
        "run constants must include non-empty run_constants_id, run_id, or RUN_ID",
    )


def _review_payload(constants: Mapping[str, Any]) -> _RunConstantsReviewPayload:
    return _RunConstantsReviewPayload(
        run_constants_id=_extract_run_constants_id(constants),
        constants=dict(constants),
    )


def display_run_constants(constants_or_path: Mapping[str, Any] | Path) -> dict[str, Any]:
    """Return the run-constants payload plus the digest shown to the operator."""

    constants = _coerce_run_constants(constants_or_path)
    payload = _review_payload(constants)
    return {
        "surface_id": SURFACE_ID,
        "run_constants_id": payload.run_constants_id,
        "decision_card_digest": compute_model_digest(payload),
        "run_constants": constants,
    }


def submit_verdict(
    constants_id: str,
    verdict_payload: Mapping[str, Any],
    transport: str,
) -> Section04_55OperatorVerdict:
    """Submit an operator verdict for displayed run constants."""

    if transport not in _ALLOWED_TRANSPORTS:
        raise GateError(
            "unsupported_transport",
            f"Section 04.55 supports cli/http verdict submission, got {transport!r}",
        )
    normalized_constants_id = constants_id.strip()
    if not normalized_constants_id:
        raise GateError(
            "run_constants_id_missing",
            "constants_id must be non-empty",
        )

    payload = dict(verdict_payload)
    supplied_id = payload.get("run_constants_id")
    if supplied_id is not None and str(supplied_id).strip() != normalized_constants_id:
        raise GateError(
            "run_constants_id_mismatch",
            "verdict run_constants_id does not match submitted constants_id",
        )
    payload["run_constants_id"] = normalized_constants_id
    return Section04_55OperatorVerdict.model_validate(payload)


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_run_constants",
    "load_run_constants",
    "submit_verdict",
]
