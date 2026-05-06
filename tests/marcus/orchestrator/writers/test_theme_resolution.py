from __future__ import annotations

import hashlib
import json

import pytest
from pydantic import ValidationError

from app.marcus.orchestrator.writers.theme_resolution import (
    GaryThemeResolution,
    ResolvedTheme,
    emit_gary_theme_resolution,
)

SCHEMA_HASH = "5b3b24b1c84197de2f819adb636b968153cad568a803691f33645cd41e0c9c2e"


def _payload() -> GaryThemeResolution:
    return GaryThemeResolution(
        plan_unit_id="unit-07",
        target_section="section-11",
        experience_profile_id="visual-led",
        creative_directive_id=None,
        resolved_theme=ResolvedTheme(
            theme_name="Bright Instructional",
            palette="brand-default",
            template_intent="diagram-forward",
        ),
    )


def test_theme_resolution_round_trips_and_emits_lf_only_json(tmp_path):
    payload = GaryThemeResolution.model_validate(_payload().model_dump(mode="json"))
    output_path = emit_gary_theme_resolution(
        payload,
        tmp_path / "gary-theme-resolution.json",
    )

    expected = json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
    raw = output_path.read_bytes()
    assert raw == expected.encode("utf-8")
    assert b"\r\n" not in raw


def test_theme_palette_rejects_unknown_value():
    data = _payload().model_dump(mode="json")
    data["resolved_theme"]["palette"] = "sepia"

    with pytest.raises(ValidationError):
        GaryThemeResolution.model_validate(data)


def test_theme_resolution_rejects_blank_plan_unit_id():
    data = _payload().model_dump(mode="json")
    data["plan_unit_id"] = "   "

    with pytest.raises(ValidationError):
        GaryThemeResolution.model_validate(data)


def test_theme_resolution_permits_null_creative_directive_id():
    payload = _payload()

    assert payload.creative_directive_id is None


def test_theme_resolution_schema_hash_is_stable():
    schema = json.dumps(GaryThemeResolution.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH
