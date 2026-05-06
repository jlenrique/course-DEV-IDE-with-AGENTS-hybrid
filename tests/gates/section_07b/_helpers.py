"""Shared fixtures for Section 07B poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g2c import G2CCard

RUN_ID = UUID("77777777-7777-4777-8777-777777777777")
SLIDE_VARIANT_ID = UUID("88888888-8888-4888-8888-888888888888")
SLIDE_ID = "slide-07"
SUBMITTED_AT = datetime(2026, 5, 6, 10, 30, tzinfo=UTC)


def fixture_per_slide_variant_card() -> G2CCard:
    return G2CCard(
        decision_card_digest="d" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=[SLIDE_ID],
            override_trail=[],
        ),
        card_id=SLIDE_VARIANT_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        readiness_status="ready",
        blocking_issues=[],
        ready_nodes=[SLIDE_ID],
        verb="approve",
    )


__all__ = [
    "RUN_ID",
    "SLIDE_ID",
    "SLIDE_VARIANT_ID",
    "SUBMITTED_AT",
    "fixture_per_slide_variant_card",
]
