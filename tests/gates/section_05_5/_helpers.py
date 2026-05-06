"""Shared fixtures for Section 05.5 poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g2c import G2CCard

RUN_ID = UUID("55555555-5555-4555-8555-555555555555")
SLIDE_ID = UUID("05050505-0505-4505-8505-050505050505")
SUBMITTED_AT = datetime(2026, 5, 6, 10, 5, tzinfo=UTC)


def fixture_per_slide_mode_card() -> G2CCard:
    return G2CCard(
        decision_card_digest="b" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["05.5"],
            override_trail=[],
        ),
        card_id=SLIDE_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        readiness_status="ready",
        blocking_issues=[],
        ready_nodes=["slide-001", "slide-002"],
        verb="approve",
    )


__all__ = [
    "RUN_ID",
    "SLIDE_ID",
    "SUBMITTED_AT",
    "fixture_per_slide_mode_card",
]

