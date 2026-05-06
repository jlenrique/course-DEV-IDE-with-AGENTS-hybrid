from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_07b.poll_surface import display_per_slide_variant, submit_verdict
from app.models.operator_verdict_section_07b import (
    SECTION_07B_SURFACE_ID,
    PerSlideVariantEditPayload,
    PerSlideVariantPayload,
    Section07BOperatorVerdict,
)
from tests.gates.section_07b._helpers import (
    RUN_ID,
    SLIDE_ID,
    SUBMITTED_AT,
    fixture_per_slide_variant_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_07b.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section07BOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_07b_operator_verdict_schema_hash_stable_across_transports() -> None:
    variant_card = fixture_per_slide_variant_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_per_slide_variant(variant_card)
        verdict = submit_verdict(
            SLIDE_ID,
            {
                "run_id": RUN_ID,
                "verb": "select",
                "operator_id": "operator_1",
                "submitted_at": SUBMITTED_AT,
                "decision_card_digest": displayed["decision_card_digest"],
                "select_payload": {"selected_variant": "B"},
            },
            transport,  # type: ignore[arg-type]
        )
        schema_hashes.add(_schema_hash())
        verdict_payloads.append(verdict.model_dump(mode="json"))

    assert len(schema_hashes) == 1
    assert verdict_payloads[0] == verdict_payloads[1] == verdict_payloads[2]
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section07BOperatorVerdict,
        surface_id=SECTION_07B_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_07b_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section07BOperatorVerdict.model_json_schema()

    assert SECTION_07B_SURFACE_ID == "section_07b_g2m_per_slide_variant"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_07b_g2m_per_slide_variant"
    )


def test_section_07b_payload_schemas_are_nested() -> None:
    schema = Section07BOperatorVerdict.model_json_schema()

    assert "PerSlideVariantPayload" in schema["$defs"]
    assert "PerSlideVariantEditPayload" in schema["$defs"]
    assert schema["$defs"]["PerSlideVariantPayload"] == (
        PerSlideVariantPayload.model_json_schema()
    )
    assert schema["$defs"]["PerSlideVariantEditPayload"] == (
        PerSlideVariantEditPayload.model_json_schema()
    )
    assert schema["properties"]["select_payload"]["anyOf"][0]["$ref"].endswith(
        "/PerSlideVariantPayload"
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/PerSlideVariantEditPayload"
    )


def test_section_07b_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section07BOperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
