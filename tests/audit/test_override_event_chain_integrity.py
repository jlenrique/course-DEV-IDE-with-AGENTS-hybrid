from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.audit.chain import verify_audit_chain
from app.audit.errors import AuditChainOrderError, AuditChainParentLinkError
from app.models.tripwire_ledger import TripwireLedgerEntry

BASE_TIME = datetime(2026, 5, 4, 12, 0, tzinfo=UTC)


def _entry(
    *,
    tripwire_id: str = "TW-7c-4",
    minutes: int = 0,
    fired_verdict: str = "not_fired",
    trace_id=None,
) -> TripwireLedgerEntry:
    return TripwireLedgerEntry.model_validate(
        {
            "tripwire_id": tripwire_id,
            "story_owner": "7c-0b",
            "fired_at": BASE_TIME + timedelta(minutes=minutes),
            "fired_verdict": fired_verdict,
            "measured_value": {"minutes": minutes},
            "escalation_action_taken": None,
            "decision_record_link": None,
            "severity": "high",
            "trace_id": trace_id,
        }
    )


def test_append_only_three_entry_ledger_succeeds():
    verify_audit_chain([_entry(minutes=1), _entry(minutes=2), _entry(minutes=3)])


def test_monotonic_timestamp_positive_for_same_tripwire():
    verify_audit_chain([_entry(minutes=10), _entry(minutes=11)])


def test_monotonic_timestamp_negative_for_same_tripwire():
    with pytest.raises(AuditChainOrderError):
        verify_audit_chain([_entry(minutes=10), _entry(minutes=9)])


def test_fired_verdict_with_trace_id_succeeds():
    verify_audit_chain([_entry(fired_verdict="fired", trace_id=uuid4())])


def test_fired_verdict_without_trace_id_raises_parent_link_error():
    with pytest.raises(AuditChainParentLinkError):
        verify_audit_chain([_entry(fired_verdict="fired", trace_id=None)])


def test_not_yet_evaluated_without_trace_id_succeeds():
    verify_audit_chain([_entry(fired_verdict="not_yet_evaluated", trace_id=None)])


def test_multi_tripwire_ids_have_independent_monotonic_chains():
    verify_audit_chain(
        [
            _entry(tripwire_id="TW-7c-4", minutes=20),
            _entry(tripwire_id="TW-7c-5", minutes=10),
        ]
    )


def test_marginal_fired_without_trace_id_requires_parent_link():
    with pytest.raises(AuditChainParentLinkError):
        verify_audit_chain([_entry(fired_verdict="marginal-fired", trace_id=None)])
