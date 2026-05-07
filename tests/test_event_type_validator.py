"""AC-T.6 — event_type open-string validator tests (Quinn Gagné seam).

Validates ``validate_event_type``:
    - Accepts all nine Gagné labels silently (no warning).
    - Accepts reserved log event_types silently.
    - WARNS (does not reject) on unknown event_types.
    - Rejects invalid regex (spaces / caps).
    - Rejects empty string.
"""

from __future__ import annotations

import logging

import pytest

from app.marcus.lesson_plan import event_type_registry
from app.marcus.lesson_plan.event_type_registry import (
    KNOWN_PLAN_UNIT_EVENT_TYPES,
    RESERVED_LOG_EVENT_TYPES,
    validate_event_type,
)


@pytest.fixture(autouse=True)
def _reset_warn_state() -> None:
    """SF-4: warn-once dedup is module-global — reset per test for isolation."""
    event_type_registry._reset_warning_state()


@pytest.mark.parametrize("label", sorted(KNOWN_PLAN_UNIT_EVENT_TYPES))
def test_event_type_accepts_all_gagne_nine_silently(label: str, caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="marcus.lesson_plan.event_type_registry"):
        assert validate_event_type(label) == label
    assert not any(
        "not in known registry" in r.message for r in caplog.records
    ), f"{label!r} is a known label and must not warn"


@pytest.mark.parametrize("label", sorted(RESERVED_LOG_EVENT_TYPES))
def test_event_type_accepts_reserved_log_events_silently(label: str, caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="marcus.lesson_plan.event_type_registry"):
        assert validate_event_type(label) == label
    assert not any(
        "not in known registry" in r.message for r in caplog.records
    )


def test_event_type_warns_on_unknown_registered(caplog) -> None:
    with caplog.at_level(logging.WARNING, logger="marcus.lesson_plan.event_type_registry"):
        assert validate_event_type("custom-event-42") == "custom-event-42"
    messages = [r.message for r in caplog.records]
    assert any("not in known registry" in m for m in messages), (
        f"Expected warning on unknown event_type; got records: {messages}"
    )
    assert any("Gagné-seam extensibility" in m for m in messages)


@pytest.mark.parametrize(
    "bad",
    [
        "Gagne Event 1",  # spaces + caps
        "GAGNE-EVENT-1",  # caps
        "gagne event 1",  # spaces
        "has/slash",
        "has#hash",
    ],
)
def test_event_type_rejects_invalid_regex(bad: str) -> None:
    with pytest.raises(ValueError) as exc:
        validate_event_type(bad)
    assert "fails open-id regex" in str(exc.value)


def test_event_type_rejects_empty_string() -> None:
    with pytest.raises(ValueError):
        validate_event_type("")


def test_pre_packet_snapshot_is_reserved_not_known_plan_unit() -> None:
    """R2 W-1: pre_packet_snapshot is RESERVED for 31-2 emission; not a Gagné label."""
    assert "pre_packet_snapshot" in RESERVED_LOG_EVENT_TYPES
    assert "pre_packet_snapshot" not in KNOWN_PLAN_UNIT_EVENT_TYPES


def test_unknown_event_type_warns_only_once_across_repeated_calls(caplog) -> None:
    """SF-4: a repeated unknown event_type warns exactly once per process lifetime."""
    with caplog.at_level(logging.WARNING, logger="marcus.lesson_plan.event_type_registry"):
        for _ in range(5):
            assert validate_event_type("noisy-unknown-event") == "noisy-unknown-event"
    relevant = [
        r
        for r in caplog.records
        if "noisy-unknown-event" in r.message and "not in known registry" in r.message
    ]
    assert len(relevant) == 1, (
        f"Expected exactly 1 dedup warning across 5 calls, got {len(relevant)}: "
        f"{[r.message for r in relevant]}"
    )


def test_warn_state_reset_helper_reenables_warning() -> None:
    """SF-4: ``_reset_warning_state`` clears the memo so the next call re-warns."""
    import logging as _logging

    validate_event_type("another-unknown-event")  # first call — warns
    event_type_registry._reset_warning_state()
    logger = _logging.getLogger("marcus.lesson_plan.event_type_registry")
    records: list[_logging.LogRecord] = []

    class _Capture(_logging.Handler):
        def emit(self, record: _logging.LogRecord) -> None:
            records.append(record)

    handler = _Capture(level=_logging.WARNING)
    logger.addHandler(handler)
    try:
        validate_event_type("another-unknown-event")
    finally:
        logger.removeHandler(handler)
    assert any(
        "another-unknown-event" in r.getMessage() and "not in known registry" in r.getMessage()
        for r in records
    ), "After _reset_warning_state, warning should fire again"
