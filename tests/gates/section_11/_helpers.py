"""Shared fixtures for Section 11 poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g4 import G4Card

RUN_ID = UUID("66666666-6666-4666-8666-666666666666")
VOICE_SELECTION_ID = UUID("77777777-7777-4777-8777-777777777777")
SUBMITTED_AT = datetime(2026, 5, 6, 9, 15, tzinfo=UTC)


def fixture_voice_selection_card() -> G4Card:
    return G4Card(
        decision_card_digest="c" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["11"],
            override_trail=[],
        ),
        card_id=VOICE_SELECTION_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        final_status="completed",
        artifact_paths=[
            "runs/c1m1-tejal-20260419b/voice-candidates/en-US-narrator.json",
            "runs/c1m1-tejal-20260419b/voice-candidates/en-US-coach.json",
        ],
        outcome_summary="Voice candidates are ready for ElevenLabs selection.",
        verb="approve",
    )


__all__ = [
    "RUN_ID",
    "SUBMITTED_AT",
    "VOICE_SELECTION_ID",
    "fixture_voice_selection_card",
]
