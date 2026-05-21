from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.gates import GateError, OperatorVerdict, clear_resume_registry, resume_from_verdict


def test_resume_from_verdict_raises_card_missing_without_registered_card() -> None:
    clear_resume_registry()
    verdict = OperatorVerdict(
        verdict_id=UUID("11111111-1111-4111-8111-111111111111"),
        trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        verb="approve",
        gate_id="irene-gate-decision-test",
        card_id=UUID("22222222-2222-4222-8222-222222222222"),
        operator_id="test-operator",
        timestamp=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        decision_card_digest="1" * 64,
    )
    with pytest.raises(GateError, match="card_missing"):
        resume_from_verdict(verdict)
