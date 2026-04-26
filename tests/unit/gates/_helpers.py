from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.gates.resume_api import compute_decision_card_digest, register_decision_card
from app.models.decision_cards import DecisionCard, DecisionCardMeta, G1Card
from app.models.state.operator_verdict import OperatorVerdict


def sample_card(*, trial_id: UUID) -> DecisionCard:
    return G1Card(
        card_id=UUID("11111111-1111-4111-8111-111111111111"),
        trial_id=trial_id,
        gate_id="G1",
        created_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        drafted_proposal={"action": "open-trial"},
        evidence=[{"kind": "manifest", "node": "04"}],
        risks=["cache cold-start"],
        verb="approve",
        meta=DecisionCardMeta(
            cache_state="healthy",
            affected_nodes=["04", "05"],
            override_trail=[],
            reject_rate=0.25,
        ),
        trial_summary="Trial opened with manifest-backed route and clean cache posture.",
        gate_focus="trial_open",
        opened_by="marcus",
        next_nodes=["05", "06"],
    )


def register_sample_card(*, trial_id: UUID):
    card = sample_card(trial_id=trial_id)
    return register_decision_card(
        card,
        issuance_timestamp=datetime(2026, 4, 26, 12, 1, tzinfo=UTC),
        server_nonce="nonce-001",
    )


def sample_verdict(
    *,
    trial_id: UUID,
    verb: str = "approve",
    digest: str | None = None,
) -> OperatorVerdict:
    stored = register_sample_card(trial_id=trial_id)
    return OperatorVerdict(
        verdict_id=UUID("22222222-2222-4222-8222-222222222222"),
        trial_id=trial_id,
        verb=verb,  # type: ignore[arg-type]
        gate_id="G1",
        card_id=stored.card.card_id,
        operator_id="juanl",
        timestamp=datetime(2026, 4, 26, 12, 2, tzinfo=UTC),
        decision_card_digest=digest or stored.digest,
        edit_payload={"replacement": "new content"} if verb == "edit" else None,
        reject_reason="fails fidelity contract" if verb == "reject" else None,
    )


def digest_for_card(card: DecisionCard) -> str:
    return compute_decision_card_digest(
        card=card,
        trial_id=card.trial_id,
        issuance_timestamp=datetime(2026, 4, 26, 12, 1, tzinfo=UTC),
        server_nonce="nonce-001",
    )
