"""Gate verdict resume substrate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from langgraph.types import Command

from app.gates.errors import GateError
from app.gates.guardrails import assert_scheduler_modules_not_loaded
from app.models.decision_cards import DecisionCard, DecisionCardBase
from app.models.state._base import enforce_tz_aware
from app.models.state.operator_verdict import OperatorVerdict

assert_scheduler_modules_not_loaded()


@dataclass(frozen=True)
class StoredDecisionCard:
    card: DecisionCard | DecisionCardBase
    issued_at: datetime
    server_nonce: str
    digest: str


_CARD_STORE: dict[tuple[UUID, str], StoredDecisionCard] = {}
_CONSUMED_NONCES: set[str] = set()


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _isoformat_utc(value: datetime) -> str:
    value = enforce_tz_aware(value)
    rendered = value.astimezone(UTC).isoformat()
    return rendered.replace("+00:00", "Z")


def compute_decision_card_digest(
    *,
    card: DecisionCard | DecisionCardBase,
    trial_id: UUID,
    issuance_timestamp: datetime,
    server_nonce: str,
) -> str:
    payload = {
        "card_content_canonical_json": card.model_dump(mode="json"),
        "trial_run_id": str(trial_id),
        "issuance_timestamp_iso": _isoformat_utc(issuance_timestamp),
        "server_nonce": server_nonce,
    }
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


def register_decision_card(
    card: DecisionCard | DecisionCardBase,
    *,
    issuance_timestamp: datetime | None = None,
    server_nonce: str | None = None,
) -> StoredDecisionCard:
    issued_at = issuance_timestamp or datetime.now(UTC)
    issued_at = enforce_tz_aware(issued_at)
    nonce = server_nonce or uuid4().hex
    stored = StoredDecisionCard(
        card=card,
        issued_at=issued_at,
        server_nonce=nonce,
        digest=compute_decision_card_digest(
            card=card,
            trial_id=card.trial_id,
            issuance_timestamp=issued_at,
            server_nonce=nonce,
        ),
    )
    _CARD_STORE[(card.trial_id, card.gate_id)] = stored
    return stored


def clear_resume_registry() -> None:
    _CARD_STORE.clear()
    _CONSUMED_NONCES.clear()


def get_registered_decision_card(trial_id: UUID, gate_id: str) -> StoredDecisionCard | None:
    return _CARD_STORE.get((trial_id, gate_id))


def _resume_payload(verdict: OperatorVerdict) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "verb": verdict.verb,
        "trial_id": str(verdict.trial_id),
        "gate_id": verdict.gate_id,
        "card_id": str(verdict.card_id),
        "operator_id": verdict.operator_id,
        "verdict_id": str(verdict.verdict_id),
        "timestamp": _isoformat_utc(verdict.timestamp),
    }
    if verdict.edit_payload is not None:
        payload["edit_payload"] = verdict.edit_payload
    if verdict.reject_reason is not None:
        payload["reject_reason"] = verdict.reject_reason
    return payload


def build_transport_response(
    *,
    command: Command,
    verdict: OperatorVerdict,
    transport_kind: str,
) -> dict[str, Any]:
    stored = get_registered_decision_card(verdict.trial_id, verdict.gate_id)
    meta = stored.card.meta.model_dump(mode="json") if stored is not None else None
    from app.ledger.emitter import emit_ledger_event
    from app.ledger.events import build_verdict_ledger_event

    emit_ledger_event(build_verdict_ledger_event(verdict, transport_kind=transport_kind))
    ledger_event = {
        "kind": "verdict",
        "trial_id": str(verdict.trial_id),
        "gate_id": verdict.gate_id,
        "operator_id": verdict.operator_id,
        "verb": verdict.verb,
        "transport_kind": transport_kind,
    }
    trace = {
        "span_name": "resume_from_verdict",
        "span_attributes": {
            "trial_id": str(verdict.trial_id),
            "gate_id": verdict.gate_id,
            "operator_id": verdict.operator_id,
            "transport_kind": transport_kind,
        },
    }
    return {
        "status": "accepted",
        "resumed_at": _isoformat_utc(datetime.now(UTC)),
        "resume": command.resume,
        "ledger_event": ledger_event,
        "trace": trace,
        "decision_card_meta": meta,
    }


def resume_from_verdict(verdict: OperatorVerdict) -> Command:
    """Resume a paused graph with a validated operator verdict."""
    stored = _CARD_STORE.get((verdict.trial_id, verdict.gate_id))
    if stored is None:
        raise GateError(
            "card_missing",
            f"no DecisionCard registered for trial_id={verdict.trial_id} gate_id={verdict.gate_id}",
        )
    if verdict.card_id != stored.card.card_id:
        raise GateError(
            "card_id_mismatch",
            "verdict card_id="
            f"{verdict.card_id} does not match stored card_id={stored.card.card_id}",
        )
    if verdict.decision_card_digest != stored.digest:
        raise GateError(
            "digest_mismatch",
            "verdict decision_card_digest does not match the stored DecisionCard digest",
        )
    nonce_key = f"{verdict.trial_id}:{stored.server_nonce}"
    if nonce_key in _CONSUMED_NONCES:
        raise GateError(
            "replay_detected",
            f"server_nonce for trial_id={verdict.trial_id} has already been consumed",
        )
    _CONSUMED_NONCES.add(nonce_key)
    return Command(resume=_resume_payload(verdict))


__all__ = [
    "build_transport_response",
    "StoredDecisionCard",
    "clear_resume_registry",
    "compute_decision_card_digest",
    "get_registered_decision_card",
    "register_decision_card",
    "resume_from_verdict",
]
