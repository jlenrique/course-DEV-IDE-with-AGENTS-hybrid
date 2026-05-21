from __future__ import annotations

from datetime import UTC, datetime

from app.models.operator_verdict_section_04_5 import (
    SECTION_04_5_SURFACE_ID,
    EstimatorEditPayload,
    Section04_5OperatorVerdict,
)
from tests.gates.section_04_5._helpers import ESTIMATOR_ID, RUN_ID
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)


def test_section_04_5_operator_verdict_schema_hash_stable_across_transports() -> None:
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section04_5OperatorVerdict,
        surface_id=SECTION_04_5_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_04_5_verdict_variant_is_tagged_with_surface_id() -> None:
    verdict = Section04_5OperatorVerdict(
        run_id=RUN_ID,
        surface_id=SECTION_04_5_SURFACE_ID,
        verb="acknowledged",
        estimator_id=str(ESTIMATOR_ID),
        operator_id="operator_1",
        submitted_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        decision_card_digest="a" * 64,
    )

    assert verdict.surface_id == "section_04_5_g1_5_estimator"
    assert (
        Section04_5OperatorVerdict.model_json_schema()["properties"]["surface_id"][
            "const"
        ]
        == "section_04_5_g1_5_estimator"
    )


def test_section_04_5_edit_payload_schema_is_nested_estimator_edit_payload() -> None:
    schema = Section04_5OperatorVerdict.model_json_schema()

    assert "EstimatorEditPayload" in schema["$defs"]
    assert (
        schema["$defs"]["EstimatorEditPayload"]
        == EstimatorEditPayload.model_json_schema()
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/EstimatorEditPayload"
    )


def test_section_04_5_estimator_id_strips_then_rejects_empty() -> None:
    verdict = Section04_5OperatorVerdict(
        run_id=RUN_ID,
        verb="acknowledged",
        estimator_id=f"  {ESTIMATOR_ID}  ",
        operator_id="operator_1",
        submitted_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        decision_card_digest="a" * 64,
    )

    assert verdict.estimator_id == str(ESTIMATOR_ID)

