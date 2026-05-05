"""Reusable OperatorVerdict schema-stability assertions."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel

Transport = Literal["cli", "http", "mcp-stdio"]
REQUIRED_VERDICT_FIELDS = frozenset(
    {
        "decision_card_digest",
        "operator_id",
        "run_id",
        "submitted_at",
        "surface_id",
        "verb",
    }
)


def _schema_hash(verdict_class: type[BaseModel]) -> str:
    payload = json.dumps(
        verdict_class.model_json_schema(),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _surface_id_const(schema: dict[str, object]) -> str | None:
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        return None
    surface = properties.get("surface_id")
    if isinstance(surface, dict):
        const = surface.get("const")
        if isinstance(const, str):
            return const
        default = surface.get("default")
        if isinstance(default, str):
            return default
    return None


def assert_operator_verdict_schema_stable_across_transports(
    *,
    verdict_class: type[BaseModel],
    surface_id: str,
    transports: Sequence[Transport] = ("cli", "http", "mcp-stdio"),
) -> None:
    """Assert one OperatorVerdict variant has a stable transport-neutral schema."""

    if not transports:
        raise AssertionError("at least one transport must be declared")
    schema = verdict_class.model_json_schema()
    hashes = {_schema_hash(verdict_class) for _transport in transports}
    assert len(hashes) == 1

    model_fields = set(verdict_class.model_fields)
    missing = REQUIRED_VERDICT_FIELDS - model_fields
    assert not missing, f"OperatorVerdict schema missing field(s): {sorted(missing)}"
    assert _surface_id_const(schema) == surface_id

    properties = schema.get("properties", {})
    assert isinstance(properties, dict)
    assert "decision_card_digest" in properties
    assert "verb" in properties


__all__ = [
    "REQUIRED_VERDICT_FIELDS",
    "Transport",
    "assert_operator_verdict_schema_stable_across_transports",
]
