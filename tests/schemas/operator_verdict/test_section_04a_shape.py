from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_04a.poll_surface import display_plan_unit, submit_verdict
from app.models.operator_verdict_section_04a import (
    SECTION_04A_SURFACE_ID,
    PlanUnitEditPayload,
    Section04AOperatorVerdict,
)
from tests.gates.section_04a._helpers import fixture_plan_unit
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_04a.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section04AOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_04a_operator_verdict_schema_hash_stable_across_transports() -> None:
    plan_unit = fixture_plan_unit()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_plan_unit(plan_unit)
        verdict = submit_verdict(
            displayed["plan_unit"]["unit_id"],
            {
                "run_id": displayed["decision_card"]["trial_id"],
                "verb": "approve",
                "operator_id": "operator_1",
                "submitted_at": displayed["decision_card"]["created_at"],
                "decision_card_digest": displayed["decision_card_digest"],
            },
            transport,  # type: ignore[arg-type]
        )
        schema_hashes.add(_schema_hash())
        verdict_payloads.append(verdict.model_dump(mode="json"))

    assert len(schema_hashes) == 1
    assert verdict_payloads[0] == verdict_payloads[1] == verdict_payloads[2]
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section04AOperatorVerdict,
        surface_id=SECTION_04A_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_04a_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section04AOperatorVerdict.model_json_schema()

    assert SECTION_04A_SURFACE_ID == "section_04a_g1a_poll"
    assert schema["properties"]["surface_id"]["const"] == "section_04a_g1a_poll"


def test_section_04a_edit_payload_schema_is_nested_plan_unit_edit_payload() -> None:
    schema = Section04AOperatorVerdict.model_json_schema()

    assert "PlanUnitEditPayload" in schema["$defs"]
    assert schema["$defs"]["PlanUnitEditPayload"] == PlanUnitEditPayload.model_json_schema()
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/PlanUnitEditPayload"
    )


def test_section_04a_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section04AOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
