"""Pure provider-payload identity and normalization for Deep Dive enrichment (37.2b).

Mirrors ``deep_dive_provider_contract`` for the 07W.3 enrichment writer with its
own provider contract mode / normalizer version so journal identity never
conflates the two LLM surfaces. The canonicalization/digest helpers are REUSED
from the 07W.1 contract module (do not re-derive).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from app.marcus.lesson_plan.deep_dive_projection import BoldTermMarker, _marked_terms
from app.marcus.lesson_plan.deep_dive_provider_contract import (
    canonical_json_mapping,
    provider_payload_digest,
)

DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE: Final[str] = "raw-json-schema"
# v2 (post-probe aa1ddff9): adds the first-appearance bold_terms metadata
# reorder — a behavior change, so journal identity honesty demands the bump.
DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION: Final[str] = (
    "deep-dive-enrichment-provider-normalizer.v2"
)
BOLD_TERMS_REORDERED_RECORD: Final[str] = "bold_terms_reordered_to_first_appearance"


def _prose_first_appearance_terms(
    normalized: Mapping[str, Any],
) -> tuple[str, ...] | None:
    """First-appearance bold terms measured from the payload's section proses.

    Matches the :class:`DeepDiveEnrichedWriterResult` validator's semantics
    exactly (``_marked_terms`` over ``strip_citation_markers``-stripped prose).
    ``None`` when the prose side is not measurable (missing/ill-typed sections
    or malformed bold markup) — those shapes stay fail-loud untouched.
    """
    # Local import: single-sourced marker-strip semantics; no cycle —
    # deep_dive_enrichment never imports this contract module.
    from app.marcus.lesson_plan.deep_dive_enrichment import (  # noqa: PLC0415
        strip_citation_markers,
    )

    sections = normalized.get("sections")
    if not isinstance(sections, list) or not sections:
        return None
    proses: list[str] = []
    for section in sections:
        if not isinstance(section, Mapping):
            return None
        prose = section.get("prose")
        if not isinstance(prose, str):
            return None
        proses.append(strip_citation_markers(prose))
    try:
        return _marked_terms(tuple(proses))
    except ValueError:
        return None


def _reordered_to_first_appearance(
    normalized: Mapping[str, Any], entries: list[object]
) -> list[object] | None:
    """Reorder ONLY the provably-unambiguous order-variant metadata shape.

    Applies when every ``bold_terms`` entry is an independently valid exact
    :class:`BoldTermMarker` mapping, the metadata term SET exactly equals the
    prose-marked term set, no metadata term repeats, and only the ORDER differs
    from first-appearance order. Entry dicts move intact (all fields preserved
    — eligibility already pins the exact ``{"term"}`` shape). Any SET
    difference (missing/extra/duplicate term) returns ``None`` and the payload
    stays fail-loud untouched.
    """
    terms: list[str] = []
    for entry in entries:
        if not (isinstance(entry, Mapping) and set(entry) == {"term"}):
            return None
        value = entry.get("term")
        if not isinstance(value, str):
            return None
        try:
            marker = BoldTermMarker.model_validate(dict(entry), strict=True)
        except ValueError:
            return None
        terms.append(marker.term)
    if len(set(terms)) != len(terms):
        return None  # duplicate metadata terms are a SET variance: fail loud
    prose_terms = _prose_first_appearance_terms(normalized)
    if prose_terms is None:
        return None
    if tuple(terms) == prose_terms:
        return None  # already first-appearance ordered: byte-stable, no record
    if set(terms) != set(prose_terms):
        return None  # missing/extra terms: fail loud untouched
    entry_by_term = {
        term: entry for term, entry in zip(terms, entries, strict=True)
    }
    return [entry_by_term[term] for term in prose_terms]


def normalize_deep_dive_enrichment_provider_payload(
    raw_payload: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Stable-deduplicate exact bold-term metadata; reorder to first appearance.

    Provably-unambiguous live-variance shapes normalize observably (recorded),
    never silently (Epic-38 retro doctrine); everything else passes through
    byte-fair. v2 adds the order-only reorder (probe aa1ddff9: the model
    returned the exact prose-marked term SET in skeleton/importance order and
    the validator red-rejected on tuple order alone).
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
    reordered = _reordered_to_first_appearance(normalized, kept)
    if reordered is not None:
        normalized["bold_terms"] = reordered
        records.append(BOLD_TERMS_REORDERED_RECORD)
    return normalized, tuple(records)


__all__ = [
    "BOLD_TERMS_REORDERED_RECORD",
    "DEEP_DIVE_ENRICHMENT_PROVIDER_CONTRACT_MODE",
    "DEEP_DIVE_ENRICHMENT_PROVIDER_NORMALIZER_VERSION",
    "canonical_json_mapping",
    "normalize_deep_dive_enrichment_provider_payload",
    "provider_payload_digest",
]
