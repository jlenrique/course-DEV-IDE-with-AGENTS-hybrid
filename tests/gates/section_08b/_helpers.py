"""Shared fixtures for Section 08B poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g3 import G3Card

RUN_ID = UUID("44444444-4444-4444-8444-444444444444")
STORYBOARD_ID = UUID("55555555-5555-4555-8555-555555555555")
SUBMITTED_AT = datetime(2026, 5, 6, 9, 0, tzinfo=UTC)


def fixture_storyboard_b_card() -> G3Card:
    return G3Card(
        decision_card_digest="b" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["08B"],
            override_trail=[],
        ),
        card_id=STORYBOARD_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        progress_percent=62.5,
        active_node_id="storyboard-b-live-url-review",
        pending_nodes=["voice-selection"],
        operator_prompt="Review Storyboard B and live URL before voice selection.",
        verb="approve",
    )


__all__ = ["RUN_ID", "STORYBOARD_ID", "SUBMITTED_AT", "fixture_storyboard_b_card"]
