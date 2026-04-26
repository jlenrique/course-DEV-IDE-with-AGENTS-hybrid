from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.runtime.override_warning import ModelOverrideWarning

_RUNTIME_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "runtime"
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "app"
    / "runtime"
    / "schema"
    / "override_warning.v1.schema.json"
)


def test_override_warning_round_trip_against_golden_fixture() -> None:
    golden = json.loads(
        (_RUNTIME_FIXTURES / "override_warning_golden.json").read_text(encoding="utf-8")
    )
    model = ModelOverrideWarning.model_validate(golden)
    assert model.model_dump(mode="json") == golden


def test_override_warning_live_schema_matches_pin_by_hash() -> None:
    pinned = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    live = ModelOverrideWarning.model_json_schema()
    pinned_hash = hashlib.sha256(
        json.dumps(pinned, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    live_hash = hashlib.sha256(
        json.dumps(live, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert live_hash == pinned_hash
