from __future__ import annotations

from datetime import UTC, datetime, timedelta

from scripts.utilities.operator_directives_poll import (
    NO_DIRECTIVES_ACK,
    PROVIDING_DIRECTIVES_ACK,
    build_poll_window,
    evaluate_submission,
    is_placeholder_response,
)


def _dt() -> datetime:
    return datetime(2026, 4, 3, 18, 0, 0, tzinfo=UTC)


def test_build_poll_window_uses_hard_timing_policy() -> None:
    window = build_poll_window(_dt())
    assert window.reply_eligible_utc == _dt() + timedelta(minutes=3)
    assert window.poll_close_utc == _dt() + timedelta(minutes=15)


def test_rejects_submission_before_3_minute_hold() -> None:
    start = _dt()
    decision = evaluate_submission(
        poll_started_utc=start,
        now_utc=start + timedelta(minutes=2, seconds=59),
        focus_directives="focus section 3",
        exclusion_directives="NONE",
        special_treatment_directives="NONE",
        acknowledgment=PROVIDING_DIRECTIVES_ACK,
    )
    assert decision.status == "rejected"
    assert decision.reason == "early-submission-before-3-minute-hold"
    assert decision.poll_status == "open"


def test_closes_poll_at_or_after_15_minutes() -> None:
    start = _dt()
    decision = evaluate_submission(
        poll_started_utc=start,
        now_utc=start + timedelta(minutes=15),
        focus_directives="focus section 3",
        exclusion_directives="NONE",
        special_treatment_directives="NONE",
        acknowledgment=PROVIDING_DIRECTIVES_ACK,
    )
    assert decision.status == "rejected"
    assert decision.reason == "poll-closed-timeout"
    assert decision.poll_status == "closed-timeout"


def test_rejects_placeholder_non_submission_payload() -> None:
    start = _dt()
    placeholder = (
        "The user is not available to respond and will review your work later. "
        "Work autonomously and make good decisions."
    )
    decision = evaluate_submission(
        poll_started_utc=start,
        now_utc=start + timedelta(minutes=4),
        focus_directives=placeholder,
        exclusion_directives="NONE",
        special_treatment_directives="NONE",
        acknowledgment=PROVIDING_DIRECTIVES_ACK,
    )
    assert decision.status == "rejected"
    assert decision.reason == "placeholder-non-submission"
    assert decision.poll_status == "open"
    assert is_placeholder_response(placeholder)


def test_accepts_no_directives_ack_with_none_fields() -> None:
    start = _dt()
    decision = evaluate_submission(
        poll_started_utc=start,
        now_utc=start + timedelta(minutes=4),
        focus_directives="NONE",
        exclusion_directives="none",
        special_treatment_directives="",
        acknowledgment=NO_DIRECTIVES_ACK,
    )
    assert decision.status == "accepted"
    assert decision.reason == "no-directives-acknowledged"
    assert decision.poll_status == "submitted"


def test_accepts_directives_when_provided_ack_selected() -> None:
    start = _dt()
    decision = evaluate_submission(
        poll_started_utc=start,
        now_utc=start + timedelta(minutes=4),
        focus_directives="Focus section 3 and case study",
        exclusion_directives="NONE",
        special_treatment_directives="Treat page 8 infographic as literal-visual",
        acknowledgment=PROVIDING_DIRECTIVES_ACK,
    )
    assert decision.status == "accepted"
    assert decision.reason == "directives-submitted"
    assert decision.poll_status == "submitted"


def test_rejects_providing_ack_with_no_directives() -> None:
    start = _dt()
    decision = evaluate_submission(
        poll_started_utc=start,
        now_utc=start + timedelta(minutes=4),
        focus_directives="NONE",
        exclusion_directives="NONE",
        special_treatment_directives="NONE",
        acknowledgment=PROVIDING_DIRECTIVES_ACK,
    )
    assert decision.status == "rejected"
    assert decision.reason == "directives-acknowledged-but-no-directives-provided"
    assert decision.poll_status == "open"
