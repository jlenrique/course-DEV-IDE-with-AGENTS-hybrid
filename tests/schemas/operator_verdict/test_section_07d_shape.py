from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_07d.poll_surface import display_motion_plan_status, submit_verdict
from app.models.operator_verdict_section_07d import (
    SECTION_07D_SURFACE_ID,
    MotionPlanEditPayload,
    Section07DOperatorVerdict,
)
from tests.gates.section_07d._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_motion_plan_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_07d.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section07DOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_07d_operator_verdict_schema_hash_stable_across_transports() -> None:
    motion_plan = fixture_motion_plan_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_motion_plan_status(motion_plan)
        verdict = submit_verdict(
            displayed["motion_plan_id"],
            {
                "run_id": RUN_ID,
                "verb": "approve",
                "operator_id": "operator_1",
                "submitted_at": SUBMITTED_AT,
                "decision_card_digest": displayed["decision_card_digest"],
            },
            transport,  # type: ignore[arg-type]
        )
        schema_hashes.add(_schema_hash())
        verdict_payloads.append(verdict.model_dump(mode="json"))

    assert len(schema_hashes) == 1
    assert verdict_payloads[0] == verdict_payloads[1] == verdict_payloads[2]
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section07DOperatorVerdict,
        surface_id=SECTION_07D_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_07d_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section07DOperatorVerdict.model_json_schema()

    assert SECTION_07D_SURFACE_ID == "section_07d_g2_5_motion_plan_polling"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_07d_g2_5_motion_plan_polling"
    )


def test_section_07d_edit_payload_schema_is_nested_motion_plan_edit_payload() -> None:
    schema = Section07DOperatorVerdict.model_json_schema()

    assert "MotionPlanEditPayload" in schema["$defs"]
    assert schema["$defs"]["MotionPlanEditPayload"] == MotionPlanEditPayload.model_json_schema()
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/MotionPlanEditPayload"
    )


def test_section_07d_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section07DOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
