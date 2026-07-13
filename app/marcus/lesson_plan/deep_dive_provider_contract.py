"""Pure provider-payload identity and normalization for Deep Dive execution."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any, Final

from app.marcus.lesson_plan.deep_dive_projection import BoldTermMarker

DEEP_DIVE_PROVIDER_CONTRACT_MODE: Final[str] = "raw-json-schema"
DEEP_DIVE_PROVIDER_NORMALIZER_VERSION: Final[str] = (
    "deep-dive-provider-normalizer.v1"
)


def canonical_json_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    decoded = json.loads(encoded)
    if not isinstance(decoded, dict):
        raise TypeError("provider payload must canonicalize to a JSON object")
    return decoded


def provider_payload_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def normalize_deep_dive_provider_payload(
    raw_payload: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Stable-deduplicate only independently valid, exact bold-term metadata."""
    if "bold_terms" in raw_payload and not isinstance(raw_payload["bold_terms"], list):
        raise TypeError("provider bold_terms must be an original JSON list")
    raw = canonical_json_mapping(raw_payload)
    normalized = canonical_json_mapping(raw)
    if normalized.get("status") != "authored" or not isinstance(
        normalized.get("bold_terms"), list
    ):
        return normalized, ()
    seen: set[str] = set()
    kept: list[object] = []
    records: list[str] = []
    for entry in normalized["bold_terms"]:
        eligible = False
        term: str | None = None
        if isinstance(entry, Mapping) and set(entry) == {"term"}:
            value = entry.get("term")
            if isinstance(value, str):
                try:
                    marker = BoldTermMarker.model_validate(dict(entry), strict=True)
                except ValueError:
                    pass
                else:
                    eligible = True
                    term = marker.term
        if eligible and term in seen:
            records.append(f"deduplicated_exact_bold_term:{term}")
            continue
        kept.append(entry)
        if eligible and term is not None:
            seen.add(term)
    normalized["bold_terms"] = kept
    return normalized, tuple(records)


__all__ = [
    "DEEP_DIVE_PROVIDER_CONTRACT_MODE",
    "DEEP_DIVE_PROVIDER_NORMALIZER_VERSION",
    "canonical_json_mapping",
    "normalize_deep_dive_provider_payload",
    "provider_payload_digest",
]
