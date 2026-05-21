from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_07f.poll_surface import display_motion_clip, submit_verdict
from app.models.operator_verdict_section_07f import (
    SECTION_07F_SURFACE_ID,
    MotionClipEditPayload,
    Section07FOperatorVerdict,
)
from tests.gates.section_07f._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_motion_clip_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_07f.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section07FOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_07f_operator_verdict_schema_hash_stable_across_transports() -> None:
    motion_clip = fixture_motion_clip_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_motion_clip(motion_clip)
        verdict = submit_verdict(
            displayed["motion_clip_id"],
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
        verdict_class=Section07FOperatorVerdict,
        surface_id=SECTION_07F_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_07f_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section07FOperatorVerdict.model_json_schema()

    assert SECTION_07F_SURFACE_ID == "section_07f_g2f_motion_gate"
    assert schema["properties"]["surface_id"]["const"] == "section_07f_g2f_motion_gate"


def test_section_07f_edit_payload_schema_is_nested_motion_clip_edit_payload() -> None:
    schema = Section07FOperatorVerdict.model_json_schema()

    assert "MotionClipEditPayload" in schema["$defs"]
    assert schema["$defs"]["MotionClipEditPayload"] == MotionClipEditPayload.model_json_schema()
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/MotionClipEditPayload"
    )


def test_section_07f_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section07FOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
