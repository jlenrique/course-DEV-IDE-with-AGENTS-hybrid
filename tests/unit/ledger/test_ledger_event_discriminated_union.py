from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.ledger.events import (
    LedgerEventAdapter,
    OverrideLedgerEvent,
    SanctumMutationLedgerEvent,
    VerdictLedgerEvent,
)

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "ledger"


@pytest.mark.parametrize(
    ("filename", "expected_type"),
    [
        ("verdict_event_golden.json", VerdictLedgerEvent),
        ("override_event_golden.json", OverrideLedgerEvent),
        ("sanctum_mutation_event_golden.json", SanctumMutationLedgerEvent),
    ],
)
def test_ledger_event_discriminated_union_routes(filename: str, expected_type: type) -> None:
    payload = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    event = LedgerEventAdapter.validate_python(payload)

    assert isinstance(event, expected_type)


def test_ledger_event_discriminated_union_rejects_unknown_kind() -> None:
    payload = json.loads((FIXTURE_DIR / "verdict_event_golden.json").read_text(encoding="utf-8"))
    payload["kind"] = "unknown"

    with pytest.raises(ValidationError):
        LedgerEventAdapter.validate_python(payload)
