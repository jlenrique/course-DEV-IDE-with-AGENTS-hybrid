from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import pytest
import yaml
from pydantic import ValidationError

from app.marcus.orchestrator.writers.outbound_envelope import (
    GaryOutboundEnvelope,
    OutboundEnvelopeEntry,
    emit_gary_outbound_envelope,
    pre_dispatch_package_gary_md,
)

SCHEMA_HASH = "382985141ffe8e6572f17415d41d8eda33c6c49e6942d0e5a6d623ea9c1b4056"
DISPATCHED_AT = datetime(2026, 5, 6, 12, 0, tzinfo=UTC)


def _entry(writer_id: str, payload_ref: str) -> dict[str, object]:
    return {
        "writer_id": writer_id,
        "target_section": "section-15",
        "payload_ref": payload_ref,
        "dispatched_at": DISPATCHED_AT,
        "operator_id": "operator_1",
    }


def _payload() -> GaryOutboundEnvelope:
    return GaryOutboundEnvelope(
        plan_unit_id="unit-07",
        target_section="section-15",
        entries=[
            OutboundEnvelopeEntry.model_validate(
                _entry("gary-theme-resolution", "gary-theme-resolution.json")
            ),
            OutboundEnvelopeEntry.model_validate(
                _entry("gary-slide-content", "gary-slide-content.json")
            ),
        ],
        dispatched_at=DISPATCHED_AT,
        operator_id="operator_1",
    )


def test_outbound_envelope_round_trips_and_emits_deterministic_lf_yaml(tmp_path):
    payload = GaryOutboundEnvelope.model_validate(_payload().model_dump(mode="json"))
    output_path = emit_gary_outbound_envelope(
        payload,
        tmp_path / "gary-outbound-envelope.yaml",
    )

    expected = yaml.safe_dump(
        payload.model_dump(mode="json"),
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
    )
    raw = output_path.read_bytes()
    assert raw == expected.encode("utf-8")
    assert b"\r\n" not in raw
    assert output_path.read_bytes() == emit_gary_outbound_envelope(
        payload,
        output_path,
    ).read_bytes()


def test_outbound_envelope_rejects_unknown_writer_id():
    data = _payload().model_dump(mode="json")
    data["entries"][0]["writer_id"] = "random-writer"

    with pytest.raises(ValidationError):
        GaryOutboundEnvelope.model_validate(data)


def test_outbound_envelope_rejects_blank_operator_id():
    data = _payload().model_dump(mode="json")
    data["operator_id"] = "   "

    with pytest.raises(ValidationError):
        GaryOutboundEnvelope.model_validate(data)


def test_outbound_envelope_rejects_empty_entries():
    data = _payload().model_dump(mode="json")
    data["entries"] = []

    with pytest.raises(ValidationError):
        GaryOutboundEnvelope.model_validate(data)


def test_pre_dispatch_package_markdown_is_deterministic_and_ordered():
    payload = _payload()
    rendered = pre_dispatch_package_gary_md(
        payload,
        payload_loaders={
            "gary-slide-content": lambda entry: json.dumps(
                {"ref": entry.payload_ref},
                sort_keys=True,
            ),
            "gary-theme-resolution": lambda entry: json.dumps(
                {"ref": entry.payload_ref},
                sort_keys=True,
            ),
        },
    )

    assert rendered == pre_dispatch_package_gary_md(
        payload,
        payload_loaders={
            "gary-slide-content": lambda entry: json.dumps(
                {"ref": entry.payload_ref},
                sort_keys=True,
            ),
            "gary-theme-resolution": lambda entry: json.dumps(
                {"ref": entry.payload_ref},
                sort_keys=True,
            ),
        },
    )
    assert rendered.index("## gary-slide-content") < rendered.index(
        "## gary-theme-resolution"
    )


def test_outbound_envelope_schema_hash_is_stable():
    schema = json.dumps(GaryOutboundEnvelope.model_json_schema(), sort_keys=True).encode()

    assert hashlib.sha256(schema).hexdigest() == SCHEMA_HASH
