from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_08b.poll_surface import display_storyboard_b, submit_verdict
from app.models.operator_verdict_section_08b import (
    SECTION_08B_SURFACE_ID,
    Section08BOperatorVerdict,
    StoryboardBEditPayload,
)
from tests.gates.section_08b._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_storyboard_b_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_08b.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section08BOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_08b_operator_verdict_schema_hash_stable_across_transports() -> None:
    storyboard = fixture_storyboard_b_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_storyboard_b(storyboard)
        verdict = submit_verdict(
            displayed["storyboard_id"],
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
        verdict_class=Section08BOperatorVerdict,
        surface_id=SECTION_08B_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_08b_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section08BOperatorVerdict.model_json_schema()

    assert SECTION_08B_SURFACE_ID == "section_08b_g3b_poll"
    assert schema["properties"]["surface_id"]["const"] == "section_08b_g3b_poll"


def test_section_08b_edit_payload_schema_is_nested_storyboard_b_edit_payload() -> None:
    schema = Section08BOperatorVerdict.model_json_schema()

    assert "StoryboardBEditPayload" in schema["$defs"]
    assert schema["$defs"]["StoryboardBEditPayload"] == StoryboardBEditPayload.model_json_schema()
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/StoryboardBEditPayload"
    )


def test_section_08b_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section08BOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
