"""Section 04A G1A per-plan-unit ratification poll surface."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

import yaml
from pydantic import BaseModel, ValidationError

from app.gates.errors import GateError
from app.models.decision_cards._base import DecisionCardMeta
from app.models.decision_cards.g1 import G1Card
from app.models.operator_verdict_section_04a import (
    SECTION_04A_SURFACE_ID,
    PlanUnitEditPayload,
    Section04AOperatorVerdict,
)
from app.parity.contracts import parity_contract
from marcus.lesson_plan.schema import PlanUnit

SURFACE_ID = SECTION_04A_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_CARD_CREATED_AT = datetime(2026, 5, 5, 12, 0, tzinfo=UTC)
_EDITABLE_PLAN_UNIT_FIELDS = frozenset(
    {
        "blueprint_signoff",
        "dials",
        "event_type",
        "gaps",
        "modality_ref",
        "rationale",
        "scope_decision",
        "source_fitness_diagnosis",
        "weather_band",
    }
)


@parity_contract(
    surface_id="section_04a_g1a_poll",
    mandatory_transports=["cli"],
    optional_transports=["http", "mcp-stdio"],
    alias_of="G1",
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 04A G1A."""
    return "section_04a_g1a_poll"


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


def load_plan_unit(plan_unit_path: Path) -> PlanUnit:
    """Load a Section 04A plan-unit JSON/YAML file with explicit UTF-8 decoding."""

    payload = yaml.safe_load(plan_unit_path.read_text(encoding="utf-8"))
    return PlanUnit.model_validate(payload)


def _coerce_plan_unit(plan_unit_or_path: PlanUnit | Path) -> PlanUnit:
    if isinstance(plan_unit_or_path, PlanUnit):
        return plan_unit_or_path
    return load_plan_unit(plan_unit_or_path)


def _deterministic_uuid4(seed: str) -> UUID:
    raw = bytearray(hashlib.sha256(seed.encode("utf-8")).digest()[:16])
    raw[6] = (raw[6] & 0x0F) | 0x40
    raw[8] = (raw[8] & 0x3F) | 0x80
    return UUID(bytes=bytes(raw))


def _g1_card_payload(plan_unit: PlanUnit) -> dict[str, Any]:
    card_id = _deterministic_uuid4(f"section-04a:{plan_unit.unit_id}:card")
    trial_id = _deterministic_uuid4(f"section-04a:{plan_unit.unit_id}:trial")
    return {
        "schema_version": "v1",
        "card_id": card_id,
        "trial_id": trial_id,
        "gate_id": "G1",
        "gate_focus": "trial_open",
        "created_at": _CARD_CREATED_AT,
        "drafted_proposal": {"plan_unit": plan_unit.model_dump(mode="json")},
        "evidence": [],
        "trial_summary": f"Ratify plan unit {plan_unit.unit_id}: {plan_unit.event_type}",
        "opened_by": "marcus",
        "next_nodes": [plan_unit.event_type],
        "verb": "approve",
        "meta": DecisionCardMeta(
            cache_state="healthy",
            affected_nodes=[plan_unit.unit_id],
            override_trail=[],
        ),
    }


def _compute_decision_card_digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(
            {
                key: (
                    value.model_dump(mode="json")
                    if isinstance(value, BaseModel)
                    else value
                )
                for key, value in payload.items()
            },
            sort_keys=True,
            separators=(",", ":"),
            default=str,
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()


def build_g1_card(plan_unit: PlanUnit) -> G1Card:
    """Build the deterministic G1 card reviewed by the operator."""

    payload = _g1_card_payload(plan_unit)
    return G1Card(
        **payload,
        decision_card_digest=_compute_decision_card_digest(payload),
    )


def display_plan_unit(plan_unit_or_path: PlanUnit | Path) -> dict[str, Any]:
    """Return the plan-unit payload plus the G1 card digest shown to the operator."""

    plan_unit = _coerce_plan_unit(plan_unit_or_path)
    decision_card = build_g1_card(plan_unit)
    return {
        "surface_id": SURFACE_ID,
        "decision_card_digest": decision_card.decision_card_digest,
        "decision_card": decision_card.model_dump(mode="json"),
        "plan_unit": plan_unit.model_dump(mode="json"),
    }


def apply_plan_unit_edit(
    plan_unit: PlanUnit,
    edit_payload: PlanUnitEditPayload,
) -> PlanUnit:
    """Apply plan-unit edits, then re-validate the complete PlanUnit."""

    unexpected_fields = set(edit_payload.updates).difference(_EDITABLE_PLAN_UNIT_FIELDS)
    if unexpected_fields:
        rendered = ", ".join(sorted(unexpected_fields))
        raise GateError(
            "plan_unit_edit_invalid",
            f"edit contains non-editable plan-unit field(s): {rendered}",
        )
    updated_payload = plan_unit.model_dump(mode="json")
    updated_payload.update(edit_payload.updates)
    try:
        return PlanUnit.model_validate(updated_payload)
    except ValidationError as exc:
        raise GateError(
            "plan_unit_edit_invalid",
            f"edited plan unit failed Section 04A validation: {exc}",
        ) from exc


def _plan_unit_for_verdict(
    plan_unit: PlanUnit,
    verdict: Section04AOperatorVerdict,
) -> PlanUnit:
    if verdict.verb == "edit":
        if verdict.edit_payload is None:
            raise GateError("plan_unit_edit_missing", "edit verdict requires edit_payload")
        return apply_plan_unit_edit(plan_unit, verdict.edit_payload)
    return plan_unit


def submit_verdict(
    plan_unit_id: str,
    verdict_payload: dict[str, Any],
    transport: TransportName,
) -> Section04AOperatorVerdict:
    """Submit an operator verdict for one displayed plan unit."""

    if transport not in {"cli", "http", "mcp-stdio"}:
        raise GateError("unsupported_transport", f"unsupported transport={transport!r}")
    if (
        "plan_unit_id" in verdict_payload
        and verdict_payload["plan_unit_id"] != plan_unit_id
    ):
        raise GateError(
            "plan_unit_id_mismatch",
            "verdict payload plan_unit_id does not match submitted plan_unit_id",
        )
    return Section04AOperatorVerdict.model_validate(
        {
            **verdict_payload,
            "surface_id": SURFACE_ID,
            "plan_unit_id": plan_unit_id,
        }
    )


def resume_from_verdict(
    plan_unit_or_path: PlanUnit | Path,
    verdict: Section04AOperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 04A verdict after digest verification."""

    plan_unit = _coerce_plan_unit(plan_unit_or_path)
    if verdict.plan_unit_id != plan_unit.unit_id:
        raise GateError(
            "plan_unit_id_mismatch",
            "verdict plan_unit_id does not match the displayed plan unit",
        )
    resumed_plan_unit = _plan_unit_for_verdict(plan_unit, verdict)
    expected_digest = build_g1_card(resumed_plan_unit).decision_card_digest
    if verdict.decision_card_digest != expected_digest:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 04A G1 card digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "plan_unit": resumed_plan_unit.model_dump(mode="json"),
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "apply_plan_unit_edit",
    "build_g1_card",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_plan_unit",
    "load_plan_unit",
    "resume_from_verdict",
    "submit_verdict",
]
