from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.ledger.events import OverrideLedgerEvent, SanctumMutationLedgerEvent, VerdictLedgerEvent

FIXTURES = {
    "verdict": (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "ledger"
        / "verdict_event_golden.json",
        VerdictLedgerEvent,
        Path(__file__).resolve().parents[3]
        / "app"
        / "ledger"
        / "schema"
        / "verdict_event.v1.schema.json",
    ),
    "override": (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "ledger"
        / "override_event_golden.json",
        OverrideLedgerEvent,
        Path(__file__).resolve().parents[3]
        / "app"
        / "ledger"
        / "schema"
        / "override_event.v1.schema.json",
    ),
    "sanctum_mutation": (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "ledger"
        / "sanctum_mutation_event_golden.json",
        SanctumMutationLedgerEvent,
        Path(__file__).resolve().parents[3]
        / "app"
        / "ledger"
        / "schema"
        / "sanctum_mutation_event.v1.schema.json",
    ),
}


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


@pytest.mark.parametrize("kind", ["verdict", "override", "sanctum_mutation"])
def test_ledger_event_strict_round_trip_and_schema(kind: str) -> None:
    fixture_path, model_class, schema_path = FIXTURES[kind]
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    model = model_class.model_validate(payload)

    assert model.model_dump(mode="json") == payload
    assert _hash(json.loads(schema_path.read_text(encoding="utf-8"))) == _hash(
        model_class.model_json_schema()
    )


@pytest.mark.parametrize(
    ("kind", "field", "value"),
    [
        ("verdict", "gate_id", ""),
        ("override", "node_id", ""),
        ("sanctum_mutation", "created_at", "2026-04-26T12:02:00"),
    ],
)
def test_ledger_event_strict_rejects_invalid_values(kind: str, field: str, value: object) -> None:
    fixture_path, model_class, _ = FIXTURES[kind]
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload[field] = value

    with pytest.raises(ValidationError):
        model_class.model_validate(payload)
