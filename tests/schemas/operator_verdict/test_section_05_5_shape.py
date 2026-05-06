from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_05_5.poll_surface import display_per_slide_mode, submit_verdict
from app.models.operator_verdict_section_05_5 import (
    SECTION_05_5_SURFACE_ID,
    PerSlideModeEditPayload,
    PerSlideModePayload,
    Section05_5OperatorVerdict,
)
from tests.gates.section_05_5._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_per_slide_mode_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_05_5.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section05_5OperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_05_5_operator_verdict_schema_hash_stable_across_transports() -> None:
    per_slide_card = fixture_per_slide_mode_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_per_slide_mode(per_slide_card)
        verdict = submit_verdict(
            displayed["slide_id"],
            {
                "run_id": RUN_ID,
                "verb": "select",
                "operator_id": "operator_1",
                "submitted_at": SUBMITTED_AT,
                "decision_card_digest": displayed["decision_card_digest"],
                "select_payload": {"selected_mode": "narrated-deck"},
            },
            transport,  # type: ignore[arg-type]
        )
        schema_hashes.add(_schema_hash())
        verdict_payloads.append(verdict.model_dump(mode="json"))

    assert len(schema_hashes) == 1
    assert verdict_payloads[0] == verdict_payloads[1] == verdict_payloads[2]
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section05_5OperatorVerdict,
        surface_id=SECTION_05_5_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_05_5_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section05_5OperatorVerdict.model_json_schema()

    assert SECTION_05_5_SURFACE_ID == "section_05_5_g2b_per_slide_mode"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_05_5_g2b_per_slide_mode"
    )


def test_section_05_5_payload_schemas_are_nested() -> None:
    schema = Section05_5OperatorVerdict.model_json_schema()

    assert "PerSlideModePayload" in schema["$defs"]
    assert "PerSlideModeEditPayload" in schema["$defs"]
    assert schema["$defs"]["PerSlideModePayload"] == PerSlideModePayload.model_json_schema()
    assert schema["$defs"]["PerSlideModeEditPayload"] == (
        PerSlideModeEditPayload.model_json_schema()
    )
    assert schema["properties"]["select_payload"]["anyOf"][0]["$ref"].endswith(
        "/PerSlideModePayload"
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/PerSlideModeEditPayload"
    )


def test_section_05_5_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section05_5OperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected

