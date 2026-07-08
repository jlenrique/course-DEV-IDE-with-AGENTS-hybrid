from __future__ import annotations

import json
from pathlib import Path

from app.marcus.course_source.asset_records import CanonicalAssetRecord

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = (
    REPO_ROOT
    / "app"
    / "marcus"
    / "course_source"
    / "schema"
    / "canonical_asset_record.v0_1.schema.json"
)
CHANGELOG = REPO_ROOT / "_bmad-output" / "implementation-artifacts" / "SCHEMA_CHANGELOG.md"


def test_canonical_asset_record_json_schema_pin_matches_live_model() -> None:
    expected = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    actual = CanonicalAssetRecord.model_json_schema()
    assert actual == expected


def test_required_fields_and_extra_forbid_surface_in_json_schema() -> None:
    schema = CanonicalAssetRecord.model_json_schema()
    required = set(schema["required"])
    assert {"asset_id", "asset_kind", "course_id", "status"} <= required
    assert schema["additionalProperties"] is False


def test_schema_changelog_names_canonical_asset_record() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "CanonicalAssetRecord v0.1" in text
    assert "Story S7 Phase-2 C" in text
