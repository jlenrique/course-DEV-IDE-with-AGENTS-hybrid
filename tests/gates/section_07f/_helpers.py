"""Shared fixtures for Section 07F poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g2c import G2CCard

RUN_ID = UUID("66666666-6666-4666-8666-666666666666")
MOTION_CLIP_ID = UUID("77777777-7777-4777-8777-777777777777")
SUBMITTED_AT = datetime(2026, 5, 6, 10, 0, tzinfo=UTC)


def fixture_motion_clip_card() -> G2CCard:
    return G2CCard(
        decision_card_digest="c" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["07F"],
            override_trail=[],
        ),
        card_id=MOTION_CLIP_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        readiness_status="ready",
        blocking_issues=[],
        ready_nodes=["motion-clip-approval"],
        verb="approve",
    )


__all__ = ["MOTION_CLIP_ID", "RUN_ID", "SUBMITTED_AT", "fixture_motion_clip_card"]
