"""Canonical Section 02A G0 poll-surface helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ValidationError

from app.composers.section_02a.directive_model import Directive
from app.gates.errors import GateError
from app.models.operator_verdict_section_02a import (
    SECTION_02A_SURFACE_ID,
    DirectiveEditPayload,
    Section02AOperatorVerdict,
    Section02AVerdictVerb,
)
from app.parity.contracts import parity_contract

SURFACE_ID = SECTION_02A_SURFACE_ID
TransportName = Literal["cli", "http", "mcp-stdio"]
_EDITABLE_SOURCE_FIELDS = frozenset(
    {
        "description",
        "excluded_reason",
        "expected_min_words",
        "locator",
        "provider",
        "role",
    }
)


@parity_contract(
    surface_id="section_02a_g0_poll",
    mandatory_transports=["cli", "http", "mcp-stdio"],
    optional_transports=["mcp-subprocess"],
)
def _parity_contract_registration() -> str:
    """Module-level parity-contract registration for Section 02A G0."""
    return "section_02a_g0_poll"


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


def load_directive(directive_path: Path) -> Directive:
    """Load a Section 02A directive YAML file with explicit UTF-8 decoding."""

    payload = yaml.safe_load(directive_path.read_text(encoding="utf-8"))
    return Directive.model_validate(payload)


def _coerce_directive(directive_or_path: Directive | Path) -> Directive:
    if isinstance(directive_or_path, Directive):
        return directive_or_path
    return load_directive(directive_or_path)


def display_directive(directive_or_path: Directive | Path) -> dict[str, Any]:
    """Return the directive payload plus the digest shown to the operator."""

    directive = _coerce_directive(directive_or_path)
    return {
        "surface_id": SURFACE_ID,
        "decision_card_digest": compute_model_digest(directive),
        "directive": directive.model_dump(mode="json"),
    }


def apply_directive_edit(
    directive: Directive,
    edit_payload: DirectiveEditPayload,
) -> Directive:
    """Apply source-level edits, then re-validate the complete directive."""

    source_rows = [source.model_dump(mode="json") for source in directive.sources]
    index_by_src_id = {row["src_id"]: index for index, row in enumerate(source_rows)}
    for src_id, updates in edit_payload.edits.items():
        if src_id not in index_by_src_id:
            raise GateError(
                "directive_edit_invalid",
                f"edit references unknown DirectiveSource src_id={src_id!r}",
            )
        unexpected_fields = set(updates).difference(_EDITABLE_SOURCE_FIELDS)
        if unexpected_fields:
            rendered = ", ".join(sorted(unexpected_fields))
            raise GateError(
                "directive_edit_invalid",
                f"edit for src_id={src_id!r} contains non-editable field(s): {rendered}",
            )
        source_rows[index_by_src_id[src_id]].update(updates)

    updated_payload = directive.model_dump(mode="json")
    updated_payload["sources"] = source_rows
    try:
        return Directive.model_validate(updated_payload)
    except ValidationError as exc:
        raise GateError(
            "directive_edit_invalid",
            f"edited directive failed Section 02A validation: {exc}",
        ) from exc


def _directive_for_verdict(
    directive: Directive,
    *,
    verb: Section02AVerdictVerb,
    edit_payload: DirectiveEditPayload | None,
) -> Directive:
    if verb == "edit":
        if edit_payload is None:
            raise GateError("directive_edit_missing", "edit verdict requires edit_payload")
        return apply_directive_edit(directive, edit_payload)
    return directive


def submit_verdict(
    directive_or_path: Directive | Path,
    *,
    verb: Section02AVerdictVerb,
    operator_id: str,
    edit_payload: DirectiveEditPayload | dict[str, dict[str, Any]] | None = None,
    reject_reason: str | None = None,
    submitted_at: datetime | None = None,
) -> Section02AOperatorVerdict:
    """Submit an operator verdict for a displayed directive."""

    directive = _coerce_directive(directive_or_path)
    typed_edit_payload = (
        None
        if edit_payload is None
        else edit_payload
        if isinstance(edit_payload, DirectiveEditPayload)
        else DirectiveEditPayload(edits=edit_payload)
    )
    resumed_directive = _directive_for_verdict(
        directive,
        verb=verb,
        edit_payload=typed_edit_payload,
    )
    return Section02AOperatorVerdict(
        run_id=resumed_directive.run_id,
        verb=verb,
        operator_id=operator_id,
        submitted_at=submitted_at or resumed_directive.composed_at,
        decision_card_digest=compute_model_digest(resumed_directive),
        edit_payload=typed_edit_payload,
        reject_reason=reject_reason,
    )


def resume_from_verdict(
    directive_or_path: Directive | Path,
    verdict: Section02AOperatorVerdict,
) -> dict[str, Any]:
    """Resume from a Section 02A verdict after digest verification."""

    directive = _coerce_directive(directive_or_path)
    if verdict.run_id != directive.run_id:
        raise GateError(
            "run_id_mismatch",
            f"verdict run_id={verdict.run_id} does not match directive run_id={directive.run_id}",
        )
    resumed_directive = _directive_for_verdict(
        directive,
        verb=verdict.verb,
        edit_payload=verdict.edit_payload,
    )
    expected_digest = compute_model_digest(resumed_directive)
    if verdict.decision_card_digest != expected_digest:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the Section 02A directive digest",
        )
    return {
        "surface_id": SURFACE_ID,
        "verb": verdict.verb,
        "directive": resumed_directive.model_dump(mode="json"),
        "operator_verdict": verdict.model_dump(mode="json"),
    }


__all__ = [
    "SURFACE_ID",
    "TransportName",
    "apply_directive_edit",
    "canonical_model_bytes",
    "compute_model_digest",
    "display_directive",
    "load_directive",
    "resume_from_verdict",
    "submit_verdict",
]
