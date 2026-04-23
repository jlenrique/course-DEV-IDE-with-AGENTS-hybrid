"""Shape-pin tests for `SanctumFingerprint` (Story 1.2 AC-1.2-A/B/C)."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.state import SanctumFingerprint
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(SanctumFingerprint, load_golden("sanctum_fingerprint"))


def test_forbids_extra_fields() -> None:
    assert_forbids_extra_field(
        SanctumFingerprint,
        {"content_sha256": "a" * 64},
    )


def test_rejects_naive_datetime() -> None:
    with pytest.raises(ValidationError):
        SanctumFingerprint(
            content_sha256="a" * 64,
            captured_at=datetime(2026, 4, 23, 12, 0, 0),  # naive
        )


def test_rejects_non_uuid4_snapshot_id() -> None:
    import uuid

    with pytest.raises(ValidationError):
        SanctumFingerprint(
            content_sha256="a" * 64,
            snapshot_id=uuid.uuid1(),  # uuid1, not uuid4
        )


def test_rejects_non_hex_content_sha256() -> None:
    with pytest.raises(ValidationError):
        SanctumFingerprint(content_sha256="g" * 64)  # 'g' not hex


def test_rejects_short_content_sha256() -> None:
    with pytest.raises(ValidationError):
        SanctumFingerprint(content_sha256="a" * 32)  # too short


def test_is_frozen() -> None:
    sf = SanctumFingerprint(content_sha256="a" * 64)
    with pytest.raises(ValidationError):
        sf.content_sha256 = "b" * 64  # frozen=True forbids


def test_default_factory_emits_uuid4() -> None:
    sf = SanctumFingerprint(content_sha256="c" * 64)
    assert sf.snapshot_id.version == 4


def test_default_factory_captured_at_is_tz_aware() -> None:
    sf = SanctumFingerprint(content_sha256="d" * 64)
    assert sf.captured_at.tzinfo is not None


def test_explicit_uuid4_accepted() -> None:
    fixed = uuid4()
    sf = SanctumFingerprint(content_sha256="e" * 64, snapshot_id=fixed)
    assert sf.snapshot_id == fixed
