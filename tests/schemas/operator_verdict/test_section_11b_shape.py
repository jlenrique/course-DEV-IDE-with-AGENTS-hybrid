from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_11b.poll_surface import display_input_package, submit_verdict
from app.models.operator_verdict_section_11b import (
    SECTION_11B_SURFACE_ID,
    InputPackageEditPayload,
    Section11BOperatorVerdict,
)
from tests.gates.section_11b._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_input_package_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_11b.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section11BOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_11b_operator_verdict_schema_hash_stable_across_transports() -> None:
    input_package = fixture_input_package_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_input_package(input_package)
        verdict = submit_verdict(
            displayed["input_package_id"],
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
        verdict_class=Section11BOperatorVerdict,
        surface_id=SECTION_11B_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_11b_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section11BOperatorVerdict.model_json_schema()

    assert SECTION_11B_SURFACE_ID == "section_11b_g4b_input_package"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_11b_g4b_input_package"
    )


def test_section_11b_payload_schemas_are_nested() -> None:
    schema = Section11BOperatorVerdict.model_json_schema()

    assert "InputPackageEditPayload" in schema["$defs"]
    assert schema["$defs"]["InputPackageEditPayload"] == (
        InputPackageEditPayload.model_json_schema()
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/InputPackageEditPayload"
    )


def test_section_11b_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section11BOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
