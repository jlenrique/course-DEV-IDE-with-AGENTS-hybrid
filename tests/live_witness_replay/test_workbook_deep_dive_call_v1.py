"""Replay the enrolled ``workbook-deep-dive-call.v1`` (07W.1) witnesses.

Completed witnesses replay the FULL provider-payload chain with zero provider
calls: raw payload → normalizer → strict candidate → skeleton gate/compose →
digest-exact result. Frozen failed attempts replay the ambiguity
classification (state ``call_in_progress`` + pinned identity).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonWriterResult,
    compose_deep_dive_skeleton,
)
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    DEEP_DIVE_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_PROVIDER_NORMALIZER_VERSION,
    normalize_deep_dive_provider_payload,
)
from tests.live_witness_replay.registry import family, skip_or_fail, witness_path

FAMILY = "workbook-deep-dive-call.v1"


def _canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _sha256(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _rows() -> list[dict[str, Any]]:
    return [row for row in family(FAMILY)["witnesses"] if row["disposition"] == "enrolled"]


def _normalize_legacy_null_map_digest(result_payload: dict[str, Any]) -> dict[str, Any]:
    """Drop a null ``slide_authority_map_digest`` (pre-38.3a legacy-null domain).

    The frozen 38.3a witnesses were captured when the optional field did not
    serialize; the digest helpers pop the None key the same way, so the replay
    comparison normalizes both sides identically instead of re-freezing the
    witness.
    """
    normalized = json.loads(_canonical(result_payload))
    authority = normalized.get("authority")
    if isinstance(authority, dict) and authority.get("slide_authority_map_digest") is None:
        authority.pop("slide_authority_map_digest", None)
    return normalized


@pytest.mark.parametrize("row", _rows(), ids=lambda row: row["id"])
def test_witness_replays_with_zero_provider_calls(row: dict[str, Any]) -> None:
    path = witness_path(row)
    if not path.is_file():
        skip_or_fail(f"witness journal missing on disk: {row['id']}")
    journal = json.loads(path.read_text(encoding="utf-8"))
    assert journal["schema_version"] == FAMILY
    assert journal["state"] == row["state"]
    capture = row.get("capture") or {}
    if "idempotency_key" in capture:
        assert journal["idempotency_key"] == capture["idempotency_key"]
    if row["state"] == "call_in_progress":
        # Frozen failed attempt: the ambiguity shape stands — a completed
        # payload must never have appeared on this coordinate.
        assert "result" not in journal
        assert "candidate" not in journal
        return
    # Completed witness: replay the full chain, zero provider calls.
    if "model_config_digest" in capture:
        assert journal["model_config_digest"] == capture["model_config_digest"]
    assert journal["provider_contract_mode"] == DEEP_DIVE_PROVIDER_CONTRACT_MODE
    assert (
        journal["provider_normalizer_version"] == DEEP_DIVE_PROVIDER_NORMALIZER_VERSION
    )
    raw_payload = journal["raw_provider_payload"]
    assert journal["raw_provider_payload_digest"] == _sha256(raw_payload)
    normalized, records = normalize_deep_dive_provider_payload(raw_payload)
    assert journal["provider_normalizations"] == list(records)
    assert journal["normalized_provider_payload_digest"] == _sha256(normalized)
    candidate = DeepDiveSkeletonWriterResult.model_validate_json(
        _canonical(normalized), strict=True
    )
    assert candidate.model_dump(mode="json") == journal["candidate"]
    request = DeepDiveSkeletonRequest.model_validate_json(
        _canonical(journal["authority"]), strict=True
    )
    result = compose_deep_dive_skeleton(request, lambda _: candidate)
    assert _normalize_legacy_null_map_digest(
        result.model_dump(mode="json")
    ) == _normalize_legacy_null_map_digest(journal["result"])
    # The frozen digest binds the journal's own persisted result bytes.
    assert journal["result_digest"] == _sha256(journal["result"])
    assert journal["authority_digest"] == result.authority_digest
    assert journal["candidate_digest"] == result.candidate_payload_digest
