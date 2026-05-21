"""Party-mode review surfaced as a LangGraph interrupt."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from langgraph.types import Command, interrupt

from app.gates.resume_api import register_decision_card, resume_from_verdict
from app.models.decision_cards import DecisionCard, DecisionCardMeta
from app.models.gates.party_mode_contribution import (
    TRACE_LINK_PATTERN,
    PartyModeContribution,
)
from app.models.state.operator_verdict import OperatorVerdict


def _normalize_contributions(
    contributions: list[PartyModeContribution | dict[str, Any]],
) -> list[PartyModeContribution]:
    return [PartyModeContribution.model_validate(item) for item in contributions]


def build_party_mode_decision_card(
    *,
    contributions: list[PartyModeContribution | dict[str, Any]],
    gate_id: str,
    trial_id: UUID,
) -> DecisionCard:
    """Build the consolidated DecisionCard for a party-mode gate."""
    now = datetime.now(UTC)
    normalized = _normalize_contributions(contributions)
    return DecisionCard(
        card_id=uuid4(),
        trial_id=trial_id,
        gate_id=gate_id,
        created_at=now,
        drafted_proposal={
            "kind": "party_mode_review",
            "personas": [item.persona for item in normalized],
        },
        evidence=[
            {
                "kind": "party_mode_contribution",
                "persona": item.persona,
                "trace_link": item.trace_link,
            }
            for item in normalized
        ],
        risks=["multi-persona review pending operator verdict"],
        verb="approve",
        meta=DecisionCardMeta(
            cache_state="healthy",
            affected_nodes=[],
            override_trail=[],
            reject_rate=0.0,
            party_mode_contributions=normalized,
            consolidated_at=now,
        ),
    )


def party_mode_as_interrupt(
    contributions: list[PartyModeContribution | dict[str, Any]],
    gate_id: str,
    *,
    trial_id: UUID,
) -> DecisionCard:
    """Pause on a consolidated party-mode DecisionCard and resume via OperatorVerdict."""
    card = build_party_mode_decision_card(
        contributions=contributions,
        gate_id=gate_id,
        trial_id=trial_id,
    )
    stored = register_decision_card(card, issuance_timestamp=card.created_at)
    verdict_payload = interrupt(
        {
            "kind": "decision_card",
            "gate_id": gate_id,
            "decision_card": card.model_dump(mode="json"),
            "decision_card_digest": stored.digest,
        }
    )
    verdict = (
        verdict_payload
        if isinstance(verdict_payload, OperatorVerdict)
        else OperatorVerdict.model_validate(verdict_payload)
    )
    command = resume_from_verdict(verdict)
    if not isinstance(command, Command):
        raise TypeError("resume_from_verdict must return a LangGraph Command")
    return card


def finding_record_has_trace_link(finding_record: dict[str, Any]) -> bool:
    """Return whether a finding record carries FR42-compliant trace evidence."""
    trace_link = finding_record.get("trace_link")
    return isinstance(trace_link, str) and TRACE_LINK_PATTERN.fullmatch(trace_link) is not None


__all__ = [
    "build_party_mode_decision_card",
    "finding_record_has_trace_link",
    "party_mode_as_interrupt",
]
