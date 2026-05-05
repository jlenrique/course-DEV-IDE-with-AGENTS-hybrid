from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid1, uuid4

import pytest
from pydantic import TypeAdapter, ValidationError

from app.models.tripwire_ledger import (
    TripwireId,
    TripwireLedgerEntry,
    TripwireSeverity,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
FROZEN_PATHS_DIR = REPO_ROOT / "tests" / "fixtures" / "frozen_paths"


def _valid_entry_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "tripwire_id": "TW-7c-1",
        "story_owner": "7c-0a",
        "fired_at": datetime(2026, 5, 4, 20, 0, tzinfo=UTC),
        "fired_verdict": "not_yet_evaluated",
        "measured_value": {"status": "seeded"},
        "escalation_action_taken": None,
        "decision_record_link": (
            "_bmad-output/implementation-artifacts/"
            "migration-7c-0a-decision-foundation.md"
        ),
        "severity": "critical",
        "trace_id": uuid4(),
    }
    payload.update(overrides)
    return payload


def test_validate_assignment_true_rejects_invalid_mutation() -> None:
    entry = TripwireLedgerEntry.model_validate(_valid_entry_payload())

    with pytest.raises(ValidationError, match="String should have at least 1 character"):
        entry.story_owner = ""


def test_extra_forbid_rejects_unknown_fields() -> None:
    payload = _valid_entry_payload(unexpected_field="red")

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TripwireLedgerEntry.model_validate(payload)


def test_tripwire_id_closed_enum_rejects_unknown_id() -> None:
    with pytest.raises(ValidationError):
        TripwireLedgerEntry.model_validate(_valid_entry_payload(tripwire_id="TW-99"))


def test_tripwire_id_schema_and_type_adapter_are_closed() -> None:
    schema = TripwireLedgerEntry.model_json_schema()
    tripwire_enum = schema["$defs"]["TripwireId"]["enum"]

    assert tripwire_enum == [
        "TW-7c-1",
        "TW-7c-2",
        "TW-7c-3",
        "TW-7c-4",
        "TW-7c-5",
        "TW-7c-6",
    ]
    assert TypeAdapter(TripwireId).validate_python("TW-7c-1") is TripwireId.TW_7C_1
    with pytest.raises(ValidationError):
        TypeAdapter(TripwireId).validate_python("TW-99")


def test_fired_at_timezone_aware_required() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        TripwireLedgerEntry.model_validate(
            _valid_entry_payload(fired_at=datetime(2026, 5, 4, 20, 0))
        )


def test_severity_closed_enum_rejects_unknown_tier() -> None:
    with pytest.raises(ValidationError):
        TripwireLedgerEntry.model_validate(_valid_entry_payload(severity="low"))


def test_trace_id_must_be_uuid4_when_present() -> None:
    with pytest.raises(ValidationError, match="UUID4"):
        TripwireLedgerEntry.model_validate(_valid_entry_payload(trace_id=uuid1()))


@pytest.mark.parametrize(
    "tripwire_id",
    [
        TripwireId.TW_7C_1,
        TripwireId.TW_7C_2,
        TripwireId.TW_7C_3,
        TripwireId.TW_7C_4,
        TripwireId.TW_7C_5,
        TripwireId.TW_7C_6,
    ],
)
@pytest.mark.parametrize(
    "severity",
    [
        TripwireSeverity.CRITICAL,
        TripwireSeverity.HIGH,
    ],
)
def test_audit_round_trip_all_six_tw_ids_by_two_severity_tiers(
    tripwire_id: TripwireId,
    severity: TripwireSeverity,
) -> None:
    entry = TripwireLedgerEntry.model_validate(
        _valid_entry_payload(
            tripwire_id=tripwire_id.value,
            severity=severity.value,
            fired_verdict="fired",
            measured_value={"round_trip": f"{tripwire_id.value}:{severity.value}"},
        )
    )

    dumped = entry.model_dump(mode="json")
    round_tripped = TripwireLedgerEntry.model_validate(dumped)

    assert round_tripped == entry
    assert dumped["tripwire_id"] == tripwire_id.value
    assert dumped["severity"] == severity.value


def test_audit_chain_field_set_complete() -> None:
    model_fields = set(TripwireLedgerEntry.model_fields)

    assert "tripwire_id" in model_fields
    assert "story_owner" in model_fields
    assert "fired_at" in model_fields
    assert "fired_verdict" in model_fields
    assert "measured_value" in model_fields
    assert "escalation_action_taken" in model_fields
    assert "decision_record_link" in model_fields
    assert "severity" in model_fields
    assert "trace_id" in model_fields
    assert TripwireLedgerEntry.model_config["validate_assignment"] is True
    assert TripwireLedgerEntry.model_config["extra"] == "forbid"
    assert TripwireLedgerEntry.model_config["frozen"] is False
    assert TripwireLedgerEntry.model_json_schema()["additionalProperties"] is False


def test_frozen_paths_fixture_directory_exists() -> None:
    assert FROZEN_PATHS_DIR.exists(), FROZEN_PATHS_DIR.as_posix()
