from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.runtime.sanctum_warning import SanctumWarning

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "runtime"
    / "sanctum_warning_golden.json"
)
SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "runtime"
    / "schema"
    / "sanctum_warning.v1.schema.json"
)


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def test_sanctum_warning_round_trip_and_schema_pin() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    warning = SanctumWarning.model_validate(payload)

    assert warning.model_dump(mode="json") == payload
    assert _hash(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))) == _hash(
        SanctumWarning.model_json_schema()
    )


def test_sanctum_warning_rejects_naive_datetime() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["mutated_at"] = datetime(2026, 4, 26, 12, 3, 0)

    with pytest.raises(ValidationError, match="timezone-aware"):
        SanctumWarning.model_validate(payload)
