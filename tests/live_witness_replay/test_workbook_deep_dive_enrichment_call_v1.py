"""Replay the ``workbook-deep-dive-enrichment-call.v1`` (07W.3) witnesses.

Zero-witness rule (Winston D3-1): at founding this family has NO frozen
witness — its first witness freezes from ``probe-37-2b-deep-dive-enrichment-001``
on PASS. Until then a normal run SKIPS with the probe named and a STRICT
pre-flight FAILS: a paid run may not claim replay-green on an unwitnessed path.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import pytest

from app.marcus.lesson_plan.deep_dive_enrichment import (
    DeepDiveEnrichedWriterResult,
    DeepDiveEnrichmentRequestV1,
    compose_deep_dive_enrichment,
)
from app.marcus.lesson_plan.deep_dive_enrichment_provider_contract import (
    DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE,
    DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION,
    normalize_deep_dive_enrichment_provider_payload,
)
from tests.live_witness_replay.registry import family, skip_or_fail, witness_path

FAMILY = "workbook-deep-dive-enrichment-call.v1"


def _canonical(value: object) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def _sha256(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _family_row() -> dict[str, Any]:
    return family(FAMILY)


def test_family_is_enrolled_and_witnessed_or_named_pending() -> None:
    row = _family_row()
    enrolled = [w for w in row["witnesses"] if w.get("disposition") == "enrolled"]
    if not enrolled:
        pending = row.get("pending_first_witness")
        assert pending, "an unwitnessed family must name its owed probe"
        skip_or_fail(
            f"no frozen witness for {FAMILY} yet — first witness owed by probe "
            f"{pending} (zero-witness rule: probe -> freeze -> replay -> spend)"
        )


@pytest.mark.parametrize(
    "row",
    [w for w in _family_row()["witnesses"] if w.get("disposition") == "enrolled"],
    ids=lambda row: row["id"],
)
def test_witness_replays_with_zero_provider_calls(row: dict[str, Any]) -> None:
    path = witness_path(row)
    if not path.is_file():
        skip_or_fail(f"witness journal missing on disk: {row['id']}")
    journal = json.loads(path.read_text(encoding="utf-8"))
    assert journal["schema_version"] == FAMILY
    assert journal["state"] == row["state"]
    if journal["state"] == "call_in_progress":
        assert "result" not in journal
        return
    assert (
        journal["provider_contract_mode"]
        == DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE
    )
    assert (
        journal["provider_normalizer_version"]
        == DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION
    )
    raw_payload = journal["raw_provider_payload"]
    assert journal["raw_provider_payload_digest"] == _sha256(raw_payload)
    normalized, records = normalize_deep_dive_enrichment_provider_payload(raw_payload)
    assert journal["provider_normalizations"] == list(records)
    assert journal["normalized_provider_payload_digest"] == _sha256(normalized)
    candidate = DeepDiveEnrichedWriterResult.model_validate_json(
        _canonical(normalized), strict=True
    )
    assert candidate.model_dump(mode="json") == journal["candidate"]
    request = DeepDiveEnrichmentRequestV1.model_validate_json(
        _canonical(journal["request"]), strict=True
    )
    result = compose_deep_dive_enrichment(request, lambda _: candidate)
    assert result.model_dump(mode="json") == journal["result"]
    assert journal["result_digest"] == _sha256(result.model_dump(mode="json"))
