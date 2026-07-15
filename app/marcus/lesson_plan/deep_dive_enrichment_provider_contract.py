"""Pure provider-payload identity and normalization for Deep Dive enrichment (37.2b).

Mirrors ``deep_dive_provider_contract`` for the 07W.3 enrichment writer with its
own provider contract mode / normalizer version so journal identity never
conflates the two LLM surfaces. The canonicalization/digest helpers are REUSED
from the 07W.1 contract module (do not re-derive).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from app.marcus.lesson_plan.deep_dive_projection import BoldTermMarker
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    canonical_json_mapping,
    provider_payload_digest,
)

DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE: Final[str] = "raw-json-schema"
DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION: Final[str] = (
    "deep-dive-enrichment-provider-normalizer.v1"
)


def normalize_deep_dive_enrichment_provider_payload(
    raw_payload: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Stable-deduplicate only independently valid, exact bold-term metadata.

    Provably-empty live-variance shapes normalize observably (recorded), never
    silently (Epic-38 retro doctrine); everything else passes through byte-fair.
    """
    if "bold_terms" in raw_payload and not isinstance(raw_payload["bold_terms"], list):
        raise TypeError("provider bold_terms must be an original JSON list")
    raw = canonical_json_mapping(raw_payload)
    normalized = canonical_json_mapping(raw)
    if normalized.get("status") != "enriched" or not isinstance(
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
    "DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE",
    "DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION",
    "canonical_json_mapping",
    "normalize_deep_dive_enrichment_provider_payload",
    "provider_payload_digest",
]
