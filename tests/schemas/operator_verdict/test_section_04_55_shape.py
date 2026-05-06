from __future__ import annotations

from datetime import UTC, datetime

from app.models.operator_verdict_section_04_55 import (
    SECTION_04_55_SURFACE_ID,
    RunConstantsEditPayload,
    Section04_55OperatorVerdict,
)
from tests.gates.section_04_55._helpers import RUN_ID
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)


def test_section_04_55_operator_verdict_schema_hash_stable_across_transports() -> None:
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section04_55OperatorVerdict,
        surface_id=SECTION_04_55_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_04_55_verdict_variant_is_tagged_with_surface_id() -> None:
    verdict = Section04_55OperatorVerdict(
        run_id=RUN_ID,
        surface_id=SECTION_04_55_SURFACE_ID,
        verb="lock",
        operator_id="operator_1",
        run_constants_id=" RUN-CONSTANTS-001 ",
        submitted_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        decision_card_digest="a" * 64,
    )

    assert verdict.surface_id == "section_04_55_g1_5_run_constants"
    assert verdict.run_constants_id == "RUN-CONSTANTS-001"
    assert (
        Section04_55OperatorVerdict.model_json_schema()["properties"]["surface_id"][
            "const"
        ]
        == "section_04_55_g1_5_run_constants"
    )


def test_section_04_55_edit_payload_schema_is_nested_run_constants_edit_payload() -> None:
    schema = Section04_55OperatorVerdict.model_json_schema()

    assert "RunConstantsEditPayload" in schema["$defs"]
    assert (
        schema["$defs"]["RunConstantsEditPayload"]
        == RunConstantsEditPayload.model_json_schema()
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/RunConstantsEditPayload"
    )

