from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import get_args
from uuid import uuid1, uuid4

import pytest
from pydantic import ValidationError

from app.manifest.compiler import production_gate_ids
from app.manifest.loader import load
from app.models.trial3_transcript import GateId, Trial3Transcript, TrialEvent

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "app/models/trial3_transcript.v1.schema.json"
MANIFEST_PATH = REPO_ROOT / "state/config/pipeline-manifest.yaml"
SCHEMA_VERSION_TO_SHA256 = {
    # Updated 2026-06-18 (Arc 2): GateId widened with the woken G2B + G4A gates
    # (additive enum members). Schema regenerated; hash re-pinned in lockstep.
    1: "40de12a6a257e8b387d4b665a5b579067593ef59c24f43f99bf8e1485203950b",
}


def _canonical_schema_bytes() -> bytes:
    return (
        json.dumps(
            Trial3Transcript.model_json_schema(),
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def _event(**overrides):
    payload = {
        "event_id": uuid4(),
        "gate_id": "G1",
        "event_type": "approve",
        "event_at": datetime(2026, 5, 6, 16, 0, tzinfo=UTC),
        "operator_id": " operator-1 ",
        "payload_digest": "a" * 64,
    }
    payload.update(overrides)
    return payload


def _transcript(**overrides):
    payload = {
        "trial_id": uuid4(),
        "started_at": datetime(2026, 5, 6, 15, 0, tzinfo=UTC),
        "completed_at": datetime(2026, 5, 6, 17, 0, tzinfo=UTC),
        "events": [_event()],
    }
    payload.update(overrides)
    return payload


def test_trial3_schema_file_matches_model_and_hash_pin() -> None:
    schema_bytes = _canonical_schema_bytes()
    assert SCHEMA_PATH.read_bytes() == schema_bytes
    digest = hashlib.sha256(schema_bytes).hexdigest()
    version = Trial3Transcript.model_fields["schema_version"].default
    assert digest == SCHEMA_VERSION_TO_SHA256[version]


def test_gate_id_literal_matches_manifest_production_gates() -> None:
    manifest = load(MANIFEST_PATH)
    assert set(get_args(GateId)) == production_gate_ids(manifest)


def test_trial3_transcript_accepts_valid_shape_and_strips_operator_id() -> None:
    transcript = Trial3Transcript.model_validate(_transcript())

    assert transcript.schema_version == 1
    assert transcript.events[0].operator_id == "operator-1"


@pytest.mark.parametrize(
    "event_patch",
    [
        {"gate_id": "G0"},
        {"event_type": "waive"},
        {"payload_digest": "A" * 64},
        {"operator_id": "   "},
    ],
)
def test_trial_event_red_rejects_closed_enums_digest_and_blank_operator(
    event_patch,
) -> None:
    with pytest.raises(ValidationError):
        TrialEvent.model_validate(_event(**event_patch))


def test_trial3_transcript_rejects_naive_datetimes() -> None:
    with pytest.raises(ValidationError):
        Trial3Transcript.model_validate(
            _transcript(started_at=datetime(2026, 5, 6, 15, 0))
        )


def test_trial3_transcript_rejects_non_uuid4_identities() -> None:
    with pytest.raises(ValidationError):
        Trial3Transcript.model_validate(_transcript(trial_id=uuid1()))

    with pytest.raises(ValidationError):
        TrialEvent.model_validate(_event(event_id=uuid1()))


def test_trial3_transcript_requires_at_least_one_event() -> None:
    with pytest.raises(ValidationError):
        Trial3Transcript.model_validate(_transcript(events=[]))
