from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ASSET_RECORDS = REPO_ROOT / "app" / "marcus" / "course_source" / "asset_records.py"


def test_asset_records_do_not_import_projector_family() -> None:
    text = ASSET_RECORDS.read_text(encoding="utf-8")
    forbidden = [
        "workbook_enrichment",
        "workbook_producer",
        "projector",
        "producer",
    ]
    assert not any(token in text for token in forbidden)
