from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_15.poll_surface import display_final_handoff, submit_verdict
from app.models.operator_verdict_section_15 import (
    SECTION_15_SURFACE_ID,
    HandoffEditPayload,
    Section15OperatorVerdict,
)
from tests.gates.section_15._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_final_handoff_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_15.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section15OperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_15_operator_verdict_schema_hash_stable_across_transports() -> None:
    final_handoff = fixture_final_handoff_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_final_handoff(final_handoff)
        verdict = submit_verdict(
            displayed["handoff_id"],
            {
                "run_id": RUN_ID,
                "verb": "complete",
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
        verdict_class=Section15OperatorVerdict,
        surface_id=SECTION_15_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_15_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section15OperatorVerdict.model_json_schema()

    assert SECTION_15_SURFACE_ID == "section_15_g5_final_handoff"
    assert schema["properties"]["surface_id"]["const"] == "section_15_g5_final_handoff"


def test_section_15_payload_schemas_are_nested() -> None:
    schema = Section15OperatorVerdict.model_json_schema()

    assert "HandoffEditPayload" in schema["$defs"]
    assert schema["$defs"]["HandoffEditPayload"] == (
        HandoffEditPayload.model_json_schema()
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/HandoffEditPayload"
    )


def test_section_15_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section15OperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
