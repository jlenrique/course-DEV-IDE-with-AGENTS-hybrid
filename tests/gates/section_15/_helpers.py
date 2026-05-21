"""Shared fixtures for Section 15 poll-surface tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from app.models.decision_cards._base import CacheState, DecisionCardMeta
from app.models.decision_cards.g5 import G5Card

RUN_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
HANDOFF_ID = UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
BUNDLE_RUN_ID = UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
SUBMITTED_AT = datetime(2026, 5, 6, 15, 30, tzinfo=UTC)


def fixture_final_handoff_card() -> G5Card:
    return G5Card(
        decision_card_digest="e" * 64,
        meta=DecisionCardMeta(
            cache_state=CacheState.HEALTHY,
            affected_nodes=["15"],
            override_trail=[],
        ),
        card_id=HANDOFF_ID,
        trial_id=RUN_ID,
        created_at=SUBMITTED_AT,
        bundle_run_id=BUNDLE_RUN_ID,
        handoff_artifact_paths=[
            Path("runs/trial-3/assembly-bundle/DESCRIPT-ASSEMBLY-GUIDE.md"),
            Path("runs/trial-3/slab-close-evidence.json"),
        ],
        handoff_summary="Final operator handoff is ready for slab close.",
        verb="approve",
    )


__all__ = [
    "BUNDLE_RUN_ID",
    "HANDOFF_ID",
    "RUN_ID",
    "SUBMITTED_AT",
    "fixture_final_handoff_card",
]
