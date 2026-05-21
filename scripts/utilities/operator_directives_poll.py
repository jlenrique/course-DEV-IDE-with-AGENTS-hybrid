"""Operator directives poll timing and submission validation helpers.

This module codifies Prompt 2A timing policy:
- hard 3-minute hold before accepting responses
- hard close at 15 minutes from poll start
- placeholder/fallback poll answers are invalid
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

REPLY_HOLD_SECONDS = 3 * 60
POLL_CLOSE_SECONDS = 15 * 60

NO_DIRECTIVES_ACK = "No operator directives — process all source content at default authority levels."
PROVIDING_DIRECTIVES_ACK = "I am providing directives and do not give this acknowledgment."

# Fallback text returned by non-interactive askQuestions tool paths.
_PLACEHOLDER_TEXT = (
    "The user is not available to respond and will review your work later. "
    "Work autonomously and make good decisions."
)


@dataclass(frozen=True)
class PollWindow:
    poll_started_utc: datetime
    reply_eligible_utc: datetime
    poll_close_utc: datetime


@dataclass(frozen=True)
class SubmissionDecision:
    status: str
    poll_status: str
    reason: str


def parse_iso_utc(ts: str) -> datetime:
    """Parse an ISO timestamp and normalize to UTC."""
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def build_poll_window(poll_started_utc: datetime) -> PollWindow:
    """Build a poll window using hard timing policy constants."""
    start = poll_started_utc.astimezone(UTC)
    return PollWindow(
        poll_started_utc=start,
        reply_eligible_utc=start + timedelta(seconds=REPLY_HOLD_SECONDS),
        poll_close_utc=start + timedelta(seconds=POLL_CLOSE_SECONDS),
    )


def is_placeholder_response(value: Any) -> bool:
    """Return True when value is a known non-interactive poll placeholder."""
    if not isinstance(value, str):
        return False
    return _PLACEHOLDER_TEXT in value.strip()


def _is_none_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "none"}
    return False


def evaluate_submission(
    *,
    poll_started_utc: datetime,
    now_utc: datetime,
    focus_directives: str | None,
    exclusion_directives: str | None,
    special_treatment_directives: str | None,
    acknowledgment: str,
) -> SubmissionDecision:
    """Evaluate whether a Prompt 2A submission is valid and in-window."""
    window = build_poll_window(poll_started_utc)
    now = now_utc.astimezone(UTC)

    if now < window.reply_eligible_utc:
        return SubmissionDecision(
            status="rejected",
            poll_status="open",
            reason="early-submission-before-3-minute-hold",
        )

    if now >= window.poll_close_utc:
        return SubmissionDecision(
            status="rejected",
            poll_status="closed-timeout",
            reason="poll-closed-timeout",
        )

    fields = [focus_directives, exclusion_directives, special_treatment_directives]
    if any(is_placeholder_response(v) for v in fields):
        return SubmissionDecision(
            status="rejected",
            poll_status="open",
            reason="placeholder-non-submission",
        )

    if acknowledgment not in {NO_DIRECTIVES_ACK, PROVIDING_DIRECTIVES_ACK}:
        return SubmissionDecision(
            status="rejected",
            poll_status="open",
            reason="invalid-acknowledgment",
        )

    if acknowledgment == NO_DIRECTIVES_ACK:
        if any(not _is_none_value(v) for v in fields):
            return SubmissionDecision(
                status="rejected",
                poll_status="open",
                reason="acknowledged-no-directives-but-directives-provided",
            )
        return SubmissionDecision(
            status="accepted",
            poll_status="submitted",
            reason="no-directives-acknowledged",
        )

    # PROVIDING_DIRECTIVES_ACK path
    if all(_is_none_value(v) for v in fields):
        return SubmissionDecision(
            status="rejected",
            poll_status="open",
            reason="directives-acknowledged-but-no-directives-provided",
        )

    return SubmissionDecision(
        status="accepted",
        poll_status="submitted",
        reason="directives-submitted",
    )
