from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.gates.section_11.poll_surface import display_voice_candidates, submit_verdict
from app.models.operator_verdict_section_11 import (
    SECTION_11_SURFACE_ID,
    Section11OperatorVerdict,
    VoiceSelectionEditPayload,
    VoiceSelectionPayload,
)
from tests.gates.section_11._helpers import (
    RUN_ID,
    SUBMITTED_AT,
    fixture_voice_selection_card,
)
from tests.schemas.operator_verdict._harness import (
    assert_operator_verdict_schema_stable_across_transports,
)

SCHEMA_PATH = Path("app/models/operator_verdict_section_11.v1.schema.json")


def _schema_hash() -> str:
    payload = json.dumps(
        Section11OperatorVerdict.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_section_11_operator_verdict_schema_hash_stable_across_transports() -> None:
    voice_card = fixture_voice_selection_card()
    schema_hashes: set[str] = set()
    verdict_payloads: list[dict[str, object]] = []

    for transport in ("cli", "http", "mcp-stdio"):
        displayed = display_voice_candidates(voice_card)
        verdict = submit_verdict(
            displayed["voice_selection_id"],
            {
                "run_id": RUN_ID,
                "verb": "select",
                "operator_id": "operator_1",
                "submitted_at": SUBMITTED_AT,
                "decision_card_digest": displayed["decision_card_digest"],
                "select_payload": {"selected_voice_id": "en-US-narrator"},
            },
            transport,  # type: ignore[arg-type]
        )
        schema_hashes.add(_schema_hash())
        verdict_payloads.append(verdict.model_dump(mode="json"))

    assert len(schema_hashes) == 1
    assert verdict_payloads[0] == verdict_payloads[1] == verdict_payloads[2]
    assert_operator_verdict_schema_stable_across_transports(
        verdict_class=Section11OperatorVerdict,
        surface_id=SECTION_11_SURFACE_ID,
        transports=["cli", "http", "mcp-stdio"],
    )


def test_section_11_verdict_variant_is_tagged_with_surface_id() -> None:
    schema = Section11OperatorVerdict.model_json_schema()

    assert SECTION_11_SURFACE_ID == "section_11_g4a_voice_selection"
    assert schema["properties"]["surface_id"]["const"] == (
        "section_11_g4a_voice_selection"
    )


def test_section_11_payload_schemas_are_nested() -> None:
    schema = Section11OperatorVerdict.model_json_schema()

    assert "VoiceSelectionPayload" in schema["$defs"]
    assert "VoiceSelectionEditPayload" in schema["$defs"]
    assert schema["$defs"]["VoiceSelectionPayload"] == VoiceSelectionPayload.model_json_schema()
    assert schema["$defs"]["VoiceSelectionEditPayload"] == (
        VoiceSelectionEditPayload.model_json_schema()
    )
    assert schema["properties"]["select_payload"]["anyOf"][0]["$ref"].endswith(
        "/VoiceSelectionPayload"
    )
    assert schema["properties"]["edit_payload"]["anyOf"][0]["$ref"].endswith(
        "/VoiceSelectionEditPayload"
    )


def test_section_11_operator_verdict_schema_file_matches_model() -> None:
    expected = json.dumps(
        Section11OperatorVerdict.model_json_schema(),
        indent=2,
        sort_keys=True,
    )

    assert SCHEMA_PATH.read_text(encoding="utf-8") == expected
