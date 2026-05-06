from __future__ import annotations

import hashlib

from app.gates.section_07c.storyboard_html_emitter import emit_storyboard_html
from app.models.operator_verdict_section_07c import StoryboardBuildPayload
from tests.gates.section_07c._helpers import (
    HTML_DIGEST,
    PLAN_UNIT_ID,
    fixture_build_payload,
    fixture_storyboard_targets,
)


def test_storyboard_html_emitter_is_byte_deterministic_and_lf_only(tmp_path):
    payload = StoryboardBuildPayload.model_validate(fixture_build_payload())
    slides = fixture_storyboard_targets()["slides"]
    first = emit_storyboard_html(
        payload,
        tmp_path / "first.html",
        plan_unit_id=PLAN_UNIT_ID,
        slide_content=slides,  # type: ignore[arg-type]
    )
    second = emit_storyboard_html(
        payload,
        tmp_path / "second.html",
        plan_unit_id=PLAN_UNIT_ID,
        slide_content=slides,  # type: ignore[arg-type]
    )

    first_bytes = first.read_bytes()
    second_bytes = second.read_bytes()
    assert first_bytes == second_bytes
    assert hashlib.sha256(first_bytes).hexdigest() == hashlib.sha256(second_bytes).hexdigest()
    assert not first_bytes.startswith(bytes([0xEF, 0xBB, 0xBF]))
    assert b"\r\n" not in first_bytes
    assert b"<!doctype html>" in first_bytes
    assert payload.storyboard_html_digest == HTML_DIGEST
