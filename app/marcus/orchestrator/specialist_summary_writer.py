"""Orchestrator-facing specialist summary writer API.

The implementation lives under ``app.models.state`` so specialist graphs can
call the emit hook without importing ``app.marcus`` and breaking lane contracts.
"""

from __future__ import annotations

from app.models.state.specialist_summary_artifacts import (
    CANONICAL_SPECIALIST_IDS,
    DEFERRED_SPECIALIST_IDS,
    AdjacentSummary,
    SummaryLengthError,
    _validate_length,
    build_summary_text,
    canonical_specialist_id,
    emit_summary,
    emit_summary_for_state,
    load_most_recent_summary,
)

__all__ = [
    "AdjacentSummary",
    "CANONICAL_SPECIALIST_IDS",
    "DEFERRED_SPECIALIST_IDS",
    "SummaryLengthError",
    "_validate_length",
    "build_summary_text",
    "canonical_specialist_id",
    "emit_summary",
    "emit_summary_for_state",
    "load_most_recent_summary",
]
