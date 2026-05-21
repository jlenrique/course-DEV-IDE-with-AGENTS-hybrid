"""Shared fixtures for Section 11B poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g4 import G4Card

RUN_ID = UUID("88888888-8888-4888-8888-888888888888")
INPUT_PACKAGE_ID = UUID("99999999-9999-4999-8999-999999999999")
SUBMITTED_AT = datetime(2026, 5, 6, 15, 0, tzinfo=UTC)


def fixture_input_package_card() -> G4Card:
    return G4Card(
        decision_card_digest="d" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["11B"],
            override_trail=[],
        ),
        card_id=INPUT_PACKAGE_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        final_status="completed",
        artifact_paths=[
            "runs/trial-3/input-package/pre-dispatch-package-gary.md",
            "runs/trial-3/input-package/voice-package.json",
        ],
        outcome_summary="Input package is ready for final assembly preview.",
        verb="approve",
    )


__all__ = [
    "INPUT_PACKAGE_ID",
    "RUN_ID",
    "SUBMITTED_AT",
    "fixture_input_package_card",
]
