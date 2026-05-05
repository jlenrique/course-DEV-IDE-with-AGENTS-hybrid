from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from app.gates.section_02a._transports import TRANSPORT_HANDLERS
from app.models.operator_verdict_section_02a import (
    SECTION_02A_SURFACE_ID,
    DirectiveEditPayload,
    Section02AOperatorVerdict,
)
from tests.gates.section_02a._helpers import fixture_directive


def _schema_hash() -> str:
    payload = json.dumps(
        Section02AOperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_02a_operator_verdict_schema_hash_stable_across_transports() -> None:
    directive = fixture_directive()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        response = TRANSPORT_HANDLERS[transport](
            directive,
            verb="approve",
            operator_id="operator_1",
        )
        schema_hashes.add(_schema_hash())
        verdict_payloads.append(response["operator_verdict"])

    assert len(schema_hashes) == 1
    assert verdict_payloads[0] == verdict_payloads[1] == verdict_payloads[2]


def test_section_02a_verdict_variant_is_tagged_with_surface_id() -> None:
    directive = fixture_directive()
    verdict = Section02AOperatorVerdict(
        run_id=directive.run_id,
        surface_id=SECTION_02A_SURFACE_ID,
        verb="approve",
        operator_id="operator_1",
        submitted_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        decision_card_digest="a" * 64,
    )

    assert verdict.surface_id == "section_02a_g0_poll"
    assert (
        Section02AOperatorVerdict.model_json_schema()["properties"]["surface_id"][
            "const"
        ]
        == "section_02a_g0_poll"
    )


def test_section_02a_edit_payload_schema_is_nested_directive_edit_payload() -> None:
    schema = Section02AOperatorVerdict.model_json_schema()

    assert "DirectiveEditPayload" in schema["$defs"]
    assert schema["$defs"]["DirectiveEditPayload"] == DirectiveEditPayload.model_json_schema()
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/DirectiveEditPayload"
    )
