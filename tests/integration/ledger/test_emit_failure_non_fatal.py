from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import psycopg
import pytest

from app.ledger.emitter import (
    emit_ledger_event,
    get_ledger_emission_failures_total,
    reset_ledger_counters,
)
from app.ledger.events import build_override_ledger_event


@pytest.fixture(autouse=True)
def _reset_counters() -> None:
    reset_ledger_counters()


def test_emit_failure_non_fatal(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = build_override_ledger_event(
        trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        node_id="04",
        operator_id="juanl",
        previous_model="gpt-5",
        new_model="gpt-5-mini",
        confirm_token="confirm-001",
        phase="submitted",
        created_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
    )

    def _boom(*args, **kwargs):
        del args, kwargs
        raise psycopg.OperationalError("connection refused")

    monkeypatch.setattr("app.ledger.emitter.psycopg.connect", _boom)

    with caplog.at_level("WARNING"):
        result = emit_ledger_event(event)

    assert result.status == "failed"
    assert result.event_id is None
    assert get_ledger_emission_failures_total() == 1
    assert "ledger emission failed" in caplog.text


def test_emit_missing_database_url_is_non_fatal(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = build_override_ledger_event(
        trial_id=UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"),
        node_id="05",
        operator_id="juanl",
        previous_model="gpt-5",
        new_model="gpt-5-mini",
        confirm_token="confirm-002",
        phase="submitted",
        created_at=datetime(2026, 4, 26, 12, 1, tzinfo=UTC),
    )

    monkeypatch.delenv("DATABASE_URL", raising=False)

    with caplog.at_level("WARNING"):
        result = emit_ledger_event(event)

    assert result.status == "failed"
    assert result.reason == "DATABASE_URL env var not set"
    assert get_ledger_emission_failures_total() == 1
    assert "ledger emission failed" in caplog.text
