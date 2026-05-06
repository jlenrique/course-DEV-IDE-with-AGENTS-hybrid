from __future__ import annotations

import hashlib
import json

import pytest
from pydantic import ValidationError

from app.marcus.orchestrator.writers.slide_content import (
    GarySlideContent,
    SlideContentEntry,
    emit_gary_slide_content,
)

SCHEMA_HASH = "6fc3bc847ee6f5f368a97d422bc97874c76f95d00102ce537eaf13935b55c52e"


def _payload() -> GarySlideContent:
    return GarySlideContent(
        plan_unit_id="unit-07",
        target_section="section-04",
        slides=[
            SlideContentEntry(
                slide_index=1,
                title="Opening frame",
                body="Introduce the source problem.",
                content_kind="narrative",
            )
        ],
    )


def test_slide_content_round_trips_and_emits_lf_only_json(tmp_path):
    payload = GarySlideContent.model_validate(_payload().model_dump(mode="json"))
    output_path = emit_gary_slide_content(payload, tmp_path / "gary-slide-content.json")

    expected = json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
    raw = output_path.read_bytes()
    assert raw == expected.encode("utf-8")
    assert b"\r\n" not in raw


def test_slide_content_kind_rejects_unknown_value():
    data = _payload().model_dump(mode="json")
    data["slides"][0]["content_kind"] = "activity"

    with pytest.raises(ValidationError):
        GarySlideContent.model_validate(data)


def test_slide_content_rejects_blank_plan_unit_id():
    data = _payload().model_dump(mode="json")
    data["plan_unit_id"] = "   "

    with pytest.raises(ValidationError):
        GarySlideContent.model_validate(data)


def test_slide_content_schema_hash_is_stable():
    schema = json.dumps(GarySlideContent.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH
