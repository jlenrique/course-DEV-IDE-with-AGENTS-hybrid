from __future__ import annotations

import json
import re

from app.marcus.course_source.asset_records import CanonicalAssetRecord

FORBIDDEN = re.compile(r"\b(intake|orchestrator)\b", re.IGNORECASE)


def test_asset_record_schema_and_dump_do_not_leak_split_voice_terms() -> None:
    schema_text = json.dumps(CanonicalAssetRecord.model_json_schema(), sort_keys=True)
    record = CanonicalAssetRecord(
        asset_id="asset-006",
        asset_kind="reading",
        course_id="course-001",
        status="missing",
    )
    dump_text = record.model_dump_json()

    assert FORBIDDEN.search(schema_text) is None
    assert FORBIDDEN.search(dump_text) is None
