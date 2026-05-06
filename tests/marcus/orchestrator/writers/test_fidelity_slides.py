from __future__ import annotations

import hashlib
import json

import pytest
from pydantic import ValidationError

from app.marcus.orchestrator.writers.fidelity_slides import (
    GaryFidelitySlides,
    VeraFidelityCriterion,
    emit_gary_fidelity_slides,
)

SCHEMA_HASH = "8e76ccb73f89c783e6900874f9e206ba7cadffbd3f84424da5a2353c8f895db8"


def _payload() -> GaryFidelitySlides:
    return GaryFidelitySlides(
        plan_unit_id="unit-07",
        target_section="section-06",
        vera_criteria=[
            VeraFidelityCriterion(
                criterion_id="vera-001",
                severity="MUST",
                description="Preserve every source-defined safety caveat.",
                vera_source_ref=None,
            )
        ],
    )


def test_fidelity_slides_round_trips_and_emits_lf_only_json(tmp_path):
    payload = GaryFidelitySlides.model_validate(_payload().model_dump(mode="json"))
    output_path = emit_gary_fidelity_slides(
        payload,
        tmp_path / "gary-fidelity-slides.json",
    )

    expected = json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
    raw = output_path.read_bytes()
    assert raw == expected.encode("utf-8")
    assert b"\r\n" not in raw


def test_fidelity_severity_rejects_unknown_value():
    data = _payload().model_dump(mode="json")
    data["vera_criteria"][0]["severity"] = "BLOCKER"

    with pytest.raises(ValidationError):
        GaryFidelitySlides.model_validate(data)


def test_fidelity_slides_rejects_blank_plan_unit_id():
    data = _payload().model_dump(mode="json")
    data["plan_unit_id"] = "   "

    with pytest.raises(ValidationError):
        GaryFidelitySlides.model_validate(data)


def test_fidelity_slides_permits_null_vera_source_ref():
    payload = _payload()

    assert payload.vera_criteria[0].vera_source_ref is None


def test_fidelity_slides_schema_hash_is_stable():
    schema = json.dumps(GaryFidelitySlides.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH
