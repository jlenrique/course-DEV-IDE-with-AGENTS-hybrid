from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.runtime import AdhocResponse

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "runtime"
    / "adhoc_response_golden.json"
)
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schema" / "adhoc_response.v1.schema.json"


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
            "utf-8"
        )
    ).hexdigest()


def _valid_payload() -> dict[str, object]:
    return {
        "text": "I answer without registering a trial.",
        "model_used": "gpt-5",
        "tokens": {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
        },
        "cost_usd": 0.0000625,
    }


def test_adhoc_response_strict_config() -> None:
    response = AdhocResponse(**_valid_payload())
    assert response.model_config["extra"] == "forbid"
    assert response.model_config["validate_assignment"] is True
    assert response.model_config["strict"] is True


def test_adhoc_response_rejects_negative_cost() -> None:
    payload = _valid_payload()
    payload["cost_usd"] = -0.01
    with pytest.raises(ValidationError):
        AdhocResponse(**payload)


def test_adhoc_response_token_shape_and_schema_pin() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    response = AdhocResponse.model_validate(payload)
    assert response.model_dump(mode="json") == payload
    assert response.tokens.total_tokens >= (
        response.tokens.input_tokens + response.tokens.output_tokens
    )
    assert _hash(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))) == _hash(
        AdhocResponse.model_json_schema()
    )
