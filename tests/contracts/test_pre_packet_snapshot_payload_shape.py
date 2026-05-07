"""AC-T.6 — ``pre_packet_snapshot`` payload shape-pin (Winston R1 amendment on 30-4).

Pins ``PrePacketSnapshotPayload`` + ``SourceRef`` shapes. If any field
drifts, 30-4 cannot reconstruct Intake-era context from the log alone.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.log import PrePacketSnapshotPayload, SourceRef

EXPECTED_PRE_PACKET_FIELDS = {
    "sme_refs",
    "ingestion_digest",
    "pre_packet_artifact_path",
    "step_03_extraction_checksum",
}


EXPECTED_SOURCE_REF_FIELDS = {
    "source_id",
    "path",
    "content_digest",
}


# ---------------------------------------------------------------------------
# PrePacketSnapshotPayload shape
# ---------------------------------------------------------------------------


def test_pre_packet_snapshot_payload_fields_match_snapshot() -> None:
    actual = set(PrePacketSnapshotPayload.model_fields.keys())
    missing = EXPECTED_PRE_PACKET_FIELDS - actual
    extra = actual - EXPECTED_PRE_PACKET_FIELDS
    assert not missing, (
        f"PrePacketSnapshotPayload missing fields: {missing}. "
        f"30-4 fanout depends on log-only Intake-era reconstruction per Winston R1."
    )
    assert not extra, (
        f"PrePacketSnapshotPayload has NEW fields: {extra}. "
        f"Update SCHEMA_CHANGELOG + snapshot."
    )


def test_pre_packet_snapshot_payload_requires_all_four_fields() -> None:
    """Missing any required field raises ValidationError."""
    full = {
        "sme_refs": [SourceRef(source_id="s1", path=None, content_digest="d1")],
        "ingestion_digest": "deadbeef",
        "pre_packet_artifact_path": "artifacts/pre-packet.json",
        "step_03_extraction_checksum": "cafebabe",
    }
    # All four present → OK.
    PrePacketSnapshotPayload(**full)
    # Drop each field in turn; each drop is a ValidationError.
    for field in EXPECTED_PRE_PACKET_FIELDS:
        partial = {k: v for k, v in full.items() if k != field}
        with pytest.raises(ValidationError):
            PrePacketSnapshotPayload(**partial)


def test_pre_packet_snapshot_payload_is_frozen() -> None:
    """Mutating a constructed payload raises (ConfigDict(frozen=True))."""
    payload = PrePacketSnapshotPayload(
        sme_refs=[SourceRef(source_id="s1", path=None, content_digest="d1")],
        ingestion_digest="deadbeef",
        pre_packet_artifact_path="artifacts/pre-packet.json",
        step_03_extraction_checksum="cafebabe",
    )
    with pytest.raises((ValidationError, TypeError, AttributeError)):
        payload.ingestion_digest = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# SourceRef shape
# ---------------------------------------------------------------------------


def test_source_ref_fields_match_snapshot() -> None:
    actual = set(SourceRef.model_fields.keys())
    assert actual == EXPECTED_SOURCE_REF_FIELDS, (
        f"SourceRef drift. Missing: {EXPECTED_SOURCE_REF_FIELDS - actual}. "
        f"New: {actual - EXPECTED_SOURCE_REF_FIELDS}."
    )


def test_source_ref_path_optional_other_fields_required() -> None:
    """``path`` is Optional; ``source_id`` + ``content_digest`` are required."""
    # path=None is valid.
    SourceRef(source_id="s1", path=None, content_digest="d1")
    # Missing source_id → raise.
    with pytest.raises(ValidationError):
        SourceRef(path="some/path", content_digest="d1")  # type: ignore[call-arg]
    # Missing content_digest → raise.
    with pytest.raises(ValidationError):
        SourceRef(source_id="s1", path="some/path")  # type: ignore[call-arg]


def test_source_ref_rejects_empty_source_id_and_digest() -> None:
    with pytest.raises(ValidationError):
        SourceRef(source_id="", path=None, content_digest="d1")
    with pytest.raises(ValidationError):
        SourceRef(source_id="s1", path=None, content_digest="")
