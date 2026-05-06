"""Shared fixtures for Section 04.5 estimator surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g1 import G1Card

RUN_ID = UUID("22222222-2222-4222-8222-222222222222")
ESTIMATOR_ID = UUID("33333333-3333-4333-8333-333333333333")


def fixture_estimator_card() -> G1Card:
    return G1Card(
        decision_card_digest="a" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["04.5"],
            override_trail=[],
        ),
        card_id=ESTIMATOR_ID,
        trial_id=RUN_ID,
        created_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        drafted_proposal={
            "parent_slide_count": 8,
            "target_total_runtime_minutes": 12.0,
            "estimated_total_slides": 14.4,
            "avg_slide_seconds": 50.0,
            "feasibility": "PASS",
        },
        evidence=[
            {
                "source": "slide_count_runtime_estimator",
                "profile_used": "visual-led",
            }
        ],
        trial_summary="Run-budget estimator values are feasible for the active profile.",
        opened_by="marcus",
        next_nodes=["04.55"],
        verb="approve",
    )


__all__ = ["ESTIMATOR_ID", "RUN_ID", "fixture_estimator_card"]

